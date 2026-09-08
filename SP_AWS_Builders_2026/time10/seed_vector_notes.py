"""Cria a tabela vetorial (EMBED_TEXT, embedding calculado dentro do TiDB) e semeia uma
descricao em texto de cada voo: rota, companhia, dia, ocupacao e receita.

Por que esses campos e nao clima: o weatherdata do dump tem so 4 estacoes, que nao batem com
os aeroportos dos voos, e o flight.departure e sempre igual ao horario do flightschedule (nenhum
voo atrasa). Descricao baseada em clima/atraso sai identica para todos os voos e a busca
semantica devolve vizinho aleatorio. Ocupacao e receita variam de verdade, entao o embedding
tambem varia.

Roda: python seed_vector_notes.py          (semeia se estiver vazia)
      python seed_vector_notes.py --reset  (dropa e semeia de novo)
"""
import os
import sys
import certifi
import pymysql
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.environ["TIDB_HOST"],
    port=int(os.environ.get("TIDB_PORT", 4000)),
    user=os.environ["TIDB_USER"],
    password=os.environ["TIDB_PASSWORD"],
    database=os.environ.get("TIDB_DATABASE", "airportdb"),
    ssl={"ca": certifi.where()},
)

EMBED_MODEL = "tidbcloud_free/amazon/titan-embed-text-v2"

DDL = f"""
CREATE TABLE IF NOT EXISTS flight_notes (
    id BIGINT AUTO_RANDOM PRIMARY KEY,
    flight_id INT,
    note TEXT,
    embedding VECTOR(1024) GENERATED ALWAYS AS (
        EMBED_TEXT('{EMBED_MODEL}', note)
    ) STORED
);
"""

# Uma frase por voo, densa em sinal: rota (sigla + cidade + pais), companhia, dia da semana,
# ocupacao com rotulo textual e receita. O rotulo ('ocupacao alta') e o que faz a busca semantica
# responder bem a perguntas como "voos com ocupacao critica".
SEED_NOTES_SQL = """
INSERT INTO flight_notes (flight_id, note)
SELECT s.flight_id,
       CONCAT(
           'Voo ', s.flightno, ' da ', s.airlinename,
           ' de ', s.orig_code, ' (', s.orig_city, ', ', s.orig_country, ')',
           ' para ', s.dest_code, ' (', s.dest_city, ', ', s.dest_country, ')',
           ', ', s.dia_semana, ' ', DATE_FORMAT(s.departure, '%Y-%m-%d %H:%i'),
           ', aeronave de ', s.capacity, ' assentos com ', s.pax, ' passageiros',
           ', ocupacao ', s.ocup, '% (',
           -- Faixas medidas no dump, nao chutadas: ocupacao vai de 24% a 72%, media 49%.
           -- Cortes fixos tipo 60/35 jogariam 98% dos voos em 'media' e o rotulo nao
           -- separaria nada na busca semantica.
           CASE WHEN s.ocup >= 53 THEN 'ocupacao alta, voo cheio'
                WHEN s.ocup >= 46 THEN 'ocupacao media'
                ELSE 'ocupacao baixa, voo vazio' END,
           '), receita ', s.receita
       ) AS note
FROM (
    SELECT f.flight_id, f.flightno, f.departure, ap.capacity,
           al.airlinename,
           COALESCE(ao.iata, ao.icao) AS orig_code,
           COALESCE(ago.city, '?')    AS orig_city,
           COALESCE(ago.country, '?') AS orig_country,
           COALESCE(ad.iata, ad.icao) AS dest_code,
           COALESCE(agd.city, '?')    AS dest_city,
           COALESCE(agd.country, '?') AS dest_country,
           ELT(DAYOFWEEK(f.departure), 'domingo', 'segunda-feira', 'terca-feira',
               'quarta-feira', 'quinta-feira', 'sexta-feira', 'sabado') AS dia_semana,
           COUNT(b.booking_id) AS pax,
           ROUND(COUNT(b.booking_id) / ap.capacity * 100, 1) AS ocup,
           ROUND(COALESCE(SUM(b.price), 0), 2) AS receita
    FROM flight f
    JOIN airport ao      ON ao.airport_id = f.`from`
    JOIN airport ad      ON ad.airport_id = f.`to`
    JOIN airline al      ON al.airline_id = f.airline_id
    JOIN airplane ap     ON ap.airplane_id = f.airplane_id
    LEFT JOIN airport_geo ago ON ago.airport_id = ao.airport_id
    LEFT JOIN airport_geo agd ON agd.airport_id = ad.airport_id
    LEFT JOIN booking b  ON b.flight_id = f.flight_id
    GROUP BY f.flight_id, f.flightno, f.departure, ap.capacity, al.airlinename,
             ao.iata, ao.icao, ad.iata, ad.icao,
             ago.city, ago.country, agd.city, agd.country
    -- RAND com semente fixa: amostra espalhada pelos 7 dias e por varias rotas, mas
    -- reproduzivel. Ordenar por flight_id traria so os voos do primeiro dia.
    ORDER BY RAND(42)
    LIMIT 500
) s;
"""

# Usada tambem pelo app (vector_search.py) — mantida aqui como consulta de exemplo do criterio.
EXAMPLE_QUERY = f"""
SELECT flight_id, note,
       VEC_COSINE_DISTANCE(embedding, EMBED_TEXT('{EMBED_MODEL}', %s)) AS distancia
FROM flight_notes
ORDER BY distancia
LIMIT 5;
"""

if __name__ == "__main__":
    reset = "--reset" in sys.argv
    with conn.cursor() as cur:
        if reset:
            cur.execute("DROP TABLE IF EXISTS flight_notes")
            conn.commit()
            print("flight_notes dropada (--reset).")

        cur.execute(DDL)
        conn.commit()
        print("Tabela flight_notes criada (ou ja existia).")

        cur.execute("SELECT COUNT(*) FROM flight_notes")
        (existing,) = cur.fetchone()
        if existing > 0:
            print(f"flight_notes ja tem {existing} linhas, pulando o INSERT.")
        else:
            cur.execute(SEED_NOTES_SQL)
            conn.commit()
            print(f"{cur.rowcount} notas inseridas em flight_notes.")

        pergunta = "voo cheio, com ocupacao alta e receita grande"
        print(f"\nTestando busca vetorial: '{pergunta}'")
        cur.execute(EXAMPLE_QUERY, (pergunta,))
        for row in cur.fetchall():
            print(row)
