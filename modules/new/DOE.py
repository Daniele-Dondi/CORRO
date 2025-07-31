import numpy as np
import pandas as pd
from pyDOE2 import fullfact

# Define number of levels per factor
level_counts = [3, 2, 4]  # Temperature, pH, Time

# Generate factorial design
design = fullfact(level_counts)

print(design)

# Define min and max for each factor
min_vals = [40, 5, 15]    # min Temperature, pH, Time
max_vals = [80, 9, 75]    # max Temperature, pH, Time

# Generate scaled levels (even spacing between min and max)
def calculate_levels(min_val, max_val, levels):
    return np.linspace(min_val, max_val, num=levels)

# Create a list of level value arrays
level_values = [calculate_levels(min_vals[i], max_vals[i], level_counts[i]) for i in range(len(level_counts))]

# Map coded levels to actual values
real_values = []
for row in design:
    mapped = [level_values[i][int(row[i])] for i in range(len(row))]
    real_values.append(mapped)

# Create DataFrame for display
df = pd.DataFrame(real_values, columns=["Temperature (°C)", "pH", "Time (min)"])
print(df)


##import numpy as np
##import pandas as pd
##from pyDOE2 import fullfact
##
### Define levels for each factor
##levels = [2, 2, 2]  # Temperature, pH, Time
##
### Generate the full factorial design
##design = fullfact(levels)
##
##print(design)
##
### Scale levels to actual values
##temperature_vals = [50, 70]
##pH_vals = [6, 8]
##time_vals = [30, 60]
##
### Map the coded levels to real values
##real_values = []
##for row in design:
##    t = temperature_vals[int(row[0])]
##    pH = pH_vals[int(row[1])]
##    time = time_vals[int(row[2])]
##    real_values.append([t, pH, time])
##
### Convert to DataFrame for readability
##df = pd.DataFrame(real_values, columns=["Temperature (°C)", "pH", "Time (min)"])
##
### Show the experimental runs
##print(df)
