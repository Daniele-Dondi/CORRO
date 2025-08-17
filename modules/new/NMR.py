###FIRST EXAMPLE
##
##import numpy as np
##from dataclasses import dataclass
##from typing import Optional, Dict, Any, List
##from scipy.signal import find_peaks, peak_widths, hilbert
##
##
##@dataclass
##class NMRParams:
##    # Input interpretation
##    dwell_time: Optional[float] = None         # seconds per point if no time column
##    use_hilbert: bool = True                   # build analytic signal if FID is real-only
##    # Spectral processing
##    line_broadening_hz: float = 1.0            # exponential apodization (Hz)
##    zero_fill_factor: float = 2.0              # multiply length by this before FFT
##    # Phase
##    auto_phase_zero: bool = True               # auto zero-order phase
##    phi0_deg: float = 0.0                      # override or initial guess (deg)
##    phi1_deg: float = 0.0                      # first-order phase (deg across full spectrum)
##    # Baseline
##    do_baseline_correction: bool = True
##    baseline_lambda: float = 1e5               # AsLS smoothness
##    baseline_p: float = 0.001                  # AsLS asymmetry 0..1
##    # Peak picking
##    prominence: Optional[float] = None         # in spectrum units; if None, auto
##    height: Optional[float] = None             # absolute height threshold; if None, auto
##    distance_points: int = 5                   # minimum distance between peaks
##    rel_width_at_half_max: float = 0.5         # fraction for width calculation
##    # Frequency axis / ppm
##    spectrometer_freq_mhz: Optional[float] = None  # e.g., 400.13 for 1H
##    ref_ppm: Optional[float] = None                # reference ppm (e.g., TMS at 0.0)
##    ref_freq_hz: Optional[float] = None            # absolute reference in Hz (alternative to ref_ppm)
##    # Output
##    n_top_peaks: Optional[int] = None          # limit number of reported peaks
##    # Safety
##    eps: float = 1e-12
##
##
##class NMRProcessor:
##    def __init__(self, params: NMRParams):
##        self.p = params
##
##    def load_fid(self, path: str):
##        data = np.loadtxt(path)
##        if data.ndim == 1:
##            data = data[:, None]
##
##        if data.shape[1] >= 3:
##            t = data[:, 0].astype(float)
##            re = data[:, 1].astype(float)
##            im = data[:, 2].astype(float)
##        elif data.shape[1] == 2:
##            # Assume [real imag]
##            re = data[:, 0].astype(float)
##            im = data[:, 1].astype(float)
##            t = None
##        else:
##            # One column: real only
##            re = data[:, 0].astype(float)
##            im = None
##            t = None
##
##        n = len(re)
##        if t is not None:
##            dt = np.median(np.diff(t))
##        else:
##            if self.p.dwell_time is None:
##                raise ValueError("No time column found. Please provide dwell_time (seconds per point).")
##            dt = float(self.p.dwell_time)
##            t = np.arange(n) * dt
##
##        if im is None:
##            if self.p.use_hilbert:
##                # Build analytic signal for better absorption lines
##                analytic = hilbert(re)
##                re = np.real(analytic)
##                im = np.imag(analytic)
##            else:
##                im = np.zeros_like(re)
##
##        fid = re + 1j * im
##        return t, dt, fid
##
##    def apodize(self, fid: np.ndarray, dt: float):
##        lb = max(self.p.line_broadening_hz, 0.0)
##        if lb <= self.p.eps:
##            return fid
##        n = fid.size
##        t = np.arange(n) * dt
##        w = np.exp(-np.pi * lb * t)  # exponential (Lorentzian) apodization
##        return fid * w
##
##    def zero_fill(self, fid: np.ndarray):
##        zf = max(self.p.zero_fill_factor, 1.0)
##        n = fid.size
##        n_zf = int(2 ** np.ceil(np.log2(n * zf)))  # next power of two
##        if n_zf <= n:
##            return fid
##        out = np.zeros(n_zf, dtype=np.complex128)
##        out[:n] = fid
##        return out
##
##    def fft_spectrum(self, fid: np.ndarray, dt: float):
##        spec = np.fft.fft(fid)
##        spec = np.fft.fftshift(spec)
##        freqs_hz = np.fft.fftshift(np.fft.fftfreq(fid.size, d=dt))
##        return freqs_hz, spec
##
##    def apply_phase(self, spec: np.ndarray, freqs_hz: np.ndarray):
##        # First-order phase ramp
##        phi1 = np.deg2rad(self.p.phi1_deg)
##        # Map frequency to -0.5..0.5 across spectrum for a simple first-order model
##        x = (freqs_hz - freqs_hz.min()) / (freqs_hz.max() - freqs_hz.min() + self.p.eps) - 0.5
##        phase_ramp = np.exp(1j * (phi1 * x))
##
##        # Zero-order phase
##        if self.p.auto_phase_zero:
##            phi0_opt = self._auto_phase_zero(np.real(spec * phase_ramp), np.imag(spec * phase_ramp))
##        else:
##            phi0_opt = np.deg2rad(self.p.phi0_deg)
##
##        phased = spec * phase_ramp * np.exp(1j * phi0_opt)
##        return phased, np.rad2deg(phi0_opt)
##
##    def _auto_phase_zero(self, re: np.ndarray, im: np.ndarray):
##        # Find phi0 minimizing L2 norm of imaginary part of spectrum
##        # Coarse-to-fine grid search is robust and fast
##        def score(phi):
##            c = np.cos(phi)
##            s = np.sin(phi)
##            im_phi = im * c + re * s  # imag after rotation
##            return np.linalg.norm(im_phi)
##
##        # Coarse grid
##        phis = np.deg2rad(np.linspace(-180, 180, 361))
##        vals = np.array([score(p) for p in phis])
##        i = np.argmin(vals)
##        phi_best = phis[i]
##
##        # Local refine
##        for step in [1.0, 0.2]:
##            local = np.deg2rad(np.linspace(np.rad2deg(phi_best) - 5*step,
##                                           np.rad2deg(phi_best) + 5*step, 51))
##            vals = np.array([score(p) for p in local])
##            phi_best = local[np.argmin(vals)]
##        return phi_best
##
##    def baseline_asls(self, y: np.ndarray, lam: float, p: float, n_iter: int = 10):
##        # Eilers & Boelens (2005) asymmetric least squares baseline
##        n = y.size
##        D = np.diff(np.eye(n), 2)
##        W = np.ones(n)
##        for _ in range(n_iter):
##            W_mat = np.diag(W)
##            Z = W_mat + lam * (D.T @ D)
##            b = np.linalg.solve(Z, W * y)
##            W = p * (y > b) + (1 - p) * (y < b)
##        return b
##
##    def to_ppm(self, freqs_hz: np.ndarray):
##        if self.p.spectrometer_freq_mhz is None:
##            return None
##        gamma = self.p.spectrometer_freq_mhz * 1e6  # Hz per ppm unit
##        if self.p.ref_ppm is not None and self.p.ref_freq_hz is None:
##            # Align such that ref_ppm corresponds to ref_freq_hz computed from center = 0 Hz
##            # If center frequency reference unknown, interpret 0 Hz as ref_ppm
##            ppm = (freqs_hz / gamma) + self.p.ref_ppm
##        elif self.p.ref_freq_hz is not None:
##            ppm = (freqs_hz - self.p.ref_freq_hz) / gamma
##        else:
##            ppm = freqs_hz / gamma
##        return ppm
##
##    def detect_peaks_and_integrate(self, x: np.ndarray, y: np.ndarray):
##        # Auto thresholds if not provided
##        y_pos = y - np.percentile(y, 5)
##        y_pos[y_pos < 0] = 0
##        prom = self.p.prominence if self.p.prominence is not None else 0.05 * (np.max(y_pos) - np.min(y_pos) + self.p.eps)
##        height = self.p.height
##
##        idx, props = find_peaks(y, prominence=prom, height=height, distance=self.p.distance_points)
##        if idx.size == 0:
##            return [], {}
##
##        # Peak widths to set integration boundaries
##        results_half = peak_widths(y, idx, rel_height=self.p.rel_width_at_half_max)
##        left_ips, right_ips = results_half[2], results_half[3]
##
##        peaks = []
##        for k, i0 in enumerate(idx):
##            l = int(np.floor(left_ips[k]))
##            r = int(np.ceil(right_ips[k]))
##            l = max(l, 0)
##            r = min(r, len(y) - 1)
##            area = np.trapz(y[l:r+1], x[l:r+1])
##            peaks.append({
##                "index": int(i0),
##                "x": float(x[i0]),
##                "height": float(y[i0]),
##                "left": float(x[l]),
##                "right": float(x[r]),
##                "area": float(area),
##                "prominence": float(props["prominences"][k]),
##                "width_points": float(results_half[0][k]),
##            })
##
##        # Sort by prominence (or area) and optionally limit
##        peaks.sort(key=lambda d: d["prominence"], reverse=True)
##        if self.p.n_top_peaks is not None:
##            peaks = peaks[: self.p.n_top_peaks]
##
##        summary = {
##            "n_peaks": len(peaks),
##            "total_area": float(np.trapz(y, x)),
##        }
##        return peaks, summary
##
##    def process(self, path: str) -> Dict[str, Any]:
##        # 1) Load
##        t, dt, fid = self.load_fid(path)
##
##        # 2) Apodization
##        fid_apod = self.apodize(fid, dt)
##
##        # 3) Zero-fill
##        fid_zf = self.zero_fill(fid_apod)
##
##        # 4) FFT
##        freqs_hz, spec = self.fft_spectrum(fid_zf, dt)
##
##        # 5) Phase
##        spec_phased, phi0_deg = self.apply_phase(spec, freqs_hz)
##
##        # 6) Absorption-mode real spectrum
##        y = np.real(spec_phased)
##
##        # 7) Baseline
##        if self.p.do_baseline_correction:
##            base = self.baseline_asls(y, self.p.baseline_lambda, self.p.baseline_p)
##            y_corr = y - base
##        else:
##            base = np.zeros_like(y)
##            y_corr = y
##
##        # 8) Axes
##        ppm = self.to_ppm(freqs_hz)
##
##        # 9) Peaks & integrals (prefer ppm if available)
##        x = ppm if ppm is not None else freqs_hz
##        peaks, summary = self.detect_peaks_and_integrate(x, y_corr)
##
##        return {
##            "time_s": t,
##            "dwell_time_s": dt,
##            "fid": fid,
##            "fid_processed": fid_zf,
##            "freq_hz": freqs_hz,
##            "ppm": ppm,                      # may be None
##            "spectrum_complex": spec_phased,
##            "spectrum_real": y,
##            "spectrum_real_corrected": y_corr,
##            "baseline": base,
##            "phase_zero_deg": phi0_deg,
##            "phase_first_deg": self.p.phi1_deg,
##            "peaks": peaks,
##            "summary": summary,
##        }
##
##
###USAGE
### pip install numpy scipy
##from pprint import pprint
##
##params = NMRParams(
##    dwell_time=2.5e-4,          # set if your file lacks a time column
##    line_broadening_hz=1.0,
##    zero_fill_factor=2.0,
##    auto_phase_zero=True,
##    phi1_deg=0.0,
##    do_baseline_correction=True,
##    prominence=None,            # auto
##    height=None,                # auto
##    distance_points=8,
##    spectrometer_freq_mhz=400.13,   # set if you want ppm axis
##    ref_ppm=0.0                     # assumes 0 Hz aligns to 0.0 ppm (TMS)
##)
##
##proc = NMRProcessor(params)
##result = proc.process("FID.txt")
##
### Access outputs
##x = result["ppm"] if result["ppm"] is not None else result["freq_hz"]
##y = result["spectrum_real_corrected"]
##
##pprint(result["peaks"])
##print("Detected peaks:", result["summary"]["n_peaks"])

