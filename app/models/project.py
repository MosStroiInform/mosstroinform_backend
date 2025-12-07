from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class StageStatus(str, enum.Enum):
    """Статусы этапов строительства"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ProjectStatus(str, enum.Enum):
    """Статусы проекта"""
    AVAILABLE = "available"
    REQUESTED = "requested"
    CONSTRUCTION = "construction"


class ProjectStage(Base):
    """Модель этапа строительства проекта"""
    __tablename__ = "project_stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(StageStatus), nullable=False, default=StageStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="stages")


class Project(Base):
    """Модель проекта строительства"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    description = Column(String(2000), nullable=True)
    area = Column(Float, nullable=False)
    floors = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String(1000), nullable=True)
    bedrooms = Column(Integer, nullable=False, default=0)
    bathrooms = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    stages = relationship("ProjectStage", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    construction_site = relationship("ConstructionSite", back_populates="project", uselist=False, cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="project", cascade="all, delete-orphan")
    final_documents = relationship("FinalDocument", back_populates="project", cascade="all, delete-orphan")

    @property
    def object_id(self):
        """Возвращает ID строительной площадки (objectId) проекта, если создана."""
        if self.construction_site:
            return self.construction_site.id
        return None

