"""Phase segmentation - the only module that knows phase boundaries.

**The anchor is the end of the recording, not the start.** The single thing
known about the protocol is that the final stretch of each readout is Om
chanting. Nobody recorded when the rest period began, several participants
skipped it, and some were still walking when recording started. So the timeline
is laid out backwards from the last valid beat:

    [ discard ][ baseline ][ guard ][        mantra        ]
    ^                                                      ^
    start (noisy, cut by artefact detection)      last valid beat

``baseline`` is given the *same duration* as ``mantra``. Comparing spectra
estimated over windows of different length introduces a systematic difference
that has nothing to do with physiology (PLAN.md section 4.3), and matching the
durations is the cheapest way to remove it.

``guard`` is excluded from every metric and every aggregate, but is returned so
plots can shade it.
"""

from __future__ import annotations

from dataclasses import dataclass

from polarmed.models import Reliability, Segment


@dataclass(frozen=True, slots=True)
class EndAnchoredPlan:
    """Resolved layout for one recording, in seconds from the first beat."""

    segments: list[Segment]
    discard_end_s: float
    valid_end_s: float
    baseline_is_full_length: bool
    note: str

    def by_name(self, name: str) -> Segment | None:
        for segment in self.segments:
            if segment.name == name:
                return segment
        return None

    @property
    def contrast_ready(self) -> bool:
        """Both sides of the primary contrast exist and carry usable data."""
        baseline, mantra = self.by_name("baseline"), self.by_name("mantra")
        return (
            baseline is not None
            and mantra is not None
            and baseline.reliability is not Reliability.INSUFFICIENT
            and mantra.reliability is not Reliability.INSUFFICIENT
        )


def segment_end_anchored(
    valid_end_s: float,
    first_beat_s: float,
    discard_end_s: float,
    mantra_min: float,
    guard_min: float,
    min_baseline_min: float,
) -> EndAnchoredPlan:
    """Lay out discard / baseline / guard / mantra backwards from the end.

    ``valid_end_s`` is the time of the **last valid beat**, not the stated
    recording duration: several recordings claim a duration far longer than the
    RR series they actually contain, and anchoring on the claim would place the
    mantra window in a region with no data at all.
    """
    mantra_s = mantra_min * 60.0
    guard_s = guard_min * 60.0
    min_baseline_s = min_baseline_min * 60.0

    segments: list[Segment] = []
    notes: list[str] = []

    mantra_start = valid_end_s - mantra_s
    if mantra_start < first_beat_s:
        # The whole recording is shorter than the chanting window.
        segments.append(
            Segment(
                name="mantra",
                level="phase",
                t_start_s=first_beat_s,
                t_end_s=valid_end_s,
                included_in_metrics=True,
                reliability=Reliability.LIMITED,
                reliability_reason=(
                    f"gravacao ({(valid_end_s - first_beat_s) / 60:.1f} min) mais curta "
                    f"que a janela de canto ({mantra_min:.0f} min)"
                ),
            )
        )
        return EndAnchoredPlan(
            segments=segments,
            discard_end_s=first_beat_s,
            valid_end_s=valid_end_s,
            baseline_is_full_length=False,
            note="sem baseline: gravacao curta demais",
        )

    segments.append(
        Segment(
            name="mantra",
            level="phase",
            t_start_s=mantra_start,
            t_end_s=valid_end_s,
            included_in_metrics=True,
            reliability=Reliability.FULL,
        )
    )

    guard_start = mantra_start - guard_s
    baseline_end = guard_start
    baseline_start = baseline_end - mantra_s  # matched duration

    usable_start = max(first_beat_s, discard_end_s)
    baseline_is_full = baseline_start >= usable_start

    if not baseline_is_full:
        baseline_start = usable_start
        available_min = (baseline_end - baseline_start) / 60.0
        if baseline_end - baseline_start < min_baseline_s:
            notes.append(
                f"baseline de apenas {max(available_min, 0):.1f} min apos descartar "
                f"o inicio ruidoso"
            )
        else:
            notes.append(
                f"baseline encurtada para {available_min:.1f} min (mantra: "
                f"{mantra_min:.0f} min) - espectro nao estritamente comparavel"
            )

    baseline_duration = baseline_end - baseline_start
    if baseline_duration <= 0:
        return EndAnchoredPlan(
            segments=segments,
            discard_end_s=usable_start,
            valid_end_s=valid_end_s,
            baseline_is_full_length=False,
            note="sem baseline utilizavel apos descartar o inicio e a guarda",
        )

    if baseline_duration >= mantra_s * 0.95:
        reliability, reason = Reliability.FULL, ""
    elif baseline_duration >= min_baseline_s:
        reliability = Reliability.LIMITED
        reason = (
            f"baseline de {baseline_duration / 60:.1f} min contra "
            f"{mantra_min:.0f} min de mantra"
        )
    else:
        reliability = Reliability.INSUFFICIENT
        reason = f"baseline de {baseline_duration / 60:.1f} min: curta demais"

    segments.insert(
        0,
        Segment(
            name="baseline",
            level="phase",
            t_start_s=baseline_start,
            t_end_s=baseline_end,
            included_in_metrics=reliability is not Reliability.INSUFFICIENT,
            reliability=reliability,
            reliability_reason=reason,
        ),
    )
    segments.insert(
        1,
        Segment(
            name="guard",
            level="phase",
            t_start_s=guard_start,
            t_end_s=mantra_start,
            included_in_metrics=False,  # never, by construction
            reliability=Reliability.FULL,
            reliability_reason="transicao, excluida de todas as metricas",
        ),
    )

    return EndAnchoredPlan(
        segments=segments,
        discard_end_s=usable_start,
        valid_end_s=valid_end_s,
        baseline_is_full_length=baseline_is_full,
        note="; ".join(notes),
    )


def mantra_epochs(plan: EndAnchoredPlan, n_epochs: int = 3) -> list[Segment]:
    """Split the mantra phase into equal consecutive epochs.

    This is the interpretive control for the main contrast (PLAN.md section 4.1):
    a metric that keeps drifting across all three epochs looks the same as one
    that simply drifts with time-in-session, whereas a step that then holds is
    what an effect of the chanting would look like.
    """
    mantra = plan.by_name("mantra")
    if mantra is None or n_epochs < 1 or mantra.duration_s <= 0:
        return []

    names = ["inicio", "meio", "fim"][:n_epochs]
    width = mantra.duration_s / n_epochs
    epochs = []
    for index, name in enumerate(names):
        start = mantra.t_start_s + index * width
        epochs.append(
            Segment(
                name=name,
                level="epoch",
                t_start_s=start,
                t_end_s=start + width,
                included_in_metrics=True,
                reliability=mantra.reliability,
                reliability_reason=mantra.reliability_reason,
            )
        )
    return epochs
