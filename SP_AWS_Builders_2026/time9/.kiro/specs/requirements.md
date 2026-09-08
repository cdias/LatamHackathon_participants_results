# AirRevenue — Requirements (spec-driven, Kiro)

## Introdução
Copiloto de revenue management que recomenda promoções para voos ociosos e cria campanhas
direcionadas a passageiros frequentes, multi-tenant por companhia, com segurança zero-trust.
Dados no TiDB, IA no Amazon Bedrock, deploy na AWS (EC2).

## Requirements

### R1 — Autenticação por companhia
**User story:** Como revenue manager, quero entrar na área da minha companhia com usuário/senha.
- WHEN credenciais válidas THEN o sistema retorna um JWT com o `airline_id`.
- WHEN credenciais inválidas THEN retorna 401.
- O token expira em ≤ 60 min.

### R2 — Isolamento multi-tenant (zero-trust)
**User story:** Como companhia, quero ver apenas os meus dados.
- WHEN qualquer rota de dado é chamada THEN o `airline_id` vem do token, nunca do cliente.
- WHEN não há token válido THEN retorna 401.
- WHEN o recurso é de outra companhia THEN retorna 404 (não vaza existência).

### R3 — Recomendação de voos ociosos
- WHEN o usuário abre as recomendações THEN o sistema lista voos futuros da companhia
  ordenados por `assentos_ociosos × urgência`, só com ociosidade ≥ 20%.

### R4 — Alvos por propensão
- WHEN um voo é selecionado THEN lista passageiros frequentes da companhia, priorizando quem
  já voou a mesma rota; PII de contato mascarada.

### R5 — Geração de texto com IA
- WHEN o usuário pede o texto THEN o sistema chama o Bedrock (Claude 3 Haiku).
- IF o Bedrock falhar THEN usa um template local (o produto não quebra).

### R6 — Campanhas
- WHEN o usuário salva THEN persiste a campanha + alvos vinculados ao `airline_id`.
- WHEN lista campanhas THEN mostra só as da companhia.

### R7 — Busca vetorial
- WHEN o usuário busca por texto THEN o sistema usa `VEC_COSINE_DISTANCE` + `EMBED_TEXT`
  sobre `flight_notes` do tenant e retorna os mais próximos.

### R8 — Segurança e segredos
- Segredos apenas em `.env` (git-ignored); senhas com hash bcrypt; CORS restrito; erros genéricos.
