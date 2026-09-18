from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid, shutil
from typing import Optional
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone

from app.database.db import get_db
from app.models.user import User
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.extracted_text import ExtractedText
from app.models.entity import Entity
from app.models.entity_evidence import EntityEvidence
from app.models.relationship import KnowledgeGraph
from app.dependencies.auth import get_current_user
from app.utils.file_validator import validate_file_extension, validate_mime_type, validate_file_size
from app.core.config import UPLOAD_DIR, EXTRACTION_METHODS
from app.schemas.document import DocumentPublicResponse

from app.services.text_extractor import extract_text 
from app.services.relation_extractor import extract_and_persist_relations

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentPublicResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_extension = validate_file_extension(file.filename)
    mime_type = validate_mime_type(file.content_type)
    file_size = validate_file_size(file)

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )
    
    document = Document(
        filename=file.filename,
        stored_filename=unique_filename,
        file_path=str(file_path),
        file_type=file_extension,
        mime_type=mime_type,
        file_size=file_size,
        status="Uploaded",
        user_id=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post(
    "/{document_id}/process",
    status_code=status.HTTP_200_OK
)
def process_document(
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
    
    if document.status == "Processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already being processed."
        )

    if document.status == "Processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has already been processed."
        )
    
    processing_job = ProcessingJob(
        document_id=document.id,
        stage="Extraction",
        status="Running"
    )

    db.add(processing_job)
    document.status = "Processing"
    db.commit()
    db.refresh(processing_job)
    db.refresh(document)

    try:
        # 1. Extract Text
        text = extract_text(
            file_path=Path(document.file_path),
            file_type=document.file_type
        )

        extracted_text = ExtractedText(
            document_id=document.id,
            extracted_text=text,
            extraction_method=EXTRACTION_METHODS[document.file_type]
        )
        db.add(extracted_text)
        db.commit()

        # 2. Fetch Extracted Entities for Graph Construction
        saved_entities = (
            db.query(Entity)
            .filter(Entity.document_id == document.id)
            .all()
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

        # 3. Extract & Persist Relationships + Knowledge Graph
        if persisted_entities_payload:
            extract_and_persist_relations(
                db=db,
                document_id=str(document.id),
                text=text,
                persisted_entities=persisted_entities_payload
            )

        processing_job.status = "Completed"
        processing_job.completed_at = datetime.now(timezone.utc)

        document.status = "Processed"
        document.processed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(extracted_text)
        db.refresh(processing_job)
        db.refresh(document)

    except Exception as e:
        db.rollback()
        processing_job.status = "Failed"
        processing_job.error_message = str(e)
        processing_job.completed_at = datetime.now(timezone.utc)

        document.status = "Failed"
        document.processed_at = datetime.now(timezone.utc)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )

    return {"message": "Document processed successfully", "document_id": document.id}


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
            detail="No entities found for this document. Extract entities before extracting relations."
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


@router.get("/{document_id}/graph")
def get_document_knowledge_graph(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        doc_uuid = uuid.UUID(str(document_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    # Ensure document exists and belongs to the authenticated user
    document = (
        db.query(Document)
        .filter(
            Document.id == doc_uuid,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # Query using string and UUID compatibility
    kg = (
        db.query(KnowledgeGraph)
        .filter(
            (KnowledgeGraph.document_id == doc_uuid) | 
            (KnowledgeGraph.document_id == str(doc_uuid))
        )
        .first()
    )

    if not kg or not kg.graph_data:
        return {"nodes": [], "edges": []}

    return kg.graph_data


@router.get(
    "/my-documents",
    response_model=list[DocumentPublicResponse]
)
def get_my_documents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of documents per page"),
    search: Optional[str] = None,
    status: Optional[str] = None,
    file_type: Optional[str] = None,
    sort: str = Query("file_size"),
    order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))
    if status:
        query = query.filter(Document.status == status)
    if file_type:
        query = query.filter(Document.file_type == file_type)

    sort_columns = {
        "filename": Document.filename,
        "uploaded_at": Document.uploaded_at,
        "file_size": Document.file_size,
    }

    sort_column = sort_columns.get(sort)
    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field."
        )

    if order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be 'asc' or 'desc'."
        )

    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.offset(offset).limit(limit).all()


@router.get(
    "/{document_id}",
    response_model=DocumentPublicResponse
)
def get_document(
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

    return document


@router.get("/{document_id}/download")
def download_document(
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

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server."
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.filename
    )


@router.get("/{document_id}/view")
def view_document(
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

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server."
        )

    if document.mime_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file type cannot be viewed directly. Please download it."
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        headers={"Content-Disposition": f'inline; filename="{document.filename}"'}
    )


@router.delete("/{document_id}")
def delete_document(
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

    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully."}