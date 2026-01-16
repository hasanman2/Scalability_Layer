from pydantic import BaseModel
from typing import Any, Dict, Optional

class QuestionRequest(BaseModel):
    attempt_id: int
    slot: int

class QuestionPayload(BaseModel):
    attempt_id: int
    slot: int 
    question_html: str
    meta: Optional[Dict[str, Any]] | None = None

class AnswerSubmission(BaseModel): 
    attempt_id: int
    slot: int 
    response: Dict[str, Any] 
    client_timestamp: Optional[float] | None = None