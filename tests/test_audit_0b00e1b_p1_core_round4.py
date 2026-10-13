"""
Audit 0b00e1b-FULL, fix/p1-core gate 7 (Fable, round 4): every probe of
the scratch sets ``p1core-cr7`` (p01–p07) and ``p1core-gate7`` (q1–q5)
as a permanent test.

1. f·D: an EXPLICIT type allow-list for coefficient / generator symbols
   (cr7/p01 all rows, gate7/q1 a3/a4, q5) — opaque atoms (EndoForm,
   PoissonBracketValue, musical maps, Act …) are refused;
   one function symbol per derivation term through nested shapes
   (cr7/p02, gate7/q1 a5, F9).
2. AoG-domain (cr7/p06, cr8/p02): an AgreementOnGenerators identity
   carries its algebra; a citation applies it to elements of that algebra
   only.  KNOWN MAIN BUG, strict-xfail: the fix moved to its own lane
   (gate 8: multi-domain first-wins, Koszul zero_pair regression).
3. Oracle corners (cr7/p04, gate7/q2 corners, q3, F5).
4. Raw facts under citation (cr7/p03, gate7/q1 a2, q1b, q4).
"""

from __future__ import annotations

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.central.calculus.scalars import is_real_constant
from jacopy.central.objects import forms, vector_fields
from jacopy.central.objects.endomorphism import EndoForm
from jacopy.central.objects.form import Form
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.musical import Flat, Sharp
from jacopy.core.expr import Integer, Neg, Power, Product, Sum, Symbol
from jacopy.core.properties import (
    AntiCommuting,
    Graded,
    NonCommuting,
    ProofRef,
    Provenance,
    Scalar,
)
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.packages.poisson.core import PoissonBracketValue
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.result import prove
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure, _is_derivation_expr, _plain_atom
from jacopy.proof.theorems import Theorem, TheoremDefinition, check_citation
from jacopy.proof.verifier import prove_operator_equation

PR = ProofRef("probe")


def _rule(table, name="gens"):
    class R(Definition):
        anchor = Act

        def matches(self, e):
            return isinstance(e, Act) and (e.op, e.arg) in table

        def rewrite(self, e):
            return table[(e.op, e.arg)]

    R.name = name
    return R()


def _cD_eq_E(reg, c, gens):
    """D(g) = w_g, E(g) = c·w_g; c·D = E holds iff c commutes with the algebra."""
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    vals = {}
    for i, g in enumerate(gens):
        w = Symbol(f"w{i}")
        if reg.get(w, Graded) is None:
            reg.declare(w, Graded(0))
        vals[(D, g)] = w
        vals[(E, g)] = Product(c, w)

    class Alg:
        generators = tuple(gens)

    return prove_operator_equation(Product(c, D), E, Alg(), registry=reg, engine=ExpansionEngine([_rule(vals)]))


def _reg():
    reg = PropertyRegistry()
    f, n, a = Symbol("f"), Symbol("n"), Symbol("a")
    reg.declare(f, Graded(0))
    reg.declare(n, Graded(0))
    reg.declare(n, NonCommuting())
    reg.declare(a, Graded(0))
    reg.declare(a, AntiCommuting())
    for s in "uvxy":
        reg.declare(Symbol(s), Graded(0))
    return reg, f, n, a, Symbol("x"), Symbol("y")


PI = PVector("pi", degree=2)


# --------------------------------------------------------------------- #
# 1. type allow-list                                                     #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "mk",
    [
        lambda f, n, a, r: EndoForm("m", n),                      # [2]
        lambda f, n, a, r: EndoForm("m", Sum(f, n)),              # [3]
        lambda f, n, a, r: EndoForm("m", a),                      # [4]
        lambda f, n, a, r: PoissonBracketValue(PI, n, f),         # [5]
        lambda f, n, a, r: n,                                     # [6]
        lambda f, n, a, r: EndoForm("m", _nc_form(r)),            # [9]
        lambda f, n, a, r: _nc_form(r),                           # [10]
        lambda f, n, a, r: EndoForm("m", f),                      # opaque, even with a plain operand
        lambda f, n, a, r: Act(vector_fields("X")[0], f),         # q1 a3
        lambda f, n, a, r: Form("hk", degree=Degree.var("k")),
        lambda f, n, a, r: Symbol("undeclared"),
        lambda f, n, a, r: _sym(r, "t", Graded(Degree.var("k"))),
    ],
    ids=["m(n)", "m(f+n)", "m(a)", "{n,f}", "n", "m(nw)", "nw", "m(f)", "X(f)", "Form(k)", "undeclared", "t:Gk"],
)
def test_1_opaque_or_unplain_coefficient_is_refused(mk):
    reg, f, n, a, x, y = _reg()
    c = mk(f, n, a, reg)
    assert not _is_derivation_expr(Product(c, Derivation("D", degree=0)), reg, (x, y))
    with pytest.raises(ProofFailure, match="DERIVATIONS only"):
        _cD_eq_E(reg, c, (x, y))


