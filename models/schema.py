from pydantic import BaseModel,Field
from typing import Optional

class RecordBase(BaseModel):
    pregnancies:int=Field(ge=0)
    glucose: float = Field(ge=0)
    blood_pressure: float = Field(ge=0)
    skin_thickness: float = Field(ge=0)
    insulin: float = Field(ge=0)
    bmi: float = Field(ge=0)
    diabetes_pedigree_function: float = Field(ge=0)
    age: int = Field(ge=0)

class RecordCreate(RecordBase):
    outcome:Optional[int]=Field(default=None)

class Record(RecordBase):
    id: int
    outcome: Optional[int] = None
    predicted: Optional[int] = None

    class Config:
        from_attributes = True