"""Audit 0B00E1B-FULL — rule matching and rule roles.

* M1X-6 (≡ K1-12, group G23): :func:`jacopy.core.wildcards.match` and
  :func:`jacopy.core.equality.alpha_equal` compared only type +
  children. A node's NON-CHILD identity payload (the bracket object of
  a ``BracketApply``, ``MultiEval.alternating``, an ``IndexedSum``
  dummy, a Hodge metric, ...) was ignored, so a rule written for one
  operation fired on another. Before: ``comm(A,B) = 0`` CLOSED
  through a true zero-bracket rule. K1-12: ``alpha_equal`` ignored the
  wildcard ``expr_type`` filter.
* M1-4: "Theorem"-named rules with role ``definition``
  (``RightLeibnizTheoremRule``, ``LeftLeibnizTheoremRule``,
  ``DDZeroDefinition``, ``DPairingUnfoldDefinition``) and
  ``CourantLocalityDefinition`` fired on structures that do not carry
  the hypotheses and the result read "assumption-free". Before
  (bare ``algebroid("E")``): ``ρ(Dk)(k) = 0`` CLOSED assumption-free;
  ``[u, f·v] = f[u,v] + ρ(u)(f)v`` CLOSED with ``requires: ()``.

Every test builds the target equality itself; hand counter-models are
in the comments.
"""

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.algorithms.rewrite import Rule
from jacopy.brackets.base import GradedBracket
from jacopy.core.equality import alpha_equal
from jacopy.core.expr import Integer, Product, Rational, Sum, Symbol
from jacopy.core.hodge import HodgeStar
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wildcards import SeqWildcard, Wildcard, match, substitute
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.result import prove
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.central.algebroid.context import algebroid
from jacopy.central.calculus.bracket_calculus import ExteriorDerivative
from jacopy.central.objects import forms, functions, vector_fields


def _kinds(result):
    return [(a.kind, a.name) for a in result.requires]


# --------------------------------------------------------------------- #
# M1X-6: non-child payload in match / alpha_equal                        #
# --------------------------------------------------------------------- #


class _ZeroBracket(GradedBracket):
    def __init__(self):
        super().__init__("zero")

    def expand(self, a, b, registry=None):
        return Integer(0)


class _CommBracket(GradedBracket):
    def __init__(self):
        super().__init__("comm")

    def expand(self, a, b, registry=None):
        return a * b - b * a


class _RuleAdapter(Definition):
    name = "true zero-bracket rule through algorithms.Rule"

    def __init__(self, rule):
        self._rule = rule

    def matches(self, expr):
        return self._rule.try_at(expr) is not None

    def rewrite(self, expr):
        return self._rule.try_at(expr)


def test_bracket_payload_blocks_wrong_rule():
    # comm(A,B) = AB − BA ≠ 0 for A = d/dx, B = x·d/dx ([A,B] = d/dx);
    # the rule "zero(?X,?Y) → 0" is TRUE for the zero bracket only.
    A, B = Derivation("A"), Derivation("B")
    zero, comm = _ZeroBracket(), _CommBracket()
    X, Y = Wildcard("X"), Wildcard("Y")
    rule = Rule(zero(X, Y), Integer(0), name="zero bracket vanishes")
    target = comm(A, B)
    assert match(zero(X, Y), target) is None
    assert match(zero(A, B), target) is None
    assert not alpha_equal(zero(A, B), target)
    assert rule.try_at(target) is None
    lhs, rhs = target, Integer(0)
    assert prove(ExpansionEngine([_RuleAdapter(rule)]), lhs, rhs).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, rhs, engine=ExpansionEngine([_RuleAdapter(rule)]))
    # positive control: the zero bracket itself still matches
    assert match(zero(X, Y), zero(A, B)) == {"X": A, "Y": B}
    assert rule.try_at(zero(A, B)) == Integer(0)
    assert alpha_equal(zero(X, Y), zero(Y, X))


def test_multieval_alternating_flag_is_identity():
    (w,) = forms("w", degree=2)
    (V,) = vector_fields("V")
    alt = MultiEval(w, V, V, alternating=True)
    plain = MultiEval(w, V, V, alternating=False)
    assert alt.alternating and not plain.alternating
    pat = MultiEval(w, Wildcard("X"), Wildcard("X"), alternating=True)
    assert match(pat, plain) is None
    assert not alpha_equal(alt, plain)
    assert match(pat, alt) == {"X": V}