def _nc_form(r):
    nw = Form("nw", degree=0)
    if r.get(nw, NonCommuting) is None:
        r.declare(nw, NonCommuting())
    return nw


def _sym(r, name, prop):
    s = Symbol(name)
    r.declare(s, prop)
    return s


def test_1_plain_symbol_coefficients_close():
    reg, f, n, a, x, y = _reg()
    assert _cD_eq_E(reg, Form("w", degree=0), (x, y)) is not None          # [1] control
    assert _cD_eq_E(reg, PVector("q0", degree=0), (x, y)) is not None
    t0 = _sym(reg, "t0", Graded(Degree.var("k") - Degree.var("k")))
    assert _cD_eq_E(reg, t0, (x, y)) is not None
    assert _cD_eq_E(reg, f, (x, y)) is not None


@pytest.mark.parametrize(
    "mk",
    [
        lambda f, n, r: (EndoForm("m", n), Symbol("y")),                     # [7]
        lambda f, n, r: (PoissonBracketValue(PI, n, Symbol("y")), Symbol("y")),  # [8]
        lambda f, n, r: (Symbol("x"), Sharp(PI)),                            # q5
        lambda f, n, r: (Symbol("x"), Flat(f)),
        lambda f, n, r: (Symbol("x"), Derivation("X", degree=0)),            # q1 a4
        lambda f, n, r: (Symbol("x"), Act(Derivation("X", degree=0), Symbol("y"))),
        lambda f, n, r: (Symbol("x"), Symbol("z")),                          # undeclared
        lambda f, n, r: (Symbol("x"), _nc_1form(r)),
    ],
    ids=["m(n)", "{n,y}", "pi#", "flat", "X", "X(y)", "undeclared", "w1+NC"],
)
def test_1_opaque_or_unplain_generator_is_refused(mk):
    reg, f, n, a, x, y = _reg()
    gens = mk(f, n, reg)
    assert not _is_derivation_expr(Product(f, Derivation("D", degree=0)), reg, gens)
    with pytest.raises(ProofFailure):
        _cD_eq_E(reg, f, gens)


def _nc_1form(r):
    w = Form("w1", degree=1)
    r.declare(w, NonCommuting())
    return w


def test_1_musical_maps_are_not_plain_atoms():
    reg, f, n, a, x, y = _reg()
    for g in (Sharp(PI), Flat(f), EndoForm("m", f), PoissonBracketValue(PI, f, f)):
        assert g.is_atom
        assert not _plain_atom(g, reg, ("function", "form"))
    g1 = _sym(reg, "g1", Graded(1))
    assert _plain_atom(g1, reg, ("function", "form"))         # a plain odd symbol generator
    assert _cD_eq_E(reg, f, (x, g1)) is not None


def test_1_one_function_symbol_per_term_through_nested_shapes():
    # cr7/p02, gate7/q1 a5, F9: f·(g·D) and f·g·D are the same shape
    reg, f, n, a, x, y = _reg()
    g, k, m = Symbol("g"), Symbol("k"), Symbol("m")
    reg.declare(g, Graded(0))
    reg.declare(k, Scalar())
    reg.declare(m, Scalar())
    D, D2 = Derivation("D", degree=0), Derivation("D2", degree=0)
    gens = (x, y)
    accepted = [
        Sum(Product(k, D), Product(D, k)), Neg(Product(f, D)), Product(f, Neg(D)),
        Product(k, f, D), Product(f, k, D), Product(f, D, k), Product(D, Sum(k, m)),
        Product(f, Sum(D, Product(k, D2))),
    ]
    refused = [
        Sum(Product(f, D), Product(D, f)), Product(Neg(f), D), Product(f, Product(g, D)),
        Product(f, Product(n, D)), Product(n, Product(f, D)), Product(f, Neg(Product(n, D))),
        Product(f, Sum(D, Product(g, D2))), Product(f, Sum(D, Product(n, D2))),
        Product(f, Sum(D, Product(D2, g))), Product(f, D, g), Product(Product(f, D), g),
        Product(f, g, D), Product(Product(f, g), D), Product(D, D2), Product(f, D, f),
        Sum(Product(f, D), Product(n, D)),
    ]
    for e in accepted:
        assert _is_derivation_expr(e, reg, gens), e
    for e in refused:
        assert not _is_derivation_expr(e, reg, gens), e
    r2 = PropertyRegistry()
    for s in (k, m):
        r2.declare(s, Scalar())
    r2.declare(Product(k, m), NonCommuting())
    assert not _is_derivation_expr(Product(Product(k, m), D), r2, gens)


