# Implementation Plan: GateMate

## Overview

Implementação incremental do GateMate em ordem de desbloqueio de dependências: infraestrutura e configuração primeiro, depois backend core (DB + rotas), busca vetorial, cliente Bedrock, frontend e entregáveis do hackathon. Cada tarefa constrói sobre a anterior e termina com a integração completa.

## Tasks

- [ ] 1. Configuração da infraestrutura do projeto
  - [ ] 1.1 Criar estrutura de diretórios e arquivos de configuração
    - Criar diretórios `backend/`, `backend/tests/`, `frontend/` (via `npm create vite@latest`)
    - Criar `backend/requirements.txt` com versões fixas: `fastapi==0.111.0`, `uvicorn==0.29.0`, `pymysql==1.1.1`, `boto3==1.34.0`, `python-dotenv==1.0.1`, `hypothesis==6.100.0`, `pytest==8.1.0`, `pytest-asyncio==0.23.0`
    - Criar `.env.example` na raiz com todas as variáveis: `TIDB_HOST`, `TIDB_PORT`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_DB`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `AWS_BEARER_TOKEN_BEDROCK`
    - Criar `.gitignore` na raiz listando explicitamente `.env`
    - _Requirements: 6.3, 6.4, 7.1_

  - [ ] 1.2 Criar hierarquia de exceções customizadas em `backend/exceptions.py`
    - Implementar `GateMateError(Exception)` como base
    - Implementar subclasses: `DatabaseUnavailableError`, `BedrockUnavailableError`, `BedrockTimeoutError`, `BedrockServiceError`, `VectorSearchValidationError`, `VectorSearchError`
    - _Requirements: 1.4, 4.4, 4.5, 4.6, 4.7, 3.5_

- [ ] 2. Módulo de conexão com TiDB (`backend/db.py`)
  - [ ] 2.1 Implementar `db.py` com conexão pymysql + SSL
    - Carregar variáveis de ambiente via `python-dotenv` antes de qualquer conexão
    - Implementar `get_connection()` usando `pymysql.connect` com `ssl={"ca": "/etc/ssl/cert.pem"}` e parâmetros do `.env`
    - Implementar `close_connection(conn)` para fechar a conexão
    - Capturar `pymysql.OperationalError` e relançar como `DatabaseUnavailableError`
    - _Requirements: 1.4, 6.1_

  - [ ]* 2.2 Escrever testes unitários para `db.py`
    - Testar que `pymysql.OperationalError` é convertido para `DatabaseUnavailableError`
    - Usar mock de `pymysql.connect` para simular falha de conexão
    - _Requirements: 1.4_

- [ ] 3. Busca vetorial e seed de dados (`backend/tidb_vector.py` e `backend/seed.py`)
  - [ ] 3.1 Implementar `search_services()` em `tidb_vector.py`
    - Validar `query`: rejeitar string vazia ou com mais de 500 caracteres lançando `VectorSearchValidationError`
    - Executar query SQL com `EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", :query)` e `VEC_COSINE_DISTANCE` ordenado por `distance ASC LIMIT 5`
    - Retornar lista de `{"name": str, "description": str, "distance": float}` ou lista vazia se sem resultados
    - Capturar erros de execução SQL e relançar como `VectorSearchError`
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 3.2 Escrever teste de propriedade para `search_services` — Property 2
    - **Property 2: Busca vetorial retorna resultados em ordem crescente de distância**
    - **Validates: Requirements 3.2**
    - Usar `@given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=1, max_size=5))` com mock do banco
    - _Requirements: 3.2_

  - [ ]* 3.3 Escrever teste de propriedade para validação de `need_description` — Property 4
    - **Property 4: Descrição de necessidade vazia ou muito longa é sempre rejeitada**
    - **Validates: Requirements 3.3**
    - Usar `@given(st.one_of(st.just(""), st.text(min_size=501)))` para verificar que `VectorSearchValidationError` é sempre lançado
    - _Requirements: 3.3_

  - [ ]* 3.4 Escrever testes unitários para `search_services`
    - Testar string vazia → `VectorSearchValidationError`; string com 501 chars → `VectorSearchValidationError`
    - Testar string com 1 char e 500 chars → aceitas
    - Testar retorno de lista vazia quando banco está vazio (sem exceção)
    - _Requirements: 3.3, 3.4_

  - [ ] 3.5 Implementar `seed_airport_services()` em `tidb_vector.py` e `backend/seed.py`
    - Criar tabela `airport_services` com `CREATE TABLE IF NOT EXISTS` com colunas: `id INT PRIMARY KEY AUTO_INCREMENT`, `name VARCHAR(255)`, `category VARCHAR(100)`, `location VARCHAR(255)`, `description TEXT`, `embedding VECTOR(1024)`
    - Definir 30+ registros sintéticos cobrindo as 7 categorias obrigatórias (mínimo 3 por categoria): café/alimentação, carregadores elétricos, lounges, farmácia, portões de embarque, banheiros, loja de conveniência
    - Inserir cada registro com `EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", description)` para preencher `embedding`
    - Em caso de falha no `EMBED_TEXT` de um registro, interromper e exibir mensagem indicando o `name` do registro, sem inserções parciais
    - Exibir contagem total ao final do seed bem-sucedido
    - `seed.py` chama `seed_airport_services()` diretamente
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 4. Cliente Amazon Bedrock (`backend/bedrock_client.py`)
  - [ ] 4.1 Implementar inicialização e `generate_action_plan()` em `bedrock_client.py`
    - Inicializar `boto3.client("bedrock-runtime", region_name="ap-southeast-1")` — NUNCA `sa-east-1`
    - Falhar na inicialização se credenciais AWS ausentes, lançando `BedrockUnavailableError`
    - Implementar `generate_action_plan(passenger_name, flight_number, flight_status, wait_time, services) -> dict`
    - Montar prompt em português (pt-BR) instruindo o modelo a retornar exatamente 3 passos numerados (1., 2., 3.) em primeira pessoa do plural
    - Chamar `invoke_model` com timeout de 10 segundos; lançar `BedrockTimeoutError` se excedido
    - Retry de até 2 vezes com `time.sleep(1)` em erro de serviço; após esgotar, lançar `BedrockServiceError`
    - Parsear a resposta para extrair `step1`, `step2`, `step3` como strings não-vazias
    - Retornar `{"step1": str, "step2": str, "step3": str}`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 4.2 Escrever teste de propriedade para estrutura do plano de ação — Property 3
    - **Property 3: Plano de ação sempre possui exatamente 3 passos não-vazios**
    - **Validates: Requirements 4.2, 4.3**
    - Usar `@given(passenger_name=st.text(min_size=1), services=st.lists(...))` com mock do Bedrock
    - Verificar que o retorno contém exatamente os campos `step1`, `step2`, `step3` e todos são não-vazios
    - _Requirements: 4.2, 4.3_

  - [ ]* 4.3 Escrever testes unitários para `bedrock_client.py`
    - Testar retry: mock de falha de serviço → verificar 2 tentativas adicionais com intervalo de 1s
    - Testar timeout: mock de timeout → verificar que `BedrockTimeoutError` é lançado
    - Testar credenciais ausentes → `BedrockUnavailableError` na inicialização
    - Testar parse de resposta com 3 passos bem formatados → retorno correto
    - _Requirements: 4.4, 4.5, 4.6, 4.7_

- [ ] 5. Aplicação FastAPI (`backend/main.py`)
  - [ ] 5.1 Implementar `main.py` com validação de ambiente, rotas e tratamento de erros
    - Validar presença e não-vacuidade de todas as variáveis obrigatórias ao inicializar; encerrar com código não-zero e listar variáveis ausentes/vazias se alguma faltar
    - Configurar `CORSMiddleware` com `allow_origins=["http://localhost:3000"]`, todos os métodos e headers
    - Implementar `GET /health` retornando `{"status": "ok"}` com HTTP 200
    - Implementar `POST /api/booking`: validar formato do código (6 chars alfanuméricos via regex); executar query SQL de lookup com JOIN em `booking`, `passenger`, `flight`; retornar `BookingResponse`; mapear `DatabaseUnavailableError` → 503, código inválido → 400, não encontrado → 400
    - Implementar `POST /api/recommend`: receber `booking_code` + `need_description`; chamar `search_services()` e `generate_action_plan()`; retornar `ActionPlanResponse`; mapear `VectorSearchValidationError` → 400, `BedrockTimeoutError` → 504, `BedrockServiceError`/`BedrockUnavailableError` → 503
    - Definir modelos Pydantic: `BookingRequest`, `BookingResponse`, `RecommendRequest`, `ActionPlanResponse`
    - Fazer bind em `0.0.0.0:8000`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.3, 4.4, 4.6, 4.7, 6.1, 6.2, 6.5, 7.4_

  - [ ]* 5.2 Escrever teste de propriedade para validação do código de reserva — Property 1
    - **Property 1: Validação de código de reserva rejeita entradas inválidas**
    - **Validates: Requirements 1.2**
    - Usar `@given(st.text().filter(lambda s: not re.match(r'^[A-Za-z0-9]{6}$', s)))` com cliente de teste FastAPI
    - Verificar que a resposta é sempre HTTP 400 sem acionar consulta ao banco
    - _Requirements: 1.2_

  - [ ]* 5.3 Escrever teste de propriedade para idempotência da consulta de reserva — Property 5
    - **Property 5: Idempotência da consulta de reserva**
    - **Validates: Requirements 1.1**
    - Usar `@given(booking_code=st.from_regex(r'[A-Za-z0-9]{6}'))` com mock do banco retornando dados fixos
    - Verificar que múltiplas chamadas com o mesmo código retornam exatamente os mesmos dados
    - _Requirements: 1.1_

  - [ ]* 5.4 Escrever testes unitários para `main.py`
    - Testar `POST /api/booking` com código inválido (especiais, tamanho 5, tamanho 7, vazio, espaços) → HTTP 400
    - Testar reserva inexistente → HTTP 400
    - Testar falha de DB → HTTP 503
    - Testar `POST /api/recommend` com entrada vazia e > 500 chars → HTTP 400
    - Testar timeout Bedrock → HTTP 504
    - Testar falha Bedrock após retries → HTTP 503
    - Testar `GET /health` → HTTP 200
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.4, 4.6, 4.7_

