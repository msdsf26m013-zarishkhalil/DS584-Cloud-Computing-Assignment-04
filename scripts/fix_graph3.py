import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv("results/graph3_autoscaling_retry2.csv")

os.makedirs("results/graphs", exist_ok=True)

time = df["elapsed_seconds"]
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

# Graph 1: Request rate
axes[0].step(time, df["request_rate"], where="post", linewidth=2)
axes[0].set_ylabel("Request Rate\n(req/s)")
axes[0].set_title("HPA Autoscaling Test: 10-Minute Load Pattern")
axes[0].grid(True, alpha=0.3)

# Graph 2: CPU utilization
axes[1].plot(time, df["cpu_utilization_percent"],
             marker="o", markersize=3, linewidth=2)
axes[1].set_ylabel("Average CPU\nUtilization (%)")
axes[1].grid(True, alpha=0.3)

# Graph 3: Web replicas
axes[2].step(time, df["replicas"], where="post",
             marker="o", markersize=3, linewidth=2)
axes[2].set_ylabel("Web Replicas")
axes[2].set_xlabel("Elapsed Time (seconds)")
axes[2].set_yticks(range(1, 6))
axes[2].grid(True, alpha=0.3)

# Mark phase transitions
for ax in axes:
    ax.axvline(120, linestyle="--", alpha=0.6)
    ax.axvline(420, linestyle="--", alpha=0.6)
    ax.set_xlim(0, 600)

axes[0].text(60, 1.02, "Low Load", transform=axes[0].get_xaxis_transform(),
             ha="center")
axes[0].text(270, 1.02, "High Load", transform=axes[0].get_xaxis_transform(),
             ha="center")
axes[0].text(510, 1.02, "Recovery", transform=axes[0].get_xaxis_transform(),
             ha="center")

plt.tight_layout()
plt.savefig("results/graphs/graph3_autoscaling.png",
            dpi=300, bbox_inches="tight")
print("Graph 3 saved: results/graphs/graph3_autoscaling.png")
plt.show()
