import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image

UPLOAD_DIR = "media"
SELFIE_DIR = os.path.join(UPLOAD_DIR, "selfies")
ID_DOC_DIR = os.path.join(UPLOAD_DIR, "id_docs")

# Create directories if they don't exist
os.makedirs(SELFIE_DIR, exist_ok=True)
os.makedirs(ID_DOC_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file(file: UploadFile) -> bool:
    if not file.filename:
        return False
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return True

def save_upload_file(file: UploadFile, directory: str) -> str:
    validate_file(file)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(directory, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        buffer.write(content)
    
    # Validate image files
    if file_ext in {".jpg", ".jpeg", ".png"}:
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid image file")
    
    return file_path

def save_selfie(file: UploadFile) -> Optional[str]:
    if not file or not file.filename:
        return None
    return save_upload_file(file, SELFIE_DIR)

def save_id_document(file: UploadFile) -> Optional[str]:
    if not file or not file.filename:
        return None
    return save_upload_file(file, ID_DOC_DIR)