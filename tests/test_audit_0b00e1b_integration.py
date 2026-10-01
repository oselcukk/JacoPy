"""Audit 0B00E1B-FULL — cross-branch integration (core product rule ×
algebroid d_E/L × metric_affine).

* P0-5 (M2-2) end to end: the generic product-rule pass consults
  ``op.splits_over_product(arg, registry)``; the algebroid
  ``LieDerivative`` (calculus ``right_leibniz=False``) answers False on
  section-valued products, so ``L_u(f·v) = ρ(u)(f)v + f L_u v`` closes
  only from a declared (or cited, derived) right-Leibniz rule — with
  ``engine=None``, ``algebroid_engine`` and every engine that carries
  :class:`ActExpansionDefinition` (the slot-reachable product rule).

Every test builds the target equality itself; hand calculations are in
the comments. "Before" = main at 4b4ee76 / audit base 0b00e1b.
"""

import pytest

from jacopy.algebra.derivation import Act
from jacopy.algorithms.product_rule import product_rule
from jacopy.core.expr import Integer, Product, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.expansion import ExpansionEngine
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.central.calculus.bracket_calculus import (
    ActExpansionDefinition,
    BracketCalculus,
    IntrinsicLDefinition,
)
from jacopy.central.objects import Bundle, functions, p_vectors, vector_fields
from jacopy.central.algebroid import algebroid, algebroid_engine, lie_E


def _prove(lhs, rhs, reg, eng=None):
    return ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng)


# --------------------------------------------------------------------- #
# P0-5 (M2-2): product_rule ↔ LieDerivative.splits_over_product          #
# --------------------------------------------------------------------- #


def _engines(A, reg):
    """The engine paths through which the product rule can reach an
    ``Act(L^E_u, ·)``: none (bare simplify / product_rule pass), the
    algebroid engine, the algebroid engine + the slot-reachable
    ActExpansionDefinition, the bare ActExpansionDefinition, and the
    research ``assemble_engine`` (which adds ActExpansionDefinition for
    any expression containing an Act)."""
    from jacopy.research.engine_assembly import assemble_engine

    alg = algebroid_engine(A, registry=reg)
    alg_act = algebroid_engine(A, registry=reg)
    alg_act.register(ActExpansionDefinition(reg))
    return {
        "none": None,
        "algebroid": alg,
        "algebroid+act": alg_act,
        "act-only": ExpansionEngine([ActExpansionDefinition(reg)]),
        "assembled": assemble_engine(
            Act(lie_E(A, A.sections("u")[0]), Integer(1)),
            registry=reg,
            extra=tuple(algebroid_engine(A, registry=reg).definitions),
        ),
    }


def _setup(decl, tag):
    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    A = algebroid(tag, Bundle(tag), declare=decl)
    u, v = A.sections("u v")
    (P,) = p_vectors("P", degree=2, bundle=A.bundle)
    return reg, f, A, u, v, P


def _rl(A, u, f, s):
    """ρ(u)(f)·s + f·[u, s]."""
    return Sum(Product(Act(A.anchor(u), f), s), Product(f, A.bracket(u, s)))


UNDECLARED = [
    (),
    ("antisymmetric", "jacobi"),
    ("symmetric-part",),
    ("metric",),
    ("courant",),
]


