"""Audit 0b00e1b (2026-09-30) — core product rule / pairing collection.

Acceptance tests for

* P0-1 (K1-2 ≡ M1X-1): the wedge Leibniz sign reads the EXTERIOR degree
  of the wedge factors, not their operator degree;
* P0-2 (M1-3): only a certified scalar function in operator position
  acts by multiplication (a degree-0 operator like Λ♯(dh) does not);
* K1-1 ≡ M1X-5: collect_pairings folds only certified scalar
  coefficients into the pairing slot;

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


def _dtilde_u():
    from jacopy.central.objects import functions
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    (u,) = functions("u", registry=reg)
    D, _ = _tilde()
    return D, u, reg


def test_p0_1_followup_mixed_sum_factor_not_expanded():
    # (a) X + u has no single exterior degree (1 vs 0): the sign
    # (−1)^{|d̃|·|X+u|} does not exist, so the node stays inert. The old
    # fallback read the operator degree (|X+u| = 0) and gave "+" for the
    # second term, which is wrong on the X-part: d̃(X∧Y) has "−".
    D, u, reg = _dtilde_u()
    X, Y = vector_fields("X Y")
    node = Act(D, Wedge(Sum(X, u), Y))
    assert product_rule(node, reg) == node


def test_p0_1_followup_scalar_product_graded_exteriorly():
    # (b) X·u = u·X = X∧u (C∞-module product). Graded Leibniz in the
    # exterior grading (|X| = 1, |u| = 0, |d̃| = 1):
    #   d̃(X·u) = d̃X·u + (−1)^{1·1} X∧d̃u = d̃X·u − X∧d̃u
    #   d̃(u·X) = d̃u∧X + (−1)^{1·0} u·d̃X
    #   d̃(X∧u) = d̃X∧u − X∧d̃u.
    # (the old Product path used |X| = 0: d̃X·u + X·d̃u).
    from jacopy.core.expr import Product

    D, u, reg = _dtilde_u()
    (X,) = vector_fields("X")
    dX, du = Act(D, X), Act(D, u)
    assert product_rule(Act(D, Product(X, u)), reg) == Sum(
        Product(dX, u), Neg(Wedge(X, du))
    )
    assert product_rule(Act(D, Product(u, X)), reg) == Sum(
        Wedge(du, X), Product(u, dX)
    )
    # all three spellings agree
    spellings = (Product(X, u), Product(u, X), Wedge(X, u))
    for a in spellings:
        for b in spellings:
            assert show_equal(Act(D, a), Act(D, b), registry=reg).steps


def test_p0_1_followup_composition_factor_not_expanded():
    # (d) X·Y inside a wedge is a composition X∘Y, not a bivector —
    # no exterior degree is invented for it: the node stays inert.
    from jacopy.core.expr import Product

    D, _, reg = _dtilde_u()
    X, Y, Z = vector_fields("X Y Z")
    node = Act(D, Wedge(Product(X, Y), Z))
    assert product_rule(node, reg) == node


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


# P0-2 follow-up (code review) ------------------------------------------ #
#
# Leibniz is a DERIVATION's property: D(ab) = D(a)b ± aD(b). Default
# reject: only a Derivation (not marked leibniz=False), an operator that
# declares leibniz=True, or a commutator of two such is split. The
# public musical Sharp is C∞-LINEAR (Λ♯(f·dh) = f·Λ♯(dh)), not a
# derivation — the old split produced the false Λ♯(f·dh) =
# Λ♯(f)·dh + f·Λ♯(dh); likewise a Graded(1) symbol Q is no derivation.


def test_p0_2_followup_non_derivation_is_not_split():
    from jacopy.core.expr import Product, Symbol
    from jacopy.core.properties import Graded

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    from jacopy.central.objects import functions

    (f,) = functions("f", registry=reg)
    S = Sharp(lam)
    node = Act(S, Product(f, dh))
    assert product_rule(node, reg) == node
    false_leibniz = Sum(Product(Act(S, f), dh), Product(f, Act(S, dh)))
    with pytest.raises(ProofFailure):
        show_equal(node, false_leibniz, registry=reg)
    Q = Symbol("Q")
    reg.declare(Q, Graded(1))
    nodeQ = Act(Q, Product(a, b))
    assert product_rule(nodeQ, reg) == nodeQ


def test_p0_2_followup_numeric_factor_pulls_out_of_linear_operator():
    # (h) ℝ-linearity of any operator: X_h(2·a) = 2·X_h(a); a FUNCTION
    # factor does not pull out (X_h(f·a) ≠ f·X_h(a) in general).
    from jacopy.core.expr import Integer, Product

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    V = Act(Sharp(lam), dh)
    assert product_rule(Act(V, Product(Integer(2), a)), reg) == Product(
        Integer(2), Act(V, a)
    )
    assert product_rule(Act(V, Product(b, a)), reg) == Act(V, Product(b, a))


def test_p0_2_followup_splits_over_product_protocol():
    # (e) operator-level protocol: splits_over_product(arg, registry)
    # -> False keeps Act(op, f·Y) unexpanded, in product_rule AND in the
    # engine rule ActExpansionDefinition (same code path).
    from jacopy.algebra.derivation import Derivation
    from jacopy.central.calculus import ActExpansionDefinition
    from jacopy.central.objects import functions
    from jacopy.core.expr import Product
    from jacopy.core.registry import PropertyRegistry

    class NoRightLeibniz(Derivation):
        def splits_over_product(self, arg, registry=None):
            return False

    class YesLeibniz(Derivation):
        def splits_over_product(self, arg, registry=None):
            return True

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    (Y,) = vector_fields("Y")
    L = NoRightLeibniz("L", degree=0)
    node = Act(L, Product(f, Y))
    assert product_rule(node, reg) == node
    assert not ActExpansionDefinition(reg).matches(node)
    # linearity still applies
    assert product_rule(Act(L, Sum(f, Y)), reg) == Sum(Act(L, f), Act(L, Y))
    M = YesLeibniz("M", degree=0)
    assert product_rule(Act(M, Product(f, Y)), reg) == Sum(
        Product(Act(M, f), Y), Product(f, Act(M, Y))
    )


def test_p0_2_followup_endoform_of_vector_is_not_scalar():
    # (f) m̃ acts on FORMS; m̃(X) for a vector field X has no form degree
    # (X's instance degree 0 is its operator degree) and is no scalar.
    from jacopy.central.calculus.scalars import is_scalar_function
    from jacopy.central.objects.endomorphism import EndoForm

    (X,) = vector_fields("X")
    (alpha,) = forms("alpha", degree=1)
    assert not is_scalar_function(EndoForm("m", X))
    with pytest.raises(AttributeError):
        EndoForm("m", X).degree
    assert EndoForm("m", alpha).degree == alpha.degree


def test_p0_2_followup_genuine_scalars_certified():
    # (g) sound type certificates, not degree: ι_X α with α a 1-form is
    # a function (1 − 1 = 0, form⊗vector contraction); f² for a function
    # f; the value of a bracket DECLARED function-valued on functions
    # (Poisson-type {f, g}). Λ♯(dh) (degree 0, a vector) stays rejected.
    from jacopy.brackets.base import GradedBracket
    from jacopy.central.calculus.scalars import is_scalar_function
    from jacopy.central.objects import functions
    from jacopy.central.objects.interior import Interior
    from jacopy.central.tangent.lie_bracket import (
        ScalarActAsMultiplicationDefinition,
    )
    from jacopy.core.expr import Integer, Power, Product

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    (f,) = functions("f", registry=reg)
    (X,) = vector_fields("X")
    (alpha,) = forms("alpha", degree=1)

    class PB(GradedBracket):
        function_valued = True

        def expand(self, a, b, registry=None):
            raise NotImplementedError

    class Undeclared(GradedBracket):
        def expand(self, a, b, registry=None):
            raise NotImplementedError

    iota = Act(Interior(X), alpha)
    for s in (iota, Power(f, Integer(2)), PB("pb")(a, b)):
        assert is_scalar_function(s, reg), s
        # acts by multiplication in operator position
        assert product_rule(Act(s, Product(a, b)), reg) == Product(
            s, Product(a, b)
        )
        assert ScalarActAsMultiplicationDefinition(reg).matches(Act(s, a))
    assert not is_scalar_function(Undeclared("u")(a, b), reg)
    assert not is_scalar_function(Act(Sharp(lam), dh), reg)


# --------------------------------------------------------------------- #
# K1-1 ≡ M1X-5 — collect_pairings folds only SCALAR coefficients         #
# --------------------------------------------------------------------- #
#
# ⟨α,·⟩ is C∞(M)-linear: Σ sᵢ⟨α,Vᵢ⟩ = ⟨α, Σ sᵢVᵢ⟩ for FUNCTIONS sᵢ.
# A vector field A is not such a coefficient: ⟨α,U⟩·A is the vector
# field (⟨α,U⟩)A, whereas ⟨α, A∘U⟩ has a second-order operator in the
# vector slot. Hand check on ℝ: α = dx, U = ∂x, V = 2∂x, A = ∂x,
# B = 3∂x: ⟨α,U⟩A + ⟨α,V⟩B = ∂x + 6∂x = 7∂x (a vector), but the old
# output's slot A∘U + B∘V = 7∂x² kills x and sends x² to 14 — not a
# derivation, so ⟨dx, 7∂x²⟩ is not a pairing at all.


def _pairing_setup():
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    (alpha,) = forms("alpha", degree=1)
    U, V, A, B = vector_fields("U V A B")
    return reg, alpha, U, V, A, B


def test_k1_1_vector_coefficients_are_not_folded():
    from jacopy.algebra.derivation import Derivation
    from jacopy.algorithms.factor_terms import collect_pairings
    from jacopy.algorithms.simplify import simplify
    from jacopy.central.objects.kind import kind_of
    from jacopy.core.expr import Product
    from jacopy.core.pairing import Pairing

    reg, alpha, U, V, A, B = _pairing_setup()
    # vector field coefficient on the right (M1X-5) and left
    for expr in (
        Sum(Product(Pairing(alpha, U), A), Product(Pairing(alpha, V), B)),
        Sum(Product(Pairing(alpha, U), A), Product(Pairing(alpha, V), A)),
    ):
        out = simplify(expr, reg)
        assert out == expr
        assert kind_of(out, reg).kind == "vector"
        assert collect_pairings(expr, reg) == expr
        assert collect_pairings(expr) == expr
    # abstract derivations on the left (K1-1 ledger acceptance)
    D, E = Derivation("D", degree=0), Derivation("E", degree=0)
    X, Y = U, V
    expr = Sum(Product(D, Pairing(alpha, X)), Product(E, Pairing(alpha, Y)))
    assert simplify(expr, reg) == expr


def test_k1_1_scalar_coefficients_still_fold():
    from jacopy.algorithms.factor_terms import collect_pairings
    from jacopy.algorithms.simplify import simplify
    from jacopy.central.objects import functions
    from jacopy.core.expr import Integer, Product, Symbol
    from jacopy.core.pairing import Pairing
    from jacopy.core.properties import Scalar

    reg, alpha, U, V, _, _ = _pairing_setup()
    f, g = functions("f g", registry=reg)
    s, t = Symbol("s"), Symbol("t")
    reg.declare(s, Scalar())
    reg.declare(t, Scalar())
    # left and right scalar coefficients: f⟨α,U⟩ + ⟨α,V⟩g = ⟨α, fU + gV⟩
    expr = Sum(Product(f, Pairing(alpha, U)), Product(Pairing(alpha, V), g))
    assert collect_pairings(expr, reg) == Pairing(
        alpha, Sum(Product(f, U), Product(g, V))
    )
    # registry-declared Scalar symbols through the full simplify pipeline
    expr2 = Sum(Product(s, Pairing(alpha, U)), Product(t, Pairing(alpha, V)))
    folded = simplify(expr2, reg)
    assert isinstance(folded, Pairing) and folded.alpha == alpha
    assert simplify(
        Sum(folded, Neg(Pairing(alpha, Sum(Product(s, U), Product(t, V))))), reg
    ) == Integer(0)
    # without a registry a declared symbol is NOT certified; numerals are
    assert collect_pairings(expr) == expr
    num = Sum(Product(Integer(2), Pairing(alpha, U)), Product(Integer(3), Pairing(alpha, V)))
    assert collect_pairings(num) == Pairing(
        alpha, Sum(Product(Integer(2), U), Product(Integer(3), V))
    )


def test_k1_1_followup_type_certified_coefficients_fold():
    # K1-1 follow-up (code review, item g): the scalar gate must not
    # lose genuine C∞ coefficients. ι_X α (α a 1-form) and f² are
    # functions, so ι_Xα·⟨β,U⟩ + f²·⟨β,V⟩ = ⟨β, ι_Xα·U + f²·V⟩; a
    # degree-0 VECTOR (Λ♯(dh)) or m̃(X) is still not folded.
    from jacopy.algorithms.factor_terms import collect_pairings
    from jacopy.central.objects import functions
    from jacopy.central.objects.endomorphism import EndoForm
    from jacopy.central.objects.interior import Interior
    from jacopy.core.expr import Integer, Power, Product
    from jacopy.core.pairing import Pairing

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    (f,) = functions("f", registry=reg)
    X, U, V = vector_fields("X U V")
    alpha, beta = forms("alpha beta", degree=1)
    iota, f2 = Act(Interior(X), alpha), Power(f, Integer(2))
    expr = Sum(Product(iota, Pairing(beta, U)), Product(f2, Pairing(beta, V)))
    assert collect_pairings(expr, reg) == Pairing(
        beta, Sum(Product(iota, U), Product(f2, V))
    )
    for bad in (Act(Sharp(lam), dh), EndoForm("m", X)):
        e = Sum(Product(bad, Pairing(beta, U)), Product(f2, Pairing(beta, V)))
        assert collect_pairings(e, reg) == e


# --------------------------------------------------------------------- #
# Second code review: ONE type source (kind_of); is_scalar_function is   #
# a thin wrapper                                                         #
# --------------------------------------------------------------------- #


def test_review2_interior_needs_a_certified_vector():
    # (1) ι_P α is a (q−p)-form for a p-vector P and a q-form α; the
    # Interior node is the p = 1 contraction. ι_Λ(dh) with Λ a BIVECTOR
    # is not a function (in the other contraction convention it is the
    # VECTOR Λ♯dh), so it must not act by multiplication:
    # X_h(f·g) = X_h(f)g + fX_h(g) ≠ X_h·f·g. Likewise ι_W α (W
    # undeclared), ι_f α, ι_{X∘Y} α are untyped. ι_X α, ι_{X+Y} α stay
    # functions.
    from jacopy.central.calculus.scalars import is_scalar_function
    from jacopy.central.objects import functions
    from jacopy.central.objects.interior import Interior
    from jacopy.core.expr import Product, Symbol

    reg, a, b, lam, dh, Sharp = _hamiltonian_setup()
    (f,) = functions("f", registry=reg)
    X, Y = vector_fields("X Y")
    (alpha,) = forms("alpha", degree=1)
    V = Act(Interior(lam), dh)
    assert not is_scalar_function(V, reg)
    with pytest.raises(ProofFailure):
        show_equal(Act(V, Product(a, b)), Product(V, a, b), registry=reg)
    for bad in (Symbol("W"), f, Product(X, Y), lam):
        assert not is_scalar_function(Act(Interior(bad), alpha), reg), bad
    for good in (X, Sum(X, Y)):
        assert is_scalar_function(Act(Interior(good), alpha), reg), good


def test_review2_power_needs_nonnegative_integer_exponent():
    # (2) f⁻¹ and f^½ are not C∞ in general; 0⁻¹ is undefined.
    from jacopy.central.calculus.scalars import is_scalar_function
    from jacopy.central.objects import functions
    from jacopy.core.expr import Integer, Power, Rational
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    (X,) = vector_fields("X")
    assert is_scalar_function(Power(f, Integer(2)), reg)
    assert is_scalar_function(Power(f, Integer(0)), reg)
    for bad in (
        Power(f, Integer(-1)),
        Power(f, Rational(1, 2)),
        Power(Integer(0), Integer(-1)),
        Power(X, Integer(2)),
    ):
        assert not is_scalar_function(bad, reg), bad


def test_review2_function_valued_declaration_is_guarded():
    # (5) a raising declaration certifies nothing (and does not raise).
    from jacopy.brackets.base import GradedBracket
    from jacopy.central.calculus.scalars import is_scalar_function

    reg, a, b, *_ = _hamiltonian_setup()

    class Broken(GradedBracket):
        def function_valued(self, a, b, registry):
            raise RuntimeError("boom")

        def expand(self, a, b, registry=None):
            raise NotImplementedError

    class Callable_(GradedBracket):
        def function_valued(self, a, b, registry):
            return True

        def expand(self, a, b, registry=None):
            raise NotImplementedError

    assert not is_scalar_function(Broken("x")(a, b), reg)
    assert is_scalar_function(Callable_("y")(a, b), reg)


def test_review2_form_product_degree_and_endoform():
    # (6) α·β (forms) is the library's transient spelling of α∧β: an
    # exterior 2-form, so m̃(α·β) has degree 2 and
    # d(m̃(α·β)·α) = d m̃(α·β)·α + (−1)^2 m̃(α·β)·dα.
    from jacopy.central.objects.endomorphism import EndoForm
    from jacopy.central.objects.kind import Kind, kind_of
    from jacopy.central.tangent.exterior import exterior_d
    from jacopy.core.expr import Integer, Power, Product

    alpha, beta = forms("alpha beta", degree=1)
    g = Form("g", degree=0)
    k = kind_of(Product(alpha, beta))
    assert (k.kind, k.degree) == ("form", Kind("form", 2).degree)
    m = EndoForm("m", Product(alpha, beta))
    from jacopy.core.symbolic_degree import Degree

    assert m.degree == Degree.const(2)
    assert EndoForm("m", Power(g, Integer(2))).degree == Degree.const(0)
    d = exterior_d()
    assert product_rule(Act(d, Product(m, alpha))) == Sum(
        Product(Act(d, m), alpha), Product(m, Act(d, alpha))
    )


def test_review2_product_path_never_uses_operator_degree_for_vectors():
    # (3) S = X + Y(Z) has no exterior type (Y(Z) is untyped). The old
    # Product path graded it by the operator degree (|S| = 0) and closed
    # the false d̃(S·u) = d̃S·u + S·d̃u (on the X part the sign is "−":
    # d̃(X·u) = d̃X·u − X∧d̃u). Now: ℝ-bilinearity splits the sum, the
    # typed piece expands, the untyped one stays inert — and the
    # linearity statement d̃(S·u) = d̃(X·u) + d̃(Y(Z)·u) closes.
    # d̃(X·Y) and d̃(u·X·Y) are compositions: inert.
    from jacopy.core.expr import Product

    D, u, reg = _dtilde_u()
    X, Y, Z = vector_fields("X Y Z")
    S = Sum(X, Act(Y, Z))
    lhs = Act(D, Product(S, u))
    false_rhs = Sum(Product(Act(D, S), u), Product(S, Act(D, u)))
    with pytest.raises(ProofFailure):
        show_equal(lhs, false_rhs, registry=reg)
    lin = Sum(Act(D, Product(X, u)), Act(D, Product(Act(Y, Z), u)))
    assert show_equal(lhs, lin, registry=reg).steps
    for node in (Act(D, Product(X, Y)), Act(D, Product(u, X, Y))):
        assert product_rule(node, reg) == node


def test_review2_commutator_of_derivations():
    # (4) [X,Y] = XY − YX of two vector fields is a derivation of degree
    # |X|+|Y| = 0: [X,Y](f·g) = [X,Y](f)·g + f·[X,Y](g), [X,Y](2) = 0,
    # hence [X,Y](2g) = 2[X,Y](g). A commutator whose degree is not
    # determinable stays linear — no exception from an engine match.
    from jacopy.algebra.commutator import Commutator
    from jacopy.algebra.derivation import degree_of
    from jacopy.central.calculus import ActExpansionDefinition
    from jacopy.central.objects import functions
    from jacopy.core.expr import Integer, Product, Symbol
    from jacopy.core.registry import PropertyRegistry
    from jacopy.core.symbolic_degree import Degree

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    X, Y = vector_fields("X Y")
    C = Commutator(X, Y)
    assert degree_of(C, reg) == Degree.const(0)
    assert show_equal(
        Act(C, Product(f, g)),
        Sum(Product(Act(C, f), g), Product(f, Act(C, g))),
        registry=reg,
    ).steps
    assert show_equal(
        Act(C, Product(Integer(2), g)), Product(Integer(2), Act(C, g)),
        registry=reg,
    ).steps
    A, B = Symbol("A"), Symbol("B")
    node = Act(Commutator(A, B), Product(f, g))
    ActExpansionDefinition(reg).matches(node)  # must not raise
