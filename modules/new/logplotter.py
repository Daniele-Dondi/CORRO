import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Simulated log data with multiple Y-values
data = """2025-10-06 10:55:48.230396\t23044.76\t12.5\t0.003
2025-10-06 10:56:39.960249\t23759.21\t13.1\t0.002
2025-10-06 10:57:31.447845\t22843.12\t12.9\t0.004
2025-10-06 10:58:22.716822\t23740.26\t13.0\t0.003"""

# Load data
df = pd.read_csv(StringIO(data), sep="\t", header=None)
df.columns = ["timestamp"] + [f"value_{i}" for i in range(1, len(df.columns))]
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
axes = [ax]

# Plot first Y-axis
axes[0].plot(df.index, df.iloc[:, 0], color=colors[0], label=df.columns[0])
axes[0].set_ylabel(df.columns[0], color=colors[0])
axes[0].tick_params(axis='y', labelcolor=colors[0])

# Plot additional Y-axes
for i in range(1, df.shape[1]):
    new_ax = ax.twinx()
    new_ax.spines["right"].set_position(("outward", 60 * i))
    new_ax.plot(df.index, df.iloc[:, i], color=colors[i % len(colors)], label=df.columns[i])
    new_ax.set_ylabel(df.columns[i], color=colors[i % len(colors)])
    new_ax.tick_params(axis='y', labelcolor=colors[i % len(colors)])
    axes.append(new_ax)

# Final touches
plt.title("Dynamic Multi-Y Time Series Plot")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
