"""Pipeline driver: from a folder of measurements to a results bundle.

Each recording is processed independently inside a try/except: one unreadable
file must never cost the other recordings, so failures are recorded and the run
continues (PLAN.md section 5).
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from polarmed.config import Config
from polarmed.io.parsers import Measurement, discover_measurements, load_measurement
from polarmed.metrics import frequency, time_domain
from polarmed.models import QualityFlag, Reliability, Segment
from polarmed.signal.phases import EndAnchoredPlan, mantra_epochs, segment_end_anchored
from polarmed.signal.rr_clean import CleanedRR, clean_rr, find_noisy_prefix_s

log = logging.getLogger(__name__)


@dataclass
class SegmentResult:
    band_id: str
    session_date: str
    measurement: str
    level: str
    segment: str
    t_start_s: float
    t_end_s: float
    duration_s: float
    reliability: str
    reliability_reason: str
    metrics: dict[str, float] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        row = {k: v for k, v in asdict(self).items() if k != "metrics"}
        row.update(self.metrics)
        return row


@dataclass
class RecordingResult:
    band_id: str
    session_date: str
    measurement: str
    session_time: str | None
    session_type: str | None
    stated_duration_s: float
    rr_span_s: float
    n_beats: int
    pct_corrected: float
    quality_flag: str
    discard_s: float
    plan: EndAnchoredPlan | None
    segments: list[SegmentResult]
    cleaned: CleanedRR | None
    app_metrics: dict[str, float]
    app_rmssd_delta_pct: float | None
    excluded_reason: str
    contrast_ready: bool

    @property
    def key(self) -> str:
        return f"{self.band_id}/{self.session_date}/{self.measurement}"

    @property
    def coverage_ratio(self) -> float:
        """RR span over stated duration - how much of the session has data."""
        if self.stated_duration_s <= 0:
            return 0.0
        return self.rr_span_s / self.stated_duration_s

    def segment_metrics(self, name: str) -> dict[str, float] | None:
        for seg in self.segments:
            if seg.segment == name:
                return seg.metrics
        return None


def _slice_rr(cleaned: CleanedRR, segment: Segment) -> np.ndarray:
    t = cleaned.t_s - cleaned.t_s[0]
    mask = (t >= segment.t_start_s) & (t < segment.t_end_s)
    return cleaned.rr_ms[mask]


def _slice_rr_t(cleaned: CleanedRR, segment: Segment) -> tuple[np.ndarray, np.ndarray]:
    t = cleaned.t_s - cleaned.t_s[0]
    mask = (t >= segment.t_start_s) & (t < segment.t_end_s)
    return cleaned.rr_ms[mask], t[mask]


def analyse_measurement(
    measurement: Measurement, config: Config
) -> RecordingResult:
    """Clean, segment and measure one recording."""
    app_values = dict(measurement.app.values)
    stated = measurement.stated_duration_s

    if measurement.rr is None or measurement.rr.values.size < 10:
        return RecordingResult(
            band_id=measurement.band_id,
            session_date=measurement.session_date,
            measurement=measurement.measurement,
            session_time=measurement.app.session_time,
            session_type=measurement.app.session_type,
            stated_duration_s=stated,
            rr_span_s=0.0,
            n_beats=0,
            pct_corrected=100.0,
            quality_flag=str(QualityFlag.EXCLUDED),
            discard_s=0.0,
            plan=None,
            segments=[],
            cleaned=None,
            app_metrics=app_values,
            app_rmssd_delta_pct=None,
            excluded_reason="sem serie RR utilizavel",
            contrast_ready=False,
        )

    cleaned = clean_rr(measurement.rr.values, measurement.rr.timestamps_ms, config.rr)
    t_rel = cleaned.t_s - cleaned.t_s[0]
    rr_span_s = float(t_rel[-1]) if t_rel.size else 0.0

    discard_s = 0.0
    if config.phases.discard_noisy_start.enabled:
        cfg = config.phases.discard_noisy_start
        discard_s = find_noisy_prefix_s(
            cleaned,
            window_s=cfg.window_s,
            step_s=cfg.step_s,
            max_scan_s=cfg.max_scan_s,
            tolerance=cfg.tolerance,
        )

    plan = segment_end_anchored(
        valid_end_s=rr_span_s,
        first_beat_s=0.0,
        discard_end_s=discard_s,
        mantra_min=config.phases.mantra_min,
        guard_min=config.phases.guard_min,
        min_baseline_min=config.phases.min_baseline_min,
    )

    # The chanting window is a fact about the recording *clock*. If the RR
    # series stops before that window, the recording cannot enter the contrast,
    # however clean the beats it does have (user decision, 2026-09-13).
    covers_clock_end = rr_span_s >= stated - 60.0 if stated > 0 else True
    excluded_reason = ""
    if not covers_clock_end:
        missing_min = (stated - rr_span_s) / 60.0
        excluded_reason = (
            f"RR termina {missing_min:.1f} min antes do fim da gravacao: "
            f"a janela de canto nao tem dados"
        )
    elif cleaned.quality_flag is QualityFlag.EXCLUDED:
        excluded_reason = f"pct_corrected {cleaned.pct_corrected:.1f}% acima do limiar"

    all_segments = list(plan.segments) + mantra_epochs(plan)
    results: list[SegmentResult] = []
    for segment in all_segments:
        rr_seg, t_seg = _slice_rr_t(cleaned, segment)
        reliability = segment.reliability
        reason = segment.reliability_reason

        if rr_seg.size < config.reliability.min_beats_time_domain:
            reliability = Reliability.INSUFFICIENT
            reason = (
                f"{rr_seg.size} batimentos < "
                f"{config.reliability.min_beats_time_domain} minimos"
            )

        metrics: dict[str, float] = {}
        if reliability is not Reliability.INSUFFICIENT and rr_seg.size >= 2:
            metrics.update(time_domain.summarise(rr_seg))
            metrics.update(frequency.summarise(rr_seg, t_seg, config.spectral))
            if metrics.get("n_welch_segments", 0) < config.reliability.min_welch_segments:
                metrics["spectral_reliable"] = 0.0
            else:
                metrics["spectral_reliable"] = 1.0
        else:
            metrics["n_beats"] = int(rr_seg.size)

        results.append(
            SegmentResult(
                band_id=measurement.band_id,
                session_date=measurement.session_date,
                measurement=measurement.measurement,
                level=segment.level,
                segment=segment.name,
                t_start_s=segment.t_start_s,
                t_end_s=segment.t_end_s,
                duration_s=segment.duration_s,
                reliability=str(reliability),
                reliability_reason=reason,
                metrics=metrics,
            )
        )

    # Cross-check against the app's own RMSSD. It is computed over at most the
    # first 1000 beats, so on a long recording it describes the opening twelve
    # minutes - a large divergence is expected and is not evidence of a bug.
    app_delta = None
    app_rmssd = app_values.get("rmssd")
    if app_rmssd:
        opening = cleaned.rr_ms[: int(app_values.get("n_rr", len(cleaned.rr_ms)))]
        ours = time_domain.rmssd(opening)
        if np.isfinite(ours) and app_rmssd > 0:
            app_delta = float(100.0 * (ours - app_rmssd) / app_rmssd)

    contrast_ready = plan.contrast_ready and covers_clock_end and not excluded_reason

    return RecordingResult(
        band_id=measurement.band_id,
        session_date=measurement.session_date,
        measurement=measurement.measurement,
        session_time=measurement.app.session_time,
        session_type=measurement.app.session_type,
        stated_duration_s=stated,
        rr_span_s=rr_span_s,
        n_beats=cleaned.n_beats,
        pct_corrected=cleaned.pct_corrected,
        quality_flag=str(cleaned.quality_flag),
        discard_s=discard_s,
        plan=plan,
        segments=results,
        cleaned=cleaned,
        app_metrics=app_values,
        app_rmssd_delta_pct=app_delta,
        excluded_reason=excluded_reason,
        contrast_ready=contrast_ready,
    )


def run(source: Path, config: Config) -> tuple[list[RecordingResult], list[str]]:
    """Analyse every measurement under ``source``. Never aborts on one failure."""
    folders = discover_measurements(source)
    results: list[RecordingResult] = []
    warnings: list[str] = []

    for folder in folders:
        label = "/".join(folder.parts[-3:])
        try:
            measurement = load_measurement(folder, load_ecg=False)
            result = analyse_measurement(measurement, config)
        except Exception as exc:  # noqa: BLE001 - deliberate: keep going
            log.exception("falha a processar %s", label)
            warnings.append(f"{label}: falhou ({exc})")
            continue

        if result.excluded_reason:
            warnings.append(f"{result.key}: {result.excluded_reason}")
        results.append(result)
        log.info(
            "%s: %d batimentos, %.1f min, %.1f%% corrigidos, contraste=%s",
            result.key,
            result.n_beats,
            result.rr_span_s / 60,
            result.pct_corrected,
            "sim" if result.contrast_ready else "nao",
        )

    return results, warnings
