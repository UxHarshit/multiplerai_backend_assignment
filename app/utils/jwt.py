from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_BCRYPT_MAX_PASSWORD_BYTES = 72


def _validate_bcrypt_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > _BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("Password is too long. Maximum allowed is 72 bytes.")

def hash_password(password: str) -> str:
    _validate_bcrypt_password_length(password)
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # Avoid backend errors for overlong input and treat it as invalid credentials.
    if len(plain.encode("utf-8")) > _BCRYPT_MAX_PASSWORD_BYTES:
        return False
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None