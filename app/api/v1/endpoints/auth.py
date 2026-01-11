import secrets
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, status, Depends, HTTPException, Response, Cookie, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import BadRequestError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter()


def get_current_user(
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего пользователя из JWT токена.
    Поддерживает два способа передачи токена:
    1. Cookie (access_token) - для веб-приложений
    2. Authorization header (Bearer token) - для мобильных и админ-панели
    """
    # Сначала пробуем получить токен из cookie
    access_token = access_token_cookie
    
    # Если нет в cookie, пробуем из заголовка Authorization
    if not access_token and authorization:
        # Поддерживаем формат "Bearer <token>"
        if authorization.startswith("Bearer "):
            access_token = authorization[7:]  # Убираем "Bearer "
        elif authorization.startswith("bearer "):
            access_token = authorization[7:]  # Поддержка lowercase
        else:
            # Если нет префикса Bearer, считаем что весь заголовок - это токен
            access_token = authorization
    
    # Если токена нет ни в cookie, ни в заголовке - возвращаем демо пользователя
    # Это обеспечивает обратную совместимость со старым демо-режимом
    if not access_token:
        return User(
            id=uuid4(),
            email="demo@mosstroinform.ru",
            password_hash="",
            name="Demo User",
            phone=None,
        )

    # Проверяем JWT токен
    payload = verify_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получаем пользователя из БД
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def _issue_jwt_tokens(user_id: str) -> tuple[str, str]:
    """Генерирует пару JWT access/refresh токенов."""
    access_token_data = {"sub": str(user_id), "type": "access"}
    refresh_token_data = {"sub": str(user_id), "type": "refresh"}

    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(refresh_token_data)

    return access_token, refresh_token


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Вход пользователя: проверяет email/пароль и возвращает JWT токены + профиль пользователя.
    """
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise BadRequestError("Invalid email or password")

    # Проверяем пароль
    if not verify_password(request.password, user.password_hash):
        raise BadRequestError("Invalid email or password")

    # Генерируем JWT токены
    access_token, refresh_token = _issue_jwt_tokens(str(user.id))

    # Устанавливаем токены в cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=1800,  # 30 минут
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=604800,  # 7 дней
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
        ),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    Создает пользователя в БД и возвращает JWT токены.
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise BadRequestError("User with this email already exists")

    # Хэшируем пароль
    hashed_password = hash_password(request.password)

    # Создаем пользователя
    user = User(
        email=request.email,
        password_hash=hashed_password,
        name=request.name,
        phone=request.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Генерируем JWT токены
    access_token, refresh_token = _issue_jwt_tokens(str(user.id))

    # Устанавливаем токены в cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=1800,  # 30 минут
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=604800,  # 7 дней
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
        ),
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(current_user: User = Depends(get_current_user)):
    """Возвращает текущего пользователя из JWT токена."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
    )


@router.post("/refresh", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: RefreshRequest,
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
    db: Session = Depends(get_db)
):
    """Обновить пару токенов по refresh-токену."""
    token_to_verify = refresh_token or request.refresh_token

    if not token_to_verify:
        raise BadRequestError("Refresh token is required")

    payload = verify_token(token_to_verify)
    if not payload or payload.get("type") != "refresh":
        raise BadRequestError("Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise BadRequestError("Invalid refresh token")

    # Проверяем, существует ли пользователь
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BadRequestError("User not found")

    # Генерируем новые JWT токены
    access_token, new_refresh_token = _issue_jwt_tokens(str(user.id))

    # Обновляем токены в cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=1800,  # 30 минут
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # В продакшене True для HTTPS
        samesite="lax",
        max_age=604800,  # 7 дней
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
        ),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """Выход из системы - очищает cookie с токенами."""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}

