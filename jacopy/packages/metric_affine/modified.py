"""
Modified E-torsion and projected E-curvature (Phase 4.E.2)
[MC Prop 3.2, Def 3.7, Prop 3.3-3.4, Cor 3.3, Def 3.11].

The pseudo tensors of 4.E.1 carry locality defects; the MC corrections
repair them:

    ᴸT(u, v)   := T⁽⁰⁾(u, v) + Σ_s L(e^s, ∇_{e_s} u, v),
    ᴸ̂R(u, v, w) := R⁽⁰⁾(u, v)w + Σ_s ∇_{𝒫(L(e^s, ∇_{e_s} u, v))} w,

with ``(e_s)`` a frame of ``E`` and ``𝒫`` a locality projector
(Phase 3.E.4 — this module is its main consumer).

The proofs turn on ONE new rule, the **coframe recombination**

    Σ_s ρ(e_s)(f) · E(e^s)  →  E(Df)

(collection direction ONLY — its inverse, a ``Df``-decomposition
axiom, would ping-pong against it; same design decision as the C2
collection of Phase 3.E.2). It is exactly the coframe-completeness
identity ``Df = Σ_s ⟨Df, e_s⟩ e^s = Σ_s ρ(e_s)(f)·e^s`` read
backwards, applied inside any slot-linear expression ``E`` via the
slot-walking substitution protocol.

* ``ᴸT`` is then ``C^∞``-tensorial in BOTH slots on a local algebroid
  (the recombined ``L(Df,u,v)`` cancels the 4.E.1 defect);
* ``ᴸ̂R``'s first slot closes the same way — the recombined
  ``∇_{𝒫(L(Df,u,v))}w`` meets the projector's ABSORPTION rule
  (``𝒫`` acts as identity on coboundary values) and cancels;
* ``ᴸ̂R``'s last slot uses the projector's KERNEL rule
  (``ρ(𝒫(L(…))) = 0``) plus the anchor morphism — MC Prop 3.3-3.4
  composed.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Expr, Neg, Product, Sum, Symbol
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.calculus.indexed_rules import contains_index
from jacopy.central.calculus.scalars import is_scalar_function
from jacopy.central.objects.connection import Connection, CovariantOp
from jacopy.central.objects.form import Form
from jacopy.central.objects.tensor import Tensor
from jacopy.central.objects.frame import (
    CoframeField,
    Frame,
    FrameField,
    FrameIndex,
)
from jacopy.central.algebroid.context import (
    Algebroid,
    AnchoredVF,
    LocalityOperator,
    MetricSharp,
)
from jacopy.central.algebroid.operators import MappedSection
from jacopy.central.algebroid.locality import LocalityProjector
from jacopy.packages.metric_affine.torsion_curvature import (
    curvature,
    torsion,
)


#: Sentinel of :func:`_hole_degree`: the hole sits in a position where
#: the expression is NOT ``C^∞``-linear in it (or in one we cannot
#: certify as such).
_NONLINEAR = -1

#: A fresh atom used only to detect whether the hole occurs.
_HOLE_PROBE = Symbol("⟪coframe-recombination hole probe⟫")

#: Operator-like atoms that are ``C^∞``-linear in EVERY rewritable slot
#: BY DEFINITION: ``L`` is ``C^∞``-trilinear [MC Def 3.5]; a
#: :class:`MappedSection` is the image under a ``C^∞``-linear bundle
#: map (the locality projector ``𝒫`` included); ``g⁻¹`` is a bundle
#: isomorphism; the anchor ``ρ`` is a bundle map. ``∇_X`` is
#: ``C^∞``-linear in its direction ``X`` (its only slot).
_LINEAR_SLOT_ATOMS = (
    LocalityOperator,
    MappedSection,
    MetricSharp,
    AnchoredVF,
    CovariantOp,
)

#: Structural nodes ``C^∞``-multilinear in every child: products of
#: functions/sections and the pairing ``⟨α, X⟩``. The evaluation
#: ``H(X_1, …, X_p)`` (:class:`MultiEval`) is NOT here: it is
#: ``C^∞``-multilinear only when the head ``H`` is a genuine tensor,
#: see :func:`_certified_tensor_head`.
_MULTILINEAR_NODES = (Product, Pairing)


def _certified_tensor_head(head: Expr, hole: Expr) -> bool:
    """True when ``head(X_1, …)`` is certainly ``C^∞``-multilinear in
    its argument slots: the head is the hole itself or a DECLARED
    tensor atom (:class:`Form` / :class:`Tensor`, the coframe
    included), which is a section of a tensor bundle by definition.

    A composite head is NOT certified. The case that matters is
    ``d_E μ``: by Palais ``(d_E μ)(u,v) = ρ(u)μ(v) − ρ(v)μ(u) −
    μ([u,v])``, so with a bracket that is only left-anchored/
    Leibniz (metric, Courant), ``[hX,v] = h[X,v] − ρ(v)(h)X +
    ⟨X,v⟩Dh`` gives

        (d_E μ)(hX, v) − h·(d_E μ)(X, v) = −⟨X,v⟩·⟨μ, Dh⟩ ≠ 0;

    it is tensorial only for a skew (Lie-algebroid) bracket, a fact not
    available locally here — so every non-atomic head is refused."""
    return head == hole or isinstance(head, (Form, Tensor))


def _hole_degree(expr: Expr, hole: Expr) -> int:
    """Certified degree of ``expr`` in the atom ``hole``.

    Returns ``0`` when ``hole`` does not occur, ``1`` when ``expr`` is
    CERTIFIED homogeneous ``C^∞``-linear in ``hole`` (every occurrence
    sits in a ``C^∞``-linear slot and every monomial carries exactly
    one), and :data:`_NONLINEAR` otherwise. The recursion is:

    * ``hole`` itself → 1; a subtree without ``hole`` → 0;
    * ``Neg`` → degree of its argument;
    * ``Sum`` → the common degree of its summands (a mix of 0 and 1 is
      AFFINE, not linear: ``Σ_s c_s·(A + B(e^s)) ≠ A + B(Df)``);
    * ``H(X_1, …)`` → as a multilinear node only when
      :func:`_certified_tensor_head` certifies ``H``, else
      :data:`_NONLINEAR`;
    * a multilinear node (``Product``, ``⟨·,·⟩``) and a
      linear-slot atom (``L``, ``Φ``, ``g⁻¹``, ``ρ``, ``∇_·``) → the
      SUM of the child degrees, which must be ≤ 1 (two occurrences are
      quadratic);
    * ``Act(op, arg)`` → ``deg(op)`` provided ``deg(arg) == 0``
      (``(f·X)(a) = f·X(a)`` and ``∇_{fX} = f∇_X`` make ``Act``
      linear in the operator; it is only ℝ-linear, NOT ``C^∞``-linear,
      in its argument — Leibniz: ``X(f·a) = f·X(a) + X(f)·a``);
    * every other node carrying ``hole`` (``Power``, a nested binder,
      an unknown operator, …) → :data:`_NONLINEAR` (conservative).
    """
    if expr == hole:
        return 1
    if expr.substitute_atom(hole, _HOLE_PROBE) == expr:
        # ``substitute_atom`` (not a children walk) so that atoms
        # hiding the hole behind a class-specific override count too.
        return 0
    if isinstance(expr, Neg):
        return _hole_degree(expr.arg, hole)
    if isinstance(expr, Sum):
        degs = {_hole_degree(c, hole) for c in expr.children}
        return degs.pop() if len(degs) == 1 else _NONLINEAR
    if isinstance(expr, Act):
        if _hole_degree(expr.arg, hole) != 0:
            return _NONLINEAR
        return _hole_degree(expr.op, hole)
    if isinstance(expr, MultiEval):
        if not _certified_tensor_head(expr.head, hole):
            return _NONLINEAR
        kids = expr.children
    elif isinstance(expr, _MULTILINEAR_NODES):
        kids = expr.children
    elif isinstance(expr, _LINEAR_SLOT_ATOMS) and expr.is_atom:
        kids = tuple(expr.rewritable_slots)
    else:
        return _NONLINEAR
    total = 0
    for c in kids:
        d = _hole_degree(c, hole)
        if d == _NONLINEAR:
            return _NONLINEAR
        total += d
    return total if total <= 1 else _NONLINEAR


class CoframeRecombinationDefinition(Definition):
    """``Σ_s ρ(e_s)(f)·E(e^s) → E(Df)`` — coframe completeness in the
    collection direction (the sole direction; the decomposition
    inverse would ping-pong).

    **Soundness condition (exact).** Write the summand as
    ``ρ(e_s)(f)·E[e^s]`` where ``E[ξ]`` is the remaining factors with
    the coframe atom replaced by a hole ``ξ``. Then

        Σ_s ρ(e_s)(f)·E[e^s] = E[Σ_s ρ(e_s)(f)·e^s] = E[Df]

    holds iff (i) the bound index ``s`` occurs in the summand ONLY
    through ``ρ(e_s)`` and the atoms ``e^s`` (so ``E`` and ``f`` are
    the same for every ``s``) and (ii) ``ξ ↦ E[ξ]`` is
    ``C^∞``-LINEAR (additive and ``E[g·ξ] = g·E[ξ]`` for functions
    ``g``); the middle step is exactly this linearity with the
    coefficients ``g = ρ(e_s)(f)``, the last is coframe completeness
    ``Df = Σ_s ⟨Df, e_s⟩ e^s``. ℝ-linearity is not enough (a
    derivative of ``e^s`` produces the Leibniz term), and neither is
    "every ``e^s`` consumed": ``E[ξ] = ⟨ξ,u⟩⟨ξ,v⟩`` is quadratic.
    (ii) is certified syntactically by :func:`_hole_degree` == 1;
    anything it cannot certify is left alone (the rule simply does
    not fire).
    """

    anchor = IndexedSum

    def __init__(
        self,
        alg: Algebroid,
        fr: Frame,
        registry: Optional[PropertyRegistry] = None,
    ) -> None:
        if not isinstance(alg, Algebroid):
            raise TypeError(
                "CoframeRecombinationDefinition expects an Algebroid"
            )
        if not isinstance(fr, Frame):
            raise TypeError(
                "CoframeRecombinationDefinition expects a Frame"
            )
        self._alg = alg
        self.owner = alg
        self._frame = fr
        self._registry = registry
        self.name = (
            f"coframe recombination ({alg.name}, {fr.name}): "
            "Σ_s ρ(e_s)(f)·E(e^s) = E(Df)"
        )

    def _split(self, expr):
        if not isinstance(expr, IndexedSum):
            return None
        dummy = expr.dummy._repr_inner()
        body = expr.body
        sign = False
        if isinstance(body, Neg):
            sign = True
            body = body.arg
        factors = (
            list(body.children) if isinstance(body, Product) else [body]
        )
        for k, c in enumerate(factors):
            if not (
                isinstance(c, Act)
                and isinstance(c.op, AnchoredVF)
                and c.op.algebroid_name == self._alg.name
                and isinstance(c.op.section, FrameField)
                and c.op.section.base_name == self._frame.name
                and c.op.section.index == dummy
                and is_scalar_function(c.arg, self._registry)
            ):
                continue
            rest = factors[:k] + factors[k + 1 :]
            if not rest:
                continue
            if contains_index(c.arg, dummy):
                # f must be the same function for every s.
                continue
            coframe_atom = self._frame.dual().field(dummy)
            if not any(
                contains_index(r, dummy) for r in rest
            ):
                continue
            return sign, c.arg, rest, coframe_atom
        return None

    def matches(self, expr: Expr) -> bool:
        split = self._split(expr)
        if split is None:
            return False
        sign, f, rest, coframe_atom = split
        dummy = expr.dummy._repr_inner()
        substituted = [
            r.substitute_atom(coframe_atom, self._alg.D(f))
            for r in rest
        ]
        # (i) Sound only if the substitution consumed EVERY occurrence
        # of the bound index ...
        if any(contains_index(r, dummy) for r in substituted):
            return False
        # (ii) ... AND the remaining factors are C^∞-linear in e^s
        # (degree exactly 1 across the whole product).
        total = 0
        for r in rest:
            d = _hole_degree(r, coframe_atom)
            if d == _NONLINEAR:
                return False
            total += d
        return total == 1

    def rewrite(self, expr: Expr) -> Expr:
        sign, f, rest, coframe_atom = self._split(expr)
        substituted = [
            r.substitute_atom(coframe_atom, self._alg.D(f))
            for r in rest
        ]
        out: Expr = (
            substituted[0]
            if len(substituted) == 1
            else Product(*substituted)
        )
        return Neg(out) if sign else out


def modified_torsion(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    u: Expr,
    v: Expr,
    *,
    bound: str = "s",
) -> Expr:
    """``ᴸT(u,v) := T⁽⁰⁾(u,v) + Σ_s L(e^s, ∇_{e_s}u, v)``
    [MC Def 3.7 with the canonical representative]."""
    if fr.bundle != alg.bundle:
        raise ValueError(
            "the frame must live on the algebroid's bundle"
        )
    dummy = FrameIndex(bound)
    return Sum(
        torsion(conn, u, v),
        IndexedSum(
            dummy,
            fr,
            LocalityOperator(
                alg.name,
                fr.dual().field(bound),
                conn(fr.field(bound), u),
                v,
            ),
        ),
    )


def projected_curvature(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    bound: str = "s",
) -> Expr:
    """``ᴸ̂R(u,v,w) := R⁽⁰⁾(u,v)w + Σ_s ∇_{𝒫(L(e^s, ∇_{e_s}u, v))} w``
    [MC Def 3.11 / Cor 3.3]."""
    if not isinstance(projector, LocalityProjector):
        raise TypeError(
            "projected_curvature expects a LocalityProjector"
        )
    if fr.bundle != alg.bundle:
        raise ValueError(
            "the frame must live on the algebroid's bundle"
        )
    dummy = FrameIndex(bound)
    correction_body = Act(
        CovariantOp(
            conn.name,
            projector(
                LocalityOperator(
                    alg.name,
                    fr.dual().field(bound),
                    conn(fr.field(bound), u),
                    v,
                )
            ),
            bundle=conn.bundle,
        ),
        w,
    )
    return Sum(
        curvature(conn, u, v, w),
        IndexedSum(dummy, fr, correction_body),
    )


def _engine(
    alg: Algebroid,
    fr: Frame,
    registry,
    *,
    projectors=(),
):
    from jacopy.central.calculus.indexed_rules import (
        IndexedSumEvalPushInDefinition,
        IndexedSumLinearityDefinition,
        KroneckerContractionDefinition,
    )
    from jacopy.packages.metric_affine.decomposition import (
        IndexedSumOperatorPushDefinition,
    )
    from jacopy.packages.metric_affine.e_connection import (
        e_connection_engine,
    )

    engine = e_connection_engine(
        alg, registry=registry, projectors=projectors
    )
    engine.register(CoframeRecombinationDefinition(alg, fr, registry))
    engine.register(IndexedSumLinearityDefinition())
    engine.register(IndexedSumEvalPushInDefinition())
    engine.register(KroneckerContractionDefinition())
    engine.register(IndexedSumOperatorPushDefinition())
    return engine


def prove_modified_torsion_tensorial(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    u: Expr,
    v: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> tuple:
    """``ᴸT(f·u, v) = f·ᴸT(u, v)`` AND ``ᴸT(u, f·v) = f·ᴸT(u, v)`` —
    the modified torsion is a genuine tensor on a local algebroid
    [MC Prop 3.2/Def 3.7]: the recombined ``L(Df,u,v)`` cancels the
    pseudo defect."""
    first = ExpandAndSimplify().prove(
        modified_torsion(alg, conn, fr, Product(f, u), v),
        Product(f, modified_torsion(alg, conn, fr, u, v)),
        registry=registry,
        engine=_engine(alg, fr, registry),
    )
    second = ExpandAndSimplify().prove(
        modified_torsion(alg, conn, fr, u, Product(f, v)),
        Product(f, modified_torsion(alg, conn, fr, u, v)),
        registry=registry,
        engine=_engine(alg, fr, registry),
    )
    return first, second


def prove_projected_curvature_first_slot(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    u: Expr,
    v: Expr,
    w: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``ᴸ̂R(f·u, v, w) = f·ᴸ̂R(u, v, w)`` [MC Cor 3.3, first slot]:
    the recombined ``∇_{𝒫(L(Df,u,v))}w`` meets the projector's
    absorption rule (``L̂ ∈ [L̃]``) and cancels the pseudo defect."""
    return ExpandAndSimplify().prove(
        projected_curvature(
            alg, conn, fr, projector, Product(f, u), v, w
        ),
        Product(
            f, projected_curvature(alg, conn, fr, projector, u, v, w)
        ),
        registry=registry,
        engine=_engine(
            alg, fr, registry, projectors=(projector,)
        ),
    )


