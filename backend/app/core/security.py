import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


class TokenPayload(BaseModel):
    sub: uuid.UUID
    exp: int


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(subject: uuid.UUID, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode JWT token and return a typed TokenPayload. Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub_str: str | None = payload.get("sub")
        exp: int | None = payload.get("exp")
        if sub_str is None or exp is None:
            return None
        return TokenPayload(sub=uuid.UUID(sub_str), exp=exp)
    except (JWTError, ValueError):
        return None
