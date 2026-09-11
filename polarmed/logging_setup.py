"""Logging to console and to ``out/<run>/run.log``.

A failure on one recording must never abort the run (PLAN.md section 5), so the
log is the only place where per-file problems become visible. It is therefore
written eagerly and flushed on every record.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

LOGGER_NAME = "polarmed"
_CONSOLE_FORMAT = "%(levelname)-7s %(message)s"
_FILE_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


class RunCounters:
    """Tally of what happened to each discovered measurement.

    Printed as the final line of every run so that a silent partial failure is
    impossible to miss.
    """

    def __init__(self) -> None:
        self.discovered = 0
        self.filtered_out = 0
        self.processed = 0
        self.warned = 0
        self.excluded = 0
        self.failed = 0

    def summary(self) -> str:
        return (
            f"descobertas={self.discovered} filtradas={self.filtered_out} "
            f"processadas={self.processed} com_aviso={self.warned} "
            f"excluidas={self.excluded} falhadas={self.failed}"
        )


def setup_logging(out_dir: Path | None = None, verbose: bool = False) -> logging.Logger:
    """Configure the package logger. Idempotent: safe to call more than once."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    console = logging.StreamHandler(stream=sys.stderr)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter(_CONSOLE_FORMAT))
    logger.addHandler(console)

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            out_dir / "run.log", mode="w", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(_FILE_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
