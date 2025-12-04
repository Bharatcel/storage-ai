# Assessment Application

A full-stack web application for storage assessment and migration planning with FastAPI backend and React frontend.

## Features

- ✅ Collect basic project information (name, environment, business purpose, criticality, owners)
- ✅ Multi-category questionnaire (General and Technical Information)
- ✅ Support for multiple question types (single choice, text input)
- ✅ Optional comments for all questions
- ✅ Questions stored in backend file (not in database)
- ✅ Responses saved to Azure SQL Database with question text
- ✅ RESTful API with FastAPI
- ✅ Modern React UI with step-by-step wizard
- ✅ Project information and user responses persisted in Azure SQL

## Project Structure

```
assessment-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models (Project, Response)
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── questions_data.py  # Questions stored in Python file
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── project_routes.py
│   │       └── question_routes.py
│   ├── main.py                # FastAPI application
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                   # React frontend
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   ├── AssessmentForm.js
    │   │   ├── BasicInfoForm.js
    │   │   ├── QuestionsForm.js
    │   │   └── *.css
    │   ├── services/
    │   │   └── api.js
    │   ├── App.js
    │   ├── index.js
    │   └── *.css
    ├── package.json
    └── .env
```

## Prerequisites

### Backend
- Python 3.8 or higher
- Azure SQL Database instance
- ODBC Driver 17 for SQL Server

### Frontend
- Node.js 16 or higher
- npm or yarn

## Setup Instructions

### 1. Azure SQL Database Setup

1. Create an Azure SQL Database instance
2. Note down the following details:
   - Server name (e.g., `your-server.database.windows.net`)
   - Database name
   - Username
   - Password
3. Configure firewall rules to allow your IP address
4. Ensure ODBC Driver 17 for SQL Server is installed on your machine

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env

# Edit .env file with your Azure SQL credentials
notepad .env
```

Update the `.env` file with your Azure SQL Database credentials:
```
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=your-server.database.windows.net
DB_DATABASE=assessment_db
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_PORT=1433
ENVIRONMENT=development
```

Start the backend server:
```powershell
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 3. Frontend Setup

```powershell
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The React app will open at `http://localhost:3000`

## Usage

1. **Fill Basic Information**
   - Enter project name
   - Select environment (Development, QA, Production)
   - Describe business purpose/storage migration objective
   - Select business criticality (1, 2, or 3)
   - Enter business owner(s) and storage owner(s)
   - Click "Next"

2. **Complete Assessment Questions**
   - Switch between "General Information" and "Technical Information" tabs
   - Answer all questions (select options or enter text)
   - Optionally add comments for any question
   - Click "Submit Assessment"

3. **View Confirmation**
   - See success message
   - Start a new assessment if needed

## API Endpoints

### Projects
- `POST /api/projects` - Create a new project
- `GET /api/projects` - Get all projects
- `GET /api/projects/{id}` - Get a specific project
- `POST /api/projects/{id}/responses` - Add responses to a project
- `GET /api/projects/{id}/responses` - Get all responses for a project

### Questions
- `GET /api/questions` - Get all questions (organized by category)
- `GET /api/questions?category={category}` - Get questions by category (general/technical)
- `GET /api/questions/{question_id}` - Get a specific question by ID

### Assessments
- `POST /api/assessments/complete` - Submit complete assessment (project + responses)

## Database Schema

### Projects Table
- id (Primary Key)
- project_name
- environment
- business_purpose
- business_criticality
- business_owners
- storage_owners
- created_at
- updated_at

### Responses Table
- id (Primary Key)
- project_id (Foreign Key)
- question_id (String - question identifier like "general_q1")
- question_text (Text - the full question)
- response_value (Text - user's answer)
- comments (Text - optional comments)
- created_at
- updated_at

**Note:** Questions are stored in `backend/app/questions_data.py` as Python data structures, not in the database.

## Customization

### Adding or Modifying Questions

Questions are stored in `backend/app/questions_data.py`. To add or modify questions:

1. Open `backend/app/questions_data.py`
2. Edit the `QUESTIONS` dictionary
3. Add your question following this format:

```python
{
    "id": "general_q5",  # Unique identifier
    "text": "Your question here?",
    "type": "single_choice",  # or "text_input"
    "category": "general",  # or "technical"
    "order": 5,
    "options": [  # Only for single_choice type
        "Option 1",
        "Option 2",
        "Option 3"
    ]
}
```

No database changes required - just restart the backend server!

### Modifying Business Criticality Levels

Edit `frontend/src/components/BasicInfoForm.js` to change the criticality options.

## Troubleshooting

### Backend Issues

**Database Connection Error**
- Verify Azure SQL credentials in `.env`
- Check firewall rules allow your IP
- Ensure ODBC Driver 17 is installed

**Module Import Errors**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**API Connection Error**
- Verify backend is running on port 8000
- Check `.env` file has correct API URL
- Check browser console for CORS errors

**npm Install Errors**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then reinstall

## Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **pyodbc** - Azure SQL Database driver
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **CSS3** - Styling

## License

This project is created for assessment and migration planning purposes.

## Support

For issues or questions, please contact the development team.
