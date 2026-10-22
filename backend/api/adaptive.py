from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.adaptive_learning_service import (
    get_learning_progress,
    recommend_next_topic,
    create_study_plan,
    get_latest_study_plan
)

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])


class StudyPlanRequest(BaseModel):
    goal: str = Field(..., description="Target exam or learning goal")
    hours_available: float = Field(default=6.0, ge=1.0, le=40.0)
    student_id: str = "student_1"


@router.get("/progress")
def api_progress(student_id: str = "student_1"):
    """
    Returns actual calculated learning progress, topic mastery scores, and weak topics.
    Zero fabricated metrics.
    """
    return get_learning_progress(student_id=student_id)


@router.get("/recommend")
def api_recommend_topic(student_id: str = "student_1"):
    """
    Analyzes stored mastery, detects gaps and prerequisites, and provides
    the recommended next topic with reasons and remediation steps.
    """
    return recommend_next_topic(student_id=student_id)


@router.post("/study-plan")
def api_create_study_plan(req: StudyPlanRequest):
    """
    Generates a personalized study schedule allocating hours to weak topics first.
    """
    return create_study_plan(
        goal=req.goal,
        hours_available=req.hours_available,
        student_id=req.student_id
    )


@router.get("/study-plan")
def api_get_latest_plan(student_id: str = "student_1"):
    """
    Retrieves the most recent study plan for the student.
    """
    plan = get_latest_study_plan(student_id=student_id)
    if not plan:
        # Generate default starter plan
        return create_study_plan(
            goal="Comprehensive Core Engineering Exam Preparation",
            hours_available=6.0,
            student_id=student_id
        )
    return plan