class TestLieProductRuleHookEndToEnd:
    @pytest.mark.parametrize("decl", UNDECLARED)
    def test_product_rule_pass_keeps_section_product_inert(self, decl):
        # Before (4b4ee76 / 0b00e1b): product_rule split
        # L_u(f v) → L_u(f)·v + f·L_u(v) for EVERY algebroid.
        reg, f, A, u, v, P = _setup(decl, "Apr" + str(len(decl)))
        L = lie_E(A, u)
        for arg in (Product(f, v), Product(f, P)):
            assert product_rule(Act(L, arg), reg) == Act(L, arg)
            assert ActExpansionDefinition(reg).matches(Act(L, arg)) is False

    @pytest.mark.parametrize("decl", UNDECLARED)
    @pytest.mark.parametrize(
        "path", ["none", "algebroid", "algebroid+act", "act-only", "assembled"]
    )
    def test_right_leibniz_split_does_not_close(self, decl, path):
        # Without right Leibniz L_u(f v) := [u, f v] is opaque: neither
        # ρ(u)(f)v + f[u,v] nor the product-rule form ρ(u)(f)v + f L_u v
        # may close. Before: CLOSED with the algebroid engine (all five
        # declaration sets) through the generic product rule.
        reg, f, A, u, v, P = _setup(decl, "Arl" + path[:3] + str(len(decl)))
        eng = _engines(A, reg)[path]
        L = lie_E(A, u)
        lhs = Act(L, Product(f, v))
        for rhs in (
            _rl(A, u, f, v),
            Sum(Product(Act(A.anchor(u), f), v), Product(f, Act(L, v))),
        ):
            with pytest.raises(ProofFailure):
                _prove(lhs, rhs, reg, eng)

    @pytest.mark.parametrize("decl", UNDECLARED + [("almost-leibniz",), ("lie",)])
    @pytest.mark.parametrize("path", ["none", "algebroid", "algebroid+act"])
    def test_bivector_product_does_not_split(self, decl, path):
        # P a bivector (a section of Λ²E, NOT a form): L_u(f·P) =
        # ρ(u)(f)P + f L_u P is unlicensed (CLOSED before on every
        # algebroid). Even a declared right-Leibniz rule on [u, f v]
        # does not reach Λ²E (no multivector bracket is modelled):
        # completeness note, not a soundness gap.
        reg, f, A, u, v, P = _setup(decl, "Abv" + path[:3] + str(len(decl)))
        eng = _engines(A, reg)[path]
        L = lie_E(A, u)
        with pytest.raises(ProofFailure):
            _prove(
                Act(L, Product(f, P)),
                Sum(Product(Act(A.anchor(u), f), P), Product(f, Act(L, P))),
                reg,
                eng,
            )

    @pytest.mark.parametrize("level", ["almost-leibniz", "lie", "leibniz"])
    @pytest.mark.parametrize("path", ["algebroid", "algebroid+act"])
    def test_declared_right_leibniz_closes(self, level, path):
        reg, f, A, u, v, P = _setup((level,), "Adl" + path[:4] + level[:3])
        chain = _prove(
            Act(lie_E(A, u), Product(f, v)),
            _rl(A, u, f, v),
            reg,
            _engines(A, reg)[path],
        )
        assert any("right-Leibniz" in s.rule for s in chain.steps)

    def test_courant_right_leibniz_closes_by_citation(self):
        # Courant level does NOT declare right Leibniz: it is derived
        # from metric invariance + non-degeneracy [B 4.11]. The product
        # rule never supplies it; citing the derived theorem does.
        from jacopy.central.algebroid import prove_right_leibniz_from_metric
        from jacopy.proof.theorems import TheoremDefinition

        reg, f, A, u, v, P = _setup(("courant",), "Acit")
        lhs = Act(lie_E(A, u), Product(f, v))
        with pytest.raises(ProofFailure):
            _prove(lhs, _rl(A, u, f, v), reg, algebroid_engine(A, registry=reg))
        _, thm = prove_right_leibniz_from_metric(A, u, v, f, registry=reg)
        eng = ExpansionEngine([TheoremDefinition(thm)])
        for d in algebroid_engine(A, registry=reg).definitions:
            eng.register(d)
        eng.register(ActExpansionDefinition(reg))
        chain = _prove(lhs, _rl(A, u, f, v), reg, eng)
        assert any(thm.name in s.rule for s in chain.steps)


class TestZeroBracketIdentityAnchor:
    """M = ℝ, E = Tℝ, ρ = id, [u,v] := 0 (ℝ-bilinear, not right
    Leibniz). e = ∂x: L_e(x e) = [e, x e] = 0, whereas the product rule
    would give ρ(e)(x)·e + x·L_e e = 1·e + 0 = e."""

    def _calc(self):
        reg = PropertyRegistry()
        (x,) = functions("x", registry=reg)
        (e,) = vector_fields("e")
        calc = BracketCalculus(
            "zero-id-int", anchor=lambda s: s, bracket=lambda a, b: Integer(0)
        )
        return reg, x, e, calc

    @pytest.mark.parametrize("with_intrinsic", [False, True])
    def test_product_rule_form_does_not_close(self, with_intrinsic):
        reg, x, e, calc = self._calc()
        L = calc.lie(e)
        lhs = Act(L, Product(x, e))
        assert product_rule(lhs, reg) == lhs
        rules = [ActExpansionDefinition(reg)]
        if with_intrinsic:
            rules.append(IntrinsicLDefinition(calc, reg))
        for eng in (None, ExpansionEngine(rules)):
            for rhs in (
                Product(Act(e, x), e),
                Sum(Product(Act(e, x), e), Product(x, Act(L, e))),
            ):
                with pytest.raises(ProofFailure):
                    _prove(lhs, rhs, reg, eng)

    def test_definition_still_closes_with_act_expansion(self):
        reg, x, e, calc = self._calc()
        eng = ExpansionEngine(
            [IntrinsicLDefinition(calc, reg), ActExpansionDefinition(reg)]
        )
        assert _prove(Act(calc.lie(e), Product(x, e)), Integer(0), reg, eng).steps


