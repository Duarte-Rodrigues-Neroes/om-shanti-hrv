"""Time-resolved metrics and the onset detector.

The detector's job in this study is not to find an onset but to make an
invisible assumption checkable: if the slow rhythm is already present at the
start, the honest answer is a low confidence, not a spurious time.
"""

from __future__ import annotations

import numpy as np
import pytest

from polarmed.config import load_config
from polarmed.metrics.sliding import detect_onset_s, sliding_metrics


@pytest.fixture(scope="module")
def spectral_config():
    return load_config().spectral


def tachogram(freq_of_time, duration_s=1800.0, amplitude_ms=60.0, mean_rr=800.0):
    """Build an RR series whose modulation frequency varies with time."""
    times, values, clock = [], [], 0.0
    phase = 0.0
    while clock < duration_s:
        freq = freq_of_time(clock)
        phase += 2 * np.pi * freq * (mean_rr / 1000.0)
        rr = mean_rr + amplitude_ms * np.sin(phase)
        times.append(clock)
        values.append(rr)
        clock += rr / 1000.0
    return np.asarray(values), np.asarray(times)


class TestSlidingMetrics:
    def test_produces_one_value_per_window(self, spectral_config):
        rr, t = tachogram(lambda _: 0.25, duration_s=600.0)
        series = sliding_metrics(rr, t, spectral_config, window_s=120.0, step_s=30.0)
        assert series.t_centre_s.size == series.rmssd.size == series.peak_freq_hz.size
        assert series.t_centre_s.size > 5

    def test_tracks_a_constant_breathing_rate(self, spectral_config):
        rr, t = tachogram(lambda _: 0.25, duration_s=900.0)
        series = sliding_metrics(rr, t, spectral_config)
        peaks = series.peak_freq_hz[np.isfinite(series.peak_freq_hz)]
        assert np.median(peaks) == pytest.approx(0.25, abs=0.02)

    def test_follows_a_change_in_breathing_rate(self, spectral_config):
        """0.25 Hz for 15 min, then 0.10 Hz - the transition the study looks for."""
        rr, t = tachogram(lambda s: 0.25 if s < 900 else 0.10, duration_s=1800.0)
        series = sliding_metrics(rr, t, spectral_config)
        early = series.peak_freq_hz[series.t_centre_s < 700]
        late = series.peak_freq_hz[series.t_centre_s > 1100]
        assert np.nanmedian(early) > np.nanmedian(late)
        assert np.nanmedian(late) == pytest.approx(0.10, abs=0.03)

    def test_too_short_a_series_returns_empty(self, spectral_config):
        assert sliding_metrics(np.full(5, 800.0), np.arange(5.0), spectral_config).rmssd.size == 0


class TestOnsetDetection:
    def test_finds_a_step_into_slow_breathing(self, spectral_config):
        rr, t = tachogram(lambda s: 0.25 if s < 600 else 0.10, duration_s=1800.0)
        series = sliding_metrics(rr, t, spectral_config)
        onset, confidence = detect_onset_s(series)
        assert np.isfinite(onset)
        assert onset == pytest.approx(600.0, abs=180.0)
        assert confidence > 1.0

    def test_reports_low_confidence_when_the_rhythm_never_changes(self, spectral_config):
        """The case that actually occurred in the real recordings.

        A slow rhythm present from the start must not be reported as an onset
        with high confidence - that would manufacture a transition that never
        happened.
        """
        rr, t = tachogram(lambda _: 0.10, duration_s=1800.0)
        series = sliding_metrics(rr, t, spectral_config)
        _, confidence = detect_onset_s(series)
        assert confidence < 2.0

    def test_empty_series_yields_nan_not_zero(self, spectral_config):
        series = sliding_metrics(np.full(5, 800.0), np.arange(5.0), spectral_config)
        onset, confidence = detect_onset_s(series)
        assert np.isnan(onset)
        assert confidence == 0.0

    def test_the_statistic_is_a_ratio_so_overall_hrv_does_not_move_it(
        self, spectral_config
    ):
        """Scaling a person's whole HRV must not change the statistic.

        This is why the detector uses a ratio rather than absolute slow-band
        power: that power varies by an order of magnitude between people, and an
        absolute threshold would need calibrating per participant (PLAN.md 4.4).

        The signal must carry broadband noise as well as the slow wave. A pure
        tone has essentially no HF content, so its HF band is numerical leakage
        that does not scale with amplitude - and the ratio would look
        amplitude-dependent for a reason that has nothing to do with the
        statistic.
        """
        rng = np.random.default_rng(23)
        base_rr, t = tachogram(lambda _: 0.10, amplitude_ms=1.0, duration_s=900.0)
        wave = base_rr - 800.0  # unit-amplitude slow wave
        noise = rng.normal(0, 1.0, wave.size)  # same noise for both

        def ratio(scale: float) -> float:
            rr = 800.0 + scale * (60.0 * wave + 12.0 * noise)
            series = sliding_metrics(rr, t, spectral_config)
            return float(np.nanmedian(series.slow_ratio_log))

        assert ratio(2.0) == pytest.approx(ratio(0.5), abs=0.25)
