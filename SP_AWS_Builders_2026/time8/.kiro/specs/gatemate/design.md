# Design Document — GateMate

## Overview

O GateMate é um concierge de IA para passageiros que enfrentam atrasos ou conexões curtas. O passageiro informa seu código de reserva, descreve em linguagem natural o que precisa, e recebe um plano de ação empático de 3 passos com serviços disponíveis no aeroporto.

A stack escolhida reflete as restrições do Hackathon TiDB × AWS (sprint de 2h30): Python (FastAPI) no backend, React (Vite) no frontend, TiDB Cloud Starter como banco de dados com busca vetorial nativa, e Amazon Bedrock para geração de linguagem natural.

### Objetivos de Design

- **Minimalismo de integrações**: usar `EMBED_TEXT` do TiDB para embeddings em vez do Bedrock, eliminando uma chamada extra ao serviço externo e reduzindo latência.
- **Resiliência**: retry automático no cliente Bedrock, timeouts explícitos e mensagens de erro em português sem expor detalhes técnicos.
- **Segurança de credenciais**: todas as configurações sensíveis via variáveis de ambiente, sem valores no repositório.
- **Reprodutibilidade**: estrutura de arquivos e comandos documentados para que avaliadores consigam executar localmente.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Navegador                            │
│           React (Vite) — porta 3000                         │
│   BookingForm → FlightInfo + NeedInput → ActionPlan         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (fetch)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI — porta 8000                        │
│  GET  /health                                               │
│  POST /api/booking    → db.py                               │
│  POST /api/recommend  → tidb_vector.py + bedrock_client.py  │
└────────┬──────────────────────────────────┬─────────────────┘
         │ pymysql + SSL                     │ boto3
         ▼                                   ▼
┌─────────────────────┐         ┌────────────────────────────┐
│  TiDB Cloud Starter │         │  Amazon Bedrock            │
│  sa-east-1          │         │  ap-southeast-1            │
│  airportdb          │         │  claude-3-haiku            │
│  ├── booking        │         └────────────────────────────┘
│  ├── passenger      │
│  ├── passengerdetails│
│  ├── flight         │
│  └── airport_services│
│      (VECTOR(1024)) │
└─────────────────────┘
```

### Decisões Técnicas

| Decisão | Alternativa descartada | Justificativa |
|---|---|---|
| `EMBED_TEXT` via TiDB para embeddings | Bedrock Titan embeddings direto | Elimina round-trip extra para `ap-southeast-1`; TiDB faz embedding e busca em uma única query SQL |
| Uma única chamada Bedrock por recomendação | Streaming ou múltiplas chamadas | Minimiza latência; contexto cabe em um único prompt com `claude-3-haiku` |
| `pymysql` com pool de conexões | SQLAlchemy | Dependência mínima; suficiente para o volume do hackathon |
| CORS via FastAPI middleware | Proxy nginx | Elimina infraestrutura adicional no ambiente de desenvolvimento |
| Retry com 2 tentativas + 1s de intervalo | Circuit breaker completo | Balanceia resiliência e complexidade dentro da sprint |

---

## Components and Interfaces

### Backend

#### `main.py` — FastAPI App

```
POST /api/booking
  Body:  { "booking_code": string }
  200:   { "passenger_name": string, "flight_number": string,
            "origin": string, "destination": string,
            "departure_time": string (ISO 8601), "status": string }
  400:   { "detail": string }   ← formato inválido ou não encontrado
  503:   { "detail": string }   ← falha de conexão com banco

POST /api/recommend
  Body:  { "booking_code": string, "need_description": string }
  200:   { "step1": string, "step2": string, "step3": string }
  400:   { "detail": string }   ← entrada inválida
  503:   { "detail": string }   ← falha Bedrock (após retries)
  504:   { "detail": string }   ← timeout Bedrock

GET /health
  200:   { "status": "ok" }
