import csv
import time
import subprocess
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://192.168.49.2:32483/api/emi"
HEADERS = {
    "Host": "emi.local",
    "Content-Type": "application/json"
}
PAYLOAD = {"P": 500000, "rate": 12, "n": 24}

DURATION = 60
RATE = 100
OUTPUT = "results/graph2_pod_cpu.csv"

def timestamp():
    return datetime.now().isoformat(timespec="seconds")

def send_request(scheduled):
    try:
        response = requests.post(
            URL, headers=HEADERS, json=PAYLOAD, timeout=20
        )
        return response.status_code
    except Exception:
        return 0

def monitor_pods():
    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "elapsed_seconds", "pod", "cpu", "memory"])

        start = time.perf_counter()

        while time.perf_counter() - start < DURATION:
            elapsed = round(time.perf_counter() - start, 1)

            try:
                output = subprocess.check_output(
                    ["kubectl", "top", "pods", "-n", "emi",
                     "-l", "app=emi-web", "--no-headers"],
                    text=True,
                    stderr=subprocess.STDOUT
                )

                rows = []
                for line in output.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        rows.append([timestamp(), elapsed,
                                     parts[0], parts[1], parts[2]])

                if len(rows) != 3:
                    print(f"WARNING: Expected 3 web pods, found {len(rows)}")

                writer.writerows(rows)
                f.flush()

                print(f"Recorded {len(rows)} pods at {elapsed}s")

            except Exception as error:
                print("Monitoring error:", error)

            remaining = 15 - (time.perf_counter() - start) % 15
            time.sleep(min(remaining, max(0, DURATION - (time.perf_counter() - start))))

def run_load():
    start = time.perf_counter()
    futures = []

    with ThreadPoolExecutor(max_workers=250) as executor:
        for i in range(RATE * DURATION):
            scheduled = start + i / RATE
            delay = scheduled - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            futures.append(executor.submit(send_request, scheduled))

        results = [future.result() for future in as_completed(futures)]

    successful = sum(1 for status in results if 200 <= status < 300)
    print(f"Load test: {len(results)} requests | {successful} successful | {len(results)-successful} errors")

monitor_thread = threading.Thread(target=monitor_pods)

print("Starting 100 req/s load test with 3 web pods...")
monitor_thread.start()
run_load()
monitor_thread.join()

print("Monitoring completed.")
print("Saved:", OUTPUT)
