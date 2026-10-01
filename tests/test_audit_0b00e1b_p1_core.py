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


def test_m1_1_a_constant_commutes_even_with_a_noncommuting_operator():
    # chef contract correction: Scalar = ℝ-constant, which commutes with
    # every ℝ-linear operator — NonCommuting included (main's behaviour,
    # now under the exact-Scalar definition)
    from jacopy.algebra.derivation import compose
    from jacopy.algorithms.sort_product import sort_product
    from jacopy.core.properties import NonCommuting
    from jacopy.proof import show_equal

    reg, D, x, c, f = _scalar_world()  # D NonCommuting, x and c Scalar
    show_equal(compose(D, x), compose(x, D), registry=reg)
    assert simplify(Sum(Product(D, c), Neg(Product(c, D))), reg) == Integer(0)
    assert sort_product(Product(D, Integer(2)), reg)[0] == Product(Integer(2), D)
    # a FUNCTION does not commute with the NonCommuting operator
    with pytest.raises(ProofFailure):
        show_equal(compose(D, f), compose(f, D), registry=reg)
    assert sort_product(Product(D, f), reg)[0] == Product(D, f)
    # a class-level NonCommuting does not stop a constant either
    E = vector_fields("E")[0]
    reg.declare_for_class(type(E), NonCommuting())
    assert sort_product(Product(E, c), reg)[0] == Product(c, E)
    # a class-level Scalar is a constant too (one contract): it jumps
    # operators, and the sort key agrees with the swap
    reg2 = PropertyRegistry()
    from jacopy.core.properties import Scalar

    reg2.declare_for_class(Symbol, Scalar())
    z = Symbol("z")
    assert sort_product(Product(E, z), reg2)[0] == Product(z, E)


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
    # review: one constant generator does not sink the proof — it is
    # left out of the certificate, the function generator carries it
    t = Symbol("t")

    class Alg2:
        generators = (y, t)

    reg.declare(t, Scalar())
    chain = prove_operator_equation(Product(Integer(2), E), Sum(E, E), Alg2(), registry=reg, engine=eng)
    top = list(chain)[0]
    assert "omitted" in top.justification and len(top.children) == 1
    # the wrong Euler identity still fails on the function generator
    with pytest.raises(ProofFailure):
        prove_operator_equation(compose(E, y), Product(Integer(2), y, E), Alg2(), registry=reg, engine=eng)


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


def test_m1_1_engine_applies_the_scalar_contract_before_any_rule():
    # chef decision (review): D(c) = 0 is a recorded contract step that
    # precedes every rule — a contradictory user rule D(x) = 1 on a
    # Scalar x is never used (no crash, no silent use of either value)
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.core.properties import Scalar
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
    assert not prove(ExpansionEngine([DX()]), Act(D, x), Integer(1), registry=bad).closed
    r = prove(ExpansionEngine([DX()]), Act(D, x), Integer(0), registry=bad)
    assert r.closed
    assert [s.rule for s in r.chain.steps][0].startswith("Scalar contract")
    assert any(a.kind == "registry" and "Scalar" in a.name for a in r.requires)
    good = PropertyRegistry()
    good.declare(x, Graded(0))
    r = prove(ExpansionEngine([DX()]), Act(D, x), Integer(1), registry=good)
    assert r.closed and not any("Scalar" in a.name for a in r.requires)


def test_m1_1_poisson_hamiltonian_on_a_scalar_does_not_crash():
    # review regression: X_f(c) → {f, c} was refused by the earlier
    # guard and killed the whole portfolio
    from jacopy.algebra.derivation import Act
    from jacopy.core.properties import Scalar
    from jacopy.packages.poisson.core import poisson_engine, poisson_structure
    from jacopy.proof import show_equal
    from jacopy.proof.result import prove

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    c = Symbol("c")
    reg.declare(c, Scalar())
    P = poisson_structure("π", declare=("poisson",))
    eng = poisson_engine(registry=reg, structures=(P,), declare_sn=False)
    assert prove(eng, Act(P.hamiltonian(f), c), Integer(0), registry=reg).closed
    show_equal(Act(P.hamiltonian(f), c), Integer(0), registry=reg, engine=eng)


