"""Audit 0b00e1b (2026-09-30) — core product rule / pairing collection.

Acceptance tests for

* P0-1 (K1-2 ≡ M1X-1): the wedge Leibniz sign reads the EXTERIOR degree
  of the wedge factors, not their operator degree;
* P0-2 (M1-3): only a certified scalar function in operator position
  acts by multiplication (a degree-0 operator like Λ♯(dh) does not);

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


# --------------------------------------------------------------------- #
# P0-2 — a degree-0 NON-derivation operator is not a multiplier          #
# --------------------------------------------------------------------- #
#
# X_h = Λ♯(dh) is a vector field, i.e. a derivation of C∞(M):
#     X_h(a·b) = X_h(a)·b + a·X_h(b).
# Counterexample to the closed "X_h(a·b) = a·X_h(b)": on ℝ², Λ = ∂x∧∂y,
# h = y gives X_h = ±∂x and X_h(x·x) = ±2x ≠ ±x = x·X_h(x). Built with
# the public Sharp, Λ♯(dh) has degree −1 + 1 = 0 and is NOT a
# Derivation instance; product_rule used "degree 0" as the certificate
# for "scalar coefficient" and rewrote X_h(a·b) as the product
# X_h·(a·b). Only a certified C∞ scalar may act by multiplication; the
# raw node stays linear-only, and the Leibniz rule is available through
# the Derivation SharpVF.


def _hamiltonian_setup():
    import jacopy.central.objects.multivector as mv
    from jacopy.central.objects import functions
    from jacopy.central.objects.musical import Sharp
    from jacopy.central.tangent import d
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    a, b, h = functions("a b h", registry=reg)
    lam = mv.bivector("Λ")
    return reg, a, b, lam, d(h), Sharp


def test_p0_2_raw_sharp_is_not_a_multiplier():
    from jacopy.core.expr import Product

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    V = Act(Sharp(lam), dh)
    for lhs, rhs in (
        (Act(V, Product(a, b)), Product(a, Act(V, b))),  # V(ab) = a·V(b)
        (Act(V, Product(a, b)), Product(b, Act(V, a))),  # V(ab) = b·V(a)
        (Act(V, a), Product(a, V)),                      # V(a) = a·V
    ):
        with pytest.raises(ProofFailure):
            show_equal(lhs, rhs, registry=reg)
    # linear-only: sums still distribute (any operator is additive)
    assert product_rule(Act(V, Sum(a, b)), reg) == Sum(Act(V, a), Act(V, b))
    # and it is no longer turned into a product
    assert product_rule(Act(V, Product(a, b)), reg) == Act(V, Product(a, b))


def test_p0_2_sharpvf_leibniz_closes():
    from jacopy.core.expr import Product
    from jacopy.packages.poisson.core import SharpVF

    reg, a, b, lam, dh, _ = _hamiltonian_setup()
    V = SharpVF(lam, dh)
    leibniz = Sum(Product(Act(V, a), b), Product(a, Act(V, b)))
    assert show_equal(Act(V, Product(a, b)), leibniz, registry=reg).steps
    with pytest.raises(ProofFailure):
        show_equal(Act(V, Product(a, b)), Product(a, Act(V, b)), registry=reg)


def test_p0_2_certified_scalar_still_multiplies():
    # Control: (f·X)(g) = f·X(g) — a certified scalar in operator
    # position (module structure of vector fields) is a multiplier.
    from jacopy.central.objects import functions
    from jacopy.central.tangent.lie_bracket import (
        ScalarActAsMultiplicationDefinition,
    )
    from jacopy.core.expr import Product
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    (X,) = vector_fields("X")
    assert show_equal(
        Act(Product(f, X), g), Product(f, Act(X, g)), registry=reg
    ).steps
    rule = ScalarActAsMultiplicationDefinition(reg)
    assert rule.matches(Act(f, g))
    hreg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    # same registry that makes degree_of(Λ♯(dh)) = 0 determinable
    assert not ScalarActAsMultiplicationDefinition(hreg).matches(
        Act(Act(Sharp(lam), dh), a)
    )
