# app/models/entity.py

import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class Entity(Base):

    __tablename__ = "entities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    entity_name = Column(
        String(255),
        nullable=False
    )

    normalized_name = Column(
        String(255),
        nullable=False
    )

    entity_type = Column(
        String(100),
        nullable=False
    )

    confidence_score = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )