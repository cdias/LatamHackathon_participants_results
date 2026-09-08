"""Busca semantica sobre flight_notes usando a coluna VECTOR do TiDB.

O embedding da pergunta e calculado pelo proprio banco (EMBED_TEXT) e comparado com
VEC_COSINE_DISTANCE — nao ha chamada a servico de embedding fora do TiDB.
"""
from db import get_connection

EMBED_MODEL = "tidbcloud_free/amazon/titan-embed-text-v2"

SIMILAR_SQL = f"""
SELECT flight_id, note,
       VEC_COSINE_DISTANCE(embedding, EMBED_TEXT('{EMBED_MODEL}', %s)) AS distancia
FROM flight_notes
ORDER BY distancia
LIMIT %s
"""


def search_similar(query: str, limit: int = 5) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SIMILAR_SQL, (query, limit))
            rows = cur.fetchall()
    finally:
        conn.close()

    for r in rows:
        # cosseno: 0 = identico, 2 = oposto. Vira "% de similaridade" pra caber na tela.
        r["similaridade"] = round((1 - float(r["distancia"])) * 100, 1)
        r["distancia"] = round(float(r["distancia"]), 4)
    return rows
