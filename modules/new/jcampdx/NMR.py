import jcamp
from jcamp import FileParser
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.widgets import Slider
from matplotlib.widgets import TextBox
import nmrglue as ng
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
from matplotlib.widgets import Button
from scipy.signal import find_peaks
from scipy.io.wavfile import write as WriteWav

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def PlayFID(d,samplerate=44100,filename="fid_sound"):
    raw_d=d.copy()    
    # Extract real part of FID    
    fid_real = np.real(raw_d)

    # Normalize to 16-bit range
    fid_real /= np.max(np.abs(fid_real))  # scale to [-1, 1]
    fid_int16 = np.int16(fid_real * 32767)

    # Define sample rate (arbitrary, since FID isn't audio — try 44100 Hz)
    sample_rate = samplerate

    # Save as WAV
    if filename[-3:]!=".wav":
        filename+=".wav"
    WriteWav(filename, sample_rate, fid_int16)

def CreateToneFromFID(d,udic,duration=3,sample_rate=44100,filename="tone"):
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
    filename="harmonic_"+filename
    if filename[-3:]!=".wav":
        filename+=".wav"
    WriteWav(filename, sample_rate, tone_int16)

def apodize(fid, sw, lb_hz=1.0):
    """
    Apply exponential apodization (line broadening) in Hz.

    Parameters:
    - fid: 1D numpy array (time-domain signal H(t))
    - sw: spectral width in Hz
    - lb_hz: line broadening in Hz

    Returns:
    - apodized FID
    """
    n = len(fid)
    dwell_time = 1.0 / sw  # seconds per point
    t = np.arange(n) * dwell_time
    window = np.exp(-np.pi * lb_hz * t)
    return fid * window    

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

def LoadFIDandShow(filename,show=True,saveWavFID=False,saveWavHarmonics=False):
##    width, center = extract_nmr_parameters(filename)
##    print(f"Spectral Width: {width} ppm")
##    print(f"Spectral Center: {center} ppm")

    # Parse JCAMP file
    data = FileParser.parse_jcamp(filename)
    jdx = FileParser.create_jcamp(data)

    # Convert to nmrglue format
    udic, d = jdx.to_nmrglue_1d()
    
    if saveWavFID:
        PlayFID(d,samplerate=8000,filename=os.path.basename(filename))
    if saveWavHarmonics:
        CreateToneFromFID(d,udic,filename=os.path.basename(filename))

    # FFT and phase correction
    raw_fft = np.fft.fftshift(np.fft.fft(d))
    spectrum = phase_correct(raw_fft, p0=np.pi, p1=0.0)
    spectrum = np.real(spectrum)

##    # Apply apodization with LB in Hz
##    d_apod = apodize(d, sw=udic[0]['sw'], lb_hz=4.0)
##
##    # FFT and phase correction
##    raw_fft = np.fft.fftshift(np.fft.fft(d_apod))
##    spectrum = phase_correct(raw_fft, p0=np.pi, p1=0.0)
##    spectrum = np.real(spectrum)


    # Create ppm axis
    size = udic[0]['size']
    sw = udic[0]['sw']
    obs_freq = udic[0]['obs']
    center = udic[0]['car']

    xaxis = np.fft.fftshift(np.fft.fftfreq(size, 1/sw))
    if center!= 999.99:
        xaxis += center
        xaxis /= obs_freq
    if show:
        Show(xaxis, spectrum, d, sw)
    else:
        return xaxis, spectrum


def Show_Stacked(X, Y, offset=1000000, labels=None):
    """
    Plots multiple Y-series stacked vertically along a shared X-axis.

    Parameters:
    - X: 1D array of X values (length N)
    - Y_list: list of 1D arrays (each of length N)
    - offset: vertical shift between stacked curves
    - labels: optional list of labels for each series
    """
    X=np.array(X)
    Y=np.array(Y)    
    plt.figure(figsize=(10, 6))
##    # Overlay each dataset
##    for i in range(X.shape[0]):
##        plt.plot(X[i], Y[i]+i*offset, label=f"Dataset {i+1}")
    plt.stackplot(X[0], Y)
    plt.gca().invert_xaxis()
##    for i, Y in enumerate(Y):
##        shift = i * offset
##        label = labels[i] if labels and i < len(labels) else f"Series {i+1}"
##        plt.plot(X[i], Y + shift, label=label)

    plt.xlabel("X")
    plt.ylabel("Stacked Intensity")
    plt.title("Stacked Plot of Multiple Series")
    #plt.legend(loc='upper right', fontsize='small')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    

def Show_Overlay(X,Y):
    X=np.array(X)
    Y=np.array(Y)
    # Validate shapes
    if X.shape != Y.shape:
        raise ValueError(f"Shape mismatch: X{X.shape} and Y{Y.shape} must match.")

    # Create the plot
    plt.figure(figsize=(8, 5))

    # Overlay each dataset
    for i in range(X.shape[0]):
        plt.plot(X[i], Y[i], label=f"Dataset {i+1}")

