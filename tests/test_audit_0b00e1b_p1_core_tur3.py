"""
Audit 0b00e1b-FULL, fix/p1-core gate 6 (Fable, tur 3): every probe of
``scratchpad-kopya/p1core-cr6`` (p01–p06) and ``p1core-gate6`` (g1–g4)
as a permanent test.

1. f·D NARROWED: the coefficient is an ℝ-constant (compound constants
   included) or ONE atom function symbol; every generator an atom of
   function / form kind; no raw NonCommuting / AntiCommuting anywhere
   (cr6/p01, p03; gate6/g3). Documented completeness loss: a TRUE
   identity with a compound coefficient, ``(c + b)·D = E`` or
   ``c·b·D = E``, is no longer certified — name the coefficient as one
   function symbol to use the shortcut.
2. The certificate reads raw declarations (gate6/g1: no filter hides a
   commutation constraint).
3. Raw contract reads are RAW facts, checked against the raw
   declarations of the citing registry (cr6/p05).
4. The oracle's independent restatement agrees with the engine across
   the class hierarchy, every ``axioms`` subset and strict / DERIVED
   (cr6/p04, gate6/g4).
5. Compound constants: a raw declaration on the node itself wins
   (gate6/g2, cr6/p06); dead ``_certify_derivation`` removed.
"""

from __future__ import annotations

from itertools import product as iproduct

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.central.calculus.scalars import is_real_constant
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.objects.form import Form
from jacopy.central.objects.multivector import PVector
from jacopy.central.tangent import tangent_engine
from jacopy.core.expr import Atom, Integer, Neg, Power, Product, Sum, Symbol
from jacopy.core.properties import (
    AntiCommuting,
    Graded,
    NonCommuting,
    ProofRef,
    Provenance,
    Scalar,
    ScalarContractError,
)
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.result import prove
from jacopy.proof.strategies import AgreementOnGenerators, ProofFailure, _is_derivation_expr
from jacopy.proof.theorems import Theorem, TheoremDefinition, check_citation
from jacopy.proof.verifier import prove_operator_equation

PR = ProofRef("probe")


def _operator_equation(reg, c, gens, deg=0, lhs=None, e_val=None):
    """D(g) = u_g, E(g) = c·u_g (or ``e_val(c, u_g)``); ``lhs`` defaults
    to c·D. Returns the chain or raises ProofFailure."""
    D, E = Derivation("D", degree=deg), Derivation("E", degree=deg)
    vals = {}
    for i, g in enumerate(gens):
        u = Symbol(f"u{i}")
        gdeg = reg.get(g, Graded)
        if reg.get(u, Graded) is None:   # the helper may run twice on one registry
            reg.declare(u, Graded(deg + (gdeg.degree.as_int() or 0 if gdeg is not None else 0)))
        vals[(D, g)] = u
        vals[(E, g)] = Product(c, u) if e_val is None else e_val(c, u)

    class Gen(Definition):
        name = "D,E on generators"
        anchor = Act

        def matches(self, e):
            return isinstance(e, Act) and (e.op, e.arg) in vals

        def rewrite(self, e):
            return vals[(e.op, e.arg)]

    class Alg:
        generators = tuple(gens)

    L = Product(c, D) if lhs is None else lhs(c, D)
    return prove_operator_equation(L, E, Alg(), registry=reg, engine=ExpansionEngine([Gen()]))


def _reg_fna():
    reg = PropertyRegistry()
    f, n, a, x, y = (Symbol(s) for s in "fnaxy")
    for s in (f, n, a, x, y):
        reg.declare(s, Graded(0))
    reg.declare(n, NonCommuting())
    reg.declare(a, AntiCommuting())
    return reg, f, n, a, x, y


# --------------------------------------------------------------------- #
# 1. narrowing                                                           #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "coeff",
    [
        lambda f, n, a: Sum(f, n), lambda f, n, a: Sum(f, a), lambda f, n, a: Power(n, Integer(2)),
        lambda f, n, a: n, lambda f, n, a: Neg(n), lambda f, n, a: Product(f, n),
        lambda f, n, a: Sum(Integer(2), n), lambda f, n, a: Sum(f, Product(f, n)),
        lambda f, n, a: Act(vector_fields("X")[0], n), lambda f, n, a: a,
        # compound coefficients WITHOUT a hidden leaf: refused too (narrowing)
        lambda f, n, a: Sum(f, f), lambda f, n, a: Neg(f), lambda f, n, a: Product(f, f),
        lambda f, n, a: Act(vector_fields("X")[0], f),
    ],
    ids=["f+n", "f+a", "n^2", "n", "-n", "f*n", "2+n", "f+f*n", "X(n)", "a", "f+f", "-f", "f*f", "X(f)"],
)
def test_1_compound_or_noncommuting_coefficient_is_refused(coeff):
    reg, f, n, a, x, y = _reg_fna()
    c = coeff(f, n, a)
    assert not _is_derivation_expr(Product(c, Derivation("D", degree=0)), reg, (x, y))
    with pytest.raises(ProofFailure, match="DERIVATIONS only"):
        _operator_equation(reg, c, (x, y))


