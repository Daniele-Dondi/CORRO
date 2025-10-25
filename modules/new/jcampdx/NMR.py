import jcamp
from jcamp import FileParser
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import nmrglue as ng
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
from matplotlib.widgets import Button
from scipy.signal import find_peaks
from scipy.io.wavfile import write

import tkinter as tk
from tkinter import filedialog


def PlayFID(d,samplerate=44100):
    raw_d=d.copy()    
    # Extract real part of FID    
    fid_real = np.real(raw_d)

    # Normalize to 16-bit range
    fid_real /= np.max(np.abs(fid_real))  # scale to [-1, 1]
    fid_int16 = np.int16(fid_real * 32767)

    # Define sample rate (arbitrary, since FID isn't audio — try 44100 Hz)
    sample_rate = samplerate

    # Save as WAV
    write("fid_sound.wav", sample_rate, fid_int16)

def CreateToneFromFID(d,udic,duration=3,sample_rate=44100):
    raw_d=d.copy()

    # FFT of real part of FID
    fft_data = np.fft.fft(np.real(raw_d))
    freqs = np.fft.fftfreq(len(raw_d), d=1/udic[0]['sw'])

    # Get magnitude spectrum
    magnitude = np.abs(fft_data)

    # Find peaks in the frequency domain
    peaks, _ = find_peaks(magnitude, height=np.max(magnitude)*0.1)
    dominant_freqs = freqs[peaks]
    top_indices = np.argsort(magnitude[peaks])[-10:]  # top 10
    harmonics = np.abs(dominant_freqs[top_indices])

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Create additive synthesis from harmonics
    tone = sum(np.sin(2 * np.pi * f * t) for f in harmonics)
    tone /= np.max(np.abs(tone))  # normalize
    tone_int16 = np.int16(tone * 32767)

    # Save as WAV
    write("harmonic_tone.wav", sample_rate, tone_int16)
    

def remove_baseline_savgol(signal, window_length=101, polyorder=3):
    baseline = savgol_filter(signal, window_length, polyorder)
    corrected = signal - baseline
    return corrected

def extract_nmr_parameters(file_path):
    spectral_width = None
    spectral_center = None

    with open(file_path, 'r') as file:
        for line in file:
            if '##$SPECTRAL WIDTH' in line:
                spectral_width = float(line.split('=')[1].strip())
            elif '##$SPECTRALCENTER' in line:
                spectral_center = float(line.split('=')[1].strip())

    return spectral_width, spectral_center

def phase_correct(data, p0=0.0, p1=0.0):
    size = len(data)
    ph = np.exp(1j * (p0 + p1 * np.linspace(-0.5, 0.5, size)))
    return np.real(data * ph)

def LoadFIDandShow(filename):
##    width, center = extract_nmr_parameters(filename)
##    print(f"Spectral Width: {width} ppm")
##    print(f"Spectral Center: {center} ppm")

    # Parse JCAMP file
    data = FileParser.parse_jcamp(filename)
    jdx = FileParser.create_jcamp(data)

    # Convert to nmrglue format
    udic, d = jdx.to_nmrglue_1d()

    PlayFID(d,samplerate=8000)
    CreateToneFromFID(d,udic)

    # FFT and phase correction
    raw_fft = np.fft.fftshift(np.fft.fft(d))
    spectrum = phase_correct(raw_fft, p0=np.pi, p1=0.0)
    spectrum = np.real(spectrum)

    # Create ppm axis
    size = udic[0]['size']
    sw = udic[0]['sw']
    obs_freq = udic[0]['obs']
    center = udic[0]['car']

    xaxis = np.fft.fftshift(np.fft.fftfreq(size, 1/sw))
    if center!= 999.99:
        xaxis += center
        xaxis /= obs_freq

    # Set up interactive plot
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25, bottom=0.35)

    # Plot original spectrum (static)
    original_line, = ax.plot(xaxis, spectrum, lw=1.5, label='Original', color='gray', alpha=0.5)

    # Plot corrected spectrum (dynamic)
    corrected_line, = ax.plot(xaxis, spectrum, lw=1.5, label='Corrected', color='blue')

    ax.set_title("Interactive savgol Baseline Correction")
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()
    ax.legend()

    # Sliders
    ax_window = plt.axes([0.25, 0.2, 0.65, 0.03])
    ax_poly = plt.axes([0.25, 0.15, 0.65, 0.03])

    # Button for peak picking
    ax_button = plt.axes([0.8, 0.05, 0.1, 0.04])
    peak_button = Button(ax_button, 'Pick Peaks')    

    slider_window = Slider(ax_window, 'Window Length', 5, 1000, valinit=101, valstep=2)
    slider_poly = Slider(ax_poly, 'Poly Order', 1, 5, valinit=3, valstep=1)

    # Slider for peak detection threshold
    ax_thresh = plt.axes([0.25, 0.1, 0.5, 0.03])
    slider_thresh = Slider(ax_thresh, 'Peak Threshold', 0.0001, 0.05, valinit=0.001, valstep=0.0001)    

    def update(val):
        window = int(slider_window.val)
        poly = int(slider_poly.val)
        if window>= len(spectrum):  # Prevent crash
            return
        corrected = remove_baseline_savgol(spectrum, window_length=window, polyorder=poly)
        corrected_line.set_ydata(corrected)
        fig.canvas.draw_idle()

    def pick_peaks(event):
        window = int(slider_window.val)
        poly = int(slider_poly.val)
        threshold = slider_thresh.val/10

        corrected = remove_baseline_savgol(spectrum, window_length=window, polyorder=poly)
        peaks, _ = find_peaks(corrected, height=np.max(corrected) * threshold, distance=10)

        # Clear previous peak markers
        for artist in ax.lines[2:]:  # Assuming first two lines are original and corrected
            artist.remove()

        # Overlay new peaks
        ax.plot(xaxis[peaks], corrected[peaks], 'ro', label='Peaks')
        ax.legend()
        fig.canvas.draw_idle()  

    slider_window.on_changed(update)
    slider_poly.on_changed(update)

    peak_button.on_clicked(pick_peaks)

    plt.show()