- [ ] 6. Checkpoint — backend funcional
  - Garantir que todos os testes de backend passam. Verificar que `uvicorn main:app --host 0.0.0.0 --port 8000` inicia sem erros com `.env` preenchido. Perguntar ao usuário se houver dúvidas.

- [ ] 7. Frontend React (`frontend/`)
  - [ ] 7.1 Implementar `frontend/src/api.js` — wrappers de fetch
    - Implementar `lookupBooking(bookingCode)`: `POST /api/booking`, lançar erro com mensagem em português do campo `detail` ou mensagem genérica após 30 segundos
    - Implementar `getRecommendation(bookingCode, needDescription)`: `POST /api/recommend`, mesmo tratamento de erros
    - Usar `AbortController` com timeout de 30 segundos para ambas as chamadas
    - _Requirements: 5.5, 5.7_

  - [ ] 7.2 Implementar `BookingForm.jsx`
    - Renderizar campo de texto para código de reserva (aceitar 1–20 chars alfanuméricos) e botão de confirmação
    - Validação local: campo vazio ou só espaços → exibir indicação de campo obrigatório sem chamar API
    - Chamar `lookupBooking()` ao submeter; exibir indicador de carregamento enquanto aguarda
    - Em erro da API, exibir mensagem em português sem expor detalhes técnicos
    - _Requirements: 5.1, 5.5, 5.6, 5.8, 5.9_

  - [ ] 7.3 Implementar `FlightInfo.jsx` com campo de necessidade
    - Receber e exibir `passenger_name`, `flight_number`, `status` do passageiro
    - Apresentar campo de texto para descrever necessidade (1–500 chars) no estilo chat
    - Chamar `getRecommendation()` ao submeter; exibir indicador de carregamento
    - Em erro, exibir mensagem em português sem detalhes técnicos
    - _Requirements: 5.2, 5.3, 5.5, 5.6_

  - [ ] 7.4 Implementar `ActionPlan.jsx`
    - Receber `step1`, `step2`, `step3` como props
    - Exibir lista numerada com separação visual entre os 3 passos
    - _Requirements: 5.4_

  - [ ] 7.5 Implementar `App.jsx` — máquina de estados de 3 passos
    - Gerenciar estados: `booking` → `need` → `plan`
    - Compor `BookingForm` → `FlightInfo` → `ActionPlan` em sequência
    - Passar dados entre etapas via props/estado
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 7.6 Escrever testes unitários para componentes do frontend
    - Testar `BookingForm`: submissão com campo vazio → erro local sem chamada à API
    - Testar `ActionPlan`: renderiza 3 passos com separação visual
    - Usar Vitest + Testing Library (já incluídos no template Vite)
    - _Requirements: 5.1, 5.4, 5.8_

