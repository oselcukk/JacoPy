"""Audit 0b00e1b (metric-affine lane) acceptance tests.

M7-1 / P0-6 — coframe recombination must fire only on C^∞-LINEAR
occurrences of the coframe atom.

The rule reads coframe completeness ``Df = Σ_s ρ(e_s)(f)·e^s`` backwards:

    Σ_s ρ(e_s)(f)·E[e^s] = E[Σ_s ρ(e_s)(f)·e^s] = E[Df].

The middle equality is C^∞-linearity of ``ξ ↦ E[ξ]`` (coefficients
``ρ(e_s)(f)`` are functions), so the rule is sound iff ``E`` is
homogeneous C^∞-linear in ``e^s`` and ``s`` enters only through
``ρ(e_s)`` and ``e^s``.

Hand counterexamples on TM (anchor = id, frame = coordinate frame):

* cubic, ℝ², h = 2x+3y, z = ∂x + 2∂y (so ⟨dx^j, z⟩ = z^j = (1, 2)):
      LHS = Σ_j ∂_j h·(z^j)³ = 2·1 + 3·8 = 26,
      RHS = (z h)³ = (2 + 6)³ = 512.       26 ≠ 512.
* derivative, ℝ, h = x², z = ∂x:
      LHS = Σ_j ∂_j h·z(⟨dx^j, z⟩) = 2x·∂x(1) = 0,
      RHS = z(z h) = ∂x(2x) = 2.            0 ≠ 2.
* quadratic, u = ∂1, v = ∂2:
      LHS = Σ_s ∂_s f·δ^s_1 δ^s_2 = 0,  RHS = ∂1 f·∂2 f.
* affine (a Sum mixing degree 0 and 1), ℝ, f = 2x, u = 0, c = 1:
      LHS = Σ_s ρ(e_s)(f)·(⟨e^s,u⟩ + c) = 2·(0 + 1) = 2,
      RHS = ⟨Df,u⟩ + c = 0 + 1 = 1.          2 ≠ 1.
"""

from __future__ import annotations

import pytest
import sympy as sp

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Integer, Power, Product, Sum
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.central.algebroid import LocalityOperator, algebroid
from jacopy.central.objects import Bundle, functions
from jacopy.central.objects.frame import Frame, FrameIndex
from jacopy.packages.metric_affine.modified import (
    CoframeRecombinationDefinition,
    _engine,
)
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure


# --------------------------------------------------------------------- #
# M7-1 setup
# --------------------------------------------------------------------- #


@pytest.fixture
def ctx():
    reg = PropertyRegistry()
    (f, c) = functions("f c", registry=reg)
    E = algebroid("Eaud", Bundle("Eaud"), declare=("local", "regular"))
    u, v, w, z = E.sections("u v w z")
    fr = Frame("e", bundle=E.bundle)
    es = fr.dual().field("s")
    rho_f = Act(E.anchor(fr.field("s")), f)
    rule = CoframeRecombinationDefinition(E, fr, reg)
    return dict(
        reg=reg, f=f, c=c, E=E, u=u, v=v, w=w, z=z, fr=fr, es=es,
        rho_f=rho_f, rule=rule,
    )


def _sum(ctx, *rest):
    return IndexedSum(
        FrameIndex("s"), ctx["fr"], Product(ctx["rho_f"], *rest)
    )


def _prove(ctx, lhs, rhs):
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=ctx["reg"],
        engine=_engine(ctx["E"], ctx["fr"], ctx["reg"]),
    )


def _rho(ctx, X, g):
    return Act(ctx["E"].anchor(X), g)


# --------------------------------------------------------------------- #
# the hand counterexamples, recomputed numerically
# --------------------------------------------------------------------- #


