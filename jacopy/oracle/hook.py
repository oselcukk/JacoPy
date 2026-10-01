"""Engine-side entry point: :func:`on_closed`.

Called at the engine's CLOSED points (SPEC §3). Controlled by
``JACOPY_ORACLE=off|warn|strict`` (default ``off``: the call returns
immediately and nothing — not even sympy — is imported), or by the
:func:`oracle_mode` context manager / the ``oracle=`` keyword of
``prove`` / ``show_equal``. ``0/false/no/none/''`` mean off; an unknown
value warns ONCE and means off (a typo never breaks the engine).

* ``warn``: refuting verdicts (DISAGREE, ASSUMPTION_LEAK) and an
  unchecked leak emit an :class:`OracleWarning`; an internal oracle
  error is recorded as UNSUPPORTED(``oracle-error:<type>``).
* ``strict``: refuting verdicts raise :class:`OracleDisagreement`;
  internal oracle errors are RAISED (an oracle bug must be loud);
  an unchecked leak is warned.

Each equation is checked once per test context (the same ``lhs = rhs``
closed again by a wrapping strategy reuses the report). :data:`REPORTS`
is a bounded ring buffer.

This module imports nothing from the engine (independence).
"""

from __future__ import annotations

import collections
import contextlib
import contextvars
import os
import warnings
from typing import Optional

MODES = ("off", "warn", "strict")
_OFF_ALIASES = ("", "0", "false", "no", "none", "off")

#: Reports produced while the oracle is on (ring buffer; the pytest
#: plugin drains it per test).
REPORTS: collections.deque = collections.deque(maxlen=10_000)

_mode_override: contextvars.ContextVar = contextvars.ContextVar("jacopy_oracle_mode", default=None)
_context: dict = {"nodeid": ""}
_active = contextvars.ContextVar("jacopy_oracle_active", default=False)
_seen: "collections.OrderedDict" = collections.OrderedDict()
_SEEN_MAX = 2048
_warned_bad_values: set = set()


class OracleWarning(UserWarning):
    """A closed equation was refuted in a concrete model."""


class OracleDisagreement(AssertionError):
    """Strict mode: a closed equation was refuted in a concrete model."""

    def __init__(self, report) -> None:
        super().__init__(str(report))
        self.report = report


def _normalize(value) -> str:
    v = (value or "").strip().lower()
    if v in _OFF_ALIASES:
        return "off"
    if v in MODES:
        return v
    if v not in _warned_bad_values:
        _warned_bad_values.add(v)
        warnings.warn(f"JACOPY_ORACLE={value!r} is not one of {MODES}; the oracle stays off", OracleWarning, stacklevel=3)
    return "off"


def current_mode(override: Optional[str] = None) -> str:
    if override is not None:
        return _normalize(override)
    o = _mode_override.get()
    if o is not None:
        return _normalize(o)
    return _normalize(os.environ.get("JACOPY_ORACLE", "off"))


@contextlib.contextmanager
def oracle_mode(mode: Optional[str]):
    """Temporarily set the oracle mode (``None`` keeps the current one)."""
    if mode is None:
        yield
        return
    token = _mode_override.set(mode)
    try:
        yield
    finally:
        _mode_override.reset(token)


def set_context(*, nodeid: str = "") -> None:
    """Tag subsequent reports (the pytest plugin sets the test node id);
    a new context also resets the per-context deduplication."""
    _context["nodeid"] = nodeid
    _seen.clear()


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
    try:
        key = (lhs, rhs, id(registry))
        hash(key)
    except TypeError:
        key = None
    if key is not None and key in _seen:
        # already checked in this context (a wrapping strategy closing the
        # same equation): no second check / record / warning, but strict
        # mode still refuses a refuted closure
        cached = _seen[key]
        if m == "strict" and cached.refutes:
            raise OracleDisagreement(cached)
        return cached
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
        except Exception as exc:  # noqa: BLE001
            if m == "strict":
                raise  # an oracle bug must be loud in strict mode
            try:
                lt, rt = lhs._repr_inner(), rhs._repr_inner()
            except Exception:  # noqa: BLE001
                lt = rt = "?"
            report = OracleReport(UNSUPPORTED, lhs=lt, rhs=rt, unsupported_type=f"oracle-error:{type(exc).__name__}",
                                  unsupported_path=(), detail=str(exc)[:300], source=source, nodeid=_context["nodeid"])
        REPORTS.append(report)
        if key is not None:
            _seen[key] = report
            while len(_seen) > _SEEN_MAX:
                _seen.popitem(last=False)
    finally:
        _active.reset(token)
    if report.refutes:
        if m == "strict":
            raise OracleDisagreement(report)
        warnings.warn(str(report), OracleWarning, stacklevel=2)
    elif getattr(report, "leak_unchecked", None):
        warnings.warn(str(report), OracleWarning, stacklevel=2)
    return report