# --------------------------------------------------------------------- #
# Non-derivation Derivation subclasses (section-valued atoms)           #
# --------------------------------------------------------------------- #


def _section_values():
    """Atoms that subclass Derivation only for slot plumbing: VALUES in
    a bundle other than TM. ``Act(value, ·)`` is undefined — before,
    the generic product rule split e.g. ``[u,v]_E(f·g)`` into
    ``[u,v]_E(f)·g + f·[u,v]_E(g)`` and zeroed ``[u,v]_E(3)``."""
    from jacopy.central.algebroid.context import LocalityOperator, MetricSharp
    from jacopy.central.algebroid.operators import (
        Derivator,
        Jacobiator,
        MappedSection,
        section_map,
    )
    from jacopy.packages.generalized.bourbaki_exact import ChiSec, PhiSec
    from jacopy.packages.generalized.bourbaki_precalculus import (
        BD,
        BIota,
        BLieR,
        BLieZ,
        BSymbol,
    )
    from jacopy.packages.generalized.bourbaki_structure import (
        BDop,
        BLieRE,
        BMetric,
        BSymbolL,
    )
    from jacopy.packages.generalized.courant_axioms import CourantD
    from jacopy.packages.generalized.general_twist import PsiInvSec, PsiSec
    from jacopy.packages.metric_affine.torsion_curvature import (
        Curvature,
        Torsion,
    )

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    A = algebroid("Asv", Bundle("Asv"))
    u, v, w = A.sections("u v w")
    X, Y = vector_fields("X Y")
    E = Bundle("Asv")
    vals = {
        "AlgebroidBracket": A.bracket(u, v),
        "MetricSharp": MetricSharp("Asv", A.D(f)),
        "LocalityOperator": LocalityOperator("Asv", A.D(f), u, v),
        "MappedSection": MappedSection("Φ", u),
        "MappedSection(E→E)": section_map("Ψ", E, E)(u),
        "Jacobiator": Jacobiator("Asv", u, v, w),
        "Derivator": Derivator("Asv", "Φ", u, v),
        "CourantD": CourantD("Asv", f),
        "BIota": BIota(X, u),
        "BD": BD(u),
        "BSymbol": BSymbol(f, u),
        "BLieR": BLieR(X, u),
        "BLieZ": BLieZ(X, u),
        "BMetric": BMetric(u, v),
        "BDop": BDop(u),
        "BSymbolL": BSymbolL(f, u),
        "BLieRE": BLieRE(u, v),
        "PhiSec": PhiSec(X),
        "ChiSec": ChiSec(u),
        "PsiSec": PsiSec(u),
        "PsiInvSec": PsiInvSec(u),
        "Torsion(E)": Torsion("∇", X, Y, bundle=E),
        "Curvature(E)": Curvature("∇", X, Y, u, bundle=E),
    }
    return reg, f, g, X, A, vals


def _vector_fields():
    """Derivation subclasses that ARE vector fields (Leibniz on C∞(M))."""
    from jacopy.central.algebroid.operators import Predator, section_map
    from jacopy.central.objects.bundle import TM
    from jacopy.packages.metric_affine.torsion_curvature import (
        Curvature,
        Torsion,
    )

    reg = PropertyRegistry()
    f, g = functions("f g", registry=reg)
    A = algebroid("Avf", Bundle("Avf"))
    u, v = A.sections("u v")
    X, Y, Z = vector_fields("X Y Z")
    return reg, f, g, {
        "AnchoredVF": A.anchor(u),
        "Predator": Predator("Avf", "Φ", u, v),
        "MappedSection(E→TM)": section_map("Φ", A.bundle, TM)(u),
        "Torsion(TM)": Torsion("∇", X, Y),
        "Curvature(TM)": Curvature("∇", X, Y, Z),
    }