def prove_projected_curvature_last_slot(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    u: Expr,
    v: Expr,
    w: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``ᴸ̂R(u, v, f·w) = f·ᴸ̂R(u, v, w)`` [MC Prop 3.3-3.4 composed]:
    the ``R⁽⁰⁾`` part needs the anchor morphism, the correction's
    Leibniz term dies by the projector's KERNEL rule
    (``ρ(𝒫(L(…))) = 0`` — ``im(L̂) ⊂ ker ρ``)."""
    return ExpandAndSimplify().prove(
        projected_curvature(
            alg, conn, fr, projector, u, v, Product(f, w)
        ),
        Product(
            f, projected_curvature(alg, conn, fr, projector, u, v, w)
        ),
        registry=registry,
        engine=_engine(
            alg, fr, registry, projectors=(projector,)
        ),
    )


def generalized_ricci_anomaly(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    bound: str = "s",
) -> Expr:
    """``Σ_s [∇_{L(e^s,∇_{e_s}u,v)}w − ∇_{𝒫L(e^s,∇_{e_s}u,v)}w]`` —
    the ``(1−𝒫)``-anomaly of the generalized Ricci identity
    [ADM eq (3.36)]."""
    dummy = FrameIndex(bound)
    L_node = LocalityOperator(
        alg.name,
        fr.dual().field(bound),
        conn(fr.field(bound), u),
        v,
    )
    return IndexedSum(
        dummy,
        fr,
        Sum(
            Act(
                CovariantOp(conn.name, L_node, bundle=conn.bundle), w
            ),
            Neg(
                Act(
                    CovariantOp(
                        conn.name,
                        projector(L_node),
                        bundle=conn.bundle,
                    ),
                    w,
                )
            ),
        ),
    )


def prove_generalized_ricci_identity(
    alg: Algebroid,
    conn: Connection,
    fr: Frame,
    projector: LocalityProjector,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
):
    """[ADM Prop 3.8]: the generalized Ricci identity on a local
    algebroid, for an ARBITRARY E-connection (purely definitional —
    no declarations):

        ∇²_{u,v}w − ∇²_{v,u}w
          = ᴸ̂R(u,v,w) − ∇_{ᴸT(u,v)}w
            + Σ_s ∇_{(1−𝒫)L(e^s,∇_{e_s}u,v)}w,

    with ``∇²_{u,v}w := ∇_u∇_v w − ∇_{∇_u v}w`` the second covariant
    derivative. The ``(1−𝒫)`` anomaly is exactly the gap between the
    modified torsion's ``L``-correction and the projected
    curvature's ``𝒫L``-correction."""
    from jacopy.proof.strategies import ExpandAndSimplify

    def cov(direction: Expr, arg: Expr) -> Expr:
        return Act(
            CovariantOp(conn.name, direction, bundle=conn.bundle),
            arg,
        )

    lhs = Sum(
        conn(u, conn(v, w)),
        Neg(conn(v, conn(u, w))),
        Neg(cov(conn(u, v), w)),
        cov(conn(v, u), w),
    )
    rhs = Sum(
        projected_curvature(alg, conn, fr, projector, u, v, w),
        Neg(cov(modified_torsion(alg, conn, fr, u, v), w)),
        generalized_ricci_anomaly(
            alg, conn, fr, projector, u, v, w
        ),
    )
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=_engine(alg, fr, registry, projectors=(projector,)),
    )
