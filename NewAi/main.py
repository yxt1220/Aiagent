# This is a sample Python script.
import json

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.upload import router as upload_router

app = FastAPI(title="Scaffolding Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段先这样，后面再收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(upload_router, prefix="/upload", tags=["upload"])

@app.get("/")
def root():
    return {"message": "Tutor API is running"}


@app.post("/reset")
def reset_session():
    from app.services.chat_service import agent
    from app.layers.file_ingestion.file_registry import file_registry
    agent.reset_episode()
    file_registry.clear_files("default-session")
    return {"message": "Session reset"}