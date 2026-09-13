"""Assemble the cohort report bundle.

Collects every number the page needs into one plain dict, so the HTML writer
does no analysis and the same bundle can be dumped to JSON for inspection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from polarmed.config import Config
from polarmed.io.parsers import discover_measurements, load_measurement
from polarmed.metrics import frequency, time_domain
from polarmed.metrics.sliding import detect_onset_s, sliding_metrics
from polarmed.models import QualityFlag
from polarmed.signal.rr_clean import clean_rr

CHANT_WINDOW_S = 900.0


def _finite(values: list[float]) -> list[float]:
    return [v for v in values if v is not None and np.isfinite(v)]


def summary_stats(values: list[float]) -> dict[str, Any]:
    """Median with the full range and n - never a mean without dispersion."""
    clean = _finite(values)
    if not clean:
        return {"n": 0, "median": None, "min": None, "max": None}
    return {
        "n": len(clean),
        "median": float(np.median(clean)),
        "min": float(np.min(clean)),
        "max": float(np.max(clean)),
    }


def smooth_for_plot(t_s: np.ndarray, y: np.ndarray, window_s: float) -> np.ndarray:
    """Moving average for the plot layer only - never for a metric.

    A 42-minute tachogram drawn at full beat resolution is a hairball: the
    beat-to-beat scatter hides the slow wave that is the whole point. Smoothing
    is applied here, at render time, and the metrics upstream never see it.
    """
    if y.size < 8 or window_s <= 0:
        return y
    span_s = float(t_s[-1] - t_s[0])
    if span_s <= 0:
        return y
    beats_per_s = y.size / span_s
    width = max(3, int(round(window_s * beats_per_s)) | 1)  # odd
    if width >= y.size:
        return y
    kernel = np.ones(width) / width
    padded = np.pad(y, width // 2, mode="edge")
    return np.convolve(padded, kernel, mode="valid")[: y.size]


def downsample(x: np.ndarray, y: np.ndarray, max_points: int = 1400):
    """Thin a series for the page without distorting its shape."""
    if x.size <= max_points:
        return x, y
    idx = np.linspace(0, x.size - 1, max_points).astype(int)
    return x[idx], y[idx]


@dataclass
class Recording:
    band_id: str
    session_date: str
    measurement: str
    session_time: str | None
    kind: str  # "repouso" | "canto"
    stated_min: float
    rr_min: float
    n_beats: int
    pct_corrected: float
    covers_session_end: bool
    truncated_min: float
    quality_flag: str = "good"
    in_aggregates: bool = True
    window_metrics: dict[str, float] = field(default_factory=dict)
    slow_hf_log: float = float("nan")
    tacogram: dict[str, list] = field(default_factory=dict)
    sliding: dict[str, list] = field(default_factory=dict)
    spectrum: dict[str, list] = field(default_factory=dict)
    excerpt: dict[str, list] = field(default_factory=dict)
    onset_min: float = float("nan")
    onset_confidence: float = 0.0
    notes: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.band_id} · {self.session_date[5:].replace('-', '/')} · {self.measurement}"


def slow_hf_ratio(rr: np.ndarray, t: np.ndarray, config: Config) -> float:
    """log10 of slow-band power over HF power - the chanting signature.

    A ratio rather than an absolute power: slow-band power varies by an order of
    magnitude between people, so an absolute threshold would need calibrating per
    participant (PLAN.md 4.4).
    """
    freqs, psd, _ = frequency.spectrum(rr, t, config.spectral)
    if freqs.size == 0:
        return float("nan")
    slow = frequency.band_power(freqs, psd, *config.spectral.bands["SLOW"])
    hf = frequency.band_power(freqs, psd, *config.spectral.bands["HF"])
    if not (np.isfinite(slow) and np.isfinite(hf)) or slow <= 0 or hf <= 0:
        return float("nan")
    return float(np.log10(slow / hf))


def build(source: Path, config: Config) -> dict[str, Any]:
    recordings: list[Recording] = []
    warnings: list[str] = []

    for folder in discover_measurements(source):
        label = "/".join(folder.parts[-3:])
        try:
            meas = load_measurement(folder)
            if meas.rr is None or meas.rr.values.size < 30:
                warnings.append(f"{label}: serie RR curta demais para analisar")
                continue

            cleaned = clean_rr(meas.rr.values, meas.rr.timestamps_ms, config.rr)
            t = cleaned.t_s - cleaned.t_s[0]
            rr = cleaned.rr_ms
            rr_span = float(t[-1])
            stated = meas.stated_duration_s
            truncated = max(0.0, stated - rr_span)
            covers_end = truncated <= 60.0

            is_rest = "rest" in meas.measurement.lower()
            kind = "repouso" if is_rest else "canto"

            notes: list[str] = []
            if is_rest:
                sel = np.ones(t.size, dtype=bool)
            else:
                if rr_span < CHANT_WINDOW_S:
                    warnings.append(
                        f"{label}: {rr_span / 60:.1f} min de RR, menos que a "
                        f"janela de canto de {CHANT_WINDOW_S / 60:.0f} min"
                    )
                    continue
                sel = t >= (rr_span - CHANT_WINDOW_S)
                if not covers_end:
                    notes.append(
                        f"RR termina {truncated / 60:.1f} min antes do fim da "
                        f"sessao; a janela e os ultimos {CHANT_WINDOW_S / 60:.0f} "
                        f"min de sinal existente, nao do relogio da sessao"
                    )

            rr_win, t_win = rr[sel], t[sel]
            if rr_win.size < config.reliability.min_beats_time_domain:
                warnings.append(f"{label}: janela com apenas {rr_win.size} batimentos")
                continue

            metrics = time_domain.summarise(rr_win)
            metrics.update(frequency.summarise(rr_win, t_win, config.spectral))

            freqs, psd, _ = frequency.spectrum(rr_win, t_win, config.spectral)
            band = (freqs >= 0.02) & (freqs <= 0.45)

            series = sliding_metrics(rr, t, config.spectral)
            onset_s, confidence = detect_onset_s(series)

            # A 90 s excerpt, taken from the middle of the analysed window.
            # At full-session zoom a 12-second wave is a few pixels wide, so the
            # claim that the oscillation is slow and large is not actually
            # visible anywhere on the page without this.
            win_t = t[sel]
            mid = (win_t[0] + win_t[-1]) / 2.0
            exc = (t >= mid - 45.0) & (t <= mid + 45.0)
            excerpt = {
                "t_s": (t[exc] - (mid - 45.0)).tolist(),
                "rr_ms": rr[exc].tolist(),
            }

            rr_plot = smooth_for_plot(t, rr, config.rr.plot_smoothing_s)
            tx, ty = downsample(t / 60.0, rr_plot)
            rx, ry = downsample(t / 60.0, rr, max_points=900)

            if cleaned.pct_corrected > config.rr.quality_warn_max_pct:
                notes.append(
                    f"{cleaned.pct_corrected:.1f}% dos batimentos corrigidos: "
                    f"excluido dos agregados"
                )

            recordings.append(
                Recording(
                    band_id=meas.band_id,
                    session_date=meas.session_date,
                    measurement=meas.measurement,
                    session_time=meas.app.session_time,
                    kind=kind,
                    stated_min=stated / 60.0,
                    rr_min=rr_span / 60.0,
                    n_beats=cleaned.n_beats,
                    pct_corrected=cleaned.pct_corrected,
                    covers_session_end=covers_end,
                    truncated_min=truncated / 60.0,
                    quality_flag=str(cleaned.quality_flag),
                    in_aggregates=cleaned.quality_flag is not QualityFlag.EXCLUDED,
                    window_metrics=metrics,
                    slow_hf_log=slow_hf_ratio(rr_win, t_win, config),
                    tacogram={
                        "t_min": tx.tolist(),
                        "rr_ms": ty.tolist(),
                        "t_raw_min": rx.tolist(),
                        "rr_raw_ms": ry.tolist(),
                    },
                    excerpt=excerpt,
                    sliding={
                        "t_min": (series.t_centre_s / 60.0).tolist(),
                        "peak_hz": np.where(
                            np.isfinite(series.peak_freq_hz), series.peak_freq_hz, None
                        ).tolist(),
                        "slow_hf": np.where(
                            np.isfinite(series.slow_ratio_log),
                            series.slow_ratio_log,
                            None,
                        ).tolist(),
                        "rmssd": np.where(
                            np.isfinite(series.rmssd), series.rmssd, None
                        ).tolist(),
                    },
                    spectrum={
                        "freq_hz": freqs[band].tolist(),
                        "psd": psd[band].tolist(),
                    },
                    onset_min=onset_s / 60.0 if np.isfinite(onset_s) else float("nan"),
                    onset_confidence=confidence,
                    notes=notes,
                )
            )
        except Exception as exc:  # noqa: BLE001 - one bad file must not stop the run
            warnings.append(f"{label}: falhou ({exc})")

    # Aggregates use only recordings that pass the correction threshold. They
    # stay visible everywhere else, marked - a recording excluded from the
    # numbers must still be on the page (PLAN.md 5.2).
    usable = [r for r in recordings if r.in_aggregates]
    rest = [r for r in usable if r.kind == "repouso"]
    chant = [r for r in usable if r.kind == "canto"]
    excluded = [r for r in recordings if not r.in_aggregates]
    for r in excluded:
        warnings.append(
            f"{r.band_id}/{r.session_date}/{r.measurement}: "
            f"{r.pct_corrected:.1f}% dos batimentos corrigidos "
            f"(limiar {config.rr.quality_warn_max_pct:.0f}%): "
            f"fora dos agregados, visivel no relatorio"
        )

    def collect(group: list[Recording], key: str) -> list[float]:
        if key == "slow_hf_log":
            return [r.slow_hf_log for r in group]
        return [r.window_metrics.get(key, float("nan")) for r in group]

    comparison = {}
    for key in (
        "slow_hf_log", "peak_freq_hz", "spectral_concentration",
        "RMSSD", "mean_HR", "SDNN", "pNN50", "SLOW_rel",
    ):
        comparison[key] = {
            "repouso": summary_stats(collect(rest, key)),
            "canto": summary_stats(collect(chant, key)),
        }

    # Do the two conditions overlap at all on the signature statistic? With
    # this many participants that is a more honest statement than a p-value.
    rest_vals = _finite(collect(rest, "slow_hf_log"))
    chant_vals = _finite(collect(chant, "slow_hf_log"))
    separation = {
        "separated": bool(rest_vals and chant_vals and max(rest_vals) < min(chant_vals)),
        "rest_max": max(rest_vals) if rest_vals else None,
        "chant_min": min(chant_vals) if chant_vals else None,
        "n_rest": len(rest_vals),
        "n_chant": len(chant_vals),
    }

    # Display range for the tacogram, from the recordings that pass quality.
    # One corrupted series with 11-second "intervals" would otherwise flatten
    # every other trace into a band a few pixels tall.
    pool = np.concatenate(
        [np.asarray(r.tacogram["rr_raw_ms"]) for r in usable if r.tacogram]
    ) if usable else np.array([600.0, 1000.0])
    taco_range = [
        float(np.floor(np.percentile(pool, 0.5) / 50) * 50 - 50),
        float(np.ceil(np.percentile(pool, 99.5) / 50) * 50 + 50),
    ]

    return {
        "taco_range_ms": taco_range,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config_sha256": config.content_hash(),
        "phase_summary": config.phase_summary(),
        "chant_window_min": CHANT_WINDOW_S / 60.0,
        "spectral": {
            "window_s": config.spectral.window_s,
            "overlap": config.spectral.overlap,
            "nfft": config.spectral.nfft,
            "bands": {k: list(v) for k, v in config.spectral.bands.items()},
        },
        "recordings": [
            {
                **{
                    k: v
                    for k, v in r.__dict__.items()
                    if k
                    not in (
                        "tacogram", "sliding", "spectrum", "excerpt", "window_metrics",
                    )
                },
                "key": r.key,
                "window_metrics": {
                    k: (None if isinstance(v, float) and not np.isfinite(v) else v)
                    for k, v in r.window_metrics.items()
                },
                "tacogram": r.tacogram,
                "sliding": r.sliding,
                "spectrum": r.spectrum,
                "excerpt": r.excerpt,
            }
            for r in recordings
        ],
        "comparison": comparison,
        "separation": separation,
        "n_excluded_from_aggregates": len(excluded),
        "warnings": warnings,
    }


def apply_publish_mode(bundle: dict[str, Any], mode: str) -> dict[str, Any]:
    """Strip what must not leave the machine, per --publish-mode (PLAN.md 10).

    ``full``       everything, for local use and projection in the room.
    ``aggregate``  drops every beat-level series. Derived statistics stay -
                   spectra, sliding metrics and summary values are not the raw
                   physiological record and cannot be turned back into one.
    ``anonymous``  also replaces band ids with per-run random labels and drops
                   the dates, which alone can identify who was in the room.

    Panels whose data is removed say so on the page rather than rendering empty.
    """
    if mode == "full":
        bundle["publish_mode"] = mode
        bundle["omitted"] = []
        return bundle

    omitted = ["tacogram", "excerpt"]
    for record in bundle["recordings"]:
        for key in omitted:
            record[key] = {}

    if mode == "anonymous":
        import random

        rng = random.Random()
        labels = {}
        for record in bundle["recordings"]:
            original = record["band_id"]
            if original not in labels:
                labels[original] = f"P{rng.randrange(100, 1000)}"
            record["band_id"] = labels[original]
            record["session_date"] = ""
            record["session_time"] = None
            record["key"] = f"{labels[original]} · {record['measurement']}"
        omitted += ["band_id", "session_date"]

    bundle["publish_mode"] = mode
    bundle["omitted"] = omitted
    return bundle


def sanitise(value: Any) -> Any:
    """Replace every non-finite float with ``None``, recursively.

    JSON has no NaN. Emitting the JavaScript literal ``NaN`` would parse in a
    browser but break ``JSON.parse``, and a missing value must read as missing
    on the page rather than as a number - so it becomes ``null``.
    """
    if isinstance(value, dict):
        return {k: sanitise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitise(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(bundle: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(sanitise(bundle), ensure_ascii=False, allow_nan=False, indent=1),
        encoding="utf-8",
    )
