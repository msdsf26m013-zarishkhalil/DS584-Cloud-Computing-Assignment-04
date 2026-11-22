
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load original experiment data
df = pd.read_csv("results/experiment_summary.csv")

# Keep only required fixed-replica experiments
df = df[df["replicas"].isin([1, 2, 3])].copy()

# Identify extreme scheduling-delay measurement
outliers = df[df["avg_response_ms"] > 100000]
df = df[df["avg_response_ms"] <= 100000].copy()

# Average duplicate runs
summary = (
    df.groupby(["replicas", "rate_req_sec"])["avg_response_ms"]
    .mean()
    .reset_index()
)

# Professional academic styling
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 16,
    "axes.labelsize": 12,
    "legend.fontsize": 10
})

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

styles = {
    1: {"color": "#2563EB", "marker": "o", "label": "1 Replica"},
    2: {"color": "#EA580C", "marker": "s", "label": "2 Replicas"},
    3: {"color": "#16A34A", "marker": "^", "label": "3 Replicas"}
}

for replicas, style in styles.items():
    data = summary[summary["replicas"] == replicas].sort_values("rate_req_sec")

    ax.plot(
        data["rate_req_sec"],
        data["avg_response_ms"],
        color=style["color"],
        marker=style["marker"],
        linewidth=2.5,
        markersize=8,
        label=style["label"]
    )

    # Display actual measured values
    for _, row in data.iterrows():
        ax.annotate(
            f'{row["avg_response_ms"]:,.0f}',
            (row["rate_req_sec"], row["avg_response_ms"]),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=8
        )

ax.set_yscale("log")
ax.set_xlabel("Request Rate (requests per second)")
ax.set_ylabel("Average Response Time (milliseconds)")
ax.set_title("Performance Comparison: Response Time vs Request Rate", pad=18)

ax.set_xticks([10, 25, 50, 100, 200])
ax.set_xticklabels(["10", "25", "50", "100", "200"])

ax.grid(True, which="major", linestyle="--", alpha=0.45)
ax.grid(True, which="minor", linestyle=":", alpha=0.2)
ax.legend(loc="upper left", frameon=True)

fig.text(
    0.5, 0.015,
    "Logarithmic Y-axis. One extreme scheduling-delay measurement "
    "above 100,000 ms was excluded from the plotted latency data.",
    ha="center",
    fontsize=8,
    color="dimgray"
)

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(
    "results/graphs/graph1_response_time.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("Improved Graph 1 saved successfully.")
print("Excluded extreme measurements:", len(outliers))
print("Original CSV remains unchanged.")
