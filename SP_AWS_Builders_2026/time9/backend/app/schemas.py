"""Schemas de entrada/saída (validação de contrato)."""
from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    airline_id: int
    airline_name: str


class GenerateCopyIn(BaseModel):
    flight_id: int
    route: str = Field(max_length=120)
    discount_pct: int = Field(ge=1, le=90)
    context: str = Field(default="", max_length=500)


class GenerateCopyOut(BaseModel):
    body: str
    source: str  # bedrock | fallback
    price_old: float
    price_new: float


class CampaignIn(BaseModel):
    flight_id: int
    title: str = Field(min_length=1, max_length=140)
    body: str = Field(min_length=1, max_length=2000)
    discount_pct: int = Field(ge=1, le=90)
    target_passenger_ids: list[int] = Field(default_factory=list)


class SearchIn(BaseModel):
    q: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=5, ge=1, le=20)
