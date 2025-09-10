import os
from datetime import datetime
from typing import Generator
from sqlalchemy import create_engine,Column,Integer,Float,DateTime
from sqlalchemy.orm import declarative_base,sessionmaker,Session

THIS_DIR=os.path.dirname("./data/diabetes.csv")
DEFAULT_DB_PATH = os.path.join(THIS_DIR, "diabetes.db")
DATABASE_URL=os.getenv("DATABASE_URL",f"sqlite:///{DEFAULT_DB_PATH}")

engine=create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

class PatientRecord(Base):
    __tablename__="patient_records"

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    pregnancies = Column(Integer, nullable=False)
    glucose = Column(Float, nullable=False)
    blood_pressure = Column(Float, nullable=False)
    skin_thickness = Column(Float, nullable=False)
    insulin = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    diabetes_pedigree_function = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    outcome = Column(Integer, nullable=True)
    predicted = Column(Integer, nullable=True)
    created_at=Column(DateTime, default=datetime.utcnow, nullable=False)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db()->Generator[Session,None,None]:
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

