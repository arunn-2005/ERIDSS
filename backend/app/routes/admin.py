from fastapi import APIRouter, Depends, status, HTTPException, Query
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.dependencies.auth import get_current_admin
from app.schemas.user import UserResponse, UserRoleUpdate, DashboardResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    users = db.query(User).all()

    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user

@router.put("/users/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if current_admin.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role."
        )

    if user.role == role_data.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is already a {role_data.role}."
        )

    user.role = role_data.role

    db.commit()

    db.refresh(user)

    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if current_admin.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account."
        )

    if user.role == "Admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another administrator cannot be deleted."
        )

    db.delete(user)

    db.commit()

    return {
        "message": "User deleted successfully."
    }

@router.get("/dashboard/total-users")
def get_total_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()

    return {
        "total_users": total_users
    }

@router.get("/dashboard/total-admins")
def get_total_admins(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    total_admins = db.query(User).filter(User.role == "Admin").count()

    return {
        "total_admins": total_admins
    }

@router.get("/dashboard/total-normal-users")
def get_total_normal_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    total_normal_users = (
        db.query(User)
        .filter(User.role == "User")
        .count()
    )

    return {
        "total_normal_users": total_normal_users
    }

@router.get("/dashboard/recent-users", response_model=list[UserResponse])
def get_recent_users(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )

    return recent_users

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    total_users = db.query(User).count()

    total_admins = (
        db.query(User)
        .filter(User.role == "Admin")
        .count()
    )

    total_normal_users = (
        db.query(User)
        .filter(User.role == "User")
        .count()
    )

    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_normal_users": total_normal_users,
        "recent_users": recent_users
    }