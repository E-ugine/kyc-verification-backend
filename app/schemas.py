from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from .models import KYCStatus

class KYCSubmissionRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    dob: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    id_number: str = Field(..., min_length=5, max_length=50)
    country: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=10, max_length=500)

class KYCApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: str
    dob: str
    id_number: str
    country: str
    address: str
    selfie: Optional[str] = None
    id_doc: Optional[str] = None
    status: KYCStatus
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class KYCStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_number: str
    status: KYCStatus
    rejection_reason: Optional[str] = None
    created_at: datetime
    
class AdminLoginRequest(BaseModel):
    username: str
    password: str    

class KYCVerificationRequest(BaseModel):
    status: KYCStatus
    rejection_reason: Optional[str] = None

class KYCStatsResponse(BaseModel):
    total_submissions: int
    approved: int
    rejected: int
    pending: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
class KYCReviewRequest(BaseModel):
    action: KYCStatus
    rejection_reason: Optional[str] = None
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        # Ensure only APPROVED or REJECTED are allowed for review actions
        if isinstance(v, str):
            try:
                enum_value = KYCStatus(v)
            except ValueError:
                raise ValueError("Action must be either APPROVED or REJECTED")
        else:
            enum_value = v
            
        if enum_value not in [KYCStatus.APPROVED, KYCStatus.REJECTED]:
            raise ValueError("Action must be either APPROVED or REJECTED")
        
        return enum_value
    
    model_config = ConfigDict(use_enum_values=True)