"""Config loading, override resolution and the invariants the validator enforces."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from polarmed.config import apply_overrides, load_config


def test_default_config_is_valid():
    config = load_config()
    assert config.phases.mantra_min == 15.0
    assert config.phases.guard_min == 3.0
    assert config.phases.min_baseline_min == 5.0
    assert config.phases.discard_noisy_start.enabled is True


def test_primary_endpoint_is_required(config_factory):
    path = config_factory(lambda d: d.pop("primary_endpoint"))
    with pytest.raises(ValidationError):
        load_config(path)


def test_primary_endpoint_rejects_malformed_date(config_factory):
    path = config_factory(
        lambda d: d["primary_endpoint"].__setitem__("declared_on", "11-09-2026")
    )
    with pytest.raises(ValidationError):
        load_config(path)


def test_phase_summary_reflects_the_cut():
    config = load_config()
    summary = config.phase_summary()
    assert "ultimos 15 min" in summary
    assert "guard 3 min (excluida)" in summary


def test_config_hash_changes_with_the_cut():
    """An old report must be traceable to its offsets, so the hash must move."""
    baseline = load_config()
    recut = load_config(overrides={"phases.mantra_min": 20.0})
    assert baseline.content_hash() != recut.content_hash()


def test_config_hash_is_stable_across_loads():
    assert load_config().content_hash() == load_config().content_hash()


class TestEndAnchoredPhases:
    """The protocol is anchored on the end of the recording.

    Only one thing is known for certain - the final stretch of each readout is
    chanting - so the config carries durations, not absolute offsets.
    """

    def test_non_positive_mantra_window_is_rejected(self, config_factory):
        path = config_factory(lambda d: d["phases"].__setitem__("mantra_min", 0.0))
        with pytest.raises(ValidationError, match="mantra_min must be positive"):
            load_config(path)

    def test_negative_guard_is_rejected(self, config_factory):
        path = config_factory(lambda d: d["phases"].__setitem__("guard_min", -1.0))
        with pytest.raises(ValidationError, match="guard_min cannot be negative"):
            load_config(path)

    def test_baseline_floor_above_the_mantra_window_is_rejected(self, config_factory):
        """The baseline is matched to the mantra, so such a floor is unreachable."""
        path = config_factory(
            lambda d: d["phases"].__setitem__("min_baseline_min", 20.0)
        )
        with pytest.raises(ValidationError, match="cannot exceed"):
            load_config(path)

    def test_a_zero_guard_is_allowed(self, config_factory):
        """Legitimate choice: drop the transition window entirely."""
        path = config_factory(lambda d: d["phases"].__setitem__("guard_min", 0.0))
        assert load_config(path).phases.guard_min == 0.0


class TestOverrides:
    def test_applies_nested_leaf(self, default_config_dict):
        result = apply_overrides(
            default_config_dict, {"phases.discard_noisy_start.tolerance": 3.0}
        )
        assert result["phases"]["discard_noisy_start"]["tolerance"] == 3.0

    def test_applies_top_level_leaf(self, default_config_dict):
        result = apply_overrides(default_config_dict, {"phases.mantra_min": 20.0})
        assert result["phases"]["mantra_min"] == 20.0

    def test_does_not_mutate_the_input(self, default_config_dict):
        before = default_config_dict["phases"]["mantra_min"]
        apply_overrides(default_config_dict, {"phases.mantra_min": 99.0})
        assert default_config_dict["phases"]["mantra_min"] == before

    def test_none_is_ignored(self, default_config_dict):
        """Unset CLI flags arrive as None and must not clobber the config."""
        result = apply_overrides(default_config_dict, {"phases.mantra_min": None})
        assert result["phases"]["mantra_min"] == 15.0

    def test_unknown_path_raises(self, default_config_dict):
        """A mistyped flag must never pass silently into a published report."""
        with pytest.raises(KeyError):
            apply_overrides(default_config_dict, {"phases.no_such_key": 1.0})

    def test_unknown_branch_raises(self, default_config_dict):
        with pytest.raises(KeyError):
            apply_overrides(default_config_dict, {"nope.deeper": 1.0})


class TestValidatorGuards:
    def test_unknown_yaml_key_is_rejected(self, config_factory):
        """A typo in the YAML must fail loudly, not be silently ignored."""
        path = config_factory(lambda d: d.__setitem__("typoed_section", {"a": 1}))
        with pytest.raises(ValidationError):
            load_config(path)

    def test_quality_thresholds_must_be_ordered(self, config_factory):
        path = config_factory(
            lambda d: d["rr"].__setitem__("quality_warn_max_pct", 1.0)
        )
        with pytest.raises(ValidationError, match="quality_warn_max_pct"):
            load_config(path)

    def test_plausibility_bounds_must_be_ordered(self, config_factory):
        path = config_factory(lambda d: d["rr"].__setitem__("plausible_max_ms", 100.0))
        with pytest.raises(ValidationError, match="plausible_max_ms"):
            load_config(path)

    def test_spectral_band_bounds_must_be_ordered(self, config_factory):
        path = config_factory(
            lambda d: d["spectral"]["bands"].__setitem__("HF", [0.4, 0.15])
        )
        with pytest.raises(ValidationError, match="upper bound"):
            load_config(path)


def test_vlf_is_disabled_by_default():
    """PLAN.md 4.3: VLF is not estimable with a 60 s window and must not ship."""
    assert load_config().spectral.vlf_enabled is False


def test_welch_window_is_phase_matched_by_default():
    """A single window length is used in every phase, so phases stay comparable."""
    config = load_config()
    assert config.spectral.window_s == 60.0
    assert config.spectral.overlap == 0.5