def test_hand_counterexamples_are_genuinely_false():
    x, y = sp.symbols("x y")
    # cubic: h = 2x+3y, z = (1, 2)
    h = 2 * x + 3 * y
    zc = (1, 2)
    lhs = sum(sp.diff(h, q) * zj**3 for q, zj in zip((x, y), zc))
    zh = sum(zj * sp.diff(h, q) for q, zj in zip((x, y), zc))
    assert (lhs, zh**3) == (26, 512)
    # derivative: h = x², z = ∂x, ⟨dx, ∂x⟩ = 1
    h1 = x**2
    assert sp.diff(h1, x) * sp.diff(sp.Integer(1), x) == 0
    assert sp.diff(sp.diff(h1, x), x) == 2
    # affine: f = 2x, u = 0, c = 1 on ℝ
    assert sp.diff(2 * x, x) * (0 + 1) == 2 != 0 + 1


# --------------------------------------------------------------------- #
# non-linear positions: the rule must NOT fire and the false identity
# must NOT be proved
# --------------------------------------------------------------------- #


def test_cubic_does_not_fire_and_26_vs_512_is_rejected(ctx):
    p = Pairing(ctx["es"], ctx["z"])
    q = _rho(ctx, ctx["z"], ctx["f"])
    lhs = _sum(ctx, Product(p, p, p))
    rhs = Product(q, q, q)  # the FALSE target (ρ(z)f)³
    assert not ctx["rule"].matches(lhs)
    with pytest.raises(ProofFailure):
        _prove(ctx, lhs, rhs)


def test_derivative_does_not_fire_and_0_vs_2_is_rejected(ctx):
    z, f, es = ctx["z"], ctx["f"], ctx["es"]
    lhs = _sum(ctx, _rho(ctx, z, Pairing(es, z)))
    rhs = _rho(ctx, z, _rho(ctx, z, f))  # the FALSE target ρ(z)ρ(z)f
    assert not ctx["rule"].matches(lhs)
    with pytest.raises(ProofFailure):
        _prove(ctx, lhs, rhs)


def test_quadratic_false_theorem_is_rejected(ctx):
    u, v, f, es = ctx["u"], ctx["v"], ctx["f"], ctx["es"]
    lhs = _sum(ctx, Pairing(es, u), Pairing(es, v))
    rhs = Product(_rho(ctx, u, f), _rho(ctx, v, f))
    assert not ctx["rule"].matches(lhs)
    with pytest.raises(ProofFailure):
        _prove(ctx, lhs, rhs)


def test_nested_locality_slots_do_not_fire(ctx):
    E, es, u, v, w = ctx["E"], ctx["es"], ctx["u"], ctx["v"], ctx["w"]
    inner = LocalityOperator(E.name, es, v, w)
    lhs = _sum(ctx, LocalityOperator(E.name, es, u, inner))
    assert not ctx["rule"].matches(lhs)
    lhs2 = _sum(
        ctx, LocalityOperator(E.name, es, u, v), Pairing(es, w)
    )
    assert not ctx["rule"].matches(lhs2)


def test_affine_sum_and_power_do_not_fire(ctx):
    es, u, c = ctx["es"], ctx["u"], ctx["c"]
    affine = _sum(ctx, Sum(Pairing(es, u), c))
    assert not ctx["rule"].matches(affine)
    power = _sum(ctx, Power(Pairing(es, u), Integer(2)))
    assert not ctx["rule"].matches(power)


def test_index_in_f_does_not_fire(ctx):
    E, fr, f, es, u = ctx["E"], ctx["fr"], ctx["f"], ctx["es"], ctx["u"]
    # f_s := ρ(e_s)(f) depends on s — Σ_s ρ(e_s)(f_s)·⟨e^s,u⟩ is not D(f_s)
    fs = Act(E.anchor(fr.field("s")), f)
    lhs = IndexedSum(
        FrameIndex("s"),
        fr,
        Product(Act(E.anchor(fr.field("s")), fs), Pairing(es, u)),
    )
    assert not ctx["rule"].matches(lhs)


# --------------------------------------------------------------------- #
# linear positions: still closes
# --------------------------------------------------------------------- #


def test_linear_pairing_still_closes(ctx):
    u, f, es = ctx["u"], ctx["f"], ctx["es"]
    lhs = _sum(ctx, Pairing(es, u))
    rhs = _rho(ctx, u, f)  # Σ_s ρ(e_s)f·⟨e^s,u⟩ = ⟨Df,u⟩ = ρ(u)f
    assert ctx["rule"].matches(lhs)
    chain = _prove(ctx, lhs, rhs)
    assert any("coframe recombination" in s.rule for s in chain.steps)


