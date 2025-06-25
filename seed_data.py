from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
import random

# Create tables
models.Base.metadata.create_all(bind=engine)

fake = Faker()

def create_fake_kyc_applications(db: Session, count: int = 50):
    statuses = [models.KYCStatus.PENDING, models.KYCStatus.APPROVED, models.KYCStatus.REJECTED]
    
    for _ in range(count):
        status = random.choice(statuses)
        rejection_reason = None
        
        if status == models.KYCStatus.REJECTED:
            rejection_reasons = [
                "Invalid document provided",
                "Photo quality too poor",
                "Information mismatch",
                "Suspected fraudulent document",
                "Incomplete application"
            ]
            rejection_reason = random.choice(rejection_reasons)
        
        kyc_app = models.KYCApplication(
            full_name=fake.name(),
            dob=fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d"),
            id_number=fake.unique.random_number(digits=10, fix_len=True),
            country=fake.country(),
            address=fake.address().replace('\n', ', '),
            selfie=f"media/selfies/fake_selfie_{fake.uuid4()}.jpg",
            id_doc=f"media/id_docs/fake_id_{fake.uuid4()}.jpg",
            status=status,
            rejection_reason=rejection_reason
        )
        
        db.add(kyc_app)
    
    db.commit()
    print(f"Created {count} fake KYC applications")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_fake_kyc_applications(db, 50)
    finally:
        db.close()