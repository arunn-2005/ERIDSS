import sys
import os

from sqlalchemy.orm import Session

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

from app.database.database import SessionLocal
from app.models.entity import Entity
from app.models.canonical_entity import CanonicalEntity


def backfill_canonical_entities():
    db: Session = SessionLocal()

    try:
        entities = db.query(Entity).order_by(Entity.created_at).all()

        print(f"Found {len(entities)} existing entities.")

        for entity in entities:

            # Skip if already linked
            if entity.canonical_entity_id is not None:
                print(
                    f"SKIP: {entity.entity_name} "
                    f"already linked."
                )
                continue

            # Find existing canonical entity
            canonical_entity = (
                db.query(CanonicalEntity)
                .filter(
                    CanonicalEntity.normalized_name
                    == entity.normalized_name,
                    CanonicalEntity.entity_type
                    == entity.entity_type
                )
                .first()
            )

            # Create canonical entity if it doesn't exist
            if canonical_entity is None:

                canonical_entity = CanonicalEntity(
                    entity_name=entity.entity_name,
                    normalized_name=entity.normalized_name,
                    entity_type=entity.entity_type,
                )

                db.add(canonical_entity)
                db.flush()

                print(
                    f"CREATED: {canonical_entity.entity_name}"
                )

            # Link entity mention to canonical entity
            entity.canonical_entity_id = canonical_entity.id

            print(
                f"LINKED: {entity.entity_name} "
                f"-> {canonical_entity.entity_name}"
            )

        db.commit()

        print("\nBackfill completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_canonical_entities()