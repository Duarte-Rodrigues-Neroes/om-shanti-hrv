"""Parsers for the verified export format (PLAN.md section 2.3).

Three files per measurement:

* ``rr_intervals.csv``  - ``seq,rr_ms,timestamp_ms``, timestamps cumulative from 0
* ``ecg_raw.csv``       - ``seq,voltage_uv,timestamp_ms``, 130 Hz
* ``metrics.json``      - metadata plus the app's own HRV values

The app's HRV values are read for cross-checking only and never become a
published result: they are computed over at most the first 1000 beats, which on
a 42-minute recording is the first twelve minutes and nothing else.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from polarmed.io.timestamps import combine_session_datetime, estimate_sampling_rate_hz
from polarmed.models import AppMetrics, ParsedSignal, SignalType, TimestampKind

APP_METRIC_KEYS = (
    "n_rr",
    "mean_rr",
    "hr_resting_mean",
    "hr_min",
    "hr_max",
    "sdnn",
    "rmssd",
    "lnrmssd",
    "pnn50",
    "data_quality_pct",
)


@dataclass(frozen=True, slots=True)
class Measurement:
    """One band x date x measurement folder, fully parsed."""

    band_id: str
    session_date: str
    measurement: str
    app: AppMetrics
    rr: ParsedSignal | None
    ecg: ParsedSignal | None
    source_dir: Path

    @property
    def key(self) -> str:
        return f"{self.band_id}/{self.session_date}/{self.measurement}"

    @property
    def stated_duration_s(self) -> float:
        return float(self.app.duration_s or 0.0)


def parse_metrics_json(path: Path) -> AppMetrics:
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = payload.get("metadata", {})
    hrv = payload.get("hrv_metrics", {})
    values = {
        key: float(hrv[key])
        for key in APP_METRIC_KEYS
        if isinstance(hrv.get(key), (int, float))
    }
    return AppMetrics(
        session_id=meta.get("session_id"),
        participant_code=meta.get("participant_code"),
        session_date=meta.get("session_date"),
        session_time=meta.get("session_time"),
        session_type=meta.get("session_type"),
        duration_s=meta.get("duration_s"),
        has_ecg=meta.get("has_ecg"),
        ecg_samples=meta.get("ecg_samples"),
        n_rr_raw=meta.get("n_rr_raw"),
        values=values,
    )


def parse_rr_csv(path: Path, t0) -> ParsedSignal:
    frame = pd.read_csv(path)
    missing = {"rr_ms", "timestamp_ms"} - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing column(s) {sorted(missing)}")

    frame = frame.dropna(subset=["rr_ms", "timestamp_ms"])
    rr = frame["rr_ms"].to_numpy(dtype=np.float64)
    stamps = frame["timestamp_ms"].to_numpy(dtype=np.float64)

    order = np.argsort(stamps, kind="stable")
    return ParsedSignal(
        signal_type=SignalType.RR,
        values=rr[order],
        timestamps_ms=stamps[order],
        fs_estimated_hz=None,  # RR is irregularly sampled by construction
        timestamp_kind=TimestampKind.RELATIVE_MS,
        t0_utc=t0,
    )


def parse_ecg_csv(path: Path, t0) -> ParsedSignal:
    frame = pd.read_csv(path)
    missing = {"voltage_uv", "timestamp_ms"} - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing column(s) {sorted(missing)}")

    frame = frame.dropna(subset=["voltage_uv", "timestamp_ms"])
    volts = frame["voltage_uv"].to_numpy(dtype=np.float64)
    stamps = frame["timestamp_ms"].to_numpy(dtype=np.float64)

    return ParsedSignal(
        signal_type=SignalType.ECG,
        values=volts,
        timestamps_ms=stamps,
        fs_estimated_hz=estimate_sampling_rate_hz(stamps),
        timestamp_kind=TimestampKind.RELATIVE_MS,
        t0_utc=t0,
    )


def load_measurement(folder: Path, load_ecg: bool = False) -> Measurement:
    """Parse one measurement folder, degrading rather than raising.

    A missing or unreadable component yields ``None`` for that signal; the
    caller decides whether the measurement is still usable.
    """
    metrics_path = folder / "metrics.json"
    app = (
        parse_metrics_json(metrics_path)
        if metrics_path.exists()
        else AppMetrics(None, None, None, None, None, None, None, None, None)
    )
    t0 = combine_session_datetime(app.session_date, app.session_time)

    rr = None
    rr_path = folder / "rr_intervals.csv"
    if rr_path.exists():
        rr = parse_rr_csv(rr_path, t0)

    ecg = None
    ecg_path = folder / "ecg_raw.csv"
    if load_ecg and ecg_path.exists():
        ecg = parse_ecg_csv(ecg_path, t0)

    return Measurement(
        band_id=folder.parts[-3],
        session_date=folder.parts[-2],
        measurement=folder.parts[-1],
        app=app,
        rr=rr,
        ecg=ecg,
        source_dir=folder,
    )


def discover_measurements(root: Path) -> list[Path]:
    """Every folder holding an ``rr_intervals.csv``, sorted for determinism."""
    return sorted({p.parent for p in root.glob("*/*/*/rr_intervals.csv")})
