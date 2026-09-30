"""Audit 0B00E1B-FULL — algebroid d_E / L^E axiom conditions.

* M2-1 (P0-4): the Palais/Koszul ``d_E`` is an ALTERNATING form only for
  a skew bracket. On a Dorfman-type bracket
  ``(d_E α)(u,u) = ρ(u)α(u) − ρ(u)α(u) − α([u,u]) = −α([u,u])``.
* M2-2 (P0-5): ``L_X(fY) = ρ(X)(f)Y + f L_X Y`` is right Leibniz of the
  bracket; it must not follow from ``L_X`` being a ``Derivation``.

Every test builds the target equality itself; hand calculations are in
the comments.
"""

import itertools

import pytest

from jacopy.algebra.derivation import Act
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.algorithms.simplify import simplify
from jacopy.core.expr import Integer, Neg, Product, Sum
from jacopy.core.multi_eval import MultiEval, admits_alternation
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.expansion import ExpansionEngine
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.central.calculus.bracket_calculus import (
    BracketCalculus,
    IntrinsicLDefinition,
)
from jacopy.central.objects import Bundle, forms, functions, vector_fields
from jacopy.central.objects.interior import Interior
from jacopy.central.algebroid import algebroid, algebroid_engine, d_E, lie_E
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


# --------------------------------------------------------------------- #
# M2-2: L on C^∞-multiples of sections needs right Leibniz               #
# --------------------------------------------------------------------- #


class TestLieDerivativeRightLeibniz:
    def test_zero_bracket_identity_anchor(self):
        # M = ℝ, E = Tℝ, ρ = id, [u,v] := 0 (ℝ-bilinear, NOT right
        # Leibniz). e = ∂x: L_e(x e) = [e, x e] = 0, whereas the product
        # rule would give ρe(x) e + x[e,e] = 1·e ≠ 0.
        reg = PropertyRegistry()
        (x,) = functions("x", registry=reg)
        (e,) = vector_fields("e")
        calc = BracketCalculus(
            "zero-id", anchor=lambda s: s, bracket=lambda a, b: Integer(0)
        )
        eng = ExpansionEngine([IntrinsicLDefinition(calc, reg)])
        lhs = Act(calc.lie(e), Product(x, e))
        assert _prove(lhs, Integer(0), reg, eng).steps
        with pytest.raises(ProofFailure):
            _prove(lhs, Product(Act(e, x), e), reg, eng)

    def test_twice_lie_counter_model(self):
        # ρ = id, [u,v] := 2[u,v]_Lie. By definition
        # L_e(x e2) = 2[e, x e2]_Lie = 2e(x)e2 + 2x[e,e2]; the product rule
        # would give e(x)e2 + 2x[e,e2], short by e(x)e2.
        reg = PropertyRegistry()
        (x,) = functions("x", registry=reg)
        e, e2 = vector_fields("e e2")
        calc = BracketCalculus(
            "twice-lie",
            anchor=lambda s: s,
            bracket=lambda a, b: Product(Integer(2), LieBracketVF(a, b)),
        )
        eng = ExpansionEngine([IntrinsicLDefinition(calc, reg)])
        lhs = Act(calc.lie(e), Product(x, e2))
        wrong = Sum(
            Product(Act(e, x), e2),
            Product(x, Integer(2), LieBracketVF(e, e2)),
        )
        with pytest.raises(ProofFailure):
            _prove(lhs, wrong, reg, eng)
        assert _prove(
            lhs, Product(Integer(2), LieBracketVF(e, Product(x, e2))), reg, eng
        ).steps

    @pytest.mark.parametrize(
        "decl", [(), ("antisymmetric", "jacobi"), ("symmetric-part",)]
    )
    def test_undeclared_right_leibniz_does_not_close(self, decl):
        reg = PropertyRegistry()
        (f,) = functions("f", registry=reg)
        A = algebroid("Anr", Bundle("Anr"), declare=decl)
        u, v = A.sections("u v")
        eng = algebroid_engine(A, registry=reg)
        lhs = Act(lie_E(A, u), Product(f, v))
        with pytest.raises(ProofFailure):
            _prove(
                lhs,
                Sum(Product(Act(A.anchor(u), f), v), Product(f, A.bracket(u, v))),
                reg,
                eng,
            )
        # the definition L_u(f v) = [u, f v] still holds
        assert _prove(lhs, A.bracket(u, Product(f, v)), reg, eng).steps

    @pytest.mark.parametrize("level", ["almost-leibniz", "lie", "leibniz"])
    def test_declared_right_leibniz_closes_with_trace(self, level):
        reg = PropertyRegistry()
        (f,) = functions("f", registry=reg)
        A = algebroid("Arl", Bundle("Arl"), declare=(level,))
        u, v = A.sections("u v")
        chain = _prove(
            Act(lie_E(A, u), Product(f, v)),
            Sum(Product(Act(A.anchor(u), f), v), Product(f, A.bracket(u, v))),
            reg,
            algebroid_engine(A, registry=reg),
        )
        assert any("right-Leibniz" in s.rule for s in chain.steps)

    def test_tangent_product_rule_still_closes(self):
        # E = TM: [X, fY] = X(f)Y + f[X,Y] by construction.
        from jacopy.central.tangent.engine import tangent_engine
        from jacopy.central.tangent.exterior import CARTAN_TM
        from jacopy.central.tangent.lie_bracket import lie_bracket

        reg = PropertyRegistry()
        (f,) = functions("f", registry=reg)
        X, Y = vector_fields("X Y")
        assert CARTAN_TM.right_leibniz and CARTAN_TM.skew
        assert _prove(
            Act(CARTAN_TM.lie(X), Product(f, Y)),
            Sum(Product(Act(X, f), Y), Product(f, lie_bracket(X, Y))),
            reg,
            tangent_engine(registry=reg),
        ).steps
