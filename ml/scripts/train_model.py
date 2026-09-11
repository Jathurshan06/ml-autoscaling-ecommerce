import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

INPUT_FILE = "ml/data/ml_dataset.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

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

# Chronological 80/20 split
split_index = int(len(df) * 0.80)

train = df.iloc[:split_index]
test = df.iloc[split_index:]

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

print("=== DATA SPLIT ===")
print("Training samples:", len(train))
print("Testing samples:", len(test))

models = {
    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
}

results = []

for name, model in models.items():

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

results_df = pd.DataFrame(results)

print("\n=== MODEL COMPARISON ===")
print(results_df.round(3).to_string(index=False))
