"""Configuration model and resolution.

The YAML file in ``config/`` is the single source of truth for every threshold,
window and phase offset in the pipeline (PLAN.md section 5). CLI flags override
individual leaves; nothing else may hard-code these numbers.

The resolved config is hashed into ``run_manifest.json`` so that an old report
can always be traced back to the exact cut that produced it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default.yaml"


class _Base(BaseModel):
    """Reject unknown keys so a typo in YAML fails loudly instead of silently."""

    model_config = ConfigDict(extra="forbid")


class PrimaryEndpoint(_Base):
    """The one result declared before looking at the data (PLAN.md section 4.7)."""

    metric: str
    contrast: str
    direction: Literal["increase", "decrease", "any"]
    declared_on: str

    @field_validator("declared_on")
    @classmethod
    def _iso_date(cls, v: str) -> str:
        from datetime import date

        date.fromisoformat(v)  # raises on malformed input
        return v


class DiscardNoisyStartConfig(_Base):
    """How much of the opening to drop, decided from the data.

    Participants were still settling - some walking - when recording began, so
    the first minutes carry motion artefact. A fixed cut would be arbitrary and
    would differ in effect between a 20-minute and a 45-minute recording.
    """

    enabled: bool = True
    window_s: float = 60.0
    step_s: float = 15.0
    max_scan_s: float = 600.0
    tolerance: float = 2.0


class PhasesConfig(_Base):
    """End-anchored protocol (see ``polarmed.signal.phases``).

    The only fact known about the protocol is that the final stretch of each
    readout is chanting, so boundaries are measured backwards from the last
    valid beat rather than forwards from the recording start.
    """

    mantra_min: float = 15.0
    guard_min: float = 3.0
    min_baseline_min: float = 5.0
    discard_noisy_start: DiscardNoisyStartConfig = Field(
        default_factory=DiscardNoisyStartConfig
    )

    @model_validator(mode="after")
    def _positive(self) -> PhasesConfig:
        if self.mantra_min <= 0:
            raise ValueError("mantra_min must be positive")
        if self.guard_min < 0:
            raise ValueError("guard_min cannot be negative")
        if self.min_baseline_min > self.mantra_min:
            raise ValueError(
                f"min_baseline_min ({self.min_baseline_min}) cannot exceed "
                f"mantra_min ({self.mantra_min}): the baseline is matched to the "
                f"mantra window and could never reach the floor"
            )
        return self


class EpochsConfig(_Base):
    duration_min: float = 3.0
    names: list[str] = Field(default_factory=lambda: ["inicio", "meio", "fim"])
    include_rest_as_epoch: bool = True


class AlignmentConfig(_Base):
    mode: Literal["recording_start", "group_start"] = "recording_start"
    group_deviation_warn_s: float = 60.0


class IngestConfig(_Base):
    session_types_included: list[str] = Field(default_factory=lambda: ["free"])
    measurement_filter: str = "livre"
    session_grouping: Literal["time", "folder"] = "time"
    session_gap_hours: float = 2.0
    app_metric_tolerance_pct: float = 5.0
    encodings_tried: list[str] = Field(
        default_factory=lambda: ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    )


class RRConfig(_Base):
    source_priority: list[str]
    plausible_min_ms: float = 300.0
    plausible_max_ms: float = 2000.0
    ectopic_median_window_beats: int = 5
    ectopic_rel_threshold: float = 0.22
    interpolation: str = "cubic"
    quality_good_max_pct: float = 5.0
    quality_warn_max_pct: float = 15.0
    resample_hz: float = 4.0
    plot_smoothing_s: float = 10.0

    @model_validator(mode="after")
    def _thresholds_ordered(self) -> RRConfig:
        if self.quality_warn_max_pct <= self.quality_good_max_pct:
            raise ValueError("quality_warn_max_pct must exceed quality_good_max_pct")
        if self.plausible_max_ms <= self.plausible_min_ms:
            raise ValueError("plausible_max_ms must exceed plausible_min_ms")
        return self


class ECGConfig(_Base):
    sampling_rate_hz: float = 130.0
    sampling_rate_tolerance_hz: float = 0.5
    bandpass_low_hz: float = 0.5
    bandpass_high_hz: float = 40.0
    powerline_hz: float = 50.0
    peak_method: str = "neurokit"


class LongWindowConfig(_Base):
    enabled: bool = True
    window_s: float = 256.0


class SpectralConfig(_Base):
    window_s: float = 60.0
    overlap: float = 0.5
    detrend: str = "linear"
    nfft: int = 1024
    peak_interpolation: str = "parabolic"
    bands: dict[str, tuple[float, float]]
    lf_marginal_warning: bool = True
    vlf_enabled: bool = False
    long_window: LongWindowConfig = Field(default_factory=LongWindowConfig)

    @model_validator(mode="after")
    def _bands_ordered(self) -> SpectralConfig:
        for name, (lo, hi) in self.bands.items():
            if hi <= lo:
                raise ValueError(
                    f"band {name}: upper bound {hi} must exceed lower bound {lo}"
                )
        return self


class ReliabilityConfig(_Base):
    min_beats_time_domain: int = 60
    min_beats_sampen: int = 250
    min_beats_dfa_a1: int = 300
    min_welch_segments: int = 2


class EDRConfig(_Base):
    enabled: bool = True
    method: Literal["r_amplitude", "qrs_area"] = "r_amplitude"
    bandpass_low_hz: float = 0.04
    bandpass_high_hz: float = 0.5
    min_confidence: float = 0.35


class EMGProxyConfig(_Base):
    band_hz: tuple[float, float] = (40.0, 60.0)
    motion_threshold_rel: float = 2.5


class OnsetConfig(_Base):
    spectrogram_window_s: float = 120.0
    spectrogram_step_s: float = 10.0
    baseline_minutes: float = 2.0
    cusum_threshold: float = 1.0
    warn_deviation_s: float = 90.0
    edr: EDRConfig = Field(default_factory=EDRConfig)
    emg_proxy: EMGProxyConfig = Field(default_factory=EMGProxyConfig)


class SlidingConfig(_Base):
    window_s: float = 60.0
    step_s: float = 10.0


class SynchronyConfig(_Base):
    enabled: bool = True
    window_s: float = 45.0
    step_s: float = 5.0
    permutation_n: int = 200
    require_permutation_null: bool = True
    max_clock_deviation_s: float = 60.0


class StatsConfig(_Base):
    ci_exact_max_n: int = 7
    bootstrap_n: int = 10000
    multiple_comparison: str = "holm"
    forbid_significance_language: bool = True


class ReportConfig(_Base):
    publish_mode: Literal["full", "aggregate", "anonymous"] = "aggregate"
    max_html_mb: float = 6.0
    forbidden_terms: list[str] = Field(default_factory=list)


class Config(_Base):
    """The fully resolved configuration for one pipeline run."""

    primary_endpoint: PrimaryEndpoint
    phases: PhasesConfig
    epochs: EpochsConfig
    alignment: AlignmentConfig
    ingest: IngestConfig
    rr: RRConfig
    ecg: ECGConfig
    spectral: SpectralConfig
    reliability: ReliabilityConfig
    onset: OnsetConfig
    sliding: SlidingConfig
    synchrony: SynchronyConfig
    stats: StatsConfig
    report: ReportConfig

    def content_hash(self) -> str:
        """SHA-256 of the resolved config, recorded in run_manifest.json."""
        payload = json.dumps(
            self.model_dump(mode="json"), sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def phase_summary(self) -> str:
        """One-line human-readable cut, for the report header and the log."""
        phases = self.phases
        return (
            f"ancorado no fim | mantra = ultimos {phases.mantra_min:g} min | "
            f"guard {phases.guard_min:g} min (excluida) | "
            f"baseline {phases.mantra_min:g} min antes da guard "
            f"(minimo {phases.min_baseline_min:g} min)"
        )


def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    return data


def apply_overrides(
    data: dict[str, Any], overrides: dict[str, Any]
) -> dict[str, Any]:
    """Apply dotted-path overrides (``phases.rest.end_min``) onto a config dict.

    Only leaves that already exist may be overridden; an unknown path raises
    rather than being silently ignored, so a mistyped flag can never pass
    unnoticed into a published report.
    """
    result = json.loads(json.dumps(data))  # deep copy via round-trip
    for dotted, value in overrides.items():
        if value is None:
            continue
        node: Any = result
        parts = dotted.split(".")
        for part in parts[:-1]:
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"override path not present in config: {dotted}")
            node = node[part]
        leaf = parts[-1]
        if not isinstance(node, dict) or leaf not in node:
            raise KeyError(f"override path not present in config: {dotted}")
        node[leaf] = value
    return result


def load_config(
    config_path: Path | None = None, overrides: dict[str, Any] | None = None
) -> Config:
    """Load the YAML config, apply CLI overrides, and validate the result."""
    path = config_path or DEFAULT_CONFIG_PATH
    data = load_yaml(path)
    if overrides:
        data = apply_overrides(data, overrides)
    return Config.model_validate(data)
