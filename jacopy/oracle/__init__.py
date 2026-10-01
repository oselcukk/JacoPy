"""Model oracle: a notation-independent falsifier for closed equations.

When the engine closes ``lhs = rhs``, the oracle evaluates both sides in
random concrete coordinate models (sympy polynomials on ``R^n``) and
compares. AGREE means "not refuted in N models" — never a proof.

Importing this package is cheap: sympy and the node realizers load
lazily on first use (``check_equal`` / ``check_chain``). The engine-side
entry point is :func:`jacopy.oracle.hook.on_closed`, controlled by
``JACOPY_ORACLE=off|warn|strict`` (library default ``off``).
"""

from __future__ import annotations

__all__ = ["check_equal", "check_chain", "OracleReport", "ChainReport"]


def __getattr__(name):
    if name in ("check_equal", "check_chain"):
        from jacopy.oracle import check

        return getattr(check, name)
    if name in ("OracleReport", "ChainReport"):
        from jacopy.oracle import report

        return getattr(report, name)
    raise AttributeError(name)
