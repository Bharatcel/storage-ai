from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, Numeric
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
    script_results = relationship("ScriptResult", back_populates="project", cascade="all, delete-orphan")
    analysis_summary = relationship("AnalysisSummary", back_populates="project", uselist=False, cascade="all, delete-orphan")

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

class ScriptResult(Base):
    __tablename__ = "tpsm_script_results"
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dbo.tpsm_projects.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)  # Original name of uploaded file
    stored_filename = Column(String(500), nullable=False)  # Name in blob storage
    blob_url = Column(String(1000), nullable=False)  # Full URL to blob storage
    file_size = Column(Integer, nullable=False)  # File size in bytes
    file_type = Column(String(100), nullable=True)  # MIME type or extension
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="script_results")

class FileMetadata(Base):
    __tablename__ = "tpsm_file_metadata"
    __table_args__ = {'schema': 'dbo'}

    id = Column(BigInteger, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dbo.tpsm_projects.id"), nullable=False)
    result_file_id = Column(Integer, ForeignKey("dbo.tpsm_script_results.id"), nullable=False)
    server_name = Column(String(255), nullable=True)
    drive_letter = Column(String(10), nullable=True)
    directory_path = Column(String(4000), nullable=True)
    file_name = Column(String(500), nullable=True)
    extension = Column(String(50), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    size_mb = Column(Numeric(18, 2), nullable=True)
    size_gb = Column(Numeric(18, 2), nullable=True)
    created_date = Column(DateTime(timezone=True), nullable=True)
    modified_date = Column(DateTime(timezone=True), nullable=True)
    accessed_date = Column(DateTime(timezone=True), nullable=True)
    file_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisResults(Base):
    __tablename__ = "tpsm_analysis_results"
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dbo.tpsm_projects.id"), nullable=False, unique=True)
    age_distribution = Column(String, nullable=True)  # JSON
    file_types = Column(String, nullable=True)  # JSON
    storage_tiers = Column(String, nullable=True)  # JSON
    cost_analysis = Column(String, nullable=True)  # JSON
    growth_projection = Column(String, nullable=True)  # JSON
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisSummary(Base):
    __tablename__ = "tpsm_analysis_summary"
    __table_args__ = {'schema': 'dbo'}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("dbo.tpsm_projects.id"), nullable=False, unique=True)
    total_files = Column(BigInteger, nullable=False)
    total_size_gb = Column(Numeric(18, 2), nullable=False)
    analyzed_files_count = Column(Integer, nullable=False)
    analysis_status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="analysis_summary")
