from pydantic import BaseModel
from typing import Any, Dict, list

class QuestionRequest(BaseModel):
    attempt_id: int
    slot: int

class QuestionPayload(BaseModel):
    attempt_id: int
    slot: int 
    question_html: str
    meta: Dict[str, Any] = {}

class AnswerSubmission: 
    attempt_id: int
    slot: int 
    response: Dict[str, Any] 
    client_timestamp: float