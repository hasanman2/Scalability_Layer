from fastapi import APIRouter, HTTPException
from app.models.exam_models import QuestionRequest, QuestionPayload, AnswerSubmission
from app.adapter.moodle_adapter import adapter
from app.services.exam_service import ExamService

router = APIRouter(tags=["exam"])

# Create one ExamService instance for this process.
exam_service = ExamService(adapter=adapter)


@router.post("/question", response_model=QuestionPayload)
async def get_question(req: QuestionRequest):
    payload = exam_service.get_question_payload(req.attempt_id, req.slot)
    return QuestionPayload(**payload)


@router.post("/answer")
async def submit_answer(req: AnswerSubmission):
    adapter.save_answer(
        attempt_id=req.attempt_id,
        slot=req.slot,
        response=req.response,
    )
    return {"status": "ok"}
