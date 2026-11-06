from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserModel
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.schemas.common import APIResponse
from app.services.auth_service import auth_service


class SimpleLoginRequest(BaseModel):
    username: Optional[str] = None
    username_or_email: Optional[str] = None
    password: str


router = APIRouter()


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(user_in: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    user = auth_service.register_user(db, user_in)
    return APIResponse(
        message="User registered successfully",
        data=user
    )


@router.post("/login")
def login(request: SimpleLoginRequest, db: Session = Depends(get_db)):
    identifier = request.username_or_email or request.username
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username or email is required"
        )
    
    login_obj = LoginRequest(username_or_email=identifier, password=request.password)
    user = auth_service.authenticate_user(db, login_obj)
    token_resp = auth_service.create_user_tokens(user)
    
    return {
        "access_token": token_resp.access_token,
        "refresh_token": token_resp.refresh_token,
        "token_type": token_resp.token_type,
        "expires_in": token_resp.expires_in,
        "role": user.role
    }


@router.get("/me", response_model=APIResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Fetch authenticated user's profile.
    """
    return APIResponse(data=current_user)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh an expired access token using a valid refresh token.
    """
    new_tokens = auth_service.refresh_access_token(db, payload.refresh_token)
    return APIResponse(data=new_tokens)


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
