from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    stored_filename: str
    file_path: str
    file_type: str
    mime_type: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True

class DocumentPublicResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True

class AdminDocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    status: str
    uploaded_at: datetime

    user_id: UUID
    username: str
    email: EmailStr

class RecentDocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    uploaded_at: datetime
    username: str

    model_config = {
        "from_attributes": True
    }


class DocumentDashboardResponse(BaseModel):
    total_documents: int
    uploaded_documents: int
    processing_documents: int
    processed_documents: int
    failed_documents: int

    recent_documents: list[RecentDocumentResponse]