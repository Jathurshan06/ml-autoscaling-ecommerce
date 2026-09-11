import math
import subprocess
import time
from collections import deque

import joblib
import pandas as pd
import requests


PROMETHEUS_URL = "http://127.0.0.1:9090"

MODEL_FILE = "ml/models/cpu_predictor.joblib"

NAMESPACE = "ml-autoscaling"
DEPLOYMENT = "backend"

MIN_REPLICAS = 1
MAX_REPLICAS = 5

# Backend CPU request = 100m
CPU_REQUEST_PER_POD_MCPU = 100

# Equivalent to Kubernetes HPA target = 50%
TARGET_CPU_UTILISATION = 0.50

# Effective target CPU per replica = 50m
TARGET_CPU_PER_POD_MCPU = (
    CPU_REQUEST_PER_POD_MCPU * TARGET_CPU_UTILISATION
)

# Collect metrics every 10 seconds
SAMPLE_INTERVAL = 10

# Prevent immediate scale-down after a scale-up
SCALE_DOWN_COOLDOWN = 60


QUERIES = {
    "request_rate":
        'sum(rate(k6_http_reqs_total[1m]))',

    "cpu_mcpu": '''
        sum(
            rate(
                container_cpu_usage_seconds_total{
                    namespace="ml-autoscaling",
                    pod=~"backend-.*",
                    cpu="total"
                }[1m]
            )
        ) * 1000
    ''',

    "memory_mib": '''
        sum(
            container_memory_working_set_bytes{
                namespace="ml-autoscaling",
                pod=~"backend-.*"
            }
        ) / 1024 / 1024
    ''',

    "replicas": '''
        kube_deployment_status_replicas{
            namespace="ml-autoscaling",
            deployment="backend"
        }
    ''',

    "avg_response_ms": '''
        sum(rate(k6_http_req_duration_milliseconds_sum[1m]))
        /
        sum(rate(k6_http_req_duration_milliseconds_count[1m]))
    ''',

    "p95_response_ms": '''
        histogram_quantile(
            0.95,
            sum by (le) (
                rate(k6_http_req_duration_milliseconds_bucket[1m])
            )
        )
    '''
}


def query_prometheus(query):
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5,
        )

        response.raise_for_status()

        result = response.json()["data"]["result"]

        if not result:
            return 0.0

        return float(result[0]["value"][1])

    except Exception as error:
        print("Prometheus query error:", error)
        return 0.0


def scale_deployment(replicas):
    command = [
        "kubectl",
        "scale",
        "deployment",
        DEPLOYMENT,
        f"--replicas={replicas}",
        "-n",
        NAMESPACE,
    ]

    subprocess.run(
        command,
        check=True
    )


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

model_package = joblib.load(MODEL_FILE)

model = model_package["model"]
features = model_package["features"]

print("=== AI PREDICTIVE AUTOSCALER ===")
print("Model:", MODEL_FILE)
print("Prediction horizon: 60 seconds")
print(
    "Target CPU per replica:",
    TARGET_CPU_PER_POD_MCPU,
    "mCPU"
)
print(
    f"Replica range: {MIN_REPLICAS}-{MAX_REPLICAS}"
)


# --------------------------------------------------
# Historical metric buffers
# --------------------------------------------------

request_history = deque(maxlen=6)
cpu_history = deque(maxlen=6)

last_scale_up_time = 0

# Tracks the most recent replica count requested by
# the predictive scaler while Kubernetes is converging.
last_requested_replicas = None


print("\nCollecting initial history...")


