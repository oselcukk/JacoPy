"""
Audit 0b00e1b-FULL, fix/p1-core gate 5 (Fable, tur 2): every probe of
``scratchpad-kopya/p1core-cr5`` and ``p1core-gate5`` as a permanent test.

1. ``f·D`` is a derivation ONLY when the coefficient is certified to
   commute with every generator (cr5/p02 [a][b], gate5/p8, p7);
   control [c], ``f(X+Y) = fX + fY`` and ``(fX)(gh)`` keep closing.
2. The derivation certificate's reads are hypotheses of the
   AgreementOnGenerators step (cr5/p04, gate5/p4b).
3. Visibility filters never hide a clash (gate5/p6 F1).
4. A predicate written for one node type may raise on another
   exact-declared expression (cr5/p03 (1)).
5. Compound constants (gate5/p2, cr5/p03 (5)).
6. Oracle independence: differential lock over every declaration
   combination (chef decision).
"""

from __future__ import annotations

from itertools import product as iproduct

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.central.calculus.scalars import is_real_constant
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.tangent import tangent_engine
from jacopy.core.expr import Integer, Neg, Product, Sum, Symbol
from jacopy.core.properties import (
    AntiCommuting,
    Graded,
    NonCommuting,
    Scalar,
    ScalarContractError,
)
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.proof.expansion import Definition, ExpansionEngine, ExplicitAssumption
from jacopy.proof.registry_facts import facts_of, registry_context, unmet
from jacopy.proof.result import Goal, ProofResult, prove
from jacopy.proof.strategies import AgreementOnGenerators, ProofFailure, _is_derivation_expr
from jacopy.proof.theorems import Theorem, TheoremDefinition, check_citation
from jacopy.proof.verifier import prove_operator_equation


# --------------------------------------------------------------------- #
# 1. f·D needs a commuting coefficient                                   #
# --------------------------------------------------------------------- #


def _cD_eq_E(coeff_props, gen_props):
    """cr5/p02: D(x)=u, D(y)=v, E(x)=c·u, E(y)=c·v; c·D = E holds iff c
    commutes with the algebra."""
    reg = PropertyRegistry()
    c, u, v, x, y = (Symbol(n) for n in "cuvxy")
    for s in (u, v):
        reg.declare(s, Graded(0))
    for p in coeff_props:
        reg.declare(c, p)
    for s in (x, y):
        for p in gen_props:
            reg.declare(s, p)
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    vals = {(D, x): u, (D, y): v, (E, x): Product(c, u), (E, y): Product(c, v)}

    class Gen(Definition):
        name = "D,E on generators"
        anchor = Act

        def matches(self, e):
            return isinstance(e, Act) and (e.op, e.arg) in vals

        def rewrite(self, e):
            return vals[(e.op, e.arg)]

    class Alg:
        generators = (x, y)

    return prove_operator_equation(Product(c, D), E, Alg(), registry=reg, engine=ExpansionEngine([Gen()]))


@pytest.mark.parametrize(
    "coeff,gens",
    [
        ([Graded(0), AntiCommuting()], [Graded(0), AntiCommuting()]),   # [a] 2·c·v·x
        ([Graded(0)], [Graded(0), NonCommuting()]),                    # [b] c·x·v − x·c·v
        ([Graded(0), NonCommuting()], [Graded(0)]),
        ([Graded(0)], [Graded(0), AntiCommuting()]),
        ([Graded(0), AntiCommuting()], [Graded(0)]),
        ([Graded(1)], [Graded(0)]),                                    # a 1-form is no coefficient
    ],
)
def test_1_cD_eq_E_refused_without_commutation(coeff, gens):
    with pytest.raises(ProofFailure, match="DERIVATIONS only"):
        _cD_eq_E(coeff, gens)


def test_1_cD_eq_E_control_closes():
    assert _cD_eq_E([Graded(0)], [Graded(0)]) is not None          # [c]
    assert _cD_eq_E([Scalar()], [Graded(0), NonCommuting()]) is not None   # a constant always commutes
    assert _cD_eq_E([Scalar()], [Graded(0), AntiCommuting()]) is not None


def test_1_gate5_p8_anticommuting_coefficient_is_refused():
    reg = PropertyRegistry()
    f, g, h = Symbol("f"), Symbol("g"), Symbol("h")
    for s in (f, g, h):
        reg.declare(s, Graded(0))
        reg.declare(s, AntiCommuting())
    X, Y = vector_fields("X Y")
    eng = tangent_engine(registry=reg)
    eng.register(ExplicitAssumption(Act(Y, g), Product(f, Act(X, g))))
    eng.register(ExplicitAssumption(Act(Y, h), Product(f, Act(X, h))))

    class A:
        generators = (g, h)

    with pytest.raises(ProofFailure, match="DERIVATIONS only"):
        AgreementOnGenerators(A()).prove(Product(f, X), Y, registry=reg, engine=eng)
    assert not _is_derivation_expr(Product(f, X), reg, (g, h))       # gate5/p7
    (t,) = (Symbol("t"),)
    reg.declare(t, Graded(1))
    assert not _is_derivation_expr(Product(t, X), reg, (g, h))