# --------------------------------------------------------------------- #
# 2. AoG-domain                                                          #
# --------------------------------------------------------------------- #


_AOG_XFAIL = pytest.mark.xfail(strict=True, reason="AoG-domain moved to its own lane; known main bug cr7/p06")


@_AOG_XFAIL
@pytest.mark.parametrize("order", ["theorem first", "rules first"])
def test_2_aog_theorem_applies_on_its_algebra_only(order):
    x, z, u = Symbol("x"), Symbol("z"), Symbol("u")
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    reg = PropertyRegistry()
    for s in (x, z, u):
        reg.declare(s, Graded(0))
    on_gens = {(D, x): u, (E, x): u}
    on_z = {(D, z): Integer(1), (E, z): Integer(0)}

    class Alg:
        generators = (x,)

    chain = prove_operator_equation(D, E, Alg(), registry=reg, engine=ExpansionEngine([_rule(on_gens)]))
    thm = Theorem("DE", "D = E on ℝ[x]", D, E, chain).with_structural_requires()
    assert any(a.kind == "domain" for a in thm.requires)
    defs = [TheoremDefinition(thm), _rule(on_gens), _rule(on_z, "onz")]
    if order == "rules first":
        defs = defs[1:] + defs[:1]
    eng = ExpansionEngine(defs)
    assert check_citation(thm, eng, registry=reg).ok
    assert prove(eng, Act(D, z), Integer(0), registry=reg).status == "RESIDUAL"   # z ∉ ℝ[x]
    assert prove(eng, Act(D, z), Integer(1), registry=reg).status == "CLOSED"
    # inside the algebra the citation still works: D(a) → E(a) for a
    # built from the generators (the engine's linearity may expand D(a)
    # first; the rule's own match is what the domain restricts)
    td = TheoremDefinition(thm)
    eng2 = ExpansionEngine([_rule(on_gens), td])     # the theorem requires its generator rule
    assert prove(eng2, Act(D, x), Act(E, x), registry=reg).status == "CLOSED"
    with __import__("jacopy.proof.registry_facts", fromlist=["registry_context"]).registry_context(reg):
        for inside in (x, Sum(Product(x, x), Integer(2)), Power(x, Integer(3)), Neg(x)):
            assert td.matches(Act(D, inside)) and td.rewrite(Act(D, inside)) == Act(E, inside), inside
        for outside in (z, Sum(x, z), Product(x, z), Power(x, z), Act(D, x)):
            assert not td.matches(Act(D, outside)), outside
        assert not td.matches(D)                           # the bare operator is never rewritten
    assert prove(eng2, D, E, registry=reg).status == "RESIDUAL"


@_AOG_XFAIL
@pytest.mark.parametrize("order", ["theorem first", "rules first"])
def test_2_known_bug_cr7_p06_aog_cited_outside_its_algebra(order):
    # D(x) = E(x) = u on ℝ[x]; z ∉ ℝ[x] with D(z) = 1, E(z) = 0: D(z) = 0 is FALSE.
    x, z, u = Symbol("x"), Symbol("z"), Symbol("u")
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    reg = PropertyRegistry()
    for s in (x, z, u):
        reg.declare(s, Graded(0))

    class Alg:
        generators = (x,)

    gens = _rule({(D, x): u, (E, x): u})
    chain = prove_operator_equation(D, E, Alg(), registry=reg, engine=ExpansionEngine([gens]))
    thm = Theorem("DE", "D = E on ℝ[x]", D, E, chain).with_structural_requires()
    defs = [TheoremDefinition(thm), gens, _rule({(D, z): Integer(1), (E, z): Integer(0)}, "onz")]
    if order == "rules first":
        defs = defs[1:] + defs[:1]
    assert not prove(ExpansionEngine(defs), Act(D, z), Integer(0), registry=reg).closed