```

Configurações do middleware:
- `CORSMiddleware` — `allow_origins=["http://localhost:3000"]`, todos os métodos e headers.
- Timeout implícito via `asyncio` nas rotas que chamam Bedrock.

#### `db.py` — Conexão TiDB

Responsável por criar e gerenciar a conexão com o TiDB Cloud. Usa `pymysql` com SSL obrigatório (`ssl={"ca": "/etc/ssl/cert.pem"}`). Expõe:

- `get_connection()` → retorna uma conexão `pymysql` pronta para uso
- `close_connection(conn)` → fecha a conexão
- Lança `DatabaseUnavailableError` se a conexão falhar

A conexão é criada por request (sem pool persistente) para simplicidade na sprint; o overhead de reconexão é aceitável dado o volume esperado.

#### `tidb_vector.py` — Busca Vetorial e Seed

Duas responsabilidades:

1. **Busca semântica** — `search_services(query: str, top_k: int = 5) -> list[dict]`:
   - Valida `query` (1–500 caracteres)
   - Executa SQL com `EMBED_TEXT` e `VEC_COSINE_DISTANCE`
   - Retorna lista de `{name, description, distance}`

2. **Seed** — `seed_airport_services()`:
   - Cria tabela `airport_services` se não existir
   - Insere 30+ registros sintéticos com `EMBED_TEXT` para preencher `embedding`
   - Exibe contagem ao final; aborta com mensagem de erro se `EMBED_TEXT` falhar

Query de busca:

```sql
SELECT name, description,
       VEC_COSINE_DISTANCE(embedding,
           EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", :query)
       ) AS distance
FROM airport_services
ORDER BY distance ASC
LIMIT :top_k;
```

#### `bedrock_client.py` — Cliente Amazon Bedrock

- Inicializa `boto3.client("bedrock-runtime", region_name="ap-southeast-1")`
- Falha na inicialização se credenciais AWS ausentes → propaga `BedrockUnavailableError`
- `generate_action_plan(passenger_name, flight_number, flight_status, wait_time, services) -> dict`:
  - Monta prompt em português (pt-BR) com todos os dados de contexto
  - Chama `invoke_model` com timeout de 10 segundos
  - Retry até 2 vezes com `time.sleep(1)` em caso de erro de serviço
  - Parseia resposta para extrair exatamente 3 passos numerados
  - Retorna `{"step1": ..., "step2": ..., "step3": ...}`

Estrutura do prompt:

```
Você é o GateMate, um assistente empático de aeroporto.
O passageiro {nome} está no voo {número} com status {status}.
Tempo estimado de espera: {tempo}.

Serviços disponíveis no aeroporto:
{lista de serviços}

Gere um plano de ação com EXATAMENTE 3 passos numerados (1., 2., 3.)
em português (pt-BR), em primeira pessoa do plural, cada passo
sendo uma instrução direta e acionável.
```

### Frontend

#### Fluxo de 3 Passos

```
Passo 1: BookingForm.jsx
  ├── Input: código de reserva (1–20 chars alfanuméricos)
  ├── Validação local: campo vazio ou só espaços → erro sem chamar API
  ├── POST /api/booking
  └── Sucesso → exibe FlightInfo + transição para Passo 2

Passo 2: FlightInfo.jsx + campo de necessidade
  ├── Exibe: nome, voo, status
  ├── Input: descrição da necessidade (1–500 chars)
  ├── POST /api/recommend
  └── Sucesso → exibe ActionPlan (Passo 3)

Passo 3: ActionPlan.jsx
  └── Lista numerada com os 3 passos, separação visual entre eles
```

#### `api.js`

```javascript
// Dois métodos principais:
export async function lookupBooking(bookingCode)   // POST /api/booking
export async function getRecommendation(bookingCode, needDescription) // POST /api/recommend
```

Ambos lançam erros com mensagens em português extraídas do campo `detail` da resposta da API, ou mensagem genérica de indisponibilidade após 30 segundos.

---

## Data Models

### Tabelas Existentes (`airportdb`)

> Schema inferido do domínio; o banco já existe no TiDB Cloud.

```sql
-- Reserva do passageiro
booking (
  booking_id    VARCHAR(6)   PRIMARY KEY,  -- código alfanumérico
  passenger_id  INT          NOT NULL,
  flight_id     INT          NOT NULL
)

-- Passageiro
passenger (
  passenger_id  INT          PRIMARY KEY AUTO_INCREMENT,
  first_name    VARCHAR(100) NOT NULL,
  last_name     VARCHAR(100) NOT NULL
)

-- Detalhes adicionais (join necessário para nome completo)
passengerdetails (
  passenger_id  INT          PRIMARY KEY,
  -- outros campos de detalhe
)

-- Voo
flight (
  flight_id     INT          PRIMARY KEY AUTO_INCREMENT,
  flight_number VARCHAR(10)  NOT NULL,
  origin        VARCHAR(3)   NOT NULL,   -- código IATA
  destination   VARCHAR(3)   NOT NULL,
  departure_time DATETIME    NOT NULL,
  status        ENUM('Scheduled','Delayed','Cancelled','Landed') NOT NULL
)
```

Query de lookup por reserva:

```sql
SELECT
    p.first_name, p.last_name,
    f.flight_number, f.origin, f.destination,
    f.departure_time, f.status
