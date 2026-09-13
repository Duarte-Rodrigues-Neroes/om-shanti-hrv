"""RR cleaning: plausibility, ectopy detection and the noisy-prefix scan."""

from __future__ import annotations

import numpy as np
import pytest

from polarmed.config import load_config
from polarmed.models import QualityFlag
from polarmed.signal.rr_clean import clean_rr, find_noisy_prefix_s, rolling_median


@pytest.fixture(scope="module")
def rr_config():
    return load_config().rr


def series(rr_ms: np.ndarray) -> np.ndarray:
    """Cumulative beat timestamps in ms, as the export provides them."""
    return np.cumsum(rr_ms)


class TestRollingMedian:
    def test_constant_input_is_unchanged(self):
        values = np.full(20, 800.0)
        assert np.allclose(rolling_median(values, 5), 800.0)

    def test_ignores_an_isolated_spike(self):
        values = np.full(21, 800.0)
        values[10] = 1600.0
        assert rolling_median(values, 5)[10] == pytest.approx(800.0)

    def test_output_length_matches_input(self):
        for n in (1, 5, 17, 100):
            assert rolling_median(np.arange(n, dtype=float), 5).size == n

    def test_empty_input(self):
        assert rolling_median(np.array([]), 5).size == 0


class TestPlausibilityFilter:
    def test_drops_intervals_outside_the_physiological_range(self, rr_config):
        rr = np.array([800.0, 250.0, 810.0, 2500.0, 805.0] * 20)
        result = clean_rr(rr, series(rr), rr_config)
        assert result.n_dropped_implausible == 40
        assert result.rr_ms.min() >= rr_config.plausible_min_ms
        assert result.rr_ms.max() <= rr_config.plausible_max_ms

    def test_a_clean_series_loses_nothing(self, rr_config):
        rng = np.random.default_rng(3)
        rr = 800.0 + rng.normal(0, 20, 400)
        result = clean_rr(rr, series(rr), rr_config)
        assert result.n_dropped_implausible == 0
        assert result.pct_corrected < rr_config.quality_good_max_pct
        assert result.quality_flag is QualityFlag.GOOD

    def test_all_implausible_yields_an_excluded_empty_result(self, rr_config):
        rr = np.full(50, 99.0)
        result = clean_rr(rr, series(rr), rr_config)
        assert result.n_beats == 0
        assert result.quality_flag is QualityFlag.EXCLUDED


class TestEctopyDetection:
    def test_flags_a_missed_beat(self, rr_config):
        """A missed beat shows up as roughly double the local interval."""
        rr = np.full(200, 800.0)
        rr[100] = 1600.0
        result = clean_rr(rr, series(rr), rr_config)
        assert result.corrected_mask[100]
        assert result.rr_ms[100] == pytest.approx(800.0, abs=60.0)

    def test_corrected_values_stay_physiological(self, rr_config):
        rng = np.random.default_rng(5)
        rr = 800.0 + rng.normal(0, 25, 300)
        rr[::17] *= 1.9  # scatter missed beats through the series
        result = clean_rr(rr, series(rr), rr_config)
        assert result.rr_ms.min() >= rr_config.plausible_min_ms
        assert result.rr_ms.max() <= rr_config.plausible_max_ms

    def test_a_steady_series_flags_nothing(self, rr_config):
        rr = np.full(300, 750.0)
        assert not clean_rr(rr, series(rr), rr_config).corrected_mask.any()

    def test_a_slow_wave_is_not_mistaken_for_ectopy(self, rr_config):
        """The chanting oscillation is large but smooth - it must survive.

        If the ectopy rule flagged it, cleaning would erase the very signal the
        study is about.
        """
        beats = np.arange(600)
        rr = 800.0 + 120.0 * np.sin(2 * np.pi * beats / 18.0)
        result = clean_rr(rr, series(rr), rr_config)
        assert result.pct_corrected < 5.0


class TestQualityFlags:
    @pytest.mark.parametrize(
        "bad_fraction, expected",
        [(0.0, QualityFlag.GOOD), (0.10, QualityFlag.WARN), (0.30, QualityFlag.EXCLUDED)],
    )
    def test_thresholds_map_to_flags(self, bad_fraction, expected, rr_config):
        rr = np.full(500, 800.0)
        n_bad = int(500 * bad_fraction)
        if n_bad:
            rr[np.linspace(5, 495, n_bad).astype(int)] = 1650.0
        result = clean_rr(rr, series(rr), rr_config)
        assert result.quality_flag is expected

    def test_pct_corrected_counts_dropped_and_interpolated(self, rr_config):
        rr = np.concatenate([np.full(90, 800.0), np.full(10, 5000.0)])
        result = clean_rr(rr, series(rr), rr_config)
        assert result.pct_corrected == pytest.approx(10.0, abs=0.1)


class TestNoisyPrefix:
    def test_a_clean_recording_loses_nothing(self):
        rng = np.random.default_rng(9)
        rr = 800.0 + rng.normal(0, 20, 3000)
        cleaned = clean_rr(rr, series(rr), load_config().rr)
        assert find_noisy_prefix_s(cleaned) == 0.0

    def test_finds_a_noisy_opening(self):
        """Walking at the start produces artefact that must be cut."""
        rng = np.random.default_rng(13)
        noisy = 800.0 + rng.normal(0, 25, 400)
        noisy[::3] *= 1.8  # heavy ectopy for the first few minutes
        calm = 800.0 + rng.normal(0, 20, 2600)
        rr = np.concatenate([noisy, calm])
        cleaned = clean_rr(rr, series(rr), load_config().rr)
        assert find_noisy_prefix_s(cleaned) > 0.0

    def test_too_short_a_series_returns_zero(self):
        rr = np.full(20, 800.0)
        cleaned = clean_rr(rr, series(rr), load_config().rr)
        assert find_noisy_prefix_s(cleaned) == 0.0


def test_cleaned_series_exposes_its_own_summary(rr_config):
    rr = np.full(300, 750.0)
    result = clean_rr(rr, series(rr), rr_config)
    assert result.n_beats == 300
    assert result.mean_hr == pytest.approx(80.0, abs=0.1)
    assert result.duration_s == pytest.approx(299 * 0.75, abs=0.75)
