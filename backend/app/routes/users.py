from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse, UserUpdateRequest, ChangePasswordRequest
from app.models.user import User
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.utils.password import hash_password, verify_password
from app.dependencies.auth import get_current_user
from app.utils.password_validator import validate_password_strength

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_username = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
    )
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered."
        )
    
    password_validation = validate_password_strength(user.password)

    if password_validation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_validation
        )

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

@router.get("/allusers",response_model = list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    return users

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Validate Username
    # -----------------------------
    if user_update.username is not None:

        existing_username = (
            db.query(User)
            .filter(User.username == user_update.username)
            .first()
        )

        if (
            existing_username
            and existing_username.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

    # -----------------------------
    # Validate Email
    # -----------------------------
    if user_update.email is not None:

        existing_email = (
            db.query(User)
            .filter(User.email == user_update.email)
            .first()
        )

        if (
            existing_email
            and existing_email.id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # -----------------------------
    # Update only provided fields
    # -----------------------------
    if user_update.username is not None:
        current_user.username = user_update.username
        current_user.email = User.email

    if user_update.email is not None:
        current_user.username = User.username
        current_user.email = user_update.email

    # -----------------------------
    # Save Changes
    # -----------------------------
    db.commit()

    db.refresh(current_user)

    return current_user

@router.put("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_data.old_password,current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password."
        )
    
    password_validation = validate_password_strength(password_data.new_password)
    if password_validation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_validation
        )

    current_user.password_hash = hash_password(password_data.new_password)

    # Save
    db.commit()

    db.refresh(current_user)

    return {
        "message": "Password changed successfully."
    }