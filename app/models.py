from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Date
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base

class KYCStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class KYCApplication(Base):
    __tablename__ = "kyc_applications"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    id_number = Column(String(50), unique=True, index=True, nullable=False)
    country = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    selfie = Column(String(500), nullable=True) 
    id_doc = Column(String(500), nullable=True) 
    status = Column(Enum(KYCStatus), default=KYCStatus.PENDING, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())