from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

data = pd.read_csv(DATA_PATH)

X = data[['temperature', 'vibration', 'pressure']]
y = data['failure']

model = RandomForestClassifier()
model.fit(X, y)

class SensorData(BaseModel):
    temperature: float
    vibration: float
    pressure: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: SensorData):
    print("🔥 Backend received request:", data)

    input_data = pd.DataFrame([[data.temperature, data.vibration, data.pressure]],
                              columns=['temperature', 'vibration', 'pressure'])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    return {
        "prediction": int(prediction),
        "confidence": float(probability)
    }