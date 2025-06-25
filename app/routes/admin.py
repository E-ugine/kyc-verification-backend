from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from .. import crud, schemas, models
from ..database import get_db
from ..auth import authenticate_admin, create_access_token, get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/login", response_model=schemas.Token)
async def admin_login(username: str, password: str):
    if not authenticate_admin(username, password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/all", response_model=List[schemas.KYCApplicationResponse])
def get_all_applications(
    status: Optional[models.KYCStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    applications = crud.get_all_kyc_applications(
        db=db, status=status, skip=skip, limit=limit
    )
    return applications

@router.get("/{kyc_id}", response_model=schemas.KYCApplicationResponse)
def get_application_details(
    kyc_id: int,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    application = crud.get_kyc_by_id(db, kyc_id)
    if not application:
        raise HTTPException(status_code=404, detail="KYC application not found")
    return application

@router.put("/verify/{kyc_id}", response_model=schemas.KYCApplicationResponse)
def verify_application(
    kyc_id: int,
    verification_data: schemas.KYCVerificationRequest,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    # Validate rejection reason
    if verification_data.status == models.KYCStatus.REJECTED and not verification_data.rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required when rejecting an application"
        )
    
    updated_application = crud.update_kyc_status(
        db=db,
        kyc_id=kyc_id,
        status=verification_data.status,
        rejection_reason=verification_data.rejection_reason
    )
    
    if not updated_application:
        raise HTTPException(status_code=404, detail="KYC application not found")
    
    return updated_application

@router.get("/stats/dashboard", response_model=schemas.KYCStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    stats = crud.get_kyc_stats(db)
    return stats