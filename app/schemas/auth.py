from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """Схема пользователя для ответов auth"""
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    phone: Optional[str] = None


class AuthResponse(BaseModel):
    """Ответ на успешную аутентификацию/регистрацию"""
    access_token: str
    refresh_token: str
    user: UserResponse


class LoginRequest(BaseModel):
    """Запрос на вход"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None


class RefreshRequest(BaseModel):
    """Запрос на обновление токенов"""
    refresh_token: str

