from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Статусы документов"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Document(Base):
    """Модель документа, требующего согласования"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    file_url = Column(String(1000), nullable=True)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="documents")

