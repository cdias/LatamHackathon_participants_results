"""Conexão com o TiDB Cloud e introspecção de schema (para grounding do NL->SQL)."""
import os
import certifi
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymysql.connect(
        host=os.environ["TIDB_HOST"],
        port=int(os.environ.get("TIDB_PORT", 4000)),
        user=os.environ["TIDB_USER"],
        password=os.environ["TIDB_PASSWORD"],
        database=os.environ.get("TIDB_DATABASE", "airportdb"),
        ssl={"ca": certifi.where()},  # certifi funciona em qualquer SO (Linux/Mac/Windows)
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


_SCHEMA_CACHE = None


def get_schema_context(force_refresh: bool = False) -> str:
    """Puxa o CREATE TABLE de cada tabela do banco. Isso ancora o LLM nos nomes de
    coluna reais em vez de a gente adivinhar o schema do dump."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE and not force_refresh:
        return _SCHEMA_CACHE

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cur.fetchall()]
            parts = []
            for t in tables:
                cur.execute(f"SHOW CREATE TABLE `{t}`")
                row = cur.fetchone()
                create_stmt = list(row.values())[1]
                parts.append(create_stmt)
            _SCHEMA_CACHE = "\n\n".join(parts)
            return _SCHEMA_CACHE
    finally:
        conn.close()


if __name__ == "__main__":
    # rode `python db.py` pra conferir a conexão e ver o schema real na tela
    print(get_schema_context())
