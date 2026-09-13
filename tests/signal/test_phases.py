"""End-anchored segmentation.

The protocol gives one certainty - the final stretch of each readout is
chanting - so every boundary is derived backwards from the last valid beat.
These tests pin that behaviour, especially the cases where the recording is too
short to hold the full layout.
"""

from __future__ import annotations

import pytest

from polarmed.models import Reliability
from polarmed.signal.phases import mantra_epochs, segment_end_anchored

MANTRA_MIN = 15.0
GUARD_MIN = 3.0
MIN_BASELINE_MIN = 5.0


def plan_for(valid_end_min: float, discard_min: float = 0.0):
    return segment_end_anchored(
        valid_end_s=valid_end_min * 60.0,
        first_beat_s=0.0,
        discard_end_s=discard_min * 60.0,
        mantra_min=MANTRA_MIN,
        guard_min=GUARD_MIN,
        min_baseline_min=MIN_BASELINE_MIN,
    )


class TestLongRecording:
    """A 42-minute recording holds the full layout with room to spare."""

    def setup_method(self):
        self.plan = plan_for(42.0)

    def test_mantra_is_the_last_fifteen_minutes(self):
        mantra = self.plan.by_name("mantra")
        assert mantra.t_end_s == pytest.approx(42.0 * 60)
        assert mantra.t_start_s == pytest.approx(27.0 * 60)
        assert mantra.duration_s == pytest.approx(15.0 * 60)

    def test_guard_sits_immediately_before_the_mantra(self):
        guard = self.plan.by_name("guard")
        assert guard.t_end_s == pytest.approx(self.plan.by_name("mantra").t_start_s)
        assert guard.duration_s == pytest.approx(GUARD_MIN * 60)

    def test_guard_is_never_included_in_metrics(self):
        assert self.plan.by_name("guard").included_in_metrics is False

    def test_baseline_matches_the_mantra_duration(self):
        """Equal windows keep the spectral comparison honest (PLAN.md 4.3)."""
        baseline = self.plan.by_name("baseline")
        mantra = self.plan.by_name("mantra")
        assert baseline.duration_s == pytest.approx(mantra.duration_s)
        assert self.plan.baseline_is_full_length is True

    def test_phases_do_not_overlap(self):
        baseline = self.plan.by_name("baseline")
        guard = self.plan.by_name("guard")
        mantra = self.plan.by_name("mantra")
        assert baseline.t_end_s <= guard.t_start_s
        assert guard.t_end_s <= mantra.t_start_s

    def test_contrast_is_ready(self):
        assert self.plan.contrast_ready is True


class TestDiscardingTheNoisyStart:
    def test_discard_shortens_the_baseline_rather_than_moving_the_mantra(self):
        """The chanting window is a fact about the end and must not move."""
        plan = plan_for(35.0, discard_min=8.0)
        mantra = plan.by_name("mantra")
        assert mantra.t_start_s == pytest.approx(20.0 * 60)
        baseline = plan.by_name("baseline")
        assert baseline.t_start_s == pytest.approx(8.0 * 60)
        assert plan.baseline_is_full_length is False

    def test_shortened_baseline_is_flagged_limited_not_full(self):
        plan = plan_for(35.0, discard_min=8.0)
        assert plan.by_name("baseline").reliability is Reliability.LIMITED
        assert "baseline" in plan.note

    def test_a_clean_start_loses_nothing(self):
        plan = plan_for(42.0, discard_min=0.0)
        assert plan.baseline_is_full_length is True


class TestShortRecordings:
    def test_recording_shorter_than_the_chanting_window(self):
        """1.1 minutes of RR: it is all mantra, and flagged as limited."""
        plan = plan_for(1.1)
        assert plan.by_name("baseline") is None
        mantra = plan.by_name("mantra")
        assert mantra.reliability is Reliability.LIMITED
        assert plan.contrast_ready is False

    def test_recording_with_no_room_for_a_baseline(self):
        """18 minutes: 15 of mantra plus 3 of guard leaves nothing before."""
        plan = plan_for(18.0)
        assert plan.by_name("baseline") is None
        assert plan.contrast_ready is False

    def test_baseline_below_the_minimum_is_insufficient(self):
        plan = plan_for(21.0)  # leaves 3 min of baseline, under the 5 min floor
        baseline = plan.by_name("baseline")
        assert baseline is not None
        assert baseline.reliability is Reliability.INSUFFICIENT
        assert baseline.included_in_metrics is False
        assert plan.contrast_ready is False

    def test_baseline_above_the_minimum_is_usable_but_limited(self):
        plan = plan_for(26.0)  # leaves 8 min of baseline
        baseline = plan.by_name("baseline")
        assert baseline.reliability is Reliability.LIMITED
        assert baseline.included_in_metrics is True
        assert plan.contrast_ready is True


class TestMantraEpochs:
    def test_three_equal_consecutive_epochs(self):
        plan = plan_for(42.0)
        epochs = mantra_epochs(plan, n_epochs=3)
        assert [e.name for e in epochs] == ["inicio", "meio", "fim"]
        assert all(e.duration_s == pytest.approx(5 * 60) for e in epochs)

    def test_epochs_tile_the_mantra_without_gaps(self):
        plan = plan_for(42.0)
        epochs = mantra_epochs(plan, n_epochs=3)
        mantra = plan.by_name("mantra")
        assert epochs[0].t_start_s == pytest.approx(mantra.t_start_s)
        assert epochs[-1].t_end_s == pytest.approx(mantra.t_end_s)
        for earlier, later in zip(epochs, epochs[1:]):
            assert earlier.t_end_s == pytest.approx(later.t_start_s)

    def test_no_mantra_means_no_epochs(self):
        empty = segment_end_anchored(0.0, 0.0, 0.0, MANTRA_MIN, GUARD_MIN, MIN_BASELINE_MIN)
        assert mantra_epochs(empty) == []


def test_boundaries_come_only_from_arguments():
    """Changing the window changes every boundary, with no code edit."""
    wide = segment_end_anchored(
        valid_end_s=42 * 60, first_beat_s=0.0, discard_end_s=0.0,
        mantra_min=20.0, guard_min=5.0, min_baseline_min=5.0,
    )
    assert wide.by_name("mantra").duration_s == pytest.approx(20 * 60)
    assert wide.by_name("guard").duration_s == pytest.approx(5 * 60)
    assert wide.by_name("baseline").duration_s == pytest.approx(17 * 60)
