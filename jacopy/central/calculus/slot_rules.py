"""
Structure-free slot-hygiene rules: pairing, wedge and sum laws as
ENGINE rules (they reach operator-atom slots, where the simplifier's
algorithm passes do not).

No calculus and no geometric structure enters these rules; they were
first written next to the package proofs that needed them and live
here so that every engine builder can reach them from the central
layer:

* :class:`PairingArgSplitDefinition` — ``⟨α, X+Y⟩ = ⟨α,X⟩ + ⟨α,Y⟩``
  (previously ``jacopy.packages.drinfeld.twist``);
* :class:`FormProductToWedgeDefinition` — ``α · β = α ∧ β``
  (previously ``jacopy.packages.drinfeld.twist``);
* :class:`WedgeSumScalarDefinition` — wedge Sum distribution and 0-form
  pull-out (previously ``jacopy.packages.drinfeld.twist``);
* :class:`WedgeZeroNegDefinition` — ``0∧α = 0``, ``(−α)∧β = −(α∧β)``
  (previously ``jacopy.packages.poisson.nambu``);
* :class:`TrivialZeroSumDefinition` — ``0 + (−0) + … = 0``
  (previously ``jacopy.packages.poisson.nambu``).

The class bodies are moved verbatim (their docstrings still name the
engine that first registered them — e.g. "scoped to the twist
engine": WHICH engines register them is unchanged); the old module
paths re-export the SAME class objects.
"""

from __future__ import annotations

from typing import Optional

from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.proof.expansion import Definition


class PairingArgSplitDefinition(Definition):
    """``⟨α, X + Y⟩ → ⟨α, X⟩ + ⟨α, Y⟩`` — pairing-argument
    additivity, SCOPED to the twist engine.

    The always-on engines deliberately leave pairing-argument sums to
    the COLLECTING pass (``collect_pairings``) because the
    citation-driven flows need the collected shape. Twist proofs are
    pure cancellation: both sides must reach one normal form, and the
    split direction is the terminating one here. Do not register this
    next to theorem-citation tactics."""

    name = "pairing argument additivity: ⟨α, X+Y⟩ = ⟨α,X⟩ + ⟨α,Y⟩"
    anchor = Pairing

    def matches(self, expr: Expr) -> bool:
        return isinstance(expr, Pairing) and isinstance(expr.X, Sum)

    def rewrite(self, expr: Expr) -> Expr:
        return Sum(
            *(Pairing(expr.alpha, t) for t in expr.X.children)
        )


class FormProductToWedgeDefinition(Definition):
    """``α · β → α ∧ β`` for a bare :class:`Product` with at least
    two determinable form-degree (≥ 1) factors — scoped to the twist
    engine (the head-position case is central
    :class:`HeadFormProductLiftDefinition`; here the shapes sit
    INSIDE sharp slots, where Leibniz splits leave ``d(f)·x``
    products). Scalar (degree-0) factors stay in front."""

    name = "form product is a wedge: α · β = α ∧ β (slot-reachable)"

    def __init__(
        self, registry: Optional[PropertyRegistry] = None
    ) -> None:
        from jacopy.core.expr import Product

        self._registry = registry
        self.anchor = Product

    def _split(self, expr: Expr):
        from jacopy.algebra.derivation import degree_of
        from jacopy.core.expr import Product

        if not (
            isinstance(expr, Product) and len(expr.children) >= 2
        ):
            return None
        scalars, formfs = [], []
        for c in expr.children:
            if hasattr(c, "wedge_degree"):
                return None
            try:
                k = degree_of(c, self._registry).as_int()
            except ValueError:
                return None
            if k is None:
                return None
            (scalars if k == 0 else formfs).append(c)
        if len(formfs) < 2:
            return None
        return scalars, formfs

    def matches(self, expr: Expr) -> bool:
        return self._split(expr) is not None

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.core.expr import Product
        from jacopy.core.wedge import Wedge

        scalars, formfs = self._split(expr)
        wedge = Wedge(*formfs)
        if not scalars:
            return wedge
        return Product(*scalars, wedge)


class WedgeSumScalarDefinition(Definition):
    """Wedge slot normalization, scoped to the twist engine: a
    ``Sum`` factor distributes (``α ∧ (x + y) = α∧x + α∧y``) and a
    degree-0 factor pulls out as a scalar coefficient (``α ∧ f =
    f·α`` — the wedge with a 0-form IS scalar multiplication). The
    algorithm passes do this in visible trees; inside sharp slots
    only Definitions fire."""

    name = "wedge normalization: Sum distributes, 0-forms pull out"

    def __init__(
        self, registry: Optional[PropertyRegistry] = None
    ) -> None:
        from jacopy.core.wedge import Wedge

        self._registry = registry
        self.anchor = Wedge

    def _site(self, expr: Expr):
        from jacopy.algebra.derivation import degree_of

        for i, c in enumerate(expr.children):
            if isinstance(c, Sum):
                return i, "sum"
            if hasattr(c, "wedge_degree"):
                continue
            try:
                k = degree_of(c, self._registry).as_int()
            except ValueError:
                continue
            if k == 0:
                return i, "scalar"
        return None

    def matches(self, expr: Expr) -> bool:
        from jacopy.core.wedge import Wedge

        return (
            isinstance(expr, Wedge)
            and len(expr.children) >= 2
            and self._site(expr) is not None
        )

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.core.expr import Product
        from jacopy.core.wedge import Wedge

        i, kind = self._site(expr)
        kids = list(expr.children)
        if kind == "sum":
            return Sum(
                *(
                    Wedge(*(kids[:i] + [t] + kids[i + 1 :]))
                    for t in kids[i].children
                )
            )
        scalar = kids[i]
        rest = kids[:i] + kids[i + 1 :]
        core = rest[0] if len(rest) == 1 else Wedge(*rest)
        return Product(scalar, core)


class WedgeZeroNegDefinition(Definition):
    """Slot-level wedge hygiene (engine rule — simplify passes cannot
    reach operator-atom slots): a zero factor kills the wedge, a Neg
    factor pulls out."""

    anchor = Wedge
    name = "wedge hygiene: 0∧α = 0, (−α)∧β = −(α∧β)"

    def matches(self, expr: Expr) -> bool:
        return isinstance(expr, Wedge) and any(
            c == Integer(0) or isinstance(c, Neg)
            for c in expr.children
        )

    def rewrite(self, expr: Expr) -> Expr:
        sign = False
        children = []
        for c in expr.children:
            while isinstance(c, Neg):
                sign = not sign
                c = c.arg
            if c == Integer(0):
                return Integer(0)
            children.append(c)
        core: Expr = (
            children[0] if len(children) == 1 else Wedge(*children)
        )
        return Neg(core) if sign else core


class TrivialZeroSumDefinition(Definition):
    """Slot-level sum hygiene: a Sum whose every term is ``0`` (up
    to Neg) collapses to ``0`` — simplify cannot reach operator-atom
    slots, the engine can."""

    anchor = Sum
    name = "sum hygiene: 0 + (−0) + … = 0"

    def matches(self, expr: Expr) -> bool:
        if not isinstance(expr, Sum):
            return False

        def is_zero(t: Expr) -> bool:
            while isinstance(t, Neg):
                t = t.arg
            return t == Integer(0)

        return all(is_zero(t) for t in expr.children)

    def rewrite(self, expr: Expr) -> Expr:
        return Integer(0)


__all__ = [
    "PairingArgSplitDefinition",
    "FormProductToWedgeDefinition",
    "WedgeSumScalarDefinition",
    "WedgeZeroNegDefinition",
    "TrivialZeroSumDefinition",
]