def load_FID():
    file_path = filedialog.askopenfilename(
        title="Select JCAMP File",
        filetypes=[("JCAMP-DX files", "*.dx")]
    )
    
    if file_path:
        LoadFIDandShow(file_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("JCAMP viewer")
    root.geometry("300x150")

    load_button = tk.Button(root, text="Load JCAMP File", command=load_FID)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()


##import jcamp
##from jcamp import FileParser
##import matplotlib.pyplot as plt
##import numpy as np
##
##def extract_nmr_parameters(file_path):
##    spectral_width = None
##    spectral_center = None
##
##    with open(file_path, 'r') as file:
##        for line in file:
##            if '##$SPECTRAL WIDTH' in line:
##                spectral_width = float(line.split('=')[1].strip())
##            elif '##$SPECTRALCENTER' in line:
##                spectral_center = float(line.split('=')[1].strip())
##
##    return spectral_width, spectral_center
##
##def LoadFIDandShow(filename):
##    
##    width, center = extract_nmr_parameters(filename)
##    print(f"Spectral Width: {width} ppm")
##    print(f"Spectral Center: {center} ppm")
##    
##    # Parse a JCAMP-DX file
##    data = FileParser.parse_jcamp(filename)
##    jdx = FileParser.create_jcamp(data)
##
##    # Convert to nmrglue format
##    udic, d = jdx.to_nmrglue_1d()
##
##    # Create x-axis in ppm
##    ##xaxis = np.fft.fftshift(np.fft.fftfreq(udic[0]['size'], 1/udic[0]['sw']))[::-1]
##
##    def phase_correct(data, p0=0.0, p1=0.0):
##        size = len(data)
##        ph = np.exp(1j * (p0 + p1 * np.linspace(-0.5, 0.5, size)))
##        return np.real(data * ph)
##
##    # Apply to FFT result
##    raw_fft = np.fft.fftshift(np.fft.fft(d))
##    spectrum = phase_correct(raw_fft, p0=np.pi, p1=0.0)  # Adjust p0 as needed
##    spectrum = np.real(spectrum)  # or np.abs(spectrum) if phase isn't corrected
##
##    # Create x-axis in ppm
##    size = udic[0]['size']                  # Number of points
##    sw = udic[0]['sw']                      # Spectral width (in Hz)
##    obs_freq = udic[0]['obs']              # Observation frequency (in MHz)
##    center = udic[0]['car']                 # Spectral center (in ppm)    
##    print(size,sw,obs_freq,center)
##
##    xaxis = np.fft.fftshift(np.fft.fftfreq(size, 1/sw))
##    #xaxis = center - xaxis / obs_freq  # Convert to ppm
##
##
##    if udic[0]['car'] != 999.99:
##        xaxis += udic[0]['car']
##        xaxis /= udic[0]['obs']
##
##    plt.figure(figsize=(10, 6))
##    plt.plot(xaxis, spectrum)
##    plt.xlabel('Chemical Shift (ppm)')
##    plt.ylabel('Intensity')
##    plt.title('NMR Spectrum (Frequency Domain)')
##    plt.gca().invert_xaxis()
##    plt.show()
##
##if __name__ == "__main__":
##    LoadFIDandShow("post.dx")
