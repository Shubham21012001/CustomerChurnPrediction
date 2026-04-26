from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from predict import predict_churn
from database import init_db, save_prediction, get_all_predictions, get_stats

# === Initialize app and database ===
app = FastAPI(
    title="Customer Churn Prediction API",
    description="Predicts whether a telecom customer will churn or not",
    version="1.0.0"
)

init_db()

# === Input schema ===
class CustomerData(BaseModel):
    tenure: float
    MonthlyCharges: float
    TotalCharges: float
    gender: str
    Partner: str
    Dependents: str
    PhoneService: str
    PaperlessBilling: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaymentMethod: str

# === Endpoints ===

@app.get("/")
def root():
    return {"message": "Customer Churn Prediction API is running!"}

@app.post("/predict")
def predict(customer: CustomerData):
    try:
        input_data = customer.dict()
        probability, prediction = predict_churn(input_data)
        save_prediction(input_data, probability, prediction)
        return {
            "churn_prediction": prediction,
            "churn_probability": probability,
            "message": f"This customer has a {round(probability*100, 1)}% chance of churning"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def history():
    rows = get_all_predictions()
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "timestamp": row[1],
            "tenure": row[2],
            "monthly_charges": row[3],
            "total_charges": row[4],
            "contract": row[5],
            "internet_service": row[6],
            "churn_probability": row[7],
            "churn_prediction": row[8]
        })
    return {"total": len(results), "predictions": results}

@app.get("/stats")
def stats():
    return get_stats()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)