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
    # dummy i would rebuild Σ_i f(j) = n·f(j) ≠ Σ_j f(j)
    i, j = Symbol("i"), Symbol("j")
    fj = Act(Derivation("f"), j)
    target = IndexedSum(j, None, fj)
    assert match(IndexedSum(i, None, Wildcard("B")), target) is None
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