def test_exterior_derivative_skew_and_calculus_distinguish():
    (X,) = vector_fields("X")
    d_skew = ExteriorDerivative("C", skew=True)
    d_plain = ExteriorDerivative("C", skew=False)
    d_other = ExteriorDerivative("C2", skew=True)
    a = Wildcard("a")
    assert match(Act(d_skew, a), Act(d_plain, X)) is None
    assert match(Act(d_skew, a), Act(d_other, X)) is None
    assert match(Act(d_skew, a), Act(d_skew, X)) == {"a": X}


def test_indexed_sum_dummy_and_payload_wildcard():
    # Σ_i ?B against Σ_j f(j): binding B = f(j) under the pattern's
    # dummy i would rebuild Σ_i f(j) = n·f(j) ≠ Σ_j f(j). The binder is
    # matched up to α-renaming instead (review of f02fa15: rejecting
    # every differently-named dummy was a false reject): B = f(i), and
    # the rebuild Σ_i f(i) is the target.
    i, j = Symbol("i"), Symbol("j")
    fj = Act(Derivation("f"), j)
    target = IndexedSum(j, None, fj)
    b = match(IndexedSum(i, None, Wildcard("B")), target)
    assert b == {"B": Act(Derivation("f"), i)}
    assert substitute(IndexedSum(i, None, Wildcard("B")), b) == target
    # renaming j → i would capture the free i in Σ_j f(j)·i: refused
    captured = IndexedSum(j, None, Product(fj, i))
    assert match(IndexedSum(i, None, Wildcard("B")), captured) is None
    assert alpha_equal(IndexedSum(i, None, Act(Derivation("f"), i)), target)
    assert not alpha_equal(IndexedSum(i, None, Act(Derivation("f"), i)), captured)
    # a WILDCARD in the payload (the bound dummy) binds like any hole
    got = match(IndexedSum(Wildcard("d"), None, Wildcard("B")), target)
    assert got == {"d": j, "B": fj}
    # Hodge metric is payload, not a child: wildcard binds, a
    # different concrete metric does not match
    (om,) = forms("om", degree=1)
    g, h = Symbol("g"), Symbol("h")
    assert match(HodgeStar(Wildcard("A"), 3, metric=Wildcard("G")), HodgeStar(om, 3, metric=g)) == {"A": om, "G": g}
    assert match(HodgeStar(Wildcard("A"), 3, metric=g), HodgeStar(om, 3, metric=h)) is None
    assert match(HodgeStar(Wildcard("A"), 2, metric=g), HodgeStar(om, 3, metric=g)) is None


def test_sequence_wildcards_unaffected():
    (X, Y, Z) = vector_fields("X Y Z")
    assert match(Sum(X, SeqWildcard("R")), Sum(X, Y, Z)) == {"R": (Y, Z)}
    assert substitute(Sum(X, SeqWildcard("R")), {"R": (Y, Z)}) == Sum(X, Y, Z)
    from jacopy.core.wildcards import node_payload

    assert node_payload(Sum(X, Y, Z)) == node_payload(Sum(X, Y))


def test_alpha_equal_respects_expr_type_k1_12():
    assert not alpha_equal(Wildcard("A", expr_type=Symbol), Wildcard("A", expr_type=Sum))
    assert alpha_equal(Wildcard("A", expr_type=Symbol), Wildcard("B", expr_type=Symbol))


# --------------------------------------------------------------------- #
# M1-4: theorem-like rules cite their theorem / need their hypotheses    #
# --------------------------------------------------------------------- #


def test_right_leibniz_rule_needs_the_declared_invariance():
    # counter-model without (7.8): [u,v] := 0, ρ = id ⇒ [u, f·v] = 0
    # but f[u,v] + ρ(u)(f)v = u(f)·v ≠ 0. At 3a38eb2 the rule fired on
    # the bare E and reported "(7.8) declared" although E declares
    # nothing; now (7.8) must be DECLARED by the structure (Def 7.1).
    from jacopy.packages.generalized.bourbaki_severa import severa_engine

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    for E, closes in ((algebroid("E"), False), (algebroid("E2", declare=("bourbaki-invariance",)), True)):
        u, v = E.sections("u v")
        lhs = E.bracket(u, Product(f, v))
        rhs = Sum(Product(f, E.bracket(u, v)), Product(Act(E.anchor(u), f), v))
        eng = severa_engine(E, reg)
        r = prove(eng, lhs, rhs, registry=reg)
        if not closes:
            assert r.status == "RESIDUAL"
            with pytest.raises(ProofFailure):
                ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng)
            continue
        assert r.status == "CLOSED"
        assert any(k == "declared" and n.startswith(f"(7.8) invariance ({E.name})") for k, n in _kinds(r))
        assert any(k == "structure" and "bourbaki-invariance" in n for k, n in _kinds(r))


