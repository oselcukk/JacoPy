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


def test_contradictory_partner_and_diagonal_raise():
    fr = frame("b")
    data = ComponentInput(fr, dim=3, total=True)
    data.set_anholonomy(2, 2, 0, 7)
    with pytest.raises(ValueError):
        data.set_anholonomy(2, 0, 2, 7)  # would mean γ^2_{20} = −7
    with pytest.raises(ValueError):
        data.set_anholonomy(1, 0, 0, 3)  # γ^1_{00} must vanish
    data.set_anholonomy(1, 0, 0, 0)  # the zero is fine