def test_linear_with_scalar_cofactor_and_locality_slot(ctx):
    E, es, u, v, c = ctx["E"], ctx["es"], ctx["u"], ctx["v"], ctx["c"]
    lhs = _sum(ctx, c, LocalityOperator(E.name, es, u, v))
    assert ctx["rule"].matches(lhs)
    out = ctx["rule"].rewrite(lhs)
    assert out == Product(
        c, LocalityOperator(E.name, E.D(ctx["f"]), u, v)
    )


def test_homogeneous_linear_sum_fires(ctx):
    es, u, v, f = ctx["es"], ctx["u"], ctx["v"], ctx["f"]
    lhs = _sum(ctx, Sum(Pairing(es, u), Pairing(es, v)))
    assert ctx["rule"].matches(lhs)
    rhs = Sum(_rho(ctx, u, f), _rho(ctx, v, f))
    _prove(ctx, lhs, rhs)


def test_anchor_direction_is_linear(ctx):
    # e^s inside the OPERATOR of Act is C^∞-linear: ρ(L(g·ξ,u,v)) =
    # g·ρ(L(ξ,u,v)) as a vector field, and (g·X)(a) = g·X(a).
    E, es, u, v = ctx["E"], ctx["es"], ctx["u"], ctx["v"]
    (g,) = functions("g", registry=ctx["reg"])
    lhs = _sum(ctx, Act(E.anchor(LocalityOperator(E.name, es, u, v)), g))
    assert ctx["rule"].matches(lhs)


# ===================================================================== #
# M7-2 — ComponentInput.set_anholonomy must store BOTH lower orders
# ===================================================================== #
#
# Definition (jacopy/central/tangent/anholonomy.py, PDF item 9b):
#     γ^c_{ab} := ⟨e^c, [e_a, e_b]⟩,
# antisymmetric in (a, b) because the Lie bracket is; the canonical atom
# anholonomy_coefficient(fr, c, a, b) returns −γ^c_{ba} for a > b. So
# γ^c_{ba} = v forces γ^c_{ab} = −v, and γ^c_{aa} = 0.
#
# Concrete witness on ℝ³: e_0 = ∂x, e_1 = ∂y, e_2 = e^{-7x}∂z.
#     [e_2, e_0] = e^{-7x}∂z∂x − ∂x(e^{-7x}∂z) = 7e^{-7x}∂z = 7·e_2,
# hence γ^2_{20} = 7 and γ^2_{02} = −7. (Before the fix, entering the
# non-canonical γ^2_{20} = 7 with total=True evaluated to 0.)

from jacopy.algorithms.simplify import simplify  # noqa: E402
from jacopy.central.objects import frame  # noqa: E402
from jacopy.central.tangent.anholonomy import (  # noqa: E402
    anholonomy_coefficient,
)
from jacopy.core.expr import Integer as _Int, Neg  # noqa: E402
from jacopy.packages.metric_affine.component_workflow import (  # noqa: E402
    ComponentInput,
)


def _eq(x, y):
    return simplify(Sum(x, Neg(y))) == _Int(0)


def test_concrete_frame_witness_gamma_2_20_is_7():
    x, y, z = sp.symbols("x y z")
    coords = (x, y, z)
    frame_vf = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, sp.exp(-7 * x)),
    ]

    def bracket(X, Y):
        return tuple(
            sp.simplify(
                sum(X[i] * sp.diff(Y[k], coords[i]) for i in range(3))
                - sum(Y[i] * sp.diff(X[k], coords[i]) for i in range(3))
            )
            for k in range(3)
        )

    br = bracket(frame_vf[2], frame_vf[0])
    assert br == tuple(sp.simplify(7 * c) for c in frame_vf[2])