def test_m1_1_scalar_at_any_level_is_a_constant():
    # chef decision A/B: ONE meaning — Scalar declared exactly, per class
    # or per predicate is an ℝ-constant; contradictions are refused at
    # every level by the effective answers
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.algorithms.product_rule import product_rule
    from jacopy.central.calculus.scalars import is_real_constant
    from jacopy.core.properties import Scalar, ScalarContractError

    D = Derivation("D", degree=1)
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    with pytest.raises(ScalarContractError):      # deliberate contract change
        reg.declare(Symbol("w"), Graded(1))
    z = Symbol("z")
    assert is_real_constant(z, reg)
    assert product_rule(Act(D, z), reg) == Integer(0)
    reg = PropertyRegistry()
    reg.declare(Symbol("w"), Graded(1))
    with pytest.raises(ScalarContractError):
        reg.declare_for_class(Symbol, Scalar())
    with pytest.raises(ScalarContractError):
        reg.declare_for_predicate(lambda e: isinstance(e, Symbol), Scalar())
    reg = PropertyRegistry()
    reg.declare_for_predicate(lambda e: isinstance(e, Symbol), Scalar())
    with pytest.raises(ScalarContractError):
        reg.declare(Symbol("w"), Graded(1))
    assert is_real_constant(Symbol("q"), reg)
    # a Scalar on a composite is not a constant atom
    c = Symbol("c")
    assert not is_real_constant(Product(c, c), reg)


def test_m1_1_leibniz_proofs_do_not_accumulate_scalar_reads():
    # review: the D(c) = 0 check queried Scalar on every Act and piled up
    # "x is not Scalar" requirements (X(Y(fg)) facts 4 → 10)
    from jacopy.algebra.derivation import Act
    from jacopy.algorithms.product_rule import product_rule
    from jacopy.core.properties import Scalar
    from jacopy.core.registry import track_reads

    reg, X, Y, Z, W, f, eng = _tm()
    (g,) = functions("g", registry=reg)
    expr = Act(X, Act(Y, Product(f, g)))
    with track_reads() as log:
        product_rule(expr, reg)
    import sys

    pr = sys.modules["jacopy.algorithms.product_rule"]

    saved = pr._annihilates
    pr._annihilates = lambda op, arg, registry: False  # contract check off
    try:
        with track_reads() as base:
            product_rule(expr, reg)
    finally:
        pr._annihilates = saved
    # the contract check adds no (negative) Scalar reads of its own
    assert len(log) == len(base)
    c = Symbol("c")
    reg.declare(c, Scalar())
    with track_reads() as log:
        assert simplify(product_rule(Act(X, Product(c, f)), reg), reg) == Product(c, Act(X, f))
    assert {r[0] for r in log if r[1] is Scalar and r[2] is not None} == {c}


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
            assert br.claimed_swap_sign(x, y, reg) == (-1 if old == 0 else 1)
            assert br.pair_swap_sign(x, y, reg) is None  # not asserted skew: decline


def test_prove_jacobi_terminates_on_inert_sn_nodes():
    # [X∧Y, f] expands to a Product (X·Y(f) − X(f)·Y) whose SN bracket
    # with X stays inert; _expand_all_brackets re-walked the unchanged
    # node forever (RecursionError). Now: an honest verdict.
    from jacopy.proof.verifier import _expand_all_brackets, prove_jacobi

    reg, X, Y, Z, W, f, eng = _tm()
    inert = SN(X, Product(f, Y))
    assert SN.expand(X, Product(f, Y), reg) == inert
    assert _expand_all_brackets(inert, reg) == inert
    with pytest.raises(ProofFailure):  # incompleteness, no longer a crash
        prove_jacobi(SN, X, Wedge(X, Y), f, registry=reg, engine=eng)


