from pydantic import BaseModel
from typing import Optional, Any, Dict


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = ""


class ChatResponse(BaseModel):
    response: str
    diagnosis: Optional[Dict[str, Any]] = None
    routing: Optional[Dict[str, Any]] = None
    retrieval: Optional[Dict[str, Any]] = None
    pedagogical_control: Optional[Dict[str, Any]] = None
    episode_state: Optional[Dict[str, Any]] = None