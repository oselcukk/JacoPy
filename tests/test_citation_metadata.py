"""CITATION.cff carries a second copy of the version literal; it must
match the single version source ``jacopy.__version__`` (audit
0B00E1B-FULL T2-8 / T2-9).

The file is read with a line scan (no YAML dependency). When the tests
run from a copy outside the repository (the CI ``wheel`` job), there is
no CITATION.cff next to them and the check is skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import jacopy

CFF = Path(__file__).resolve().parents[1] / "CITATION.cff"


def _cff_field(name: str) -> str:
    for line in CFF.read_text(encoding="utf-8").splitlines():
        m = re.match(rf"^{name}:\s*(.*?)\s*$", line)
        if m:
            return m.group(1).strip("\"'")
    raise AssertionError(f"CITATION.cff has no top-level {name!r} field")


@pytest.mark.skipif(not CFF.is_file(), reason="CITATION.cff is not next to the tests (wheel run)")
def test_citation_version_matches_package_version():
    assert _cff_field("version") == jacopy.__version__


@pytest.mark.skipif(not CFF.is_file(), reason="CITATION.cff is not next to the tests (wheel run)")
def test_citation_title_is_the_project_name():
    assert _cff_field("title") == "JacoPy"
