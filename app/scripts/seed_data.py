"""
Скрипт для заполнения базы данных тестовыми данными.

Запуск:
    python -m app.scripts.seed_data
"""
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.project import Project, ProjectStage, StageStatus
from app.models.document import Document, DocumentStatus
from app.models.construction_site import ConstructionSite, Camera
from app.models.chat import Chat, Message
from app.models.completion import FinalDocument, FinalDocumentStatus


def create_tables():
    """Создает все таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)


def clear_data(db: Session):
    """Очищает все данные из базы"""
    db.query(Message).delete()
    db.query(Chat).delete()
    db.query(Camera).delete()
    db.query(ConstructionSite).delete()
    db.query(FinalDocument).delete()
    db.query(Document).delete()
    db.query(ProjectStage).delete()
    db.query(Project).delete()
    db.commit()


def seed_projects(db: Session) -> list[Project]:
    """Создает тестовые проекты"""
    projects = [
        Project(
            id=uuid4(),
            name="Дом на участке 6 соток",
            address="Московская область, д. Примерное, ул. Садовая, 15",
            description="Двухэтажный дом с гаражом и террасой. Общая площадь 120.5 кв.м.",
            area=120.5,
            floors=2,
            price=5000000,
            image_url="https://example.com/images/house1.jpg"
        ),
        Project(
            id=uuid4(),
            name="Коттедж в стиле модерн",
            address="Московская область, КП Лесная поляна, 42",
            description="Современный коттедж с панорамными окнами. Площадь 180 кв.м.",
            area=180.0,
            floors=2,
            price=8500000,
            image_url="https://example.com/images/house2.jpg"
        ),
        Project(
            id=uuid4(),
            name="Дачный дом эконом-класса",
            address="Тверская область, СНТ Ромашка, участок 23",
            description="Компактный одноэтажный дом для сезонного проживания.",
            area=65.0,
            floors=1,
            price=2200000,
            image_url="https://example.com/images/house3.jpg"
        ),
    ]
    
    for project in projects:
        db.add(project)
    db.commit()
    
    return projects


def seed_stages(db: Session, projects: list[Project]):
    """Создает этапы для проектов"""
    stage_templates = [
        ("Фундамент", StageStatus.COMPLETED),
        ("Стены", StageStatus.IN_PROGRESS),
        ("Кровля", StageStatus.PENDING),
        ("Инженерные сети", StageStatus.PENDING),
        ("Отделка", StageStatus.PENDING),
    ]
    
    for project in projects:
        for name, status in stage_templates:
            stage = ProjectStage(
                id=uuid4(),
                project_id=project.id,
                name=name,
                status=status
            )
            db.add(stage)
    
    db.commit()


def seed_documents(db: Session, projects: list[Project]):
    """Создает документы для проектов"""
    doc_templates = [
        ("Проектная документация", "Полный комплект проектной документации", DocumentStatus.APPROVED),
        ("Разрешение на строительство", "Официальное разрешение от местных властей", DocumentStatus.APPROVED),
        ("Смета на строительство", "Детальная смета всех работ", DocumentStatus.UNDER_REVIEW),
        ("Договор подряда", "Договор с подрядной организацией", DocumentStatus.PENDING),
    ]
    
    for project in projects:
        for title, description, status in doc_templates:
            submitted_at = datetime.utcnow() - timedelta(days=30)
            approved_at = datetime.utcnow() - timedelta(days=15) if status == DocumentStatus.APPROVED else None
            
            doc = Document(
                id=uuid4(),
                project_id=project.id,
                title=title,
                description=description,
                file_url=f"https://example.com/files/{project.id}/{title.replace(' ', '_').lower()}.pdf",
                status=status,
                submitted_at=submitted_at,
                approved_at=approved_at
            )
            db.add(doc)
    
    db.commit()


def seed_construction_sites(db: Session, projects: list[Project]):
    """Создает строительные площадки и камеры"""
    for i, project in enumerate(projects):
        progress = [0.35, 0.65, 0.15][i]
        
        site = ConstructionSite(
            id=uuid4(),
            project_id=project.id,
            start_date=datetime.utcnow() - timedelta(days=90),
            expected_completion_date=datetime.utcnow() + timedelta(days=180),
            progress=progress
        )
        db.add(site)
        db.flush()  # Получаем ID для связи с камерами
        
        # Добавляем камеры
        cameras = [
            Camera(
                id=uuid4(),
                construction_site_id=site.id,
                name="Камера 1 - Главный фасад",
                description="Обзор главного фасада здания",
                stream_url=f"rtsp://example.com/stream/{site.id}/cam1",
                is_active=True,
                thumbnail_url=f"https://example.com/thumbnails/{site.id}/cam1.jpg"
            ),
            Camera(
                id=uuid4(),
                construction_site_id=site.id,
                name="Камера 2 - Задний двор",
                description="Обзор заднего двора и стройматериалов",
                stream_url=f"rtsp://example.com/stream/{site.id}/cam2",
                is_active=True,
                thumbnail_url=f"https://example.com/thumbnails/{site.id}/cam2.jpg"
            ),
        ]
        
        for camera in cameras:
            db.add(camera)
    
    db.commit()


def seed_chats(db: Session, projects: list[Project]):
    """Создает чаты и сообщения"""
    specialists = [
        ("Иван Петров", "https://example.com/avatars/ivan.jpg"),
        ("Мария Сидорова", "https://example.com/avatars/maria.jpg"),
        ("Алексей Козлов", None),
    ]
    
    for i, project in enumerate(projects):
        specialist_name, avatar_url = specialists[i % len(specialists)]
        
        chat = Chat(
            id=uuid4(),
            project_id=project.id,
            specialist_name=specialist_name,
            specialist_avatar_url=avatar_url,
            is_active=True
        )
        db.add(chat)
        db.flush()
        
        # Добавляем сообщения
        messages = [
            Message(
                id=uuid4(),
                chat_id=chat.id,
                text="Добрый день! У меня вопрос по документам.",
                sent_at=datetime.utcnow() - timedelta(hours=5),
                is_from_specialist=False,
                is_read=True
            ),
            Message(
                id=uuid4(),
                chat_id=chat.id,
                text="Здравствуйте! Конечно, задавайте вопросы.",
                sent_at=datetime.utcnow() - timedelta(hours=4, minutes=55),
                is_from_specialist=True,
                is_read=True
            ),
            Message(
                id=uuid4(),
                chat_id=chat.id,
                text="Когда будет готов проект?",
                sent_at=datetime.utcnow() - timedelta(hours=2),
                is_from_specialist=False,
                is_read=True
            ),
            Message(
                id=uuid4(),
                chat_id=chat.id,
                text="Проект будет готов в течение недели.",
                sent_at=datetime.utcnow() - timedelta(hours=1),
                is_from_specialist=True,
                is_read=False
            ),
        ]
        
        for message in messages:
            db.add(message)
    
    db.commit()


def seed_final_documents(db: Session, projects: list[Project]):
    """Создает финальные документы для завершения строительства"""
    final_doc_templates = [
        ("Акт приёмки-передачи", "Документ о приёмке готового объекта"),
        ("Гарантийное обязательство", "Гарантия на выполненные работы"),
        ("Технический паспорт", "Технический паспорт объекта"),
    ]
    
    for project in projects:
        for title, description in final_doc_templates:
            doc = FinalDocument(
                id=uuid4(),
                project_id=project.id,
                title=title,
                description=description,
                file_url=f"https://example.com/files/{project.id}/final_{title.replace(' ', '_').lower()}.pdf",
                status=FinalDocumentStatus.PENDING,
                submitted_at=datetime.utcnow() - timedelta(days=5)
            )
            db.add(doc)
    
    db.commit()


def seed_all():
    """Заполняет базу данных всеми тестовыми данными"""
    print("Создание таблиц...")
    create_tables()
    
    db = SessionLocal()
    try:
        print("Очистка существующих данных...")
        clear_data(db)
        
        print("Создание проектов...")
        projects = seed_projects(db)
        
        print("Создание этапов проектов...")
        seed_stages(db, projects)
        
        print("Создание документов...")
        seed_documents(db, projects)
        
        print("Создание строительных площадок и камер...")
        seed_construction_sites(db, projects)
        
        print("Создание чатов и сообщений...")
        seed_chats(db, projects)
        
        print("Создание финальных документов...")
        seed_final_documents(db, projects)
        
        print("\n✅ База данных успешно заполнена тестовыми данными!")
        print(f"   Создано проектов: {len(projects)}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при заполнении базы данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()

