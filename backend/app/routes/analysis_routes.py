"""
Analysis API Routes
Endpoints for triggering and retrieving storage analysis
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List
import json
from app.database import get_db
from app.models import (
    Project, AnalysisSummary, AnalysisResults
)
from app.services.storage_analyzer import StorageAnalyzer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/trigger/{project_id}")
async def trigger_analysis(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger storage analysis for a project
    Runs asynchronously in background
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if already processing
    summary = db.query(AnalysisSummary).filter(
        AnalysisSummary.project_id == project_id
    ).first()
    
    if summary and summary.analysis_status == "processing":
        raise HTTPException(
            status_code=409, 
            detail="Analysis already in progress"
        )
    
    # Start analysis in background with proper async handling
    async def run_analysis():
        from app.database import SessionLocal
        db_session = SessionLocal()
        try:
            analyzer = StorageAnalyzer(db_session)
            await analyzer.analyze_project(project_id)
        except Exception as e:
            logger.error(f"Background analysis failed: {str(e)}")
        finally:
            db_session.close()
    
    background_tasks.add_task(run_analysis)
    
    return {
        "message": "Analysis started",
        "project_id": project_id,
        "status": "processing"
    }


@router.get("/status/{project_id}")
def get_analysis_status(project_id: int, db: Session = Depends(get_db)):
    """
    Check analysis status for a project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    summary = db.query(AnalysisSummary).filter(
        AnalysisSummary.project_id == project_id
    ).first()
    
    if not summary:
        return {
            "project_id": project_id,
            "status": "not_started",
            "message": "No analysis has been run yet"
        }
    
    return {
        "project_id": project_id,
        "status": summary.analysis_status,
        "total_files": summary.total_files,
        "total_size_gb": float(summary.total_size_gb) if summary.total_size_gb else 0,
        "analyzed_files_count": summary.analyzed_files_count,
        "started_at": summary.started_at.isoformat() if summary.started_at else None,
        "completed_at": summary.completed_at.isoformat() if summary.completed_at else None,
        "error_message": summary.error_message
    }


@router.get("/results/{project_id}")
def get_analysis_results(project_id: int, db: Session = Depends(get_db)):
    """
    Get complete analysis results for a project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    summary = db.query(AnalysisSummary).filter(
        AnalysisSummary.project_id == project_id
    ).first()
    
    if not summary or summary.analysis_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Analysis not completed yet. Please check status first."
        )
    
    # Fetch analysis results (stored as JSON)
    results = db.query(AnalysisResults).filter(
        AnalysisResults.project_id == project_id
    ).first()
    
    if not results:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    return {
        "project_id": project_id,
        "summary": {
            "total_files": summary.total_files,
            "total_size_gb": float(summary.total_size_gb),
            "analyzed_files_count": summary.analyzed_files_count,
            "completed_at": summary.completed_at.isoformat()
        },
        "age_distribution": json.loads(results.age_distribution) if results.age_distribution else [],
        "file_types": json.loads(results.file_types) if results.file_types else [],
        "storage_tiers": json.loads(results.storage_tiers) if results.storage_tiers else [],
        "cost_analysis": json.loads(results.cost_analysis) if results.cost_analysis else None,
        "growth_projection": json.loads(results.growth_projection) if results.growth_projection else None
    }


@router.delete("/results/{project_id}")
def delete_analysis_results(project_id: int, db: Session = Depends(get_db)):
    """
    Delete analysis results for a project (to re-run analysis)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete will cascade to all analysis tables
    deleted = db.query(AnalysisSummary).filter(
        AnalysisSummary.project_id == project_id
    ).delete()
    
    db.commit()
    
    return {
        "message": "Analysis results deleted successfully",
        "project_id": project_id
    }
