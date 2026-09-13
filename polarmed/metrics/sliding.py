"""Time-resolved HRV and the slow-breathing signature.

This is the analysis that answers the question the segmentation cannot: *when*
does the slow respiratory rhythm appear? With no marker for the start of
chanting, a sliding spectrogram of the tachogram turns an invisible assumption
into a curve that can be looked at (PLAN.md section 4.4).

The detection statistic is a **ratio**, not an absolute power:

    S(t) = log10( P(0.05-0.12 Hz) / P(0.15-0.40 Hz) )

Absolute slow-band power varies by an order of magnitude between people, which
would force a per-subject threshold. The ratio is dimensionless, normalises
against each person's overall HRV amplitude, and measures the thing that
actually happens: respiratory sinus arrhythmia moving out of ~0.25 Hz and into
~0.1 Hz.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from polarmed.config import SpectralConfig
from polarmed.metrics.frequency import band_power, parabolic_peak, spectrum
from polarmed.metrics.time_domain import mean_hr, rmssd, sdnn


@dataclass(frozen=True, slots=True)
class SlidingSeries:
    """One value per window centre, all arrays the same length."""

    t_centre_s: np.ndarray
    rmssd: np.ndarray
    sdnn: np.ndarray
    mean_hr: np.ndarray
    peak_freq_hz: np.ndarray
    slow_rel: np.ndarray
    slow_ratio_log: np.ndarray  # the detection statistic S(t)
    concentration: np.ndarray
    n_beats: np.ndarray


def sliding_metrics(
    rr_ms: np.ndarray,
    t_s: np.ndarray,
    config: SpectralConfig,
    window_s: float = 120.0,
    step_s: float = 10.0,
    min_beats: int = 40,
) -> SlidingSeries:
    """Slide a window over the tachogram, measuring each position."""
    t = np.asarray(t_s, dtype=float)
    t = t - t[0] if t.size else t
    if t.size < min_beats:
        empty = np.array([])
        return SlidingSeries(*([empty] * 9))

    starts = np.arange(0.0, max(t[-1] - window_s, 0.0) + step_s, step_s)
    slow_lo, slow_hi = config.bands["SLOW"]
    hf_lo, hf_hi = config.bands["HF"]
    lf_lo, _ = config.bands["LF"]

    centres, out_rmssd, out_sdnn, out_hr = [], [], [], []
    out_peak, out_slow_rel, out_ratio, out_conc, out_n = [], [], [], [], []

    for start in starts:
        mask = (t >= start) & (t < start + window_s)
        rr_win = rr_ms[mask]
        t_win = t[mask]
        centres.append(start + window_s / 2.0)
        out_n.append(rr_win.size)

        if rr_win.size < min_beats:
            for bucket in (out_rmssd, out_sdnn, out_hr, out_peak,
                           out_slow_rel, out_ratio, out_conc):
                bucket.append(np.nan)
            continue

        out_rmssd.append(rmssd(rr_win))
        out_sdnn.append(sdnn(rr_win))
        out_hr.append(mean_hr(rr_win))

        freqs, psd, _ = spectrum(rr_win, t_win, config)
        if freqs.size == 0:
            out_peak.append(np.nan)
            out_slow_rel.append(np.nan)
            out_ratio.append(np.nan)
            out_conc.append(np.nan)
            continue

        slow = band_power(freqs, psd, slow_lo, slow_hi)
        hf = band_power(freqs, psd, hf_lo, hf_hi)
        total = band_power(freqs, psd, lf_lo, hf_hi)
        peak = parabolic_peak(freqs, psd, lf_lo, hf_hi)

        out_peak.append(peak)
        out_slow_rel.append(slow / total if total and total > 0 else np.nan)
        out_ratio.append(
            float(np.log10(slow / hf)) if slow > 0 and hf > 0 else np.nan
        )
        out_conc.append(
            band_power(freqs, psd, peak - 0.02, peak + 0.02) / total
            if np.isfinite(peak) and total and total > 0
            else np.nan
        )

    return SlidingSeries(
        t_centre_s=np.asarray(centres),
        rmssd=np.asarray(out_rmssd),
        sdnn=np.asarray(out_sdnn),
        mean_hr=np.asarray(out_hr),
        peak_freq_hz=np.asarray(out_peak),
        slow_rel=np.asarray(out_slow_rel),
        slow_ratio_log=np.asarray(out_ratio),
        concentration=np.asarray(out_conc),
        n_beats=np.asarray(out_n),
    )


def detect_onset_s(
    series: SlidingSeries, baseline_s: float = 120.0, k: float = 1.0
) -> tuple[float, float]:
    """Locate a sustained step up in ``slow_ratio_log``.

    Returns ``(onset_seconds, confidence)``. Confidence is the size of the step
    in baseline standard deviations, so a value near zero means "no step found",
    not "onset at time zero".

    The baseline is taken from the opening of the recording, which is exactly the
    assumption under test: if the slow rhythm is already present there, the step
    will be small and the confidence low - and that is the honest answer.
    """
    stat = series.slow_ratio_log
    ok = np.isfinite(stat)
    if ok.sum() < 8:
        return float("nan"), 0.0

    base_mask = ok & (series.t_centre_s <= baseline_s)
    if base_mask.sum() < 3:
        base_mask = ok & (series.t_centre_s <= series.t_centre_s[ok][0] + baseline_s)
    if base_mask.sum() < 3:
        return float("nan"), 0.0

    base_median = float(np.median(stat[base_mask]))
    base_sd = float(np.std(stat[base_mask]))
    threshold = base_median + k * max(base_sd, 0.05)

    # A step must be sustained, not a single noisy window.
    above = ok & (stat > threshold)
    run_needed = 3
    run = 0
    for index in range(stat.size):
        run = run + 1 if above[index] else 0
        if run >= run_needed:
            onset = float(series.t_centre_s[index - run_needed + 1])
            confidence = (
                (float(np.nanmedian(stat[ok & (series.t_centre_s >= onset)])) - base_median)
                / max(base_sd, 0.05)
            )
            return onset, float(confidence)
    return float("nan"), 0.0
