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

###################################################################
import pandas as pd
from pyDOE2 import pbdesign

# Number of factors
num_factors = 7

# Define min and max values for each factor
min_vals = [10, 20, 5, 100, 1, 50, 8]
max_vals = [30, 40, 15, 200, 5, 70, 12]
factor_names = ["A", "B", "C", "D", "E", "F", "G"]

# Generate Plackett-Burman design matrix (coded -1 and +1)
design_matrix = pbdesign(num_factors)

# Map coded values to actual levels
real_values = []
for row in design_matrix:
    mapped_row = [
        min_vals[i] if val == -1 else max_vals[i] 
        for i, val in enumerate(row)
    ]
    real_values.append(mapped_row)

# Create DataFrame
df_pb = pd.DataFrame(real_values, columns=factor_names)
df_pb.index = [f"Run {i+1}" for i in range(len(df_pb))]

print(df_pb)

print("without libraries")
import itertools

class DesignOfExperiments:
    def __init__(self, level_counts, min_vals, max_vals):
        self.level_counts = level_counts
        self.min_vals = min_vals
        self.max_vals = max_vals
        self.coded_matrix = []
        self.real_matrix = []

    def generate_factorial(self):
        """Generate full factorial matrix using coded levels"""
        self.coded_matrix = list(itertools.product(*[range(levels) for levels in self.level_counts]))
        return self.coded_matrix

    def scale_levels(self):
        """Convert coded levels into real-world values"""
        def scale(min_val, max_val, num_levels):
            return [min_val + i * (max_val - min_val) / (num_levels - 1) for i in range(num_levels)]

        self.level_values = [scale(self.min_vals[i], self.max_vals[i], self.level_counts[i])
                             for i in range(len(self.level_counts))]

        self.real_matrix = [[self.level_values[i][coded] for i, coded in enumerate(row)]
                            for row in self.coded_matrix]
        return self.real_matrix

    def get_design(self):
        if not self.real_matrix:
            self.generate_factorial()
            self.scale_levels()
        return self.real_matrix

# Define design parameters
levels = [3, 2, 4]
min_vals = [40, 5, 15]
max_vals = [80, 9, 75]

# Instantiate and generate design
doe = DesignOfExperiments(levels, min_vals, max_vals)
matrix = doe.get_design()

# Print a few rows
for row in matrix[:5]:
    print(row)