- [ ] 8. Checkpoint — frontend funcional
  - Garantir que `npm run dev` inicia sem erros e a interface flui pelos 3 passos. Perguntar ao usuário se houver dúvidas.

- [ ] 9. Entregáveis do hackathon
  - [ ] 9.1 Criar `SUBMISSION.md` na raiz do repositório
    - Incluir descrição do projeto em até 500 palavras
    - Incluir passo a passo de execução local com comandos exatos para backend (`pip install -r requirements.txt`, `uvicorn main:app --host 0.0.0.0 --port 8000`) e frontend (`npm install`, `npm run dev`)
    - Incluir lista de tecnologias e bibliotecas com versões: Python 3.11+, FastAPI 0.111.0, uvicorn 0.29.0, pymysql 1.1.1, boto3 1.34.0, python-dotenv 1.0.1, React 18, Vite 5, TiDB Cloud Starter, Amazon Bedrock (claude-3-haiku), Hypothesis 6.100.0, pytest 8.1.0
    - _Requirements: 7.2_

  - [ ] 9.2 Criar `.kiro/steering.md` com diretrizes do projeto
    - Documentar stack, restrições de região (Bedrock: `ap-southeast-1`, TiDB: `sa-east-1`), convenções de código e estrutura de arquivos
    - _Requirements: 7.1_

- [ ] 10. Checkpoint final — todos os testes passando
  - Garantir que todos os testes de backend e frontend passam. Verificar que `GET /health` retorna HTTP 200. Executar `python seed.py` e confirmar ≥ 30 registros inseridos. Perguntar ao usuário se houver dúvidas.

## Notes

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia os requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental ao longo da sprint
- Os testes de propriedade usam a biblioteca **Hypothesis** (Python) com mínimo de 100 iterações cada
- A região do Bedrock é sempre `ap-southeast-1` — nunca confundir com a região do TiDB (`sa-east-1`)
- A conexão TiDB SEMPRE usa `ssl={"ca": "/etc/ssl/cert.pem"}`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "3.1", "4.1"] },
    { "id": 2, "tasks": ["2.2", "3.2", "3.3", "3.4", "4.2", "4.3", "3.5"] },
    { "id": 3, "tasks": ["5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3", "5.4", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.3", "7.4"] },
    { "id": 6, "tasks": ["7.5", "9.1", "9.2"] },
    { "id": 7, "tasks": ["7.6"] }
  ]
}
```
