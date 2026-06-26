from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.utils.password import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user