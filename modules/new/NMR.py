import jcamp
from jcamp import FileParser
import matplotlib.pyplot as plt
import numpy as np

# Parse a JCAMP-DX file
data = FileParser.parse_jcamp("post.dx")
jdx = FileParser.create_jcamp(data)

# Convert to nmrglue format
udic, d = jdx.to_nmrglue_1d()

# Create x-axis in ppm
##xaxis = np.fft.fftshift(np.fft.fftfreq(udic[0]['size'], 1/udic[0]['sw']))[::-1]

def phase_correct(data, p0=0.0, p1=0.0):
    size = len(data)
    ph = np.exp(1j * (p0 + p1 * np.linspace(-0.5, 0.5, size)))
    return np.real(data * ph)

# Apply to FFT result
raw_fft = np.fft.fftshift(np.fft.fft(d))
spectrum = phase_correct(raw_fft, p0=np.pi, p1=0.0)  # Adjust p0 as needed
spectrum = np.real(spectrum)  # or np.abs(spectrum) if phase isn't corrected

# Create x-axis in ppm
size = udic[0]['size']
sw = udic[0]['sw']
obs = udic[0]['obs']
car = udic[0]['car']

xaxis = np.fft.fftshift(np.fft.fftfreq(size, 1/sw))
xaxis = car - xaxis / obs  # Convert to ppm



if udic[0]['car'] != 999.99:
    xaxis += udic[0]['car']
    xaxis /= udic[0]['obs']

plt.figure(figsize=(10, 6))
plt.plot(xaxis, spectrum)
plt.xlabel('Chemical Shift (ppm)')
plt.ylabel('Intensity')
plt.title('NMR Spectrum (Frequency Domain)')
plt.gca().invert_xaxis()
plt.show()