def test_1_compound_generators_are_refused():
    reg, f, n, a, x, y = _reg_fna()
    D = Derivation("D", degree=0)
    for g in (Sum(x, n), Product(x, n), Sum(x, y), Neg(x)):
        assert not _is_derivation_expr(Product(f, D), reg, (x, g))
    assert _is_derivation_expr(Product(f, D), reg, (x, y))
    # a compound CONSTANT coefficient stays accepted (constants commute)
    c = Symbol("c")
    reg.declare(c, Scalar())
    for k in (Product(Integer(2), c), Sum(c, Integer(1)), Neg(c)):
        assert _is_derivation_expr(Product(k, D), reg, (x, y))
        assert _is_derivation_expr(Product(D, k), reg, (x, y))


def test_1_atom_coefficient_identities_keep_closing():
    # cr6/p01 [6] [9], gate6/g3: odd D / odd, mixed, symbolic-degree generators
    for deg, gdegs in ((1, (1, 1)), (1, (0, 1)), (0, (1, 1)), (1, (Degree.var("k"), Degree.var("k")))):
        reg = PropertyRegistry()
        f, x, y = Symbol("f"), Symbol("x"), Symbol("y")
        reg.declare(f, Graded(0))
        reg.declare(x, Graded(gdegs[0]))
        reg.declare(y, Graded(gdegs[1]))
        assert _operator_equation(reg, f, (x, y), deg=deg) is not None
    reg = PropertyRegistry()
    c, b, x, y = (Symbol(s) for s in "cbxy")
    for s in (c, b, x, y):
        reg.declare(s, Graded(0))
    # outer Sum / Neg structure recurses
    assert _operator_equation(reg, c, (x, y), lhs=lambda c, D: Neg(Product(c, D)),
                              e_val=lambda c, u: Neg(Product(c, u))) is not None
    F = Derivation("F", degree=0)
    assert _is_derivation_expr(Sum(Product(c, Derivation("D", degree=0)), Product(b, F)), reg, (x, y))


def test_1_documented_completeness_loss_compound_true_identities():
    # (c + b)·D = E and c·b·D = E are TRUE on a commutative algebra of
    # functions but no longer certified (gate-6 narrowing); naming the
    # coefficient as one function symbol h recovers the shortcut
    reg = PropertyRegistry()
    c, b, h, x, y = (Symbol(s) for s in "cbhxy")
    for s in (c, b, h, x, y):
        reg.declare(s, Graded(0))
    for coeff in (Sum(c, b), Product(c, b)):
        with pytest.raises(ProofFailure, match="DERIVATIONS only"):
            _operator_equation(reg, coeff, (x, y))
        assert not _is_derivation_expr(Product(coeff, Derivation("D", degree=0)), reg, (x, y))
    assert _operator_equation(reg, h, (x, y)) is not None
    D, X = Derivation("D", degree=0), vector_fields("X")[0]
    assert not _is_derivation_expr(Product(c, b, D), reg, (x, y))   # two function factors
    assert not _is_derivation_expr(Product(c, X), reg, None)        # unknown algebra


# --------------------------------------------------------------------- #
# 2. raw reads in the certificate                                       #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize("filt", ["axioms-graded", "axioms-graded-scalar", "strict-derived"])
@pytest.mark.parametrize("which", ["coeff-and-gens-AC", "gens-NC"])
def test_2_filters_never_hide_a_commutation_constraint(filt, which):
    strict = filt == "strict-derived"
    reg = PropertyRegistry(strict_axioms_only=strict)
    c, x, y = Symbol("c"), Symbol("x"), Symbol("y")
    for s in (c, x, y):
        reg.declare(s, Graded(0))
    mk = (lambda cls: cls(provenance=Provenance.DERIVED, proof=PR)) if strict else (lambda cls: cls())
    if which == "coeff-and-gens-AC":
        for s in (c, x, y):
            reg.declare(s, mk(AntiCommuting))
    else:
        for s in (x, y):
            reg.declare(s, mk(NonCommuting))
    ctx = reg.axioms([Graded] if filt == "axioms-graded" else [Graded, Scalar]) if not strict else None
    if ctx is None:
        with pytest.raises(ProofFailure, match="DERIVATIONS only"):
            _operator_equation(reg, c, (x, y))
    else:
        with ctx:
            with pytest.raises(ProofFailure, match="DERIVATIONS only"):
                _operator_equation(reg, c, (x, y))
    # control: the TRUE identity under the same filter
    reg2 = PropertyRegistry()
    for s in (c, x, y):
        reg2.declare(s, Graded(0))
    with reg2.axioms([Graded]):
        assert _operator_equation(reg2, c, (x, y)) is not None


