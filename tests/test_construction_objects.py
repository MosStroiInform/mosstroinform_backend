from uuid import uuid4

from app.models.project import Project
from app.models.construction_site import ConstructionSite


def test_get_construction_objects(client, db_session):
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Проект объекта",
        address="МО, ул. Тестовая, 5",
        area=110.0,
        floors=2,
        price=4500000.0,
        bedrooms=3,
        bathrooms=2,
    )
    db_session.add(project)

    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        progress=0.4,
    )
    db_session.add(site)
    db_session.commit()

    response = client.get("/api/v1/construction-objects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(site_id)
    assert data[0]["projectId"] == str(project_id)
    assert data[0]["allDocumentsSigned"] is False
    assert data[0]["isCompleted"] is False


def test_complete_construction_object(client, db_session):
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Проект завершения",
        address="СПб, ул. Строителей, 3",
        area=95.0,
        floors=2,
        price=3800000.0,
    )
    db_session.add(project)

    site_id = uuid4()
    site = ConstructionSite(
        id=site_id,
        project_id=project_id,
        progress=1.0,
        all_documents_signed=True,
    )
    db_session.add(site)
    db_session.commit()

    response = client.post(f"/api/v1/construction-objects/{site_id}/complete")
    assert response.status_code == 204

    db_session.refresh(site)
    assert site.is_completed is True


def test_update_documents_status(client, db_session):
    project_id = uuid4()
    project = Project(
        id=project_id,
        name="Проект документов",
        address="МО, ул. Док, 7",
        area=70.0,
        floors=1,
        price=2000000.0,
    )
    db_session.add(project)

    site = ConstructionSite(
        id=uuid4(),
        project_id=project_id,
        progress=0.2,
        all_documents_signed=False,
    )
    db_session.add(site)
    db_session.commit()

    response = client.patch(
        f"/api/v1/construction-objects/by-project/{project_id}/documents-status",
        json={"allDocumentsSigned": True},
    )
    assert response.status_code == 204

    db_session.refresh(site)
    assert site.all_documents_signed is True