@pytest.mark.parametrize("total", [False, True])
def test_non_canonical_order_is_not_swallowed(total):
    fr = frame("b")
    data = ComponentInput(fr, dim=3, total=total)
    data.set_anholonomy(2, 2, 0, 7)  # γ^2_{20} = 7 (non-canonical order)
    assert _eq(data.evaluate(anholonomy_coefficient(fr, 2, 2, 0)), _Int(7))
    assert _eq(
        data.evaluate(anholonomy_coefficient(fr, 2, 0, 2)), _Int(-7)
    )


def test_lane_acceptance_symbolic_value():
    reg = PropertyRegistry()
    (h,) = functions("h", registry=reg)
    fr = frame()
    data = ComponentInput(fr, dim=2, total=True)
    data.set_anholonomy("0", "1", "0", h)  # γ^0_{10} = h
    g01 = data.evaluate(anholonomy_coefficient(fr, "0", "0", "1"), registry=reg)
    g10 = data.evaluate(anholonomy_coefficient(fr, "0", "1", "0"), registry=reg)
    assert _eq(g01, Neg(h))
    assert _eq(g10, h)


def test_canonical_and_non_canonical_entry_agree():
    reg = PropertyRegistry()
    (h,) = functions("h", registry=reg)
    fr = frame()
    a = ComponentInput(fr, dim=2, total=True)
    a.set_anholonomy("0", "0", "1", Neg(h))
    b = ComponentInput(fr, dim=2, total=True)
    b.set_anholonomy("0", "1", "0", h)
    for lo in (("0", "1"), ("1", "0")):
        atom = anholonomy_coefficient(fr, "0", *lo)
        assert _eq(
            a.evaluate(atom, registry=reg), b.evaluate(atom, registry=reg)
        )


def test_consistent_explicit_partner_is_accepted():
    fr = frame("b")
    data = ComponentInput(fr, dim=3, total=True)
    data.set_anholonomy(2, 2, 0, 7)
    data.set_anholonomy(2, 0, 2, -7)  # the same fact, other order
    assert data.anholonomy_value(("2", "2", "0")) == _Int(7)
    assert data.anholonomy_value(("2", "0", "2")) == _Int(-7)


def test_overwrite_updates_both_orders_and_diagonal_raises():
    # Chief's decision: overwrite like set_gamma/set_pi/set_metric, but
    # always both orders together (value and −value).
    fr = frame("b")
    data = ComponentInput(fr, dim=3, total=True)
    data.set_anholonomy(2, 2, 0, 7)
    data.set_anholonomy(2, 0, 2, 5)  # redefine via the other order
    assert data.anholonomy_value(("2", "0", "2")) == _Int(5)
    assert data.anholonomy_value(("2", "2", "0")) == _Int(-5)
    assert _eq(data.evaluate(anholonomy_coefficient(fr, 2, 2, 0)), _Int(-5))
    with pytest.raises(ValueError):
        data.set_anholonomy(1, 0, 0, 3)  # γ^1_{00} must vanish
    data.set_anholonomy(1, 0, 0, 0)  # the zero is fine


def test_commuting_symbolic_partner_is_accepted():
    # h·k and k·h are the same scalar: the partner write must not fail.
    reg = PropertyRegistry()
    h, k = functions("h k", registry=reg)
    fr = frame()
    data = ComponentInput(fr, dim=2, total=True)
    data.set_anholonomy("0", "1", "0", Product(h, k))
    data.set_anholonomy("0", "0", "1", Neg(Product(k, h)))
    g10 = data.evaluate(anholonomy_coefficient(fr, "0", "1", "0"), registry=reg)
    assert _eq(g10, Product(h, k))


# ===================================================================== #
# M7-1 follow-up (verifier): MultiEval heads and the f-index guard
# ===================================================================== #
#
# (d_E μ)(u,v) = ρ(u)μ(v) − ρ(v)μ(u) − μ([u,v])  (Palais). For a bracket
# that is only left-anchored/Leibniz, e.g. the Dorfman bracket with
#     [hX, v] = h[X,v] − ρ(v)(h)X + ⟨X,v⟩·Dh,
# one gets
#     (d_E μ)(hX, v) − h·(d_E μ)(X, v) = −⟨X,v⟩·⟨μ, Dh⟩ ≠ 0,
# so d_E μ is NOT a tensor and Σ_s ρ(e_s)f·(d_E μ)(g⁻¹e^s, v) ≠
# (d_E μ)(g⁻¹Df, v) in general. Before this fix the rule fired and
# produced exactly that right-hand side.

