"""Regression: the ``oracle_exempt`` marker of the oracle pytest plugin.

Under ``--oracle=strict`` a deliberately false closure ``X = Y`` must
fail an unmarked test, while a test marked
``@pytest.mark.oracle_exempt(reason=...)`` passes and its refutation is
counted as ``EXEMPT`` in the report (never silently dropped, never
counted as DISAGREE). A marker without a reason is refused.

The plugin lives in ``tests/conftest.py``; it is run in a subprocess on a
throw-away test directory (no ``pytester``: ``pytest_plugins`` is not
allowed in a non-root conftest, and the CI wheel job runs a copy of
``tests/``).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_CONFTEST = Path(__file__).with_name("conftest.py")

_INNER = '''
import pytest

from jacopy.central.objects import vector_fields
from jacopy.oracle import hook


def _close_false():
    X, Y = vector_fields("X Y")
    hook.on_closed(X, Y, source="exempt-regression")


def _close_true():
    X, = vector_fields("X")
    hook.on_closed(X, X, source="exempt-regression")


@pytest.mark.oracle_exempt(reason="deliberately false X = Y")
def test_marked():
    _close_true()
    _close_false()


def test_unmarked():
    _close_false()


@pytest.mark.oracle_exempt(reason="stale: closes nothing false")
def test_marked_unused():
    _close_true()


@pytest.mark.oracle_exempt
def test_marked_without_reason():
    pass
'''


def _run(tmp_path, *args):
    shutil.copy(_CONFTEST, tmp_path / "conftest.py")
    (tmp_path / "test_inner.py").write_text(_INNER, encoding="utf-8")
    env = dict(os.environ)
    env.pop("JACOPY_ORACLE", None)
    # the inner run must import the same jacopy as this one
    import jacopy

    pkg_root = str(Path(jacopy.__file__).resolve().parent.parent)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (pkg_root, env.get("PYTHONPATH")) if p)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
         "--rootdir", str(tmp_path), str(tmp_path / "test_inner.py"), *args],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=300,
    )


def _outcomes(stdout):
    out = {}
    for line in stdout.splitlines():
        for tag in ("PASSED", "FAILED", "ERROR"):
            if line.startswith(tag + " ") and "::" in line:
                out[line.split("::", 1)[1].split()[0]] = tag
    return out


def test_strict_exempts_marked_and_fails_unmarked(tmp_path):
    pytest.importorskip("sympy")
    report = tmp_path / "oracle-report.json"
    proc = _run(tmp_path, "--oracle=strict", f"--oracle-report={report}")
    outcomes = _outcomes(proc.stdout)
    assert outcomes.get("test_marked") == "PASSED", proc.stdout + proc.stderr
    assert outcomes.get("test_unmarked") == "FAILED", proc.stdout + proc.stderr
    assert "OracleDisagreement" in proc.stdout
    assert outcomes.get("test_marked_unused") == "PASSED", proc.stdout
    # a marker without a reason is an error, not a silent exemption
    assert outcomes.get("test_marked_without_reason") in ("FAILED", "ERROR"), proc.stdout

    data = json.loads(report.read_text(encoding="utf-8"))
    summary, recs = data["summary"], data["records"]
    assert summary["verdicts"].get("EXEMPT") == 1
    # the unmarked refutation is still DISAGREE; the exempt one is not
    assert summary["verdicts"].get("DISAGREE") == 1
    marked = [r for r in recs if r["nodeid"].endswith("::test_marked")]
    assert sorted(r["verdict"] for r in marked) == ["AGREE", "DISAGREE"]
    (ex,) = [r for r in marked if r.get("exempt")]
    assert ex["verdict"] == "DISAGREE" and ex["exempt_reason"] == "deliberately false X = Y"
    assert not any(r.get("exempt") for r in recs if r["nodeid"].endswith("::test_unmarked"))
    exempt_tests = {k.split("::", 1)[1]: v for k, v in summary["exempt_tests"].items()}
    assert exempt_tests["test_marked"]["refuting"] == 1
    assert [k.split("::", 1)[1] for k in summary["exempt_unused"]] == ["test_marked_unused"]
    assert "EXEMPT" in proc.stdout and "EXEMPT-UNUSED" in proc.stdout


def test_without_oracle_marker_changes_nothing(tmp_path):
    proc = _run(tmp_path)
    outcomes = _outcomes(proc.stdout)
    assert outcomes.get("test_marked") == "PASSED", proc.stdout + proc.stderr
    assert outcomes.get("test_unmarked") == "PASSED", proc.stdout + proc.stderr
    assert outcomes.get("test_marked_without_reason") in ("FAILED", "ERROR"), proc.stdout
    assert "PytestUnknownMarkWarning" not in proc.stdout + proc.stderr