def test_dd_zero_and_pairing_unfold_need_the_courant_data():
    # counter-model: E = TM, ρ = id, positive-definite g, D := grad_g
    # obeys (L) but ρ(Dk)(k) = |dk|² ≠ 0 and (Df,u) = u(f) ≠ ½u(f)
    from jacopy.packages.generalized.courant_axioms import (
        CourantD,
        DDZeroDefinition,
        DPairingUnfoldDefinition,
        courant_context,
    )

    reg = PropertyRegistry()
    f, k = functions("f k", registry=reg)
    A = algebroid("A")
    (u,) = A.sections("u")
    act_lhs, act_rhs = Act(A.anchor(CourantD("A", k)), k), Integer(0)
    eng = ExpansionEngine([DDZeroDefinition(A)])
    assert prove(eng, act_lhs, act_rhs, registry=reg).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(act_lhs, act_rhs, registry=reg, engine=eng)
    mlhs = A.metric(CourantD("A", f), CourantD("A", k))
    assert prove(eng, mlhs, Integer(0), registry=reg).status == "RESIDUAL"
    plhs = A.metric(CourantD("A", f), u)
    prhs = Product(Rational(1, 2), Act(A.anchor(u), f))
    assert prove(ExpansionEngine([DPairingUnfoldDefinition(A)]), plhs, prhs, registry=reg).status == "RESIDUAL"

    # skew + [C2] but [C5] NOT declared: no citation (review of 3a38eb2)
    B = algebroid("B", declare=("anchor-morphism", "antisymmetric"))
    (yb,) = B.sections("y")
    assert prove(ExpansionEngine([DDZeroDefinition(B)]), Act(B.anchor(CourantD("B", k)), k), Integer(0), registry=reg).status == "RESIDUAL"
    assert prove(
        ExpansionEngine([DPairingUnfoldDefinition(B)]),
        B.metric(CourantD("B", f), yb),
        Product(Rational(1, 2), Act(B.anchor(yb), f)),
        registry=reg,
    ).status == "RESIDUAL"

    # on the LWX data the citations close, carrying [C2] and [C5]
    C = courant_context("C")
    (y,) = C.sections("y")
    r = prove(ExpansionEngine([DDZeroDefinition(C)]), Act(C.anchor(CourantD("C", k)), k), Integer(0), registry=reg)
    assert r.status == "CLOSED"
    names = [n for kind, n in _kinds(r) if kind == "declared"]
    assert any(n.startswith("[C5] invariance (C)") for n in names)
    assert any(n.startswith("anchor morphism (C)") for n in names)
    r2 = prove(
        ExpansionEngine([DPairingUnfoldDefinition(C)]),
        C.metric(CourantD("C", f), y),
        Product(Rational(1, 2), Act(C.anchor(y), f)),
        registry=reg,
    )
    assert r2.status == "CLOSED"
    assert any(k_ == "declared" and n.startswith("[C5] invariance (C)") for k_, n in _kinds(r2))
    assert not any(k_ == "legacy" for k_, _ in _kinds(r2))


def test_courant_locality_is_a_recorded_assumption():
    # ᵍL(Ω,u,v) = g(u,v)·g⁻¹(Ω) is MC Prop 4.1 on an almost-Courant
    # algebroid only; registering the rule is a hypothesis
    from jacopy.central.algebroid.context import LocalityOperator
    from jacopy.central.objects import Bundle
    from jacopy.packages.metric_affine.admissible import CourantLocalityDefinition

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    E = algebroid("E", Bundle("E"))
    u, v = E.sections("u v")
    lhs = LocalityOperator(E.name, E.D(f), u, v)
    rhs = Product(E.metric(u, v), E.sharp(E.D(f)))
    r = prove(ExpansionEngine([CourantLocalityDefinition(E)]), lhs, rhs, registry=reg)
    assert r.status == "CLOSED"
    assert any(k == "declared" and n.startswith("Courant locality (E)") for k, n in _kinds(r))


