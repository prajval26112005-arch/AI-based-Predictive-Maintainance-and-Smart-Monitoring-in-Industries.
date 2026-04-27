import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

# Train model once
data = pd.read_csv(DATA_PATH)
X = data[['temperature', 'vibration', 'pressure']]
y = data['failure']

model = RandomForestClassifier()
model.fit(X, y)

def predict_failure(temp, vib, pres):
    input_data = [[temp, vib, pres]]
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    return int(prediction), float(probability)
from sklearn.metrics import accuracy_score

y_pred = model.predict(X)
accuracy = accuracy_score(y, y_pred)
print("Model Accuracy:", accuracy)