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


def test_payload_wildcard_binds_hodge_metric():
    # Hodge metric is payload, not a child: wildcard binds, a
    # different concrete metric (or dim) does not match
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
    assert any(kd == "textual" and "exactness (8.5) (X, declared)" in n for kd, n in _kinds(r))
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
    assert any(kd == "textual" and "exactness (8.5) (X, declared)" in n for kd, n in _kinds(r))
    t = Theorem("liez_use", "ρ([φV, χz])(h) = 0", lhs, Integer(0), r.chain).with_structural_requires()
    assert t.chain_replayed
    assert check_citation(t, exact_bourbaki_engine(X, reg), registry=reg).ok


def _closes_wrongly(rule, lhs, rhs):
    eng = ExpansionEngine([_RuleAdapter(rule)])
    assert prove(eng, lhs, rhs).status == "RESIDUAL"
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, rhs, engine=eng)


def test_rule_with_unbound_rhs_wildcard_never_fires():
    # review of 0939bfe: the old guard only refused when the TARGET had
    # no wildcard; a target carrying an unrelated wildcard let ?Q leak
    (om,) = forms("om", degree=1)
    A, Q = Wildcard("A"), Wildcard("Q")
    rule = Rule(Product(A, Symbol("c")), Product(Q, A))
    assert rule.try_at(Product(om, Symbol("c"))) is None
    assert rule.try_at(Product(Wildcard("Z"), Symbol("c"))) is None


def test_cited_rule_reraises_programming_errors():
    from jacopy.packages.generalized._cited_rule import CitedTheoremMixin

    for exc in (NotImplementedError, RecursionError):

        class Broken(CitedTheoremMixin, Definition):
            name = "broken citation"

            def _prove_cited(self, exc=exc):
                raise exc("bug")

            def matches(self, expr):
                return self._licensed()

            def rewrite(self, expr):  # pragma: no cover
                return expr

        with pytest.raises(exc):
            Broken().matches(Symbol("x"))


def test_sequence_binding_used_as_single_hole_never_fires():
    # (?*r + x) → ?r: the sequence binding cannot fill a single hole;
    # the result kept a literal ?r (main too)
    x = Symbol("x")
    rule = Rule(Sum(SeqWildcard("r"), x), Wildcard("r"))
    assert rule.try_at(Sum(Symbol("a"), Symbol("b"), x)) is None


def test_target_wildcard_with_rhs_name_is_legitimate():
    # Z(?f) → ?f on Z(?f) (the target itself holds a wildcard): main
    # rewrites it; 05b03b1's post-check refused
    Z = lambda x: Act(Derivation("Z"), x)  # noqa: E731
    r = Rule(Z(Wildcard("f")), Wildcard("f"))
    assert r.try_at(Z(Wildcard("f"))) == Wildcard("f")
    assert r.try_at(Z(Wildcard("g"))) == Wildcard("g")


# --------------------------------------------------------------------- #
# Σ binders: the NARROW contract (jacopy.core.wildcards docstring).      #
# Every false closure found by the earlier review rounds, in its        #
# concrete-dummy form, plus the documented completeness limits.         #
# --------------------------------------------------------------------- #


def _sx():
    i, j = Symbol("i"), Symbol("j")
    mk = lambda n: (lambda *x: Act(Derivation(n), x[0] if len(x) == 1 else Product(*x)))  # noqa: E731
    S = lambda d, b: IndexedSum(d, None, b)  # noqa: E731
    return i, j, mk("F"), mk("G"), S, Wildcard("f"), Wildcard("g")


def test_sigma_wildcard_dummy_is_unsupported():
    i, j, F, G, S, f, g = _sx()
    D = Wildcard("D")
    assert match(S(D, f), S(i, F(i))) is None
    with pytest.raises(ValueError):
        Rule(S(D, f), f)
    with pytest.raises(ValueError):
        Rule(f, S(D, f))


def test_sigma_matches_only_the_same_named_dummy():
    # documented completeness limit: Σ_j F(j) is α-equal to Σ_i F(i)
    # but a Σ_i pattern does not match it
    i, j, F, G, S, f, g = _sx()
    assert match(S(i, f), S(i, F(i))) == {"f": F(i)}
    assert match(S(i, f), S(j, F(j))) is None


def test_true_same_named_sigma_proofs_still_close():
    # lie(Σ_i F(i), Σ_i F(i)) = 0 (antisymmetry instance; CLOSED on main)
    i, j, F, G, S, f, g = _sx()
    br = _CommBracket()
    rule = Rule(br(S(i, f), S(i, f)), Integer(0))
    t = br(S(i, F(i)), S(i, F(i)))
    assert prove(ExpansionEngine([_RuleAdapter(rule)]), t, Integer(0)).status == "CLOSED"


