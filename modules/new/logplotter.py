import pandas as pd
import matplotlib.pyplot as plt

# Load data from a string or file
data = """2025-10-06 10:55:48.230396\t23044.76
2025-10-06 10:56:39.960249\t23759.21
2025-10-06 10:57:31.447845\t22843.12
2025-10-06 11:07:47.635414\t23454.95"""

# Convert to DataFrame
from io import StringIO
df = pd.read_csv(StringIO(data), sep="\t", header=None, names=["timestamp", "value"])
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Plot
plt.figure(figsize=(10, 5))
plt.plot(df["timestamp"], df["value"], marker='o')
plt.title("Time Series Plot")
plt.xlabel("Timestamp")
plt.ylabel("Value")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
