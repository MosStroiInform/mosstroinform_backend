import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.models.project import Project
from app.models.construction_site import ConstructionSite, Camera


def test_get_construction_site_by_project(client, db_session):
    """Тест получения строительной площадки по проекту"""
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
    
    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        start_date=datetime.utcnow() - timedelta(days=30),
        expected_completion_date=datetime.utcnow() + timedelta(days=180),
        progress=0.35
    )
    db_session.add(site)
    db_session.commit()
    
    response = client.get(f"/api/v1/construction-sites/project/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(site_id)
    assert data["project_name"] == "Тестовый проект"
    assert data["progress"] == 0.35
    assert data["progress"] == 0.35


def test_get_construction_site_not_found(client, db_session):
    """Тест получения несуществующей строительной площадки"""
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
    db_session.commit()
    
    response = client.get(f"/api/v1/construction-sites/project/{project_id}")
    assert response.status_code == 404


def test_get_cameras(client, db_session):
    """Тест получения списка камер"""
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
    
    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        progress=0.5
    )
    db_session.add(site)
    
    camera = Camera(
        id=uuid4(),
        construction_site_id=site_id,
        name="Камера 1",
        description="Тестовая камера",
        stream_url="rtsp://example.com/stream/1",
        is_active=True,
        thumbnail_url="https://example.com/thumb1.jpg"
    )
    db_session.add(camera)
    db_session.commit()
    
    response = client.get(f"/api/v1/construction-sites/{site_id}/cameras")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Камера 1"


def test_get_camera_by_id(client, db_session):
    """Тест получения камеры по ID"""
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
    
    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        progress=0.5
    )
    db_session.add(site)
    
    camera_id = uuid4()
    camera = Camera(
        id=camera_id,
        construction_site_id=site_id,
        name="Камера 2",
        description="Детальная камера",
        stream_url="rtsp://example.com/stream/2",
        is_active=True
    )
    db_session.add(camera)
    db_session.commit()
    
    response = client.get(f"/api/v1/construction-sites/{site_id}/cameras/{camera_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(camera_id)
    assert data["name"] == "Камера 2"


def test_get_camera_not_found(client, db_session):
    """Тест получения несуществующей камеры"""
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
    
    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        progress=0.5
    )
    db_session.add(site)
    db_session.commit()
    
    fake_camera_id = uuid4()
    response = client.get(f"/api/v1/construction-sites/{site_id}/cameras/{fake_camera_id}")
    assert response.status_code == 404

