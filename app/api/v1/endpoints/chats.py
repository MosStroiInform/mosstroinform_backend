from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.chat import Chat, Message
from app.schemas.chat import ChatResponse, MessageResponse, MessageCreateRequest
from app.schemas.base import EmptyResponse

router = APIRouter()


@router.get("", response_model=List[ChatResponse])
async def get_chats(db: Session = Depends(get_db)):
    """
    Получить список всех чатов
    
    Возвращает список всех чатов пользователя с информацией о последнем сообщении
    и количестве непрочитанных сообщений.
    """
    chats = db.query(Chat).filter(Chat.is_active == True).all()
    
    result = []
    for chat in chats:
        # Получаем последнее сообщение
        last_message = db.query(Message).filter(
            Message.chat_id == chat.id
        ).order_by(desc(Message.sent_at)).first()
        
        # Подсчитываем непрочитанные сообщения (от специалиста)
        unread_count = db.query(func.count(Message.id)).filter(
            Message.chat_id == chat.id,
            Message.is_from_specialist == True,
            Message.is_read == False
        ).scalar() or 0
        
        response_data = {
            "id": chat.id,
            "project_id": chat.project_id,
            "specialist_name": chat.specialist_name,
            "specialist_avatar_url": chat.specialist_avatar_url,
            "last_message": last_message.text if last_message else None,
            "last_message_at": last_message.sent_at if last_message else None,
            "unread_count": unread_count,
            "is_active": chat.is_active,
        }
        
        result.append(ChatResponse(**response_data))
    
    # Сортируем по дате последнего сообщения (новые первыми)
    result.sort(key=lambda x: x.last_message_at or datetime.min, reverse=True)
    
    return result


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: UUID, db: Session = Depends(get_db)):
    """
    Получить информацию о чате
    
    Возвращает детальную информацию о чате по его идентификатору.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise NotFoundError("Chat", str(chat_id))
    
    # Получаем последнее сообщение
    last_message = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(desc(Message.sent_at)).first()
    
    # Подсчитываем непрочитанные сообщения
    unread_count = db.query(func.count(Message.id)).filter(
        Message.chat_id == chat_id,
        Message.is_from_specialist == True,
        Message.is_read == False
    ).scalar() or 0
    
    response_data = {
        "id": chat.id,
        "project_id": chat.project_id,
        "specialist_name": chat.specialist_name,
        "specialist_avatar_url": chat.specialist_avatar_url,
        "last_message": last_message.text if last_message else None,
        "last_message_at": last_message.sent_at if last_message else None,
        "unread_count": unread_count,
        "is_active": chat.is_active,
    }
    
    return ChatResponse(**response_data)


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: UUID, db: Session = Depends(get_db)):
    """
    Получить сообщения чата
    
    Возвращает список всех сообщений в чате, отсортированных по времени отправки.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise NotFoundError("Chat", str(chat_id))
    
    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.sent_at).all()
    
    return messages


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: UUID,
    request: MessageCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Отправить сообщение
    
    Отправляет новое сообщение в чат. Сообщение считается отправленным от пользователя (не от специалиста).
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise NotFoundError("Chat", str(chat_id))
    
    if not request.text or not request.text.strip():
        raise BadRequestError("Message text cannot be empty")
    
    message = Message(
        chat_id=chat_id,
        text=request.text.strip(),
        sent_at=datetime.utcnow(),
        is_from_specialist=False,
        is_read=False
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.post("/{chat_id}/messages/read", response_model=EmptyResponse, status_code=status.HTTP_200_OK)
async def mark_messages_as_read(chat_id: UUID, db: Session = Depends(get_db)):
    """
    Отметить сообщения как прочитанные
    
    Отмечает все непрочитанные сообщения от специалиста в чате как прочитанные.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise NotFoundError("Chat", str(chat_id))
    
    # Отмечаем все непрочитанные сообщения от специалиста как прочитанные
    db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.is_from_specialist == True,
        Message.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return EmptyResponse()
