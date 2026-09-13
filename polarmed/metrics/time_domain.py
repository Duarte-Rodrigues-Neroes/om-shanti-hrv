"""Time-domain HRV.

Written out rather than delegated, because these are the study's actual claims
and being able to test each against an analytically known value is worth more
than the dependency (PLAN.md section 4.14).
"""

from __future__ import annotations

import numpy as np


def mean_rr(rr_ms: np.ndarray) -> float:
    return float(np.mean(rr_ms)) if rr_ms.size else float("nan")


def mean_hr(rr_ms: np.ndarray) -> float:
    """Mean instantaneous heart rate.

    The mean of 60000/RR, not 60000 divided by the mean RR: the two differ by
    Jensen's inequality, and the former is what "mean heart rate" denotes.
    """
    return float(np.mean(60000.0 / rr_ms)) if rr_ms.size else float("nan")


def sdnn(rr_ms: np.ndarray) -> float:
    """Standard deviation of the intervals (population form, ddof=0)."""
    return float(np.std(rr_ms, ddof=0)) if rr_ms.size >= 2 else float("nan")


def rmssd(rr_ms: np.ndarray) -> float:
    """Root mean square of successive differences."""
    if rr_ms.size < 2:
        return float("nan")
    diffs = np.diff(rr_ms)
    return float(np.sqrt(np.mean(diffs**2)))


def pnn50(rr_ms: np.ndarray) -> float:
    """Percentage of successive intervals differing by more than 50 ms."""
    if rr_ms.size < 2:
        return float("nan")
    diffs = np.abs(np.diff(rr_ms))
    return float(100.0 * np.mean(diffs > 50.0))


def cvnn(rr_ms: np.ndarray) -> float:
    """SDNN normalised by mean RR - comparable across different heart rates."""
    mean = mean_rr(rr_ms)
    if not np.isfinite(mean) or mean == 0:
        return float("nan")
    return float(sdnn(rr_ms) / mean)


def poincare(rr_ms: np.ndarray) -> tuple[float, float, float]:
    """Poincare descriptors ``(SD1, SD2, SD1/SD2)``.

    SD1 is the short-term scatter perpendicular to the line of identity and is
    an algebraic restatement of RMSSD; SD2 is the long-term scatter.
    """
    if rr_ms.size < 3:
        return float("nan"), float("nan"), float("nan")
    sd_sd = float(np.std(np.diff(rr_ms), ddof=0))
    sd1 = sd_sd / np.sqrt(2.0)
    variance = float(np.var(rr_ms, ddof=0))
    sd2_squared = 2.0 * variance - 0.5 * sd_sd**2
    sd2 = float(np.sqrt(sd2_squared)) if sd2_squared > 0 else float("nan")
    ratio = sd1 / sd2 if sd2 and np.isfinite(sd2) and sd2 != 0 else float("nan")
    return float(sd1), sd2, float(ratio)


def summarise(rr_ms: np.ndarray) -> dict[str, float]:
    """All time-domain metrics for one segment."""
    sd1, sd2, ratio = poincare(rr_ms)
    hr = 60000.0 / rr_ms if rr_ms.size else np.array([])
    return {
        "n_beats": int(rr_ms.size),
        "mean_RR": mean_rr(rr_ms),
        "mean_HR": mean_hr(rr_ms),
        "min_HR": float(np.min(hr)) if hr.size else float("nan"),
        "max_HR": float(np.max(hr)) if hr.size else float("nan"),
        "SDNN": sdnn(rr_ms),
        "RMSSD": rmssd(rr_ms),
        "pNN50": pnn50(rr_ms),
        "CVNN": cvnn(rr_ms),
        "SD1": sd1,
        "SD2": sd2,
        "SD1_SD2": ratio,
    }
