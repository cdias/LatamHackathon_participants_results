# ✈️ AirRevenue

Copiloto de *revenue management* para companhias aéreas: recomenda **promoções para voos com
assentos ociosos** e cria **campanhas direcionadas** a passageiros frequentes. Multi-tenant por
companhia, com **segurança zero-trust**.

Feito no **Hackathon TiDB × AWS 2026**. Dados no **TiDB Cloud**, IA no **Amazon Bedrock**,
busca **vetorial no TiDB**, deploy na **AWS EC2**, spec-driven com **Kiro**.

## Arquitetura
![arquitetura](docs/architecture.png)

- **Frontend:** Vue 3 (Vite) — `frontend/`
- **Backend:** FastAPI — `backend/`
- **Dados:** TiDB Cloud (`airportdb` + tabelas de campanha, coluna `VECTOR`)
- **IA:** Amazon Bedrock (Claude 3 Haiku, ap-southeast-1) com fallback

## Rodar
Veja [SUBMISSION.md](SUBMISSION.md#como-rodar).

## Segurança
JWT curto, isolamento multi-tenant (tenant sempre do token), PII mascarada, segredos só em
`.env`. Testes em `tests/scanapi.yaml`.

## Documentação
- Descritivo de negócio: `docs/01-descritivo-negocio.md`
- Arquitetura: `docs/02-arquitetura.md`
- Especificação técnica: `docs/03-especificacao-tecnica.md`
- Specs Kiro: `.kiro/specs/`
- Pitch: `docs/pitch.html`
