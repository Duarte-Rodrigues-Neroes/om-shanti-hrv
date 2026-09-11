"""Timestamp conversion, to the millisecond.

The Polar 2000 epoch is the highest-value test in ingestion: getting it wrong
places every recording in the 1970s while leaving the *relative* spacing intact,
so nothing downstream looks broken.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from polarmed.io.timestamps import (
    POLAR_EPOCH_OFFSET_S,
    classify_epoch_ns,
    combine_session_datetime,
    estimate_sampling_rate_hz,
    polar2000_ns_to_utc,
    polar2000_ns_array_to_unix_s,
    unix_ns_to_utc,
)

NS = 1_000_000_000


def test_polar_epoch_offset_is_exactly_30_years_with_7_leap_days():
    expected = (30 * 365 + 7) * 24 * 3600
    assert POLAR_EPOCH_OFFSET_S == expected
    assert POLAR_EPOCH_OFFSET_S == 946_684_800


def test_polar_zero_is_the_year_2000():
    assert polar2000_ns_to_utc(0) == datetime(2000, 1, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "value_ns, expected",
    [
        (0, datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
        (NS, datetime(2000, 1, 1, 0, 0, 1, tzinfo=timezone.utc)),
        (86_400 * NS, datetime(2000, 1, 2, 0, 0, 0, tzinfo=timezone.utc)),
        # 2026-08-03T20:23:49Z, a plausible session start.
        (839_103_829 * NS, datetime(2026, 8, 3, 20, 23, 49, tzinfo=timezone.utc)),
    ],
)
def test_known_polar_timestamps(value_ns, expected):
    assert polar2000_ns_to_utc(value_ns) == expected


def test_millisecond_precision_is_preserved():
    result = polar2000_ns_to_utc(1_500_000_000)  # 1.5 s after the epoch
    assert result == datetime(2000, 1, 1, 0, 0, 1, 500_000, tzinfo=timezone.utc)


def test_round_trip_through_the_array_helper():
    stamps = np.array([0, NS, 2 * NS], dtype=np.int64)
    unix_s = polar2000_ns_array_to_unix_s(stamps)
    assert unix_s[0] == POLAR_EPOCH_OFFSET_S
    assert np.allclose(np.diff(unix_s), 1.0)


def test_reading_polar_as_unix_would_land_in_the_seventies():
    """Guards the failure mode this module exists to prevent."""
    polar_ns = 835_475_029 * NS
    assert polar2000_ns_to_utc(polar_ns).year == 2026
    assert unix_ns_to_utc(polar_ns).year == 1996  # what the bug would produce


class TestEpochClassification:
    def test_recognises_polar_epoch(self):
        assert classify_epoch_ns(np.array([835_475_029 * NS])) == "polar2000_ns"

    def test_recognises_unix_epoch(self):
        assert classify_epoch_ns(np.array([1_785_000_000 * NS])) == "unix_ns"

    def test_empty_is_unknown(self):
        assert classify_epoch_ns(np.array([], dtype=np.int64)) == "unknown"

    def test_implausible_value_is_unknown(self):
        assert classify_epoch_ns(np.array([12345])) == "unknown"


class TestSessionDatetime:
    def test_combines_date_and_time(self):
        result = combine_session_datetime("2026-08-08", "17:18:03")
        assert result == datetime(2026, 8, 8, 17, 18, 3, tzinfo=timezone.utc)

    @pytest.mark.parametrize(
        "date, time",
        [(None, "17:18:03"), ("2026-08-08", None), (None, None), ("", "")],
    )
    def test_missing_field_yields_none(self, date, time):
        assert combine_session_datetime(date, time) is None

    def test_malformed_input_yields_none_rather_than_raising(self):
        """A bad metrics.json must not abort the run for the other 30 bands."""
        assert combine_session_datetime("08/08/2026", "17:18:03") is None


class TestSamplingRateEstimation:
    def test_estimates_130hz_despite_millisecond_quantisation(self):
        """The verified ECG export: 130 Hz stamped in whole milliseconds.

        Deltas alternate between 7 and 8 ms, so a median-based estimator would
        return 125 or 143 Hz. Only averaging recovers the true rate.
        """
        stamps = np.round(np.arange(0, 1000) * (1000.0 / 130.0))
        assert estimate_sampling_rate_hz(stamps) == pytest.approx(130.0, abs=0.2)

    def test_matches_the_real_export(self):
        """Reproduces the observed file: 3066 samples spanning 23576 ms."""
        stamps = np.round(np.arange(0, 3066) * (1000.0 / 130.0))
        assert estimate_sampling_rate_hz(stamps) == pytest.approx(130.0, abs=0.1)

    def test_a_dropout_is_excluded_not_averaged_in(self):
        """A 40 s Bluetooth gap must not drag the estimate down."""
        clean = np.arange(0, 500) * 8.0
        after_gap = clean + clean[-1] + 40_000
        stamps = np.concatenate([clean, after_gap])
        assert estimate_sampling_rate_hz(stamps) == pytest.approx(125.0, abs=0.5)

    def test_too_few_samples_yields_none(self):
        assert estimate_sampling_rate_hz(np.array([0.0])) is None

    def test_constant_timestamps_yield_none(self):
        assert estimate_sampling_rate_hz(np.zeros(10)) is None
