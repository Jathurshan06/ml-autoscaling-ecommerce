import pandas as pd
import matplotlib.pyplot as plt

# Load validation predictions
df = pd.read_csv("ml/data/validation_predictions.csv")

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Convert time to elapsed minutes from the start of validation
df["elapsed_minutes"] = (
    df["timestamp"] - df["timestamp"].iloc[0]
).dt.total_seconds() / 60

# Create plot
plt.figure(figsize=(12, 6))

plt.plot(
    df["elapsed_minutes"],
    df["future_cpu_mcpu"],
    linewidth=2,
    label="Actual future CPU"
)

plt.plot(
    df["elapsed_minutes"],
    df["predicted_future_cpu_mcpu"],
    linewidth=2,
    label="Predicted future CPU"
)

plt.xlabel("Elapsed time (minutes)")
plt.ylabel("Backend CPU demand (mCPU)")
plt.title("Independent Validation: Actual vs Predicted Future CPU Demand")

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# Save high-resolution image
plt.savefig(
    "ml/results/validation_actual_vs_predicted.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: ml/results/validation_actual_vs_predicted.png")
