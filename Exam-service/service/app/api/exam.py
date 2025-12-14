from fastapi import APIRouter, HTTPException
from app.models.exam_models import QuestionRequest, QuestionPayload, AnswerSubmission
from app.adapter.moodle_adapter import adapter

router = APIRouter(prefix="/api/exam/", tags=["exam"])


@router.post("/questin", response_model=QuestionPayload)
async def get_question(req: QuestionRequest):
    # later: validate token, attempt ownership, etc.
    payload = adapter.get_question_payload(req.attempt_id, req.slot)
    return QuestionPayload(**payload)

@router.post("/answer")
async def submit_answer(req: AnswerSubmission):
    # later: validation, logging, etc.
    adapter.save_answer(
        attempt_id = req.attempt_id,
        slot = req.slot,
        response = req.response
    )
    return {"status" : "ok"}
