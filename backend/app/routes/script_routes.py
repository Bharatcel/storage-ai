from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")

@router.get("/list")
async def list_scripts():
    """
    List all available scripts in the scripts directory.
    Returns list of script files with their names and sizes.
    """
    if not os.path.exists(SCRIPTS_DIR):
        return {"scripts": []}
    
    scripts = []
    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith(('.ps1', '.sh', '.py', '.bat', '.cmd')):
            file_path = os.path.join(SCRIPTS_DIR, filename)
            file_size = os.path.getsize(file_path)
            scripts.append({
                "filename": filename,
                "size": file_size
            })
    
    return {"scripts": scripts}

@router.get("/download/{filename}")
async def download_script(filename: str):
    """
    Download a specific script file by name.
    """
    # Sanitize filename to prevent directory traversal
    filename = os.path.basename(filename)
    
    script_path = os.path.join(SCRIPTS_DIR, filename)
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Script file '{filename}' not found")
    
    return FileResponse(
        path=script_path,
        filename=filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