def test_1_correct_fD_identities_keep_closing():
    reg = PropertyRegistry()
    f, g, h = functions("f g h", registry=reg)
    X, Y = vector_fields("X Y")
    eng = tangent_engine(registry=reg)

    class A:
        generators = (g,)

    assert AgreementOnGenerators(A()).prove(
        Product(f, Sum(X, Y)), Sum(Product(f, X), Product(f, Y)), registry=reg, engine=eng
    ) is not None
    r = prove(eng, Act(Product(f, X), Product(g, h)),
              Product(f, Sum(Product(Act(X, g), h), Product(g, Act(X, h)))), registry=reg)
    assert r.status in ("CLOSED", "RESIDUAL")  # the product-rule shape is the same as before this turn
    from jacopy.algorithms.product_rule import product_rule
    assert product_rule(Act(Product(f, X), Product(g, h)), reg) == Product(
        f, Sum(Product(Act(X, g), h), Product(g, Act(X, h)))
    )
    # generators of form kind: a degree-0 function commutes with them
    (w,) = forms("w", degree=1)
    assert _is_derivation_expr(Product(f, X), reg, (g, w))
    # a vector-field generator (operator kind): unknown commutation, refused
    assert not _is_derivation_expr(Product(f, X), reg, (g, Y))


# --------------------------------------------------------------------- #
# 2. certificate reads are hypotheses                                   #
# --------------------------------------------------------------------- #


def test_2_cD_eq_E_not_citable_where_c_is_noncommuting():
    c, u, v, x, y = (Symbol(n) for n in "cuvxy")
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    vals = {(D, x): u, (D, y): v, (E, x): Product(c, u), (E, y): Product(c, v)}

    class Gen(Definition):
        name = "D,E on generators"
        anchor = Act

        def matches(self, e):
            return isinstance(e, Act) and (e.op, e.arg) in vals

        def rewrite(self, e):
            return vals[(e.op, e.arg)]

    class Alg:
        generators = (x, y)

    def mk(nc):
        r = PropertyRegistry()
        for s in (u, v, x, y, c):
            r.declare(s, Graded(0))
        if nc:
            r.declare(c, NonCommuting())
        return r

    src, tgt = mk(False), mk(True)
    with pytest.raises(ProofFailure):
        prove_operator_equation(Product(c, D), E, Alg(), registry=tgt, engine=ExpansionEngine([Gen()]))
    chain = prove_operator_equation(Product(c, D), E, Alg(), registry=src, engine=ExpansionEngine([Gen()]))
    thm = Theorem("cD=E", "c·D = E", Product(c, D), E, chain).with_structural_requires()
    names = {str(f) for f in thm.registry_facts}
    assert any(n.startswith("c has no NonCommuting declared") for n in names)
    assert any(n.startswith("x has no AntiCommuting declared") for n in names)
    eng = ExpansionEngine([Gen(), TheoremDefinition(thm)])
    assert not check_citation(thm, eng, registry=tgt).ok
    assert prove(eng, Product(c, D), E, registry=tgt).status == "RESIDUAL"
    assert check_citation(thm, eng, registry=src).ok


def test_2_gate5_p4b_facts_name_the_coefficient():
    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    X, Y = vector_fields("X Y")
    eng = tangent_engine(registry=reg)

    class A:
        generators = (g,)

    lhs, rhs = Product(f, Sum(X, Y)), Sum(Product(f, Y), Product(f, X))
    with registry_context(reg):
        chain = AgreementOnGenerators(A()).prove(lhs, rhs, registry=reg, engine=eng)
    facts = facts_of(ProofResult.from_chain(chain, Goal(lhs, rhs)).requires)
    bad = PropertyRegistry()
    bad.declare(f, Graded(0))
    bad.declare(f, NonCommuting())
    bad.declare(g, Graded(0))
    assert any(u.expr == f and u.prop_cls is NonCommuting for u in unmet(facts, bad))


# --------------------------------------------------------------------- #
# 3. filters never hide a clash                                         #
# --------------------------------------------------------------------- #


def test_3_axioms_filter_does_not_make_a_graded_element_a_constant():
    (X,) = vector_fields("X")
    is_sym = lambda e: isinstance(e, Symbol)  # noqa: E731
    r = PropertyRegistry()
    w = Symbol("w")
    r.declare_for_predicate(is_sym, Scalar())
    r.declare_for_predicate(is_sym, Graded(1))          # not enumerable: query-time reject
    assert not is_real_constant(w, r)
    with r.axioms([Scalar]):
        assert r.get(w, Graded) is None                  # the filter hides it from readers …
        assert not is_real_constant(w, r)                # … but the clash is decided on the raw data
        assert prove(tangent_engine(registry=r), Act(X, w), Integer(0), registry=r).status == "RESIDUAL"
    r2 = PropertyRegistry()
    r2.declare_for_class(Symbol, Scalar())
    (f,) = functions("f", registry=r2)
    with r2.axioms([Scalar]):
        assert r2.get(f, Scalar) is None                 # shadowing is raw too
        assert not is_real_constant(f, r2)
    with r2.axioms([Graded]):
        assert not is_real_constant(Symbol("z"), r2)     # a filtered-out Scalar is not usable