@pytest.mark.xfail(strict=True, reason="AoG-domain moved to its own lane; known main bug cr8/p02")
def test_2_known_bug_cr8_p02_two_aog_domains_in_one_chain():
    # D = E on ℝ[x], E = G on ℝ[y], G(x) = 0: D = G holds on ℝ only; D(x) = u, so D(x) = 0 is FALSE.
    from jacopy.proof.chain import ProofChain

    x, y, u, v = (Symbol(n) for n in "xyuv")
    D, E, G = (Derivation(n, degree=0) for n in "DEG")
    reg = PropertyRegistry()
    for s in (x, y, u, v):
        reg.declare(s, Graded(0))
    table = _rule({(D, x): u, (E, x): u, (E, y): v, (G, y): v, (G, x): Integer(0)}, "table")

    class AX:
        generators = (x,)

    class AY:
        generators = (y,)

    c1 = prove_operator_equation(D, E, AX(), registry=reg, engine=ExpansionEngine([table]))
    c2 = prove_operator_equation(E, G, AY(), registry=reg, engine=ExpansionEngine([table]))
    thm = Theorem("DG", "D = G", D, G, ProofChain(list(c1.steps) + list(c2.steps))).with_structural_requires()
    eng = ExpansionEngine([TheoremDefinition(thm), table])
    assert not prove(eng, Act(D, x), Integer(0), registry=reg).closed


# --------------------------------------------------------------------- #
# 3. oracle corners                                                      #
# --------------------------------------------------------------------- #


class _Env:
    def __init__(self, registry):
        self.registry = registry


class _MyScalar(Scalar):
    pass


def test_3_oracle_scalar_subclass_filters_by_exact_type():
    pytest.importorskip("sympy")  # the model oracle needs the optional ``oracle`` extra
    from jacopy.oracle.realize import _declared_constant

    w = Symbol("w")
    r = PropertyRegistry()
    r.declare_for_predicate(lambda e: e == w, _MyScalar())
    assert _declared_constant(w, _Env(r)) == is_real_constant(w, r) is True
    with r.axioms([Scalar]):
        assert _declared_constant(w, _Env(r)) == is_real_constant(w, r) is False
    with r.axioms([_MyScalar]):
        assert _declared_constant(w, _Env(r)) == is_real_constant(w, r) is True
    r2 = PropertyRegistry()
    r2.declare(w, _MyScalar())
    assert _declared_constant(w, _Env(r2)) == is_real_constant(w, r2)


def test_3_oracle_form_of_symbolic_degree_is_not_a_constant():
    pytest.importorskip("sympy")  # the model oracle needs the optional ``oracle`` extra
    from jacopy.oracle.realize import _declared_constant

    r = PropertyRegistry()
    hk = Form("hk", degree=Degree.var("k"))
    r.declare(hk, Scalar())
    assert not is_real_constant(hk, r)
    assert not _declared_constant(hk, _Env(r))          # even at the k = 0 sample
    h0 = Form("h0", degree=0)
    r.declare(h0, Scalar())
    assert is_real_constant(h0, r) and _declared_constant(h0, _Env(r))


def test_3_oracle_refuses_a_compound_with_its_own_declaration():
    pytest.importorskip("sympy")
    from jacopy.oracle.check import check_equal

    k, m = Symbol("k"), Symbol("m")
    (X,) = vector_fields("X")
    r = PropertyRegistry()
    r.declare(k, Scalar())
    r.declare(m, Scalar())
    assert check_equal(Act(X, Product(k, m)), Integer(0), registry=r, owners=[]).verdict == "AGREE"
    r.declare(Product(k, m), Graded(1))
    assert not is_real_constant(Product(k, m), r)
    assert check_equal(Act(X, Product(k, m)), Integer(0), registry=r, owners=[]).verdict == "UNSUPPORTED"


# --------------------------------------------------------------------- #
# 4. raw facts under citation                                           #
# --------------------------------------------------------------------- #


