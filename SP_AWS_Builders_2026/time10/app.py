"""Ask the Airport — pergunta em português entra, SQL + explicação de risco saem."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db import get_connection, get_schema_context
from bedrock_client import generate_sql, explain_results
from vector_search import search_similar

app = FastAPI(title="Ask the Airport")

FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "create", "truncate", "grant", ";--")


class AskRequest(BaseModel):
    question: str


class SimilarRequest(BaseModel):
    query: str
    limit: int = 5


@app.post("/api/ask")
def ask(req: AskRequest):
    schema = get_schema_context()
    sql = generate_sql(req.question, schema)

    lowered = sql.lower().strip()
    if not lowered.startswith("select") or any(word in lowered for word in FORBIDDEN):
        return {"error": "SQL gerado não parece seguro, tente reformular a pergunta.", "sql": sql}

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    except Exception as exc:
        # SQL gerado pode não rodar (coluna inexistente, palavra reservada). Devolve o erro em
        # vez de estourar 500, pra a tela mostrar o que aconteceu em vez de "Erro: [object]".
        return {"error": f"O SQL gerado não rodou no banco: {exc}", "sql": sql}
    finally:
        conn.close()

    answer = explain_results(req.question, sql, rows)
    return {"sql": sql, "rows": rows, "answer": answer}


@app.post("/api/similar")
def similar(req: SimilarRequest):
    """Busca semântica: o TiDB calcula o embedding da frase (EMBED_TEXT) e ordena as notas de
    voo por VEC_COSINE_DISTANCE. Nenhum serviço de embedding externo no caminho."""
    try:
        rows = search_similar(req.query, min(max(req.limit, 1), 20))
    except Exception as exc:
        return {"error": f"Busca vetorial falhou: {exc}"}
    return {"query": req.query, "results": rows}


@app.get("/api/health")
def health():
    return {"ok": True}


# serve o front-end estático por último, pra não pisar nas rotas /api/*
app.mount("/", StaticFiles(directory="static", html=True), name="static")