def test_pair_swap_sign_declines_on_a_bracket_not_asserted_skew():
    class _NotSkew(GradedBracket):
        def __init__(self):
            super().__init__("ns", degree=0, is_graded_antisymmetric=False)

        def expand(self, a, b, registry=None):
            return BracketApply(self, a, b)

    reg = PropertyRegistry()
    a = Symbol("a")
    reg.declare(a, Graded(0))
    br = _NotSkew()
    assert br.pair_swap_sign(a, a, reg) is None          # no rewrite licence
    assert br.claimed_swap_sign(a, a, reg) == -1         # the claim itself
    assert br.graded_antisymmetry_obstruction(a, a, reg) == Sum(br(a, a), br(a, a))


def test_derived_bracket_grades_like_its_base():
    # {a, b}_π = [[a, π]_SN, b]_SN on the multivector module: shift
    # |π| + 2·(−1) = 0, so on functions the claimed sign is −1 — the
    # Poisson bracket of functions is antisymmetric (oracle). The old
    # recorded degree (|π| + 2·0 with operator degrees) was not the
    # base's grading.
    from jacopy.brackets.derived import DerivedBracket
    from jacopy.proof.strategies import DerivedBracketStrategy

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    pi = PVector("pi", degree=2)
    with pytest.raises(ValueError, match="base bracket's grading"):
        DerivedBracket(SN, pi, degree_Q=1)
    br = DerivedBracket(SN, pi, degree_Q=2)
    assert br.grading_degree(f, reg).as_int() == 0
    assert br.operand_shift.as_int() == 0
    assert br.claimed_swap_sign(f, g, reg) == -1
    assert br.module_product(f, g) == Wedge(f, g)
    pytest.importorskip("sympy")
    from jacopy.oracle.check import check_equal

    skew = Sum(br.expand(f, g, reg), br.expand(g, f, reg))
    sym = Sum(br.expand(f, g, reg), Neg(br.expand(g, f, reg)))
    assert check_equal(skew, Integer(0), registry=reg, owners=[]).verdict == "AGREE"
    assert check_equal(sym, Integer(0), registry=reg, owners=[]).verdict == "DISAGREE"
    # the strategy's odd-generator test reads the same shift: |π| − 1 odd
    try:
        DerivedBracketStrategy().prove_jacobi(br, f, g, Symbol("h"), registry=reg)
    except ProofFailure as exc:
        assert "must be ODD" not in str(exc)
    except ValueError:
        pass


def test_inert_bracket_is_retried_after_its_operands_expand():
    from jacopy.proof.verifier import _expand_all_brackets

    u = Symbol("u")

    class _Outer(GradedBracket):
        def __init__(self):
            super().__init__("outer", degree=0)

        def expand(self, a, b, registry=None):
            # supported only once the left operand is the atom u
            return Integer(1) if a == u else BracketApply(self, a, b)

    class _Inner(GradedBracket):
        def __init__(self):
            super().__init__("inner", degree=0)

        def expand(self, a, b, registry=None):
            return u

    O, I = _Outer(), _Inner()
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")
    assert _expand_all_brackets(O(I(p, q), r), None) == Integer(1)
    assert _expand_all_brackets(O(p, r), None) == O(p, r)  # stays inert, terminates


def test_m1_1_registry_check_uses_the_effective_answers():
    # review: an exact declaration overrides a class-level one of the
    # same type — main accepted this, and it is consistent
    from jacopy.core.properties import Scalar, ScalarContractError

    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Graded(1))
    c = Symbol("c")
    reg.declare(c, Graded(0))
    reg.declare(c, Scalar())
    reg2 = PropertyRegistry()
    d = Symbol("d")
    reg2.declare(d, Graded(0))
    reg2.declare(d, Scalar())
    reg2.declare_for_class(Symbol, Graded(1))  # d's exact Graded(0) wins
    with pytest.raises(ScalarContractError):
        reg2.declare(Symbol("e"), Scalar())     # effective Graded(1)


