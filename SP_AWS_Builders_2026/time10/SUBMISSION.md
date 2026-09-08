# SUBMISSION.md

## Time
Nome do time: The Last Member
Integrantes: Gustavo Luz

## Pitch
Ask the Airport: a analista de operações pergunta em português sobre voos, rotas, ocupação e
receita — e recebe o SQL, os dados e a explicação em linguagem simples, sem escrever uma linha
de query.

## O que faz
Marina, analista de operações, digita uma pergunta em português. O sistema lê o schema real do
`airportdb` no TiDB (via `SHOW CREATE TABLE`, não schema chutado), gera uma query `SELECT` com o
Claude no Bedrock, valida que ela é somente leitura, executa no TiDB e devolve três coisas: a
resposta em português, o SQL gerado e as linhas cruas — para a analista poder auditar de onde
veio o número.

Além do NL→SQL, a base tem uma camada semântica: 500 voos foram descritos em texto e indexados
numa coluna `VECTOR(1024)` gerada por `EMBED_TEXT` dentro do próprio TiDB — o embedding é
calculado pelo banco, sem passar por nenhum serviço externo. A busca por vizinho mais próximo
usa `VEC_COSINE_DISTANCE`, e é o que permite pedir "me ache voos parecidos com este".

## Dois usuários, uma interface
O mesmo copiloto serve dois públicos sem nenhuma mudança de código:
- **Uso interno**: a analista de operações (Marina) faz perguntas direto pra apoiar decisão —
  ocupação por rota, receita por companhia, achar padrões parecidos.
- **Autoatendimento do passageiro**: a mesma interface roda num **totem no aeroporto** (ou
  tablet no balcão de atendimento), permitindo o próprio passageiro perguntar em linguagem
  natural sobre voos e rotas, ou uma funcionária de atendimento usar a ferramenta pra responder
  mais rápido a quem está na fila — sem precisar saber SQL nem abrir um sistema interno
  complicado. É a mesma pergunta em português, só muda quem está do outro lado da tela.

## Stack — marque o que você realmente usou
- [x] TiDB Cloud Starter na AWS sa-east-1
      `gateway01.sa-east-1.prod.aws.tidbcloud.com:4000`, database `airportdb`, TLS via `certifi`.
- [x] Busca vetorial no TiDB (coluna VECTOR ou EMBED_TEXT)
      Tabela `flight_notes` com `VECTOR(1024)` gerada por
      `EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', note)` e consulta por
      `VEC_COSINE_DISTANCE`. 500 linhas indexadas.
- [x] Amazon Bedrock (ap-southeast-1)
      `bedrock-runtime` via boto3, modelo `anthropic.claude-3-5-sonnet-20240620-v1:0` para gerar
      o SQL e para explicar o resultado.
- [ ] Publicado na AWS -> URL no ar:
- [x] Construído com Kiro (.kiro/ commitado)
      `.kiro/steering/` (product.md, tech.md) e
      `.kiro/specs/ask-the-airport-copilot/` (requirements.md, design.md, tasks.md).

## Onde olhar
Conexão TiDB e grounding de schema: `db.py` — `get_connection()` (TLS) e
`get_schema_context()`, que puxa o `CREATE TABLE` real de cada tabela para ancorar o LLM nos
nomes de coluna verdadeiros.

Loop principal e guarda de segurança: `app.py` — endpoint `POST /api/ask`; a lista `FORBIDDEN` e
a checagem de `startswith("select")` rejeitam qualquer SQL que não seja leitura antes de tocar no
banco.

Busca vetorial: `seed_vector_notes.py` — o `CREATE TABLE` com a coluna `VECTOR(1024)` +
`EMBED_TEXT` e o INSERT que descreve cada voo em texto (rota, companhia, dia, ocupação,
receita). `vector_search.py` — `search_similar()`, a consulta com `VEC_COSINE_DISTANCE`
usada em produção, exposta no endpoint `POST /api/similar` e no bloco "Busca semântica" da
tela.

Chamadas ao Bedrock: `bedrock_client.py` — `_invoke()` (boto3 `invoke_model`), `generate_sql()`
com o system prompt de NL→SQL, e `explain_results()`, que traduz as linhas devolvidas em
resposta de negócio.

Front-end: `static/index.html` — uma página, sem build, servida pelo próprio FastAPI.

## Nota sobre o dataset
Vale registrar o que checamos no dado antes de escolher o recorte do produto: o `airportdb`
cobre apenas 2015-06-02 a 2015-06-08, o `flight.departure` é sempre idêntico ao horário de
`flightschedule` (nenhum voo do dump atrasa, o atraso máximo é 0 minuto) e o `weatherdata` tem
só 4 estações, que não correspondem aos aeroportos dos voos. Por isso o copiloto não promete
previsão de atraso: ele responde sobre o que o dado sustenta de fato — rotas, volume de
passageiros, ocupação por aeronave e receita por voo, em cima de 617 mil reservas com preço
real.

## Demo
Link do vídeo de 2 minutos ou da aplicação no ar: https://youtu.be/xO3NqwIe6-M
