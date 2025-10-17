##import jcamp
##print(dir(jcamp))

from jcamp import jcamp_read
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


# Replace with your actual file path
data = jcamp_read('pre.dx')

# Inspect the keys and data
print(data.keys())


x = data['x'] # Usually chemical shift (ppm)
y = data['y'] # Intensity

plt.plot(x, y)
plt.xlabel('Chemical Shift (ppm)')
plt.ylabel('Intensity')
plt.title('NMR Spectrum')
plt.gca().invert_xaxis() # NMR spectra usually have decreasing ppm from left to right
plt.show()


peaks, _ = find_peaks(y, height=0.05) # Adjust height threshold as needed
for p in peaks:
    print(f"Peak at {x[p]:.2f} ppm with intensity {y[p]:.2f}")
