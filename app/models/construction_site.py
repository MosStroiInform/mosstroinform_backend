from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base


class Camera(Base):
    """Модель камеры на строительной площадке"""
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    construction_site_id = Column(UUID(as_uuid=True), ForeignKey("construction_sites.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    stream_url = Column(String(1000), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    construction_site = relationship("ConstructionSite", back_populates="cameras")


class ConstructionSite(Base):
    """Модель строительной площадки"""
    __tablename__ = "construction_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    start_date = Column(DateTime, nullable=True)
    expected_completion_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0, nullable=False)  # от 0.0 до 1.0
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="construction_site")
    cameras = relationship("Camera", back_populates="construction_site", cascade="all, delete-orphan")

