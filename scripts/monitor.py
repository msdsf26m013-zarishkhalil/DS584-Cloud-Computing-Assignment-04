import csv
import time
import subprocess
import os
import threading
from datetime import datetime

os.makedirs("results", exist_ok=True)

duration = 900

def timestamp():
    return datetime.now().isoformat(timespec="seconds")

def read_cpu():
    with open("/proc/stat") as f:
        values = list(map(int, f.readline().split()[1:]))
    idle = values[3] + values[4]
    total = sum(values)
    return idle, total

def host_monitor():
    with open("results/host_cpu.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "host_cpu_percent"])

        previous_idle, previous_total = read_cpu()
        start = time.monotonic()

        while time.monotonic() - start < duration:
            time.sleep(1)
            idle, total = read_cpu()

            total_diff = total - previous_total
            idle_diff = idle - previous_idle

            cpu_percent = (
                100 * (1 - idle_diff / total_diff)
                if total_diff else 0
            )

            writer.writerow([timestamp(), round(cpu_percent, 2)])
            f.flush()

            previous_idle, previous_total = idle, total

def pod_monitor():
    with open("results/pod_metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "pod", "cpu", "memory"])

        start = time.monotonic()

        while time.monotonic() - start < duration:
            try:
                output = subprocess.check_output(
                    ["kubectl", "top", "pods", "-n", "emi", "--no-headers"],
                    text=True,
                    stderr=subprocess.STDOUT
                )

                for line in output.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        writer.writerow([
                            timestamp(), parts[0], parts[1], parts[2]
                        ])

                f.flush()

            except Exception as error:
                print("Pod monitoring error:", error)

            time.sleep(15)

print("Monitoring started for 10 minutes.")
print("Host CPU: every 1 second")
print("Pod CPU and memory: every 15 seconds")

threads = [
    threading.Thread(target=host_monitor),
    threading.Thread(target=pod_monitor)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Monitoring completed.")
print("Saved: results/host_cpu.csv")
print("Saved: results/pod_metrics.csv")