class TestSectionValuedAtomsAreNotDerivations:
    def test_product_rule_leaves_act_inert(self):
        reg, f, g, X, A, vals = _section_values()
        for name, op in vals.items():
            for arg in (Product(f, g), Product(f, X)):
                assert product_rule(Act(op, arg), reg) == Act(op, arg), name
            # no D(c) = 0 annihilation either
            assert product_rule(Act(op, Integer(3)), reg) == Act(op, Integer(3)), name
            assert ActExpansionDefinition(reg).matches(Act(op, Product(f, g))) is False

    def test_leibniz_split_does_not_close(self):
        # [u,v]_E(f·g) = [u,v]_E(f)·g + f·[u,v]_E(g) CLOSED before
        # (engine=None and algebroid_engine).
        reg, f, g, X, A, vals = _section_values()
        for name in ("AlgebroidBracket", "Jacobiator", "MetricSharp"):
            op = vals[name]
            lhs = Act(op, Product(f, g))
            rhs = Sum(Product(Act(op, f), g), Product(f, Act(op, g)))
            for eng in (None, algebroid_engine(A, registry=reg)):
                with pytest.raises(ProofFailure):
                    _prove(lhs, rhs, reg, eng)

    def test_markers_survive_slot_rewrites(self):
        from jacopy.central.algebroid.operators import (
            MappedSection,
            MappedSectionLinearityDefinition,
        )

        reg, f, g, X, A, vals = _section_values()
        (u,) = A.sections("u")
        for name, op in vals.items():
            new = op.with_slots(*op.rewritable_slots)
            assert new.leibniz is False and new.section_value, name
        # the TM flag of a mapped section is identity and survives
        # its linearity rule
        tm = MappedSection("Φ", Product(f, u), tangent=True)
        assert tm != MappedSection("Φ", Product(f, u))
        out = MappedSectionLinearityDefinition(reg).rewrite(tm)
        assert out == Product(f, MappedSection("Φ", u, tangent=True))

    def test_vector_fields_still_split(self):
        reg, f, g, ops = _vector_fields()
        for name, op in ops.items():
            assert product_rule(Act(op, Product(f, g)), reg) == Sum(
                Product(Act(op, f), g), Product(f, Act(op, g))
            ), name
            assert product_rule(Act(op, Integer(3)), reg) == Integer(0), name

    def test_act_on_section_value_is_untyped(self):
        # kind_of (the one type source): ρ(u)(f) is a function, but
        # [u,v]_E(f) is undefined — before it was typed 'function' and
        # so certified as a scalar coefficient.
        from jacopy.central.calculus.scalars import is_scalar_function
        from jacopy.central.objects.kind import kind_of

        reg, f, g, X, A, vals = _section_values()
        for name, op in vals.items():
            assert kind_of(Act(op, f), reg).kind != "function", name
            assert not is_scalar_function(Act(op, f), reg), name
        (u,) = A.sections("u")
        assert is_scalar_function(Act(A.anchor(u), f), reg)


# --------------------------------------------------------------------- #
# metric_affine engines: IndexedSumLinearity with the registry          #
# --------------------------------------------------------------------- #


