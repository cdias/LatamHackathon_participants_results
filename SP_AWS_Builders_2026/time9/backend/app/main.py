"""AirRevenue API — FastAPI. Zero-trust: rotas de dado exigem JWT; tenant vem do token."""
import logging
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import services
from .bedrock import generate_promo_copy
from .config import get_settings
from .db import query
from .schemas import (CampaignIn, GenerateCopyIn, GenerateCopyOut, LoginIn,
                      SearchIn, TokenOut)
from .security import (Tenant, create_token, current_tenant, verify_password)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()

app = FastAPI(title="AirRevenue API", version="1.0.0",
              description="Recomendação de promoções para voos ociosos — multi-tenant, zero-trust.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=TokenOut)
def login(body: LoginIn):
    rows = query(
        "SELECT id, airline_id, username, password_hash FROM airline_user WHERE username=%s",
        (body.username,),
    )
    if not rows or not verify_password(body.password, rows[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    u = rows[0]
    token = create_token(user_id=u["id"], airline_id=u["airline_id"], username=u["username"])
    return TokenOut(access_token=token, airline_id=u["airline_id"],
                    airline_name=services.airline_name(u["airline_id"]))


@app.get("/api/me")
def me(t: Tenant = Depends(current_tenant)):
    return {"user_id": t.user_id, "airline_id": t.airline_id, "username": t.username,
            "airline_name": services.airline_name(t.airline_id)}


@app.get("/api/recommendations")
def recommendations(limit: int = 20, t: Tenant = Depends(current_tenant)):
    return {"airline_id": t.airline_id,
            "flights": services.recommend_flights(t.airline_id, min(limit, 100))}


@app.get("/api/flights/{flight_id}/targets")
def targets(flight_id: int, limit: int = 20, t: Tenant = Depends(current_tenant)):
    rows = services.flight_targets(t.airline_id, flight_id, min(limit, 100))
    if not rows:
        # 404 tanto para voo inexistente quanto para voo de outro tenant (não vaza existência)
        raise HTTPException(status_code=404, detail="Voo não encontrado")
    return {"flight_id": flight_id, "targets": rows}


@app.post("/api/campaigns/generate-copy", response_model=GenerateCopyOut)
def generate_copy(body: GenerateCopyIn, t: Tenant = Depends(current_tenant)):
    price_old = services.flight_avg_price(t.airline_id, body.flight_id)
    price_new = round(price_old * (1 - body.discount_pct / 100), 2)
    text, source = generate_promo_copy(
        route=body.route, discount_pct=body.discount_pct,
        airline=services.airline_name(t.airline_id),
        price_old=price_old, context=body.context,
    )
    return GenerateCopyOut(body=text, source=source, price_old=price_old, price_new=price_new)


@app.post("/api/campaigns")
def create_campaign(body: CampaignIn, t: Tenant = Depends(current_tenant)):
    try:
        cid = services.create_campaign(t.airline_id, t.user_id, body.model_dump())
    except PermissionError:
        raise HTTPException(status_code=404, detail="Voo não encontrado")
    return {"id": cid, "status": "draft"}


@app.get("/api/campaigns")
def campaigns(t: Tenant = Depends(current_tenant)):
    return {"campaigns": services.list_campaigns(t.airline_id)}


@app.post("/api/search")
def search(body: SearchIn, t: Tenant = Depends(current_tenant)):
    return {"results": services.vector_search(t.airline_id, body.q, body.limit)}


# Entrypoint Lambda (documentado): from mangum import Mangum; handler = Mangum(app)
