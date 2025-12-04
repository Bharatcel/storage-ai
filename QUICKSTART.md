# Quick Start Guide

## Step 1: Setup Azure SQL Database

1. Go to Azure Portal
2. Create a new SQL Database
3. Note the connection details
4. Add your IP to firewall rules

## Step 2: Configure Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your database credentials
uvicorn main:app --reload
```

## Step 3: Start Frontend

```powershell
cd frontend
npm install
npm start
```

## Step 4: Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Default Questions Included

### General Information (4 questions)
1. Total storage capacity required (text input)
2. Expected data growth rate (single choice)
3. Primary purpose of storage (single choice)
4. Expected retention period (single choice)

### Technical Information (6 questions)
1. Performance requirements (IOPS) (text input)
2. Required availability SLA (single choice)
3. Storage tier needed (single choice)
4. Encryption requirements (single choice)
5. Network connectivity requirement (single choice)
6. Compliance requirements (text input)

You can customize these questions by editing `backend/app/questions_data.py` - no database changes needed!
