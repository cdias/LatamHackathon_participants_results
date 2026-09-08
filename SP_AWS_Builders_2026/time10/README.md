# Ask the Airport

Copiloto conversacional sobre o dataset `airportdb`: pergunte em português sobre rotas,
ocupação e receita e receba o SQL, os dados e a explicação em linguagem simples. Inclui busca
semântica de voos parecidos usando coluna `VECTOR` do TiDB.

## Rodar local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha com as credenciais do time
python db.py            # confere a conexão e imprime o schema real
python seed_vector_notes.py   # cria e semeia flight_notes (use --reset pra regerar as notas)
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Abra `http://localhost:8000`.

## Deploy na EC2

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Confira o IP público atual da instância (muda a cada restart) e acesse
`http://<ip-publico>:8000`.
