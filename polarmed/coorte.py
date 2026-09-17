"""Coorte de três gravações, com o canto a começar num instante conhecido.

O registo da sessão fixa o início do canto ao **minuto 13**. Isso muda a
natureza do estudo: cada gravação passa a conter as duas condições, e a
comparação passa a ser **dentro do mesmo participante** em vez de entre
pessoas diferentes.

    [descarte][      baseline      ][guard][        canto        ]
    0        1                     13     14                    fim

As duas janelas têm a **mesma duração** dentro de cada gravação: comparar
espectros estimados sobre janelas de comprimento diferente introduz uma
diferença sistemática que não é fisiologia. Quando o canto disponível é mais
curto do que a baseline possível, encurtam-se as duas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from polarmed.config import Config
from polarmed.io.parsers import load_measurement
from polarmed.metrics import frequency, time_domain
from polarmed.metrics.cohort import (
    MIN_EPOCHS,
    MarkerAggregate,
    block_bootstrap_ci,
    cliffs_delta,
    median_ci_by_recording,
    median_difference,
    min_attainable_sign_p,
    sign_test_p,
)
from polarmed.metrics.sliding import sliding_metrics
from polarmed.signal.rr_clean import clean_rr

#: As três gravações que o registo identifica como sessões de Om válidas.
COHORT = (
    "HM13/2026-09-11/livre_1h_2",
    "HM15/2026-09-11/livre_1h",
    "HM16/2026-09-13/livre_1h",
)

CHANT_START_MIN = 13.0
GUARD_MIN = 1.0
DISCARD_START_MIN = 1.0

SLIDING_WINDOW_S = 120.0
SLIDING_HOP_S = 10.0

#: (chave, rótulo, unidade, de onde vem na série deslizante, casas decimais)
MARKERS = (
    ("slow_hf", "Domínio da respiração lenta", "log₁₀", "slow_ratio_log", 2),
    ("peak_hz", "Frequência do pico", "Hz", "peak_freq_hz", 3),
    ("concentration", "Concentração espectral", "fração", "concentration", 2),
    ("rmssd", "RMSSD", "ms", "rmssd", 1),
    ("sdnn", "SDNN", "ms", "sdnn", 1),
    ("hr", "Frequência cardíaca", "bpm", "mean_hr", 1),
)


@dataclass
class RecordingWindows:
    key: str
    band: str
    date: str
    rr_end_min: float
    window_min: float
    baseline_range: tuple[float, float]
    chant_range: tuple[float, float]
    n_beats_baseline: int
    n_beats_chant: int
    pct_corrected: float
    #: Séries deslizantes por fase: ``{marcador: (baseline, canto)}``
    series: dict[str, tuple[np.ndarray, np.ndarray]]
    #: Valor agregado por fase: ``{marcador: (baseline, canto)}``
    values: dict[str, tuple[float, float]]
    tacogram: dict[str, list]
    spectra: dict[str, dict[str, list]]

    @property
    def label(self) -> str:
        return f"{self.band} · {self.date[5:].replace('-', '/')}"


def _phase_windows(
    rr_end_min: float, config: Config
) -> tuple[tuple[float, float], tuple[float, float], float]:
    """Janelas emparelhadas e de igual duração para uma gravação."""
    available = rr_end_min - (CHANT_START_MIN + GUARD_MIN)
    length = min(CHANT_START_MIN - DISCARD_START_MIN, available)
    baseline = (CHANT_START_MIN - length, CHANT_START_MIN)
    chant = (CHANT_START_MIN + GUARD_MIN, CHANT_START_MIN + GUARD_MIN + length)
    return baseline, chant, length


def load_recording(source: Path, key: str, config: Config) -> RecordingWindows | None:
    measurement = load_measurement(source / key)
    if measurement.rr is None or measurement.rr.values.size < 100:
        return None

    cleaned = clean_rr(measurement.rr.values, measurement.rr.timestamps_ms, config.rr)
    t_min = (cleaned.t_s - cleaned.t_s[0]) / 60.0
    rr = cleaned.rr_ms
    rr_end = float(t_min[-1])

    baseline_range, chant_range, length = _phase_windows(rr_end, config)
    if length <= 2.0:
        return None

    def mask(window: tuple[float, float]) -> np.ndarray:
        return (t_min >= window[0]) & (t_min < window[1])

    base_mask, chant_mask = mask(baseline_range), mask(chant_range)

    series: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    values: dict[str, tuple[float, float]] = {}
    spectra: dict[str, dict[str, list]] = {}

    for phase, selection, window in (
        ("baseline", base_mask, baseline_range),
        ("canto", chant_mask, chant_range),
    ):
        rr_phase = rr[selection]
        t_phase = (t_min[selection] - window[0]) * 60.0
        freqs, psd, _ = frequency.spectrum(rr_phase, t_phase, config.spectral)
        band = (freqs >= 0.02) & (freqs <= 0.45)
        spectra[phase] = {"freq_hz": freqs[band].tolist(), "psd": psd[band].tolist()}

    # As séries deslizantes correm sobre a gravação inteira e só depois se
    # cortam por fase: assim cada janela tem sempre 120 s reais de sinal, em
    # vez de janelas truncadas na fronteira das fases.
    full = sliding_metrics(
        rr, t_min * 60.0, config.spectral,
        window_s=SLIDING_WINDOW_S, step_s=SLIDING_HOP_S,
    )
    centre_min = full.t_centre_s / 60.0
    in_base = (centre_min >= baseline_range[0]) & (centre_min < baseline_range[1])
    in_chant = (centre_min >= chant_range[0]) & (centre_min < chant_range[1])

    for marker_key, _, _, attribute, _ in MARKERS:
        full_series = getattr(full, attribute)
        a, b = full_series[in_base], full_series[in_chant]
        series[marker_key] = (a, b)
        values[marker_key] = (
            float(np.nanmedian(a)) if np.isfinite(a).any() else float("nan"),
            float(np.nanmedian(b)) if np.isfinite(b).any() else float("nan"),
        )

    step = max(1, rr.size // 1200)
    return RecordingWindows(
        key=key,
        band=measurement.band_id,
        date=measurement.session_date,
        rr_end_min=rr_end,
        window_min=length,
        baseline_range=baseline_range,
        chant_range=chant_range,
        n_beats_baseline=int(base_mask.sum()),
        n_beats_chant=int(chant_mask.sum()),
        pct_corrected=cleaned.pct_corrected,
        series=series,
        values=values,
        tacogram={"t_min": t_min[::step].tolist(), "rr_ms": rr[::step].tolist()},
        spectra=spectra,
    )


def aggregate_marker(
    marker_key: str, label: str, unit: str, recordings: list[RecordingWindows]
) -> MarkerAggregate:
    per_recording, cliffs, deltas = [], [], []
    for rec in recordings:
        baseline, chant = rec.values[marker_key]
        delta = chant - baseline
        per_recording.append((rec.label, baseline, chant, delta))
        if np.isfinite(delta):
            deltas.append(delta)
        a, b = rec.series[marker_key]
        cliffs.append((rec.label, cliffs_delta(a, b)))

    values = np.asarray(deltas, dtype=np.float64)
    n = int(values.size)
    n_up = int((values > 0).sum())
    low, high = median_ci_by_recording(values) if n >= 3 else (float("nan"),) * 2

    return MarkerAggregate(
        key=marker_key,
        label=label,
        unit=unit,
        n_recordings=n,
        median_delta=float(np.median(values)) if n else float("nan"),
        ci_low=low,
        ci_high=high,
        n_up=n_up,
        sign_p=sign_test_p(n_up, n),
        min_sign_p=min_attainable_sign_p(n),
        per_recording=tuple(per_recording),
        cliffs=tuple(cliffs),
    )


def anonymise(bundle: dict[str, Any]) -> dict[str, Any]:
    """Substitui identificadores de banda e datas em toda a estrutura.

    A pagina da coorte carrega os rotulos em varios sitios — nas gravacoes, em
    ``per_recording`` de cada marcador, nos deltas de Cliff e nas linhas do
    bootstrap. Anonimizar so um deles deixaria os outros a identificar as
    pessoas, que e exatamente o modo de falha que ja aconteceu uma vez neste
    projeto.
    """
    from polarmed.report.build import (
        BAND_ID_PATTERN,
        ISO_DATE_PATTERN,
        _anon_salt,
        anonymise_label,
    )

    salt = _anon_salt()
    labels: dict[str, str] = {}
    for record in bundle["recordings"]:
        labels.setdefault(record["band"], anonymise_label(record["band"], salt))

    def scrub(text: str) -> str:
        for original, label in labels.items():
            text = text.replace(original, label)
        for found in BAND_ID_PATTERN.findall(text):
            text = text.replace(found, anonymise_label(found, salt))
        return ISO_DATE_PATTERN.sub("", text).replace(" · ", "").strip(" ·")

    for record in bundle["recordings"]:
        record["label"] = labels[record["band"]]
        record["band"] = labels[record["band"]]
        record["date"] = ""
    for marker in bundle["markers"]:
        marker["per_recording"] = [
            [scrub(row[0]), *row[1:]] for row in marker["per_recording"]
        ]
        marker["cliffs"] = [[scrub(row[0]), row[1]] for row in marker["cliffs"]]
    for rows in bundle["within"].values():
        for row in rows:
            row["recording"] = scrub(row["recording"])
    bundle["warnings"] = [scrub(w) for w in bundle.get("warnings", [])]
    bundle["anonymised"] = True
    return bundle


def build(source: Path, config: Config) -> dict[str, Any]:
    from datetime import datetime, timezone

    recordings, warnings = [], []
    for key in COHORT:
        rec = load_recording(source, key, config)
        if rec is None:
            warnings.append(f"{key}: sem janelas utilizaveis a volta do minuto 13")
            continue
        recordings.append(rec)

    markers = [
        aggregate_marker(key, label, unit, recordings)
        for key, label, unit, _, _ in MARKERS
    ]

    # Intervalo dentro de cada gravação, por bootstrap por blocos. Responde a
    # uma pergunta diferente da do teste de sinal: não "quantas subiram" mas
    # "nesta pessoa, a diferença aguenta a autocorrelação das janelas".
    within = {}
    for marker_key, label, unit, _, _ in MARKERS:
        rows = []
        for rec in recordings:
            a, b = rec.series[marker_key]
            estimate = block_bootstrap_ci(
                a, b, median_difference,
                hop_s=SLIDING_HOP_S, window_s=SLIDING_WINDOW_S, seed=7,
            )
            rows.append(
                {
                    "recording": rec.label,
                    "value": estimate.value,
                    "ci_low": estimate.ci_low,
                    "ci_high": estimate.ci_high,
                    "block_len": estimate.block_len,
                    "n": estimate.n,
                    "n_effective": estimate.n_effective,
                    "excludes_zero": estimate.excludes_zero,
                }
            )
        within[marker_key] = rows

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config_sha256": config.content_hash(),
        "protocol": {
            "chant_start_min": CHANT_START_MIN,
            "guard_min": GUARD_MIN,
            "discard_start_min": DISCARD_START_MIN,
            "sliding_window_s": SLIDING_WINDOW_S,
            "sliding_hop_s": SLIDING_HOP_S,
            "min_epochs": MIN_EPOCHS,
        },
        "spectral": {
            "window_s": config.spectral.window_s,
            "overlap": config.spectral.overlap,
            "nfft": config.spectral.nfft,
            "bands": {k: list(v) for k, v in config.spectral.bands.items()},
        },
        "recordings": [
            {
                "label": r.label,
                "band": r.band,
                "date": r.date,
                "rr_end_min": r.rr_end_min,
                "window_min": r.window_min,
                "baseline_range": list(r.baseline_range),
                "chant_range": list(r.chant_range),
                "n_beats_baseline": r.n_beats_baseline,
                "n_beats_chant": r.n_beats_chant,
                "pct_corrected": r.pct_corrected,
                "values": {k: list(v) for k, v in r.values.items()},
                "tacogram": r.tacogram,
                "spectra": r.spectra,
                "series": {
                    k: [
                        np.where(np.isfinite(v[0]), v[0], None).tolist(),
                        np.where(np.isfinite(v[1]), v[1], None).tolist(),
                    ]
                    for k, v in r.series.items()
                },
            }
            for r in recordings
        ],
        "markers": [
            {
                "key": m.key,
                "label": m.label,
                "unit": m.unit,
                "n": m.n_recordings,
                "median_delta": m.median_delta,
                "ci_low": m.ci_low,
                "ci_high": m.ci_high,
                "n_up": m.n_up,
                "n_down": m.n_down,
                "sign_p": m.sign_p,
                "min_sign_p": m.min_sign_p,
                "unanimous": m.unanimous,
                "consistent": m.consistent,
                "direction": m.direction,
                "per_recording": [list(x) for x in m.per_recording],
                "cliffs": [list(x) for x in m.cliffs],
            }
            for m in markers
        ],
        "within": within,
        "warnings": warnings,
    }
