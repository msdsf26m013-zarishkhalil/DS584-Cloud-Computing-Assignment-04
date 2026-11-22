
import pandas as pd
import matplotlib.pyplot as plt
import os

# Project results folder
os.makedirs("results/graphs", exist_ok=True)

# Load saved CSV files
performance = pd.read_csv("results/experiment_summary.csv")
pod_metrics = pd.read_csv("results/pod_metrics.csv")
hpa = pd.read_csv("results/hpa_load_test.csv")

# Convert CPU values such as 5m into numeric millicores
pod_metrics["cpu_millicores"] = (
    pod_metrics["cpu"].str.replace("m", "", regex=False).astype(float)
)

# GRAPH 1: Average response time vs request rate
# Duplicate experimental runs are averaged
grouped = performance.groupby(
    ["replicas", "rate_req_sec"]
)["avg_response_ms"].mean().reset_index()

plt.figure(figsize=(9, 5))
for replicas in sorted(grouped["replicas"].unique()):
    data = grouped[grouped["replicas"] == replicas]
    plt.plot(
        data["rate_req_sec"],
        data["avg_response_ms"],
        marker="o",
        label=f"{replicas} Replica(s)"
    )

plt.xlabel("Request Rate (requests/sec)")
plt.ylabel("Average Response Time (ms)")
plt.title("Average Response Time vs Request Rate")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("results/graphs/graph1_response_time.png", dpi=300)
plt.close()

# GRAPH 2: CPU utilization of web pods over time
web_pods = pod_metrics[pod_metrics["pod"].str.startswith("emi-web")].copy()
web_pods["timestamp"] = pd.to_datetime(web_pods["timestamp"])

plt.figure(figsize=(11, 5))
for pod, data in web_pods.groupby("pod"):
    plt.plot(
        data["timestamp"],
        data["cpu_millicores"],
        marker=".",
        label=pod[-5:]
    )

plt.xlabel("Time")
plt.ylabel("CPU Usage (millicores)")
plt.title("Web Pod CPU Usage Over Time")
plt.legend(title="Pod ID")
plt.xticks(rotation=30)
plt.grid(True)
plt.tight_layout()
plt.savefig("results/graphs/graph2_pod_cpu.png", dpi=300)
plt.close()

# GRAPH 3: Staged load test - request rate and success/error counts
hpa["stage"] = ["Low Load", "High Load", "Low Load (Recovery)"]

fig, ax1 = plt.subplots(figsize=(9, 5))
x = range(len(hpa))

ax1.bar(x, hpa["rate_req_sec"], alpha=0.7, label="Request Rate")
ax1.set_ylabel("Request Rate (requests/sec)")
ax1.set_xticks(list(x))
ax1.set_xticklabels(hpa["stage"])

ax2 = ax1.twinx()
ax2.plot(x, hpa["successful"], marker="o", label="Successful Requests")
ax2.plot(x, hpa["errors"], marker="s", label="Errors")
ax2.set_ylabel("Number of Requests")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.title("Staged Load Test: Request Rate and Outcomes")
fig.tight_layout()
plt.savefig("results/graphs/graph3_hpa_load.png", dpi=300)
plt.close()

print("All 3 graphs generated successfully in results/graphs/")