def test_severa_library_theorems_record_the_cited_leibniz():
    from jacopy.packages.generalized.bourbaki_exact import exact_bourbaki_context
    from jacopy.packages.generalized.bourbaki_severa import (
        prove_delta_first_slot_anomaly,
        prove_delta_tensorial_second_slot,
    )

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    E = exact_bourbaki_context()
    U, V = vector_fields("U V")
    _, t2 = prove_delta_tensorial_second_slot(E, U, V, f, registry=reg)
    assert any(a.kind == "declared" and a.name.startswith("(7.8) invariance (E)") for a in t2.requires)
    assert not t2.legacy
    # the left-Leibniz record rests on undeclared (6.11) instances:
    # the honest state is the legacy marker, not assumption-free
    _, t1 = prove_delta_first_slot_anomaly(E, U, V, f, registry=reg)
    assert t1.legacy


def test_cited_theorem_does_not_touch_the_callers_registry():
    # the cited theorem is proved with helper symbols in a PRIVATE
    # registry (K3: no fixed-name helpers written into user registries)
    from jacopy.packages.generalized.courant_axioms import CourantD, DDZeroDefinition, courant_context

    reg = PropertyRegistry()
    (k,) = functions("k", registry=reg)
    before = dict(reg._props)
    C = courant_context("C")
    r = prove(ExpansionEngine([DDZeroDefinition(C)]), Act(C.anchor(CourantD("C", k)), k), Integer(0), registry=reg)
    assert r.status == "CLOSED"
    assert dict(reg._props) == before


def test_liez_definition_rule_cites_lemma_91():
    # (9.7) rewrites [φV, χz] → χ(ℒ^Z_V z), i.e. asserts [φV, χz] ∈ im χ
    # (Lemma 9.1: anchor morphism + ker ρ = im χ). Counter-model
    # without a morphism anchor: put [φV, χz] := φW, then
    # ρ([φV, χz]) = W ≠ 0. Before: CLOSED assumption-free on a bare E.
    from jacopy.packages.generalized.bourbaki_exact import (
        ChiSec,
        PhiSec,
        exact_bourbaki_context,
        exact_bourbaki_engine,
    )
    from jacopy.packages.generalized.bourbaki_precalculus import BD

    reg = PropertyRegistry()
    h, k = functions("h k", registry=reg)
    (V,) = vector_fields("V")
    bare = algebroid("E")
    lhs = Act(bare.anchor(bare.bracket(PhiSec(V), ChiSec(BD(k)))), h)
    eng = exact_bourbaki_engine(bare, reg)
    assert prove(eng, lhs, Integer(0), registry=reg).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, Integer(0), registry=reg, engine=eng)
    X = exact_bourbaki_context("X")
    lhs_x = Act(X.anchor(X.bracket(PhiSec(V), ChiSec(BD(k)))), h)
    r = prove(exact_bourbaki_engine(X, reg), lhs_x, Integer(0), registry=reg)
    assert r.status == "CLOSED"
    assert any(kd == "declared" and n.startswith("anchor morphism (X)") for kd, n in _kinds(r))
    # Lemma 9.1 gives only ρ([φV, χz]) = 0; im χ also needs exactness
    # ker ρ = im χ (8.5): declared, and carried as a requirement (review
    # of 3a38eb2: it was implicit)
    assert any(kd == "declared" and n.startswith("exactness (8.5) (X)") for kd, n in _kinds(r))
    P = algebroid("P", declare=("anchor-morphism",))
    lhs_p = Act(P.anchor(P.bracket(PhiSec(V), ChiSec(BD(k)))), h)
    assert prove(exact_bourbaki_engine(P, reg), lhs_p, Integer(0), registry=reg).status == "RESIDUAL"


# --------------------------------------------------------------------- #
# review of f02fa15 (M1X-6): payload wildcards must be SUBSTITUTED       #
# --------------------------------------------------------------------- #