from jacopy.central.algebroid import d_E  # noqa: E402
from jacopy.central.algebroid.context import MetricSharp  # noqa: E402
from jacopy.central.objects import Form  # noqa: E402
from jacopy.core.multi_eval import MultiEval  # noqa: E402


def test_dorfman_d_mu_is_not_tensorial():
    # E = TR ⊕ T*R, sections a∂ + b dx, ρ = projection to ∂-part,
    # ⟨a∂+b dx, c∂+e dx⟩ = a e + c b, D h = h' dx,
    # Dorfman [a∂+b dx, c∂+e dx] = (a c' − c a')∂ + (a e)' dx
    # (L_X η with ι_Y dξ = 0 in dimension 1).
    x = sp.symbols("x")
    a, b, c, e, p, q, h = (
        sp.Function(n)(x) for n in ("a", "b", "c", "e", "p", "q", "h")
    )

    def br(U, V):
        (a1, b1), (c1, e1) = U, V
        return (
            a1 * sp.diff(c1, x) - c1 * sp.diff(a1, x),
            sp.diff(a1 * e1, x),
        )

    def mu(U):  # μ(a∂ + b dx) = p a + q b
        return p * U[0] + q * U[1]

    def rho(U, g):
        return U[0] * sp.diff(g, x)

    def dmu(U, V):
        return rho(U, mu(V)) - rho(V, mu(U)) - mu(br(U, V))

    X, v = (a, b), (c, e)
    hX = (h * a, h * b)
    defect = sp.expand(dmu(hX, v) - h * dmu(X, v))
    pairing = a * e + c * b
    target = -pairing * mu((0, sp.diff(h, x)))  # −⟨X,v⟩·⟨μ, Dh⟩
    assert sp.simplify(defect - target) == 0
    assert defect != 0


def test_d_E_head_multieval_does_not_fire(ctx):
    E, es, v = ctx["E"], ctx["es"], ctx["v"]
    mu = Form("μ", degree=1, bundle=E.bundle)
    lhs = _sum(ctx, MultiEval(d_E(E, mu), MetricSharp(E.name, es), v))
    # the FALSE target (d_E μ)(g⁻¹ Df, v)
    false_rhs = MultiEval(
        d_E(E, mu), MetricSharp(E.name, E.D(ctx["f"])), v
    )
    assert not ctx["rule"].matches(lhs)
    assert ctx["rule"].rewrite(lhs) == false_rhs  # what firing WOULD give


def test_declared_form_head_multieval_still_fires(ctx):
    E, es, v = ctx["E"], ctx["es"], ctx["v"]
    om = Form("ω", degree=2, bundle=E.bundle)  # a genuine tensor
    lhs = _sum(ctx, MultiEval(om, MetricSharp(E.name, es), v))
    assert ctx["rule"].matches(lhs)
    assert ctx["rule"].rewrite(lhs) == MultiEval(
        om, MetricSharp(E.name, E.D(ctx["f"])), v
    )


def test_split_refuses_s_dependent_f(ctx):
    # f_s := ⟨e^s, u⟩ depends on s; Σ_s ρ(e_s)(f_s)·⟨e^s,w⟩ is not
    # ⟨D f_s, w⟩ for any single function. matches() also rejects it
    # through the post-substitution index check (D f_s still carries
    # s), so the guard is pinned at the _split contract that rewrite()
    # relies on: no candidate with an s-dependent f is ever produced.
    E, fr, es, u, w = ctx["E"], ctx["fr"], ctx["es"], ctx["u"], ctx["w"]
    fs = Pairing(es, u)
    lhs = IndexedSum(
        FrameIndex("s"),
        fr,
        Product(Act(E.anchor(fr.field("s")), fs), Pairing(es, w)),
    )
    assert ctx["rule"]._split(lhs) is None
    assert not ctx["rule"].matches(lhs)


