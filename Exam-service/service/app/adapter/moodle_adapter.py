from typing import Any, Dict
from sqlalchemy import create_engine, text
from . import db_session 
from app.config import settings

class MoodleAdapter:
    """
    Encapsulates all LMS-specific logic.
    Skeleton implementation with placeholder queries.
    """

    def __init__(self) -> None: 
        self.engine = create_engine(settings.lms_db_url, future = True)

    
    def get_question_payload(slef, attempt_id: int, slot: int) -> Dict[str, Any] :
        # TODO: replace with real Moodle queries/query_*
        # For now, just return a dummy payload
        return{
            attempt_id: attempt_id,
            slot: slot,
            "question_html": f"<p>Question {slot} for attempt {attempt_id} (dummy)</p>",
            "meta": {"max_mark": 1.0}, 
        }
    
    def save_answer(
            self, 
            attempt_id: int,
            slot: int,
            response: Dict[str, Any]
    ) -> None:
        # TODO: write to moodle DB tables
        # For now, this is just a stub
        # with self.engine.begin() as conn:
        #     conn.execute(text("..."), {...})
        pass

adapter = MoodleAdapter()