from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from services.adaptive_learning_service import (
    generate_quiz,
    submit_quiz,
    get_quiz_by_id,
    get_quiz_attempts
)

router = APIRouter(prefix="/quiz", tags=["Quiz"])


class QuizGenerateRequest(BaseModel):
    topic: Optional[str] = None
    num_questions: int = Field(default=3, ge=1, le=10)
    student_id: str = "student_1"


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str]  # e.g. {"1": "B", "2": "C"}
    student_id: str = "student_1"


@router.post("/generate")
def api_generate_quiz(req: QuizGenerateRequest):
    """
    Generates a targeted engineering quiz based on course notes or weak topics.
    """
    try:
        quiz = generate_quiz(
            topic=req.topic,
            num_questions=req.num_questions,
            student_id=req.student_id
        )
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")


@router.post("/submit")
def api_submit_quiz(req: QuizSubmitRequest):
    """
    Evaluates quiz answers, provides misconception analysis, updates stored mastery in SQLite.
    """
    try:
        result = submit_quiz(
            quiz_id=req.quiz_id,
            student_answers=req.answers,
            student_id=req.student_id
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/history")
def api_quiz_history(student_id: str = "student_1", limit: int = 10):
    """
    Returns student's past quiz attempts and scores.
    """
    attempts = get_quiz_attempts(student_id=student_id, limit=limit)
    return {
        "student_id": student_id,
        "total_attempts": len(attempts),
        "attempts": attempts
    }


@router.get("/{quiz_id}")
def api_get_quiz(quiz_id: str):
    """
    Retrieves existing quiz by ID.
    """
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return quiz
