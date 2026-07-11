from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import asc, desc
import uuid
from pathlib import Path
from fastapi.responses import FileResponse

from app.database.db import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.models.document import Document
from app.schemas.document import AdminDocumentResponse, DocumentDashboardResponse, RecentDocumentResponse

router = APIRouter(
    prefix="/admin/documents",
    tags=["Admin Documents"]
)

@router.get(
    "/get_all_documents",
    response_model=list[AdminDocumentResponse]
)
def getAllDocuments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Documents per page"),
    search: Optional[str] = None,
    status: Optional[str] = None,
    file_type: Optional[str] = None,
    sort: str = Query("uploaded_at"),
    order: str = Query("desc"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    offset = (page - 1) * limit

    query = (
        db.query(Document, User)
        .join(User, Document.user_id == User.id)
    )

    # Search
    if search:
        query = query.filter(
            Document.filename.ilike(f"%{search}%")
        )

    # Filter by status
    if status:
        query = query.filter(
            Document.status == status
        )

    # Filter by file type
    if file_type:
        query = query.filter(
            Document.file_type == file_type
        )

    # Sorting
    sortable_columns = {
        "filename": Document.filename,
        "uploaded_at": Document.uploaded_at,
        "file_size": Document.file_size,
        "status": Document.status,
        "username": User.username
    }

    sort_column = sortable_columns.get(sort, Document.uploaded_at)

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Pagination
    results = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    response = []

    for document, user in results:
        response.append(
            AdminDocumentResponse(
                id=document.id,
                filename=document.filename,
                file_type=document.file_type,
                status=document.status,
                uploaded_at=document.uploaded_at,

                user_id=user.id,
                username=user.username,
                email=user.email
            )
        )

    return response

@router.get(
    "/dashboard",
    response_model=DocumentDashboardResponse
)
def get_document_dashboard(
    limit: int = Query(5, ge=1, le=20),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    total_documents = db.query(Document).count()

    uploaded_documents = (
        db.query(Document)
        .filter(Document.status == "Uploaded")
        .count()
    )

    processing_documents = (
        db.query(Document)
        .filter(Document.status == "Processing")
        .count()
    )

    processed_documents = (
        db.query(Document)
        .filter(Document.status == "Processed")
        .count()
    )

    failed_documents = (
        db.query(Document)
        .filter(Document.status == "Failed")
        .count()
    )

    recent_documents = (
        db.query(Document, User)
        .join(User, Document.user_id == User.id)
        .order_by(Document.uploaded_at.desc())
        .limit(limit)
        .all()
    )

    recent_response = []

    for document, user in recent_documents:
        recent_response.append(
            RecentDocumentResponse(
                id=document.id,
                filename=document.filename,
                status=document.status,
                uploaded_at=document.uploaded_at,
                username=user.username
            )
        )

    return DocumentDashboardResponse(
        total_documents=total_documents,
        uploaded_documents=uploaded_documents,
        processing_documents=processing_documents,
        processed_documents=processed_documents,
        failed_documents=failed_documents,
        recent_documents=recent_response
    )

@router.get(
    "/{document_id}/download"
)
def download_document(
    document_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
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
            detail="File not found on the server."
        )

    return FileResponse(
        path=file_path,
        filename=document.filename,
        media_type=document.mime_type
    )

@router.get(
    "/{document_id}/view"
)
def view_document_in_browser(
    document_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
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
            detail="File not found on the server."
        )
    
    if document.mime_type not in ["application/pdf", "text/plain" ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file type cannot be viewed directly. Please download it."
        )
     
    
    return FileResponse(
        path = file_path,
        media_type = document.mime_type,
        headers = {"Content-Disposition": f"inline; filename={document.filename}"}
    )

@router.delete(
    "/{document_id}/delete"
)
def delete_document(
    document_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
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

    return { "message": "Document deleted successfully." }

@router.get(
    "/{document_id}",
    response_model=AdminDocumentResponse
)
def get_document_by_id(
    document_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    result = (
        db.query(Document, User)
        .join(User, Document.user_id == User.id)
        .filter(Document.id == document_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    document, user = result

    return AdminDocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        status=document.status,
        uploaded_at=document.uploaded_at,

        user_id=user.id,
        username=user.username,
        email=user.email
    )
