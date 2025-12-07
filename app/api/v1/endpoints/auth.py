import secrets
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, status

from app.core.exceptions import BadRequestError
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter()

# Простая in-memory "база" пользователей и токенов для демо-окружения
_current_user: Optional[UserResponse] = UserResponse(
    id=uuid4(),
    email="demo@mosstroinform.ru",
    name="Demo User",
    phone=None,
)
_current_refresh_token: Optional[str] = None


def _issue_tokens() -> tuple[str, str]:
    """Генерирует пару access/refresh токенов и сохраняет refresh в памяти."""
    global _current_refresh_token
    access = secrets.token_urlsafe(32)
    refresh = secrets.token_urlsafe(48)
    _current_refresh_token = refresh
    return access, refresh


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    Упрощенный вход: принимает email/пароль и возвращает токены + профиль пользователя.
    В текущей версии пароль не проверяется (демо-режим).
    """
    access, refresh = _issue_tokens()
    # Обновляем email пользователя под ввод, если отличается
    global _current_user
    _current_user = UserResponse(
        id=_current_user.id,
        email=request.email,
        name=_current_user.name,
        phone=_current_user.phone,
    )
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        user=_current_user,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def register(request: RegisterRequest):
    """
    Регистрация нового пользователя (демо).
    Создает пользователя в памяти и возвращает токены.
    """
    global _current_user
    _current_user = UserResponse(
        id=uuid4(),
        email=request.email,
        name=request.name,
        phone=request.phone,
    )
    access, refresh = _issue_tokens()
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        user=_current_user,
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me():
    """Возвращает текущего пользователя (демо-версия, без проверки токена)."""
    return _current_user


@router.post("/refresh", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def refresh(request: RefreshRequest):
    """Обновить пару токенов по refresh-токену."""
    if _current_refresh_token and request.refresh_token != _current_refresh_token:
        raise BadRequestError("Invalid refresh token")
    access, refresh_token = _issue_tokens()
    return AuthResponse(
        access_token=access,
        refresh_token=refresh_token,
        user=_current_user,
    )

