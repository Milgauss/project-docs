"""Guardrails against README / plan drift vs the public API and contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "rel,banned",
    [
        (
            "README.md",
            [
                r"not exported from api_spend",
                r"not yet present in api_spend\.__all__",
                r"planned in phase 8",
            ],
        ),
        (
            "IMPLEMENTATION_PLAN.md",
            [
                r"not exported from api_spend",
                r"not yet present in api_spend\.__all__",
            ],
        ),
    ],
)
def test_marketing_and_plan_docs_no_stale_export_claims(rel: str, banned: list[str]) -> None:
    text = _read(rel).lower()
    for pattern in banned:
        assert not re.search(pattern, text, flags=re.IGNORECASE), (
            f"{rel} contains stale pattern /{pattern}/i — update doc or fix the API"
        )


def test_planned_interface_has_sources_of_truth_section() -> None:
    text = _read("PLANNED_INTERFACE.md")
    assert "sources-of-truth" in text
    assert "## 0. Sources of truth" in text


def test_readme_links_planned_interface_sources_of_truth() -> None:
    text = _read("README.md")
    assert "PLANNED_INTERFACE.md#sources-of-truth" in text