class TestMetricAffineIndexedSumRegistry:
    """The metric_affine engines built IndexedSumLinearityDefinition
    without the registry: a functions() symbol in the MIDDLE of an
    indexed-sum body was not certified scalar, so it was never pulled
    out (completeness regression of the order-preserving rule)."""

    def _setup(self):
        from jacopy.core.indexed_sum import IndexedSum
        from jacopy.core.pairing import Pairing
        from jacopy.central.objects.frame import Frame, FrameIndex

        reg = PropertyRegistry()
        (h,) = functions("h", registry=reg)
        E = algebroid("Eir", Bundle("Eir"), declare=("lie",))
        (v,) = E.sections("v")
        fr = Frame("e", bundle=E.bundle)
        s = FrameIndex("s")
        c_s = Pairing(fr.dual().field("s"), v)
        return reg, h, E, fr, s, c_s, IndexedSum

    def test_engines_carry_the_registry(self):
        from jacopy.central.calculus.indexed_rules import (
            IndexedSumLinearityDefinition,
        )
        from jacopy.packages.metric_affine.engine import metric_affine_engine
        from jacopy.packages.metric_affine.modified import _engine

        reg, h, E, fr, s, c_s, IS = self._setup()
        for eng in (metric_affine_engine(registry=reg), _engine(E, fr, reg)):
            rules = [
                r for r in eng.definitions
                if isinstance(r, IndexedSumLinearityDefinition)
            ]
            assert rules and all(r._registry is reg for r in rules)
            # Σ_s ⟨e^s,v⟩·h·e_s → h·Σ_s ⟨e^s,v⟩·e_s (h passes a scalar)
            x = IS(s, fr, Product(c_s, h, fr.field("s")))
            assert rules[0].rewrite(x) == Product(
                h, IS(s, fr, Product(c_s, fr.field("s")))
            )

    def test_middle_scalar_closes_through_modified_engine(self):
        # ρ(Σ_s ⟨e^s,v⟩·h·e_s) = h·ρ(Σ_s ⟨e^s,v⟩·e_s): ρ is C∞-linear
        # and h a function. ProofFailure before (registry-less rule).
        from jacopy.packages.metric_affine.modified import _engine

        reg, h, E, fr, s, c_s, IS = self._setup()
        lhs = E.anchor(IS(s, fr, Product(c_s, h, fr.field("s"))))
        rhs = Product(h, E.anchor(IS(s, fr, Product(c_s, fr.field("s")))))
        assert _prove(lhs, rhs, reg, _engine(E, fr, reg)).steps


# --------------------------------------------------------------------- #
# ConnectionForm: alternation certificate                              #
# --------------------------------------------------------------------- #


class TestConnectionFormAlternation:
    def test_wedge_of_connection_forms_is_alternating(self):
        # ω^a_b is a 1-form, so (ω^a_b ∧ ω^b_c)(X,Y) + (…)(Y,X) = 0.
        # Before: admits_alternation False (no certificate) → the sum
        # stayed unsimplified (completeness).
        from jacopy.algorithms.simplify import simplify
        from jacopy.core.multi_eval import MultiEval, admits_alternation
        from jacopy.core.wedge import Wedge
        from jacopy.central.objects import forms
        from jacopy.packages.metric_affine.frame_components import (
            ConnectionForm,
        )

        reg = PropertyRegistry()
        X, Y = vector_fields("X Y")
        (th,) = forms("θ", degree=1)
        w1 = ConnectionForm("∇", "e", "a", "b")
        w2 = ConnectionForm("∇", "e", "b", "c")
        assert admits_alternation(w1)
        for W in (Wedge(w1, w2), Wedge(w1, th)):
            assert admits_alternation(W)
            assert simplify(
                Sum(MultiEval(W, X, Y), MultiEval(W, Y, X)), reg
            ) == Integer(0)


# --------------------------------------------------------------------- #
# EndoForm typed with the registry                                     #
# --------------------------------------------------------------------- #


class TestEndoFormRegistryKind:
    def test_function_argument_through_registry(self):
        # f a functions() symbol: m̃(f²) is a 0-form. Before: kind
        # 'unknown' and d(m̃(f²)·α) raised "Degree … not determined".
        from jacopy.central.calculus.scalars import is_scalar_function
        from jacopy.central.objects import forms
        from jacopy.central.objects.endomorphism import EndoForm
        from jacopy.central.objects.kind import kind_of
        from jacopy.central.tangent.exterior import d
        from jacopy.core.expr import Neg, Power
        from jacopy.core.wedge import Wedge

        reg = PropertyRegistry()
        (f,) = functions("f", registry=reg)
        a, b = forms("α β", degree=1)
        (X,) = vector_fields("X")
        m = EndoForm("m", Power(f, Integer(2)))
        assert kind_of(m, reg).kind == "function"
        assert is_scalar_function(m, reg)
        assert product_rule(d(Product(m, a)), reg) == Sum(
            Product(d(m), a), Product(m, d(a))
        )
        # m̃(f·α) is a 1-form: d(m̃(fα)∧β) = dm̃(fα)∧β − m̃(fα)∧dβ
        mf = EndoForm("m", Product(f, a))
        assert kind_of(mf, reg).degree == a.degree
        assert product_rule(d(Wedge(mf, b)), reg) == Sum(
            Wedge(d(mf), b), Neg(Wedge(mf, d(b)))
        )
        # unchanged: m̃ of a vector field has no form type
        assert kind_of(EndoForm("m", X), reg).kind == "unknown"
        assert not is_scalar_function(EndoForm("m", X), reg)
