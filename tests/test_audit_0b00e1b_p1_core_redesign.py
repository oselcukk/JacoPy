"""
Audit 0b00e1b-FULL, fix/p1-core redesign (Fable, 2026-10-02): the ten
open findings of the last merge gate, one locking test each.

M1-1 ≡ M1-2 (Scalar = ℝ-constant, ONE predicate
:func:`jacopy.central.calculus.scalars.is_real_constant`):

1. exact ``Graded(0)`` (``functions(...)``) SHADOWS a class-level Scalar —
   ``X(f) = 0`` must not close;
2. the contract is checked on the EFFECTIVE answers on every declaration
   path (exact / class / predicate / retract) in every order;
3. ``NonCommuting`` (and ``AntiCommuting``) is never an ℝ-constant;
4. the model oracle calls the SAME predicate;
5. ``f·D`` is a derivation for a genuine function ``f`` (``D·f`` is not);
6. negative Scalar answers are not hypotheses — the documented
   monotonicity contract (constants are functions);
10. no import cycle around ``annihilates``; cached hot path.

(K1-3 findings 7–9 are locked in ``test_audit_0b00e1b_k1_3_hooks.py``.)

Plus the single-source lock: no ``Scalar`` registry lookup outside the
predicate module, and an adversarial declaration-combination sweep.
"""

from __future__ import annotations

import inspect
import re
import subprocess
import sys
from itertools import product as iproduct
from pathlib import Path

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.algorithms.product_rule import product_rule
from jacopy.algorithms.sort_product import sort_product
from jacopy.central.calculus.scalars import annihilates, is_real_constant
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.objects.multivector import PVector
from jacopy.central.tangent import tangent_engine
from jacopy.central.tangent.schouten import SN
from jacopy.core.expr import Integer, Product, Sum, Symbol
from jacopy.core.properties import (
    AntiCommuting,
    Graded,
    NonCommuting,
    Scalar,
    ScalarContractError,
)
from jacopy.core.registry import PropertyRegistry, track_reads
from jacopy.core.symbolic_degree import Degree
from jacopy.proof.result import prove
from jacopy.proof.strategies import (
    AgreementOnGenerators,
    DerivedBracketStrategy,
    ExpandAndSimplify,
    ProofFailure,
    _is_derivation_expr,
)

ROOT = Path(__file__).resolve().parents[1]


def _status(engine, lhs, rhs, reg):
    return prove(engine, lhs, rhs, registry=reg).status


# --------------------------------------------------------------------- #
# 1. shadowing                                                           #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize("order", ["functions-first", "class-scalar-first"])
def test_1_exact_graded0_shadows_class_scalar(order):
    # the NEW false closure of the last gate: declare_for_class(Symbol,
    # Scalar()) + functions('f') closed X(f) = 0 (main: RESIDUAL)
    reg = PropertyRegistry()
    if order == "class-scalar-first":
        reg.declare_for_class(Symbol, Scalar())
        (f,) = functions("f", registry=reg)
    else:
        (f,) = functions("f", registry=reg)
        reg.declare_for_class(Symbol, Scalar())
    (X,) = vector_fields("X")
    assert reg.get(f, Scalar) is None               # the registry's own answer
    assert reg.get(f, Graded).degree.as_int() == 0
    assert not is_real_constant(f, reg)
    assert product_rule(Act(X, f), reg) == Act(X, f)
    eng = tangent_engine(registry=reg)
    assert _status(eng, Act(X, f), Integer(0), reg) == "RESIDUAL"
    # the undeclared symbol still inherits the class-level constant
    z = Symbol("z")
    assert is_real_constant(z, reg)
    assert _status(eng, Act(X, z), Integer(0), reg) == "CLOSED"
    # and a class-level Graded(0) under an EXACT Scalar: a constant
    reg2 = PropertyRegistry()
    reg2.declare_for_class(Symbol, Graded(0))
    c = Symbol("c")
    reg2.declare(c, Scalar())
    assert is_real_constant(c, reg2)
    assert not is_real_constant(Symbol("g"), reg2)


# --------------------------------------------------------------------- #
# 2. effective answers on every path, order-independent                  #
# --------------------------------------------------------------------- #


def _declarers(reg, w):
    return {
        "exact": lambda p: reg.declare(w, p),
        "class": lambda p: reg.declare_for_class(Symbol, p),
        "predicate": lambda p: reg.declare_for_predicate(
            lambda e: isinstance(e, Symbol), p
        ),
    }


LEVEL = {"exact": 0, "class": 1, "predicate": 2}


