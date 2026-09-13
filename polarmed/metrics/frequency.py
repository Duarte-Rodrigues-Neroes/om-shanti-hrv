"""Frequency-domain HRV.

Two decisions from PLAN.md are enforced here rather than left to library
defaults, because they *are* the methodology:

* **Identical windowing in every phase** (section 4.3). A 60 s Hann window with
  50 % overlap gives five segments in a three-minute window and dozens in a
  long one, but the estimator is the same on both sides of the contrast. VLF is
  not reported: it would need windows of five minutes or more.
* **Zero-padding plus parabolic interpolation for the peak** (section 4.3b).
  With 60 s windows the bin spacing is 0.0167 Hz, so 0.100 Hz and 0.117 Hz land
  in adjacent bins and a peak-frequency trace comes out as a staircase. Padding
  to 1024 points and interpolating over the three bins around the maximum gives
  a sub-bin reading. This improves the *resolution of the reading*, not the
  spectral resolution, which the window length still governs.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal import welch

from polarmed.config import SpectralConfig


def resample_uniform(
    rr_ms: np.ndarray, t_s: np.ndarray, fs_hz: float
) -> tuple[np.ndarray, np.ndarray]:
    """Cubic-interpolate the tachogram onto a uniform grid.

    Spectral estimation needs even sampling, and the RR series is by definition
    sampled at the beats themselves.
    """
    if rr_ms.size < 4:
        return np.array([]), np.array([])
    t_rel = t_s - t_s[0]
    grid = np.arange(0.0, float(t_rel[-1]), 1.0 / fs_hz)
    if grid.size < 8:
        return np.array([]), np.array([])
    spline = CubicSpline(t_rel, rr_ms, extrapolate=False)
    values = spline(grid)
    ok = np.isfinite(values)
    return grid[ok], values[ok]


def parabolic_peak(freqs: np.ndarray, power: np.ndarray, lo: float, hi: float) -> float:
    """Sub-bin peak frequency inside ``[lo, hi]`` by parabolic interpolation."""
    band = (freqs >= lo) & (freqs <= hi)
    if band.sum() < 3:
        return float("nan")
    idx_local = int(np.argmax(power[band]))
    idx = int(np.flatnonzero(band)[idx_local])
    if idx <= 0 or idx >= freqs.size - 1:
        return float(freqs[idx])

    y0, y1, y2 = power[idx - 1], power[idx], power[idx + 1]
    denominator = y0 - 2.0 * y1 + y2
    if denominator == 0:
        return float(freqs[idx])
    offset = 0.5 * (y0 - y2) / denominator
    offset = float(np.clip(offset, -1.0, 1.0))
    return float(freqs[idx] + offset * (freqs[1] - freqs[0]))


def spectrum(
    rr_ms: np.ndarray, t_s: np.ndarray, config: SpectralConfig, fs_hz: float = 4.0
) -> tuple[np.ndarray, np.ndarray, int]:
    """Welch PSD of the tachogram, in ms^2/Hz. Returns ``(freqs, psd, n_segments)``."""
    grid, values = resample_uniform(rr_ms, t_s, fs_hz)
    if grid.size < 16:
        return np.array([]), np.array([]), 0

    nperseg = int(round(config.window_s * fs_hz))
    if nperseg > values.size:
        nperseg = int(values.size)
    if nperseg < 16:
        return np.array([]), np.array([]), 0

    noverlap = int(nperseg * config.overlap)
    step = nperseg - noverlap
    n_segments = 1 + max(0, (values.size - nperseg) // step) if step > 0 else 1

    freqs, psd = welch(
        values - np.mean(values),
        fs=fs_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=max(config.nfft, nperseg),
        detrend=config.detrend,
        scaling="density",
    )
    return freqs, psd, int(n_segments)


def band_power(freqs: np.ndarray, psd: np.ndarray, lo: float, hi: float) -> float:
    band = (freqs >= lo) & (freqs < hi)
    if not band.any():
        return float("nan")
    return float(np.trapezoid(psd[band], freqs[band]))


def summarise(
    rr_ms: np.ndarray, t_s: np.ndarray, config: SpectralConfig, fs_hz: float = 4.0
) -> dict[str, float]:
    """Band powers, the slow-breathing signature, and spectral concentration."""
    freqs, psd, n_segments = spectrum(rr_ms, t_s, config, fs_hz)
    empty = {
        "LF_abs": float("nan"),
        "HF_abs": float("nan"),
        "SLOW_abs": float("nan"),
        "LF_nu": float("nan"),
        "HF_nu": float("nan"),
        "LF_HF": float("nan"),
        "SLOW_rel": float("nan"),
        "total_power": float("nan"),
        "slow_peak_freq_hz": float("nan"),
        "peak_freq_hz": float("nan"),
        "spectral_concentration": float("nan"),
        "n_welch_segments": 0,
        "welch_window_s": config.window_s,
    }
    if freqs.size == 0:
        return empty

    slow_lo, slow_hi = config.bands["SLOW"]
    lf_lo, lf_hi = config.bands["LF"]
    hf_lo, hf_hi = config.bands["HF"]

    lf = band_power(freqs, psd, lf_lo, lf_hi)
    hf = band_power(freqs, psd, hf_lo, hf_hi)
    slow = band_power(freqs, psd, slow_lo, slow_hi)
    total = band_power(freqs, psd, lf_lo, hf_hi)

    lf_hf_sum = lf + hf
    peak = parabolic_peak(freqs, psd, lf_lo, hf_hi)

    # How concentrated is the spectrum around its dominant peak? During
    # collective chanting the breathing rhythm is imposed and near-identical
    # breath to breath, so the power collapses towards a single line.
    concentration = float("nan")
    if np.isfinite(peak) and np.isfinite(total) and total > 0:
        concentration = band_power(freqs, psd, peak - 0.02, peak + 0.02) / total

    return {
        "LF_abs": lf,
        "HF_abs": hf,
        "SLOW_abs": slow,
        "LF_nu": 100.0 * lf / lf_hf_sum if lf_hf_sum > 0 else float("nan"),
        "HF_nu": 100.0 * hf / lf_hf_sum if lf_hf_sum > 0 else float("nan"),
        "LF_HF": lf / hf if hf > 0 else float("nan"),
        "SLOW_rel": slow / total if total > 0 else float("nan"),
        "total_power": total,
        "slow_peak_freq_hz": parabolic_peak(freqs, psd, slow_lo, slow_hi),
        "peak_freq_hz": peak,
        "spectral_concentration": concentration,
        "n_welch_segments": n_segments,
        "welch_window_s": config.window_s,
    }
