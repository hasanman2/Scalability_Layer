from functools import lru_cache
from typing import Any, Dict

from app.adapter.moodle_adapter import MoodleAdapter


class ExamService:
    """
    Exam Delivery Service core logic.

    - Owns the tiny in-process cache.
    - Delegates all LMS-specific DB access to the adapter.
    """

    def __init__(self, adapter: MoodleAdapter) -> None:
        self._adapter = adapter

    @lru_cache(maxsize=10_000)
    def _get_question_cached(self, attempt_id: int, slot: int) -> Dict[str, Any]:
        """
        Tiny local cache.

        Key: (attempt_id, slot)
        Value: question payload as returned by the adapter.
        """
        # This always goes through the adapter (LMS-specific logic).
        return self._adapter.get_question_payload(attempt_id, slot)

    def get_question_payload(self, attempt_id: int, slot: int) -> Dict[str, Any]:
        """
        Public method used by the FastAPI route.

        For callers, this *is* the Exam Delivery Service:
        they ask for a question, and it is returned (possibly from cache).
        """
        return self._get_question_cached(attempt_id, slot)
