from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.blob_storage import get_blob_storage_service, BlobStorageService
from typing import Optional

router = APIRouter()

@router.post("/upload")
async def upload_file(
    project_id: int = Form(...),
    question_id: str = Form(...),
    file: UploadFile = File(...),
    blob_service: Optional[BlobStorageService] = Depends(get_blob_storage_service),
    db: Session = Depends(get_db)
):
    """
    Upload a file to Azure Blob Storage
    
    - **project_id**: The project ID this file belongs to
    - **question_id**: The question ID this file is answering
    - **file**: The file to upload (allowed: .png, .txt, .jpg, .jpeg, .pdf)
    
    Returns the blob URL to store in the response
    """
    if not blob_service:
        raise HTTPException(
            status_code=503,
            detail="Blob storage service not configured. Please set AZURE_STORAGE_CONNECTION_STRING in .env"
        )
    
    try:
        # Upload file and get URL
        blob_url = await blob_service.upload_file(file, project_id, question_id)
        
        return {
            "success": True,
            "blob_url": blob_url,
            "filename": file.filename,
            "project_id": project_id,
            "question_id": question_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.delete("/upload")
async def delete_file(
    blob_url: str,
    blob_service: Optional[BlobStorageService] = Depends(get_blob_storage_service)
):
    """
    Delete a file from Azure Blob Storage
    
    - **blob_url**: The full blob URL to delete
    """
    if not blob_service:
        raise HTTPException(
            status_code=503,
            detail="Blob storage service not configured"
        )
    
    success = await blob_service.delete_file(blob_url)
    
    if success:
        return {"success": True, "message": "File deleted successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete file"
        )
