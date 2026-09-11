"""Data contracts (PLAN.md section 6).

Frozen dataclasses for what circulates in memory; Pydantic only at the
boundaries where untrusted input is validated. Units live in the field names,
because a column called ``duration`` in a CSV is how a seconds/milliseconds bug
survives to publication.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np


class SignalType(StrEnum):
    """What a file contains, decided by content first and filename last."""

    ECG = "ECG"
    RR = "RR"
    METRICS = "METRICS"
    HR = "HR"  # legacy Polar Sensor Logger only
    ACC = "ACC"  # legacy Polar Sensor Logger only
    UNKNOWN = "UNKNOWN"


class DetectedBy(StrEnum):
    CONTENT = "content"
    HEADER = "header"
    FILENAME = "filename"
    NONE = "none"


class TimestampKind(StrEnum):
    RELATIVE_MS = "relative_ms"  # the verified export: starts at 0
    POLAR2000_NS = "polar2000_ns"  # Polar Sensor Logger
    UNIX_NS = "unix_ns"
    UNIX_MS = "unix_ms"
    ISO8601 = "iso8601"
    NONE = "none"
    UNKNOWN = "unknown"


class ParseStatus(StrEnum):
    OK = "ok"
    PARTIAL = "partial"  # read, but truncated or with dropped rows
    UNRESOLVED = "unresolved"  # could not classify - must be investigated
    SKIPPED_BY_FILTER = "skipped_by_filter"  # expected, not a problem


class FilterMatch(StrEnum):
    METADATA = "metadata"  # session_type from metrics.json - preferred
    FOLDER = "folder"  # token in the measurement folder name
    FILENAME = "filename"
    NONE = "none"


class RRSource(StrEnum):
    NATIVE_RR = "native_rr"
    HR_COLUMN_RR = "hr_column_rr"
    ECG_PEAKS = "ecg_peaks"
    HR_1HZ = "hr_1hz"


class QualityFlag(StrEnum):
    GOOD = "good"
    WARN = "warn"
    EXCLUDED = "excluded"


class Reliability(StrEnum):
    """Whether a metric may be computed on a segment at all.

    ``INSUFFICIENT`` means the value is not produced - never a number computed
    on inadequate data and quietly presented alongside sound ones.
    """

    FULL = "full"
    LIMITED = "limited"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True, slots=True)
class FileRecord:
    """One row of ``inventory.csv`` (PLAN.md section 6.1)."""

    path: Path
    rel_path: str
    band_id: str
    session_date: str | None
    measurement_folder: str
    session_type: str | None
    passes_filter: bool
    filter_matched_on: FilterMatch
    signal_type: SignalType
    detected_by: DetectedBy
    delimiter: str | None
    decimal: str | None
    encoding: str | None
    timestamp_kind: TimestampKind
    t_start_utc: datetime | None
    t_end_utc: datetime | None
    duration_s: float | None
    n_rows: int
    fs_estimated_hz: float | None
    parse_status: ParseStatus
    note: str = ""

    def to_row(self) -> dict[str, Any]:
        """Flatten for the CSV writer, with enums and paths as plain strings."""
        row = asdict(self)
        row["path"] = str(self.path)
        for key, value in row.items():
            if isinstance(value, StrEnum):
                row[key] = str(value)
            elif isinstance(value, datetime):
                row[key] = value.isoformat()
        return row


@dataclass(frozen=True, slots=True)
class ParsedSignal:
    """Raw numeric content of one signal file, before any cleaning."""

    signal_type: SignalType
    values: np.ndarray  # uV for ECG, ms for RR, bpm for HR
    timestamps_ms: np.ndarray  # relative to the start of this recording
    fs_estimated_hz: float | None
    timestamp_kind: TimestampKind
    t0_utc: datetime | None
    n_rows_dropped: int = 0
    note: str = ""

    @property
    def duration_s(self) -> float:
        if self.timestamps_ms.size < 2:
            return 0.0
        return float(self.timestamps_ms[-1] - self.timestamps_ms[0]) / 1000.0


@dataclass(frozen=True, slots=True)
class AppMetrics:
    """The HRV values the logging app already computed (PLAN.md section 2.3).

    Read for cross-checking only. The pipeline always recomputes from raw RR;
    these never become a published result.
    """

    session_id: str | None
    participant_code: str | None
    session_date: str | None
    session_time: str | None
    session_type: str | None
    duration_s: float | None
    has_ecg: bool | None
    ecg_samples: int | None
    n_rr_raw: int | None
    values: dict[str, float] = field(default_factory=dict)

    def get(self, key: str) -> float | None:
        return self.values.get(key)


@dataclass(frozen=True, slots=True)
class Segment:
    """A window of one recording (PLAN.md section 6.3).

    This is the only type that carries phase boundaries. Nothing downstream may
    know the numbers 0, 3 or 6 - they arrive here and go no further.
    """

    name: str
    level: str  # "phase" | "epoch"
    t_start_s: float
    t_end_s: float
    included_in_metrics: bool
    reliability: Reliability = Reliability.FULL
    reliability_reason: str = ""

    @property
    def duration_s(self) -> float:
        return self.t_end_s - self.t_start_s
