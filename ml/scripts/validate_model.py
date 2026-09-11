import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

TRAINING_FILE = "ml/data/ml_dataset.csv"
VALIDATION_FILE = "ml/data/metrics_2026-08-28_21-38-55.csv"

PREDICTION_SECONDS = 60


features = [
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

target = "future_cpu_mcpu"


def preprocess_validation(df):

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Lag features
    df["request_rate_lag1"] = df["request_rate"].shift(1)
    df["request_rate_lag3"] = df["request_rate"].shift(3)
    df["request_rate_lag6"] = df["request_rate"].shift(6)

    df["cpu_lag1"] = df["cpu_mcpu"].shift(1)
    df["cpu_lag3"] = df["cpu_mcpu"].shift(3)
    df["cpu_lag6"] = df["cpu_mcpu"].shift(6)

    # Rolling averages
    df["request_rate_rolling_mean_3"] = (
        df["request_rate"].rolling(3).mean()
    )

    df["request_rate_rolling_mean_6"] = (
        df["request_rate"].rolling(6).mean()
    )

    df["cpu_rolling_mean_3"] = (
        df["cpu_mcpu"].rolling(3).mean()
    )

    df["cpu_rolling_mean_6"] = (
        df["cpu_mcpu"].rolling(6).mean()
    )

    # Trends
    df["request_rate_change"] = (
        df["request_rate"] - df["request_rate_lag3"]
    )

    df["cpu_change"] = (
        df["cpu_mcpu"] - df["cpu_lag3"]
    )

    # True 60-second future CPU target
    future_cpu = []

    for current_time in df["timestamp"]:

        target_time = current_time + pd.Timedelta(
            seconds=PREDICTION_SECONDS
        )

        future_rows = df[df["timestamp"] >= target_time]

        if future_rows.empty:
            future_cpu.append(None)
        else:
            future_cpu.append(
                future_rows.iloc[0]["cpu_mcpu"]
            )

    df["future_cpu_mcpu"] = future_cpu

    return df.dropna().reset_index(drop=True)


# -------------------------------------------------
# Original training data
# -------------------------------------------------

train = pd.read_csv(TRAINING_FILE)

X_train = train[features]
y_train = train[target]


# -------------------------------------------------
# Independent validation workload
# -------------------------------------------------

validation_raw = pd.read_csv(VALIDATION_FILE)

validation = preprocess_validation(
    validation_raw
)

X_validation = validation[features]
y_validation = validation[target]


# -------------------------------------------------
# Train Linear Regression
# -------------------------------------------------

model = LinearRegression()

model.fit(
    X_train,
    y_train
)


# -------------------------------------------------
# Predict unseen workload
# -------------------------------------------------

predictions = model.predict(
    X_validation
)


# Prevent impossible negative CPU predictions
predictions = predictions.clip(min=0)


# -------------------------------------------------
# Evaluate
# -------------------------------------------------

mae = mean_absolute_error(
    y_validation,
    predictions
)

rmse = mean_squared_error(
    y_validation,
    predictions
) ** 0.5

r2 = r2_score(
    y_validation,
    predictions
)


print("=== INDEPENDENT VALIDATION ===")

print("Training samples:", len(train))
print("Validation samples:", len(validation))

print(
    "Validation period:",
    validation["timestamp"].min(),
    "to",
    validation["timestamp"].max()
)

print("\nValidation workload:")
print(
    "Max request rate:",
    round(validation["request_rate"].max(), 3)
)

print(
    "Max CPU:",
    round(validation["cpu_mcpu"].max(), 3),
    "mCPU"
)

print(
    "Max replicas:",
    int(validation["replicas"].max())
)


print("\n=== LINEAR REGRESSION VALIDATION RESULTS ===")
print(f"MAE:  {mae:.3f} mCPU")
print(f"RMSE: {rmse:.3f} mCPU")
print(f"R²:   {r2:.3f}")


# Save prediction results for later graphs/report
results = validation[
    [
        "timestamp",
        "request_rate",
        "cpu_mcpu",
        "future_cpu_mcpu",
        "replicas"
    ]
].copy()

results["predicted_future_cpu_mcpu"] = predictions

results.to_csv(
    "ml/data/validation_predictions.csv",
    index=False
)

print(
    "\nSaved predictions to:",
    "ml/data/validation_predictions.csv"
)
