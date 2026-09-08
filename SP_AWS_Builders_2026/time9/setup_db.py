#!/usr/bin/env python3
"""Cria as tabelas do AirRevenue no TiDB e popula:
  - airline_user: 1 usuário por companhia de demo (senha bcrypt)
  - flight_notes: nota textual por voo (amostra) com coluna VECTOR gerada por EMBED_TEXT
Lê credenciais do backend/.env (ou variáveis de ambiente)."""
import os
import sys

# permite rodar de qualquer lugar, achando o pacote app/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app.config import get_settings          # noqa: E402
from app import db                            # noqa: E402
from app.security import hash_password        # noqa: E402

DEMO_AIRLINES = [82, 66, 73, 80, 99, 81]  # top companhias por nº de voos
DEMO_PASSWORD = os.environ.get("SEED_PASSWORD", "airrevenue2026")

DDL = [
    """CREATE TABLE IF NOT EXISTS airline_user (
        id BIGINT AUTO_RANDOM PRIMARY KEY,
        airline_id SMALLINT NOT NULL,
        username VARCHAR(64) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS campaign (
        id BIGINT AUTO_RANDOM PRIMARY KEY,
        airline_id SMALLINT NOT NULL,
        flight_id INT NOT NULL,
        title VARCHAR(140) NOT NULL,
        body TEXT NOT NULL,
        discount_pct INT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'draft',
        created_by BIGINT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_campaign_airline (airline_id)
    )""",
    """CREATE TABLE IF NOT EXISTS campaign_target (
        id BIGINT AUTO_RANDOM PRIMARY KEY,
        campaign_id BIGINT NOT NULL,
        passenger_id INT NOT NULL,
        score DOUBLE DEFAULT 0,
        INDEX idx_target_campaign (campaign_id)
    )""",
    """CREATE TABLE IF NOT EXISTS flight_notes (
        id BIGINT AUTO_RANDOM PRIMARY KEY,
        airline_id SMALLINT NOT NULL,
        flight_id INT NOT NULL,
        note TEXT NOT NULL,
        embedding VECTOR(1024) GENERATED ALWAYS AS (
          EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', note)
        ) STORED,
        INDEX idx_notes_airline (airline_id)
    )""",
]


def main():
    s = get_settings()
    print(f"TiDB {s.tidb_host}:{s.tidb_port} db={s.tidb_database}")

    for stmt in DDL:
        db.execute(stmt)
    print("Tabelas criadas/verificadas.")

    # usuários por companhia (idempotente)
    ph = hash_password(DEMO_PASSWORD)
    for aid in DEMO_AIRLINES:
        uname = f"airline{aid}"
        exists = db.query("SELECT id FROM airline_user WHERE username=%s", (uname,))
        if not exists:
            db.execute(
                "INSERT INTO airline_user(airline_id, username, password_hash) VALUES(%s,%s,%s)",
                (aid, uname, ph),
            )
    users = db.query("SELECT username, airline_id FROM airline_user ORDER BY airline_id")
    print(f"Usuários ({len(users)}):", ", ".join(f"{u['username']}(cia {u['airline_id']})" for u in users))

    # flight_notes: uma nota descritiva por voo (amostra) para as companhias de demo
    placeholders = ",".join(["%s"] * len(DEMO_AIRLINES))
    already = db.query("SELECT COUNT(*) c FROM flight_notes")[0]["c"]
    if already == 0:
        rows = db.query(
            f"""SELECT f.flight_id, f.airline_id, f.flightno,
                       go.city AS o, gd.city AS d, HOUR(f.departure) AS h
                FROM flight f
                LEFT JOIN airport_geo go ON go.airport_id=f.`from`
                LEFT JOIN airport_geo gd ON gd.airport_id=f.`to`
                WHERE f.airline_id IN ({placeholders})""",
            tuple(DEMO_AIRLINES),
        )
        n = 0
        for r in rows:
            periodo = ("madrugada" if r["h"] < 6 else "manhã" if r["h"] < 12
                       else "tarde" if r["h"] < 18 else "noite")
            note = (f"Voo {r['flightno']} de {r['o']} para {r['d']}, partida no período da "
                    f"{periodo}. Rota operada pela companhia {r['airline_id']}.")
            db.execute(
                "INSERT INTO flight_notes(airline_id, flight_id, note) VALUES(%s,%s,%s)",
                (r["airline_id"], r["flight_id"], note),
            )
            n += 1
        print(f"flight_notes inseridas: {n} (embedding VECTOR gerado pelo TiDB via EMBED_TEXT)")
    else:
        print(f"flight_notes já populada ({already} linhas).")

    print("SEED OK")


if __name__ == "__main__":
    main()
