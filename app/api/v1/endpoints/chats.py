from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from uuid import UUID
from datetime import datetime
import httpx
import os
import asyncio

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

        chat_response = ChatResponse(**response_data)
        result.append(chat_response)

    # Сортируем по дате последнего сообщения (новые первыми)
    result.sort(key=lambda x: x.lastMessageAt or datetime.min, reverse=True)
    
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

    chat_response = ChatResponse(**response_data)

    # Создаем объект ответа для сортировки
    chat_response = ChatResponse(**response_data)
    
    return chat_response


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
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Отправить сообщение
    
    Отправляет новое сообщение в чат. 
    Если fromSpecialist=True, сообщение считается отправленным от специалиста (админ-панель).
    Если fromSpecialist=False или не указано, сообщение считается отправленным от пользователя (мобильное приложение).
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise NotFoundError("Chat", str(chat_id))
    
    if not request.text or not request.text.strip():
        raise BadRequestError("Message text cannot be empty")
    
    # Админ-панель отправляет от специалиста, мобильное приложение - от пользователя
    is_from_specialist = request.fromSpecialist if request.fromSpecialist is not None else False
    
    message = Message(
        chat_id=chat_id,
        text=request.text.strip(),
        sent_at=datetime.utcnow(),
        is_from_specialist=is_from_specialist,
        is_read=False
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Транслируем сообщение через WebSocket сервис (в фоне, не блокируем ответ)
    async def broadcast_message():
        try:
            websocket_url = os.getenv("WEBSOCKET_SERVICE_URL", "http://websocket:8080")
            broadcast_url = f"{websocket_url}/api/broadcast/message"
            
            # Форматируем дату в ISO формате для Java LocalDateTime
            sent_at_iso = message.sent_at.isoformat() if message.sent_at else datetime.utcnow().isoformat()
            # Убираем микросекунды, если они есть, и добавляем Z для UTC
            if '.' in sent_at_iso:
                sent_at_iso = sent_at_iso.split('.')[0] + 'Z'
            elif '+' in sent_at_iso or sent_at_iso.endswith('Z'):
                pass  # Уже в правильном формате
            else:
                sent_at_iso = sent_at_iso + 'Z'
            
            broadcast_data = {
                "messageId": str(message.id),
                "chatId": str(chat_id),
                "text": message.text,
                "fromSpecialist": message.is_from_specialist,
                "isRead": message.is_read,
                "sentAt": sent_at_iso
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.post(broadcast_url, json=broadcast_data)
                    if response.status_code != 200:
                        print(f"WebSocket broadcast failed: {response.status_code}")
                except Exception as e:
                    print(f"Failed to broadcast message to WebSocket: {e}")
        except Exception as e:
            print(f"Error broadcasting message: {e}")
    
    # Запускаем транслирование в фоне через BackgroundTasks
    if background_tasks:
        background_tasks.add_task(broadcast_message)
    else:
        # Fallback для случаев, когда BackgroundTasks не доступен
        asyncio.create_task(broadcast_message())
    
    return message


@router.post(
    "/{chat_id}/messages/read",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
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
    
    return None
