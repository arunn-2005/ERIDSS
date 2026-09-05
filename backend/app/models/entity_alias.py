import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class EntityAlias(Base):
    __tablename__ = "entity_aliases"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    canonical_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("canonical_entities.id"),
        nullable=False
    )

    alias_name = Column(
        String(255),
        nullable=False
    )

    normalized_alias = Column(
        String(255),
        nullable=False
    )

    entity_type = Column(
        String(100),
        nullable=False
    )

    alias_type = Column(
        String(50),
        nullable=False
    )