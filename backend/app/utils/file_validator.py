from pathlib import Path
from fastapi import HTTPException, status

from app.core.config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE

def validate_file_extension(filename: str):

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are allowed."
        )
    return extension

def validate_mime_type(content_type: str):

    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX and TXT files are allowed."
        )

    return content_type

def validate_file_size(file):

    # Move cursor to end of file
    file.file.seek(0, 2)

    # Get file size
    file_size = file.file.tell()

    # Reset cursor to beginning
    file.file.seek(0)

    # Validate size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit."
        )

    return file_size