# ===================================================================== #
# M7-1 follow-up 2 (code-review): per-(node, slot) linearity certificates
# ===================================================================== #
#
# Every case below FIRED on 6b3fba0 (items 1-4, wrongly) or was REFUSED
# there (item 5, wrongly). For a function h:
#  1) ⟨ι_u(d_E μ), hX⟩: d_E μ(u, hX) ∋ −μ([u, hX]); ⟨L^E_u μ, hX⟩ =
#     ρ(u)(μ(hX)) − μ([u,hX]) — neither is h·(…) without a declared
#     right-Leibniz/skew bracket, so the pairing's other slot must be a
#     certified tensor.
#  2) compose is stored as Product: ∇_u∇_{hX}w = h∇_u∇_X w +
#     ρ(u)(h)∇_X w and ρ(u)ρ(hX)c = hρ(u)ρ(X)c + ρ(u)(h)ρ(X)c; only the
#     LEFTMOST factor is C^∞-linear (∇_{hX}∇_u w = h∇_X∇_u w).
#  3) a bare operator factor Product(∇_{hX}, w) is not a pointwise value.
#  4) ρ(hX) on a 1-form μ is a Lie derivative: L_{hX}μ = hL_Xμ + μ(X)dh.
#  5) g(hX, v) = h·g(X, v) (g a (0,2)-tensor) and ι_{hX}μ = h·ι_Xμ for a
#     declared form μ — genuinely linear, must fire.

from jacopy.algebra.derivation import compose  # noqa: E402
from jacopy.central.algebroid import lie_E  # noqa: E402
from jacopy.central.algebroid.context import EMetric  # noqa: E402
from jacopy.central.objects.connection import CovariantOp  # noqa: E402
from jacopy.central.objects.interior import Interior  # noqa: E402


@pytest.fixture
def cr(ctx):
    E = ctx["E"]
    X = MetricSharp(E.name, ctx["es"])  # g⁻¹e^s, linear in e^s
    mu = Form("μ", degree=1, bundle=E.bundle)

    def nab(Y):
        return CovariantOp("∇", Y, bundle=E.bundle)

    return dict(ctx, X=X, mu=mu, nab=nab, rho=E.anchor)


def _fires(ctx, body):
    return ctx["rule"].matches(_sum(ctx, body))


def test_item1_pairing_with_non_tensorial_form_does_not_fire(cr):
    E, u, X, mu = cr["E"], cr["u"], cr["X"], cr["mu"]
    body = Pairing(Act(Interior(u), d_E(E, mu)), X)
    # the FALSE target the old rule produced: ⟨ι_u d_E μ, g⁻¹Df⟩
    assert cr["rule"].rewrite(_sum(cr, body)) == Pairing(
        Act(Interior(u), d_E(E, mu)), MetricSharp(E.name, E.D(cr["f"]))
    )
    assert not _fires(cr, body)
    assert not _fires(cr, Pairing(Act(lie_E(E, u), mu), X))


def test_item2_composition_only_leftmost_factor(cr):
    nab, rho, u, w, c, X = (
        cr["nab"], cr["rho"], cr["u"], cr["w"], cr["c"], cr["X"]
    )
    assert not _fires(cr, Act(compose(nab(u), nab(X)), w))
    assert not _fires(cr, Act(compose(rho(u), rho(X)), c))
    assert _fires(cr, Act(compose(nab(X), nab(u)), w))


def test_item3_bare_operator_factor_does_not_fire(cr):
    assert not _fires(cr, Product(cr["nab"](cr["X"]), cr["w"]))


def test_item4_anchor_on_a_form_does_not_fire(cr):
    assert not _fires(cr, Act(cr["rho"](cr["X"]), cr["mu"]))
    assert _fires(cr, Act(cr["rho"](cr["X"]), cr["c"]))  # on a scalar


