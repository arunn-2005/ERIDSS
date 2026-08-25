import uuid

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.models.user import User
from app.models.document import Document
from app.models.extracted_text import ExtractedText
from app.models.entity import Entity
from app.models.entity_evidence import EntityEvidence
from app.models.processing_job import ProcessingJob

from app.dependencies.auth import get_current_user

from app.services.entity_extractor import extract_entities
from app.services.pii_detector import (
    detect_pii,
    mask_pii
)


router = APIRouter(
    prefix="/documents",
    tags=["Entity Extraction"]
)


@router.post(
    "/{document_id}/extract-entities",
    status_code=status.HTTP_200_OK
)
def extract_document_entities(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ---------------------------------
    # 1. Find document
    # ---------------------------------

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


    # ---------------------------------
    # 2. Get extracted text
    # ---------------------------------

    extracted_text = (
        db.query(ExtractedText)
        .filter(
            ExtractedText.document_id == document.id
        )
        .first()
    )

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text has not been extracted yet."
        )


    # ---------------------------------
    # 3. Check running NLP job
    # ---------------------------------

    existing_job = (
        db.query(ProcessingJob)
        .filter(
            ProcessingJob.document_id == document.id,
            ProcessingJob.stage == "NLP",
            ProcessingJob.status == "Running"
        )
        .first()
    )

    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity extraction is already in progress."
        )


    # ---------------------------------
    # 4. Create NLP processing job
    # ---------------------------------

    processing_job = ProcessingJob(
        document_id=document.id,
        stage="NLP",
        status="Running",
        started_at=datetime.now(timezone.utc)
    )

    db.add(processing_job)

    db.commit()

    db.refresh(processing_job)


    try:

        # ---------------------------------
        # 5. Detect and mask PII
        # ---------------------------------

        raw_text = extracted_text.extracted_text

        pii_results = detect_pii(raw_text)

        sanitized_text = mask_pii(
            raw_text,
            pii_results
        )

        # ---------------------------------
        # 6. Extract enterprise entities
        # ---------------------------------

        extracted_entities = extract_entities(
            sanitized_text
        )

        saved_entities = []


        # ---------------------------------
        # 7. Process entities
        # ---------------------------------

        for entity_data in extracted_entities:

            entity = (
                db.query(Entity)
                .filter(
                    Entity.document_id == document.id,
                    Entity.normalized_name
                    == entity_data["normalized_name"],
                    Entity.entity_type
                    == entity_data["entity_type"]
                )
                .first()
            )


            # ---------------------------------
            # 8. Create entity if new
            # ---------------------------------

            if not entity:

                entity = Entity(
                    document_id=document.id,
                    entity_name=entity_data["entity_name"],
                    normalized_name=entity_data["normalized_name"],
                    entity_type=entity_data["entity_type"],
                    confidence_score=entity_data["confidence_score"]
                )

                db.add(entity)

                db.flush()


            # ---------------------------------
            # 9. Check duplicate evidence
            # ---------------------------------

            for evidence_data in entity_data["evidence"]:

                existing_evidence = (
                    db.query(EntityEvidence)
                    .filter(
                        EntityEvidence.entity_id == entity.id,
                        EntityEvidence.document_id == document.id,
                        EntityEvidence.source_text
                        == evidence_data["source_text"]
                    )
                    .first()
                )


            # ---------------------------------
            # 10. Create evidence
            # ---------------------------------

            if not existing_evidence:

                evidence = EntityEvidence(
                    entity_id=entity.id,
                    document_id=document.id,
                    source_text=evidence_data["source_text"]
                )

                db.add(evidence)


            if entity not in saved_entities:
                saved_entities.append(entity)


        # ---------------------------------
        # 11. Mark job completed
        # ---------------------------------

        processing_job.status = "Completed"

        processing_job.completed_at = (
            datetime.now(timezone.utc)
        )


        db.commit()


        # ---------------------------------
        # 12. Refresh
        # ---------------------------------

        db.refresh(processing_job)

        for entity in saved_entities:
            db.refresh(entity)


        # ---------------------------------
        # 13. Return response
        # ---------------------------------

        return {
            "message": "Entity extraction completed successfully.",
            "document_id": document.id,
            "processing_job_id": processing_job.id,
            "entities": [
                {
                    "id": entity.id,
                    "entity_name": entity.entity_name,
                    "normalized_name": entity.normalized_name,
                    "entity_type": entity.entity_type,
                    "confidence_score": entity.confidence_score
                }
                for entity in saved_entities
            ]
        }


    except Exception as e:

        processing_job.status = "Failed"
        processing_job.completed_at = (
            datetime.now(timezone.utc)
        )
        processing_job.error_message = str(e)

        db.commit()

        print("ENTITY EXTRACTION ERROR:", repr(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )