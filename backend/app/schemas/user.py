from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import Literal

# Base Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr


# Schema for User Registration
class UserCreate(UserBase):
    password: str


# Schema for Returning User Details
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    role: str

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserRoleUpdate(BaseModel):
    role: Literal["User", "Admin"]

class DashboardResponse(BaseModel):
    total_users: int
    total_admins: int
    total_normal_users: int
    recent_users: list[UserResponse]