def test_item5_metric_and_interior_slots_fire(cr):
    E, X, v, mu, f = cr["E"], cr["X"], cr["v"], cr["mu"], cr["f"]
    gDf = MetricSharp(E.name, E.D(f))
    lhs = _sum(cr, EMetric(E.name, X, v))
    assert cr["rule"].matches(lhs)
    assert cr["rule"].rewrite(lhs) == EMetric(E.name, gDf, v)
    lhs = _sum(cr, Act(Interior(X), mu))
    assert cr["rule"].matches(lhs)
    assert cr["rule"].rewrite(lhs) == Act(Interior(gDf), mu)
    # ι_X of a NON-tensorial form stays refused
    assert not _fires(cr, Act(Interior(X), d_E(E, mu)))


# ===================================================================== #
# M7-1 follow-up 3: the coefficient's POSITION in the (non-commutative,
# composition-storing) product, and the missing tensor atoms
# ===================================================================== #
#
# Product also stores compositions: Product(⟨e^s,v⟩, ρ(w), ρ(e_s)f)
# applied to g is ⟨e^s,v⟩·ρ(w)(ρ(e_s)f·g), so
#   Σ_s ⟨e^s,v⟩·ρ(w)∘ρ(e_s)f (g)
#     = ρ(v)f·ρ(w)g + g·Σ_s ⟨e^s,v⟩·ρ(w)(ρ(e_s)f)       (TRUE)
#     ≠ ⟨Df,v⟩·ρ(w)(g)                                   (what firing gave)
# the Leibniz term Σ_s ⟨e^s,v⟩ g ρ(w)(ρ(e_s)f) is lost. The same holds for
# a Neg/Sum-wrapped operator, a TM vector field Y, and ∇_w. On fb21fd8
# the four false targets below were PROVED by ExpandAndSimplify + _engine.

from jacopy.central.objects import vector_fields  # noqa: E402
from jacopy.packages.metric_affine.frame_components import (  # noqa: E402
    ConnectionForm,
)
from jacopy.packages.metric_affine.metric import (  # noqa: E402
    MetricValue,
    NonMetricity,
)


def _refused(ctx, lhs, false_rhs):
    with pytest.raises(ProofFailure):
        _prove(ctx, lhs, false_rhs)


def test_item1_coefficient_right_of_operator_false_identity_rejected(cr):
    E, es, v, w, f = cr["E"], cr["es"], cr["v"], cr["w"], cr["f"]
    rho = cr["rho"]
    (g,) = functions("g", registry=cr["reg"])
    body = compose(Pairing(es, v), rho(w), cr["rho_f"])
    lhs = Act(IndexedSum(FrameIndex("s"), cr["fr"], body), g)
    false_rhs = Act(compose(Pairing(E.D(f), v), rho(w)), g)
    assert not cr["rule"].matches(IndexedSum(FrameIndex("s"), cr["fr"], body))
    _refused(cr, lhs, false_rhs)


def test_item2_wrapped_operator_false_identity_rejected(cr):
    E, X, f, c = cr["E"], cr["X"], cr["f"], cr["c"]
    rho, fr = cr["rho"], cr["fr"]
    (g,) = functions("g", registry=cr["reg"])
    neg_body = Product(Neg(rho(X)), cr["rho_f"])
    sum_body = Product(
        Sum(rho(X), rho(MetricSharp(E.name, Product(c, cr["es"])))),
        cr["rho_f"],
    )
    for body in (neg_body, sum_body):
        assert not cr["rule"].matches(IndexedSum(FrameIndex("s"), fr, body))
    lhs = Act(IndexedSum(FrameIndex("s"), fr, neg_body), g)
    false_rhs = Act(Neg(rho(MetricSharp(E.name, E.D(f)))), g)
    _refused(cr, lhs, false_rhs)


def test_item3_tm_vector_field_and_nabla_false_identities_rejected(cr):
    E, es, v, w, z, f = (
        cr["E"], cr["es"], cr["v"], cr["w"], cr["z"], cr["f"]
    )
    fr = cr["fr"]
    (g,) = functions("g", registry=cr["reg"])
    (Y,) = vector_fields("Y")
    body = Product(Pairing(es, v), Y, cr["rho_f"])
    assert not cr["rule"].matches(IndexedSum(FrameIndex("s"), fr, body))
    lhs = Act(IndexedSum(FrameIndex("s"), fr, body), g)
    _refused(cr, lhs, Act(Product(Pairing(E.D(f), v), Y), g))
    nab_w = CovariantOp("∇", w, bundle=E.bundle)
    lhs = Act(
        IndexedSum(
            FrameIndex("s"), fr, compose(Pairing(es, v), nab_w, cr["rho_f"])
        ),
        z,
    )
    _refused(cr, lhs, Act(compose(Pairing(E.D(f), v), nab_w), z))


