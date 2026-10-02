"""
Audit 0b00e1b-FULL K1-3 (K1-4, M1X-7), fix/p1-core redesign (Fable,
2026-10-02): the three open gate findings on the Schouten / derived
bracket grading hooks, one locking test each.

7. ``DerivedBracket.degree_Q`` is validated against the registry (a
   contradicting declaration is refused, an undeclared one derived);
8. ``pair_swap_sign`` — the rewrite licence — declines (``None``) on an
   undeterminable or symbolic degree instead of raising;
9. Koszul (``acting_on``) mode is typed: bivector generator, 1-form
   operands; the Leibniz obstruction is refused there.
"""

from __future__ import annotations

import pytest

from jacopy.algebra.derivation import Derivation
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.objects.multivector import PVector
from jacopy.central.tangent.schouten import SN
from jacopy.core.expr import Sum, Symbol
from jacopy.core.properties import Graded
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.proof.strategies import DerivedBracketStrategy, ProofFailure


# --------------------------------------------------------------------- #
# 7. degree_Q validated against the registry                            #
# --------------------------------------------------------------------- #


class _Comm:
    """A graded-Lie commutator base in the operator grading."""

    def __new__(cls):
        from jacopy.brackets.base import GradedBracket

        class C(GradedBracket):
            def __init__(self):
                super().__init__("comm", degree=0, satisfies_graded_jacobi=True)

            def expand(self, a, b, registry=None):
                return a * b - b * a

        return C()


def test_7_derived_degree_q_is_checked_against_the_registry():
    from jacopy.brackets.derived import DerivedBracket

    reg = PropertyRegistry()
    Q = Symbol("Q")
    reg.declare(Q, Graded(1))
    syms = [Symbol(n) for n in "ABC"]
    for s in syms:
        reg.declare(s, Graded(0))
    # declared degree_Q contradicts the registry: refused
    br = DerivedBracket(_Comm(), Q, degree_Q=0)
    with pytest.raises(ValueError, match="degree_Q"):
        br.generator_degree(reg)
    with pytest.raises(ProofFailure, match="degree_Q"):
        DerivedBracketStrategy().prove_jacobi(br, *syms, registry=reg)
    with pytest.raises(ValueError):
        br.claimed_swap_sign(syms[0], syms[1], reg)
    # undeclared: derived from the registry (|Q| = 1, odd — the parity
    # precondition passes and the strategy proceeds to the skew checks)
    br2 = DerivedBracket(_Comm(), Q)
    assert br2.degree_Q.as_int() is None
    assert br2.generator_degree(reg).as_int() == 1
    assert br2.operand_degree(syms[0], reg).as_int() == 1
    assert br2.claimed_swap_sign(syms[0], syms[1], reg) == 1
    # (degree-0 graded-commutative operands: everything commutes, the
    # derived bracket vanishes and the cyclic Jacobi closes honestly)
    assert DerivedBracketStrategy().prove_jacobi(br2, *syms, registry=reg) is not None
    # consistent declaration: fine, and the registry-free answer stands
    br3 = DerivedBracket(_Comm(), Q, degree_Q=1)
    assert br3.generator_degree(reg).as_int() == 1
    assert br3.generator_degree(None).as_int() == 1
    # a Poisson bivector: the base grading is structural
    pi = PVector("pi", degree=2)
    assert DerivedBracket(SN, pi).generator_degree(reg).as_int() == 2


# --------------------------------------------------------------------- #
# 8. pair_swap_sign declines                                            #
# --------------------------------------------------------------------- #


def test_8_pair_swap_sign_never_raises():
    from jacopy.brackets.derived import DerivedBracket

    reg = PropertyRegistry()
    (X,) = vector_fields("X")
    u = Symbol("u")                                   # no multivector degree
    assert SN.pair_swap_sign(u, X, reg) is None
    assert SN.pair_swap_sign(X, u, None) is None
    assert SN.pair_swap_sign(X, X, reg) == -1         # the determinable case still answers
    br = _Comm()
    assert br.pair_swap_sign(Symbol("a"), Symbol("b"), reg) is None
    reg.declare(Symbol("a"), Graded(Degree.var("k")))
    reg.declare(Symbol("b"), Graded(Degree.var("l")))
    assert br.pair_swap_sign(Symbol("a"), Symbol("b"), reg) is None   # symbolic parity
    assert DerivedBracket(SN, PVector("pi", degree=2)).pair_swap_sign(u, X, reg) is None
    with pytest.raises(ValueError):                   # the CLAIM still raises
        SN.claimed_swap_sign(u, X, reg)


# --------------------------------------------------------------------- #
# 9. Koszul mode is typed                                               #
# --------------------------------------------------------------------- #


def test_9_koszul_mode_needs_a_bivector_and_one_forms():
    from jacopy.brackets.base import BracketApply
    from jacopy.brackets.derived import DerivedBracket

    rho = Derivation("π♯", degree=0)
    with pytest.raises(ValueError, match="BIVECTOR"):
        DerivedBracket(SN, PVector("P3", degree=3), acting_on=rho)
    with pytest.raises(ValueError, match="BIVECTOR"):
        DerivedBracket(SN, vector_fields("X")[0], acting_on=rho)
    pi = PVector("pi", degree=2)
    K = DerivedBracket(SN, pi, acting_on=rho)
    reg = PropertyRegistry()
    a, b = forms("alpha beta", degree=1)
    (w,) = forms("w", degree=2)
    (f,) = functions("f", registry=reg)
    assert K.koszul_well_typed(a, b, reg)
    assert isinstance(K.expand(a, b, reg), Sum)                 # the 3-term formula
    for x, y in ((a, w), (w, a), (a, f), (f, b)):
        assert not K.koszul_well_typed(x, y, reg)
        assert K.expand(x, y, reg) == BracketApply(K, x, y)   # ill-typed: inert
    with pytest.raises(ValueError, match="1-forms"):
        K.leibniz_obstruction(a, b, b, reg)
    with pytest.raises(ProofFailure, match="Koszul"):
        DerivedBracketStrategy().prove_jacobi(K, a, b, w, registry=reg)
    # a generator whose degree needs a registry: typed at use, not at init
    Q = Symbol("Q")
    K2 = DerivedBracket(_Comm(), Q, acting_on=rho)
    assert K2.expand(a, b, reg) == BracketApply(K2, a, b)   # |Q| unknown: inert
