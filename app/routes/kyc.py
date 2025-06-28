from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
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
    """
    Submit a new KYC application with personal details and identity documents
    
    Args:
        full_name: Applicant's full legal name
        dob: Date of birth in YYYY-MM-DD format
        id_number: Government-issued ID number
        country: Country of residence
        address: Full residential address
        selfie: Selfie image file
        id_doc: Scanned ID document file
    """
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
    """
    Check the status of a KYC application by ID number
    
    Args:
        id_number: The ID number used in the KYC application
    """
    kyc_application = crud.get_kyc_by_id_number(db, id_number)
    if not kyc_application:
        raise HTTPException(status_code=404, detail="KYC application not found")
    
    return schemas.KYCStatusResponse(
        id_number=kyc_application.id_number,
        status=kyc_application.status,
        rejection_reason=kyc_application.rejection_reason,
        created_at=kyc_application.created_at
    )

@router.get("/applications", response_model=List[schemas.KYCApplicationResponse])
def get_all_kyc_applications(
    status: Optional[models.KYCStatus] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Fetch all KYC applications with optional filtering by status and pagination
    
    Args:
        status: Filter by application status (PENDING, APPROVED, REJECTED)
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    """
    applications = crud.get_all_kyc_applications(db, status=status, skip=skip, limit=limit)
    return applications

@router.get("/application/{application_id}", response_model=schemas.KYCApplicationResponse)
def get_kyc_application_by_id(application_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single KYC application by its unique ID
    
    Args:
        application_id: The database ID of the KYC application
    """
    application = crud.get_kyc_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=404, 
            detail="KYC application not found"
        )
    return application

@router.patch("/admin/review/{application_id}", response_model=schemas.KYCApplicationResponse)
def review_kyc_application(
    application_id: int,
    review_data: schemas.KYCReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to approve or reject a KYC application
    
    Args:
        application_id: The ID of the KYC application to review
        review_data: Contains action (APPROVED/REJECTED) and optional rejection_reason
    """
    # Validate that application exists
    existing_application = crud.get_kyc_by_id(db, application_id)
    if not existing_application:
        raise HTTPException(
            status_code=404,
            detail="KYC application not found"
        )
    
    # Validate that application is in pending status
    if existing_application.status != models.KYCStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review application with status: {existing_application.status.value}"
        )
    
    # Validate rejection reason if rejecting
    if review_data.action == models.KYCStatus.REJECTED and not review_data.rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required when rejecting an application"
        )
    
    # Validate that rejection reason is not provided when approving
    if review_data.action == models.KYCStatus.APPROVED and review_data.rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason should not be provided when approving an application"
        )
    
    # Update the application status
    updated_application = crud.update_kyc_status(
        db=db,
        kyc_id=application_id,
        status=review_data.action,
        rejection_reason=review_data.rejection_reason if review_data.action == models.KYCStatus.REJECTED else None
    )
    
    if not updated_application:
        raise HTTPException(
            status_code=500,
            detail="Failed to update KYC application"
        )
    
    return updated_application

@router.get("/admin/pending", response_model=List[schemas.KYCApplicationResponse])
def get_pending_kyc_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to get all pending KYC applications for review
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    """
    return crud.get_all_kyc_applications(
        db=db, 
        status=models.KYCStatus.PENDING, 
        skip=skip, 
        limit=limit
    )

@router.get("/admin/approved", response_model=List[schemas.KYCApplicationResponse])
def get_approved_kyc_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to get all approved KYC applications
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    """
    return crud.get_all_kyc_applications(
        db=db, 
        status=models.KYCStatus.APPROVED, 
        skip=skip, 
        limit=limit
    )

@router.get("/admin/rejected", response_model=List[schemas.KYCApplicationResponse])
def get_rejected_kyc_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to get all rejected KYC applications
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    """
    return crud.get_all_kyc_applications(
        db=db, 
        status=models.KYCStatus.REJECTED, 
        skip=skip, 
        limit=limit
    )

@router.get("/admin/stats", response_model=schemas.KYCStatsResponse)
def get_kyc_statistics(db: Session = Depends(get_db)):
    """
    Admin endpoint to get KYC application statistics
    
    Returns:
        Object containing counts of applications by status and other metrics
    """
    return crud.get_kyc_stats(db)