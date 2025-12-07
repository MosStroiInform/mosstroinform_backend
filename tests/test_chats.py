import pytest
from uuid import uuid4
from datetime import datetime
from app.models.project import Project
from app.models.chat import Chat, Message


def test_get_chats_empty(client):
    """Тест получения пустого списка чатов"""
    response = client.get("/api/v1/chats")
    assert response.status_code == 200
    assert response.json() == []


def test_get_chats(client, db_session):
    """Тест получения списка чатов"""
    # Создаем проект и чат
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    
    chat_id = uuid4()
    chat = Chat(
        id=chat_id,
        project_id=project_id,
        specialist_name="Иван Петров",
        specialist_avatar_url="https://example.com/avatar.jpg",
        is_active=True
    )
    db_session.add(chat)
    db_session.commit()
    
    response = client.get("/api/v1/chats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["specialistName"] == "Иван Петров"


def test_get_chat_by_id(client, db_session):
    """Тест получения чата по ID"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    
    chat_id = uuid4()
    chat = Chat(
        id=chat_id,
        project_id=project_id,
        specialist_name="Мария Сидорова",
        is_active=True
    )
    db_session.add(chat)
    db_session.commit()
    
    response = client.get(f"/api/v1/chats/{chat_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(chat_id)
    assert data["specialistName"] == "Мария Сидорова"


def test_get_chat_not_found(client):
    """Тест получения несуществующего чата"""
    fake_id = uuid4()
    response = client.get(f"/api/v1/chats/{fake_id}")
    assert response.status_code == 404


def test_get_messages(client, db_session):
    """Тест получения сообщений чата"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    
    chat_id = uuid4()
    chat = Chat(
        id=chat_id,
        project_id=project_id,
        specialist_name="Тест",
        is_active=True
    )
    db_session.add(chat)
    
    message = Message(
        id=uuid4(),
        chat_id=chat_id,
        text="Тестовое сообщение",
        sent_at=datetime.utcnow(),
        is_from_specialist=False,
        is_read=False
    )
    db_session.add(message)
    db_session.commit()
    
    response = client.get(f"/api/v1/chats/{chat_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Тестовое сообщение"


def test_create_message(client, db_session):
    """Тест отправки сообщения"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    
    chat_id = uuid4()
    chat = Chat(
        id=chat_id,
        project_id=project_id,
        specialist_name="Тест",
        is_active=True
    )
    db_session.add(chat)
    db_session.commit()
    
    response = client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"text": "Новое сообщение"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Новое сообщение"
    assert data["isFromSpecialist"] == False


def test_mark_messages_as_read(client, db_session):
    """Тест отметки сообщений как прочитанных"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    
    chat_id = uuid4()
    chat = Chat(
        id=chat_id,
        project_id=project_id,
        specialist_name="Тест",
        is_active=True
    )
    db_session.add(chat)
    
    message = Message(
        id=uuid4(),
        chat_id=chat_id,
        text="Сообщение от специалиста",
        sent_at=datetime.utcnow(),
        is_from_specialist=True,
        is_read=False
    )
    db_session.add(message)
    db_session.commit()
    
    response = client.post(f"/api/v1/chats/{chat_id}/messages/read")
    assert response.status_code == 204
    
    # Проверяем, что сообщение отмечено как прочитанное
    db_session.refresh(message)
    assert message.is_read == True

