from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


# Base Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "User"


# Schema for User Registration
class UserCreate(UserBase):
    password: str


# Schema for Returning User Details
class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True