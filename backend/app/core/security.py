from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
import hashlib
import hmac
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

# Bcrypt context with fallback
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)
api_key_header = APIKeyHeader(name="X-IoT-API-Key", auto_error=False)


def get_password_hash(password: str) -> str:
    try:
        # Truncate to 72 bytes to avoid passlib-bcrypt 4.0 bug
        return pwd_context.hash(password[:72])
    except Exception:
        salt = settings.SECRET_KEY[:16].encode("utf-8")
        pwd_bytes = password.encode("utf-8")
        return hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, iterations=100000).hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("$2"):
            return pwd_context.verify(plain_password[:72], hashed_password)
    except Exception:
        pass
    salt = settings.SECRET_KEY[:16].encode("utf-8")
    pwd_bytes = plain_password.encode("utf-8")
    expected = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, iterations=100000).hex()
    return hmac.compare_digest(expected, hashed_password)


def create_access_token(
    data_or_subject: Union[dict, Any] = None,
    expires_delta: Optional[timedelta] = None,
    subject: Union[str, Any] = None,
    data: Optional[dict] = None
) -> str:
    target = subject if subject is not None else (data if data is not None else data_or_subject)
    if isinstance(target, dict):
        to_encode = target.copy()
    else:
        to_encode = {"sub": str(target), "type": "access"}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)



def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7))
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    from app.models.user import UserModel
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(token)
    sub: str = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(UserModel).filter((UserModel.id == sub) | (UserModel.username == sub)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user



def get_current_active_admin(current_user = Depends(get_current_user)):
    if getattr(current_user, "role", None) not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires administrator privilege",
        )
    return current_user


def verify_iot_api_key(api_key: Optional[str] = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-IoT-API-Key header")
    if api_key == getattr(settings, "IOT_DEFAULT_API_KEY", ""):
        return {"authenticated": True, "type": "master"}
    return {"authenticated": True, "api_key": api_key}
