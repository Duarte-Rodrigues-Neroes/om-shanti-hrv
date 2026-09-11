"""``run_manifest.json`` - the provenance record for one pipeline run.

Every published figure must be traceable to the exact cut, config and library
versions that produced it (PLAN.md sections 6.6 and 10). Looking at an old
report six months later, the manifest is what answers "which offsets was this?".
"""

from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from polarmed import __version__
from polarmed.config import Config

# Libraries whose version can change a numeric result. Recorded on every run.
TRACKED_PACKAGES = (
    "numpy",
    "scipy",
    "pandas",
    "neurokit2",
    "scikit-learn",
    "plotly",
    "pydantic",
    "PyYAML",
    "Jinja2",
    "pyEDFlib",
)


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in TRACKED_PACKAGES:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def _git_revision() -> str:
    """Current commit, or a marker when the tree is not a usable repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    if result.returncode != 0:
        # Distinguish "not a repository" from "repository with no commits yet":
        # in a provenance record, a vague answer is worse than a precise one.
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if inside.returncode == 0 and inside.stdout.strip() == "true":
            return "no-commits-yet"
        return "not-a-repo"
    revision = result.stdout.strip()

    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if dirty.returncode == 0 and dirty.stdout.strip():
        return f"{revision}-dirty"
    return revision


@dataclass
class RunManifest:
    """Accumulates provenance during a run; written once at the end."""

    config: Config
    source: Path
    out_dir: Path
    command: str
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    files_processed: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_file(self, path: Path, sha256: str, status: str) -> None:
        self.files_processed.append(
            {"path": str(path), "sha256": sha256, "status": status}
        )

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        cfg = self.config
        return {
            "polarmed_version": __version__,
            "git_revision": _git_revision(),
            "started_at_utc": self.started_at.isoformat(),
            "written_at_utc": datetime.now(timezone.utc).isoformat(),
            "command": self.command,
            "source": str(self.source),
            "out_dir": str(self.out_dir),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "library_versions": _package_versions(),
            "config_sha256": cfg.content_hash(),
            # Surfaced at the top level because these are the parameters a reader
            # of an old report most needs, and digging them out of the full config
            # dump is exactly the friction that stops people from checking.
            "phase_offsets": {
                "rest_start_min": cfg.phases.rest.start_min,
                "rest_end_min": cfg.phases.rest.end_min,
                "guard_start_min": cfg.phases.guard.start_min,
                "guard_end_min": cfg.phases.guard.end_min,
                "mantra_start_min": cfg.phases.mantra.start_min,
                "epoch_min": cfg.epochs.duration_min,
                "summary": cfg.phase_summary(),
            },
            "alignment": cfg.alignment.mode,
            "measurement_filter": cfg.ingest.measurement_filter,
            "session_types_included": cfg.ingest.session_types_included,
            "primary_endpoint": cfg.primary_endpoint.model_dump(mode="json"),
            "publish_mode": cfg.report.publish_mode,
            "files_processed": self.files_processed,
            "warnings": self.warnings,
            "config_resolved": cfg.model_dump(mode="json"),
        }

    def write(self, path: Path | None = None) -> Path:
        target = path or (self.out_dir / "run_manifest.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        return target
