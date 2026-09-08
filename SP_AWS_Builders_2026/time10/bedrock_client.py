"""Wrapper fino sobre o Bedrock (Claude via boto3) — sempre em ap-southeast-1."""
import json
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
TEXT_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
FAST_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"

_client = None


def _bedrock():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime", region_name=REGION)
    return _client


def _invoke(prompt: str, model_id: str = FAST_MODEL, max_tokens: int = 800, system: str = None) -> str:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    resp = _bedrock().invoke_model(modelId=model_id, body=json.dumps(body))
    return json.loads(resp["body"].read())["content"][0]["text"]


SQL_SYSTEM = """Você é um gerador de SQL para MySQL/TiDB. Dado o schema abaixo e uma pergunta em português,
responda APENAS com uma única query SELECT (nunca INSERT/UPDATE/DELETE/DROP/ALTER), sem explicação, sem
markdown, sem crases.

Se a pergunta envolver risco de atraso, disrupção ou clima, faça JOIN entre flight e weatherdata usando
weatherdata.station = flight.`from` (aeroporto de origem) e weatherdata.log_date = DATE(flight.departure) —
essa relação não tem FK declarada no schema, mas station corresponde ao airport_id. Traga a coluna
weatherdata.weather (enum: rain, fog, thunderstorm, snowfall, etc.) e wind/humidity quando relevante.

flight.`from` e flight.`to` são airport_id (não sigla) — faça JOIN com airport para trazer iata/name quando
a pergunta pedir nome de cidade ou aeroporto.

ATENÇÃO: a tabela `airport` NÃO tem colunas country nem city — NUNCA escreva airport.country ou airport.city,
isso quebra a query. País e cidade estão em `airport_geo`. Exemplo obrigatório de como filtrar por país:

SELECT f.flightno, ap.name
FROM flight f
JOIN airport ap ON ap.airport_id = f.`from`
JOIN airport_geo ag ON ag.airport_id = ap.airport_id
WHERE ag.country = 'Brazil'
LIMIT 20;

DOIS DADOS QUE NÃO EXISTEM NESTE BANCO — não tente responder com eles, diga que o dado não existe:
1) CLIMA: weatherdata tem apenas 4 estações, que não correspondem a nenhum aeroporto dos voos. Não use
   weatherdata para risco de nenhum voo específico.
2) ATRASO: medimos, e flight.departure é SEMPRE idêntico ao horário de flightschedule — o atraso máximo do
   banco inteiro é 0 minuto. Nenhum voo atrasa. Não gere query de atraso comparando flight com
   flightschedule: a coluna resultante seria uma coluna de zeros.

O que este banco sustenta de verdade é OCUPAÇÃO e RECEITA, via booking (617 mil reservas com preço) e
airplane.capacity. Ocupação = passageiros do voo / capacidade da aeronave.

REGRA CRÍTICA de ocupação: agrupe SEMPRE por f.flight_id, NUNCA por f.flightno. O mesmo flightno repete
todos os dias da semana; agrupar por flightno soma as reservas dos 7 dias contra a capacidade de uma única
aeronave e produz ocupação absurda (acima de 100%). Exemplo correto:

SELECT f.flight_id, f.flightno, ap.name AS origem, a.capacity,
       COUNT(b.booking_id) AS passageiros,
       ROUND(COUNT(b.booking_id) / a.capacity * 100, 1) AS ocupacao_pct,
       ROUND(SUM(b.price), 2) AS receita
FROM flight f
JOIN airport ap ON ap.airport_id = f.`from`
JOIN airplane a ON a.airplane_id = f.airplane_id
LEFT JOIN booking b ON b.flight_id = f.flight_id
GROUP BY f.flight_id, f.flightno, ap.name, a.capacity
ORDER BY ocupacao_pct DESC
LIMIT 20;

Sempre adicione LIMIT 20 a menos que a pergunta peça uma contagem/agregação (COUNT, SUM, AVG).

IMPORTANTE: quando a pergunta citar um nome de lugar (cidade, aeroporto), NÃO assuma que bate exatamente com
airport_geo.city — use LIKE '%termo%' (case-insensitive) tanto em airport.name quanto em airport_geo.city
quando não tiver certeza. Ex: "voos de Guarulhos" deve buscar (airport.name LIKE '%GUARULHOS%' OR
airport_geo.city LIKE '%SAO PAULO%' OR airport_geo.city LIKE '%GUARULHOS%').

IMPORTANTE: os dados desse banco cobrem APENAS a semana de 2015-06-02 a 2015-06-09. NUNCA use CURDATE(),
NOW() ou datas relativas ao dia de hoje — a data "hoje" não existe nesse banco. Se a pergunta disser "essa
semana", "últimos dias" etc., interprete como o intervalo fixo 2015-06-02 a 2015-06-09.

Schema real do banco (CREATE TABLE de cada tabela):
{schema}
"""


def generate_sql(question: str, schema: str) -> str:
    system = SQL_SYSTEM.format(schema=schema)
    sql = _invoke(question, model_id=TEXT_MODEL, max_tokens=500, system=system)
    sql = sql.strip().strip("`").strip()
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    return sql


EXPLAIN_SYSTEM = """Você é um copiloto de operações aeroportuárias explicando dados para uma analista chamada
Marina, que não escreve SQL. Responda em português, direto, em no máximo 4 frases.

Se o resultado trouxer ocupação ou receita, destaque isso como o ponto mais importante: diga quais voos ou
rotas se destacam e o que isso significa para a operação (voo cheio perto do limite da aeronave, rota com
receita concentrada, voo vazio que talvez não se pague). A ocupação típica deste banco fica entre 24% e
72%, com média de 49% — use isso como referência para dizer se um número é alto ou baixo.

Se algum valor de ocupação vier acima de 100%, NÃO trate como overbooking: é erro da query (agrupamento por
flightno em vez de flight_id, somando vários dias). Avise que o número está inconsistente.

Nunca invente números que não estão no resultado.
"""


def explain_results(question: str, sql: str, rows: list) -> str:
    prompt = (
        f"Pergunta original: {question}\n\n"
        f"SQL executado: {sql}\n\n"
        f"Resultado (JSON, pode estar truncado): {json.dumps(rows, default=str)[:6000]}"
    )
    return _invoke(prompt, model_id=TEXT_MODEL, max_tokens=400, system=EXPLAIN_SYSTEM)
