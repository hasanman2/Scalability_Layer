# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import exam as exam_api
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Moodle origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exam_api.router, prefix="/api/exam")
app.mount("/static", StaticFiles(directory="static"), name="static")
