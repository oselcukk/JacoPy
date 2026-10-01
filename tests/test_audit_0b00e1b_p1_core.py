"""Audit 0b00e1b-FULL — P1 core lane.

* K1-3 (with G7 = K1-4 ≡ M1X-7): the bracket obstruction helpers take
  their signs from ONE bracket-specific grading hook
  (``GradedBracket.operand_degree`` / ``grading_degree`` /
  ``module_product``); Schouten–Nijenhuis grades in the multivector
  grading (``s = m − 1``), and the Leibniz sign carries the bracket
  degree ``k``.

Every acceptance test builds the wrong target here and shows it fails,
next to the correct one closing.
"""

from itertools import product as iproduct

import pytest

from jacopy.brackets.base import BracketApply, GradedBracket
from jacopy.central.objects import functions, vector_fields
from jacopy.central.objects.multivector import PVector
from jacopy.central.tangent import tangent_engine
from jacopy.central.tangent.schouten import SN
from jacopy.core.expr import Integer, Neg, Product, Sum, Symbol
from jacopy.core.properties import Graded
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.algorithms import simplify
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure


# --------------------------------------------------------------------- #
# K1-3: Schouten–Nijenhuis obstructions in the multivector grading       #
# --------------------------------------------------------------------- #
#
# Sign convention, derived by hand from the library's SN definition
# (schouten.py: [X,f] = X(f), [f,X] = −X(f), [X,Y] = [X,Y]_Lie and the
# wedge-Leibniz recursion [Z, X∧Y] = [Z,X]∧Y + (−1)^{s(Z)m(X)} X∧[Z,Y],
# [X∧Y, Z] = X∧[Y,Z] + (−1)^{s(Z)m(Y)} [X,Z]∧Y, s = m − 1):
#
#   (1,0)  [X, f] = X(f) = −[f, X]                    → ε = −1, s·s = 0·(−1) even
#   (2,1)  [X∧Y, Z] = X∧[Y,Z] + [X,Z]∧Y
#          [Z, X∧Y] = [Z,X]∧Y + X∧[Z,Y] = −[X∧Y, Z]  → ε = −1, s·s = 1·0 even
#   (2,0)  [X∧Y, f] = X∧Y(f) − X(f)∧Y
#          [f, X∧Y] = −X(f)∧Y + X∧Y(f) = +[X∧Y, f]   → ε = +1, s·s = 1·(−1) odd
#   (2,2)  ε = +1: [π, π] = +[π, π], no constraint (s·s = 1·1 odd)
#
# i.e. [P, Q] = −(−1)^{(p−1)(q−1)} [Q, P], the literature convention
# (Marle; Vaisman, Lectures on the Geometry of Poisson Manifolds §1),
# and graded Jacobi Σ_cyc (−1)^{(p−1)(r−1)} [P, [Q, R]] = 0. The OLD
# obstruction used the operator degree (vector field 0, p-vector p):
# for (2,2) it built [π,π] + [π,π], i.e. "every bivector is Poisson".


def _tm():
    reg = PropertyRegistry()
    X, Y, Z, W = vector_fields("X Y Z W")
    (f,) = functions("f", registry=reg)
    return reg, X, Y, Z, W, f, tangent_engine(registry=reg)


def _closes(lhs, reg, eng):
    ExpandAndSimplify().prove(lhs, Integer(0), registry=reg, engine=eng)


