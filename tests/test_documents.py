import pytest
from uuid import uuid4
from datetime import datetime
from app.models.project import Project
from app.models.document import Document, DocumentStatus


def test_get_documents_empty(client):
    """Тест получения пустого списка документов"""
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_get_document_by_id(client, db_session):
    """Тест получения документа по ID"""
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
    
    document_id = uuid4()
    document = Document(
        id=document_id,
        project_id=project_id,
        title="Тестовый документ",
        description="Описание документа",
        status=DocumentStatus.PENDING
    )
    db_session.add(document)
    db_session.commit()
    
    response = client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(document_id)
    assert data["title"] == "Тестовый документ"


def test_approve_document(client, db_session):
    """Тест одобрения документа"""
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
    
    document_id = uuid4()
    document = Document(
        id=document_id,
        project_id=project_id,
        title="Тестовый документ",
        status=DocumentStatus.PENDING
    )
    db_session.add(document)
    db_session.commit()
    
    response = client.post(f"/api/v1/documents/{document_id}/approve")
    assert response.status_code == 200
    
    # Проверяем, что статус изменился
    db_session.refresh(document)
    assert document.status == DocumentStatus.APPROVED
    assert document.approved_at is not None


def test_reject_document(client, db_session):
    """Тест отклонения документа"""
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
    
    document_id = uuid4()
    document = Document(
        id=document_id,
        project_id=project_id,
        title="Тестовый документ",
        status=DocumentStatus.PENDING
    )
    db_session.add(document)
    db_session.commit()
    
    response = client.post(
        f"/api/v1/documents/{document_id}/reject",
        json={"reason": "Несоответствие требованиям"}
    )
    assert response.status_code == 200
    
    # Проверяем, что статус изменился
    db_session.refresh(document)
    assert document.status == DocumentStatus.REJECTED
    assert document.rejection_reason == "Несоответствие требованиям"

