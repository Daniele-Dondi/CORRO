import numpy as np
import scipy.signal as signal
#import scipy.integrate# as integral
from scipy import integrate

# Load the chromatogram data
def load_data(file_path):
    data = np.loadtxt(file_path)
    x = data[:, 0]  # Time or retention factor
    y = data[:, 1]  # Intensity
    return x, y

# Detect peaks
def detect_peaks(x, y, height=None, prominence=None):
    peaks, _ = signal.find_peaks(y, height=height, prominence=prominence)
    return peaks

# Calculate area under peaks
def calculate_area(x, y, peaks):
    areas = {}
    for peak in peaks:
        left_idx = max(0, peak - 5)
        right_idx = min(len(x) - 1, peak + 5)
        area = integrate.trapezoid(y[left_idx:right_idx], x[left_idx:right_idx])
        areas[x[peak]] = area
    return areas

# Main function
def main(file_path):
    x, y = load_data(file_path)
    peaks = detect_peaks(x, y, height=80, prominence=20)  # Adjust params as needed
    areas = calculate_area(x, y, peaks)

    print("Detected peaks and their areas:")
    for peak_pos, area in areas.items():
        print(f"Peak at {peak_pos:.2f}, Area: {area:.2f}")

# Example usage
file_path = "chromatogram.txt"  # Replace with your actual file path
main(file_path)