def test_free_term_is_not_captured_by_a_sigma():
    # ?g·Σ_i ?f → Σ_i (?g·?f): on i·Σ_i F(i) the outer i is free;
    # Σ_i (i·F(i)) would capture it. j·Σ_i F(i) is a legitimate push.
    i, j, F, G, S, f, g = _sx()
    rule = Rule(Product(g, S(i, f)), S(i, Product(g, f)))
    _closes_wrongly(rule, Product(i, S(i, F(i))), S(i, Product(i, F(i))))
    _closes_wrongly(rule, Product(G(i), S(i, F(i))), S(i, Product(F(i), G(i))))
    assert rule.try_at(Product(j, S(i, F(i)))) == S(i, Product(j, F(i)))


def test_bound_term_does_not_escape_its_sigma():
    i, j, F, G, S, f, g = _sx()
    pull = Rule(S(i, Product(g, f)), Product(g, S(i, f)))
    _closes_wrongly(pull, S(i, Product(F(i), i)), Product(F(i), S(i, i)))
    assert pull.try_at(S(i, Product(j, F(i)))) == Product(j, S(i, F(i)))
    # a value bound inside reused outside on the LEFT: Σ_i F(i)·F(i)
    k_rule = Rule(Product(S(i, f), f), S(i, Product(f, f)))
    _closes_wrongly(k_rule, Product(S(i, F(i)), F(i)), S(i, Product(F(i), F(i))))
    # a value depending on two binders, moved under one of them only
    two = Rule(S(i, Product(f, S(j, g))), Product(S(i, f), S(j, g)))
    t = S(i, Product(F(i), S(j, G(i, j))))
    _closes_wrongly(two, t, Product(S(i, F(i)), S(j, G(i, j))))
    assert two.try_at(S(i, Product(F(i), S(j, G(j))))) == Product(S(i, F(i)), S(j, G(j)))


def test_nested_same_named_sigmas_are_rejected():
    # Σ_i ?f · Σ_i ?g → Σ_i Σ_i (?f·?g): the inner Σ_i would capture
    # F's i (n = 2, F = G = id: 9 ≠ 10)
    i, j, F, G, S, f, g = _sx()
    cauchy = Rule(Product(S(i, f), S(i, g)), S(i, S(i, Product(f, g))))
    _closes_wrongly(cauchy, Product(S(i, F(i)), S(i, G(i))), S(i, S(i, Product(F(i), G(i)))))
    ok = Rule(Product(S(i, f), S(j, g)), S(i, S(j, Product(f, g))))
    assert ok.try_at(Product(S(i, F(i)), S(j, G(j)))) == S(i, S(j, Product(F(i), G(j))))


def test_binder_check_survives_sequence_backtracking():
    i, j, F, G, S, f, g = _sx()
    Z = lambda x: Act(Derivation("Z"), x)  # noqa: E731
    Q = lambda x: Act(Derivation("Q"), x)  # noqa: E731
    a, b, h = Symbol("a"), Symbol("b"), Wildcard("h")
    body = Product(S(i, f), SeqWildcard("r"), Z(h))
    rule = Rule(Q(body), body)
    t = Q(Product(S(i, F(i)), a, Z(b)))
    assert prove(ExpansionEngine([_RuleAdapter(rule)]), t, Product(S(i, F(i)), a, Z(b))).status == "CLOSED"
    _closes_wrongly(rule, t, Product(S(j, F(i)), a, Z(b)))
    lhs = Product(S(i, Product(f, g)), SeqWildcard("r"), Z(h))
    rhs = Product(S(i, f), g, SeqWildcard("r"), Z(h))
    _closes_wrongly(Rule(lhs, rhs), Product(S(i, Product(F(i), G(i))), a, Z(b)), Product(S(i, F(i)), G(i), a, Z(b)))


def test_sequence_binding_never_fills_a_single_position():
    i, j, F, G, S, f, g = _sx()
    a, b, x = Symbol("a"), Symbol("b"), Symbol("x")
    r = SeqWildcard("r")
    assert Rule(Sum(r, x), r).try_at(Sum(a, b, x)) is None
    assert Rule(Sum(r, x), S(i, r)).try_at(Sum(a, b, x)) is None
    assert Rule(Sum(r, x), Product(r, x)).try_at(Sum(a, b, x)) == Product(a, b, x)


def test_binder_contexts_are_not_shared_between_alpha_equal_rules():
    # Σ_i ?f·Σ_i ?g and Σ_i ?f·Σ_j ?g are α-EQUAL Exprs; their binder
    # contexts differ, so they must not be cached by equality
    i, j, F, G, S, f, g = _sx()
    bad = Rule(Product(S(i, f), S(i, g)), S(i, S(i, Product(f, g))))
    ok = Rule(Product(S(i, f), S(j, g)), S(i, S(j, Product(f, g))))
    assert bad.lhs == ok.lhs
    assert bad.try_at(Product(S(i, F(i)), S(i, G(i)))) is None
    assert ok.try_at(Product(S(i, F(i)), S(j, G(j)))) == S(i, S(j, Product(F(i), G(j))))
    assert bad.try_at(Product(S(i, F(i)), S(i, G(i)))) is None