# --------------------------------------------------------------------- #
# 3. raw facts in citations                                             #
# --------------------------------------------------------------------- #


def test_3_raw_contract_reads_are_citation_hypotheses():
    D, y = Derivation("D", degree=0), Symbol("y")
    src = PropertyRegistry()
    src.declare(y, Scalar())
    r = prove(ExpansionEngine(), Act(D, y), Integer(0), registry=src)
    assert r.closed
    thm = Theorem("dy0", "D(y) = 0", Act(D, y), Integer(0), r.chain).with_structural_requires()
    assert any(f.raw and f.prop_cls is Graded for f in thm.registry_facts)
    tgt = PropertyRegistry()
    is_sym = lambda e: isinstance(e, Symbol)  # noqa: E731
    tgt.declare_for_predicate(is_sym, Scalar())
    tgt.declare_for_predicate(is_sym, Graded(1))
    eng = ExpansionEngine([TheoremDefinition(thm)])
    with tgt.axioms([Scalar]):
        assert not is_real_constant(y, tgt)
        assert prove(ExpansionEngine(), Act(D, y), Integer(0), registry=tgt).status == "RESIDUAL"
        assert not check_citation(thm, eng, registry=tgt).ok
        assert prove(eng, Act(D, y), Integer(0), registry=tgt).status == "RESIDUAL"
    assert check_citation(thm, eng, registry=src).ok


# --------------------------------------------------------------------- #
# 4. oracle restatement: hierarchy, filters, strict                     #
# --------------------------------------------------------------------- #


class _Env:
    def __init__(self, registry):
        self.registry = registry


class _Coord(Symbol):
    pass


_PROPS = {
    "S": lambda: Scalar(), "Sd": lambda: Scalar(provenance=Provenance.DERIVED, proof=PR),
    "G0": lambda: Graded(0), "G1": lambda: Graded(1), "Gk": lambda: Graded(Degree.var("k")),
    "NC": lambda: NonCommuting(), "NCd": lambda: NonCommuting(provenance=Provenance.DERIVED, proof=PR),
    "AC": lambda: AntiCommuting(),
}
_LEVELS = ("exact", "class:Coord", "class:Symbol", "class:Atom", "predicate")
_FILTERS = {"none": None, "empty": [], "S": [Scalar], "G": [Graded], "GS": [Graded, Scalar],
            "all": [Scalar, Graded, NonCommuting, AntiCommuting]}


def _declare(reg, w, name, level):
    p = _PROPS[name]()
    if level == "exact":
        reg.declare(w, p)
    elif level.startswith("class:"):
        reg.declare_for_class({"Coord": _Coord, "Symbol": Symbol, "Atom": Atom}[level[6:]], p)
    else:
        reg.declare_for_predicate(lambda e: isinstance(e, Symbol), p)


def _combos():
    for n in (1, 2):
        for names in iproduct(_PROPS, repeat=n):
            if len(set(names)) < n:
                continue
            for lv in iproduct(_LEVELS, repeat=n):
                yield tuple(zip(names, lv))


@pytest.mark.contract_table
def test_4_oracle_and_engine_agree_over_hierarchy_filters_and_strict():
    # ONE test over the whole table: 1–2 declarations from {S, DERIVED S,
    # G0, G1, Gk, NC, DERIVED NC, AC} at exact / class (subclass, Symbol,
    # Atom) / predicate level × every axioms subset × axiom / strict mode
    # = 17 280 comparisons on a Symbol-subclass instance; the first
    # mismatch names its combination
    from jacopy.oracle.realize import _declared_constant

    checked = 0
    for combo in _combos():
        for strict in (False, True):
            reg = PropertyRegistry(strict_axioms_only=strict)
            w = _Coord("w")
            for name, lv in combo:
                try:
                    _declare(reg, w, name, lv)
                except (ScalarContractError, ValueError):
                    continue
            for filt, allowed in _FILTERS.items():
                if allowed is None:
                    assert _declared_constant(w, _Env(reg)) == is_real_constant(w, reg), (combo, strict)
                else:
                    with reg.axioms(allowed):
                        assert _declared_constant(w, _Env(reg)) == is_real_constant(w, reg), (combo, strict, filt)
                checked += 1
    assert checked == 17280