def test_k1_3_sn_shifted_degree_hooks():
    reg, X, Y, Z, W, f, _ = _tm()
    pi = PVector("pi", degree=2)
    assert SN.grading_degree(pi, reg).as_int() == 2
    assert SN.operand_degree(pi, reg).as_int() == 1
    assert SN.operand_degree(X, reg).as_int() == 0
    assert SN.operand_degree(f, reg).as_int() == -1
    assert SN.operand_degree(Wedge(X, Y), reg).as_int() == 1
    # ε in [a, b] = ε [b, a]: −(−1)^{(p−1)(q−1)}
    for p, q in iproduct(range(4), repeat=2):
        a = [f, X, pi, PVector("P3", degree=3)][p]
        b = [f, Y, PVector("B2", degree=2), PVector("Q3", degree=3)][q]
        expected = -((-1) ** ((p - 1) * (q - 1)))
        assert SN.pair_swap_sign(a, b, reg) == expected, (p, q)
    # undeterminable multivector degree: no guessed sign
    with pytest.raises(ValueError):
        SN.pair_swap_sign(Symbol("u"), X, reg)


def test_k1_3_sn_bivector_antisymmetry_is_no_constraint():
    # the audit's acceptance: (π, π) must NOT produce a "= 0" claim
    pi = PVector("pi", degree=2)
    ob = SN.graded_antisymmetry_obstruction(pi, pi)
    assert simplify(ob) == Integer(0)  # [π,π] − [π,π]: trivially 0
    P, Q = PVector("P3", degree=3), PVector("Q3", degree=3)
    assert SN.graded_antisymmetry_obstruction(P, Q) == Sum(SN(P, Q), SN(Q, P))
    A, B = PVector("A2", degree=2), PVector("B2", degree=2)
    assert SN.graded_antisymmetry_obstruction(A, B) == Sum(SN(A, B), Neg(SN(B, A)))


@pytest.mark.parametrize("case", ["bivectors", "pi_pi", "bivector_function"])
def test_k1_3_sn_antisymmetry_closes_and_wrong_sign_fails(case):
    reg, X, Y, Z, W, f, eng = _tm()
    a, b = {
        "bivectors": (Wedge(X, Y), Wedge(Z, W)),
        "pi_pi": (Wedge(X, Y), Wedge(X, Y)),
        "bivector_function": (Wedge(X, Y), f),
    }[case]
    _closes(SN.graded_antisymmetry_obstruction(a, b, reg), reg, eng)
    # the OLD (operator-degree) target: [a,b] + [b,a] for these pairs
    with pytest.raises(ProofFailure):
        _closes(Sum(SN(a, b), SN(b, a)), reg, eng)


def test_k1_3_sn_jacobi_signs():
    # mixed degrees (1, 2, 2): signs (−1)^{s(a)s(c)} = +, +, − (s = 0, 1, 1)
    X = vector_fields("X")[0]
    A, B = PVector("A2", degree=2), PVector("B2", degree=2)
    ob = SN.graded_jacobi_obstruction(X, A, B)
    assert ob == Sum(SN(X, SN(A, B)), SN(A, SN(B, X)), Neg(SN(B, SN(X, A))))
    assert [SN.jacobi_term_sign(*t) for t in ((X, A, B), (A, B, X), (B, X, A))] == [1, 1, -1]


def test_k1_3_sn_leibniz_over_wedge():
    reg, X, Y, Z, W, f, eng = _tm()
    P = Wedge(X, Y)
    # (a function factor inside the wedge, (P | f, Z), is checked by the
    # oracle test below: the engine does not normalize f∧Z vs f·Z)
    for a, b, c in ((P, Z, W), (f, Z, W), (X, Z, W)):
        ob = SN.leibniz_obstruction(a, b, c, reg)
        _closes(ob, reg, eng)
    # (2 | 1, 1): s(P)·m(Z) = 1 odd → b∧[a,c] enters with +; the
    # flipped sign must fail
    wrong = Sum(
        SN(P, Wedge(Z, W)), Neg(Wedge(SN(P, Z), W)), Neg(Wedge(Z, SN(P, W)))
    )
    with pytest.raises(ProofFailure):
        _closes(wrong, reg, eng)


