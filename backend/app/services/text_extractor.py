from pathlib import Path

from fastapi import HTTPException, status

from app.services.pdf_extractor import extract_pdf_text
from app.services.docx_extractor import extract_docx_text
from app.services.txt_extractor import extract_txt_text


def extract_text(file_path: Path, file_type: str) -> str:
    """
    Extract text based on the uploaded file type.
    """

    if file_type == ".pdf":
        return extract_pdf_text(file_path)

    elif file_type == ".docx":
        return extract_docx_text(file_path)

    elif file_type == ".txt":
        return extract_txt_text(file_path)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported document type."
    )