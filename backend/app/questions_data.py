# Questions data stored in backend
# All assessment questions are defined here

# Import questions from questions.py
from app.questions import questions as IMPORTED_QUESTIONS

# Keep the same structure for backward compatibility
QUESTIONS = IMPORTED_QUESTIONS

def transform_question(q):
    """Transform question format for frontend compatibility"""
    # Keywords that indicate an exclusive option
    exclusive_keywords = [
        "none of the above",
        "not applicable",
        "not sure",
        "no",
        "other than above"
    ]
    
    # Transform options and mark exclusive ones
    transformed_options = []
    for opt in q.get("options", []):
        option_text = opt["text"]
        is_exclusive = any(keyword in option_text.lower() for keyword in exclusive_keywords)
        
        transformed_options.append({
            "text": option_text,
            "weight": opt.get("weight"),
            "is_exclusive": is_exclusive
        })
    
    return {
        "id": str(q["id"]),  # Convert to string for frontend
        "text": q["question"],  # Map 'question' to 'text'
        "description": q.get("description", ""),
        "type": q["type"],
        "options": transformed_options,
        "other_option": q.get("other_option"),
        "file_upload": q.get("file_upload", False)
    }

def get_all_questions():
    """Get all questions from both categories"""
    general = [transform_question(q) for q in QUESTIONS.get("General Questions", [])]
    technical = [transform_question(q) for q in QUESTIONS.get("Technical Questions", [])]
    
    return {
        "general": general,
        "technical": technical
    }

def get_questions_by_category(category: str):
    """Get questions filtered by category"""
    category_map = {
        "general": "General Questions",
        "technical": "Technical Questions"
    }
    
    mapped_category = category_map.get(category.lower(), category)
    questions = QUESTIONS.get(mapped_category, [])
    
    # Transform questions for frontend
    return [transform_question(q) for q in questions]

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
                return transform_question(question)
    return None
