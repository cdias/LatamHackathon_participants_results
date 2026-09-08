# Design — Ask the Airport Copilot

## Fluxo
1. Usuário digita uma pergunta em `static/index.html`.
2. `POST /api/ask` (`app.py`) recebe a pergunta.
3. `db.get_schema_context()` traz o schema real (cacheado após a primeira chamada).
4. `bedrock_client.generate_sql()` pede pro Claude Haiku (Bedrock) gerar um único SELECT,
   com instrução explícita de fazer JOIN com `weatherdata` quando a pergunta for sobre risco.
5. `app.py` valida que é só SELECT e executa no TiDB via `db.get_connection()`.
6. `bedrock_client.explain_results()` pede pro Claude 3.5 Sonnet explicar o resultado em
   português simples, destacando risco de disrupção quando os dados de clima indicarem.
7. Resposta (SQL + linhas + explicação) volta pro front-end.

## Busca vetorial (concierge semântico)
- `flight_notes.embedding` é uma coluna `VECTOR(1024) GENERATED ALWAYS AS (EMBED_TEXT(...))`.
- Populada com notas sintéticas cruzando voo + clima (`seed_vector_notes.py`).
- Consulta usa `ORDER BY VEC_COSINE_DISTANCE(embedding, EMBED_TEXT(...))`.

## Por que essa arquitetura
- Simples o bastante pra terminar no sprint: um endpoint, duas chamadas ao Bedrock, uma
  tabela extra.
- Schema introspectado em runtime evita retrabalho se o dump tiver nomes de coluna
  diferentes do esperado.
