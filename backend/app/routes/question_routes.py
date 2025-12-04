from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.questions_data import get_all_questions, get_questions_by_category, get_question_by_id

router = APIRouter()

@router.get("/questions")
def get_questions(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all questions or filter by category.
    
    Query Parameters:
    - category (optional): Filter by 'general' or 'technical'
    
    Returns all questions organized by category if no filter is provided.
    """
    if category:
        questions = get_questions_by_category(category)
        if not questions:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        return {"category": category, "questions": questions}
    
    return get_all_questions()

@router.get("/questions/{question_id}")
def get_question(question_id: str) -> Dict[str, Any]:
    """
    Get a specific question by ID.
    
    Path Parameters:
    - question_id: The unique identifier of the question (e.g., 'general_q1')
    """
    question = get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found")
    return question
