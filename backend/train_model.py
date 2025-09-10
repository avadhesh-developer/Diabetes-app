import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

df = pd.read_csv("./data/diabetes.csv")

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

model = RandomForestClassifier(verbose=True)
model.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.joblib")
print("Model saved as models/model.joblib")