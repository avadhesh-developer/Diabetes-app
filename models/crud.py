from sqlalchemy.orm import Session
from .db import PatientRecord
from .schema import RecordCreate
from typing import List,Optional

def create_record(db:Session,data:RecordCreate,predicted:Optional[int]=None)->PatientRecord:

    record=PatientRecord(
        pregnancies=data.pregnancies,
        glucose=data.glucose,
        blood_pressure=data.blood_pressure,
        skin_thickness=data.skin_thickness,
        insulin=data.insulin,
        bmi=data.bmi,
        diabetes_pedigree_function=data.diabetes_pedigree_function,
        age=data.age,
        outcome=data.outcome,
        predicted=predicted,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def list_records(db: Session, limit: int = 50) -> List[PatientRecord]:
    return db.query(PatientRecord).order_by(PatientRecord.id.desc()).limit(limit).all()




