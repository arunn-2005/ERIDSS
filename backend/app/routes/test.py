from fastapi import APIRouter, Depends
from app.models.user import User
from app.dependencies.auth import get_current_admin

router = APIRouter()

@router.get("/test")
def test():
    return {"message": "Test route is working!"}

@router.get("/test-admin")
def test_admin(current_admin: User = Depends(get_current_admin)):
    return {
        "message": "Welcome Admin!",
        "username": current_admin.username
    }