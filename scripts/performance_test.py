import requests
import time
import csv
import os
import argparse
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser()
parser.add_argument("--replicas", type=int, required=True)
parser.add_argument("--rate", type=int, required=True)
parser.add_argument("--duration", type=int, default=60)
args = parser.parse_args()

URL = "http://192.168.49.2:32483/api/emi"
HEADERS = {
    "Host": "emi.local",
    "Content-Type": "application/json"
}
PAYLOAD = {"P": 500000, "rate": 12, "n": 24}

os.makedirs("results", exist_ok=True)

def send_request(scheduled):
    try:
        response = requests.post(
            URL, headers=HEADERS, json=PAYLOAD, timeout=20
        )
        latency = (time.perf_counter() - scheduled) * 1000
        return response.status_code, latency, ""
    except Exception as error:
        latency = (time.perf_counter() - scheduled) * 1000
        return 0, latency, str(error)

print(f"Starting: {args.rate} req/s | {args.replicas} replicas | {args.duration}s")

start = time.perf_counter()
futures = []

with ThreadPoolExecutor(max_workers=250) as executor:
    for i in range(args.rate * args.duration):
        scheduled = start + i / args.rate
        delay = scheduled - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        futures.append(executor.submit(send_request, scheduled))

    results = [future.result() for future in as_completed(futures)]

latencies = [r[1] for r in results]
success = sum(1 for r in results if 200 <= r[0] < 300)
errors = len(results) - success
avg = statistics.mean(latencies) if latencies else 0
p95 = sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else 0

summary_file = "results/experiment_summary.csv"
write_header = not os.path.exists(summary_file)

with open(summary_file, "a", newline="") as file:
    writer = csv.writer(file)
    if write_header:
        writer.writerow(["replicas", "rate_req_sec", "duration_sec",
                         "total_requests", "successful", "errors",
                         "avg_response_ms", "p95_response_ms"])
    writer.writerow([args.replicas, args.rate, args.duration,
                     len(results), success, errors, round(avg, 2), round(p95, 2)])

print(f"Total: {len(results)} | Successful: {success} | Errors: {errors}")
print(f"Average response time: {avg:.2f} ms")
print(f"P95 response time: {p95:.2f} ms")
print(f"Saved: {summary_file}")
