from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Project Schemas
class ProjectBase(BaseModel):
    project_name: str
    environment: str  # Development, QA, Production
    business_purpose: str
    business_criticality: str  # 1, 2, 3
    business_owners: str
    storage_owners: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response Schemas
class ResponseBase(BaseModel):
    question_id: str  # Question identifier (e.g., "general_q1", "technical_q2")
    question_text: str  # The full question text
    response_value: str  # User's answer
    comments: Optional[str] = None

class ResponseCreate(ResponseBase):
    pass

class ResponseWithProject(ResponseBase):
    project_id: int

class ResponseResponse(ResponseWithProject):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Complete Assessment Schema
class CompleteAssessment(BaseModel):
    project: ProjectCreate
    responses: List[ResponseCreate]
