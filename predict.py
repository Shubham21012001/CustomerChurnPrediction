import pickle
import json
import numpy as np
import pandas as pd

# === Load model ===
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

# === Load feature columns ===
with open("artifacts/feature_columns.txt", "r") as f:
    feature_columns = [line.strip() for line in f.readlines()]

print(f"✅ Model loaded successfully")
print(f"✅ Loaded {len(feature_columns)} feature columns")

def predict_churn(input_data: dict):
    """
    Takes raw customer data as a dictionary,
    aligns it to model feature columns,
    and returns churn probability and prediction.
    """

    # === Step 1: Convert input to DataFrame ===
    df = pd.DataFrame([input_data])

    # === Step 2: One-hot encode categorical columns ===
    categorical_cols = [
        "MultipleLines", "InternetService", "OnlineSecurity",
        "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies", "Contract", "PaymentMethod"
    ]
    binary_cols = {
        "gender": {"Male": 1, "Female": 0},
        "Partner": {"Yes": 1, "No": 0},
        "Dependents": {"Yes": 1, "No": 0},
        "PhoneService": {"Yes": 1, "No": 0},
        "PaperlessBilling": {"Yes": 1, "No": 0},
    }

    # Apply binary encoding
    for col, mapping in binary_cols.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)

    # Apply one-hot encoding
    df = pd.get_dummies(df, columns=categorical_cols)

    # === Step 3: Align columns to match training features ===
    # Add missing columns with 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    # Keep only the columns the model was trained on, in the right order
    df = df[feature_columns]

    # === Step 4: Convert booleans to int ===
    for col in df.select_dtypes(include=["bool"]).columns:
        df[col] = df[col].astype(int)

    # === Step 5: Make prediction ===
    probability = model.predict_proba(df)[0][1]
    threshold = 0.35
    prediction = "Churn" if probability >= threshold else "No Churn"

    return round(float(probability), 4), prediction