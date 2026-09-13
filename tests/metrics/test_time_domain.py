"""Time-domain HRV against analytically known values.

Every case here has a value derivable by hand, so a regression shows up as a
wrong number rather than as a plot that merely looks odd.
"""

from __future__ import annotations

import numpy as np
import pytest

from polarmed.metrics.time_domain import (
    cvnn,
    mean_hr,
    mean_rr,
    pnn50,
    poincare,
    rmssd,
    sdnn,
    summarise,
)


class TestRMSSD:
    def test_constant_series_has_zero_variability(self):
        assert rmssd(np.full(100, 800.0)) == 0.0

    def test_known_successive_differences(self):
        # diffs: +100, -100, +100 -> RMS = 100
        rr = np.array([800.0, 900.0, 800.0, 900.0])
        assert rmssd(rr) == pytest.approx(100.0, abs=1e-9)

    def test_alternating_series_equals_half_the_swing(self):
        """A +-d square wave has successive differences of exactly 2d."""
        d = 37.5
        rr = 800.0 + d * np.array([1.0, -1.0] * 50)
        assert rmssd(rr) == pytest.approx(2 * d, abs=1e-9)

    def test_single_beat_is_undefined(self):
        assert np.isnan(rmssd(np.array([800.0])))


class TestSDNN:
    def test_constant_series_has_zero_sd(self):
        assert sdnn(np.full(50, 750.0)) == 0.0

    def test_two_point_series(self):
        # mean 850, deviations +-50 -> population sd = 50
        assert sdnn(np.array([800.0, 900.0])) == pytest.approx(50.0, abs=1e-9)

    def test_matches_numpy_population_sd(self):
        rng = np.random.default_rng(20260913)
        rr = rng.normal(820.0, 45.0, size=500)
        assert sdnn(rr) == pytest.approx(float(np.std(rr, ddof=0)), abs=1e-12)


class TestMeanHR:
    def test_is_the_mean_of_instantaneous_rates_not_the_rate_of_the_mean(self):
        """The two differ by Jensen's inequality; we report the former."""
        rr = np.array([600.0, 1200.0])
        assert mean_hr(rr) == pytest.approx(75.0, abs=1e-9)  # (100 + 50) / 2
        assert 60000.0 / mean_rr(rr) == pytest.approx(66.6667, abs=1e-3)

    def test_one_second_intervals_are_sixty_bpm(self):
        assert mean_hr(np.full(10, 1000.0)) == pytest.approx(60.0, abs=1e-12)


class TestPNN50:
    def test_no_differences_above_threshold(self):
        rr = np.array([800.0, 820.0, 800.0, 830.0])  # diffs 20, 20, 30
        assert pnn50(rr) == 0.0

    def test_all_differences_above_threshold(self):
        rr = np.array([700.0, 900.0, 700.0, 900.0])  # diffs all 200
        assert pnn50(rr) == pytest.approx(100.0)

    def test_exactly_fifty_is_not_counted(self):
        """The definition is *greater than* 50 ms, not at least."""
        assert pnn50(np.array([800.0, 850.0])) == 0.0
        assert pnn50(np.array([800.0, 850.1])) == pytest.approx(100.0)

    def test_half_the_differences(self):
        rr = np.array([800.0, 900.0, 910.0, 1010.0, 1020.0])  # 100, 10, 100, 10
        assert pnn50(rr) == pytest.approx(50.0)


class TestPoincare:
    def test_sd1_tracks_rmssd_over_root_two(self):
        """SD1 = SDSD/sqrt(2), which equals RMSSD/sqrt(2) only when the mean
        successive difference is zero.

        SDSD^2 = mean(d^2) - mean(d)^2, and mean(d) = (last - first)/(n-1), so
        the two coincide only for a series that ends where it began. On real
        data the gap is negligible but not zero, and asserting exact equality
        would be asserting something false.
        """
        rng = np.random.default_rng(7)
        rr = rng.normal(800.0, 40.0, size=400)
        sd1, _, _ = poincare(rr)
        assert sd1 == pytest.approx(rmssd(rr) / np.sqrt(2.0), rel=1e-5)

    def test_sd1_equals_rmssd_over_root_two_when_the_series_returns(self):
        """Construct mean(d) == 0 exactly and the identity becomes exact."""
        rr = np.array([800.0, 900.0, 850.0, 800.0])  # first == last
        sd1, _, _ = poincare(rr)
        assert sd1 == pytest.approx(rmssd(rr) / np.sqrt(2.0), rel=1e-12)

    def test_constant_series_has_no_short_term_scatter(self):
        sd1, sd2, _ = poincare(np.full(50, 800.0))
        assert sd1 == pytest.approx(0.0, abs=1e-12)
        assert np.isnan(sd2) or sd2 == pytest.approx(0.0, abs=1e-9)


class TestCVNN:
    def test_is_sdnn_over_mean(self):
        rr = np.array([800.0, 900.0, 850.0, 870.0])
        assert cvnn(rr) == pytest.approx(sdnn(rr) / mean_rr(rr), rel=1e-12)

    def test_is_scale_invariant(self):
        """Doubling every interval leaves the coefficient of variation alone."""
        rr = np.array([700.0, 800.0, 900.0])
        assert cvnn(rr) == pytest.approx(cvnn(rr * 2.0), rel=1e-12)


class TestSummarise:
    def test_reports_every_expected_key(self):
        result = summarise(np.array([800.0, 850.0, 820.0, 870.0, 810.0]))
        expected = {
            "n_beats", "mean_RR", "mean_HR", "min_HR", "max_HR", "SDNN",
            "RMSSD", "pNN50", "CVNN", "SD1", "SD2", "SD1_SD2",
        }
        assert expected <= set(result)

    def test_min_and_max_hr_bracket_the_mean(self):
        rr = np.array([700.0, 800.0, 900.0, 1000.0])
        result = summarise(rr)
        assert result["min_HR"] <= result["mean_HR"] <= result["max_HR"]

    def test_empty_series_does_not_raise(self):
        """A recording with no usable beats must not abort the whole run."""
        result = summarise(np.array([]))
        assert result["n_beats"] == 0
        assert np.isnan(result["RMSSD"])
