from typing import List
import pandas as pd

EXPECTED_FEATURES:List[str]=[
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]

def load_feature_from_csv_file(csv_path:str)->pd.DataFrame:
    df=pd.read_csv(csv_path,encoding="latin1")
    missing=[c for c in EXPECTED_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    features=df[EXPECTED_FEATURES].copy().fillna(0)
    return features