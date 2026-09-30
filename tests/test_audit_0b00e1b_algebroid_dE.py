"""Audit 0B00E1B-FULL — algebroid d_E / L^E axiom conditions.

* M2-1 (P0-4): the Palais/Koszul ``d_E`` is an ALTERNATING form only for
  a skew bracket. On a Dorfman-type bracket
  ``(d_E α)(u,u) = ρ(u)α(u) − ρ(u)α(u) − α([u,u]) = −α([u,u])``.

Every test builds the target equality itself; hand calculations are in
the comments.
"""

import itertools

import pytest

from jacopy.algebra.derivation import Act
from jacopy.algorithms.simplify import simplify
from jacopy.core.expr import Integer, Neg, Sum
from jacopy.core.multi_eval import MultiEval, admits_alternation
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.central.objects import Bundle, forms
from jacopy.central.objects.interior import Interior
from jacopy.central.algebroid import algebroid, algebroid_engine, d_E
from jacopy.central.algebroid.calculus import algebroid_calculus, evaluate


def _prove(lhs, rhs, reg, eng=None):
    return ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng)


# --------------------------------------------------------------------- #
# Concrete finite-dimensional models (numbers, no engine)                #
# --------------------------------------------------------------------- #


def _bracket(table, x, y):
    """ℝ-bilinear bracket on ℝ² from its values on the basis."""
    out = [0, 0]
    for i, j in itertools.product(range(2), repeat=2):
        c = x[i] * y[j]
        if c:
            for k in range(2):
                out[k] += c * table.get((i, j), (0, 0))[k]
    return tuple(out)


def _palais_zero_anchor(alpha, table, u, v):
    """ρ = 0 (a point base): (d_E α)(u,v) = −α([u,v])."""
    b = _bracket(table, u, v)
    return -(alpha[0] * b[0] + alpha[1] * b[1])


class TestConcreteModels:
    def test_leibniz_model_diagonal_is_minus_one(self):
        # E = ℝ² over a point, ρ = 0, only [e1,e1] = e2, α = e².
        # All iterated brackets vanish ([e2,·] = [·,e2] = 0), so
        # Leibniz–Jacobi holds; right Leibniz is trivial (constant
        # functions). (d_E α)(e1,e1) = −α([e1,e1]) = −α(e2) = −1 ≠ 0:
        # alternation of d_E is FALSE on this Leibniz algebroid.
        table = {(0, 0): (0, 1)}
        e1, alpha = (1, 0), (0, 1)
        assert _palais_zero_anchor(alpha, table, e1, e1) == -1


# --------------------------------------------------------------------- #
# M2-1: d_E is alternating only for a skew bracket                       #
# --------------------------------------------------------------------- #

NON_SKEW = ("leibniz", "almost-courant", "courant")


def _alg(level, name):
    reg = PropertyRegistry()
    C = algebroid(name, Bundle(name), declare=(level,))
    u, v = C.sections("u v")
    (m,) = forms("m", degree=1, bundle=C.bundle)
    return reg, C, u, v, m


class TestDEAlternation:
    @pytest.mark.parametrize("level", NON_SKEW)
    def test_non_skew_level_keeps_minus_m_uu(self, level):
        reg, C, u, v, m = _alg(level, "N" + level.replace("-", ""))
        eng = algebroid_engine(C, registry=reg)
        assert not algebroid_calculus(C).skew
        # Even when an alternating evaluation is REQUESTED, the node is
        # normalized to a plain multilinear one: simplify must not kill
        # it, and the target d(m)(u,u) = −m([u,u]) closes while
        # d(m)(u,u) = 0 does not (default and algebroid engines).
        node = MultiEval(d_E(C, m), u, u, alternating=True)
        assert node.alternating is False
        assert simplify(node, reg) != Integer(0)
        target = Neg(Pairing(m, C.bracket(u, u)))
        assert _prove(node, target, reg, eng).steps
        for engine in (None, eng):
            with pytest.raises(ProofFailure):
                _prove(node, Integer(0), reg, engine)

    def test_leibniz_swap_is_symmetric_part(self):
        # Ordered Palais: dm(u,v) + dm(v,u) = −m([u,v] + [v,u]) — the
        # symmetric part, not 0.
        reg, C, u, v, m = _alg("leibniz", "Lsw")
        eng = algebroid_engine(C, registry=reg)
        lhs = Sum(evaluate(d_E(C, m), u, v), evaluate(d_E(C, m), v, u))
        rhs = Neg(Pairing(m, Sum(C.bracket(u, v), C.bracket(v, u))))
        assert _prove(lhs, rhs, reg, eng).steps
        with pytest.raises(ProofFailure):
            _prove(lhs, Integer(0), reg, eng)

    def test_interior_source_agrees_with_palais(self):
        # ⟨ι_u d_E m, u⟩ = (d_E m)(u,u) (first-slot insertion) = −m([u,u]);
        # simplify-first and expand-first must agree (no alternation).
        reg, C, u, v, m = _alg("leibniz", "Lint")
        eng = algebroid_engine(C, registry=reg)
        node = Pairing(Act(Interior(u), d_E(C, m)), u)
        assert simplify(node, reg) != Integer(0)
        target = Neg(Pairing(m, C.bracket(u, u)))
        assert _prove(node, target, reg, eng).steps
        assert _prove(simplify(node, reg), target, reg, eng).steps

    def test_lie_level_still_alternating(self):
        # Skew bracket: dm(u,u) = −m([u,u]) = 0 and dm(v,u) = −dm(u,v).
        reg, C, u, v, m = _alg("lie", "Lok")
        eng = algebroid_engine(C, registry=reg)
        assert algebroid_calculus(C).skew
        assert admits_alternation(d_E(C, m))
        assert evaluate(d_E(C, m), u, u).alternating
        assert _prove(evaluate(d_E(C, m), u, u), Integer(0), reg, eng).steps
        assert _prove(
            evaluate(d_E(C, m), v, u), Neg(evaluate(d_E(C, m), u, v)), reg, eng
        ).steps

    def test_cartan_magic_one_forms_survives_on_courant(self):
        # ⟨ι_u dα, v⟩ + ⟨dι_uα, v⟩ = ρuα(v) − ρvα(u) − α[u,v] + ρvα(u)
        # = ρuα(v) − α[u,v] = ⟨L_uα, v⟩ for ANY bracket (ordered).
        from jacopy.central.algebroid.calculus import (
            prove_cartan_magic_on_one_forms,
        )

        reg, C, u, v, m = _alg("courant", "Cmag")
        assert prove_cartan_magic_on_one_forms(C, u, m, v, registry=reg).steps
