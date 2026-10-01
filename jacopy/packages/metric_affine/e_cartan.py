"""
The two-fold E-Cartan structure equations [ADM Prop 3.9, Eq. (3.48)]
(Phase 4.F.4b / 4.F.6; audit 0b00e1b-FULL M7-4).

ADM writes the Cartan structure equations on an anti-commutable local
pre-Leibniz algebroid with TWO different exterior derivatives:

    T^a(∇)   = d(∇) e^a     + ω^a_b(∇) ∧ e^b,
    R^a_b(∇) = d̂(∇) ω^a_b(∇) + ω^a_c(∇) ∧ ω^c_b(∇),

where ``T^a(u,v) := ⟨e^a, ᴸT(u,v)⟩`` (the modified E-torsion, built
with the modified bracket ``[u,v]^∇ = [u,v] − Λ(u,v)``) and
``R^a_b(u,v) := ⟨e^a, ᴸ̂R(u,v)e_b⟩`` (the E-curvature, built with the
PROJECTED modified bracket ``b̂ = [·,·] − Λ̂``), ADM (3.39)-(3.40);
``d(∇)``/``d̂(∇)`` are the Palais-type derivatives (3.41)/(3.42) of
the (projected) modified bracket, ``ω^a_b(v) := ⟨e^a, ∇_v e_b⟩``
(3.38).

Machine form: both equations are proved EVALUATED ON THE FRAME,
``(·)(e_b, e_c)``, with the genuine indexed wedge sum, through the
derived-algebroid engine of :mod:`~jacopy.packages.metric_affine.derived`
(``E^∇`` / ``E^∇̂`` whose bracket bridges definitionally to the
(projected) modified bracket) plus the frame layer: the connection-form
evaluation (:class:`ConnectionFormEvaluationDefinition` — bundle-
agnostic, so it is its own algebroid counterpart), the wedge evaluation,
frame duality ``⟨e^a, e_b⟩ = δ^a_b`` and the guarded pairing split.

* :func:`prove_e_cartan_first` — declaration-free, for an ARBITRARY
  E-connection (the evaluated identity uses no anti-symmetry).
* :func:`prove_e_cartan_second` — needs the frame-decomposition
  declaration ``∇_{e_b}e_c = Σ_s Γ^s_bc e_s`` (opt-in assumption): the
  ``ω ∧ ω`` term and the second covariant derivative meet in the ΓΓ
  form (ADM's proof does the same: it replaces ``v`` by ``∇_v X_b``).

Mixing the derivatives honestly FAILS (tested): the first equation
with ``d̂(∇)`` leaves the ``(1−𝒫)Λ`` anomaly, the second with ``d(∇)``
likewise — exactly why ADM needs two derivatives.

Sign convention: identical to the package's ``ᴸT = T⁽⁰⁾ + Λ`` and
``ᴸ̂R = R⁽⁰⁾ + ∇_{Λ̂}`` (= ADM (3.13)/(3.20) with the modified
brackets), so (3.48) holds as PRINTED; a sign-flipped wedge term is
refused (tested).

NOT built (ROADMAP: deferred): ADM Prop 3.10 (the algebraic Bianchi
identities rewritten with the projected torsion ``T̂``, Def 3.16 — the
package has no ``T̂``; the content is ADM Prop 3.7, proved in
:mod:`e_bianchi`) and ADM Prop 3.11 (differential Bianchi with
``d̂(∇)²``; needs torsion/curvature 2-form atoms and ``d̂`` on 2-forms
at three frame arguments).
"""

from __future__ import annotations

from typing import Optional

from jacopy.bibliography import cite
from jacopy.core.expr import Expr, Neg, Sum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.objects.connection import Connection
from jacopy.central.objects.frame import Frame, IndexLike, _index_str
from jacopy.central.algebroid.context import Algebroid
from jacopy.central.algebroid.locality import LocalityProjector
from jacopy.packages.metric_affine.derived import (
    d_derived,
    derived_algebroid,
)
from jacopy.packages.metric_affine.frame_components import (
    ConnectionFormEvaluationDefinition,
    FrameConnectionCoefficientDefinition,
    FramePairingScalarDefinition,
    FramePairingSplitDefinition,
    connection_form,
)
from jacopy.packages.metric_affine.modified import (
    modified_torsion,
    projected_curvature,
)