# --------------------------------------------------------------------- #
# 4. raising predicates                                                 #
# --------------------------------------------------------------------- #


def test_4_predicate_raising_on_a_foreign_node_is_no_match():
    reg = PropertyRegistry()
    reg.declare(Product(Symbol("a"), Symbol("b")), Graded(0))
    reg.declare_for_predicate(lambda e: e.name.startswith("k"), Scalar())
    assert len(reg) == 2
    assert is_real_constant(Symbol("k1"), reg)
    (a,) = forms("a", degree=1)
    reg2 = PropertyRegistry()
    reg2.declare(a, Graded(1))
    reg2.declare_for_predicate(lambda e: e.name.startswith("c"), Scalar())
    # (an exact Graded(1) SHADOWS a predicate Scalar — accepted, not a
    # constant; the clash is refused where the Scalar is more specific)
    reg3 = PropertyRegistry()
    reg3.declare(Symbol("k"), Graded(1))
    reg3.declare_for_predicate(lambda e: e.name.startswith("k"), Scalar())
    assert not is_real_constant(Symbol("k"), reg3) and is_real_constant(Symbol("k2"), reg3)
    reg4 = PropertyRegistry()
    reg4.declare_for_predicate(lambda e: e.name.startswith("k"), Graded(1))
    with pytest.raises(ScalarContractError):
        reg4.declare(Symbol("k"), Scalar())


# --------------------------------------------------------------------- #
# 5. compound constants                                                 #
# --------------------------------------------------------------------- #


def test_5_compound_constants():
    reg = PropertyRegistry()
    c, d = Symbol("c"), Symbol("d")
    reg.declare(c, Scalar())
    reg.declare(d, Scalar())
    f, g = functions("f g", registry=reg)
    X, Y = vector_fields("X Y")
    p = Symbol("p")
    reg.declare(p, Scalar())
    reg.declare(p, Graded(Degree.var("k")))
    for e in (Integer(3), Neg(Integer(2)), Product(Integer(2), c), Sum(c, Integer(1)), Neg(c), Product(c, d)):
        assert is_real_constant(e, reg), e
    for e in (p, Product(c, f), Sum(f, c), Act(Y, c), Act(X, f)):
        assert not is_real_constant(e, reg), e
    eng = tangent_engine(registry=reg)
    st = lambda l, r: prove(eng, l, r, registry=reg).status  # noqa: E731
    assert st(Act(X, Product(c, d)), Integer(0)) == "CLOSED"
    assert st(Act(X, Sum(c, Integer(1))), Integer(0)) == "CLOSED"
    assert st(Act(X, Neg(c)), Integer(0)) == "CLOSED"
    assert st(Act(X, Product(Integer(2), c)), Integer(0)) == "CLOSED"
    assert st(Act(X, Act(Y, c)), Integer(0)) == "CLOSED"
    assert st(Act(X, p), Integer(0)) == "RESIDUAL"
    for lhs in (Product(f, g), Product(c, f), Sum(f, c), Act(Y, f), Act(Product(c, X), g), f):
        assert st(Act(X, lhs) if not isinstance(lhs, Act) or lhs.op is not Product else lhs, Integer(0)) == "RESIDUAL", lhs


# --------------------------------------------------------------------- #
# 6. oracle independence — differential lock                            #
# --------------------------------------------------------------------- #


class _Env:
    def __init__(self, registry):
        self.registry = registry


_PROPS = {"S": Scalar, "G0": lambda: Graded(0), "G1": lambda: Graded(1), "Gk": lambda: Graded(Degree.var("k")),
          "NC": NonCommuting, "AC": AntiCommuting}
_LEVELS = ("exact", "class", "predicate")


def _combos():
    for n in (1, 2, 3):
        for names in iproduct(_PROPS, repeat=n):
            if len(set(names)) < n:
                continue
            for lv in iproduct(_LEVELS, repeat=n):
                yield tuple(zip(names, lv))


@pytest.mark.parametrize("combo", list(_combos()), ids=lambda c: "+".join(f"{n}@{l}" for n, l in c))
def test_6_oracle_and_engine_constant_predicates_agree(combo):
    from jacopy.oracle.realize import _declared_constant

    reg = PropertyRegistry()
    w = Symbol("w")
    for name, lv in combo:
        p = _PROPS[name]()
        try:
            if lv == "exact":
                reg.declare(w, p)
            elif lv == "class":
                reg.declare_for_class(Symbol, p)
            else:
                reg.declare_for_predicate(lambda e: isinstance(e, Symbol), p)
        except (ScalarContractError, ValueError):
            continue
    assert _declared_constant(w, _Env(reg)) == is_real_constant(w, reg), combo
    with reg.axioms([Scalar]):
        assert _declared_constant(w, _Env(reg)) == is_real_constant(w, reg), ("axioms", combo)
