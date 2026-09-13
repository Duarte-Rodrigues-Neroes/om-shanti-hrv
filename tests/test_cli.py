"""CLI argument resolution, the dry run, and the manifest it writes."""

from __future__ import annotations

import json

import pytest

from polarmed.cli import build_parser, collect_overrides, main


def parse(argv: list[str]):
    return build_parser().parse_args(argv)


class TestOverrideCollection:
    def test_mantra_window_maps_to_a_duration(self):
        """Phases are anchored on the end, so the flag carries a duration."""
        overrides = collect_overrides(
            parse(["run", "--source", "s", "--out", "o", "--mantra-min", "20"])
        )
        assert overrides == {"phases.mantra_min": 20.0}

    def test_guard_and_baseline_floor_map_to_durations(self):
        overrides = collect_overrides(
            parse(
                ["run", "--source", "s", "--out", "o",
                 "--guard-min", "5", "--min-baseline-min", "8"]
            )
        )
        assert overrides["phases.guard_min"] == 5.0
        assert overrides["phases.min_baseline_min"] == 8.0

    def test_noisy_start_discard_can_be_switched_off(self):
        overrides = collect_overrides(
            parse(["run", "--source", "s", "--out", "o", "--no-discard-noisy-start"])
        )
        assert overrides["phases.discard_noisy_start.enabled"] is False

    def test_unset_flags_produce_no_overrides(self):
        assert collect_overrides(parse(["run", "--source", "s", "--out", "o"])) == {}

    def test_session_types_are_split_on_commas(self):
        overrides = collect_overrides(
            parse(
                ["run", "--source", "s", "--out", "o", "--session-types", "free, rest"]
            )
        )
        assert overrides["ingest.session_types_included"] == ["free", "rest"]

    def test_empty_session_types_disables_the_filter(self):
        overrides = collect_overrides(
            parse(["run", "--source", "s", "--out", "o", "--session-types", ""])
        )
        assert overrides["ingest.session_types_included"] == []

    def test_empty_measurement_filter_is_kept_not_dropped(self):
        """An empty string disables the folder-token filter and is meaningful."""
        overrides = collect_overrides(
            parse(["run", "--source", "s", "--out", "o", "--measurement-filter", ""])
        )
        assert overrides["ingest.measurement_filter"] == ""

    def test_all_documented_flags_map_to_config_paths(self):
        overrides = collect_overrides(
            parse(
                [
                    "run",
                    "--source", "s",
                    "--out", "o",
                    "--mantra-min", "18",
                    "--epoch-min", "2",
                    "--align", "group_start",
                    "--hrv-window", "45",
                    "--exclude-threshold", "20",
                    "--session-grouping", "folder",
                    "--publish-mode", "anonymous",
                ]
            )
        )
        assert overrides == {
            "phases.mantra_min": 18.0,
            "epochs.duration_min": 2.0,
            "alignment.mode": "group_start",
            "sliding.window_s": 45.0,
            "rr.quality_warn_max_pct": 20.0,
            "ingest.session_grouping": "folder",
            "report.publish_mode": "anonymous",
        }


class TestDryRun:
    def test_writes_manifest_with_the_requested_cut(self, tmp_path):
        out = tmp_path / "run"
        code = main(
            [
                "run",
                "--source", str(tmp_path / "missing"),
                "--out", str(out),
                "--mantra-min", "20",
                "--guard-min", "5",
                "--dry-run",
            ]
        )
        assert code == 0

        manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
        offsets = manifest["phase_offsets"]
        assert offsets["anchor"] == "end_of_valid_rr"
        assert offsets["mantra_min"] == 20.0
        assert offsets["guard_min"] == 5.0
        assert offsets["baseline_matched_to_mantra"] is True
        assert "ultimos 20 min" in offsets["summary"]

    def test_manifest_records_provenance(self, tmp_path):
        out = tmp_path / "run"
        main(["run", "--source", str(tmp_path), "--out", str(out), "--dry-run"])
        manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))

        for key in (
            "polarmed_version",
            "git_revision",
            "config_sha256",
            "library_versions",
            "primary_endpoint",
            "publish_mode",
            "config_resolved",
        ):
            assert key in manifest, f"manifesto sem {key}"

        # The libraries that can change a numeric result must be pinned in the record.
        for package in ("numpy", "scipy", "neurokit2"):
            assert manifest["library_versions"][package] != "not-installed"

    def test_writes_run_log(self, tmp_path):
        out = tmp_path / "run"
        main(["run", "--source", str(tmp_path), "--out", str(out), "--dry-run"])
        log = (out / "run.log").read_text(encoding="utf-8")
        assert "recorte" in log

    def test_missing_source_is_only_a_warning_during_dry_run(self, tmp_path):
        out = tmp_path / "run"
        code = main(
            [
                "run",
                "--source", str(tmp_path / "nope"),
                "--out", str(out),
                "--dry-run",
            ]
        )
        assert code == 0
        manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
        assert any("nao existe" in w for w in manifest["warnings"])

    def test_missing_source_fails_a_real_run(self, tmp_path):
        out = tmp_path / "run"
        code = main(
            ["run", "--source", str(tmp_path / "nope"), "--out", str(out)]
        )
        assert code == 2


class TestRefusals:
    def test_refuses_config_without_primary_endpoint(self, config_factory, tmp_path, capsys):
        path = config_factory(lambda d: d.pop("primary_endpoint"))
        code = main(
            [
                "run",
                "--source", str(tmp_path),
                "--out", str(tmp_path / "run"),
                "--config", str(path),
                "--dry-run",
            ]
        )
        assert code == 2
        message = capsys.readouterr().err
        assert "primary_endpoint" in message
        # The message must be actionable, not a bare validator dump.
        assert "PLAN.md 4.7" in message

    def test_refuses_incoherent_cut(self, config_factory, tmp_path, capsys):
        path = config_factory(
            lambda d: d["phases"].__setitem__("mantra_min", 0.0)
        )
        code = main(
            [
                "run",
                "--source", str(tmp_path),
                "--out", str(tmp_path / "run"),
                "--config", str(path),
                "--dry-run",
            ]
        )
        assert code == 2
        assert "mantra_min must be positive" in capsys.readouterr().err

    def test_missing_config_file_is_reported_cleanly(self, tmp_path, capsys):
        code = main(
            [
                "run",
                "--source", str(tmp_path),
                "--out", str(tmp_path / "run"),
                "--config", str(tmp_path / "nao_existe.yaml"),
                "--dry-run",
            ]
        )
        assert code == 2
        assert "nao encontrado" in capsys.readouterr().err

    def test_subcommand_is_required(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])
