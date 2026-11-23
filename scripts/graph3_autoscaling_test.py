
import requests
import time
import csv
import os
import json
import threading
import subprocess
from datetime import datetime
from concurrent.futures import (
    ThreadPoolExecutor, wait, FIRST_COMPLETED
)

URL = "http://emi.local/api/emi"
HEADERS = {"Content-Type": "application/json"}
PAYLOAD = {"P": 500000, "rate": 12, "n": 24}

OUTPUT = "results/graph3_autoscaling_retry2.csv"
os.makedirs("results", exist_ok=True)

phases = [
    ("Low Load", 10, 120),
    ("High Load", 100, 300),
    ("Recovery", 10, 180)
]

local = threading.local()
lock = threading.Lock()

interval_success = 0
interval_errors = 0


def send_request():
    global interval_success, interval_errors

    if not hasattr(local, "session"):
        local.session = requests.Session()

    try:
        response = local.session.post(
            URL, headers=HEADERS,
            json=PAYLOAD, timeout=20
        )
        success = response.status_code == 200
    except Exception:
        success = False

    with lock:
        if success:
            interval_success += 1
        else:
            interval_errors += 1

    return success


def monitor(start):
    global interval_success, interval_errors

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "elapsed_seconds", "stage",
            "request_rate", "cpu_utilization_percent",
            "replicas", "successful", "errors"
        ])

        next_sample = start

        while next_sample <= start + 600:
            delay = next_sample - time.monotonic()
            if delay > 0:
                time.sleep(delay)

            elapsed = time.monotonic() - start

            if elapsed < 120:
                stage, rate = "Low Load", 10
            elif elapsed < 420:
                stage, rate = "High Load", 100
            else:
                stage, rate = "Recovery", 10

            cpu, replicas = None, None

            try:
                result = subprocess.run(
                    ["kubectl", "get", "hpa", "emi-web-hpa",
                     "-n", "emi", "-o", "json"],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=True
                )

                data = json.loads(result.stdout)
                metrics = data.get("status", {}).get(
                    "currentMetrics", []
                )

                for metric in metrics:
                    if metric.get("resource", {}).get("name") == "cpu":
                        cpu = metric["resource"]["current"].get(
                            "averageUtilization"
                        )

                replicas = data.get("status", {}).get(
                    "currentReplicas"
                )

            except Exception as e:
                print("Monitoring warning:", e)

            with lock:
                success = interval_success
                errors = interval_errors
                interval_success = 0
                interval_errors = 0

            writer.writerow([
                datetime.now().isoformat(),
                round(elapsed, 1), stage, rate,
                cpu, replicas, success, errors
            ])
            f.flush()

            print(
                f"{elapsed:6.1f}s | {stage:10} | "
                f"CPU: {cpu}% | Replicas: {replicas}"
            )

            next_sample += 15


start = time.monotonic()

monitor_thread = threading.Thread(
    target=monitor, args=(start,)
)
monitor_thread.start()

phase_results = []

try:
    with ThreadPoolExecutor(max_workers=200) as executor:
        pending = set()
        phase_start = start

        for stage, rate, duration in phases:
            print(f"\n{stage}: {rate} req/s for {duration}s")

            submitted = 0
            for i in range(rate * duration):
                scheduled = phase_start + i / rate

                delay = scheduled - time.monotonic()
                if delay > 0:
                    time.sleep(delay)

                while len(pending) >= 500:
                    done, pending = wait(
                        pending, return_when=FIRST_COMPLETED
                    )

                pending.add(executor.submit(send_request))
                submitted += 1

            phase_results.append((stage, submitted))
            phase_start += duration

        while pending:
            done, pending = wait(
                pending, return_when=FIRST_COMPLETED
            )

finally:
    monitor_thread.join()

print("\nTest finished.")
print("Requests submitted per phase:", phase_results)
print("Saved:", OUTPUT)
print("Actual elapsed time:", round(time.monotonic() - start, 1))