##    for x in X:
##        for i in range(x.shape[0]):
##            plt.plot(x[i], Y[i], label=f"Dataset {i+1}")
        

    # Add labels, title, legend, and grid
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Overlay Plot of Multiple Datasets")
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()


def plot_xy_lines(X_list, Y_list, xlim=None, invert_x=True):
    """
    Plots multiple XY datasets as connected lines on a shared X-axis scale.

    Parameters:
    - X_list: list of 1D arrays (X values)
    - Y_list: list of 1D arrays (Y values), same length as X_list
    - xlim: optional tuple (xmin, xmax) to fix the X-axis scale
    - invert_x: if True, inverts the X-axis direction
    """
    plt.figure(figsize=(10, 6))
    for i, (x, y) in enumerate(zip(X_list, Y_list)):
        plt.plot(x, y, label=f"Series {i+1}", linewidth=1.5)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("XY Line Plot of Multiple Datasets")
    if xlim:
        plt.xlim(xlim)
    if invert_x:
        plt.gca().invert_xaxis()
    plt.legend(loc='best', fontsize='small')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def Show_Heatmap(X, Y_list, vmin=None, vmax=None, interactive=True):
    """
    Plots a heatmap from a list of Y arrays aligned to a common X axis.

    Parameters:
    - X: 1D array of X values (length N)
    - Y_list: list of 1D arrays (each of length N)
    - vmin, vmax: optional color scale limits
    - interactive: if True, adds sliders to adjust vmin and vmax
    """
    X=np.array(X)
    Y_matrix = np.array(Y_list)  # shape: (n_series, len(X))

    fig, ax = plt.subplots()
    im = ax.imshow(Y_matrix, aspect='auto', extent=[X.min(), X.max(), 0, len(Y_list)],
                   origin='lower', cmap='viridis', vmin=vmin, vmax=vmax)
    plt.colorbar(im, ax=ax, label='Intensity')
    plt.gca().invert_xaxis()
    ax.set_xlabel('X')
    ax.set_ylabel('Series Index')
    ax.set_title('Heatmap of Multiple Series')

    if interactive:
        # Add sliders for vmin and vmax
        ax_vmin = plt.axes([0.25, 0.02, 0.50, 0.02])
        ax_vmax = plt.axes([0.25, 0.06, 0.50, 0.02])
        slider_vmin = Slider(ax_vmin, 'vmin', np.min(Y_matrix), np.max(Y_matrix), valinit=vmin or np.min(Y_matrix))
        slider_vmax = Slider(ax_vmax, 'vmax', np.min(Y_matrix), np.max(Y_matrix), valinit=vmax or np.max(Y_matrix))

        def update(val):
            im.set_clim(slider_vmin.val, slider_vmax.val)
            fig.canvas.draw_idle()

        slider_vmin.on_changed(update)
        slider_vmax.on_changed(update)

    plt.show()
    

def Show(xaxis, spectrum, fid=None, sw=None):
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25, bottom=0.35)

    # Plot spectrum
    line, = ax.plot(xaxis, spectrum, lw=1.5, label='Spectrum', color='blue')
    ax.set_title("Interactive Spectrum with Apodization")
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()
    ax.legend()

    # TextBox for LB in Hz
    axbox = plt.axes([0.25, 0.05, 0.2, 0.05])
    text_box = TextBox(axbox, 'LB (Hz)', initial="1.0")

    # Button to recalc
    ax_button = plt.axes([0.5, 0.05, 0.1, 0.05])
    recalc_button = Button(ax_button, 'Recalc')

    def recalc(event):
        try:
            lb_val = float(text_box.text)
            if fid is not None and sw is not None:
                d_apod = apodize(fid, sw, lb_val)
                raw_fft = np.fft.fftshift(np.fft.fft(d_apod))
                new_spectrum = np.real(phase_correct(raw_fft, p0=np.pi, p1=0.0))
                line.set_ydata(new_spectrum)
                fig.canvas.draw_idle()
        except ValueError:
            print("Invalid LB value")

    recalc_button.on_clicked(recalc)
    plt.show()


