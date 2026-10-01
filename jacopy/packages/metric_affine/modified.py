"""
Modified E-torsion and projected E-curvature (Phase 4.E.2)
[MC Corollary 3.2, Definition 3.7, Propositions 3.3–3.4, Corollary 3.3,
Definition 3.11].

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

from jacopy.algebra.derivation import Act, Derivation
from jacopy.bibliography import cite
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
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.vector_field import VectorField
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
    CoboundaryForm,
    EMetric,
    LocalityOperator,
    MetricSharp,
)
from jacopy.central.algebroid.operators import MappedSection
from jacopy.central.algebroid.locality import LocalityProjector
from jacopy.packages.metric_affine.frame_components import ConnectionForm
from jacopy.packages.metric_affine.metric import MetricValue, NonMetricity
from jacopy.packages.metric_affine.torsion_curvature import (
    curvature,
    torsion,
)


#: Degree sentinel: the hole sits where the expression is NOT certified
#: ``C^∞``-linear in it.
_NONLINEAR = -1

#: A fresh atom, used only to detect a hole hidden inside an atom whose
#: ``substitute_atom`` reaches private state.
_HOLE_PROBE = Symbol("⟪coframe-recombination hole probe⟫")

# ---- the kind tables (the ONLY place classes are listed) ------------ #

#: Derivation subclasses that denote SECTIONS (values) when they stand
#: LAST in a product: every atom declaring the ``section_value``
#: protocol (a section of ``E``, ``L(α,u,v)`` [MC Def 3.5], ``Φ(u)``
#: for a bundle map ``Φ`` — the projector ``𝒫`` included — ``g⁻¹(ω)``,
#: ``[u,v]_E``, …) plus the TM vector fields (a :class:`VectorField`
#: is a section of its bundle; on TM it is not marked a section value
#: because it also acts on functions). Followed by another factor, any
#: Derivation (these included) is an operator acting on what follows.
def _is_section_value(e: Expr) -> bool:
    return isinstance(e, VectorField) or getattr(e, "section_value", False) is True


#: Declared tensor ATOMS without slots — sections of a tensor bundle by
#: definition: forms/tensors (coframe included), sections, ``Df``
#: (``⟨Df, hX⟩ = ρ(hX)f = h⟨Df, X⟩``) and the connection 1-form
#: ``ω^a_b(X) := ⟨e^a, ∇_X e_b⟩`` (``∇_{hX} = h∇_X``).
_TENSOR_ATOMS = (Form, Tensor, VectorField, CoboundaryForm, ConnectionForm)

#: Atoms ``C^∞``-multilinear in EVERY rewritable slot by definition:
#: ``g(u,v)`` on ``E`` and ``g(X,Y)`` (metric, a (0,2)-tensor);
#: ``Q(X,Y,Z) = X(g(Y,Z)) − g(∇_X Y,Z) − g(Y,∇_X Z) = (∇_X g)(Y,Z)``
#: (the ``X(h)`` terms cancel against Leibniz of ``∇``: a tensor);
#: ``L`` (trilinear [MC Def 3.5]); ``Φ`` / ``𝒫`` (bundle maps);
#: ``g⁻¹`` (bundle iso); ``ρ(X)`` as a vector-field value (bundle map).
_MULTILINEAR_SLOT_ATOMS = (
    EMetric,
    MetricValue,
    NonMetricity,
    LocalityOperator,
    MappedSection,
    MetricSharp,
    AnchoredVF,
)


def _is_operator(e: Expr) -> bool:
    """An operator even when it stands last: ``∇_X``, ``ρ(X)`` /
    ``ι_X`` / ``L_X`` / ``d`` or any other non-section derivation, a
    composition (``compose`` stores ``D1∘D2`` as a :class:`Product`),
    looking through ``Neg``/``Sum``/``Product``."""
    if isinstance(e, (Neg, Sum, Product)):
        return any(_is_operator(c) for c in e.children)
    return isinstance(e, Derivation) and not _is_section_value(e)


class _LinearityCertifier:
    """One post-order pass computing the degree of an expression in
    ``hole``: ``0`` (hole absent), ``1`` (CERTIFIED homogeneous
    ``C^∞``-linear) or :data:`_NONLINEAR`. Every (node, slot) pair has
    an explicit certificate below; anything else is NONLINEAR.

    Certificates (why ``E[h·ξ] = h·E[ξ]`` for a function ``h``):

    * ``Neg``: ``−`` is ``C^∞``-linear. ``Sum``: all summands the SAME
      degree (0/1 mixed is affine: ``Σ_s c_s(A + B[e^s]) ≠ A + B[Df]``).
    * ``Product`` is non-commutative and also stores compositions
      (see :meth:`product_degree`): the hole sits in one factor with
      only scalar functions to its left, and that factor is a scalar
      or stands last as a value (a non-scalar followed by another
      factor acts on it: ``D∘(hX) = h·D∘X + D(h)·X``). The recombined
      coefficient ``ρ(e_s)(f)`` may itself be pulled out only if every
      factor left of it is a scalar function.
    * ``Act(op, arg)``, hole in the operator only (``arg`` is where
      Leibniz lives, except for ``ι``):
        - ``∇_{hX}(·) = h·∇_X(·)``: the direction slot of a connection
          (also as the LEFTMOST factor of a composition,
          ``∇_{hX}∘D = h·∇_X∘D``; a later factor is not linear:
          ``∇_u∇_{hX}w = h∇_u∇_X w + ρ(u)(h)∇_X w``);
        - ``ρ(hX)(a) = h·ρ(X)(a)`` for a SCALAR ``a`` (compositions of
          vector fields keep it scalar); on a form ``ρ(X)`` would be
          a Lie derivative, not linear;
        - ``ι_{hX}μ = h·ι_Xμ`` only for a certified tensor ``μ``
          (``ι_{hX}(d_E μ)(v) = d_E μ(hX, v) ≠ h·d_E μ(X, v)`` for a
          non-skew bracket);
      hole in the argument: only ``ι_X(hμ) = h·ι_Xμ``.
    * ``⟨α, X⟩``, ``g(u, v)`` (:class:`EMetric` / :class:`MetricValue`,
      (0,2)-tensors), ``Q(X,Y,Z)`` (:class:`NonMetricity`) and
      ``H(X_1, …)`` (:class:`MultiEval`): bilinear/multilinear ONLY if
      every hole-free slot (the head included) is a certified tensor.
      ``⟨ι_u(d_E μ), hX⟩`` is not ``h⟨ι_u(d_E μ), X⟩``: by Palais,
      ``d_E μ(u, hX)`` contains ``μ([u, hX])``, and with a Courant/
      metric (Leibniz) bracket ``(d_E μ)(hX, v) − h(d_E μ)(X, v) =
      −⟨X,v⟩⟨μ, Dh⟩``; skewness of the bracket is not known locally.
    * ``L(α,u,v)`` (``C^∞``-trilinear by definition [MC Def 3.5]),
      ``Φ(u)`` (bundle map, 𝒫 included), ``g⁻¹(ω)`` (bundle iso),
      ``ρ(X)`` as a VALUE inside a slot (bundle map): sum of slot
      degrees ≤ 1, other slots certified tensors.
    * Any other node or atom carrying the hole → NONLINEAR.
    """

    def __init__(self, hole: Expr, registry) -> None:
        self._hole = hole
        self._reg = registry
        self._deg: dict = {}
        self._cert: dict = {}

    # ---- helpers --------------------------------------------------- #

    def _scalar(self, e: Expr) -> bool:
        return is_scalar_function(e, self._reg)

    def certified(self, e: Expr) -> bool:
        """``e`` (hole-free) is a genuine tensor field / function —
        built only from declared tensors, functions and tensorial
        operations."""
        key = id(e)
        if key in self._cert:
            return self._cert[key][1]
        out = self._certified(e)
        self._cert[key] = (e, out)
        return out

    def _certified(self, e: Expr) -> bool:
        if self._scalar(e):
            return True
        if isinstance(e, _TENSOR_ATOMS):
            return True
        if isinstance(e, _MULTILINEAR_SLOT_ATOMS):
            return all(self.certified(s) for s in e.rewritable_slots)
        if isinstance(e, (Neg, Sum)):
            return all(self.certified(c) for c in e.children)
        if isinstance(e, Product):
            *left, last = e.children
            return (
                all(self._scalar(c) for c in left)
                and not _is_operator(last)
                and self.certified(last)
            )
        if isinstance(e, Act) and isinstance(e.op, CovariantOp):
            # ∇ of a tensor is a tensor.
            return self.certified(e.op.vector) and self.certified(e.arg)
        if isinstance(e, Act) and isinstance(e.op, Interior):
            return self.certified(e.op.vector) and self.certified(e.arg)
        return False

    def _slots_degree(self, kids) -> int:
        """Multilinear node: at most one slot carries the hole, every
        other slot a certified tensor."""
        degs = [self.degree(k) for k in kids]
        if _NONLINEAR in degs or sum(degs) > 1:
            return _NONLINEAR
        if sum(degs) == 0:
            return 0
        if all(
            self.certified(k) for k, d in zip(kids, degs) if d == 0
        ):
            return 1
        return _NONLINEAR

    # ---- the pass -------------------------------------------------- #

    def degree(self, e: Expr) -> int:
        key = id(e)
        if key in self._deg:
            return self._deg[key][1]
        out = self._degree(e)
        self._deg[key] = (e, out)  # keep e alive: id() stays unique
        return out

    def _degree(self, e: Expr) -> int:
        if e == self._hole:
            return 1
        if isinstance(e, Neg):
            return self.degree(e.arg)
        if isinstance(e, Sum):
            degs = {self.degree(c) for c in e.children}
            return degs.pop() if len(degs) == 1 else _NONLINEAR
        if isinstance(e, Product):
            return self.product_degree(e.children)
        if isinstance(e, Act):
            return self._act_degree(e)
        if isinstance(e, (Pairing, MultiEval)):
            return self._slots_degree(e.children)
        if isinstance(e, _MULTILINEAR_SLOT_ATOMS):
            return self._slots_degree(tuple(e.rewritable_slots))
        # Unknown node / atom: fine only if the hole is absent.
        if e.children:
            degs = {self.degree(c) for c in e.children}
            return 0 if degs == {0} else _NONLINEAR
        if e.substitute_atom(self._hole, _HOLE_PROBE) == e:
            return 0
        return _NONLINEAR

    def product_degree(self, factors, coefficient: int = -1) -> int:
        """Degree of the (possibly non-commutative, composition-storing)
        product ``factors``. The hole sits in one factor ``j``:

        * every factor left of ``j`` is a scalar function (a Derivation
          there would act on the hole: ``D∘(hX) = hD∘X + D(h)X``);
        * factor ``j`` is a scalar, or it stands LAST and is a value
          (not an operator) — a non-scalar followed by another factor
          acts on it.

        ``coefficient`` is the index of ``ρ(e_s)(f)`` in the ORIGINAL
        factor list (−1: none). Pulling it out of the product is
        ``C^∞``-linear only if every factor left of it is a scalar
        function; otherwise it sits inside an operator's argument
        (``Σ_s ⟨e^s,v⟩·ρ(w)∘ρ(e_s)(f)`` loses the Leibniz term
        ``Σ_s ⟨e^s,v⟩·ρ(w)(ρ(e_s)f)``).
        """
        if coefficient >= 0 and not all(
            self._scalar(c) for c in factors[:coefficient]
        ):
            return _NONLINEAR
        degs = [
            0 if i == coefficient else self.degree(c)
            for i, c in enumerate(factors)
        ]
        if _NONLINEAR in degs or sum(degs) > 1:
            return _NONLINEAR
        if sum(degs) == 0:
            return 0
        j = degs.index(1)
        if not all(self._scalar(c) for c in factors[:j]):
            return _NONLINEAR
        hole_factor = factors[j]
        if self._scalar(hole_factor):
            return 1
        if j != len(factors) - 1 or _is_operator(hole_factor):
            return _NONLINEAR
        return 1

    def _act_degree(self, e: Act) -> int:
        op, arg = e.op, e.arg
        ops = list(op.children) if isinstance(op, Product) else [op]
        d_arg = self.degree(arg)
        d_ops = [
            self.degree(o.vector)
            if isinstance(o, (CovariantOp, Interior))
            else self.degree(o)
            for o in ops
        ]
        if _NONLINEAR in d_ops or d_arg == _NONLINEAR:
            return _NONLINEAR
        if sum(d_ops) + d_arg == 0:
            return 0
        if sum(d_ops) + d_arg > 1:
            return _NONLINEAR
        if d_arg == 1:
            # only ι_X(hμ) = h·ι_Xμ
            return 1 if len(ops) == 1 and isinstance(op, Interior) else _NONLINEAR
        if d_ops[0] != 1:
            return _NONLINEAR  # hole in a non-leftmost factor
        # d_ops[0] == 1 from here on: certify the leading operator's slot.
        lead = ops[0]
        if isinstance(lead, CovariantOp):
            return 1  # ∇_{hX}(·) = h·∇_X(·), whatever follows
        if isinstance(lead, AnchoredVF):
            # ρ(hX)(a) = h·ρ(X)(a) only on a scalar; a chain of vector
            # fields keeps a scalar a scalar.
            if all(
                isinstance(o, (AnchoredVF, VectorField)) for o in ops[1:]
            ) and self._scalar(arg):
                return 1
            return _NONLINEAR
        if isinstance(lead, Interior) and len(ops) == 1:
            # ι_{hX}μ = h·ι_Xμ only for a genuine tensor μ.
            return 1 if self.certified(arg) else _NONLINEAR
        return _NONLINEAR


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
    (ii) is certified syntactically by :class:`_LinearityCertifier`;
    anything it cannot certify is left alone (the rule simply does
    not fire).
    """

    anchor = IndexedSum
    source = cite("DereliDogan2020", "proof of Corollary 3.2")

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
            return sign, c.arg, rest, coframe_atom, factors, k
        return None

    def matches(self, expr: Expr) -> bool:
        split = self._split(expr)
        if split is None:
            return False
        sign, f, rest, coframe_atom, factors, k = split
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
        # Certified on the ORIGINAL factor list: the product is
        # non-commutative and stores compositions, so WHERE ρ(e_s)(f)
        # stands decides whether it may be pulled out at all.
        cert = _LinearityCertifier(coframe_atom, self._registry)
        return cert.product_degree(factors, coefficient=k) == 1

    def rewrite(self, expr: Expr) -> Expr:
        sign, f, rest, coframe_atom, _, _ = self._split(expr)
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
    engine.register(IndexedSumLinearityDefinition(registry))
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
    [MC Corollary 3.2 / Definition 3.7]: the recombined ``L(Df,u,v)`` cancels the
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
