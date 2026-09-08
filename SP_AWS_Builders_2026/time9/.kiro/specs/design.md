# AirRevenue — Design (spec-driven, Kiro)

## Arquitetura
- **Frontend:** Vue 3 (Vite, SPA) — área por companhia. JWT em memória (reduz XSS).
- **Backend:** FastAPI + Uvicorn na EC2 (sa-east-1), porta 8000, bind `0.0.0.0`.
- **Dados:** TiDB Cloud (MySQL-compat), TLS na 4000. Tabelas do `airportdb` (RO) + novas (RW).
- **IA:** Amazon Bedrock em ap-southeast-1 (Claude 3 Haiku), com fallback local.

## Componentes do backend
- `config.py` — settings via env (zero hardcode).
- `db.py` — acesso TiDB (pymysql), helpers query/execute.
- `security.py` — bcrypt, JWT HS256, dependência `current_tenant` (tenant do token).
- `services.py` — regras: recommend_flights, flight_targets, create_campaign, list_campaigns, vector_search.
- `bedrock.py` — geração de texto com fallback.
- `main.py` — rotas FastAPI, CORS, zero-trust.

## Modelo de dados (novas tabelas)
`airline_user`, `campaign`, `campaign_target`, `flight_notes(embedding VECTOR(1024) STORED)`.

## Decisões
- **Data-âncora** `2015-06-02` como "agora" (dataset é de jun/2015).
- **Score de voo:** `ociosos / (1 + dias_ate_partida)`.
- **404 em vez de 403** para recurso de outro tenant (não vaza existência).
- **Deploy EC2** (conta é bedrock-only); SAM documentado em `infra/`.

## Testes
ScanAPI (`tests/scanapi.yaml`): health, 401 sem token, login inválido/válido, recomendações,
busca vetorial, token forjado → 401.