FROM booking b
JOIN passenger p ON b.passenger_id = p.passenger_id
JOIN flight f    ON b.flight_id    = f.flight_id
WHERE b.booking_id = :booking_code;
```

### Tabela Nova (`airport_services`)

```sql
CREATE TABLE IF NOT EXISTS airport_services (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(255)  NOT NULL,
    category    VARCHAR(100)  NOT NULL,
    location    VARCHAR(255)  NOT NULL,
    description TEXT          NOT NULL,
    embedding   VECTOR(1024)
);
```

Categorias obrigatórias (mínimo 3 registros cada):
`café/alimentação`, `carregadores elétricos`, `lounges`, `farmácia`, `portões de embarque`, `banheiros`, `loja de conveniência`

### Estrutura de Resposta da API

```python
# Resposta de /api/booking
class BookingResponse(BaseModel):
    passenger_name: str
    flight_number:  str
    origin:         str
    destination:    str
    departure_time: str   # ISO 8601
    status:         Literal["Scheduled", "Delayed", "Cancelled", "Landed"]

# Resposta de /api/recommend
class ActionPlanResponse(BaseModel):
    step1: str
    step2: str
    step3: str

# Resposta de erro (padrão FastAPI)
class ErrorResponse(BaseModel):
    detail: str
```

### Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `TIDB_HOST` | Host do cluster TiDB Cloud |
| `TIDB_PORT` | Porta (padrão: 4000) |
| `TIDB_USER` | Usuário do banco |
| `TIDB_PASSWORD` | Senha do banco |
| `TIDB_DB` | Nome do banco (`airportdb`) |
| `AWS_ACCESS_KEY_ID` | Chave de acesso AWS |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta AWS |
| `AWS_DEFAULT_REGION` | Região Bedrock (`ap-southeast-1`) |
| `AWS_BEARER_TOKEN_BEDROCK` | Token Bearer para Bedrock (se necessário) |

---

## Correctness Properties

*Uma propriedade é uma característica ou comportamento que deve ser verdadeiro em todas as execuções válidas de um sistema — essencialmente, uma declaração formal sobre o que o sistema deve fazer. Propriedades servem como ponte entre especificações legíveis por humanos e garantias de corretude verificáveis por máquina.*

### Property 1: Validação de código de reserva rejeita entradas inválidas

*Para qualquer* string que não seja composta exclusivamente por 6 caracteres alfanuméricos, a API SHALL retornar erro de validação sem acionar consulta ao banco de dados.

**Validates: Requirements 1.2**

### Property 2: Busca vetorial retorna resultados em ordem crescente de distância

*Para qualquer* consulta de necessidade válida (1–500 caracteres), a lista de serviços retornada pela busca semântica SHALL estar ordenada em ordem crescente de distância de cosseno — ou seja, para quaisquer dois resultados consecutivos `r[i]` e `r[i+1]`, `r[i].distance <= r[i+1].distance`.

**Validates: Requirements 3.2**

### Property 3: Plano de ação sempre possui exatamente 3 passos não-vazios

*Para qualquer* combinação válida de dados de passageiro e lista de serviços relevantes, a resposta parseada do Bedrock SHALL conter exatamente 3 campos (`step1`, `step2`, `step3`), todos com conteúdo não-vazio e não-nulo.

**Validates: Requirements 4.2, 4.3**

### Property 4: Descrição de necessidade vazia ou muito longa é sempre rejeitada

*Para qualquer* string com comprimento zero ou superior a 500 caracteres, a busca semântica SHALL retornar erro de validação sem executar consulta vetorial no banco de dados.

**Validates: Requirements 3.3**

### Property 5: Idempotência da consulta de reserva

*Para qualquer* código de reserva válido existente no banco, múltiplas chamadas ao endpoint `POST /api/booking` com o mesmo código SHALL retornar os mesmos dados de passageiro e voo, independentemente da ordem ou quantidade de chamadas.

**Validates: Requirements 1.1**

---

## Error Handling

### Camadas de Erro

```
Frontend (React)
  └── Captura erros de fetch (network, timeout 30s)
      └── Exibe mensagem em português sem detalhes técnicos

FastAPI (main.py)
  ├── Validação de input → HTTP 400 com detail legível
  ├── DatabaseUnavailableError → HTTP 503 "Serviço de dados indisponível"
  ├── BedrockTimeoutError → HTTP 504 "Tempo limite excedido ao gerar recomendações"
  └── BedrockServiceError (após retries) → HTTP 503 "Falha no serviço de recomendações"

db.py
  └── pymysql.OperationalError → DatabaseUnavailableError

