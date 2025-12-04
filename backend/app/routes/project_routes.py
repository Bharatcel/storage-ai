from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, Response
from app.schemas import (
    ProjectCreate, 
    ProjectResponse, 
    CompleteAssessment,
    ResponseResponse
)

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project with basic information"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return projects

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/assessments/complete", status_code=status.HTTP_201_CREATED)
def create_complete_assessment(assessment: CompleteAssessment, db: Session = Depends(get_db)):
    """Create a complete assessment with project and all responses"""
    # Create project
    db_project = Project(**assessment.project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Create responses
    db_responses = []
    for response_data in assessment.responses:
        db_response = Response(
            project_id=db_project.id,
            question_id=response_data.question_id,
            question_text=response_data.question_text,
            response_value=response_data.response_value,
            comments=response_data.comments
        )
        db.add(db_response)
        db_responses.append(db_response)
    
    db.commit()
    
    return {
        "message": "Assessment created successfully",
        "project_id": db_project.id,
        "responses_count": len(db_responses)
    }

@router.get("/projects/{project_id}/responses", response_model=List[ResponseResponse])
def get_project_responses(project_id: int, db: Session = Depends(get_db)):
    """Get all responses for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    responses = db.query(Response).filter(Response.project_id == project_id).order_by(Response.id).all()
    return responses
