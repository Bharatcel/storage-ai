from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, ScriptResult
from app.blob_storage import BlobStorageService
import os

router = APIRouter()

# Allowed file extensions for script results
ALLOWED_EXTENSIONS = {'.csv', '.txt', '.json', '.xml', '.xlsx', '.xls', '.log', '.pdf', '.html'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file

@router.post("/upload-results/{project_id}")
async def upload_script_results(
    project_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple script result files for a project.
    Files are stored in Azure Blob Storage and metadata in database.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    blob_service = BlobStorageService()
    
    try:
        for file in files:
            # Validate file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of 50MB"
                )
            
            # Upload to blob storage with path: results/project_{id}/{filename}
            blob_path = f"results/project_{project_id}/{file.filename}"
            blob_url = await blob_service.upload_file(
                file_content=file_content,
                file_name=file.filename,
                blob_path=blob_path
            )
            
            # Save metadata to database
            script_result = ScriptResult(
                project_id=project_id,
                original_filename=file.filename,
                stored_filename=blob_path,
                blob_url=blob_url,
                file_size=file_size,
                file_type=file.content_type or file_ext
            )
            db.add(script_result)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file_size,
                "url": blob_url
            })
        
        db.commit()
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
            "project_id": project_id,
            "files": uploaded_files
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/results/{project_id}")
async def get_project_results(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all uploaded script result files for a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    results = db.query(ScriptResult).filter(
        ScriptResult.project_id == project_id
    ).order_by(ScriptResult.uploaded_at.desc()).all()
    
    return {
        "project_id": project_id,
        "project_name": project.project_name,
        "total_files": len(results),
        "files": [
            {
                "id": result.id,
                "filename": result.original_filename,
                "size": result.file_size,
                "type": result.file_type,
                "uploaded_at": result.uploaded_at.isoformat(),
                "url": result.blob_url
            }
            for result in results
        ]
    }


@router.delete("/results/{result_id}")
async def delete_script_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a script result file.
    """
    result = db.query(ScriptResult).filter(ScriptResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result file not found")
    
    try:
        # Delete from blob storage
        blob_service = BlobStorageService()
        await blob_service.delete_file(result.stored_filename)
        
        # Delete from database
        db.delete(result)
        db.commit()
        
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