def test_derived_bracket_derives_degree_q_and_grades_koszul_mode():
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.brackets.derived import DerivedBracket, derived_bracket
    from jacopy.central.objects import forms

    pi = PVector("pi", degree=2)
    assert DerivedBracket(SN, pi).degree_Q.as_int() == 2       # derived, no error
    assert derived_bracket(SN, pi).degree_Q.as_int() == 2
    assert DerivedBracket(SN, pi, degree_Q=2).degree_Q.as_int() == 2
    with pytest.raises(ValueError):
        DerivedBracket(SN, pi, degree_Q=1)                        # explicit contradiction
    K = DerivedBracket(SN, pi, acting_on=Derivation("π♯", degree=0))
    reg = PropertyRegistry()
    a, b, c = forms("alpha beta gamma", degree=1)
    # Koszul bracket on Ω(M): form grading, degree −1 → s = 0 on 1-forms
    assert K.operand_shift.as_int() == -1
    assert K.claimed_swap_sign(a, b, reg) == -1
    assert [K.jacobi_term_sign(*t, reg) for t in ((a, b, c), (b, c, a), (c, a, b))] == [1, 1, 1]
    assert K.module_product(a, b) == Wedge(a, b)


def test_koszul_signs_agree_with_the_model_oracle():
    pytest.importorskip("sympy")
    from jacopy.algebra.derivation import Derivation, Act
    from jacopy.brackets.derived import DerivedBracket
    from jacopy.central.objects import forms
    from jacopy.central.tangent.exterior import CARTAN_TM, d
    from jacopy.core.pairing import Pairing
    from jacopy.oracle.check import check_equal
    from jacopy.packages.poisson.core import SharpVF, poisson_structure

    P = poisson_structure("π", declare=("poisson",))
    pi = P.pi
    K = DerivedBracket(SN, pi, acting_on=Derivation("π♯", degree=0))
    reg = PropertyRegistry()
    a, b, c = forms("alpha beta gamma", degree=1)

    def kz(x, y):  # the formula K emits, the anchor realised as π♯
        rx, ry = SharpVF(pi, x), SharpVF(pi, y)
        return Sum(Act(CARTAN_TM.lie(rx), y), Neg(Act(CARTAN_TM.lie(ry), x)), Neg(d(Pairing(y, rx))))

    def verdict(e):
        return check_equal(e, Integer(0), registry=reg, owners=[P]).verdict

    eps = K.claimed_swap_sign(a, b, reg)
    assert verdict(Sum(kz(a, b), kz(b, a) if eps == -1 else Neg(kz(b, a)))) == "AGREE"
    assert verdict(Sum(kz(a, b), Neg(kz(b, a)) if eps == -1 else kz(b, a))) == "DISAGREE"
    terms = (kz(a, kz(b, c)), kz(b, kz(c, a)), kz(c, kz(a, b)))
    signs = [K.jacobi_term_sign(*t, reg) for t in ((a, b, c), (b, c, a), (c, a, b))]
    assert verdict(Sum(*[t if s == 1 else Neg(t) for t, s in zip(terms, signs)])) == "AGREE"


def test_derived_strategy_message_names_the_base_shift():
    from jacopy.brackets.derived import DerivedBracket
    from jacopy.proof.strategies import DerivedBracketStrategy

    class _Comm(GradedBracket):
        def __init__(self):
            super().__init__("comm", degree=0)

        def expand(self, a, b, registry=None):
            return a * b - b * a

    reg = PropertyRegistry()
    syms = [Symbol(n) for n in "ABC"]
    for x in syms:
        reg.declare(x, Graded(0))
    br = DerivedBracket(_Comm(), Symbol("Q"), degree_Q=0)
    with pytest.raises(ProofFailure, match="k_base = 0"):
        DerivedBracketStrategy().prove_jacobi(br, *syms, registry=reg)


def test_oracle_models_scalars_at_any_level_as_constants():
    pytest.importorskip("sympy")
    from jacopy.algebra.derivation import Act
    from jacopy.central.objects import forms
    from jacopy.core.properties import Scalar
    from jacopy.oracle.check import check_equal

    X = vector_fields("X")[0]
    reg = PropertyRegistry()
    reg.declare_for_class(Symbol, Scalar())
    z = Symbol("z")
    assert check_equal(Act(X, z), Integer(0), registry=reg, owners=[]).verdict == "AGREE"
    (h,) = forms("h", degree=0)
    reg.declare(h, Scalar())
    assert check_equal(Act(X, h), Integer(0), registry=reg, owners=[]).verdict == "AGREE"
    (k,) = forms("k", degree=0)
    assert check_equal(Act(X, k), Integer(0), registry=reg, owners=[]).verdict == "DISAGREE"


