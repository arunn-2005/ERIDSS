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
from app.dependencies.auth import get_current_user
from app.utils.file_validator import validate_file_extension, validate_mime_type, validate_file_size
from app.core.config import UPLOAD_DIR, EXTRACTION_METHODS
from app.schemas.document import DocumentPublicResponse
from app.services.text_extractor import extract_text 

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentPublicResponse,status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file extension
    file_extension = validate_file_extension(file.filename)

    # Validate MIME type
    mime_type = validate_mime_type(file.content_type)

    # Validate file size
    file_size = validate_file_size(file)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Create file path
    file_path = UPLOAD_DIR / unique_filename

    # Save file
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
    
    # Save to database
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
            detail="Document processing failed."
        )

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

    print("Page:", page)
    print("Limit:", limit)
    print("Search:", search)
    print("Status:", status)
    print("File Type:", file_type)
    
    offset = (page-1) * limit

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

    documents = (
        query 
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return documents


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

    if document.mime_type not in [
        "application/pdf",
        "text/plain"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file type cannot be viewed directly. Please download it."
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{document.filename}"'
        }
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

    return {
        "message": "Document deleted successfully."
    }