#: Literature anchor of the two theorems (metadata only).
SOURCE = cite("DereliDogan2023", "Proposition 3.9, Eq. (3.48)")


def e_cartan_engine(
    base: Algebroid,
    derived: Algebroid,
    conn: Connection,
    fr: Frame,
    *,
    registry: Optional[PropertyRegistry] = None,
    projector: Optional[LocalityProjector] = None,
    projected_bracket: Optional[bool] = None,
    decomposed: bool = False,
):
    """The derived-algebroid engine plus the frame layer of the Cartan
    equations.

    ``projector`` registers the base projector's rules; the derived
    bracket bridges to ``[·,·] − Λ̂`` when ``projected_bracket`` (default:
    ``projector is not None``) and to ``[·,·] − Λ`` otherwise — kept
    separate so the "wrong derivative" honest-fail tests can pair a
    projected curvature with the UNPROJECTED ``d(∇)``. ``decomposed``
    registers the opt-in frame-decomposition declaration."""
    from jacopy.central.calculus import (
        IntrinsicDDefinition,
        IntrinsicLDefinition,
    )
    from jacopy.central.algebroid.calculus import algebroid_calculus
    from jacopy.central.calculus.indexed_rules import WedgeEvalDefinition
    from jacopy.central.tangent.definitions import FrameDualityDefinition
    from jacopy.packages.metric_affine.decomposition import (
        ConnectionFrameDecompositionDefinition,
    )
    from jacopy.packages.metric_affine.derived import (
        DerivedAnchorBridgeDefinition,
        DerivedBracketBridgeDefinition,
    )
    from jacopy.packages.metric_affine.modified import _engine

    if projected_bracket is None:
        projected_bracket = projector is not None
    if projected_bracket and projector is None:
        raise ValueError("a projected bracket needs the projector")
    engine = _engine(
        base, fr, registry,
        projectors=(projector,) if projector is not None else (),
    )
    calc = algebroid_calculus(derived)
    engine.register(IntrinsicDDefinition(calc, registry))
    engine.register(IntrinsicLDefinition(calc, registry))
    engine.register(
        DerivedBracketBridgeDefinition(
            base, derived, conn, fr,
            projector if projected_bracket else None,
        )
    )
    engine.register(DerivedAnchorBridgeDefinition(base, derived))
    if decomposed:
        engine.register(ConnectionFrameDecompositionDefinition(conn, fr))
    engine.register(ConnectionFormEvaluationDefinition(conn, fr))
    engine.register(WedgeEvalDefinition(registry))
    engine.register(FrameDualityDefinition())
    engine.register(FramePairingSplitDefinition())
    engine.register(FrameConnectionCoefficientDefinition())
    engine.register(FramePairingScalarDefinition(registry))
    return engine


def _check_bound(bound: str, *labels) -> None:
    for label in labels:
        if _index_str(label) == bound:
            raise ValueError(
                f"bound index {bound!r} collides with a free index; "
                "pass a different `bound` name"
            )


def _ev(expr: Expr, u: Expr, v: Expr) -> MultiEval:
    return MultiEval(expr, u, v, alternating=True, slot_kind="vector")


