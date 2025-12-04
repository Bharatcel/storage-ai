# Architecture Summary

## What's Stored Where

### Backend Python File (`backend/app/questions_data.py`)
- **All Questions** - Stored as Python dictionaries
- Categories: General and Technical
- Each question has: id, text, type, category, order, and optional options
- Easy to modify without database changes

### Azure SQL Database
Only stores:

1. **Projects Table**
   - Basic project information (name, environment, business purpose, etc.)
   - Assessment ID is the project.id

2. **Responses Table**
   - Links to project via project_id
   - Stores question_id (string identifier like "general_q1")
   - Stores question_text (the full question for historical record)
   - Stores response_value (user's answer - either selected option or full text input)
   - Stores optional comments from user

## Data Flow

1. **Frontend loads** → Fetches questions from backend API (`GET /api/questions`)
2. **User fills basic info** → Stored in React state
3. **User answers questions** → Stored in React state with comments
4. **User submits** → Single API call (`POST /api/assessments/complete`)
   - Creates Project record
   - Creates Response records (one per question answered)
   - Each response includes the question text for future reference

## Benefits of This Architecture

✅ **Simple Database** - Only 2 tables instead of 3
✅ **Easy Question Management** - Edit Python file, restart server
✅ **Historical Accuracy** - Question text saved with each response
✅ **Flexible** - Can change questions without affecting existing data
✅ **Fast** - No database queries just to load questions

## How to Add Questions

Edit `backend/app/questions_data.py`:

```python
QUESTIONS = {
    "general": [
        {
            "id": "general_q5",  # Must be unique
            "text": "What is your question?",
            "type": "text_input",  # or "single_choice"
            "category": "general",
            "order": 5,
            # For single_choice, add options:
            # "options": ["Option 1", "Option 2"]
        }
    ]
}
```

Restart backend server - that's it!