@pytest.mark.parametrize("clash", [Graded(1), NonCommuting(), AntiCommuting()])
@pytest.mark.parametrize("ls,lc", list(iproduct(LEVEL, LEVEL)))
@pytest.mark.parametrize("scalar_first", [True, False])
def test_2_contract_on_effective_answers_any_path_any_order(clash, ls, lc, scalar_first):
    # the ONE rule: the clash SHADOWS a strictly less specific Scalar
    # (accepted, w is not a constant); otherwise the pair is REFUSED —
    # whichever of the two is declared second, on whatever path
    reg = PropertyRegistry()
    w = Symbol("w")
    d = _declarers(reg, w)
    steps = [lambda: d[ls](Scalar()), lambda: d[lc](clash)]
    if not scalar_first:
        steps.reverse()
    D = Derivation("D", degree=0)
    if LEVEL[lc] < LEVEL[ls]:                      # shadowed: accepted
        for s in steps:
            s()
        assert reg.get(w, Scalar) is None
        assert not is_real_constant(w, reg)
        assert product_rule(Act(D, w), reg) == Act(D, w)
        return
    if lc == "predicate" and ls != "exact":
        # a predicate cannot be enumerated at declaration time when no
        # exact instance exists: the contradiction is caught at QUERY
        # time (default-reject) — w is never certified a constant
        for s in steps:
            s()
        assert not is_real_constant(w, reg)
        assert product_rule(Act(D, w), reg) == Act(D, w)
        return
    steps[0]()
    with pytest.raises(ScalarContractError):
        steps[1]()
    assert len(reg) == 1                           # the refused mutation was undone
    assert is_real_constant(w, reg) == scalar_first


def test_2_retract_is_rechecked():
    # exact Scalar + exact Graded(0) hide a class-level Graded(1): the
    # retract of the Graded(0) would EXPOSE "constant of degree 1"
    reg = PropertyRegistry()
    x = Symbol("x")
    reg.declare(x, Graded(0))
    reg.declare(x, Scalar())
    reg.declare_for_class(Symbol, Graded(1))
    with pytest.raises(ScalarContractError):
        reg.retract(x, Graded)
    assert reg.get(x, Graded).degree.as_int() == 0   # unchanged
    assert is_real_constant(x, reg)
    # retract_for_class likewise
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Graded(0))
    reg.declare_for_class(Symbol, Scalar())
    reg.declare_for_class(Symbol.__mro__[1], Graded(2))
    with pytest.raises(ScalarContractError):
        reg.retract_for_class(Symbol, Graded)
    assert is_real_constant(Symbol("y"), reg)
    # retracting the shadowing declaration is fine: the symbol becomes
    # the class-level constant it was never said not to be
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    (f,) = functions("f", registry=reg)
    assert not is_real_constant(f, reg)
    reg.retract(f, Graded)
    assert is_real_constant(f, reg)
    # scope() rolls the whole thing back
    reg = PropertyRegistry()
    (g,) = functions("g", registry=reg)
    with reg.scope():
        reg.retract(g, Graded)
        reg.declare(g, Scalar())
        assert is_real_constant(g, reg)
    assert not is_real_constant(g, reg)


# --------------------------------------------------------------------- #
# 3. NonCommuting                                                        #
# --------------------------------------------------------------------- #


def test_3_noncommuting_is_never_a_constant():
    D = Derivation("D", degree=0)
    # same level: refused either way
    for first, second in ((Scalar(), NonCommuting()), (NonCommuting(), Scalar())):
        reg = PropertyRegistry()
        x = Symbol("x")
        reg.declare(x, first)
        with pytest.raises(ScalarContractError):
            reg.declare(x, second)
    # an exact NonCommuting shadows the class-level constant: no swap,
    # no D(x) = 0
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    x = Symbol("x")
    reg.declare(x, NonCommuting())
    reg.declare(x, Graded(0))
    assert not is_real_constant(x, reg)
    assert sort_product(Product(D, x), reg)[0] == Product(D, x)
    assert product_rule(Act(D, x), reg) == Act(D, x)
    # a predicate-level NonCommuting under a class-level Scalar cannot
    # be enumerated at declaration: the predicate rejects at query time
    reg = PropertyRegistry()
    reg.declare_for_predicate(lambda e: isinstance(e, Symbol), NonCommuting())
    reg.declare_for_class(Symbol, Scalar())
    assert not is_real_constant(Symbol("q"), reg)
    assert not annihilates(D, Symbol("q"), reg)
    # AntiCommuting: a non-zero constant cannot anticommute
    reg = PropertyRegistry()
    y = Symbol("y")
    reg.declare(y, AntiCommuting())
    with pytest.raises(ScalarContractError):
        reg.declare(y, Scalar())


# --------------------------------------------------------------------- #
# 4. the oracle calls the one predicate                                  #
# --------------------------------------------------------------------- #


