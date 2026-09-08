"""Acesso ao TiDB via pymysql. Conexão por requisição (simples e robusto para o protótipo).
Todas as queries de negócio recebem o tenant (airline_id) do token — nunca do cliente."""
import pymysql
from pymysql.cursors import DictCursor
from .config import get_settings


def _connect():
    s = get_settings()
    return pymysql.connect(
        host=s.tidb_host, port=s.tidb_port, user=s.tidb_user,
        password=s.tidb_password, database=s.tidb_database,
        ssl={"ca": s.tidb_ssl_ca} if s.tidb_ssl_ca else None,
        cursorclass=DictCursor, autocommit=True,
        connect_timeout=15, read_timeout=60, write_timeout=60,
    )


def query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql: str, params: tuple | dict | None = None) -> int:
    """Executa INSERT/UPDATE/DELETE e retorna lastrowid (ou rowcount)."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.lastrowid or cur.rowcount
    finally:
        conn.close()