def test_payload_wildcard_is_substituted_not_left_literal():
    # ⋆ is C∞-linear: ⋆_g(f·ω) = f·⋆_g ω, metric by metric. At 3a38eb2
    # match bound ?G but substitute kept it literal: both ⋆_g(fω) and
    # ⋆_h(fω) rewrote to f·⋆_?G ω, closing ⋆_g(fω) = ⋆_h(fω) (false
    # for g ≠ h: ⋆ depends on the metric) assumption-free.
    from jacopy.core.wildcards import PayloadSubstitutionError

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    (om,) = forms("om", degree=1)
    g, h = Symbol("g"), Symbol("h")
    F, A, G = Wildcard("F"), Wildcard("A"), Wildcard("G")
    rule = Rule(HodgeStar(Product(F, A), 3, metric=G), Product(F, HodgeStar(A, 3, metric=G)))
    assert rule.try_at(HodgeStar(Product(f, om), 3, metric=g)) == Product(f, HodgeStar(om, 3, metric=g))
    assert rule.try_at(HodgeStar(Product(f, om), 3, metric=h)) == Product(f, HodgeStar(om, 3, metric=h))
    lhs, rhs = HodgeStar(Product(f, om), 3, metric=g), HodgeStar(Product(f, om), 3, metric=h)
    eng = ExpansionEngine([_RuleAdapter(rule)])
    assert prove(eng, lhs, rhs, registry=reg).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng)
    # an unbound payload hole is an error, and a Rule does not fire
    with pytest.raises(PayloadSubstitutionError):
        substitute(HodgeStar(om, 3, metric=Wildcard("Q")), {})
    bad = Rule(HodgeStar(A, 3, metric=g), HodgeStar(A, 3, metric=Wildcard("Q")))
    assert bad.try_at(HodgeStar(om, 3, metric=g)) is None
    # IndexedSum dummy hole is filled too
    j = Symbol("j")
    fj = Act(Derivation("f"), j)
    d, B = Wildcard("d"), Wildcard("B")
    b = match(IndexedSum(d, None, B), IndexedSum(j, None, fj))
    assert substitute(IndexedSum(d, None, B), b) == IndexedSum(j, None, fj)


def test_object_shared_by_child_and_payload_still_matches():
    # HodgeStar(g, 3, metric=g): the same object is the child and the
    # metric. At 9aa7495 the identity strip removed both, so an equal
    # but separately built node did not match / was not alpha-equal.
    g1, g2 = Symbol("g"), Symbol("g")
    a = HodgeStar(g1, 3, metric=g1)
    b = HodgeStar(g2, 3, metric=Symbol("g"))
    assert a == b
    assert match(a, b) == {}
    assert alpha_equal(a, b)
    assert match(HodgeStar(Wildcard("A"), 3, metric=Wildcard("A")), b) == {"A": g2}


def test_alpha_expr_type_is_order_insensitive():
    assert alpha_equal(
        Wildcard("A", expr_type=(Symbol, Sum)), Wildcard("B", expr_type=(Sum, Symbol))
    )


# --------------------------------------------------------------------- #
# review of 38080c2 / 3a38eb2 (M1-4)                                     #
# --------------------------------------------------------------------- #


def test_dd_zero_ignores_a_foreign_d():
    # ρ∘D = 0 is proved for C's D. A bare A's D_A is arbitrary (take
    # D_A := grad: g(D_A f, D_A k) = ⟨df, dk⟩ ≠ 0). At 3a38eb2 DDZero(C)
    # fired on C's pairing/anchor of D_A.
    from jacopy.packages.generalized.courant_axioms import CourantD, DDZeroDefinition, courant_context

    reg = PropertyRegistry()
    f, k = functions("f k", registry=reg)
    C = courant_context("C")
    eng = ExpansionEngine([DDZeroDefinition(C)])
    lhs = C.metric(CourantD("A", f), CourantD("A", k))
    assert prove(eng, lhs, Integer(0), registry=reg).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, Integer(0), registry=reg, engine=eng)
    act = Act(C.anchor(CourantD("A", k)), k)
    assert prove(eng, act, Integer(0), registry=reg).status == "RESIDUAL"
    # control: C's own D still closes
    own = Act(C.anchor(CourantD("C", k)), k)
    assert prove(eng, own, Integer(0), registry=reg).status == "CLOSED"


def test_cited_rule_inert_and_cached_when_prover_diverges():
    from jacopy.packages.generalized._cited_rule import CitedTheoremMixin

    calls = []

    class Diverging(CitedTheoremMixin, Definition):
        name = "diverging citation"

        def _prove_cited(self):
            calls.append(1)
            raise RuntimeError("ExpansionEngine did not converge")

        def matches(self, expr):
            return self._licensed()

        def rewrite(self, expr):  # pragma: no cover - never fires
            return Integer(0)

    rule = Diverging()
    x = Symbol("x")
    assert not rule.matches(x) and not rule.matches(x)
    assert rule.theorem is None
    assert len(calls) == 1
    assert prove(ExpansionEngine([rule]), x, Integer(0)).status == "RESIDUAL"


