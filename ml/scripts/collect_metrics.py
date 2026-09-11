import csv
import time
from datetime import datetime

import requests

PROMETHEUS_URL = "http://127.0.0.1:9090"

RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_FILE = (
    f"ml/data/metrics_{RUN_TIMESTAMP}.csv"
)

SAMPLE_INTERVAL = 10  # seconds


QUERIES = {
    "request_rate": 'sum(rate(k6_http_reqs_total[1m]))',

    "vus": 'k6_vus',

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

    "hpa_desired_replicas": '''
        kube_horizontalpodautoscaler_status_desired_replicas{
            namespace="ml-autoscaling",
            horizontalpodautoscaler="backend"
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
    ''',

    "failed_req_rate": '''
        sum(rate(
            k6_http_req_failed_total{
                condition="nonzero"
            }[1m]
        ))
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

        data = response.json()

        results = data["data"]["result"]

        if not results:
            return 0.0

        return float(results[0]["value"][1])

    except Exception as error:
        print(f"Query error: {error}")
        return 0.0


def collect():
    fieldnames = ["timestamp"] + list(QUERIES.keys())

    print("Starting Prometheus metric collection...")
    print(f"Saving data to: {OUTPUT_FILE}")
    print(f"Sampling interval: {SAMPLE_INTERVAL} seconds")
    print("Press Ctrl+C to stop.")

    with open(OUTPUT_FILE, "a", newline="") as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        if csvfile.tell() == 0:
            writer.writeheader()

        try:
            while True:

                row = {
                    "timestamp": datetime.now().isoformat()
                }

                for metric_name, query in QUERIES.items():
                    row[metric_name] = query_prometheus(query)

                writer.writerow(row)
                csvfile.flush()

                print(row)

                time.sleep(SAMPLE_INTERVAL)

        except KeyboardInterrupt:
            print("\nMetric collection stopped.")


if __name__ == "__main__":
    collect()