def e_cartan_first_sides(
    base: Algebroid,
    conn: Connection,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    *,
    bound: str = "s",
    projected_d: bool = False,
):
    """``(lhs, rhs, derived)`` of the first equation on ``(e_b, e_c)``:
    ``⟨e^a, ᴸT(e_b,e_c)⟩`` and
    ``d(∇)e^a(e_b,e_c) + (Σ_s ω^a_s ∧ e^s)(e_b,e_c)``
    (``projected_d=True`` puts ``d̂(∇)`` in — a WRONG statement, kept
    for the honest-failure test)."""
    from jacopy.core.indexed_sum import IndexedSum
    from jacopy.core.wedge import Wedge
    from jacopy.central.objects.frame import FrameIndex

    _check_bound(bound, a, b, c)
    derived = derived_algebroid(base, projected=projected_d)
    e_up = fr.dual().field(a)
    eb, ec = fr.field(b), fr.field(c)
    wedge_sum = IndexedSum(
        FrameIndex(bound),
        fr,
        Wedge(connection_form(conn, fr, a, bound), fr.dual().field(bound)),
    )
    lhs = Pairing(e_up, modified_torsion(base, conn, fr, eb, ec))
    rhs = Sum(_ev(d_derived(derived, e_up), eb, ec), _ev(wedge_sum, eb, ec))
    return lhs, rhs, derived


def prove_e_cartan_first(
    base: Algebroid,
    conn: Connection,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    *,
    bound: str = "s",
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """[ADM Prop 3.9, first of (3.48)], frame-evaluated:

    ``⟨e^a, ᴸT(e_b,e_c)⟩ = d(∇)e^a(e_b,e_c) + (Σ_s ω^a_s ∧ e^s)(e_b,e_c)``

    — declaration-free (arbitrary E-connection on any algebroid with
    a locality operator)."""
    lhs, rhs, derived = e_cartan_first_sides(
        base, conn, fr, a, b, c, bound=bound
    )
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=e_cartan_engine(base, derived, conn, fr, registry=registry),
    )


def e_cartan_second_sides(
    base: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    d: IndexLike,
    *,
    bound: str = "s",
    projected_d: bool = True,
):
    """``(lhs, rhs, derived)`` of the second equation on ``(e_c, e_d)``:
    ``⟨e^a, ᴸ̂R(e_c,e_d)e_b⟩`` and
    ``d̂(∇)ω^a_b(e_c,e_d) + (Σ_s ω^a_s ∧ ω^s_b)(e_c,e_d)``
    (``projected_d=False`` puts ``d(∇)`` in — WRONG, for the
    honest-failure test)."""
    from jacopy.core.indexed_sum import IndexedSum
    from jacopy.core.wedge import Wedge
    from jacopy.central.objects.frame import FrameIndex

    _check_bound(bound, a, b, c, d)
    derived = derived_algebroid(base, projected=projected_d)
    ec, ed = fr.field(c), fr.field(d)
    lhs = Pairing(
        fr.dual().field(a),
        projected_curvature(base, conn, fr, projector, ec, ed, fr.field(b)),
    )
    wedge_sum = IndexedSum(
        FrameIndex(bound),
        fr,
        Wedge(
            connection_form(conn, fr, a, bound),
            connection_form(conn, fr, bound, b),
        ),
    )
    rhs = Sum(
        _ev(d_derived(derived, connection_form(conn, fr, a, b)), ec, ed),
        _ev(wedge_sum, ec, ed),
    )
    return lhs, rhs, derived


def prove_e_cartan_second(
    base: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    d: IndexLike,
    *,
    bound: str = "s",
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """[ADM Prop 3.9, second of (3.48)], frame-evaluated:

    ``⟨e^a, ᴸ̂R(e_c,e_d)e_b⟩ = d̂(∇)ω^a_b(e_c,e_d) + (Σ_s ω^a_s ∧ ω^s_b)(e_c,e_d)``

    — needs the opt-in frame-decomposition declaration for
    ``(∇, frame)``; no algebroid declaration."""
    lhs, rhs, derived = e_cartan_second_sides(
        base, conn, fr, projector, a, b, c, d, bound=bound
    )
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=e_cartan_engine(
            base,
            derived,
            conn,
            fr,
            registry=registry,
            projector=projector,
            decomposed=True,
        ),
    )


__all__ = [
    "SOURCE",
    "e_cartan_engine",
    "e_cartan_first_sides",
    "e_cartan_second_sides",
    "prove_e_cartan_first",
    "prove_e_cartan_second",
]
