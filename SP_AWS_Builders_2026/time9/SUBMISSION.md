# SUBMISSION.md

## Time
Nome do time: latam-hackathon-009
Integrantes: 
- Liara Pereira (@liara_programadora) 
- Nicola Caprirolo (@nicolacaprirolo)
- Vinicius Araújo (@viniciusaraujo.ai) 
- Flávio Pimenta (@pimenta.dev)

## Pitch
AirRevenue — copiloto de revenue management que recomenda promoções para voos com assentos
ociosos e cria campanhas direcionadas aos passageiros frequentes de cada companhia.

## O que faz
Cada companhia entra na sua própria área (multi-tenant, zero-trust) e vê seus voos futuros
ranqueados por oportunidade (assentos ociosos × urgência). Ao escolher um voo, o sistema lista
os passageiros frequentes com maior propensão, gera o texto da promoção com IA (Amazon Bedrock)
e salva a campanha. Uma busca semântica (vetorial no TiDB) encontra voos/notas parecidos.

## Stack — marque o que você realmente usou
- [x] TiDB Cloud Starter na AWS — dados `airportdb` + tabelas de campanha (leitura e escrita)
- [x] Busca vetorial no TiDB (coluna VECTOR + EMBED_TEXT + VEC_COSINE_DISTANCE)
- [x] Amazon Bedrock (ap-southeast-1, Claude 3 Haiku) — geração do texto promocional (com fallback)
- [x] Publicado na AWS -> URL no ar: http://<EC2_PUBLIC_IP>:8000 (API) e :3000 (frontend)
- [x] Construído com Kiro (.kiro/ commitado)

> Observação de elegibilidade: a conta do hackathon é *bedrock-only* (nega Lambda/CloudFormation/
> S3-create/CloudFront/ec2:Describe — verificado via AWS CLI). O deploy executado é na **EC2 do
> time (sa-east-1)**, conforme recomendado no guia. O deploy serverless (SAM: API Gateway + Lambda
> + S3/CloudFront) está pronto e documentado em `infra/` como alternativa (Fase 2).

## Onde olhar
Conexão/consultas TiDB:       backend/app/db.py · backend/app/services.py
Busca vetorial:               backend/app/services.py (função `vector_search`) · setup_db.py (coluna VECTOR)
Chamadas ao Bedrock:          backend/app/bedrock.py
Segurança zero-trust (JWT):   backend/app/security.py · backend/app/main.py
Testes de API (ScanAPI):      tests/scanapi.yaml
Frontend (Vue):               frontend/src/App.vue · frontend/src/api.js
Specs / arquitetura:          docs/ · .kiro/specs/

## Demo
Pitch (2 min): docs/pitch.html
Screenshot do produto: docs/demo-recommendations.png
Link do vídeo ou da aplicação no ar: (preencher)

## Como rodar
```bash
# Backend
cd backend && cp .env.example .env   # preencher TIDB_* e (opcional) AWS_BEARER_TOKEN_BEDROCK
pip install -r requirements.txt
python ../setup_db.py                # cria tabelas + seed + embeddings (uma vez)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev   # http://localhost:3000

# Testes de API
cd tests && BASE_URL=http://localhost:8000 USERNAME=airline82 PASSWORD=airrevenue2026 \
  scanapi run scanapi.yaml
```
Usuários de demonstração: `airline82`, `airline66`, `airline73`, `airline80`, `airline99`, `airline81`
(senha `airrevenue2026`).

## O que faríamos a seguir
- Injeção de atraso simulado para ativar o copiloto de disrupção (o dataset não modela atrasos).
- Disparo real das campanhas (e-mail/push) e medição de conversão.
- Deploy serverless completo (SAM) em conta com permissões amplas.
