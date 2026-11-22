
import pandas as pd
import matplotlib.pyplot as plt

# Load pod monitoring data
df = pd.read_csv("results/pod_metrics.csv")

# Keep only EMI web pods
df = df[df["pod"].str.startswith("emi-web")].copy()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["cpu_millicores"] = (
    df["cpu"].str.replace("m", "", regex=False).astype(float)
)

df = df.sort_values("timestamp")

plt.rcParams.update({"font.size": 11})

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

for pod, data in df.groupby("pod"):
    ax.plot(
        data["timestamp"],
        data["cpu_millicores"],
        marker="o",
        markersize=4,
        linewidth=1.8,
        label=pod[-5:]
    )

ax.set_title("CPU Utilization of EMI Web Pods Over Time", fontsize=15, pad=15)
ax.set_xlabel("Monitoring Time")
ax.set_ylabel("CPU Usage (millicores)")

ax.grid(True, linestyle="--", alpha=0.35)
ax.legend(title="Pod ID", bbox_to_anchor=(1.02, 1), loc="upper left")

fig.autofmt_xdate()
plt.tight_layout()

plt.savefig(
    "results/graphs/graph2_pod_cpu.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("Improved Graph 2 saved successfully.")
print("Web pod records plotted:", len(df))
