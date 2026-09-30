"""Audit 0B00E1B-FULL — algebroid d_E / L^E axiom conditions.

* M2-1 (P0-4): the Palais/Koszul ``d_E`` is an ALTERNATING form only for
  a skew bracket. On a Dorfman-type bracket
  ``(d_E α)(u,u) = ρ(u)α(u) − ρ(u)α(u) − α([u,u]) = −α([u,u])``.
* M2-2 (P0-5): ``L_X(fY) = ρ(X)(f)Y + f L_X Y`` is right Leibniz of the
  bracket; it must not follow from ``L_X`` being a ``Derivation``.
* M2-3 (P1): the one-form ``d_E²`` defect formula needs antisymmetry;
  in general a symmetric-part term survives.

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
import jacopy.central.algebroid.defect_formulas as df


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

    def test_symmetric_part_correction_model(self):
        # E = ℝ² over a point, ρ = 0, only [a,b] = a, μ = a*;
        # u = a, v = b, w = a+b. With ρ = 0 the ordered double Palais
        # is d²μ(u,v,w) = μ([[u,v],w] − [[u,w],v] + [[v,w],u]).
        # [u,v] = a, [u,w] = a, [v,w] = 0 ⇒ d²μ = μ([a,a+b] − [a,b]) = 0.
        # J(u,v,w) = [u,[v,w]] − [[u,v],w] − [v,[u,w]] = 0 − a − 0 = −a,
        # so the skew-only formula gives −μ(J) = 1 ≠ 0 = d²μ, while the
        # corrected −μ(J) + μ(S(u,[v,w]) − S(v,[u,w])) = 1 − 1 = 0.
        table = {(0, 1): (1, 0)}
        br = lambda x, y: _bracket(table, x, y)  # noqa: E731
        add = lambda x, y: (x[0] + y[0], x[1] + y[1])  # noqa: E731
        sub = lambda x, y: (x[0] - y[0], x[1] - y[1])  # noqa: E731
        S = lambda x, y: add(br(x, y), br(y, x))  # noqa: E731
        mu = lambda x: x[0]  # noqa: E731
        u, v = (1, 0), (0, 1)
        w = add(u, v)
        d2 = mu(add(sub(br(br(u, v), w), br(br(u, w), v)), br(br(v, w), u)))
        J = sub(sub(br(u, br(v, w)), br(br(u, v), w)), br(v, br(u, w)))
        old_rhs = -mu(J)
        new_rhs = -mu(J) + mu(sub(S(u, br(v, w)), S(v, br(u, w))))
        assert (d2, old_rhs, new_rhs) == (0, 1, 0)


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


# --------------------------------------------------------------------- #
# M2-3: the one-form d² defect needs antisymmetry                        #
# --------------------------------------------------------------------- #


def _defect_setup(decls):
    reg = PropertyRegistry()
    E = algebroid("Ed3", Bundle("Ed3"), declare=decls)
    u, v, w = E.sections("u v w")
    (mu,) = forms("μ3", degree=1, bundle=E.bundle)
    return reg, E, u, v, w, mu


class TestDSquaredDefectScope:
    def test_skew_formula_fails_bare_and_closes_skew(self):
        reg, E, u, v, w, mu = _defect_setup(())
        with pytest.raises(ProofFailure):
            df.prove_defect_d_squared_on_one_forms(E, mu, u, v, w, registry=reg)
        reg, E, u, v, w, mu = _defect_setup(("antisymmetric",))
        assert df.prove_defect_d_squared_on_one_forms(
            E, mu, u, v, w, registry=reg
        ).steps

    def test_general_formula_closes_bare(self):
        # d²μ(u,v,w) = 𝒫(u,v)μ(w) − 𝒫(u,w)μ(v) + 𝒫(v,w)μ(u)
        #   + μ([[u,v],w] − [[u,w],v] + [[v,w],u]),
        # and the last bracket = −μ(J) + μ(S(u,[v,w]) − S(v,[u,w])).
        reg, E, u, v, w, mu = _defect_setup(())
        assert df.prove_defect_d_squared_on_one_forms_general(
            E, mu, u, v, w, registry=reg
        ).steps

    def test_module_no_longer_claims_any_bracket_for_all(self):
        doc = df.__doc__
        assert "All DECLARATION-FREE" not in doc
        assert "NEEDS ``antisymmetric``" in doc


# --------------------------------------------------------------------- #
# Code-review follow-ups: default-reject alternation (M2-1)             #
# Each case CLOSED / zeroed on c1121c8.                                  #
# --------------------------------------------------------------------- #


class TestAlternationDefaultReject:
    def test_wedge_with_non_alternating_factor(self):
        # leibniz: (d_E m)(u,u) = −m([u,u]) ≠ 0, so d_E m ∧ n is not an
        # alternating 3-form and (dm∧n)(u,u,v) must not collapse to 0;
        # the claim (dm∧n − m∧dn)(u,u,v) = 0 must not close.
        from jacopy.core.wedge import Wedge

        reg = PropertyRegistry()
        C = algebroid("Lw", Bundle("Lw"), declare=("leibniz",))
        u, v = C.sections("u v")
        m, n = forms("m n", degree=1, bundle=C.bundle)
        node = MultiEval(Wedge(d_E(C, m), n), u, u, v)
        assert not node.alternating
        assert simplify(node, reg) != Integer(0)
        lhs = Sum(node, Neg(MultiEval(Wedge(m, d_E(C, n)), u, u, v)))
        with pytest.raises(ProofFailure):
            _prove(lhs, Integer(0), reg, algebroid_engine(C, registry=reg))

    def test_multivector_interior_of_non_skew_d(self):
        # courant: ι_P(d_E μ3)(a,a) = (d_E μ3)(P, a, a) — d_E μ3 is not
        # alternating, so the repeated slot does not force 0.
        from jacopy.central.objects import p_vectors
        from jacopy.central.objects.multivector_interior import (
            MultivectorInterior,
        )

        reg = PropertyRegistry()
        C = algebroid("Cm", Bundle("Cm"), declare=("courant",))
        (a,) = C.sections("a")
        (mu3,) = forms("μ3", degree=3, bundle=C.bundle)
        (P,) = p_vectors("P", degree=2, bundle=C.bundle)
        node = MultiEval(
            Act(MultivectorInterior(P, registry=reg), d_E(C, mu3)), a, a
        )
        assert not node.alternating
        assert simplify(node, reg) != Integer(0)

    def test_tilde_interior_of_non_skew_d(self):
        # a non-skew calculus (e.g. the p ≥ 2 Nambu–Koszul bracket):
        # ι̃_β(dR)(γ,γ) must not collapse to 0.
        from jacopy.central.objects import p_vectors
        from jacopy.central.objects.tilde_interior import TildeInterior
        from jacopy.central.tangent.lie_bracket import lie_bracket

        reg = PropertyRegistry()
        calc = BracketCalculus(
            "nsk", anchor=lambda s: s, bracket=lie_bracket
        )
        (R,) = p_vectors("R", degree=3)
        be, ga = forms("β γ", degree=1)
        node = MultiEval(
            Act(TildeInterior(be), Act(calc.d, R)), ga, ga,
            slot_kind="covector",
        )
        assert not node.alternating
        assert simplify(node, reg) != Integer(0)

    def test_tensor_inner_evaluation_never_upgraded(self):
        # (dT)(X,X,W) for a (0,2)-tensor T (Palais, any bracket) contains
        # +ρ(W)(T(X,X)); T is not alternating, so T(X,X) must stay.
        from jacopy.central.objects import tensors
        from jacopy.central.calculus.bracket_calculus import (
            IntrinsicDDefinition,
        )
        from jacopy.central.tangent.lie_bracket import lie_bracket

        reg = PropertyRegistry()
        calc = BracketCalculus(
            "nsk2", anchor=lambda s: s, bracket=lie_bracket
        )
        (T,) = tensors("T", upper=0, lower=2)
        X, W = vector_fields("X W")
        node = MultiEval(Act(calc.d, T), X, X, W, alternating=False)
        out = IntrinsicDDefinition(calc, reg).rewrite(node)
        target = Act(W, MultiEval(T, X, X, alternating=False))
        assert target in out.children
        assert not admits_alternation(T)

    def test_d_identity_carries_skewness(self):
        from jacopy.central.calculus.bracket_calculus import (
            ExteriorDerivative,
        )
        from jacopy.central.tangent.lie_bracket import lie_bracket

        mk = lambda sk: BracketCalculus(  # noqa: E731
            "K", anchor=lambda s: s, bracket=lie_bracket, skew=sk
        ).d
        assert mk(True) != mk(False)
        assert hash(mk(True)) != hash(mk(False))
        assert ExteriorDerivative("K").alternating_values is False


# --------------------------------------------------------------------- #
# Code-review follow-ups: section-valued L arguments (M2-2)             #
# Each case CLOSED on c1121c8.                                           #
# --------------------------------------------------------------------- #


def _rl(A, u, f, s):
    """The right-Leibniz shape ρ(u)(f)·s + f·[u, s]."""
    return Sum(Product(Act(A.anchor(u), f), s), Product(f, A.bracket(u, s)))


class TestSectionValuedLieArguments:
    def _bare(self, decl=()):
        reg = PropertyRegistry()
        (f,) = functions("f", registry=reg)
        A = algebroid("Asv", Bundle("Asv"), declare=decl)
        u, v, w = A.sections("u v w")
        return reg, f, A, u, v, w, algebroid_engine(A, registry=reg)

    def test_bare_does_not_close(self):
        # Bare bracket: L_u(X) = [u, X] with [u, fX] opaque, so none of
        # the right-Leibniz consequences below may close.
        reg, f, A, u, v, w, eng = self._bare()
        L = lie_E(A, u)
        cases = [
            (Act(L, Product(f, Sum(u, v))), _rl(A, u, f, Sum(u, v))),
            (
                Act(L, Sum(Product(f, v), w)),
                Sum(_rl(A, u, f, v), A.bracket(u, w)),
            ),
            (Act(L, Neg(Product(f, v))), Neg(_rl(A, u, f, v))),
        ]
        for lhs, rhs in cases:
            with pytest.raises(ProofFailure):
                _prove(lhs, rhs, reg, eng)

    def test_declared_right_leibniz_closes(self):
        reg, f, A, u, v, w, eng = self._bare(("almost-leibniz",))
        L = lie_E(A, u)
        assert _prove(
            Act(L, Sum(Product(f, v), w)),
            Sum(_rl(A, u, f, v), A.bracket(u, w)),
            reg,
            eng,
        ).steps
        assert _prove(
            Act(L, Neg(Product(f, v))), Neg(_rl(A, u, f, v)), reg, eng
        ).steps

    def test_splits_over_product_protocol(self):
        # The product-rule hook: refused on f·v without right Leibniz,
        # allowed on f·α (a form: holds for any bracket) and on TM.
        from jacopy.central.tangent.exterior import CARTAN_TM

        reg, f, A, u, v, w, eng = self._bare()
        (al,) = forms("α", degree=1, bundle=A.bundle)
        L = lie_E(A, u)
        assert L.splits_over_product(Product(f, v), reg) is False
        assert L.splits_over_product(Product(f, al), reg) is True
        X, Y = vector_fields("X Y")
        assert CARTAN_TM.lie(X).splits_over_product(Product(f, Y), reg)
        # the protocol survives the slot rewrite
        assert L.with_slots(v).splits_over_product(Product(f, v), reg) is False


# --------------------------------------------------------------------- #
# Code-review follow-up: general d²μ under declarations (M2-3)          #
# --------------------------------------------------------------------- #


class TestGeneralDSquaredUnderDeclarations:
    @pytest.mark.parametrize(
        "decl", [("leibniz",), ("courant",), ("almost-courant",), ("lie",)]
    )
    def test_closes(self, decl):
        # The identity uses no axiom; a declared J → 0 used to fire on
        # one side only (ProofFailure on c1121c8 for leibniz/courant).
        reg, E, u, v, w, mu = _defect_setup(decl)
        assert df.prove_defect_d_squared_on_one_forms_general(
            E, mu, u, v, w, registry=reg
        ).steps


# --------------------------------------------------------------------- #
# M7-1 root: indexed-sum linearity must preserve factor order           #
# --------------------------------------------------------------------- #


class TestIndexedSumLinearityOrder:
    def _setup(self):
        from jacopy.core.indexed_sum import IndexedSum
        from jacopy.central.objects.frame import Frame, FrameIndex

        reg = PropertyRegistry()
        g, f0, h = functions("g f0 h", registry=reg)
        E = algebroid("Eix", Bundle("Eix"), declare=("lie",))
        v, w = E.sections("v w")
        fr = Frame("e", bundle=E.bundle)
        s = FrameIndex("s")
        c_s = Pairing(fr.dual().field("s"), v)
        return reg, g, f0, h, E, v, w, fr, s, c_s, IndexedSum

    def test_middle_operator_not_pulled(self):
        # Operator composition: (Σ_s ⟨e^s,v⟩·ρ(w)·ρ(e_s)(f0))(g)
        #   = Σ_s ⟨e^s,v⟩ · ρ(w)(ρ(e_s)(f0)·g);
        # pulling ρ(w) out gives ρ(w)(Σ_s ⟨e^s,v⟩ρ(e_s)(f0)·g), which
        # has the extra Σ_s ρ(w)(⟨e^s,v⟩)·ρ(e_s)(f0)·g. PROVED on the
        # previous rule; must not close.
        from jacopy.packages.metric_affine.torsion_curvature import _engine

        reg, g, f0, h, E, v, w, fr, s, c_s, IS = self._setup()
        B = Act(E.anchor(fr.field("s")), f0)
        lhs = Act(IS(s, fr, Product(c_s, E.anchor(w), B)), g)
        pulled = Act(Product(E.anchor(w), IS(s, fr, Product(c_s, B))), g)
        with pytest.raises(ProofFailure):
            _prove(lhs, pulled, reg, _engine(reg))

    def test_prefix_suffix_order_and_scalar_middle(self):
        from jacopy.central.calculus.indexed_rules import (
            IndexedSumLinearityDefinition as R,
        )

        reg, g, f0, h, E, v, w, fr, s, c_s, IS = self._setup()
        rule = R(reg)
        # free prefix ρ(w) stays left, free suffix h stays right
        x = IS(s, fr, Product(E.anchor(w), c_s, h))
        assert rule.rewrite(x) == Product(E.anchor(w), IS(s, fr, c_s), h)
        # a scalar middle factor may pass scalar factors only
        B = Act(E.anchor(fr.field("s")), g)
        y = IS(s, fr, Product(c_s, f0, B))
        assert rule.rewrite(y) == Product(f0, IS(s, fr, Product(c_s, B)))
        # an operator middle factor: nothing to pull
        z = IS(s, fr, Product(c_s, E.anchor(w), B))
        assert not rule.matches(z)
