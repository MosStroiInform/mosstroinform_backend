import pytest
from uuid import uuid4
from datetime import datetime
from app.models.project import Project
from app.models.construction_site import ConstructionSite
from app.models.completion import FinalDocument, FinalDocumentStatus


def test_get_completion_status(client, db_session):
    """Тест получения статуса завершения строительства"""
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
    
    site = ConstructionSite(
        id=uuid4(),
        project_id=project_id,
        progress=0.85
    )
    db_session.add(site)
    db_session.commit()
    
    response = client.get(f"/api/v1/projects/{project_id}/completion-status")
    assert response.status_code == 200
    data = response.json()
    assert data["projectId"] == str(project_id)
    assert data["progress"] == 0.85
    assert data["isCompleted"] == False


def test_get_final_documents(client, db_session):
    """Тест получения списка финальных документов"""
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
    
    doc = FinalDocument(
        id=uuid4(),
        project_id=project_id,
        title="Акт приёмки",
        description="Тестовый документ",
        status=FinalDocumentStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(f"/api/v1/projects/{project_id}/final-documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Акт приёмки"


def test_get_final_document_by_id(client, db_session):
    """Тест получения финального документа по ID"""
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
    
    doc_id = uuid4()
    doc = FinalDocument(
        id=doc_id,
        project_id=project_id,
        title="Гарантийное обязательство",
        status=FinalDocumentStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(f"/api/v1/projects/{project_id}/final-documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc_id)
    assert data["title"] == "Гарантийное обязательство"


def test_sign_final_document(client, db_session):
    """Тест подписания финального документа"""
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
    
    doc_id = uuid4()
    doc = FinalDocument(
        id=doc_id,
        project_id=project_id,
        title="Акт приёмки",
        status=FinalDocumentStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.post(f"/api/v1/projects/{project_id}/final-documents/{doc_id}/sign")
    assert response.status_code == 200
    
    # Проверяем, что статус изменился
    db_session.refresh(doc)
    assert doc.status == FinalDocumentStatus.SIGNED
    assert doc.signed_at is not None


def test_reject_final_document(client, db_session):
    """Тест отклонения финального документа"""
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
    
    doc_id = uuid4()
    doc = FinalDocument(
        id=doc_id,
        project_id=project_id,
        title="Акт приёмки",
        status=FinalDocumentStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.post(
        f"/api/v1/projects/{project_id}/final-documents/{doc_id}/reject",
        json={"reason": "Ошибки в документе"}
    )
    assert response.status_code == 200
    
    # Проверяем, что статус изменился
    db_session.refresh(doc)
    assert doc.status == FinalDocumentStatus.REJECTED
    assert doc.rejection_reason == "Ошибки в документе"


def test_sign_already_signed_document(client, db_session):
    """Тест подписания уже подписанного документа"""
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
    
    doc_id = uuid4()
    doc = FinalDocument(
        id=doc_id,
        project_id=project_id,
        title="Акт приёмки",
        status=FinalDocumentStatus.SIGNED,
        signed_at=datetime.utcnow()
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.post(f"/api/v1/projects/{project_id}/final-documents/{doc_id}/sign")
    assert response.status_code == 400


def test_completion_status_completed(client, db_session):
    """Тест статуса завершения при полном завершении"""
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
    
    site = ConstructionSite(
        id=uuid4(),
        project_id=project_id,
        progress=1.0
    )
    db_session.add(site)
    
    doc = FinalDocument(
        id=uuid4(),
        project_id=project_id,
        title="Акт приёмки",
        status=FinalDocumentStatus.SIGNED,
        signed_at=datetime.utcnow()
    )
    db_session.add(doc)
    db_session.commit()
    
    response = client.get(f"/api/v1/projects/{project_id}/completion-status")
    assert response.status_code == 200
    data = response.json()
    assert data["isCompleted"] == True
    assert data["completionDate"] is not None

