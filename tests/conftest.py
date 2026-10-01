"""pytest plugin for the model oracle (SPEC §3).

Without ``--oracle`` nothing changes (the library default ``off``
applies). ``--oracle=warn|strict`` turns the falsifier on at every
CLOSED point of the engine; reports are tagged with the test node id
and summarized in ``--oracle-report`` (JSON).
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


_STATE = {"on": False, "records": []}


def pytest_configure(config):
    mode = config.getoption("--oracle")
    if mode is None or mode == "off":
        return
    os.environ["JACOPY_ORACLE"] = mode
    os.environ["JACOPY_ORACLE_SAMPLES"] = str(config.getoption("--oracle-samples"))
    os.environ["JACOPY_ORACLE_SEED"] = str(config.getoption("--oracle-seed"))
    # refuting reports are collected below; keep the warnings out of the
    # tests' own warning assertions
    config.addinivalue_line("filterwarnings", "ignore::jacopy.oracle.hook.OracleWarning")
    _STATE["on"] = True


@pytest.fixture(autouse=True)
def _oracle_context(request):
    if not _STATE["on"]:
        yield
        return
    from jacopy.oracle import hook

    hook.set_context(nodeid=request.node.nodeid)
    hook.REPORTS.clear()
    yield
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
        _STATE["records"].append(rec)
    hook.REPORTS.clear()
    hook.set_context(nodeid="")


def pytest_sessionfinish(session, exitstatus):
    if not _STATE["on"]:
        return
    recs = _STATE["records"]
    verdicts = Counter(r["verdict"] for r in recs)
    unsupported = Counter(r["unsupported_type"] for r in recs if r["verdict"] == "UNSUPPORTED")
    sources = Counter(r["source"] for r in recs)
    summary = {
        "closed_events": len(recs),
        "verdicts": dict(verdicts),
        "sources": dict(sources),
        "unsupported_histogram": dict(unsupported.most_common()),
        "oracle_seconds": round(sum(r["elapsed"] for r in recs), 2),
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
    for k, v in list(s["unsupported_histogram"].items())[:10]:
        tr.write_line(f"  UNSUPPORTED {v:6d}  {k}")
