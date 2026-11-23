import requests
import time
import csv
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://192.168.49.2:32483/api/emi"
HEADERS = {"Host": "emi.local", "Content-Type": "application/json"}
PAYLOAD = {"P": 500000, "rate": 12, "n": 24}

phases = [(10, 120), (100, 300), (10, 180)]
os.makedirs("results", exist_ok=True)

with open("results/hpa_load_test_retry.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "rate_req_sec", "duration_sec",
                     "total_requests", "successful", "errors"])

    for rate, duration in phases:
        print(f"\nStarting {rate} req/s for {duration} seconds")
        start = time.monotonic()
        futures = []

        with ThreadPoolExecutor(max_workers=250) as executor:
            for i in range(rate * duration):
                scheduled = start + i / rate
                delay = scheduled - time.monotonic()
                if delay > 0:
                    time.sleep(delay)

                futures.append(executor.submit(
                    requests.post, URL,
                    headers=HEADERS, json=PAYLOAD, timeout=20
                ))

            success = errors = 0
            for future in as_completed(futures):
                try:
                    if future.result().status_code == 200:
                        success += 1
                    else:
                        errors += 1
                except Exception:
                    errors += 1

        writer.writerow([datetime.now().isoformat(), rate, duration,
                         rate * duration, success, errors])
        f.flush()
        print(f"Completed: {success} successful | {errors} errors")

print("\n10-minute staged load test completed.")
print("Saved: results/hpa_load_test_retry.csv")
