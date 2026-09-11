import os
import joblib
import pandas as pd

from sklearn.linear_model import LinearRegression

INPUT_FILE = "ml/data/ml_dataset.csv"
MODEL_DIR = "ml/models"
MODEL_FILE = f"{MODEL_DIR}/cpu_predictor.joblib"

FEATURES = [
    "request_rate",
    "cpu_mcpu",
    "memory_mib",
    "replicas",
    "avg_response_ms",
    "p95_response_ms",

    "request_rate_lag1",
    "request_rate_lag3",
    "request_rate_lag6",

    "cpu_lag1",
    "cpu_lag3",
    "cpu_lag6",

    "request_rate_rolling_mean_3",
    "request_rate_rolling_mean_6",

    "cpu_rolling_mean_3",
    "cpu_rolling_mean_6",

    "request_rate_change",
    "cpu_change",
]

TARGET = "future_cpu_mcpu"

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

X = df[FEATURES]
y = df[TARGET]

model = LinearRegression()

model.fit(X, y)

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "prediction_horizon_seconds": 60
    },
    MODEL_FILE
)

print("=== MODEL SAVED ===")
print("Model:", MODEL_FILE)
print("Training samples:", len(df))
print("Features:", len(FEATURES))
print("Prediction horizon: 60 seconds")