bedrock_client.py
  ├── Credenciais ausentes → BedrockUnavailableError (falha na inicialização)
  ├── Timeout (10s) → BedrockTimeoutError
  └── Erro de serviço → retry 2x com 1s de intervalo → BedrockServiceError

tidb_vector.py
  ├── Input vazio ou > 500 chars → VectorSearchValidationError
  ├── EMBED_TEXT falha → VectorSearchError
  └── Tabela vazia → lista vazia (sem exceção)
```

### Hierarquia de Exceções Customizadas

```python
class GateMateError(Exception): pass
class DatabaseUnavailableError(GateMateError): pass
class BedrockUnavailableError(GateMateError): pass
class BedrockTimeoutError(GateMateError): pass
class BedrockServiceError(GateMateError): pass
class VectorSearchValidationError(GateMateError): pass
class VectorSearchError(GateMateError): pass
```

### Mensagens de Erro para o Passageiro

| Código HTTP | Mensagem exibida no frontend |
|---|---|
| 400 (reserva inválida) | "Código de reserva inválido. Por favor, verifique e tente novamente." |
| 400 (não encontrada) | "Reserva não encontrada. Confirme seu código e tente novamente." |
| 400 (entrada vazia/longa) | "Por favor, descreva sua necessidade em até 500 caracteres." |
| 503 | "Serviço temporariamente indisponível. Tente novamente em alguns instantes." |
| 504 | "A geração do seu plano está demorando mais que o esperado. Tente novamente." |
| timeout frontend | "Não foi possível conectar ao serviço. Tente novamente em breve." |

---

## Testing Strategy

### Testes Unitários (pytest)

Foco em exemplos específicos, casos de borda e condições de erro:

- **`test_booking_validation`**: código com caracteres especiais, tamanho 5, tamanho 7, vazio, espaços
- **`test_booking_lookup`**: reserva existente retorna campos corretos; reserva inexistente retorna 400
- **`test_vector_search_validation`**: string vazia, string com 501 chars rejeitadas; string com 1 char e 500 chars aceitas
- **`test_vector_search_ordering`**: mock do banco retorna registros fora de ordem → verifica ordenação
- **`test_action_plan_parsing`**: resposta do Bedrock com 3 passos bem formatados → parse correto; resposta malformada → erro
- **`test_bedrock_retry`**: mock de falha de serviço → verifica 2 retries com intervalo de 1s
- **`test_bedrock_timeout`**: mock de timeout → verifica HTTP 504
- **`test_env_validation`**: variáveis ausentes → exit não-zero com nomes das variáveis

### Testes de Propriedade (pytest + Hypothesis)

Cada propriedade do design recebe um único teste de propriedade com mínimo de 100 iterações:

```python
# Feature: gatemate, Property 1: booking validation rejects invalid inputs
@given(st.text().filter(lambda s: not re.match(r'^[A-Za-z0-9]{6}$', s)))
@settings(max_examples=100)
def test_property_booking_validation(invalid_code):
    ...

# Feature: gatemate, Property 2: vector search results ordered by distance
@given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=1, max_size=5))
@settings(max_examples=100)
def test_property_vector_search_ordering(distances):
    ...

# Feature: gatemate, Property 3: action plan always has exactly 3 non-empty steps
@given(passenger_name=st.text(min_size=1), services=st.lists(service_strategy, min_size=0, max_size=5))
@settings(max_examples=100)
def test_property_action_plan_structure(passenger_name, services):
    ...

# Feature: gatemate, Property 4: empty/oversized need description always rejected
@given(st.one_of(st.just(""), st.text(min_size=501)))
@settings(max_examples=100)
def test_property_need_description_validation(invalid_input):
    ...

# Feature: gatemate, Property 5: booking lookup idempotency
@given(booking_code=st.from_regex(r'[A-Za-z0-9]{6}'))
@settings(max_examples=100)
def test_property_booking_idempotency(booking_code):
    ...
```

Biblioteca: **Hypothesis** (Python), padrão para property-based testing no ecossistema pytest.

### Testes de Integração

Executados manualmente ou em CI com ambiente TiDB + AWS reais:

- `POST /api/booking` com código existente → resposta em < 3 segundos
- `POST /api/recommend` com necessidade válida → plano com 3 passos em < 12 segundos (2s busca + 10s Bedrock)
- `GET /health` → HTTP 200

### Testes de Fumaça (Smoke Tests)

- API inicia sem erros com todas as variáveis do `.env.example` preenchidas
- Frontend acessível na porta 3000 após `npm run dev`
- Tabela `airport_services` existe e contém ≥ 30 registros após `python seed.py`
