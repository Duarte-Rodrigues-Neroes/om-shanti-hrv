"""Timestamp conversion.

Two clocks matter here and they are easy to confuse:

* The **verified export** (PLAN.md section 2.3) stamps every row in milliseconds
  *relative to the start of that recording*, beginning at 0. Absolute wall-clock
  time exists only in ``metrics.json`` (``session_date`` + ``session_time``).
* The **Polar Sensor Logger** stamps a sensor clock in nanoseconds with its
  epoch at 2000-01-01, which is 30 years off Unix. Reading it as Unix time
  silently places every recording in 1970 and is the kind of bug that survives
  to publication because the *relative* spacing still looks right.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np

# Polar's sensor clock counts from 2000-01-01T00:00:00Z.
POLAR_EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Offset between the two epochs. 30 years spanning 1972..1999, of which
# 1972, 76, 80, 84, 88, 92, 96 are leap years: 7 leap days.
POLAR_EPOCH_OFFSET_S = (POLAR_EPOCH - UNIX_EPOCH).total_seconds()

NS_PER_S = 1_000_000_000
MS_PER_S = 1_000

# A Unix-epoch nanosecond timestamp for any plausible recording date is far
# larger than a Polar-epoch one, which is what lets us tell them apart.
# 2015-01-01 in Unix nanoseconds:
_UNIX_NS_SANITY_FLOOR = 1_420_070_400 * NS_PER_S


def polar2000_ns_to_utc(value_ns: int | float) -> datetime:
    """Convert a Polar sensor timestamp (ns since 2000-01-01) to UTC."""
    seconds = float(value_ns) / NS_PER_S + POLAR_EPOCH_OFFSET_S
    return UNIX_EPOCH + timedelta(seconds=seconds)


def polar2000_ns_array_to_unix_s(values_ns: np.ndarray) -> np.ndarray:
    """Vectorised form, returning seconds since the Unix epoch."""
    return values_ns.astype(np.float64) / NS_PER_S + POLAR_EPOCH_OFFSET_S


def unix_ns_to_utc(value_ns: int | float) -> datetime:
    return UNIX_EPOCH + timedelta(seconds=float(value_ns) / NS_PER_S)


def classify_epoch_ns(values_ns: np.ndarray) -> str:
    """Decide whether a nanosecond column is Polar-epoch or Unix-epoch.

    Returns ``"polar2000_ns"``, ``"unix_ns"`` or ``"unknown"``. The test is
    whether reading the value as Unix time lands in a plausible recording era;
    a Polar timestamp read as Unix lands in the 1970s-90s, far below the floor.
    """
    if values_ns.size == 0:
        return "unknown"
    first = float(values_ns[0])
    if first >= _UNIX_NS_SANITY_FLOOR:
        return "unix_ns"
    # Would it land somewhere sensible once the epoch offset is applied?
    as_unix_s = first / NS_PER_S + POLAR_EPOCH_OFFSET_S
    year_2015 = 1_420_070_400
    year_2100 = 4_102_444_800
    if year_2015 <= as_unix_s <= year_2100:
        return "polar2000_ns"
    return "unknown"


def combine_session_datetime(
    session_date: str | None, session_time: str | None
) -> datetime | None:
    """Build the recording's absolute t0 from ``metrics.json`` fields.

    The export gives local wall-clock date and time with no zone. We attach UTC
    rather than guessing Europe/Lisbon, because the only use of absolute time is
    *relative* comparison between bands recorded in the same room: a constant
    offset applied to every recording cancels out. Guessing a zone would risk a
    one-hour error at a DST boundary that would not cancel.

    Returns ``None`` when either field is missing, which downstream treats as
    "cannot enter the synchrony analysis" rather than as an error.
    """
    if not session_date or not session_time:
        return None
    try:
        return datetime.fromisoformat(f"{session_date}T{session_time}").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def estimate_sampling_rate_hz(
    timestamps_ms: np.ndarray, gap_factor: float = 5.0
) -> float | None:
    """Estimate fs from timestamp deltas, never from a column name.

    Two hazards have to be handled at once, and they pull in opposite
    directions:

    * **Quantisation.** The verified export stamps whole milliseconds, so a
      130 Hz stream (7.6923 ms per sample) alternates between deltas of 7 and 8.
      The *median* of that is exactly 7 or 8, which reads as 143 Hz or 125 Hz -
      never 130. So the median is unusable here.
    * **Dropouts.** A Bluetooth gap inserts one enormous delta, which would drag
      a plain mean far below the true rate.

    So: drop deltas larger than ``gap_factor`` times the median (the dropouts),
    then average what remains (defeating the quantisation). On the real
    3066-sample ECG export this returns 130.005 Hz.
    """
    if timestamps_ms.size < 2:
        return None
    deltas = np.diff(timestamps_ms.astype(np.float64))
    deltas = deltas[deltas > 0]
    if deltas.size == 0:
        return None

    median_delta_ms = float(np.median(deltas))
    if median_delta_ms <= 0:
        return None

    kept = deltas[deltas <= gap_factor * median_delta_ms]
    if kept.size == 0:
        return None

    mean_delta_ms = float(np.mean(kept))
    if mean_delta_ms <= 0:
        return None
    return MS_PER_S / mean_delta_ms
