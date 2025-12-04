from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Project(Base):
    __tablename__ = "tpsm_projects"
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    environment = Column(String(50), nullable=False)  # Development, QA, Production
    business_purpose = Column(Text, nullable=False)
    business_criticality = Column(String(100), nullable=False)  # Increased to 100 chars
    business_owners = Column(String(500), nullable=False)
    storage_owners = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    responses = relationship("Response", back_populates="project", cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "tpsm_responses"
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dbo.tpsm_projects.id"), nullable=False)
    question_id = Column(String(50), nullable=False)  # Question identifier from frontend
    question_text = Column(Text, nullable=False)  # Store the question text
    response_value = Column(Text, nullable=False)  # User's answer
    comments = Column(Text, nullable=True)  # Optional comments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="responses")
