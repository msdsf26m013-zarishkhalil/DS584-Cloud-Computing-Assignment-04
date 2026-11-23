
import pandas as pd
import matplotlib.pyplot as plt

# Load actual three-pod monitoring readings
df = pd.read_csv("results/graph2_pod_cpu.csv")

# Convert CPU values from millicores to numbers
df["cpu_millicores"] = (
    df["cpu"].str.replace("m", "", regex=False).astype(float)
)

# Plot settings
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 12
})

fig, ax = plt.subplots(figsize=(11, 6))

# Plot each actual web pod
for i, (pod, data) in enumerate(df.groupby("pod"), start=1):
    data = data.sort_values("elapsed_seconds")

    ax.plot(
        data["elapsed_seconds"],
        data["cpu_millicores"],
        marker="o",
        linewidth=2.5,
        markersize=7,
        label=f"Web Pod {i} ({pod[-5:]})"
    )

# Labels and title
ax.set_title(
    "CPU Utilization of Three Web Pods During Load Testing",
    pad=18,
    fontweight="bold"
)

ax.set_xlabel("Elapsed Time (seconds)")
ax.set_ylabel("CPU Usage (millicores)")

# Actual sampling intervals
ax.set_xticks([0, 15, 30, 45])
ax.set_xlim(-2, 47)
ax.set_ylim(bottom=0)

ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(title="Kubernetes Web Pods")

# Experiment information
fig.text(
    0.5, 0.015,
    "Load: 100 requests/sec | 6,000 successful requests | 0 errors\n"
    "Three web pods | CPU sampled every 15 seconds",
    ha="center",
    fontsize=9
)

plt.tight_layout(rect=[0, 0.08, 1, 1])

# Save graph
plt.savefig(
    "results/graphs/graph2_pod_cpu.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Graph 2 generated successfully!")
print("Pods plotted:", df["pod"].nunique())
print("Actual records plotted:", len(df))
print("Saved: results/graphs/graph2_pod_cpu.png")