##def Show(xaxis, spectrum):
##
##    # Set up interactive plot
##    fig, ax = plt.subplots()
##    plt.subplots_adjust(left=0.25, bottom=0.35)
##
##    # Plot original spectrum (static)
##    original_line, = ax.plot(xaxis, spectrum, lw=1.5, label='Original', color='gray', alpha=0.5)
##
##    # Plot corrected spectrum (dynamic)
##    corrected_line, = ax.plot(xaxis, spectrum, lw=1.5, label='Corrected', color='blue')
##
##    ax.set_title("Interactive savgol Baseline Correction")
##    ax.set_xlabel("Chemical Shift (ppm)")
##    ax.set_ylabel("Intensity")
##    ax.invert_xaxis()
##    ax.legend()
##
##    # Sliders
##    ax_window = plt.axes([0.25, 0.2, 0.65, 0.03])
##    ax_poly = plt.axes([0.25, 0.15, 0.65, 0.03])
##
##    # Button for peak picking
##    ax_button = plt.axes([0.8, 0.05, 0.1, 0.04])
##    peak_button = Button(ax_button, 'Pick Peaks')    
##
##    slider_window = Slider(ax_window, 'Window Length', 5, 1000, valinit=101, valstep=2)
##    slider_poly = Slider(ax_poly, 'Poly Order', 1, 5, valinit=3, valstep=1)
##
##    # Slider for peak detection threshold
##    ax_thresh = plt.axes([0.25, 0.1, 0.5, 0.03])
##    slider_thresh = Slider(ax_thresh, 'Peak Threshold', 0.0001, 0.05, valinit=0.001, valstep=0.0001)    
##
##    def update(val):
##        window = int(slider_window.val)
##        poly = int(slider_poly.val)
##        if window>= len(spectrum):  # Prevent crash
##            return
##        corrected = remove_baseline_savgol(spectrum, window_length=window, polyorder=poly)
##        corrected_line.set_ydata(corrected)
##        fig.canvas.draw_idle()
##
##    def pick_peaks(event):
##        window = int(slider_window.val)
##        poly = int(slider_poly.val)
##        threshold = slider_thresh.val/10
##
##        corrected = remove_baseline_savgol(spectrum, window_length=window, polyorder=poly)
##        peaks, _ = find_peaks(corrected, height=np.max(corrected) * threshold, distance=10)
##
##        # Clear previous peak markers
##        for artist in ax.lines[2:]:  # Assuming first two lines are original and corrected
##            artist.remove()
##
##        # Overlay new peaks
##        ax.plot(xaxis[peaks], corrected[peaks], 'ro', label='Peaks')
##        ax.legend()
##        fig.canvas.draw_idle()  
##
##    slider_window.on_changed(update)
##    slider_poly.on_changed(update)
##
##    peak_button.on_clicked(pick_peaks)
##
##    plt.show()

def ask_mode():
    """Opens a custom dialog with 'Single' and 'Overlay' buttons."""
    # Create a modal dialog window
    dialog = tk.Toplevel(root)
    dialog.title("Choose Mode")
    dialog.geometry("500x120")
    dialog.resizable(False, False)
    dialog.grab_set()  # Make it modal (blocks interaction with main window)

    # Store the result in a mutable object
    result = {"choice": None}

    # Label
    tk.Label(dialog, text="Select mode:", font=("Arial", 12)).pack(pady=10)

    # Button actions
    def choose(choice):
        result["choice"] = choice
        dialog.destroy()

    # Buttons
    tk.Button(dialog, text="Single", width=10, command=lambda: choose("Single")).pack(side="left", padx=20, pady=10)
    tk.Button(dialog, text="Overlay", width=10, command=lambda: choose("Overlay")).pack(side="left", padx=20, pady=10)
    tk.Button(dialog, text="Heatmap", width=10, command=lambda: choose("Heatmap")).pack(side="left", padx=20, pady=10)
    tk.Button(dialog, text="Stacked", width=10, command=lambda: choose("Stacked")).pack(side="left", padx=20, pady=10)
    

    # Wait for the dialog to close
    root.wait_window(dialog)
    return result["choice"]    

def load_FID():
    file_path = filedialog.askopenfilenames(
        title="Select JCAMP File",
        filetypes=[("JCAMP-DX files", "*.dx")]
    )
    
    if file_path:
        Overlay=False
        if len(file_path)>1:
            choice = ask_mode()
            if choice:
                if choice in ["Overlay","Heatmap","Stacked"]:
                    Overlay=True
            else:
                messagebox.showwarning("No Selection", "You closed the dialog without choosing.")
                return
        if Overlay:
            X_arr,Y_arr=[],[]
            for file in file_path:
                X,Y=LoadFIDandShow(file,show=False)
                X_arr.append(X)
                Y_arr.append(Y)
            if choice=="Heatmap":
                Show_Heatmap(X_arr,Y_arr)
            elif choice=="Stacked":
                Show_Stacked(X_arr,Y_arr)
            else:
                plot_xy_lines(X_arr,Y_arr)

        else:
            for file in file_path:
                LoadFIDandShow(file)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("JCAMP viewer")
    root.geometry("300x150")

    load_button = tk.Button(root, text="Load JCAMP File", command=load_FID)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()
