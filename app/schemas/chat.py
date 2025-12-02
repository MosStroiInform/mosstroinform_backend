from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ChatResponse(BaseModel):
    """Схема чата для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    specialistName: str = Field(..., alias="specialist_name")
    specialistAvatarUrl: Optional[str] = Field(None, alias="specialist_avatar_url")
    lastMessage: Optional[str] = Field(None, alias="last_message")
    lastMessageAt: Optional[datetime] = Field(None, alias="last_message_at")
    unreadCount: int = Field(0, alias="unread_count")
    isActive: bool = Field(..., alias="is_active")

    class Config:
        from_attributes = True
        populate_by_name = True


# Для списка чатов используем List[ChatResponse] напрямую в эндпоинтах


class MessageResponse(BaseModel):
    """Схема сообщения для ответа"""
    id: UUID
    chatId: UUID = Field(..., alias="chat_id")
    text: str
    sentAt: datetime = Field(..., alias="sent_at")
    isFromSpecialist: bool = Field(..., alias="is_from_specialist")
    isRead: bool = Field(..., alias="is_read")

    class Config:
        from_attributes = True
        populate_by_name = True


# Для списка сообщений используем List[MessageResponse] напрямую в эндпоинтах


class MessageCreateRequest(BaseModel):
    """Схема запроса на создание сообщения"""
    text: str = Field(..., min_length=1)

