import pandas as pd
import numpy as np


HPA_FILE = "ml/data/final_hpa_run.csv"
PRED_FILE = "ml/data/final_predictive_run.csv"

# Consider workload active when request rate exceeds 1 req/s
ACTIVE_THRESHOLD = 1.0


def load_and_trim(path, name):
    df = pd.read_csv(path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    active = df[df["request_rate"] > ACTIVE_THRESHOLD]

    if active.empty:
        raise ValueError(f"No active workload found in {path}")

    start = active["timestamp"].iloc[0]
    end = active["timestamp"].iloc[-1]

    trimmed = df[
        (df["timestamp"] >= start) &
        (df["timestamp"] <= end)
    ].copy()

    trimmed = trimmed.reset_index(drop=True)

    return trimmed, start, end


def calculate_metrics(df, name):

    duration = (
        df["timestamp"].iloc[-1]
        - df["timestamp"].iloc[0]
    ).total_seconds()

    # Approximate time represented by each observation
    intervals = (
        df["timestamp"]
        .diff()
        .dt.total_seconds()
    )

    sample_interval = intervals.median()

    # Replica-seconds approximates total allocated pod time
    replica_seconds = (
        df["replicas"].sum() * sample_interval
    )

    replica_minutes = replica_seconds / 60

    return {
        "Method": name,
        "Samples": len(df),
        "Duration_min": duration / 60,
        "Max_request_rate": df["request_rate"].max(),
        "Avg_request_rate": df["request_rate"].mean(),
        "Max_CPU_mCPU": df["cpu_mcpu"].max(),
        "Avg_CPU_mCPU": df["cpu_mcpu"].mean(),
        "Max_replicas": df["replicas"].max(),
        "Avg_replicas": df["replicas"].mean(),
        "Replica_minutes": replica_minutes,
        "Avg_response_ms": df["avg_response_ms"].mean(),
        "Max_avg_response_ms": df["avg_response_ms"].max(),
        "Avg_p95_ms": df["p95_response_ms"].mean(),
        "Max_p95_ms": df["p95_response_ms"].max(),
        "Max_failed_req_rate": df["failed_req_rate"].max(),
    }


def print_scaling_events(df, name):

    print(f"\n=== {name} REPLICA CHANGES ===")

    previous = None

    start = df["timestamp"].iloc[0]

    for _, row in df.iterrows():

        current = int(row["replicas"])

        if previous is None:
            previous = current
            print(
                f"+0.0s -> {current} replica(s)"
            )
            continue

        if current != previous:

            elapsed = (
                row["timestamp"] - start
            ).total_seconds()

            print(
                f"+{elapsed:.1f}s: "
                f"{previous} -> {current} replicas | "
                f"request_rate={row['request_rate']:.2f} | "
                f"CPU={row['cpu_mcpu']:.2f}m"
            )

            previous = current


hpa, hpa_start, hpa_end = load_and_trim(
    HPA_FILE,
    "HPA"
)

pred, pred_start, pred_end = load_and_trim(
    PRED_FILE,
    "Predictive"
)


print("=== ACTIVE WORKLOAD WINDOWS ===")

print(
    "HPA:",
    hpa_start,
    "to",
    hpa_end,
    f"({(hpa_end-hpa_start).total_seconds()/60:.2f} min)"
)

print(
    "Predictive:",
    pred_start,
    "to",
    pred_end,
    f"({(pred_end-pred_start).total_seconds()/60:.2f} min)"
)


hpa_metrics = calculate_metrics(
    hpa,
    "HPA"
)

pred_metrics = calculate_metrics(
    pred,
    "Predictive"
)

results = pd.DataFrame(
    [hpa_metrics, pred_metrics]
)


print("\n=== FINAL COMPARISON ===")

pd.set_option(
    "display.max_columns",
    None
)

print(
    results.round(3).to_string(index=False)
)


print_scaling_events(
    hpa,
    "HPA"
)

print_scaling_events(
    pred,
    "PREDICTIVE"
)


results.to_csv(
    "ml/data/final_autoscaler_comparison.csv",
    index=False
)

hpa.to_csv(
    "ml/data/final_hpa_active.csv",
    index=False
)

pred.to_csv(
    "ml/data/final_predictive_active.csv",
    index=False
)


print(
    "\nSaved:"
)

print(
    "ml/data/final_autoscaler_comparison.csv"
)

print(
    "ml/data/final_hpa_active.csv"
)

print(
    "ml/data/final_predictive_active.csv"
)
