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


@pytest.mark.parametrize("value", ["", "0", "false", "None", "OFF", "no"])
def test_off_aliases(monkeypatch, value):
    monkeypatch.setenv("JACOPY_ORACLE", value)
    assert hook.current_mode() == "off"


def test_unknown_mode_warns_once_and_is_off(monkeypatch):
    monkeypatch.setenv("JACOPY_ORACLE", "loud")
    hook._warned_bad_values.discard("loud")
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        assert hook.current_mode() == "off"
        assert hook.current_mode() == "off"
    assert sum(issubclass(w.category, hook.OracleWarning) for w in rec) == 1
    assert hook.on_closed(Integer(1), Integer(2)) is None


def test_reports_buffer_is_bounded():
    assert hook.REPORTS.maxlen is not None


def test_internal_error_raises_in_strict_records_in_warn(monkeypatch):
    pytest.importorskip("sympy")
    from jacopy.oracle import check

    def boom(*a, **k):
        raise TypeError("realizer bug")

    monkeypatch.setattr(check, "check_equal", boom)
    lhs, good, _ = _cartan_case()
    hook.set_context(nodeid="t-internal")
    with hook.oracle_mode("strict"):
        with pytest.raises(TypeError):
            hook.on_closed(lhs, good)
    hook.set_context(nodeid="t-internal-2")
    with hook.oracle_mode("warn"):
        rep = hook.on_closed(lhs, good)
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "oracle-error:TypeError"
    hook.set_context(nodeid="")


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
    hook.set_context(nodeid="t-prove")
    show_equal(lhs, good, registry=reg, engine=eng)  # off: nothing recorded
    assert not hook.REPORTS
    show_equal(lhs, good, registry=reg, engine=eng, oracle="warn")
    # the inner ExpandAndSimplify closure and the show_equal wrapper are ONE check
    assert len(hook.REPORTS) == 1 and hook.REPORTS[-1].source == "ExpandAndSimplify"
    assert hook.REPORTS[-1].verdict == "AGREE"
    from jacopy.proof.strategies import ExpandAndSimplify, PortfolioStrategy

    hook.set_context(nodeid="t-portfolio")
    hook.REPORTS.clear()
    show_equal(lhs, good, registry=reg, engine=eng, oracle="warn",
               strategy=PortfolioStrategy([ExpandAndSimplify()]))
    assert len(hook.REPORTS) == 1
    hook.set_context(nodeid="t-prove2")
    res = prove(eng, lhs, good, registry=reg, oracle="warn")
    if res.closed:
        assert hook.REPORTS[-1].source == "prove"
    # reflexive closure: trivial AGREE without realization
    rep = hook.on_closed(lhs, lhs, mode="warn")
    assert rep.verdict == "AGREE" and rep.detail.startswith("trivial")
    hook.REPORTS.clear()
    hook.set_context(nodeid="")