def test_liez_result_is_citable_in_its_own_engine():
    # review of 03a70c1: the exactness step carried a key no rule had,
    # so check_citation refused the LieZ result even in
    # exact_bourbaki_engine. The `exact` flag is now licensed by the
    # registered ExactnessDeclaration.
    from jacopy.proof.theorems import Theorem, check_citation
    from jacopy.packages.generalized.bourbaki_exact import (
        ChiSec,
        PhiSec,
        exact_bourbaki_context,
        exact_bourbaki_engine,
    )
    from jacopy.packages.generalized.bourbaki_precalculus import BD

    reg = PropertyRegistry()
    h, k = functions("h k", registry=reg)
    (V,) = vector_fields("V")
    X = exact_bourbaki_context("X")
    lhs = Act(X.anchor(X.bracket(PhiSec(V), ChiSec(BD(k)))), h)
    eng = exact_bourbaki_engine(X, reg)
    r = prove(eng, lhs, Integer(0), registry=reg)
    assert r.status == "CLOSED"
    assert any(kd == "declared" and n.startswith("exactness (8.5) (X)") for kd, n in _kinds(r))
    t = Theorem("liez_use", "ρ([φV, χz])(h) = 0", lhs, Integer(0), r.chain).with_structural_requires()
    assert check_citation(t, exact_bourbaki_engine(X, reg)).ok


# --------------------------------------------------------------------- #
# review of cf9cf2c: Σ binder scope in match / substitute                #
# --------------------------------------------------------------------- #


def _sigma_setup():
    i, j = Symbol("i"), Symbol("j")
    F = lambda x: Act(Derivation("F"), x)  # noqa: E731
    return i, j, F, Wildcard("D"), Wildcard("A"), Wildcard("B")


def _closes_wrongly(rule, lhs, rhs):
    eng = ExpansionEngine([_RuleAdapter(rule)])
    assert prove(eng, lhs, rhs).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, rhs, engine=eng)


def test_sigma_wildcard_dummy_does_not_capture_a_free_atom():
    # Σ_D F(D)·i → i·Σ_D F(D) pulls the FREE i out. On Σ_i F(i)·i the i
    # is bound: Σ_i F(i)·i ≠ i·Σ_j F(j) (n = 2, F = id: 1+4 ≠ 2·3).
    # At cf9cf2c: CLOSED.
    i, j, F, D, A, B = _sigma_setup()
    rule = Rule(IndexedSum(D, None, Product(F(D), i)), Product(i, IndexedSum(D, None, F(D))))
    _closes_wrongly(rule, IndexedSum(i, None, Product(F(i), i)), Product(i, IndexedSum(j, None, F(j))))
    # the legitimate pull still works
    assert rule.try_at(IndexedSum(j, None, Product(F(j), i))) == Product(i, IndexedSum(j, None, F(j)))


def test_sigma_substitution_avoids_capture():
    # A·Σ_D B → Σ_D (A·B) on i·Σ_i F(i): the outer i is free; pushing it
    # in must rename the binder, not capture: Σ_k (i·F(k)) ≠ Σ_i (i·F(i)).
    # At cf9cf2c: Σ_i (i·F(i)), CLOSED.
    i, j, F, D, A, B = _sigma_setup()
    rule = Rule(Product(A, IndexedSum(D, None, B)), IndexedSum(D, None, Product(A, B)))
    t = Product(i, IndexedSum(i, None, F(i)))
    out = rule.try_at(t)
    assert out is not None and out == IndexedSum(j, None, Product(i, F(j)))  # α-equal
    _closes_wrongly(rule, t, IndexedSum(i, None, Product(i, F(i))))
    # no clash: plain push
    assert rule.try_at(Product(j, IndexedSum(i, None, F(i)))) == IndexedSum(i, None, Product(j, F(i)))


def test_sigma_bound_term_does_not_escape_its_binder():
    # Σ_D (A·B) → A·Σ_D B pulls a constant factor out; on Σ_i F(i)·i the
    # factor F(i) depends on the bound i: Σ_i F(i)·i ≠ F(i)·Σ_i i.
    # At cf9cf2c: CLOSED.
    i, j, F, D, A, B = _sigma_setup()
    rule = Rule(IndexedSum(D, None, Product(A, B)), Product(A, IndexedSum(D, None, B)))
    _closes_wrongly(rule, IndexedSum(i, None, Product(F(i), i)), Product(F(i), IndexedSum(i, None, i)))
    assert rule.try_at(IndexedSum(i, None, Product(j, F(i)))) == Product(j, IndexedSum(i, None, F(i)))
