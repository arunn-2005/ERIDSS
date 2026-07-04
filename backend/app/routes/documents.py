from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import uuid, shutil

from app.database.db import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.utils.file_validator import validate_file_extension, validate_mime_type, validate_file_size
from app.core.config import UPLOAD_DIR
from app.models.document import Document
from app.schemas.document import DocumentPublicResponse

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