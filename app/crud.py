from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from . import models, schemas

def create_kyc_application(db: Session, kyc_data: schemas.KYCSubmissionRequest, 
                          selfie_path: Optional[str] = None, 
                          id_doc_path: Optional[str] = None) -> models.KYCApplication:
    db_kyc = models.KYCApplication(
        full_name=kyc_data.full_name,
        dob=kyc_data.dob,
        id_number=kyc_data.id_number,
        country=kyc_data.country,
        address=kyc_data.address,
        selfie=selfie_path,
        id_doc=id_doc_path
    )
    db.add(db_kyc)
    db.commit()
    db.refresh(db_kyc)
    return db_kyc

def get_kyc_by_id_number(db: Session, id_number: str) -> Optional[models.KYCApplication]:
    return db.query(models.KYCApplication).filter(
        models.KYCApplication.id_number == id_number
    ).first()

def get_kyc_by_id(db: Session, kyc_id: int) -> Optional[models.KYCApplication]:
    return db.query(models.KYCApplication).filter(
        models.KYCApplication.id == kyc_id
    ).first()

def get_all_kyc_applications(db: Session, status: Optional[models.KYCStatus] = None, 
                           skip: int = 0, limit: int = 100) -> List[models.KYCApplication]:
    query = db.query(models.KYCApplication)
    if status:
        query = query.filter(models.KYCApplication.status == status)
    return query.offset(skip).limit(limit).all()

def update_kyc_status(db: Session, kyc_id: int, status: models.KYCStatus, 
                     rejection_reason: Optional[str] = None) -> Optional[models.KYCApplication]:
    db_kyc = db.query(models.KYCApplication).filter(
        models.KYCApplication.id == kyc_id
    ).first()
    if db_kyc:
        db_kyc.status = status
        
        # Handle rejection_reason based on status
        if status == models.KYCStatus.REJECTED:
            # For rejected status, rejection_reason should be provided
            db_kyc.rejection_reason = rejection_reason
        else:
            # For APPROVED or PENDING status, clear rejection_reason
            db_kyc.rejection_reason = None
            
        db.commit()
        db.refresh(db_kyc)
    return db_kyc

def get_kyc_stats(db: Session) -> dict:
    total = db.query(models.KYCApplication).count()
    approved = db.query(models.KYCApplication).filter(
        models.KYCApplication.status == models.KYCStatus.APPROVED
    ).count()
    rejected = db.query(models.KYCApplication).filter(
        models.KYCApplication.status == models.KYCStatus.REJECTED
    ).count()
    pending = db.query(models.KYCApplication).filter(
        models.KYCApplication.status == models.KYCStatus.PENDING
    ).count()
    
    return {
        "total_submissions": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }