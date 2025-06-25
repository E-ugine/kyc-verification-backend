from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, schemas, models
from ..database import get_db
from ..utils.file_upload import save_selfie, save_id_document

router = APIRouter(prefix="/kyc", tags=["KYC"])

@router.post("/submit", response_model=schemas.KYCApplicationResponse)
async def submit_kyc_application(
    full_name: str = Form(...),
    dob: str = Form(...),
    id_number: str = Form(...),
    country: str = Form(...),
    address: str = Form(...),
    selfie: Optional[UploadFile] = File(None),
    id_doc: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Check if ID number already exists
    existing_kyc = crud.get_kyc_by_id_number(db, id_number)
    if existing_kyc:
        raise HTTPException(
            status_code=400,
            detail="KYC application with this ID number already exists"
        )
    
    # Validate and create request object
    try:
        kyc_request = schemas.KYCSubmissionRequest(
            full_name=full_name,
            dob=dob,
            id_number=id_number,
            country=country,
            address=address
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Handle file uploads
    selfie_path = None
    id_doc_path = None
    
    try:
        if selfie:
            selfie_path = save_selfie(selfie)
        if id_doc:
            id_doc_path = save_id_document(id_doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload error: {str(e)}")
    
    # Create KYC application
    kyc_application = crud.create_kyc_application(
        db=db,
        kyc_data=kyc_request,
        selfie_path=selfie_path,
        id_doc_path=id_doc_path
    )
    
    return kyc_application

@router.get("/status/{id_number}", response_model=schemas.KYCStatusResponse)
def get_kyc_status(id_number: str, db: Session = Depends(get_db)):
    kyc_application = crud.get_kyc_by_id_number(db, id_number)
    if not kyc_application:
        raise HTTPException(status_code=404, detail="KYC application not found")
    
    return schemas.KYCStatusResponse(
        id_number=kyc_application.id_number,
        status=kyc_application.status,
        rejection_reason=kyc_application.rejection_reason,
        created_at=kyc_application.created_at
    )