def test_cited_records_replay_status_is_visible():
    # after the proof-trust-2 rebase: a record built from hand-made steps
    # is legacy/unreplayed. Lemma 9.1 (LieZ) and the DDZero record are
    # now library chains; the Uchino / (7.2) provers are two-leg
    # narrative chains (strip by non-degeneracy) — their `unreplayed`
    # markers flow, VISIBLY, into every result citing them (a later task)
    from jacopy.packages.generalized.bourbaki_exact import LieZDefinitionRule, exact_bourbaki_context
    from jacopy.packages.generalized.bourbaki_severa import RightLeibnizTheoremRule
    from jacopy.packages.generalized.courant_axioms import (
        DDZeroDefinition,
        DPairingUnfoldDefinition,
        courant_context,
    )

    liez = LieZDefinitionRule(exact_bourbaki_context("X")).theorem
    assert liez.chain_replayed and not liez.legacy
    C = courant_context("C")
    dd = DDZeroDefinition(C).theorem
    assert not any(a.kind == "legacy" for a in dd.requires)  # its own chain is minted
    assert any(a.kind == "unreplayed" and "uchino_d_formula" in a.name for a in dd.requires)
    dp = DPairingUnfoldDefinition(C).theorem
    assert any(a.kind == "unreplayed" for a in dp.requires)
    reg = PropertyRegistry()
    rl = RightLeibnizTheoremRule(algebroid("E", declare=("bourbaki-invariance",)), reg).theorem
    assert any(a.kind == "unreplayed" for a in rl.requires)


def test_alpha_equal_rules_do_not_share_payload_or_names():
    # ⋆_{Σ_i ?m} and ⋆_{Σ_j ?m} patterns are α-EQUAL; a global
    # equality-keyed cache made the Σ_j rule match ⋆_{Σ_i Q(i)} after
    # the Σ_i rule had run (order-dependent escape, review of 65bf04e)
    i, j, F, G, S, f, g = _sx()
    a = Symbol("a")
    Q = lambda x: Act(Derivation("Q"), x)  # noqa: E731
    x, m = Wildcard("x"), Wildcard("m")

    def mk(d):
        return Rule(HodgeStar(x, 3, metric=S(d, m)), HodgeStar(Product(x, x), 3, metric=S(d, m)))

    t = HodgeStar(a, 3, metric=S(i, Q(i)))
    assert mk(j).try_at(t) is None  # cold
    assert mk(i).try_at(t) == HodgeStar(Product(a, a), 3, metric=S(i, Q(i)))
    assert mk(j).try_at(t) is None  # warm


def test_frame_atoms_count_as_dummy_occurrences():
    # e_a and δ^a_b carry the index a in a slot: traverse.contains missed
    # them (escape and capture through a frame atom)
    from jacopy.central.objects.frame import FrameField, FrameIndex, KroneckerDelta

    a = FrameIndex("a")
    f, g = Wildcard("f"), Wildcard("g")
    S = lambda d, b: IndexedSum(d, None, b)  # noqa: E731
    eA, eB, c = FrameField("e", "a"), FrameField("e", "b"), Symbol("c")
    pull = Rule(S(a, Product(f, g)), Product(g, S(a, f)))
    assert pull.try_at(S(a, Product(eA, c))) == Product(c, S(a, eA))
    assert pull.try_at(S(a, Product(eA, eA))) is None
    push = Rule(Product(S(a, f), g), S(a, Product(f, g)))
    assert push.try_at(Product(S(a, eB), eA)) is None
    assert push.try_at(Product(S(a, eB), KroneckerDelta("a", "b"))) is None
    assert push.try_at(Product(S(a, eB), c)) == S(a, Product(eB, c))
    # alpha_equal: an inner binder's own occurrence is not free
    from jacopy.core.indexed_sum import dummy_in

    assert dummy_in(eA, a)


def test_sequence_splices_into_any_children_run():
    # Wedge(a, ?*r) → Wedge(?*r, a): main rewrote it; 65bf04e refused
    # every non-Sum/Product run (regression)
    from jacopy.core.wedge import Wedge

    a, b, c = Symbol("a"), Symbol("b"), Symbol("c")
    r, x = SeqWildcard("r"), Wildcard("x")
    assert Rule(Wedge(a, r), Wedge(r, a)).try_at(Wedge(a, b, c)) == Wedge(b, c, a)
    assert Rule(Sum(x, r), Product(r, x)).try_at(Sum(a, b, c)) == Product(b, c, a)


def test_sigma_wildcard_dummy_in_payload_refused():
    i, j, F, G, S, f, g = _sx()
    with pytest.raises(ValueError):
        Rule(HodgeStar(Wildcard("x"), 3, metric=S(Wildcard("D"), Wildcard("m"))), Wildcard("x"))


def test_alpha_equal_ignores_an_inner_binders_own_dummy():
    i, j, F, G, S, f, g = _sx()
    p = S(i, S(i, F(i)))
    q = S(j, S(i, F(i)))
    assert p == q and alpha_equal(p, q)
