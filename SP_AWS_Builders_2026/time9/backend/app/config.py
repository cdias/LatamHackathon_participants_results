"""Configuração central — tudo vem de variáveis de ambiente (.env). Nada hardcoded."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # TiDB
    tidb_host: str = "localhost"
    tidb_port: int = 4000
    tidb_user: str = "root"
    tidb_password: str = ""
    tidb_database: str = "airportdb"
    tidb_ssl_ca: str = "/etc/ssl/cert.pem"

    # Auth / JWT (zero-trust) — SECRET obrigatório em produção
    jwt_secret: str = "change-me-in-env"
    jwt_alg: str = "HS256"
    jwt_expire_minutes: int = 60

    # Bedrock (Singapura)
    aws_region: str = "ap-southeast-1"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    aws_bearer_token_bedrock: str = ""

    # CORS — origem do frontend
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Data-âncora: o dataset é de jun/2015; usamos esta data como "agora" para a lógica.
    anchor_now: str = "2015-06-02 00:00:00"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
