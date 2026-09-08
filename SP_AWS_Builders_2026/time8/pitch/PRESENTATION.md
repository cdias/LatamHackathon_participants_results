# GateMate — Deck de Apresentação

---

## Slide 1 — Capa

```
╔══════════════════════════════════════════╗
║                                          ║
║   ✈  GateMate                           ║
║                                          ║
║   Copiloto pessoal do passageiro         ║
║   conectado                              ║
║                                          ║
║   Hackathon TiDB × AWS · SP · 2026      ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## Slide 2 — O Problema

**Todo passageiro já viveu isso:**

| Situação | O que acontece hoje |
|---|---|
| Voo atrasado 2h | App mostra "Delayed". Só. |
| Conexão de 45min | Sem orientação de rota |
| Celular sem bateria | Você que se vire |
| Criança com fome | Nenhum serviço próximo sugerido |

> O aeroporto tem tudo que você precisa.
> Ninguém te conta onde está.

---

## Slide 3 — A Solução

```
  Código de reserva
         │
         ▼
  ┌─────────────────┐
  │   GateMate      │  ← "preciso de café e tomada
  │   sabe seu voo  │     perto do portão 12"
  │   seu status    │
  │   seu tempo     │
  └────────┬────────┘
           │
           ▼
    Plano de 3 passos
    empático e acionável
    em português
```

**Interface**: https://airport-concierge-ai.lovable.app/

---

## Slide 4 — Como Funciona (Fluxo)

```
Passo 1 ──────────────────────────────────
  Passageiro digita código de reserva
  → TiDB consulta booking + passenger + flight
  → Retorna: nome, voo, status, horário

Passo 2 ──────────────────────────────────
  Passageiro descreve necessidade
  → TiDB gera embedding com EMBED_TEXT
  → VEC_COSINE_DISTANCE busca os 5 serviços
    mais próximos semanticamente

Passo 3 ──────────────────────────────────
  Contexto enviado ao Bedrock
  → Claude 3 Haiku gera plano de 3 passos
  → Empático, em pt-BR, acionável
```

---

## Slide 5 — Features Principais

### ✅ Busca por Código de Reserva
- Integração direta com o dataset `airportdb`
- Tabelas: `booking`, `passenger`, `flight`
- Sem login, sem fricção

### ✅ Busca Vetorial Semântica (TiDB)
- Tabela `airport_services` com `VECTOR(1024)`
- `EMBED_TEXT` nativo — sem Bedrock para embeddings
- Query: linguagem natural → serviços relevantes

### ✅ Plano de Ação com IA (Bedrock)
- Modelo: `anthropic.claude-3-haiku-20240307-v1:0`
- Região: `ap-southeast-1` (Singapura)
- Output: 3 passos numerados, pt-BR, tom empático

### ✅ Interface Conversacional
- React (Vite) + FastAPI
- Fluxo de 3 etapas guiadas
- Sem cadastro, funciona com código de reserva

---

## Slide 6 — A Tech Stack

```
┌─────────────────────────────────────────────┐
│  Frontend: React (Vite) · porta 3000        │
│  Backend:  FastAPI (Python) · porta 8000    │
├─────────────────────────────────────────────┤
│  Banco:    TiDB Cloud Starter               │
│            sa-east-1 (São Paulo)            │
│            VECTOR(1024) + EMBED_TEXT        │
├─────────────────────────────────────────────┤
│  IA:       Amazon Bedrock                   │
│            ap-southeast-1 (Singapura)       │
│            Claude 3 Haiku                   │
├─────────────────────────────────────────────┤
│  Deploy:   EC2 sa-east-1                    │
│  Spec:     Kiro (.kiro/ commitado)          │
└─────────────────────────────────────────────┘
```

---

## Slide 7 — Pontuação Esperada

| Critério | Pts | Status |
|---|---|---|
| ✅ Funciona na demo | 20 | App rodando ao vivo |
| ✅ Inovação — concierge semântico | 15 | Busca vetorial + LLM |
| ✅ Valor de negócio real | 15 | Passageiro estressado |
| ✅ Demo e pitch claros | 10 | 2 min, mostra funcionando |
| ✅ TiDB Cloud Starter AWS | 10 | sa-east-1 |
| ✅ Busca vetorial no TiDB | 8 | EMBED_TEXT + VEC_COSINE |
| ✅ Amazon Bedrock | 8 | Claude Haiku ap-southeast-1 |
| ✅ Publicado na EC2 | 8 | sa-east-1, porta 8000 |
| ✅ Construído com Kiro | 6 | .kiro/ commitado |
| **TOTAL** | **100** | 🎯 |

---

## Slide 8 — Fechamento

```
╔══════════════════════════════════════════════╗
║                                              ║
║  "A companhia aérea te dá o número          ║
║   do portão.                                 ║
║                                              ║
║   O GateMate te dá o próximo passo."        ║
║                                              ║
║  ✈  airport-concierge-ai.lovable.app        ║
║                                              ║
╚══════════════════════════════════════════════╝
```

