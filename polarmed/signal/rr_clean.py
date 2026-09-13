"""RR series cleaning (PLAN.md section 5.2).

Three stages, each recorded rather than silently applied:

1. **Plausibility** - drop intervals outside a physiological range.
2. **Ectopy** - flag beats deviating from a local rolling median by more than a
   relative threshold, which catches missed and extra beats without assuming a
   fixed heart rate.
3. **Correction** - cubic interpolation over flagged beats, keeping a mask of
   exactly what was changed.

``pct_corrected`` is the quality number that decides whether a recording enters
the group aggregates.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline

from polarmed.config import RRConfig
from polarmed.models import QualityFlag


@dataclass(frozen=True, slots=True)
class CleanedRR:
    """A cleaned RR series with a full record of what was changed."""

    rr_ms: np.ndarray  # corrected intervals
    t_s: np.ndarray  # cumulative beat time, seconds from recording start
    corrected_mask: np.ndarray  # True where the value was interpolated
    n_dropped_implausible: int
    pct_corrected: float
    quality_flag: QualityFlag

    @property
    def n_beats(self) -> int:
        return int(self.rr_ms.size)

    @property
    def duration_s(self) -> float:
        return float(self.t_s[-1] - self.t_s[0]) if self.t_s.size > 1 else 0.0

    @property
    def mean_hr(self) -> float:
        return float(60000.0 / np.mean(self.rr_ms)) if self.rr_ms.size else float("nan")


def rolling_median(values: np.ndarray, window: int) -> np.ndarray:
    """Centred rolling median with edge padding.

    Written out rather than taken from pandas so the edge behaviour is explicit:
    the first and last beats are compared against the nearest full window rather
    than against a shrinking one, which would make them spuriously self-similar.
    """
    if values.size == 0:
        return values.copy()
    half = max(1, window // 2)
    padded = np.pad(values, half, mode="edge")
    strided = np.lib.stride_tricks.sliding_window_view(padded, 2 * half + 1)
    return np.median(strided, axis=1)[: values.size]


def clean_rr(
    rr_ms: np.ndarray, timestamps_ms: np.ndarray, config: RRConfig
) -> CleanedRR:
    """Apply plausibility filtering, ectopy detection and cubic correction."""
    rr = np.asarray(rr_ms, dtype=np.float64)
    stamps = np.asarray(timestamps_ms, dtype=np.float64)

    plausible = (rr >= config.plausible_min_ms) & (rr <= config.plausible_max_ms)
    n_dropped = int((~plausible).sum())
    rr = rr[plausible]
    stamps = stamps[plausible]

    if rr.size == 0:
        return CleanedRR(
            rr_ms=rr,
            t_s=stamps / 1000.0,
            corrected_mask=np.zeros(0, dtype=bool),
            n_dropped_implausible=n_dropped,
            pct_corrected=100.0,
            quality_flag=QualityFlag.EXCLUDED,
        )

    # Ectopy: relative deviation from the local rolling median.
    local = rolling_median(rr, config.ectopic_median_window_beats)
    with np.errstate(divide="ignore", invalid="ignore"):
        deviation = np.abs(rr - local) / np.where(local > 0, local, np.nan)
    ectopic = np.nan_to_num(deviation, nan=0.0) > config.ectopic_rel_threshold

    corrected = rr.copy()
    if ectopic.any() and (~ectopic).sum() >= 4:
        good_idx = np.flatnonzero(~ectopic)
        spline = CubicSpline(good_idx, rr[good_idx], extrapolate=True)
        corrected[ectopic] = spline(np.flatnonzero(ectopic))
        # Interpolation can overshoot; keep the result physiological.
        corrected = np.clip(corrected, config.plausible_min_ms, config.plausible_max_ms)
    elif ectopic.any():
        # Too few clean beats to interpolate against - fall back to the median.
        corrected[ectopic] = float(np.median(rr[~ectopic])) if (~ectopic).any() else np.nan

    total_touched = n_dropped + int(ectopic.sum())
    denominator = n_dropped + rr.size
    pct = 100.0 * total_touched / denominator if denominator else 100.0

    if pct < config.quality_good_max_pct:
        flag = QualityFlag.GOOD
    elif pct <= config.quality_warn_max_pct:
        flag = QualityFlag.WARN
    else:
        flag = QualityFlag.EXCLUDED

    return CleanedRR(
        rr_ms=corrected,
        t_s=stamps / 1000.0,
        corrected_mask=ectopic,
        n_dropped_implausible=n_dropped,
        pct_corrected=float(pct),
        quality_flag=flag,
    )


def find_noisy_prefix_s(
    cleaned: CleanedRR,
    window_s: float = 60.0,
    step_s: float = 15.0,
    max_scan_s: float = 600.0,
    tolerance: float = 2.0,
) -> float:
    """Find how much of the start to discard, from the data rather than a constant.

    Participants were moving - some walking - at the beginning of the session, so
    the opening minutes carry motion artefact. Rather than cutting a fixed number
    of minutes, slide a window over the correction rate and return the first time
    at which it settles to within ``tolerance`` times the recording's median
    window rate.

    Returns 0.0 when the start is already as clean as the rest, so a well-behaved
    recording loses nothing.
    """
    if cleaned.n_beats < 30:
        return 0.0

    t = cleaned.t_s - cleaned.t_s[0]
    total = float(t[-1])
    scan_end = min(max_scan_s, total * 0.5)
    if scan_end <= window_s:
        return 0.0

    starts = np.arange(0.0, scan_end, step_s)
    rates = []
    for start in starts:
        sel = (t >= start) & (t < start + window_s)
        rates.append(cleaned.corrected_mask[sel].mean() if sel.sum() >= 10 else np.nan)
    rates = np.asarray(rates, dtype=float)

    # Reference: how noisy is the recording once past the scan region?
    baseline = cleaned.corrected_mask[t >= scan_end]
    reference = float(baseline.mean()) if baseline.size >= 30 else 0.0
    threshold = max(reference * tolerance, 0.02)

    settled = np.flatnonzero(np.nan_to_num(rates, nan=np.inf) <= threshold)
    if settled.size == 0:
        return float(scan_end)
    return float(starts[settled[0]])
