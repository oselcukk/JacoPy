"""pytest plugin for the model oracle (SPEC §3).

Without ``--oracle`` nothing changes (the library default ``off``
applies). ``--oracle=warn|strict`` turns the falsifier on at every
CLOSED point of the engine; reports are tagged with the test node id
and summarized in ``--oracle-report`` (JSON).

``@pytest.mark.oracle_exempt(reason="...")`` marks a test that closes a
deliberately false equation (e.g. to test record keeping, not
mathematics). Under ``--oracle=strict`` such a test runs with the oracle
in ``warn`` mode, so its refuting verdicts do not fail it; they are
NOT dropped: the report counts them as ``EXEMPT`` (each record keeps its
original verdict and the reason), and an exemption that refuted nothing
is listed as unused. A test-local ``oracle_mode("strict")`` still wins.
"""

import json
import os
from collections import Counter

import pytest


def pytest_addoption(parser):
    g = parser.getgroup("oracle", "model oracle (jacopy.oracle)")
    g.addoption("--oracle", choices=("off", "warn", "strict"), default=None,
                help="run the model oracle on every closed equation (default: JACOPY_ORACLE / off)")
    g.addoption("--oracle-samples", type=int, default=2, help="models per closure (default 2)")
    g.addoption("--oracle-seed", type=int, default=0, help="base seed (default 0)")
    g.addoption("--oracle-report", default=".oracle/report.json", help="JSON report path")


_STATE = {"on": False, "records": [], "exempt": {}}

#: verdicts an exempt test may produce without failing under strict
_EXEMPTABLE = ("DISAGREE", "ASSUMPTION_LEAK", "AMBIGUOUS")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "oracle_exempt(reason): the test closes a deliberately false equation; "
        "--oracle=strict reports its refuting verdicts as EXEMPT instead of failing it",
    )
    mode = config.getoption("--oracle")
    if mode is None or mode == "off":
        return
    if config.getoption("--oracle-samples") < 1:
        raise pytest.UsageError("--oracle-samples must be a positive int")
    os.environ["JACOPY_ORACLE"] = mode
    os.environ["JACOPY_ORACLE_SAMPLES"] = str(config.getoption("--oracle-samples"))
    os.environ["JACOPY_ORACLE_SEED"] = str(config.getoption("--oracle-seed"))
    # refuting reports are collected below; keep the warnings out of the
    # tests' own warning assertions
    config.addinivalue_line("filterwarnings", "ignore::jacopy.oracle.hook.OracleWarning")
    _STATE["on"] = True


@pytest.fixture(autouse=True)
def _oracle_context(request):
    exempt = request.node.get_closest_marker("oracle_exempt")
    reason = None
    if exempt is not None:
        reason = exempt.kwargs.get("reason") or (exempt.args[0] if exempt.args else None)
        if not isinstance(reason, str) or not reason.strip():
            pytest.fail("@pytest.mark.oracle_exempt needs a non-empty reason=...", pytrace=False)
    if not _STATE["on"]:
        yield
        return
    from jacopy.oracle import hook

    if exempt is not None:
        _STATE["exempt"][request.node.nodeid] = {"reason": reason, "refuting": 0}
    hook.set_context(nodeid=request.node.nodeid)
    hook.REPORTS.clear()
    saved_mode = os.environ.get("JACOPY_ORACLE")
    if exempt is not None and saved_mode == "strict":
        os.environ["JACOPY_ORACLE"] = "warn"  # refutations recorded, not raised
    yield  # teardown below runs whatever the test outcome
    if saved_mode is not None:
        os.environ["JACOPY_ORACLE"] = saved_mode
    for r in hook.REPORTS:
        rec = {
            "nodeid": r.nodeid, "source": r.source, "verdict": r.verdict,
            "unsupported_type": r.unsupported_type, "elapsed": round(r.elapsed, 4),
        }
        if r.verdict != "AGREE" and r.verdict != "UNSUPPORTED":
            rec.update(r.to_dict())
        elif r.verdict == "UNSUPPORTED":
            rec["unsupported_path"] = [str(x) for x in (r.unsupported_path or ())]
            rec["detail"] = r.detail
        if reason is not None and r.verdict in _EXEMPTABLE:
            rec["exempt"] = True
            rec["exempt_reason"] = reason
            _STATE["exempt"][request.node.nodeid]["refuting"] += 1
        _STATE["records"].append(rec)
    hook.REPORTS.clear()
    hook.set_context(nodeid="")


def pytest_sessionfinish(session, exitstatus):
    if not _STATE["on"]:
        return
    recs = _STATE["records"]
    # an exempted refutation is counted as EXEMPT, never as DISAGREE / AGREE
    verdicts = Counter("EXEMPT" if r.get("exempt") else r["verdict"] for r in recs)
    exempt_tests = _STATE["exempt"]
    unsupported = Counter(r["unsupported_type"] for r in recs if r["verdict"] == "UNSUPPORTED")
    sources = Counter(r["source"] for r in recs)
    summary = {
        "closed_events": len(recs),
        "verdicts": dict(verdicts),
        "sources": dict(sources),
        "unsupported_histogram": dict(unsupported.most_common()),
        "oracle_seconds": round(sum(r["elapsed"] for r in recs), 2),
        "exempt_tests": {k: dict(v) for k, v in sorted(exempt_tests.items())},
        # an exemption that refuted nothing is stale: listed, not hidden
        "exempt_unused": sorted(k for k, v in exempt_tests.items() if not v["refuting"]),
        "seed": session.config.getoption("--oracle-seed"),
        "samples": session.config.getoption("--oracle-samples"),
    }
    path = session.config.getoption("--oracle-report")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "records": recs}, fh, ensure_ascii=False, indent=1)
    _STATE["summary"] = summary


def pytest_terminal_summary(terminalreporter):
    s = _STATE.get("summary")
    if not s:
        return
    tr = terminalreporter
    tr.section("model oracle")
    tr.write_line(f"closed events: {s['closed_events']}  verdicts: {s['verdicts']}")
    for k, v in s["exempt_tests"].items():
        tr.write_line(f"  EXEMPT {v['refuting']:3d}  {k}  ({v['reason']})")
    for k in s["exempt_unused"]:
        tr.write_line(f"  EXEMPT-UNUSED  {k}  (marked oracle_exempt but nothing was refuted)")
    for k, v in list(s["unsupported_histogram"].items())[:10]:
        tr.write_line(f"  UNSUPPORTED {v:6d}  {k}")
