# Testing

The protected test set is the union of the groups below. A change is
green when all of them are; the counts change as the suite grows and
are not the criterion — the commands are. (For orientation: on
2026-10-02 the fast suite was 2,572 passed, 12 skipped, 5 xfailed in
122 test files, branch `fix/display-polish`; `main` at `8b46a5d` had
2,528 / 12 / 5 in 118 files. The notebook smoke run passes 4/4.)

## 1. Fast suite (every push, every supported Python)

```sh
.venv/bin/python -m pytest tests -q
```

Pure Python. The only optional dependency the suite knows about is
**sympy, the `oracle` extra**: tests that call the model oracle (or
walk every module, `jacopy.oracle` included) start with
`pytest.importorskip("sympy")` and are reported as skipped when it is
missing. Install it with `pip install -e ".[test,oracle]"` (or
`.[dev]`) to run them.

### Wheel run (CI job `wheel`)

In CI (`.github/workflows/tests.yml`, job `wheel`) the fast suite runs
on Python 3.10, 3.11, 3.12, 3.13 and 3.14 **from the installed wheel**,
with only `pytest` next to it (no sympy): the wheel is built with
`python -m build`, installed into a clean interpreter, and the tests
are executed from a copy of `tests/` outside the repository so the
source tree cannot shadow the package. Tests that need a repository
file (`pyproject.toml`, `examples/`, `CITATION.cff`,
`docs/CITATIONS.md`) skip with a reason. The same check locally:

```sh
make test-wheel
```

or by hand:

```sh
python -m build --wheel --outdir dist
python -m venv /tmp/jacopy-wheel && /tmp/jacopy-wheel/bin/pip install dist/*.whl pytest
cp -R tests /tmp/jacopy-wheel/tests && cd /tmp/jacopy-wheel && bin/python -m pytest tests -q -p no:cacheprovider
```

The run must have no collection error and no failure; the skips are
the sympy-dependent tests, the repository-file tests and the slow
suites.

## 2. Slow proof suites (weekly / on request)

Some closures take one to fifteen minutes. They are gated by
environment variables and skipped otherwise (the skip reason names the
variable and the expected time):

```sh
JACOPY_RUN_SLOW=1 .venv/bin/python -m pytest tests -q          # ~1–2 min closures
JACOPY_RUN_VERY_SLOW=1 .venv/bin/python -m pytest tests -q     # the ~14 min rotated metric invariance
```

CI runs the `JACOPY_RUN_SLOW=1` set in the `slow` job on the weekly
schedule and on a manual `workflow_dispatch` with `slow = true`. The
`JACOPY_RUN_VERY_SLOW=1` closure (about fourteen minutes) is not run
by CI; run it locally before a release.

## 3. The model oracle

The oracle (`jacopy.oracle`, needs the `oracle` extra) evaluates both
sides of every equation the engine closes in random concrete models.
The pytest plugin in `tests/conftest.py` adds:

| Option | Meaning |
|---|---|
| `--oracle=off\|warn\|strict` | `off` (default, or `JACOPY_ORACLE`): nothing changes. `warn`: a refuting verdict is recorded (and warned). `strict`: a refuting verdict (`DISAGREE`, `ASSUMPTION_LEAK`) or an ambiguity fails the test; an internal oracle error is raised. |
| `--oracle-report PATH` | JSON report: closed events, verdict counts, `UNSUPPORTED` histogram, exempt tests, unused exemptions (default `.oracle/report.json`). |
| `--oracle-samples N` | models per closure (default 2). |
| `--oracle-seed N` | base seed (default 0). |

```sh
.venv/bin/python -m pytest tests -q --oracle=strict --oracle-report oracle-report.json
make test-oracle      # --oracle=warn, report in .oracle/report.json
```

Markers registered by the plugin:

* `@pytest.mark.oracle_exempt(reason="...")` — the test closes a
  deliberately false equation (to test record keeping, not
  mathematics). Under `--oracle=strict` it runs with the oracle in
  `warn` mode; its refuting verdicts are counted as `EXEMPT` in the
  report (with the reason), never dropped. An exemption that refuted
  nothing is listed under `exempt_unused`. The reason is mandatory: an
  empty one fails the test. A test-local `oracle_mode("strict")` still
  wins.
* `@pytest.mark.contract_table` — a Scalar-contract differential table
  (the engine predicate against the oracle's independent restatement)
  run as one test over every declaration combination.

CI runs the fast suite under `--oracle=strict` in the `oracle` job
(Python 3.12, `pip install -e ".[test,oracle]"`) and uploads the JSON
report as an artifact.

## 4. Notebook smoke run

```sh
.venv/bin/python scripts/run_notebooks.py      # or: make notebooks
```

Executes every code cell of every notebook under `examples/` in a fresh
namespace, in order. It is a code check, not a rendering check. CI runs
it in the `slow` job.

## 5. Merge gate

Before a branch is merged into `main`, run all of the following on the
branch and compare with the same commands on `main`:

1. the fast suite (section 1) — same pass/skip/xfail counts, plus the
   branch's new tests;
2. the slow suites with `JACOPY_RUN_SLOW=1` (section 2);
3. the fast suite under `--oracle=strict` (section 3) — no refutation
   outside the declared exemptions;
4. the notebook smoke run (section 4);
5. for packaging changes, the wheel run (section 1).

Known bugs are kept visible as strict `xfail` tests (for example the
AgreementOnGenerators domain cases in
`tests/test_audit_0b00e1b_p1_core_round4.py`); a strict `xfail` that
starts passing fails the run, so the fix must remove the marker.

## 6. Independent audit tests (outside the repository)

The audit directory `../audit_jacopy_v3/` (next to the repository
checkout) holds the reviewer's counterexample tests. They are part of
the protected set and are re-run after every fix round:

```sh
cd ../audit_jacopy_v3 && ../jacopy_v3/.venv/bin/python -m pytest -q
```

Files: `test_review_regressions.py`, `test_fix_recheck.py`,
`test_second_fix_recheck.py`, `test_compliance_gaps.py`,
`test_new_developments_audit.py`, `test_e6e9c1e_recheck.py`,
`test_research_notebook_audit.py`, `test_post_f685_audit.py`,
`test_f6b6791_recheck.py`, `test_library_api_audit.py` (the six
library-API contracts), `test_4dd888e_progress.py`,
`test_1b3c4b3_recheck.py`, `test_0058df0_k3_audit.py`,
`test_7a11162_recheck.py`, `test_dc44f79_progress.py`, plus the
coordinate oracles they import.
The audit files are not published with the package.

## Optional dependencies

| Package | Extra | Used by |
|---|---|---|
| `sympy` | `oracle` | the model oracle and the tests that call it |
| `rich` | `rich` | coloured terminal proofs (plain text without it) |
| `ipykernel` | `docs` | the Jupyter kernel for the notebooks |
| `pdflatex` | — (system) | `tests/test_citations.py` compiles a real document when it is on `PATH`; skipped otherwise |
