import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# FILE LOCATIONS
# ============================================================

HPA_FILE = "ml/data/final_hpa_active.csv"
PRED_FILE = "ml/data/final_predictive_active.csv"
OUTPUT_DIR = "ml/results"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

def prepare(path):
    df = pd.read_csv(path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Convert timestamps to elapsed seconds from workload start
    df["elapsed_seconds"] = (
        df["timestamp"] - df["timestamp"].iloc[0]
    ).dt.total_seconds()

    return df


hpa = prepare(HPA_FILE)
pred = prepare(PRED_FILE)


# ============================================================
# FIGURE 1
# HPA REQUEST RATE + REPLICA COUNT
# ============================================================

fig, ax1 = plt.subplots(figsize=(10, 5.5))

# Request rate
ax1.plot(
    hpa["elapsed_seconds"],
    hpa["request_rate"],
    color="blue",
    linewidth=2,
    label="Request Rate"
)

ax1.set_xlabel("Elapsed Time (seconds)")
ax1.set_ylabel(
    "Request Rate (requests/s)",
    color="blue"
)

ax1.tick_params(
    axis="y",
    labelcolor="blue"
)

ax1.grid(
    True,
    alpha=0.25
)

# Replica count
ax2 = ax1.twinx()

ax2.step(
    hpa["elapsed_seconds"],
    hpa["replicas"],
    where="post",
    color="red",
    linewidth=2,
    label="Backend Replicas"
)

ax2.set_ylabel(
    "Number of Replicas",
    color="red"
)

ax2.tick_params(
    axis="y",
    labelcolor="red"
)

ax2.set_ylim(0.5, 5.5)
ax2.set_yticks([1, 2, 3, 4, 5])

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="upper left"
)

plt.title(
    "Kubernetes HPA: Request Rate and Replica Scaling"
)

fig.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/hpa_scaling.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 2
# PREDICTIVE REQUEST RATE + REPLICA COUNT
# ============================================================

fig, ax1 = plt.subplots(figsize=(10, 5.5))

# Request rate
ax1.plot(
    pred["elapsed_seconds"],
    pred["request_rate"],
    color="blue",
    linewidth=2,
    label="Request Rate"
)

ax1.set_xlabel("Elapsed Time (seconds)")
ax1.set_ylabel(
    "Request Rate (requests/s)",
    color="blue"
)

ax1.tick_params(
    axis="y",
    labelcolor="blue"
)

ax1.grid(
    True,
    alpha=0.25
)

# Replica count
ax2 = ax1.twinx()

ax2.step(
    pred["elapsed_seconds"],
    pred["replicas"],
    where="post",
    color="red",
    linewidth=2,
    label="Backend Replicas"
)

ax2.set_ylabel(
    "Number of Replicas",
    color="red"
)

ax2.tick_params(
    axis="y",
    labelcolor="red"
)

ax2.set_ylim(0.5, 5.5)
ax2.set_yticks([1, 2, 3, 4, 5])

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="upper left"
)

plt.title(
    "Predictive Autoscaler: Request Rate and Replica Scaling"
)

fig.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/predictive_scaling.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 3
# DIRECT HPA VS PREDICTIVE REPLICA COMPARISON
# ============================================================

fig, ax = plt.subplots(figsize=(10, 5.5))

ax.step(
    hpa["elapsed_seconds"],
    hpa["replicas"],
    where="post",
    color="blue",
    linewidth=2.2,
    label="Kubernetes HPA"
)

ax.step(
    pred["elapsed_seconds"],
    pred["replicas"],
    where="post",
    color="red",
    linewidth=2.2,
    label="Predictive Autoscaler"
)

ax.set_xlabel(
    "Elapsed Time (seconds)"
)

ax.set_ylabel(
    "Number of Backend Replicas"
)

ax.set_ylim(0.5, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])

ax.grid(
    True,
    alpha=0.25
)

ax.legend(
    loc="lower right"
)

plt.title(
    "Replica Scaling Comparison: HPA vs Predictive Autoscaler"
)

fig.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/replica_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINISHED
# ============================================================

print("\n=== GRAPHS GENERATED SUCCESSFULLY ===")
print(f"1. {OUTPUT_DIR}/hpa_scaling.png")
print(f"2. {OUTPUT_DIR}/predictive_scaling.png")
print(f"3. {OUTPUT_DIR}/replica_comparison.png")