try:

    while True:

        request_rate = query_prometheus(
            QUERIES["request_rate"]
        )

        cpu_mcpu = query_prometheus(
            QUERIES["cpu_mcpu"]
        )

        memory_mib = query_prometheus(
            QUERIES["memory_mib"]
        )

        replicas = query_prometheus(
            QUERIES["replicas"]
        )

        avg_response_ms = query_prometheus(
            QUERIES["avg_response_ms"]
        )

        p95_response_ms = query_prometheus(
            QUERIES["p95_response_ms"]
        )


        request_history.append(request_rate)
        cpu_history.append(cpu_mcpu)


        # Need six samples for lag-6 / rolling-6 features
        if len(request_history) < 6:

            print(
                f"History {len(request_history)}/6 | "
                f"requests={request_rate:.2f} | "
                f"CPU={cpu_mcpu:.2f}m"
            )

            time.sleep(SAMPLE_INTERVAL)
            continue


        # --------------------------------------------------
        # Generate the same features used during training
        # --------------------------------------------------

        row = {
            "request_rate": request_rate,
            "cpu_mcpu": cpu_mcpu,
            "memory_mib": memory_mib,
            "replicas": replicas,
            "avg_response_ms": avg_response_ms,
            "p95_response_ms": p95_response_ms,

            "request_rate_lag1":
                request_history[-2],

            "request_rate_lag3":
                request_history[-4],

            "request_rate_lag6":
                request_history[0],

            "cpu_lag1":
                cpu_history[-2],

            "cpu_lag3":
                cpu_history[-4],

            "cpu_lag6":
                cpu_history[0],

            "request_rate_rolling_mean_3":
                sum(list(request_history)[-3:]) / 3,

            "request_rate_rolling_mean_6":
                sum(request_history) / 6,

            "cpu_rolling_mean_3":
                sum(list(cpu_history)[-3:]) / 3,

            "cpu_rolling_mean_6":
                sum(cpu_history) / 6,

            "request_rate_change":
                request_rate - request_history[-4],

            "cpu_change":
                cpu_mcpu - cpu_history[-4],
        }


        X = pd.DataFrame(
            [row],
            columns=features
        )


        # --------------------------------------------------
        # Predict CPU demand approximately 60 seconds ahead
        # --------------------------------------------------

        predicted_cpu = float(
            model.predict(X)[0]
        )

        predicted_cpu = max(
            0,
            predicted_cpu
        )


        # --------------------------------------------------
        # Convert predicted CPU demand to replica count
        # --------------------------------------------------

        desired_replicas = math.ceil(
            predicted_cpu /
            TARGET_CPU_PER_POD_MCPU
        )

        desired_replicas = max(
            MIN_REPLICAS,
            desired_replicas
        )

        desired_replicas = min(
            MAX_REPLICAS,
            desired_replicas
        )


        current_replicas = int(
            round(replicas)
        )


        print(
            f"Requests={request_rate:7.2f} req/s | "
            f"CPU={cpu_mcpu:7.2f}m | "
            f"Predicted(+60s)={predicted_cpu:7.2f}m | "
            f"Current={current_replicas} | "
            f"Desired={desired_replicas}"
        )


        # --------------------------------------------------
        # Determine effective current replica state
        # --------------------------------------------------

        effective_current = current_replicas

        if last_requested_replicas is not None:

            effective_current = last_requested_replicas

            # Kubernetes has caught up with the previous
            # scaling request.
            if current_replicas == last_requested_replicas:

                last_requested_replicas = None
                effective_current = current_replicas


        # --------------------------------------------------
        # Scale up
        # --------------------------------------------------

        if desired_replicas > effective_current:

            print(
                f" SCALE UP: "
                f"{effective_current} -> "
                f"{desired_replicas}"
            )

            scale_deployment(
                desired_replicas
            )

            last_requested_replicas = desired_replicas
            last_scale_up_time = time.time()


        # --------------------------------------------------
        # Scale down
        # --------------------------------------------------

        elif desired_replicas < effective_current:

            seconds_since_scale_up = (
                time.time() - last_scale_up_time
            )

            if (
                seconds_since_scale_up
                >= SCALE_DOWN_COOLDOWN
            ):

                print(
                    f" SCALE DOWN: "
                    f"{effective_current} -> "
                    f"{desired_replicas}"
                )

                scale_deployment(
                    desired_replicas
                )

                last_requested_replicas = desired_replicas

            else:

                remaining = int(
                    SCALE_DOWN_COOLDOWN
                    - seconds_since_scale_up
                )

                print(
                    " Scale-down deferred "
                    f"(cooldown: {remaining}s remaining)"
                )


        time.sleep(SAMPLE_INTERVAL)


except KeyboardInterrupt:

    print(
        "\nPredictive autoscaler stopped."
    )

except Exception as error:

    print(
        "\nPredictive autoscaler stopped due to error:"
    )

    print(error)
