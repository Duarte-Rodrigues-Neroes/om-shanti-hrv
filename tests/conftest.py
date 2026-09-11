"""Shared fixtures."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from polarmed.config import DEFAULT_CONFIG_PATH

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def default_config_dict() -> dict[str, Any]:
    """The shipped config, parsed. Treat as read-only; copy before mutating."""
    with open(DEFAULT_CONFIG_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def config_factory(default_config_dict, tmp_path):
    """Write a variant of the default config to a temp file and return its path."""

    def _make(mutate=None, name: str = "config.yaml") -> Path:
        data = copy.deepcopy(default_config_dict)
        if mutate is not None:
            mutate(data)
        path = tmp_path / name
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, allow_unicode=True)
        return path

    return _make
