# Questions data stored in backend
# All assessment questions are defined here

# Import questions from questions.py
from app.questions import questions as IMPORTED_QUESTIONS

# Keep the same structure for backward compatibility
QUESTIONS = IMPORTED_QUESTIONS

def get_all_questions():
    """Get all questions from both categories"""
    return QUESTIONS

def get_questions_by_category(category: str):
    """Get questions filtered by category"""
    category_map = {
        "general": "General Questions",
        "technical": "Technical Questions"
    }
    
    mapped_category = category_map.get(category.lower(), category)
    return QUESTIONS.get(mapped_category, [])

def get_question_by_id(question_id: str | int):
    """Get a specific question by its ID"""
    # Convert to int if string
    if isinstance(question_id, str):
        try:
            question_id = int(question_id)
        except ValueError:
            return None
    
    # Search through all categories
    for category, question_list in QUESTIONS.items():
        for question in question_list:
            if question["id"] == question_id:
                return question
    return None
