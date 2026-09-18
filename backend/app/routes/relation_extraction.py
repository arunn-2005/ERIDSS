import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.models.document import Document
from app.models.extracted_text import ExtractedText
from app.models.entity import Entity
from app.dependencies.auth import get_current_user
from app.services.relation_extractor import extract_and_persist_relations

router = APIRouter(
    prefix="/documents",
    tags=["Relation Extraction"]
)

@router.post(
    "/{document_id}/extract-relations",
    status_code=status.HTTP_200_OK
)
def extract_document_relations(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    extracted_text_obj = (
        db.query(ExtractedText)
        .filter(ExtractedText.document_id == document_id)
        .first()
    )

    if not extracted_text_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted text found for this document. Run text processing first."
        )

    saved_entities = (
        db.query(Entity)
        .filter(Entity.document_id == document_id)
        .all()
    )

    if not saved_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No entities found for this document. Run extract-entities first."
        )

    persisted_entities_payload = [
        {
            "id": str(e.id),
            "entity_name": getattr(e, "name", getattr(e, "entity_name", "")),
            "entity_type": getattr(e, "entity_type", "ENTITY"),
            "start": getattr(e, "start_char", 0),
            "end": getattr(e, "end_char", 0)
        }
        for e in saved_entities
    ]

    graph_payload = extract_and_persist_relations(
        db=db,
        document_id=str(document_id),
        text=extracted_text_obj.extracted_text,
        persisted_entities=persisted_entities_payload
    )

    return {
        "message": "Relationships extracted successfully.",
        "graph": graph_payload
    }