"""Regras de negócio. TODAS as funções recebem airline_id do token (tenant) e o aplicam
no WHERE — isolamento multi-tenant (RN-004). Nunca confiar em tenant vindo do cliente."""
from .config import get_settings
from . import db


def airline_name(airline_id: int) -> str:
    rows = db.query("SELECT airlinename FROM airline WHERE airline_id=%s", (airline_id,))
    return rows[0]["airlinename"] if rows else f"Airline {airline_id}"


def flight_avg_price(airline_id: int, flight_id: int) -> float:
    """Preço médio do voo (base para o preço antigo). Valida posse do tenant.
    Se o voo não tiver reservas, usa a média da companhia como estimativa."""
    rows = db.query(
        """SELECT AVG(b.price) AS avg_price
           FROM booking b JOIN flight f ON f.flight_id=b.flight_id
           WHERE b.flight_id=%s AND f.airline_id=%s""",
        (flight_id, airline_id),
    )
    if rows and rows[0]["avg_price"] is not None:
        return round(float(rows[0]["avg_price"]), 2)
    fb = db.query(
        """SELECT AVG(b.price) AS avg_price FROM booking b
           JOIN flight f ON f.flight_id=b.flight_id WHERE f.airline_id=%s""",
        (airline_id,),
    )
    return round(float(fb[0]["avg_price"]), 2) if fb and fb[0]["avg_price"] else 0.0


def recommend_flights(airline_id: int, limit: int = 20) -> list[dict]:
    """RF-003 / RN-001: voos futuros (vs anchor) da companhia, ranqueados por
    assentos ociosos * urgência. Só ociosidade >= 20%."""
    anchor = get_settings().anchor_now
    sql = """
    SELECT f.flight_id, f.flightno,
           COALESCE(NULLIF(go.city, ''), ao.name) AS origem,
           COALESCE(NULLIF(gd.city, ''), ad.name) AS destino,
           COALESCE(NULLIF(ao.iata, ''), ao.icao) AS from_iata,
           COALESCE(NULLIF(ad.iata, ''), ad.icao) AS to_iata,
           f.departure,
           ap.capacity,
           COUNT(b.booking_id) AS vendidos,
           (ap.capacity - COUNT(b.booking_id)) AS ociosos,
           ROUND(100*(ap.capacity - COUNT(b.booking_id))/ap.capacity, 1) AS ociosidade_pct,
           DATEDIFF(f.departure, %(anchor)s) AS dias_ate_partida,
           ROUND((ap.capacity - COUNT(b.booking_id)) /
                 (1 + GREATEST(DATEDIFF(f.departure, %(anchor)s), 0)), 1) AS score
    FROM flight f
    JOIN airplane ap ON ap.airplane_id = f.airplane_id
    JOIN airport ao ON ao.airport_id = f.`from`
    JOIN airport ad ON ad.airport_id = f.`to`
    LEFT JOIN airport_geo go ON go.airport_id = f.`from`
    LEFT JOIN airport_geo gd ON gd.airport_id = f.`to`
    LEFT JOIN booking b ON b.flight_id = f.flight_id
    WHERE f.airline_id = %(aid)s
      AND f.departure >= %(anchor)s
    GROUP BY f.flight_id, f.flightno, go.city, gd.city, ao.iata, ad.iata,
             ao.icao, ad.icao, ao.name, ad.name,
             f.departure, ap.capacity
    HAVING ociosidade_pct >= 20
    ORDER BY score DESC
    LIMIT %(lim)s
    """
    return db.query(sql, {"aid": airline_id, "anchor": anchor, "lim": limit})


def flight_targets(airline_id: int, flight_id: int, limit: int = 20) -> list[dict]:
    """RF-004 / RN-002: passageiros frequentes da companhia (por nº de voos na cia),
    priorizando quem já voou a mesma rota. Valida que o voo pertence ao tenant."""
    owns = db.query(
        "SELECT 1 FROM flight WHERE flight_id=%s AND airline_id=%s",
        (flight_id, airline_id),
    )
    if not owns:
        return []  # roteador transforma em 404

    sql = """
    WITH rota AS (SELECT `from` AS o, `to` AS d FROM flight WHERE flight_id=%(fid)s),
    freq AS (
      SELECT b.passenger_id,
             COUNT(*) AS voos_na_cia,
             SUM(CASE WHEN f.`from`=(SELECT o FROM rota) AND f.`to`=(SELECT d FROM rota)
                      THEN 1 ELSE 0 END) AS voos_na_rota
      FROM booking b
      JOIN flight f ON f.flight_id = b.flight_id
      WHERE f.airline_id = %(aid)s
      GROUP BY b.passenger_id
    )
    SELECT p.passenger_id, p.firstname, p.lastname,
           pd.emailaddress, pd.country,
           fr.voos_na_cia, fr.voos_na_rota,
           (fr.voos_na_cia + 3*fr.voos_na_rota) AS score
    FROM freq fr
    JOIN passenger p ON p.passenger_id = fr.passenger_id
    LEFT JOIN passengerdetails pd ON pd.passenger_id = fr.passenger_id
    ORDER BY score DESC, fr.voos_na_cia DESC
    LIMIT %(lim)s
    """
    rows = db.query(sql, {"fid": flight_id, "aid": airline_id, "lim": limit})
    for r in rows:  # mascara PII na saída
        e = r.get("emailaddress") or ""
        if "@" in e:
            a, b = e.split("@", 1)
            r["emailaddress"] = a[:2] + "***@" + b
    return rows


def create_campaign(airline_id: int, user_id: int, data: dict) -> int:
    """RF-006: grava campanha + alvos, vinculada ao tenant. Valida posse do voo."""
    owns = db.query(
        "SELECT 1 FROM flight WHERE flight_id=%s AND airline_id=%s",
        (data["flight_id"], airline_id),
    )
    if not owns:
        raise PermissionError("flight not in tenant")

    cid = db.execute(
        """INSERT INTO campaign(airline_id, flight_id, title, body, discount_pct, status, created_by)
           VALUES(%s,%s,%s,%s,%s,'draft',%s)""",
        (airline_id, data["flight_id"], data["title"], data["body"],
         data["discount_pct"], user_id),
    )
    for pid in data.get("target_passenger_ids", [])[:500]:
        db.execute(
            "INSERT INTO campaign_target(campaign_id, passenger_id, score) VALUES(%s,%s,%s)",
            (cid, int(pid), 0),
        )
    return cid


def list_campaigns(airline_id: int) -> list[dict]:
    """RF-007: campanhas do tenant."""
    return db.query(
        """SELECT c.id, c.flight_id, c.title, c.body, c.discount_pct, c.status, c.created_at,
                  (SELECT COUNT(*) FROM campaign_target t WHERE t.campaign_id=c.id) AS alvos
           FROM campaign c WHERE c.airline_id=%s ORDER BY c.created_at DESC""",
        (airline_id,),
    )


def vector_search(airline_id: int, text: str, limit: int = 5) -> list[dict]:
    """RF-008: busca semântica sobre flight_notes do tenant via VEC_COSINE_DISTANCE + EMBED_TEXT."""
    sql = """
    SELECT n.flight_id, n.note,
           VEC_COSINE_DISTANCE(
             n.embedding,
             EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', %(q)s)
           ) AS distancia
    FROM flight_notes n
    WHERE n.airline_id = %(aid)s
    ORDER BY distancia ASC
    LIMIT %(lim)s
    """
    return db.query(sql, {"q": text, "aid": airline_id, "lim": limit})