class _Env:
    def __init__(self, registry):
        self.registry = registry


def test_4_oracle_constant_agrees_with_the_engine_predicate_on_function_atoms():
    # gate 5 (chef): the oracle restates the contract INDEPENDENTLY (no
    # engine import — test_oracle_independence) and this differential
    # check locks the two implementations together on the atoms the
    # oracle dispatches to it (a Symbol, a degree-0 Form / PVector —
    # the function-kind half is the oracle caller's dispatch)
    from jacopy.oracle.realize import _declared_constant

    (h,) = forms("h", degree=0)
    cases = []
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    (f,) = functions("f", registry=reg)
    reg.declare(Symbol("s"), Graded(Degree.var("k")))
    reg.declare(Symbol("n"), NonCommuting())
    cases += [(reg, e) for e in (f, Symbol("z"), Symbol("s"), Symbol("n"))]
    reg2 = PropertyRegistry()
    reg2.declare_for_predicate(lambda e: True, Scalar())
    reg2.declare(h, Graded(0))
    reg2.declare_for_class(Symbol, AntiCommuting())
    cases += [(reg2, e) for e in (h, Symbol("t"), PVector("q", degree=0))]
    for r, e in cases:
        assert _declared_constant(e, _Env(r)) == is_real_constant(e, r), e
    # the oracle mints no hypotheses
    with track_reads() as log:
        _declared_constant(Symbol("t"), _Env(reg2))
    assert log == []


def test_4_oracle_models_a_shadowed_scalar_as_a_function():
    pytest.importorskip("sympy")
    from jacopy.oracle.check import check_equal

    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    (f,) = functions("f", registry=reg)
    (X,) = vector_fields("X")
    assert check_equal(Act(X, f), Integer(0), registry=reg, owners=[]).verdict == "DISAGREE"
    assert check_equal(Act(X, Symbol("z")), Integer(0), registry=reg, owners=[]).verdict == "AGREE"


# --------------------------------------------------------------------- #
# 5. f·D is a derivation                                                 #
# --------------------------------------------------------------------- #


def test_5_function_times_derivation_is_a_derivation():
    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    X, Y = vector_fields("X Y")
    c = Symbol("c")
    reg.declare(c, Scalar())
    x = Symbol("x")
    reg.declare(x, Graded(0))
    reg.declare(x, NonCommuting())
    gens = (g,)                                              # a commutative algebra of functions
    assert _is_derivation_expr(Product(f, X), reg, gens)
    assert not _is_derivation_expr(Product(f, g, X), reg, gens)  # gate 6: ONE atom coefficient
    assert _is_derivation_expr(Product(c, X, c), reg)        # constants need no algebra
    assert _is_derivation_expr(Product(Integer(2), f, X), reg, gens)
    assert not _is_derivation_expr(Product(f, X), reg)        # unknown algebra: refused
    assert not _is_derivation_expr(Product(X, f), reg, gens)  # D∘(f·): composition
    assert not _is_derivation_expr(Product(f, X, g), reg, gens)
    assert not _is_derivation_expr(Product(x, X), reg, gens)  # x does not commute
    assert not _is_derivation_expr(Product(f, X, Y), reg, gens)  # two derivations
    # a proof that needs it: f·(X + Y) = f·X + f·Y as operators
    class _Alg:
        generators = (g,)

    chain = AgreementOnGenerators(_Alg()).prove(
        Product(f, Sum(X, Y)), Sum(Product(f, X), Product(f, Y)),
        registry=reg, engine=tangent_engine(registry=reg),
    )
    assert chain is not None
    # and the composition is still refused (M1-2)
    with pytest.raises(ProofFailure, match="DERIVATIONS only"):
        AgreementOnGenerators(_Alg()).prove(
            Product(X, f), Product(f, X), registry=reg,
            engine=tangent_engine(registry=reg),
        )


# --------------------------------------------------------------------- #
# 6. negative answers are not hypotheses (monotonicity)                 #
# --------------------------------------------------------------------- #


