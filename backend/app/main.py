from fastapi import FastAPI
from app.routes.test import router as test_router
from app.routes.users import router as users_router
from app.routes.auth import router as auth_router
from app.database.database import Base, engine
from app import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise Risk Intelligence & Decision Support System",
    version="1.0.0"
)

app.include_router(test_router)
app.include_router(users_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to ERIDSS API"
    }

