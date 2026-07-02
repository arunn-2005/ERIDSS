from pydantic import BaseModel
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