"""Audit 0b00e1b-FULL — P1 core lane.

* K1-3 (with G7 = K1-4 ≡ M1X-7): the bracket obstruction helpers take
  their signs from ONE bracket-specific grading hook
  (``GradedBracket.operand_degree`` / ``grading_degree`` /
  ``module_product``); Schouten–Nijenhuis grades in the multivector
  grading (``s = m − 1``), and the Leibniz sign carries the bracket
  degree ``k``.
* M1-1 ≡ M1-2 (G4): the Scalar CONTRACT — ``Scalar`` is an ℝ-constant.
  NonCommuting beats Scalar in sort_product; a Scalar commutes with a
  derivation AND is annihilated by it (product_rule ``D(c) = 0``); it
  is still kind ``function``; AgreementOnGenerators refuses a Scalar
  generator (the contradictory "D(x) ≠ 0 for a constant x" input).

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


# --------------------------------------------------------------------- #
# M1-1 ≡ M1-2 (G4): Scalar = ℝ-constant                                   #
# --------------------------------------------------------------------- #
#
# ℝ[x], D = d/dx: (D∘x)(x) = D(x²) = 2x ≠ x = (x∘D)(x), so D∘x = x∘D is
# FALSE for a function x; for an ℝ-constant c, D∘c = c∘D + D(c) = c∘D
# is TRUE. The contract makes the two halves consistent.


def _scalar_world():
    from jacopy.algebra.derivation import Derivation
    from jacopy.core.properties import NonCommuting, Scalar

    reg = PropertyRegistry()
    D, x, c = Derivation("D", degree=0), Symbol("x"), Symbol("c")
    reg.declare(x, Scalar())
    reg.declare(D, NonCommuting())
    reg.declare(c, Scalar())
    (f,) = functions("f", registry=reg)
    return reg, D, x, c, f


def test_m1_1_noncommuting_beats_scalar():
    from jacopy.algebra.derivation import compose
    from jacopy.algorithms.sort_product import sort_product
    from jacopy.proof import show_equal
    from jacopy.proof.expansion import ExpansionEngine
    from jacopy.proof.result import prove

    reg, D, x, c, f = _scalar_world()
    # the audit's own fixture shape: x Scalar, D NonCommuting
    with pytest.raises(ProofFailure):
        show_equal(compose(D, x), compose(x, D), registry=reg)
    assert prove(ExpansionEngine(), compose(D, x), compose(x, D), registry=reg).status == "RESIDUAL"
    assert sort_product(Product(D, x), reg)[0] == Product(D, x)
    # a class-level NonCommuting still beats an exact Scalar (the
    # exact same-expression combination is refused by the registry)
    from jacopy.core.properties import NonCommuting

    E = vector_fields("E")[0]
    reg.declare_for_class(type(E), NonCommuting())
    assert sort_product(Product(E, c), reg)[0] == Product(E, c)


def test_m1_1_scalar_constant_commutes_and_is_annihilated_consistently():
    from jacopy.algebra.derivation import Act, Derivation, compose
    from jacopy.algorithms.product_rule import product_rule
    from jacopy.central.calculus.scalars import is_scalar_function
    from jacopy.central.objects.kind import kind_of
    from jacopy.proof import show_equal

    reg, _, _, c, f = _scalar_world()
    D = Derivation("Δ", degree=0)  # no NonCommuting declaration
    # (b) swap AND D(c) = 0 — the operator identity and its action agree
    show_equal(compose(D, c), compose(c, D), registry=reg)
    assert product_rule(Act(D, c), reg) == Integer(0)
    show_equal(Act(Sum(compose(D, c), Neg(compose(c, D))), f), Integer(0), registry=reg)
    show_equal(Act(D, Product(c, f)), Product(c, Act(D, f)), registry=reg)
    X = vector_fields("X")[0]
    eng = tangent_engine(registry=reg)
    show_equal(Act(X, c), Integer(0), registry=reg, engine=eng)
    # a FUNCTION is not killed and does not commute with an operator
    assert product_rule(Act(D, f), reg) == Act(D, f)
    with pytest.raises(ProofFailure):
        show_equal(compose(D, f), compose(f, D), registry=reg)
    with pytest.raises(ProofFailure):
        show_equal(Act(D, f), Integer(0), registry=reg)
    # (c) still a (constant) function
    assert kind_of(c, reg).kind == "function" and is_scalar_function(c, reg)


def test_m1_2_scalar_generator_is_refused():
    from jacopy.algebra.derivation import Act, Derivation, compose
    from jacopy.core.properties import Scalar
    from jacopy.proof.expansion import Definition, ExpansionEngine
    from jacopy.proof.verifier import prove_operator_equation

    E, y = Derivation("E", degree=0), Symbol("y")

    class EY(Definition):
        name = "E(y)=y"
        anchor = Act

        def matches(self, e):
            return e == Act(E, y)

        def rewrite(self, e):
            return y

    class Alg:
        generators = (y,)

    eng = ExpansionEngine([EY()])
    # Euler operator on ℝ[y]: (E∘y)(y²) = 3y³ ≠ 4y³ = (2y·E)(y²)
    for decl in (Scalar(), Graded(0)):
        reg = PropertyRegistry()
        reg.declare(y, decl)
        with pytest.raises(ProofFailure):
            prove_operator_equation(compose(E, y), Product(Integer(2), y, E), Alg(), registry=reg, engine=eng)
    reg = PropertyRegistry()
    reg.declare(y, Scalar())
    with pytest.raises(ProofFailure, match="declared Scalar"):
        prove_operator_equation(Product(y, E), Product(y, E), Alg(), registry=reg, engine=eng)
    # a correct operator equation with a Graded(0) generator still closes
    reg = PropertyRegistry()
    reg.declare(y, Graded(0))
    prove_operator_equation(Product(Integer(2), E), Sum(E, E), Alg(), registry=reg, engine=eng)


def test_m1_1_scalar_contract_matches_the_model_oracle():
    pytest.importorskip("sympy")
    from jacopy.algebra.derivation import Act, compose
    from jacopy.core.properties import Scalar
    from jacopy.oracle.check import check_equal

    reg = PropertyRegistry()
    c = Symbol("c")
    reg.declare(c, Scalar())
    (f,) = functions("f", registry=reg)
    X = vector_fields("X")[0]

    def verdict(lhs, rhs):
        return check_equal(lhs, rhs, registry=reg, owners=[], samples=2).verdict

    assert verdict(compose(X, c), compose(c, X)) == "AGREE"
    assert verdict(Act(X, c), Integer(0)) == "AGREE"
    assert verdict(Act(X, f), Integer(0)) == "DISAGREE"


def test_m1_1_engine_refuses_nonzero_derivative_of_a_scalar():
    # chef decision (d)/(i): a rule D(x) = 1 on a Scalar x is reported,
    # never silently resolved either way
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.core.properties import Scalar, ScalarContractError
    from jacopy.proof import show_equal
    from jacopy.proof.expansion import Definition, ExpansionEngine
    from jacopy.proof.result import prove

    D, x = Derivation("D", degree=0), Symbol("x")

    class DX(Definition):
        name = "D(x)=1"
        anchor = Act

        def matches(self, e):
            return e == Act(D, x)

        def rewrite(self, e):
            return Integer(1)

    bad = PropertyRegistry()
    bad.declare(x, Scalar())
    with pytest.raises(ScalarContractError, match="declared Scalar"):
        prove(ExpansionEngine([DX()]), Act(D, x), Integer(1), registry=bad)
    with pytest.raises(ScalarContractError):
        show_equal(Act(D, x), Integer(1), registry=bad, engine=ExpansionEngine([DX()]))
    good = PropertyRegistry()
    good.declare(x, Graded(0))
    assert prove(ExpansionEngine([DX()]), Act(D, x), Integer(1), registry=good).closed
    # the guard's own registry reads are not hypotheses of the step
    r = prove(ExpansionEngine([DX()]), Act(D, x), Integer(1), registry=good)
    assert not any("Scalar" in a.name for a in r.requires)


def test_m1_1_registry_refuses_contradictory_scalar_declarations():
    from jacopy.core.properties import NonCommuting, Scalar, ScalarContractError
    from jacopy.core.symbolic_degree import Degree

    for first, second in (
        (Scalar(), Graded(1)),
        (Graded(2), Scalar()),
        (Scalar(), NonCommuting()),
        (NonCommuting(), Scalar()),
    ):
        reg = PropertyRegistry()
        x = Symbol("x")
        reg.declare(x, first)
        with pytest.raises(ScalarContractError):
            reg.declare(x, second)
    # consistent: a constant is a degree-0 (constant) function; a
    # symbolic degree is not provably non-zero
    reg = PropertyRegistry()
    reg.declare(Symbol("x"), Scalar())
    reg.declare(Symbol("x"), Graded(0))
    reg.declare(Symbol("y"), Graded(Degree.var("k")))
    reg.declare(Symbol("y"), Scalar())


def test_derived_bracket_skew_sign_comes_from_pair_swap_sign():
    # chef (v): DerivedBracketStrategy._skew_defect reads its sign from
    # bracket.pair_swap_sign — the same value as the former hand-written
    # ((|x|+k)(|y|+k)) parity, k = |Q| + 2|base|
    from jacopy.brackets.derived import DerivedBracket
    from jacopy.algebra.derivation import degree_of

    class _Comm(GradedBracket):
        def __init__(self):
            super().__init__("comm", degree=0)

        def expand(self, a, b, registry=None):
            return a * b - b * a

    reg = PropertyRegistry()
    syms = []
    for d in range(3):
        s = Symbol(f"g{d}")
        reg.declare(s, Graded(d))
        syms.append(s)
    for dq in (0, 1, 2):
        br = DerivedBracket(_Comm(), Symbol("Q"), degree_Q=dq)
        k = br.degree
        for x, y in iproduct(syms, repeat=2):
            old = ((degree_of(x, reg) + k) * (degree_of(y, reg) + k)).parity()
            assert br.pair_swap_sign(x, y, reg) == (-1 if old == 0 else 1)
