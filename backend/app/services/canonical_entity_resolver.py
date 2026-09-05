from sqlalchemy.orm import Session

from app.models.canonical_entity import CanonicalEntity
from app.models.entity_alias import EntityAlias


def find_or_create_canonical_entity(
    db: Session,
    entity_data: dict
) -> CanonicalEntity:

    normalized_name = entity_data["normalized_name"]
    entity_type = entity_data["entity_type"]

    # --------------------------------------------------
    # 1. Check exact canonical entity
    # --------------------------------------------------
    canonical_entity = (
        db.query(CanonicalEntity)
        .filter(
            CanonicalEntity.normalized_name == normalized_name,
            CanonicalEntity.entity_type == entity_type
        )
        .first()
    )

    if canonical_entity:
        return canonical_entity

    # --------------------------------------------------
    # 2. Check known alias
    # --------------------------------------------------
    alias = (
        db.query(EntityAlias)
        .filter(
            EntityAlias.normalized_alias == normalized_name,
            EntityAlias.entity_type == entity_type
        )
        .first()
    )

    if alias:
        canonical_entity = (
            db.query(CanonicalEntity)
            .filter(
                CanonicalEntity.id == alias.canonical_entity_id
            )
            .first()
        )

        if canonical_entity:
            return canonical_entity

    # --------------------------------------------------
    # 3. Create new canonical entity
    # --------------------------------------------------
    canonical_entity = CanonicalEntity(
        entity_name=entity_data["entity_name"],
        normalized_name=normalized_name,
        entity_type=entity_type
    )

    db.add(canonical_entity)
    db.flush()

    return canonical_entity