# SECOND PROCEDURE
import numpy as np
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt

def process_fid(path, lb_hz=1.0, zero_fill_factor=2, prominence=0.05):
    # Load data
    data = np.loadtxt(path)
    t_us, re, im = data[:,0], data[:,1], data[:,2]
    t_s = t_us * 1e-6
    dt = np.median(np.diff(t_s))
    fid = re + 1j*im

    # Apodization (Lorentzian)
    apod = np.exp(-np.pi * lb_hz * np.arange(len(fid))*dt)
    fid *= apod

    # Zero‑fill
    n_zf = int(len(fid)*zero_fill_factor)
    fid = np.pad(fid, (0, n_zf-len(fid)), 'constant')

    # FFT
    spec = np.fft.fftshift(np.fft.fft(fid))
    freqs = np.fft.fftshift(np.fft.fftfreq(len(fid), dt))

    # Simple zero‑order phase correction to maximize real signal
    phi0 = np.linspace(-180, 180, 361)
    best_phi = phi0[np.argmax([np.sum(np.real(spec*np.exp(-1j*np.deg2rad(p)))) for p in phi0])]
    spec *= np.exp(-1j*np.deg2rad(best_phi))

    # Real part of spectrum
    y = np.real(spec)

    # Peak detection
    prom_val = prominence * (np.max(y) - np.min(y))
    idx, props = find_peaks(y, prominence=prom_val)
    widths, w_h, left_ips, right_ips = peak_widths(y, idx, rel_height=0.5)

    peaks = []
    for i, p in enumerate(idx):
        l = int(np.floor(left_ips[i]))
        r = int(np.ceil(right_ips[i]))
        area = np.trapz(y[l:r+1], freqs[l:r+1])
        peaks.append({
            'freq_Hz': freqs[p],
            'height': y[p],
            'area': area
        })

    return freqs, y, peaks

# ---- Run it ----
freqs, spectrum, peaks = process_fid("FID.txt")

# Print results
for pk in peaks:
    print(pk)

# Optional plot
import matplotlib.pyplot as plt
plt.plot(freqs, spectrum)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Intensity")
plt.title("NMR Spectrum")
plt.show()

