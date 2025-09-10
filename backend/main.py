from io import BytesIO
from sqlalchemy.orm import Session
import tempfile
import pandas as pd
import joblib
import numpy as np
import os
# from typing import List
from fastapi import FastAPI,HTTPException,UploadFile,File,Depends
from pydantic import BaseModel
from research.chatbot import get_chat_response
from data.csv_pipeline import load_feature_from_csv_file
from data.pdf_pipeline_with_feature_extract import extract_text_from_pdf
from data.pdf_pipeline_with_feature_extract import extract_features_with_validation as extract_pdf_features
from models.db import init_db,get_db
from models.schema import RecordCreate
from models import crud

app=FastAPI()

class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree_function: float
    age: int

class ChatRequest(BaseModel):
    question:str


MODEL_PATH = os.path.join(os.path.dirname("diabities-prediction-app"), "models", "model.joblib")
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

init_db()

@app.get("/")
def read_root():
    return {"message": "Diabetes Prediction API is running."}

@app.post("/predict")
def predict_diabetes(data: DiabetesInput, db: Session = Depends(get_db)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Run the training script to generate model.joblib")
    input_row = [
        data.pregnancies,
        data.glucose,
        data.blood_pressure,
        data.skin_thickness,
        data.insulin,
        data.bmi,
        data.diabetes_pedigree_function,
        data.age,
    ]
    prediction = int(model.predict(np.array([input_row]))[0])
    record = crud.create_record(db, RecordCreate(**data.dict()), predicted=prediction)
    return {"diabetes_risk": prediction, "record_id": record.id}

@app.post("/predict/csv")
def predict_from_csv(file:UploadFile=File(...)):
    if model is None:
        raise HTTPException(status_code=500,detail="model not loaded")
    
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content=file.file.read()
        df=pd.read_csv(BytesIO(content))
        features=load_feature_from_csv_file(BytesIO(content))
        preds=model.predict(features.values)
        return {"count":len(preds),"predictions":[int(x) for x in preds]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing error: {e}")
    
@app.post("/predict/pdf")
def predict_from_pdf(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    temp_file = None
    try:
        # create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(file.file.read())
        temp_file.close()
        
        # extract text from PDF
        text = extract_text_from_pdf(temp_file.name)
        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail=f"PDF appears to be empty or unreadable. Extracted text length: {len(text) if text else 0} characters"
            )
        
        # show first 200 characters of extracted text
        print(f"PDF Text Preview: {text[:200]}...")
        
        feats, missing_features = extract_pdf_features(text)
        if not feats:
            raise HTTPException(
                status_code=400, 
                detail="could not extract any features from PDF. Ensure the PDF contains text with values like: Pregnancies: 1, Glucose: 120, BloodPressure: 70, etc."
            )
        
        if missing_features:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required features: {missing_features}. Found: {list(feats.keys())}. Please ensure all 8 features are present in the PDF."
            )
        # Make prediction
        input_row = [[
            feats["pregnancies"],
            feats["glucose"],
            feats["blood_pressure"],
            feats["skin_thickness"],
            feats["insulin"],
            feats["bmi"],
            feats["diabetes_pedigree_function"],
            feats["age"],
        ]]
        pred = int(model.predict(np.array(input_row))[0])
        return {
            "prediction": pred,
            "features": feats,
            "extracted_text_length": len(text),
            "message": "PDF processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing error: {str(e)}")
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

@app.get("/records")
def list_recent_records(db:Session = Depends(get_db)):
    items=crud.list_records(db)
    return[
        {
            "id": r.id,
            "pregnancies": r.pregnancies,
            "glucose": r.glucose,
            "blood_pressure": r.blood_pressure,
            "skin_thickness": r.skin_thickness,
            "insulin": r.insulin,
            "bmi": r.bmi,
            "diabetes_pedigree_function": r.diabetes_pedigree_function,
            "age": r.age,
            "outcome": r.outcome,
            "predicted": r.predicted,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in items
    ]


@app.post("/chat")
def chat(req:ChatRequest):
    answer=get_chat_response(req.question)
    return {"answer": answer}