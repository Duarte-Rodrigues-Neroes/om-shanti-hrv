"""What each --publish-mode is allowed to let out of the machine (PLAN.md 10).

These are privacy assertions, not formatting ones. A regression here publishes
physiological data about identifiable people, so every mode is checked for what
it must *remove*, including from free text - the first implementation
anonymised the structured fields and left the band ids sitting in the warning
strings.
"""

from __future__ import annotations

import copy

import pytest

from polarmed.report.build import (
    BAND_ID_PATTERN,
    ISO_DATE_PATTERN,
    anonymise_label,
    apply_publish_mode,
)

REAL_IDS = ("HM01", "HM02", "HM07", "HM09", "HM11", "HM13", "HM15", "HM16")


@pytest.fixture
def bundle():
    return {
        "recordings": [
            {
                "band_id": "HM13",
                "session_date": "2026-09-11",
                "session_time": "17:18:11",
                "measurement": "livre_1h_2",
                "key": "HM13 · 09/11 · livre_1h_2",
                "tacogram": {"t_min": [0.0, 1.0], "rr_ms": [800.0, 810.0],
                             "t_raw_min": [0.0], "rr_raw_ms": [800.0]},
                "excerpt": {"t_s": [0.0, 1.0], "rr_ms": [800.0, 810.0]},
                "spectrum": {"freq_hz": [0.1], "psd": [1000.0]},
                "sliding": {"t_min": [1.0], "slow_hf": [1.2]},
            },
            {
                "band_id": "HM01",
                "session_date": "2026-09-11",
                "session_time": "09:02:00",
                "measurement": "rest_5min_manha",
                "key": "HM01 · 09/11 · rest_5min_manha",
                "tacogram": {"t_min": [0.0], "rr_ms": [900.0],
                             "t_raw_min": [0.0], "rr_raw_ms": [900.0]},
                "excerpt": {"t_s": [0.0], "rr_ms": [900.0]},
                "spectrum": {"freq_hz": [0.2], "psd": [500.0]},
                "sliding": {"t_min": [1.0], "slow_hf": [0.4]},
            },
        ],
        # HM11 was skipped for being too short, so it appears only here.
        "warnings": [
            "HM11/2026-09-12/livre_1h: 6.2 min de RR, menos que a janela",
            "HM07/2026-09-11/rest_5min_manha: 41.4% corrigidos",
        ],
    }


class TestPatterns:
    def test_band_pattern_matches_real_ids(self):
        for band in REAL_IDS:
            assert BAND_ID_PATTERN.findall(f"{band}/2026-09-11/x") == [band]

    def test_date_pattern_matches_iso_dates(self):
        assert ISO_DATE_PATTERN.findall("a/2026-09-11/b") == ["2026-09-11"]

    def test_patterns_contain_no_control_characters(self):
        """An escaping slip once turned the word boundaries into backspaces,
        leaving a pattern that silently matched nothing."""
        for pattern in (BAND_ID_PATTERN.pattern, ISO_DATE_PATTERN.pattern):
            assert all(ord(ch) >= 32 for ch in pattern), repr(pattern)


class TestFullMode:
    def test_keeps_everything(self, bundle):
        result = apply_publish_mode(copy.deepcopy(bundle), "full")
        assert result["omitted"] == []
        assert result["recordings"][0]["tacogram"]["rr_ms"]
        assert result["recordings"][0]["band_id"] == "HM13"


class TestAggregateMode:
    def test_drops_every_beat_level_series(self, bundle):
        result = apply_publish_mode(copy.deepcopy(bundle), "aggregate")
        for record in result["recordings"]:
            assert record["tacogram"] == {}
            assert record["excerpt"] == {}

    def test_keeps_derived_statistics(self, bundle):
        """Spectra and sliding series are not the raw physiological record."""
        result = apply_publish_mode(copy.deepcopy(bundle), "aggregate")
        assert result["recordings"][0]["spectrum"]["psd"]
        assert result["recordings"][0]["sliding"]["slow_hf"]

    def test_keeps_band_ids(self, bundle):
        """aggregate is pseudonymous, not anonymous - ids are already codes."""
        result = apply_publish_mode(copy.deepcopy(bundle), "aggregate")
        assert result["recordings"][0]["band_id"] == "HM13"


class TestAnonymousMode:
    def test_replaces_band_ids(self, bundle):
        result = apply_publish_mode(copy.deepcopy(bundle), "anonymous")
        for record in result["recordings"]:
            assert record["band_id"] not in REAL_IDS
            assert record["band_id"].startswith("P")

    def test_removes_dates_and_times(self, bundle):
        result = apply_publish_mode(copy.deepcopy(bundle), "anonymous")
        for record in result["recordings"]:
            assert record["session_date"] == ""
            assert record["session_time"] is None

    def test_scrubs_warnings_of_ids_and_dates(self, bundle):
        """The regression this test exists for."""
        result = apply_publish_mode(copy.deepcopy(bundle), "anonymous")
        joined = " ".join(result["warnings"])
        assert not BAND_ID_PATTERN.findall(joined)
        assert not ISO_DATE_PATTERN.findall(joined)

    def test_labels_bands_that_only_appear_in_warnings(self, bundle):
        """A band skipped for being too short must not stay identifiable."""
        result = apply_publish_mode(copy.deepcopy(bundle), "anonymous")
        assert "HM11" not in " ".join(result["warnings"])

    def test_no_real_id_survives_anywhere_in_the_bundle(self, bundle):
        import json

        result = apply_publish_mode(copy.deepcopy(bundle), "anonymous")
        blob = json.dumps(result, ensure_ascii=False)
        assert not BAND_ID_PATTERN.findall(blob)
        assert not ISO_DATE_PATTERN.findall(blob)

    def test_labels_are_stable_for_the_same_salt(self):
        """Otherwise two versions of the report cannot be compared at all."""
        assert anonymise_label("HM13", "salt-a") == anonymise_label("HM13", "salt-a")

    def test_labels_differ_for_a_different_salt(self):
        assert anonymise_label("HM13", "salt-a") != anonymise_label("HM13", "salt-b")

    def test_distinct_bands_get_distinct_labels(self):
        labels = {anonymise_label(b, "salt-a") for b in REAL_IDS}
        assert len(labels) == len(REAL_IDS)
