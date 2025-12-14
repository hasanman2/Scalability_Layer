from fastapi import FastAPI
from app.config import settings
from app.api import exam as exam_api

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {"status" : "ok"}


app.include_router(exam_api.router)