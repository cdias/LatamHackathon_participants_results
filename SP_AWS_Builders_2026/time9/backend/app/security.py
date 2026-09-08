"""Segurança zero-trust: senhas com bcrypt, JWT HS256 curto, tenant extraído SEMPRE do token."""
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
from jose import JWTError, jwt
from .config import get_settings

_bearer = HTTPBearer(auto_error=True)


def hash_password(plain: str) -> str:
    # bcrypt limita a 72 bytes; truncamos explicitamente para evitar erro.
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_token(*, user_id: int, airline_id: int, username: str) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "airline_id": airline_id,
        "username": username,
        "iat": now,
        "exp": now + timedelta(minutes=s.jwt_expire_minutes),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_alg)


class Tenant:
    """Contexto autenticado. airline_id vem do token assinado, nunca do cliente."""
    def __init__(self, user_id: int, airline_id: int, username: str):
        self.user_id = user_id
        self.airline_id = airline_id
        self.username = username


def current_tenant(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Tenant:
    s = get_settings()
    err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(creds.credentials, s.jwt_secret, algorithms=[s.jwt_alg])
        airline_id = payload.get("airline_id")
        user_id = payload.get("sub")
        if airline_id is None or user_id is None:
            raise err
        return Tenant(int(user_id), int(airline_id), payload.get("username", ""))
    except (JWTError, ValueError):
        raise err