def test_6_negative_scalar_answers_are_not_hypotheses():
    from jacopy.proof.registry_facts import facts_from_log, unmet

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    (X,) = vector_fields("X")
    with track_reads() as log:
        assert not is_real_constant(f, reg)
    assert not any(entry[1] is Scalar for entry in log)      # negative: silent
    with track_reads() as log:
        c = Symbol("c")
        reg.declare(c, Scalar())
        assert is_real_constant(c, reg)
    assert {entry[1] for entry in log if entry[0] == c} == {Scalar, Graded, NonCommuting, AntiCommuting}
    # the contract: a Leibniz proof for FUNCTIONS stays citable where
    # one of them is later a constant (constants are functions) …
    eng = tangent_engine(registry=reg)
    lhs = Act(X, Product(f, g))
    rhs = Sum(Product(Act(X, f), g), Product(f, Act(X, g)))
    chain = ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng)
    facts = tuple(
        fact for step in chain for fact in (getattr(step, "registry_facts", ()) or ())
    )
    assert facts, "the proof consulted the registry"
    assert not any(fact.prop_cls is Scalar and fact.value is None for fact in facts)
    const = PropertyRegistry()
    const.declare(g, Graded(0))
    const.declare(f, Graded(0))
    const.declare(f, Scalar())
    assert unmet(facts, const) == ()
    # … while a proof that USED "c is Scalar" is not citable where c is
    # a function (the positive fact is recorded)
    r2 = prove(eng, Act(X, c), Integer(0), registry=reg)
    assert r2.closed
    facts2 = tuple(
        fact for step in r2.chain for fact in (getattr(step, "registry_facts", ()) or ())
    )
    fun = PropertyRegistry()
    fun.declare(c, Graded(0))
    assert any(u.prop_cls is Scalar for u in unmet(facts2, fun))


# --------------------------------------------------------------------- #
# 10. no import cycle, cached hot path                                  #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "first",
    [
        "jacopy.central.calculus.scalars",
        "jacopy.algorithms.product_rule",
        "jacopy.algebra.commutator",
        "jacopy.core.registry",
        "jacopy.central.objects.kind",
    ],
)
def test_10_predicate_modules_import_in_any_order(first):
    code = (
        f"import {first}; import jacopy.central.calculus.scalars as s; "
        "import jacopy.algorithms.product_rule as p; "
        "assert s.annihilates.__module__ == 'jacopy.central.calculus.scalars'"
    )
    subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)


def test_10_annihilates_has_no_late_import_and_the_hot_path_caches():
    pr = sys.modules["jacopy.algorithms.product_rule"]  # the package re-exports the function under the same name

    assert "import" not in inspect.getsource(annihilates).split('"""')[-1]
    reg = PropertyRegistry()
    c = Symbol("c")
    reg.declare(c, Scalar())
    pr._ANNIHILATES = None
    assert product_rule(Act(Derivation("D", degree=1), c), reg) == Integer(0)
    assert pr._ANNIHILATES is annihilates


# --------------------------------------------------------------------- #
# single source: no Scalar lookup outside the predicate module          #
# --------------------------------------------------------------------- #


def test_no_scalar_registry_lookup_outside_the_predicate():
    pattern = re.compile(r"\.(has|get|peek)\(\s*[^,()]+,\s*Scalar\s*\)")
    offenders = []
    for path in sorted((ROOT / "jacopy").rglob("*.py")):
        if path.name == "scalars.py" and path.parent.name == "calculus":
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not offenders, offenders


# --------------------------------------------------------------------- #
# adversarial sweep: every declaration combination, main-safe closures  #
# --------------------------------------------------------------------- #


def _combos():
    props = {"S": Scalar(), "G0": Graded(0), "G1": Graded(1), "NC": NonCommuting()}
    levels = ("exact", "class", "predicate")
    for n in (1, 2):
        for names in iproduct(props, repeat=n):
            if len(set(names)) < n:
                continue
            for lv in iproduct(levels, repeat=n):
                yield tuple(zip(names, lv))


@pytest.mark.parametrize("combo", list(_combos()), ids=lambda c: "+".join(f"{n}@{l}" for n, l in c))
def test_sweep_constant_iff_unshadowed_scalar_without_clash(combo):
    # the predicate's answer for the declared symbol must equal the
    # rule stated in core.properties.Scalar on the declarations that
    # SURVIVED (a refused one is undone) — and a closure X(w) = 0 must
    # follow it exactly
    reg = PropertyRegistry()
    w = Symbol("w")
    d = _declarers(reg, w)
    props = {"S": Scalar(), "G0": Graded(0), "G1": Graded(1), "NC": NonCommuting()}
    applied = {}
    for name, lv in combo:
        try:
            d[lv](props[name])
        except (ScalarContractError, ValueError):
            continue
        applied[name] = LEVEL[lv]
    expected = False
    if "S" in applied:
        ls = applied["S"]
        shadowed = any(applied[n] < ls for n in ("G0", "G1", "NC") if n in applied)
        clash = any(applied[n] >= ls for n in ("G1", "NC") if n in applied)
        expected = not shadowed and not clash
    assert is_real_constant(w, reg) == expected, (combo, applied)
    (X,) = vector_fields("X")
    status = _status(tangent_engine(registry=reg), Act(X, w), Integer(0), reg)
    assert (status == "CLOSED") == expected, (combo, applied, status)