def _fD_theorem():
    reg = PropertyRegistry()
    f, x, y = Symbol("f"), Symbol("x"), Symbol("y")
    for s in (f, x, y):
        reg.declare(s, Graded(0))
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    vals = {}
    for i, g in enumerate((x, y)):
        u = Symbol(f"u{i}")
        reg.declare(u, Graded(0))
        vals[(D, g)] = u
        vals[(E, g)] = Product(f, u)

    class Alg:
        generators = (x, y)

    rule = _rule(vals)
    chain = prove_operator_equation(Product(f, D), E, Alg(), registry=reg, engine=ExpansionEngine([rule]))
    thm = Theorem("fD=E", "f·D = E", Product(f, D), E, chain).with_structural_requires()
    return reg, f, x, y, thm, ExpansionEngine([rule, TheoremDefinition(thm)])


def _fresh(f, x, y):
    r = PropertyRegistry()
    for s in (f, x, y, Symbol("u0"), Symbol("u1")):
        r.declare(s, Graded(0))
    return r


def test_4_fD_citation_follows_the_raw_declarations():
    reg, f, x, y, thm, eng = _fD_theorem()
    ok = lambda r: check_citation(thm, eng, registry=r).ok  # noqa: E731
    assert ok(reg)
    with reg.axioms([Graded]):
        assert ok(reg)
    r = _fresh(f, x, y); r.declare(f, NonCommuting()); assert not ok(r)
    with r.axioms([Graded]):
        assert not ok(r)                                   # the filter hides nothing
    r = _fresh(f, x, y); r.declare_for_class(Symbol, AntiCommuting()); assert not ok(r)
    r = _fresh(f, x, y); r.declare_for_predicate(lambda e: e == x, NonCommuting()); assert not ok(r)
    r = PropertyRegistry(strict_axioms_only=True)
    for s in (f, x, y, Symbol("u0"), Symbol("u1")):
        r.declare(s, Graded(0))
    r.declare(f, NonCommuting(provenance=Provenance.DERIVED, proof=PR)); assert not ok(r)
    r = _fresh(f, x, y); r.declare(f, NonCommuting()); r.retract(f, NonCommuting); assert ok(r)
    r = _fresh(f, x, y)
    with r.scope():
        r.declare(y, AntiCommuting())
        assert not ok(r)
    assert ok(r)
    r = PropertyRegistry(); r.declare_for_class(Symbol, Graded(0)); assert ok(r)   # same content, class level
    r = _fresh(f, x, y); r.declare_for_class(Symbol, Graded(1)); assert ok(r)         # exact Graded(0) wins
    r = _fresh(f, x, y); r.declare_for_predicate(lambda e: isinstance(e, Symbol), Scalar())
    assert ok(r)                                           # f a constant: still a derivation


def test_4_compound_constant_citation_follows_the_node_declaration():
    X = Derivation("X", degree=0)
    c, k = Symbol("c"), Symbol("k")

    def src():
        r = PropertyRegistry()
        r.declare(c, Scalar())
        r.declare(k, Scalar())
        return r

    for node in (Product(c, k), Sum(c, k), Neg(c), Sum(c, Integer(1))):
        r = src()
        res = prove(ExpansionEngine(), Act(X, node), Integer(0), registry=r)
        assert res.closed
        thm = Theorem("t", "X(node)=0", Act(X, node), Integer(0), res.chain).with_structural_requires()
        assert any(f.raw and f.expr == node for f in thm.registry_facts)
        eng = ExpansionEngine([TheoremDefinition(thm)])
        for mut, direct, cite in (
            (lambda r: r.declare(node, NonCommuting()), False, False),
            (lambda r: r.declare(node, Graded(1)), False, False),
            # Graded(0) on the node: still a constant directly; the citation
            # compares raw facts EXACTLY ("no Graded" ≠ Graded(0)) — a sound
            # incompleteness, the direct proof closes
            (lambda r: r.declare(node, Graded(0)), True, False),
            (lambda r: r.declare_for_class(type(node), NonCommuting()), False, False),
            (lambda r: r.declare_for_predicate(lambda e: e == node, AntiCommuting()), False, False),
        ):
            r = src()
            mut(r)
            assert is_real_constant(node, r) == direct, node
            assert check_citation(thm, eng, registry=r).ok == cite, node
            assert (prove(eng, Act(X, node), Integer(0), registry=r).status == "CLOSED") == (direct or cite), node
