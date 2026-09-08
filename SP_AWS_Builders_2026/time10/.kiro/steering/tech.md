# Ask the Airport — Stack técnica

- **Backend**: Python + FastAPI (`app.py`)
- **Banco**: TiDB Cloud Starter (sa-east-1), dataset `airportdb`, conectado via `pymysql` (`db.py`)
- **LLM**: Amazon Bedrock (ap-southeast-1), `anthropic.claude-3-haiku` para gerar SQL rápido,
  `anthropic.claude-3-5-sonnet` para explicar o resultado (`bedrock_client.py`)
- **Busca vetorial**: coluna `VECTOR(1024)` na tabela `flight_notes`, gerada com `EMBED_TEXT`
  nativo do TiDB (sem depender do Bedrock para embeddings) — `seed_vector_notes.py`
- **Front-end**: HTML/JS estático simples (`static/index.html`), servido pelo próprio FastAPI
- **Deploy**: EC2 do time em sa-east-1, `uvicorn app:app --host 0.0.0.0 --port 8000`

## Decisões
- SQL é sempre gerado com o schema real introspectado via `SHOW CREATE TABLE` (ver
  `db.py::get_schema_context`), para não depender de suposições sobre nomes de coluna do dump.
- Só SELECT é permitido — qualquer outra operação é bloqueada antes de chegar ao banco.
- Prompt de geração de SQL sabe que perguntas de risco/disrupção devem fazer JOIN com
  `weatherdata`.
