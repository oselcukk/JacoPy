"""Engine-side entry point: :func:`on_closed`.

Called at the engine's CLOSED points (SPEC §3). Controlled by
``JACOPY_ORACLE=off|warn|strict`` (default ``off``: the call returns
immediately and nothing — not even sympy — is imported), or by the
:func:`oracle_mode` context manager / the ``oracle=`` keyword of
``prove`` / ``show_equal``.

* ``warn``: refuting verdicts (DISAGREE, ASSUMPTION_LEAK) emit an
  :class:`OracleWarning`; every report is appended to :data:`REPORTS`.
* ``strict``: refuting verdicts raise :class:`OracleDisagreement`.

An internal oracle error never breaks a proof in ``warn`` mode: it is
recorded as UNSUPPORTED(``oracle-error:<type>``).

This module imports nothing from the engine (independence).
"""

from __future__ import annotations

import contextlib
import contextvars
import os
import warnings
from typing import List, Optional

MODES = ("off", "warn", "strict")

#: Every report produced while the oracle is on (bounded by the caller;
#: the pytest plugin drains it per test).
REPORTS: List = []

_mode_override: contextvars.ContextVar = contextvars.ContextVar("jacopy_oracle_mode", default=None)
_context: dict = {"nodeid": ""}
_active = contextvars.ContextVar("jacopy_oracle_active", default=False)


class OracleWarning(UserWarning):
    """A closed equation was refuted in a concrete model."""


class OracleDisagreement(AssertionError):
    """Strict mode: a closed equation was refuted in a concrete model."""

    def __init__(self, report) -> None:
        super().__init__(str(report))
        self.report = report


def current_mode(override: Optional[str] = None) -> str:
    mode = override or _mode_override.get() or os.environ.get("JACOPY_ORACLE", "off") or "off"
    mode = mode.strip().lower()
    if mode not in MODES:
        raise ValueError(f"JACOPY_ORACLE must be one of {MODES}, got {mode!r}")
    return mode


@contextlib.contextmanager
def oracle_mode(mode: Optional[str]):
    """Temporarily set the oracle mode (``None`` keeps the current one)."""
    if mode is None:
        yield
        return
    current_mode(mode)  # validate
    token = _mode_override.set(mode)
    try:
        yield
    finally:
        _mode_override.reset(token)


def set_context(*, nodeid: str = "") -> None:
    """Tag subsequent reports (the pytest plugin sets the test node id)."""
    _context["nodeid"] = nodeid


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def on_closed(lhs, rhs, *, registry=None, source: str = "", engine=None, owners=None,
              requires=None, chain=None, mode: Optional[str] = None):
    """Run the oracle on a just-closed equation ``lhs = rhs``.

    Returns the :class:`~jacopy.oracle.report.OracleReport` (``None`` when
    the oracle is off)."""
    m = current_mode(mode)
    if m == "off" or _active.get():
        return None
    token = _active.set(True)  # no re-entrancy
    try:
        from jacopy.oracle.report import UNSUPPORTED, OracleReport

        try:
            from jacopy.oracle.check import check_equal

            if owners is None and engine is not None:
                owners = getattr(engine, "owners", None)
            report = check_equal(
                lhs, rhs, registry=registry, owners=owners, requires=requires, chain=chain,
                samples=_int_env("JACOPY_ORACLE_SAMPLES", 2), seed=_int_env("JACOPY_ORACLE_SEED", 0),
                source=source, nodeid=_context["nodeid"],
            )
        except Exception as exc:  # noqa: BLE001 — the oracle must not break proofs
            try:
                lt, rt = lhs._repr_inner(), rhs._repr_inner()
            except Exception:  # noqa: BLE001
                lt = rt = "?"
            report = OracleReport(UNSUPPORTED, lhs=lt, rhs=rt, unsupported_type=f"oracle-error:{type(exc).__name__}",
                                  unsupported_path=(), detail=str(exc)[:300], source=source, nodeid=_context["nodeid"])
        REPORTS.append(report)
    finally:
        _active.reset(token)
    if report.refutes:
        if m == "strict":
            raise OracleDisagreement(report)
        warnings.warn(str(report), OracleWarning, stacklevel=2)
    return report
