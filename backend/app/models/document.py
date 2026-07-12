import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    BigInteger,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    filename = Column(
        String(255),
        nullable=False
    )

    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True
    )

    file_path = Column(
        Text,
        nullable=False
    )

    file_type = Column(
        String(20),
        nullable=False
    )

    mime_type = Column(
        String(100),
        nullable=False
    )

    file_size = Column(
        BigInteger,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="Uploaded"
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    processing_jobs = relationship(
        "ProcessingJob",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    extracted_text = relationship(
        "ExtractedText",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan"
    )