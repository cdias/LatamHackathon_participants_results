# Deploy na EC2 (sa-east-1) — AirRevenue

A conta do hackathon é *bedrock-only*; o deploy é na **EC2 do time**. Acesso via **Session
Manager** (sem SSH). Portas abertas: **8000-8999** e **3000**. Bind em **0.0.0.0**.

## Passos (dentro da EC2, via Session Manager)

```bash
# 1. Ferramentas (Amazon Linux)
sudo dnf install -y git python3.11 python3.11-pip nodejs

# 2. Código
git clone https://github.com/flap/airrevenue.git && cd airrevenue

# 3. Backend
cd backend
cp .env.example .env      # preencher TIDB_* e (opcional) AWS_BEARER_TOKEN_BEDROCK
python3.11 -m pip install -r requirements.txt
python3.11 ../setup_db.py            # uma vez: tabelas + seed + embeddings
nohup python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# 4. Frontend (servido estático)
cd ../frontend
npm install && VITE_API_BASE="http://<EC2_PUBLIC_IP>:8000" npm run build
nohup npx vite preview --host 0.0.0.0 --port 3000 > web.log 2>&1 &
```

Acessos:
- API:      `http://<EC2_PUBLIC_IP>:8000/api/health`
- Frontend: `http://<EC2_PUBLIC_IP>:3000`

> ⚠️ O IP público muda a cada stop/start (sem Elastic IP). Reconferir no console após restart.
> ⚠️ Tudo aqui é público (sem TLS/auth na porta). Segredos só no `.env` da instância.
