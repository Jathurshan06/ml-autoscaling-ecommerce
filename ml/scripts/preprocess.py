import pandas as pd

INPUT_FILE = "ml/data/training_run_2026-08-28.csv"
OUTPUT_FILE = "ml/data/ml_dataset.csv"

# Prediction horizon
PREDICTION_SECONDS = 60


# -------------------------------------------------
# Load data
# -------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)


# -------------------------------------------------
# Create historical features
# -------------------------------------------------

# Approximately 10, 30 and 60 seconds of history.
df["request_rate_lag1"] = df["request_rate"].shift(1)
df["request_rate_lag3"] = df["request_rate"].shift(3)
df["request_rate_lag6"] = df["request_rate"].shift(6)

df["cpu_lag1"] = df["cpu_mcpu"].shift(1)
df["cpu_lag3"] = df["cpu_mcpu"].shift(3)
df["cpu_lag6"] = df["cpu_mcpu"].shift(6)


# Recent rolling behaviour
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


# Workload trend
df["request_rate_change"] = (
    df["request_rate"] - df["request_rate_lag3"]
)

df["cpu_change"] = (
    df["cpu_mcpu"] - df["cpu_lag3"]
)


# -------------------------------------------------
# Create true 60-second future CPU target
# -------------------------------------------------

timestamps = df["timestamp"]
cpu_values = df["cpu_mcpu"]

future_cpu = []

for current_time in timestamps:

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


# -------------------------------------------------
# Remove rows where lag or future target is missing
# -------------------------------------------------

df = df.dropna().reset_index(drop=True)


# -------------------------------------------------
# Save processed dataset
# -------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)


print("=== PREPROCESSING COMPLETE ===")
print("Input:", INPUT_FILE)
print("Output:", OUTPUT_FILE)
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nDataset columns:")
for column in df.columns:
    print(" -", column)

print("\nFuture CPU target:")
print(df["future_cpu_mcpu"].describe())
