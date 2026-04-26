import sqlite3
import os
from datetime import datetime

DB_PATH = "predictions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tenure REAL,
            monthly_charges REAL,
            total_charges REAL,
            contract TEXT,
            internet_service TEXT,
            churn_probability REAL,
            churn_prediction TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(input_data: dict, probability: float, prediction: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            timestamp, tenure, monthly_charges, total_charges,
            contract, internet_service, churn_probability, churn_prediction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_data.get("tenure", 0),
        input_data.get("MonthlyCharges", 0),
        input_data.get("TotalCharges", 0),
        input_data.get("Contract", ""),
        input_data.get("InternetService", ""),
        round(probability, 4),
        prediction
    ))
    conn.commit()
    conn.close()

def get_all_predictions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE churn_prediction = 'Churn'")
    churned = cursor.fetchone()[0]
    conn.close()
    return {
        "total_predictions": total,
        "churn_count": churned,
        "no_churn_count": total - churned,
        "churn_rate_percent": round((churned / total * 100), 2) if total > 0 else 0
    }