def test_coefficient_left_of_operator_still_closes(cr):
    # Σ_s ρ(e_s)f·⟨e^s,v⟩·ρ(w)(g) = ρ(v)f·ρ(w)(g): the coefficient stands
    # left of every operator, pulling it out is C^∞-linear.
    v, w, f, rho = cr["v"], cr["w"], cr["f"], cr["rho"]
    (g,) = functions("g", registry=cr["reg"])
    lhs = IndexedSum(
        FrameIndex("s"),
        cr["fr"],
        Product(cr["rho_f"], Pairing(cr["es"], v), Act(rho(w), g)),
    )
    assert cr["rule"].matches(lhs)
    _prove(cr, lhs, Product(Act(rho(v), f), Act(rho(w), g)))


# ---- item 4: tensors certified from their definitions ---------------- #


def test_nonmetricity_and_connection_form_are_tensorial_sympy():
    # Generic ∇ (Γ^k_ij) and metric g_ij on ℝ²:
    # Q(X,Y,Z) := X(g(Y,Z)) − g(∇_X Y, Z) − g(Y, ∇_X Z) is C^∞-linear in
    # every slot, and ω^a_b(X) := ⟨e^a, ∇_X e_b⟩ in X (∇_{hX} = h∇_X).
    x, y = sp.symbols("x y")
    co = (x, y)
    F = lambda n: sp.Function(n)(x, y)  # noqa: E731
    G = [[F(f"g{i}{j}") if i <= j else F(f"g{j}{i}") for j in range(2)]
         for i in range(2)]
    Gam = [[[F(f"G{k}{i}{j}") for j in range(2)] for i in range(2)]
           for k in range(2)]
    vec = lambda n: [F(f"{n}{i}") for i in range(2)]  # noqa: E731
    X, Y, Z, h = vec("X"), vec("Y"), vec("Z"), F("h")

    def act(V, fn):
        return sum(V[i] * sp.diff(fn, co[i]) for i in range(2))

    def nabla(V, W):
        return [
            act(V, W[k])
            + sum(Gam[k][i][j] * V[i] * W[j] for i in range(2) for j in range(2))
            for k in range(2)
        ]

    def g(A, B):
        return sum(G[i][j] * A[i] * B[j] for i in range(2) for j in range(2))

    def Q(A, B, C):
        return act(A, g(B, C)) - g(nabla(A, B), C) - g(B, nabla(A, C))

    hs = lambda V: [h * c for c in V]  # noqa: E731
    base = Q(X, Y, Z)
    for args in ((hs(X), Y, Z), (X, hs(Y), Z), (X, Y, hs(Z))):
        assert sp.expand(Q(*args) - h * base) == 0
    e_b = [sp.Integer(1), sp.Integer(0)]
    assert all(
        sp.expand(a - h * b) == 0
        for a, b in zip(nabla(hs(X), e_b), nabla(X, e_b))
    )


def test_item4_metric_value_nonmetricity_connection_form_fire(cr):
    E, X, v, w, f = cr["E"], cr["X"], cr["v"], cr["w"], cr["f"]
    gDf = MetricSharp(E.name, E.D(f))
    for body, expected in [
        (MetricValue("g", X, v), MetricValue("g", gDf, v)),
        (
            NonMetricity("∇", "g", X, v, w, bundle=E.bundle),
            NonMetricity("∇", "g", gDf, v, w, bundle=E.bundle),
        ),
        (
            Pairing(ConnectionForm("∇", "e", "a", "b"), X),
            Pairing(ConnectionForm("∇", "e", "a", "b"), gDf),
        ),
    ]:
        lhs = _sum(cr, body)
        assert cr["rule"].matches(lhs), body
        assert cr["rule"].rewrite(lhs) == expected
