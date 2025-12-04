"""
Azure Blob Storage service for file uploads
"""
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.config import settings
from fastapi import HTTPException, UploadFile
import uuid
from typing import Optional
import os

# Allowed file extensions
ALLOWED_EXTENSIONS = {".png", ".txt", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class BlobStorageService:
    def __init__(self):
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("Azure Storage connection string not configured")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        
        # Ensure container exists
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                print(f"✅ Created blob container: {self.container_name}")
        except Exception as e:
            print(f"⚠️  Container check/creation warning: {e}")
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Validate file extension and size
        Raises HTTPException if validation fails
        """
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (if available)
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
                )
    
    async def upload_file(
        self, 
        file: UploadFile, 
        project_id: int, 
        question_id: str
    ) -> str:
        """
        Upload file to Azure Blob Storage
        Returns the blob URL
        """
        # Validate file first
        self.validate_file(file)
        
        # Generate unique blob name
        file_ext = os.path.splitext(file.filename)[1].lower()
        blob_name = f"project_{project_id}/question_{question_id}/{uuid.uuid4()}{file_ext}"
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Read file content
            file_content = await file.read()
            
            # Set content type based on extension
            content_type_map = {
                ".pdf": "application/pdf",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".txt": "text/plain"
            }
            content_type = content_type_map.get(file_ext, "application/octet-stream")
            
            # Upload to blob storage
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )
            
            # Return the blob URL
            return blob_client.url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def delete_file(self, blob_url: str) -> bool:
        """
        Delete a file from Azure Blob Storage
        Returns True if successful
        """
        try:
            # Extract blob name from URL
            blob_name = blob_url.split(f"{self.container_name}/")[-1]
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
            
        except Exception as e:
            print(f"Failed to delete blob: {e}")
            return False

# Create singleton instance
def get_blob_storage_service() -> Optional[BlobStorageService]:
    """Get blob storage service instance"""
    try:
        return BlobStorageService()
    except ValueError as e:
        print(f"⚠️  Blob storage not configured: {e}")
        return None