def test_4_oracle_corners_from_the_probes():
    from jacopy.oracle.realize import _declared_constant

    (h,) = forms("h", degree=0)
    w = Symbol("w")
    cases = []
    r = PropertyRegistry(); r.declare_for_class(Atom, Scalar()); r.declare_for_class(Symbol, Graded(0))
    cases.append((r, w, False))                       # MRO depth: Graded(0)@Symbol shadows Scalar@Atom
    r = PropertyRegistry(); r.declare_for_class(Atom, Scalar()); r.declare_for_class(Form, Graded(0))
    cases.append((r, h, False))
    r = PropertyRegistry(); r.declare_for_class(Symbol, Scalar()); r.declare_for_class(Symbol, Graded(0))
    cases.append((r, w, True))                        # same class: a constant
    r = PropertyRegistry(strict_axioms_only=True); r.declare(w, Scalar(provenance=Provenance.DERIVED, proof=PR))
    cases.append((r, w, False))
    r = PropertyRegistry(); r.declare(w, Scalar()); r.declare(w, Graded(Degree.var("k") - Degree.var("k")))
    cases.append((r, w, True))
    for reg, e, expected in cases:
        assert _declared_constant(e, _Env(reg)) == is_real_constant(e, reg) == expected, (reg, e)
    r = PropertyRegistry(); r.declare(w, Scalar())
    for allowed in ([Graded], []):
        with r.axioms(allowed):
            assert _declared_constant(w, _Env(r)) == is_real_constant(w, r) is False
    with r.axioms([Scalar]):
        assert _declared_constant(w, _Env(r)) == is_real_constant(w, r) is True


# --------------------------------------------------------------------- #
# 5. compound constants: the node's own declaration; dead code          #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize("prop", [Graded(1), NonCommuting(), AntiCommuting()], ids=["G1", "NC", "AC"])
def test_5_raw_declaration_on_the_compound_node_wins(prop):
    reg = PropertyRegistry()
    c, k = Symbol("c"), Symbol("k")
    reg.declare(c, Scalar())
    reg.declare(k, Scalar())
    (X,) = vector_fields("X")
    ck = Product(c, k)
    assert is_real_constant(ck, reg)
    assert prove(tangent_engine(registry=reg), Act(X, ck), Integer(0), registry=reg).status == "CLOSED"
    reg.declare(ck, prop)
    assert not is_real_constant(ck, reg)
    assert prove(tangent_engine(registry=reg), Act(X, ck), Integer(0), registry=reg).status == "RESIDUAL"
    reg2 = PropertyRegistry()
    reg2.declare(c, Scalar())
    reg2.declare(k, Scalar())
    reg2.declare(ck, Graded(0))                       # a degree-0 declaration does not contradict
    assert is_real_constant(ck, reg2)


def test_5_compound_constants_never_zero_a_non_constant():
    reg = PropertyRegistry()
    c, e = Symbol("c"), Symbol("e")
    reg.declare(c, Scalar())
    reg.declare(e, Scalar())
    (f,) = functions("f", registry=reg)
    X, Y = vector_fields("X Y")
    (w1,) = forms("w1", degree=1)
    (w0,) = forms("w0", degree=0)
    reg.declare(w0, Scalar())
    a = Symbol("a")
    reg.declare(a, Graded(0))
    reg.declare(a, AntiCommuting())
    q2 = PVector("q2", degree=2)
    reg.declare(q2, Scalar())                         # a bivector "constant": kind refuses it
    eng = tangent_engine(registry=reg)
    st = lambda arg: prove(eng, Act(Y, arg), Integer(0), registry=reg).status  # noqa: E731
    for arg in (Product(c, w1), Product(c, X), Product(c, f), Product(c, a), Product(c, Act(X, f)),
                Sum(c, f), Neg(Product(c, f)), Product(c, q2)):
        assert not is_real_constant(arg, reg), arg
        assert st(arg) == "RESIDUAL", arg
    for arg in (Sum(c, Neg(c)), Sum(Product(c, e), Integer(1)), Product(c, w0), Sum(c, e, Integer(1))):
        assert is_real_constant(arg, reg), arg
        assert st(arg) == "CLOSED", arg


def test_5_dead_certify_derivation_removed():
    assert not hasattr(AgreementOnGenerators, "_certify_derivation")