def test_scalar_facts_travel_with_citations():
    # chef decision C — probe 1: D(x) = 0 proved with x Scalar must not
    # be citable where x is a function; probe 2: an operator identity
    # proved by dropping a "constant" generator c must not be citable
    # where c is a function
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.core.properties import Scalar
    from jacopy.proof.expansion import ExpansionEngine
    from jacopy.proof.result import prove
    from jacopy.proof.theorems import Theorem, check_citation, TheoremDefinition
    from jacopy.proof.verifier import prove_operator_equation

    D, x = Derivation("D", degree=0), Symbol("x")
    src = PropertyRegistry()
    src.declare(x, Scalar())
    tgt = PropertyRegistry()
    tgt.declare(x, Graded(0))
    r = prove(ExpansionEngine(), Act(D, x), Integer(0), registry=src)
    assert r.closed
    thm = Theorem("dx0", "D(x) = 0", Act(D, x), Integer(0), r.chain).with_structural_requires()
    eng = ExpansionEngine([TheoremDefinition(thm)])
    assert not check_citation(thm, eng, registry=tgt).ok
    assert prove(eng, Act(D, x), Integer(0), registry=tgt).status == "RESIDUAL"
    assert check_citation(thm, eng, registry=src).ok

    # probe 2: D1, D2 agree on f (both 0) — c is dropped as a constant
    D1, D2 = Derivation("D1", degree=0), Derivation("D2", degree=0)
    f, c = Symbol("f"), Symbol("c")

    class Alg:
        generators = (f, c)

    from jacopy.proof.expansion import Definition

    class Kill(Definition):
        name = "D1(f)=D2(f)=0"
        anchor = Act

        def matches(self, e):
            return isinstance(e, Act) and e.op in (D1, D2) and e.arg == f

        def rewrite(self, e):
            return Integer(0)

    src = PropertyRegistry()
    src.declare(f, Graded(0))
    src.declare(c, Scalar())
    chain = prove_operator_equation(D1, D2, Alg(), registry=src, engine=ExpansionEngine([Kill()]))
    thm2 = Theorem("d1d2", "D1 = D2", D1, D2, chain).with_structural_requires()
    assert any(fct.expr == c and fct.prop_cls is Scalar for fct in thm2.registry_facts)
    tgt = PropertyRegistry()
    tgt.declare(f, Graded(0))
    tgt.declare(c, Graded(0))
    eng2 = ExpansionEngine([Kill(), TheoremDefinition(thm2)])
    assert not check_citation(thm2, eng2, registry=tgt).ok
    assert check_citation(thm2, eng2, registry=src).ok


def test_derived_bracket_degree_and_undeterminable_generator():
    # chef decision D/E
    from jacopy.algebra.derivation import Derivation, degree_of
    from jacopy.brackets.derived import DerivedBracket
    from jacopy.central.objects import forms
    from jacopy.proof.strategies import DerivedBracketStrategy

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    pi = PVector("pi", degree=2)
    P = DerivedBracket(SN, pi)
    assert P.degree.as_int() == 0 and degree_of(P(f, g), reg).as_int() == 0
    K = DerivedBracket(SN, pi, acting_on=Derivation("π♯", degree=0))
    a, b = forms("alpha beta", degree=1)
    assert K.degree.as_int() == -1 and degree_of(K(a, b), reg).as_int() == 1
    # Q's degree needs a registry: symbolic, never a silent 0
    Q = Symbol("Q")

    class _Comm(GradedBracket):
        def __init__(self):
            super().__init__("comm", degree=0, satisfies_graded_jacobi=True)

        def expand(self, a, b, registry=None):
            return a * b - b * a

    br = DerivedBracket(_Comm(), Q)
    assert br.degree_Q.as_int() is None
    syms = [Symbol(n) for n in "ABC"]
    for s_ in syms:
        reg.declare(s_, Graded(0))
    with pytest.raises(ProofFailure, match="must be ODD"):
        DerivedBracketStrategy().prove_jacobi(br, *syms, registry=reg)
