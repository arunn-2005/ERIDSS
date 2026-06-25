from fastapi import FastAPI
from app.routes.test import router as test_router

app = FastAPI(
    title="Enterprise Risk Intelligence & Decision Support System",
    version="1.0.0"
)

app.include_router(test_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to ERIDSS API"
    }