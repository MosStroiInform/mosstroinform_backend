import pytest
from uuid import uuid4
from app.models.project import Project, ProjectStage, StageStatus


def test_get_projects_empty(client):
    """Тест получения пустого списка проектов"""
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_get_projects(client, db_session):
    """Тест получения списка проектов"""
    # Создаем тестовый проект
    project = Project(
        id=uuid4(),
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        description="Описание проекта",
        area=100.5,
        floors=2,
        price=5000000.0,
        image_url="https://example.com/image.jpg"
    )
    db_session.add(project)
    db_session.commit()
    
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Тестовый проект"
    assert data[0]["address"] == "Москва, ул. Тестовая, 1"


def test_get_project_by_id(client, db_session):
    """Тест получения проекта по ID"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        description="Описание проекта",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    db_session.commit()
    
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(project_id)
    assert data["name"] == "Тестовый проект"


def test_get_project_not_found(client):
    """Тест получения несуществующего проекта"""
    fake_id = uuid4()
    response = client.get(f"/api/v1/projects/{fake_id}")
    assert response.status_code == 404
    assert "error" in response.json()


def test_request_construction(client, db_session):
    """Тест запроса на строительство"""
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Тестовый проект",
        address="Москва, ул. Тестовая, 1",
        description="Описание проекта",
        area=100.5,
        floors=2,
        price=5000000.0
    )
    db_session.add(project)
    db_session.commit()
    
    response = client.post(f"/api/v1/projects/{project_id}/request")
    assert response.status_code == 204