def test_k1_3_sn_obstructions_agree_with_model_oracle():
    pytest.importorskip("sympy")
    from jacopy.oracle.check import check_equal

    reg = PropertyRegistry()
    (g,) = functions("g", registry=reg)
    X = vector_fields("X")[0]
    A, B = PVector("A2", degree=2), PVector("B2", degree=2)
    P3 = PVector("P3", degree=3)

    def verdict(e):
        return check_equal(e, Integer(0), registry=reg, owners=[], samples=2).verdict

    for a, b in ((A, B), (A, A), (A, g), (X, P3), (A, P3)):
        assert verdict(SN.graded_antisymmetry_obstruction(a, b, reg)) == "AGREE"
    assert verdict(Sum(SN(A, B), SN(B, A))) == "DISAGREE"  # old (2,2) claim
    assert verdict(Sum(SN(A, g), SN(g, A))) == "DISAGREE"  # old (2,0) claim
    good = SN.graded_jacobi_obstruction(X, A, B, reg)
    assert verdict(good) == "AGREE"
    assert verdict(Sum(SN(X, SN(A, B)), SN(A, SN(B, X)), SN(B, SN(X, A)))) == "DISAGREE"
    assert verdict(SN.leibniz_obstruction(A, X, vector_fields("Y")[0], reg)) == "AGREE"
    assert verdict(SN.leibniz_obstruction(A, g, X, reg)) == "AGREE"
    assert verdict(SN.leibniz_obstruction(g, X, A, reg)) == "AGREE"


# --------------------------------------------------------------------- #
# G7 (K1-4 ≡ M1X-7): Leibniz sign carries the bracket degree k            #
# --------------------------------------------------------------------- #


class _ExteriorSN(GradedBracket):
    """The coordinate SN bracket on ℝ[x] ⊗ Λ(e_x, e_y) as a degree −1
    bracket on the exterior algebra (|x| = 0, |e| = 1): the three values
    the test needs, from [x, e_x] = −1 and the degree −1 derivation rule
    (audit exp/V-K1/v4_leibniz.py)."""

    def __init__(self, f, ey, ex, degree=-1):
        super().__init__("SNext", degree=degree)
        self._t = {(f, ey): Integer(0), (f, ex): Integer(-1), (f, Product(ey, ex)): ey}

    def expand(self, a, b, registry=None):
        return self._t.get((a, b), BracketApply(self, a, b))


def test_g7_leibniz_sign_uses_shifted_degree_of_a():
    f, ey, ex = Symbol("x"), Symbol("ey"), Symbol("ex")
    reg = PropertyRegistry()
    for s, d in ((f, 0), (ey, 1), (ex, 1)):
        reg.declare(s, Graded(d))
    B = _ExteriorSN(f, ey, ex)

    def expand(e):
        if isinstance(e, BracketApply):
            return B.expand(e.a, e.b)
        return e._rebuild(tuple(map(expand, e.children))) if e.children else e

    # hand table for k = −1: sign (−1)^{(|a|−1)|b|}
    for da, db, sign in ((0, 0, 1), (0, 1, -1), (1, 1, 1), (2, 1, -1), (1, 0, 1)):
        a, b = Symbol(f"a{da}{db}"), Symbol(f"b{da}{db}")
        reg.declare(a, Graded(da))
        reg.declare(b, Graded(db))
        assert B.leibniz_term_sign(a, b, reg) == sign, (da, db)
    ob = B.leibniz_obstruction(f, ey, ex, reg)
    assert simplify(expand(ob), reg) == Integer(0)
    # the old unshifted target [x, ey·ex] − [x,ey]·ex − ey·[x,ex] = 2·ey
    old = Sum(B(f, Product(ey, ex)), Neg(Product(B(f, ey), ex)), Neg(Product(ey, B(f, ex))))
    assert simplify(expand(old), reg) != Integer(0)
    # degree-0 brackets are unchanged: (−1)^{|a||b|}
    C = _ExteriorSN(f, ey, ex, degree=0)
    assert C.leibniz_term_sign(ey, ex, reg) == -1
    assert C.leibniz_term_sign(f, ex, reg) == 1
