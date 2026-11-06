from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.core.errors import ConflictError


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> User:
        user = (
            db.query(User)
            .filter((User.username == login_data.username_or_email) | (User.email == login_data.username_or_email))
            .first()
        )
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        return user

    @staticmethod
    def register_user(db: Session, reg_data: RegisterRequest) -> User:
        # Check existing username
        if db.query(User).filter(User.username == reg_data.username).first():
            raise ConflictError(f"Username '{reg_data.username}' is already taken")

        # Check existing email
        if db.query(User).filter(User.email == reg_data.email).first():
            raise ConflictError(f"Email '{reg_data.email}' is already registered")

        hashed_pwd = get_password_hash(reg_data.password)
        new_user = User(
            username=reg_data.username,
            email=reg_data.email,
            hashed_password=hashed_pwd,
            full_name=reg_data.full_name,
            role=reg_data.role or "operator",
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def create_user_tokens(user: User) -> TokenResponse:
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, refresh token expected"
            )
        user_id = payload.get("sub")
        user = db.query(User).filter((User.id == str(user_id)) | (User.username == str(user_id))).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or does not exist"
            )
        return AuthService.create_user_tokens(user)


auth_service = AuthService()

