"""Integration of the oracle hook: default off changes nothing; warn /
strict modes report and refute."""

import warnings

import pytest

from jacopy.core.expr import Integer, Neg, Sum
from jacopy.oracle import hook


def test_default_is_off(monkeypatch):
    monkeypatch.delenv("JACOPY_ORACLE", raising=False)
    assert hook.current_mode() == "off"
    assert hook.on_closed(Integer(1), Integer(2)) is None


def test_bad_mode_rejected(monkeypatch):
    monkeypatch.setenv("JACOPY_ORACLE", "loud")
    with pytest.raises(ValueError):
        hook.current_mode()


def _cartan_case():
    from jacopy.algebra.derivation import Act
    from jacopy.central.objects import forms, vector_fields
    from jacopy.central.objects.interior import Interior
    from jacopy.central.tangent.exterior import CARTAN_TM, d

    from jacopy.core.pairing import Pairing

    X, Y = vector_fields("X Y")
    w, = forms("omega", degree=1)
    lhs = Pairing(Act(CARTAN_TM.lie(X), w), Y)
    di, id_ = Pairing(d(Act(Interior(X), w)), Y), Pairing(Act(Interior(X), d(w)), Y)
    return lhs, Sum(di, id_), Sum(di, Neg(id_))


def test_warn_and_strict_on_refuted_closure(monkeypatch):
    pytest.importorskip("sympy")
    monkeypatch.delenv("JACOPY_ORACLE", raising=False)
    lhs, good, bad = _cartan_case()
    with hook.oracle_mode("warn"):
        assert hook.on_closed(lhs, good).verdict == "AGREE"
        with warnings.catch_warnings(record=True) as rec:
            warnings.simplefilter("always")
            rep = hook.on_closed(lhs, bad)
        assert rep.verdict == "DISAGREE" and any(issubclass(w.category, hook.OracleWarning) for w in rec)
    with hook.oracle_mode("strict"):
        with pytest.raises(hook.OracleDisagreement):
            hook.on_closed(lhs, bad)


def test_prove_and_show_equal_call_the_hook(monkeypatch):
    pytest.importorskip("sympy")
    monkeypatch.delenv("JACOPY_ORACLE", raising=False)
    from jacopy.central.tangent.engine import tangent_engine
    from jacopy.core.registry import PropertyRegistry
    from jacopy.proof import show_equal
    from jacopy.proof.result import prove

    lhs, good, _ = _cartan_case()
    reg = PropertyRegistry()
    eng = tangent_engine(registry=reg)
    hook.REPORTS.clear()
    show_equal(lhs, good, registry=reg, engine=eng)  # off: nothing recorded
    assert not hook.REPORTS
    show_equal(lhs, good, registry=reg, engine=eng, oracle="warn")
    assert hook.REPORTS and hook.REPORTS[-1].source == "ExpandAndSimplify"
    assert hook.REPORTS[-1].verdict == "AGREE"
    res = prove(eng, lhs, good, registry=reg, oracle="warn")
    if res.closed:
        assert hook.REPORTS[-1].source == "prove"
    hook.REPORTS.clear()
