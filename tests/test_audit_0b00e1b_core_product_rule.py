"""Audit 0b00e1b (2026-09-30) — core product rule / pairing collection.

Acceptance tests for

* P0-1 (K1-2 ≡ M1X-1): the wedge Leibniz sign reads the EXTERIOR degree
  of the wedge factors, not their operator degree;

each test builds the target identity itself and checks both the correct
and the wrong-sign statement.
"""

import pytest

from jacopy.algebra.derivation import Act
from jacopy.algorithms import product_rule
from jacopy.central.objects import forms, vector_fields
from jacopy.central.objects.form import Form
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.tilde_interior import TildeInterior
from jacopy.core.expr import Neg, Sum
from jacopy.core.wedge import Wedge
from jacopy.proof.strategies import ProofFailure
from jacopy.proof.verifier import show_equal


# --------------------------------------------------------------------- #
# P0-1 — graded Leibniz over the wedge                                   #
# --------------------------------------------------------------------- #
#
# A degree-|D| (anti)derivation of a graded-commutative algebra obeys
#     D(a∧b) = Da∧b + (−1)^{|D||a|} a∧Db,
# where |a| is the degree of a IN THAT ALGEBRA. On multivectors
# (Γ(ΛTM), the algebra d̃ = d_π and ι̃_ω act on) a vector field is a
# 1-vector: |X| = 1 — its operator degree 0 (as a derivation of C∞(M))
# is a different grading and must not enter the sign. Hence
#     d̃(X∧Y) = d̃X∧Y + (−1)^{1·1} X∧d̃Y = d̃X∧Y − X∧d̃Y.
# The bug read |X| = 0 and produced "+".


def _tilde():
    from jacopy.packages.poisson.core import poisson_structure
    from jacopy.packages.poisson.tilde import tilde_calculus, tilde_engine

    P = poisson_structure("pi", declare=("poisson",))
    return tilde_calculus(P).d, tilde_engine(P)


def test_p0_1_dtilde_wedge_minus_closes_plus_fails():
    D, eng = _tilde()
    X, Y = vector_fields("X Y")
    lhs = Act(D, Wedge(X, Y))
    minus = Sum(Wedge(Act(D, X), Y), Neg(Wedge(X, Act(D, Y))))
    plus = Sum(Wedge(Act(D, X), Y), Wedge(X, Act(D, Y)))
    for engine in (None, eng):
        kw = {} if engine is None else {"engine": engine}
        chain = show_equal(lhs, minus, **kw)
        assert chain.steps
        with pytest.raises(ProofFailure):
            show_equal(lhs, plus, **kw)


def test_p0_1_dtilde_triple_signs():
    # d̃(X∧Y∧Z): running degrees 0, 1, 2 -> signs +, −, +.
    D, _ = _tilde()
    X, Y, Z = vector_fields("X Y Z")
    expected = Sum(
        Wedge(Act(D, X), Y, Z),
        Neg(Wedge(X, Act(D, Y), Z)),
        Wedge(X, Y, Act(D, Z)),
    )
    assert product_rule(Act(D, Wedge(X, Y, Z))) == expected


def test_p0_1_dtilde_of_dtilde_factor_is_a_bivector():
    # d̃(d̃X ∧ Y) = d̃d̃X∧Y + (−1)^{1·|d̃X|} d̃X∧d̃Y with |d̃X| = 1+1 = 2:
    # the second term is POSITIVE. (Operator-degree reading: |d̃X| = 1+0
    # = 1, wrong minus sign.)
    D, _ = _tilde()
    X, Y = vector_fields("X Y")
    dX = Act(D, X)
    expected = Sum(Wedge(Act(D, dX), Y), Wedge(dX, Act(D, Y)))
    assert product_rule(Act(D, Wedge(dX, Y))) == expected


def test_p0_1_tilde_interior_contraction_value():
    # ι̃_dy on ex∧ey∧ez (|ι̃| = −1 ≡ 1 mod 2, |e_i| = 1):
    #   ι̃(ex)∧ey∧ez − ex∧ι̃(ey)∧ez + ex∧ey∧ι̃(ez)
    # With ⟨dy,ex⟩ = ⟨dy,ez⟩ = 0, ⟨dy,ey⟩ = 1 this is −ex∧ez, matching the
    # definition (ι̃_dy V)(dx,dz) = V(dy,dx,dz) = −1.
    w = Form("dy", degree=1)
    D = TildeInterior(w)
    ex, ey, ez = vector_fields("ex ey ez")
    expected = Sum(
        Wedge(Act(D, ex), ey, ez),
        Neg(Wedge(ex, Act(D, ey), ez)),
        Wedge(ex, ey, Act(D, ez)),
    )
    assert product_rule(Act(D, Wedge(ex, ey, ez))) == expected
    # The PVector spelling agrees (it always had the right degree).
    p, q, s = (PVector(n, degree=1) for n in ("p", "q", "s"))
    assert product_rule(Act(D, Wedge(p, q, s))) == Sum(
        Wedge(Act(D, p), q, s),
        Neg(Wedge(p, Act(D, q), s)),
        Wedge(p, q, Act(D, s)),
    )


def test_p0_1_forms_signs_unchanged():
    # Control: forms were already graded by their own degree.
    # d(α₁∧β₂) = dα∧β − α∧dβ ;  d(β₂∧α₁) = dβ∧α + β∧dα.
    from jacopy.central.tangent.exterior import exterior_d

    d = exterior_d()
    alpha = Form("alpha", degree=1)
    beta = Form("beta", degree=2)
    assert product_rule(Act(d, Wedge(alpha, beta))) == Sum(
        Wedge(Act(d, alpha), beta), Neg(Wedge(alpha, Act(d, beta)))
    )
    assert product_rule(Act(d, Wedge(beta, alpha))) == Sum(
        Wedge(Act(d, beta), alpha), Wedge(beta, Act(d, alpha))
    )
