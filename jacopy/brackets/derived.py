"""
Derived bracket construction, the mathematical heart of the package.

Given a graded bracket ``[·, ·]`` on a graded module and a generator
``Q`` of odd (or appropriate) degree, the *derived bracket* is

    {a, b}_Q := [[a, Q], b]

which is automatically a graded Leibniz bracket regardless of any
conditions on ``Q``. Over a graded LIE base with an ODD (shifted)
generator, the condition

    [Q, Q] = 0

makes the derived bracket a LODAY (left-Leibniz-Jacobi) bracket
[Kosmann-Schwarzbach 1996 — year AMBIGUOUS: local sources list only "Derived brackets" (2004); docs/CITATIONS.md]. It is NOT automatically graded
antisymmetric, and the cyclic Lie-form Jacobi holds only where the
bracket is additionally skew (e.g. on suitable abelian subalgebras)
— the proof layer's :class:`DerivedBracketStrategy` checks exactly
these preconditions before certifying anything (2026-09-08 audit).
This conditionality is the point of the construction: Poisson,
Courant, and Koszul brackets arise as derived brackets of a
Schouten-type base, each Jacobi reducing to one equation on ``Q``
*on the slots where the extra hypotheses hold*.

The :class:`DerivedBracket` class captures this construction at the
algorithmic level:

* :meth:`expand` produces ``[[a, Q], b]`` using the base bracket's own
  :meth:`~jacopy.brackets.base.GradedBracket.expand` on each layer.
* :meth:`jacobi_obstruction` returns ``[Q, Q]_base``, the Expr whose
  vanishing is the remaining hypothesis for the derived bracket's
  Jacobi under the theorem's preconditions.
* :func:`derived_bracket` is a light factory helper.

The *Derived Bracket Theorem* itself — Loday Jacobi from a
vanishing obstruction under the stated preconditions — is registered
as a package-level theorem in
Phase 9 and consulted from the proof layer. This module only provides
the object; the theorem lives elsewhere so that each new
``DerivedBracket`` instance automatically inherits the result rather
than re-proving it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from jacopy.algebra.derivation import Act, Derivation, degree_of
from jacopy.algorithms.simplify import simplify
from jacopy.brackets.base import BracketApply, GradedBracket
from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree, DegreeLike, as_degree


LieDerivativeFactory = Callable[[Expr], Derivation]


@dataclass(frozen=True)
class VanishingCondition:
    """A proof-level claim of the form ``obstruction = 0``.

    A :class:`VanishingCondition` is the typed handle the proof layer
    consumes when a construction's correctness rests on a single
    equation. :meth:`DerivedBracket.jacobi_condition` returns one whose
    :attr:`obstruction` is ``[Q, Q]_base``: under the Derived Bracket
    Theorem's preconditions (graded-Lie base, odd shifted generator —
    plus per-slot skewness for the cyclic Lie form) its vanishing is
    the remaining hypothesis for Jacobi on ``{·, ·}_Q``, so passing
    the condition around is passing that hypothesis.

    The class is intentionally minimal, it is data, not a proof
    tactic. :meth:`holds` runs :func:`simplify` against the
    ``obstruction`` and reports whether the canonical form is the
    literal :class:`Integer` ``0``. Symbolic residues that the
    canonical pipeline can't settle return ``False`` even if the
    underlying math would eventually close them; the expectation is
    that the proof layer (e.g.
    :class:`jacopy.proof.strategies.DerivedBracketStrategy`) is the
    right tool for non-trivial discharges.
    """

    obstruction: Expr
    name: str = "vanishing condition"

    def holds(self, registry: Optional[PropertyRegistry] = None) -> bool:
        """True iff the obstruction simplifies to :class:`Integer` ``0``."""
        return simplify(self.obstruction, registry) == Integer(0)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name}: {self.obstruction._repr_inner()} = 0"


class DerivedBracket(GradedBracket):
    """``{a, b}_Q := [[a, Q]_base, b]_base``.

    Parameters
    ----------
    base
        The underlying graded bracket.
    Q
        The generator, an :class:`Expr` of degree ``degree_Q``.
    degree_Q
        The generator's degree, measured in the BASE bracket's grading
        (:meth:`~jacopy.brackets.base.GradedBracket.grading_degree`:
        multivector degree for SN, so ``|π| = 2``). When omitted it is
        DERIVED from ``Q`` through that hook; when ``Q``'s degree is
        not determinable without a registry it stays SYMBOLIC
        (``|Q|``), never a silent 0, so parity checks refuse. An
        explicit value contradicting a determinable degree raises
        :class:`ValueError`. The derived bracket's own degree is
        ``degree_Q + 2·k_base`` with ``k_base`` the base's degree in
        its own grading (``operand_shift``; −1 for SN), and −1 in
        ``acting_on`` (Koszul) mode.
    name
        Optional display name. Defaults to a structured tag derived
        from the base bracket and generator.
    acting_on
        Optional :class:`~jacopy.algebra.derivation.Derivation` that
        lifts operands into the domain of the base bracket. The
        canonical use is the Koszul bracket on 1-forms: with
        ``base=sn``, ``Q=π``, and ``acting_on=π^♯`` (an
        :class:`~jacopy.calculus.anchor.Anchor` or musical
        :class:`~jacopy.calculus.musical.Sharp`), :meth:`expand`
        emits the classical Koszul formula
        ``L_{ρa} b − L_{ρb} a − d⟨ρa, b⟩`` rather than the literal
        ``[[a, Q]_base, b]_base``. The literal form is unreachable
        when operands are 1-forms and the base bracket (SN) takes
        multivectors, the anchor bridges the two bundles.
    d, lie_derivative
        Cartan operators used *only* when ``acting_on`` is set. Default
        to the smooth-manifold singletons.
    """

    def __init__(
        self,
        base: GradedBracket,
        Q: Expr,
        *,
        degree_Q: Optional[DegreeLike] = None,
        name: Optional[str] = None,
        acting_on: Optional[Derivation] = None,
        d: Optional[Derivation] = None,
        lie_derivative: Optional[LieDerivativeFactory] = None,
    ) -> None:
        if not isinstance(base, GradedBracket):
            raise TypeError("DerivedBracket 'base' must be a GradedBracket")
        if not isinstance(Q, Expr):
            raise TypeError("DerivedBracket generator 'Q' must be an Expr")
        if acting_on is not None and not isinstance(acting_on, Derivation):
            raise TypeError(
                f"DerivedBracket acting_on must be a Derivation, "
                f"got {type(acting_on).__name__}"
            )
        self._base = base
        self._Q = Q
        try:
            q_deg = base.grading_degree(Q, None)
        except (ValueError, TypeError):
            q_deg = None
        if degree_Q is None:
            # derived from the base grading (review: DerivedBracket(SN,
            # π) must not need an explicit |π|). Undeterminable (needs a
            # registry, symbolic): a SYMBOLIC degree |Q| — never a silent
            # 0; every parity that depends on it is then undecidable and
            # refused (DerivedBracketStrategy, the obstructions)
            self._degree_Q = (
                q_deg if q_deg is not None
                else Degree.var(f"|{Q._repr_inner()}|")
            )
        else:
            self._degree_Q = as_degree(degree_Q)
        if (
            degree_Q is not None
            and q_deg is not None
            and q_deg.as_int() is not None
            and self._degree_Q.as_int() is not None
            and q_deg.as_int() != self._degree_Q.as_int()
        ):
            raise ValueError(
                f"DerivedBracket: degree_Q = {self._degree_Q!r} but the "
                f"generator {Q!r} has degree {q_deg!r} in the base "
                f"bracket's grading; degree_Q is measured there"
            )
        if (
            acting_on is not None
            and self._degree_Q.as_int() is not None
            and self._degree_Q.as_int() != 2
        ):
            raise ValueError(
                "DerivedBracket: acting_on (Koszul) mode is the bracket of "
                f"a BIVECTOR on 1-forms; the generator {Q!r} has degree "
                f"{self._degree_Q!r} in the base grading"
            )
        self._acting_on = acting_on
        # Cartan ops resolved lazily to avoid import-time cycles, only
        # used when acting_on is set.
        self._d_override = d
        self._lie_derivative_override = lie_derivative
        display = name or f"{{·,·}}_{Q._repr_inner()}"
        # Derived-bracket degree formula: |[[a,Q],b]| = |a| + |b| +
        # |Q| + 2·|base| — each base-bracket layer contributes its own
        # degree (2026-09-07 audit, finding 2: the previous
        # ``|Q| − 2`` hard-coded the Schouten-type base |base| = −1).
        # Graded Leibniz always holds; antisymmetry is NOT automatic
        # (a derived bracket is Loday, skew only on suitable slots —
        # 2026-09-08 re-audit, finding 2) and Jacobi is conditional
        # on [Q, Q]_base = 0 + the theorem's preconditions, checked
        # by the proof layer. Both surfaced as non-claims here.
        # The bracket's degree in its operands' grading (review D): the
        # base contributes its degree IN ITS OWN grading
        # (``operand_shift``: −1 for SN, so |{f, g}_π| = 0); in
        # acting_on (Koszul) mode the bracket on Ω(M) has degree −1
        # (two 1-forms give a 1-form).
        if acting_on is not None:
            own_degree = Degree.const(-1)
        else:
            k_b = base.operand_shift
            own_degree = self._degree_Q + k_b + k_b
        super().__init__(
            display,
            degree=own_degree,
            is_graded_antisymmetric=False,
            satisfies_leibniz=True,
            satisfies_graded_jacobi=None,
        )

    @property
    def base(self) -> GradedBracket:
        return self._base

    # ---- grading hooks (audit 0b00e1b K1-3 family) ----------------- #
    #
    # The derived bracket lives on the BASE's module: same grading,
    # same product. In that grading the base has degree
    # ``k_b = base.operand_shift`` and ``|[[a,Q],b]| = |a| + |b| + |Q|
    # + 2·k_b``, so the derived shift is ``|Q| + 2·k_b`` (``degree_Q``
    # is the generator's degree in the base's grading). For a base
    # whose grading is the operator grading this equals the recorded
    # ``degree``; for an SN base (k_b = −1, multivector grading) the
    # recorded ``degree`` (|Q| + 0) is not the right shift — the
    # hooks below are.

    #
    # In ``acting_on`` (Koszul) mode the operands are NOT elements of
    # the base module: they are forms, lifted by the anchor. There the
    # bracket is the Koszul bracket of the bivector ``Q`` on Ω(M) —
    # graded in the FORM degree (:func:`degree_of`) with degree −1
    # (``|[α, β]_π| = |α| + |β| − 1``: two 1-forms give a 1-form),
    # a derivation of ``∧``. So ``s(α) = |α| − 1``: on 1-forms
    # ``s = 0`` and the claimed sign is the plain antisymmetry ε = −1.

    def grading_degree(
        self, x: Expr, registry: Optional[PropertyRegistry] = None
    ) -> Degree:
        if self._acting_on is not None:
            return degree_of(x, registry)
        return self._base.grading_degree(x, registry)

    def generator_degree(
        self, registry: Optional[PropertyRegistry] = None
    ) -> Degree:
        """``|Q|`` in the base grading, VALIDATED against the registry
        (audit 0b00e1b K1-3 review #7): the degree the base's
        :meth:`grading_degree` determines for ``Q`` under ``registry``
        wins; a declared ``degree_Q`` that contradicts a determinable
        degree raises :class:`ValueError`; when the registry cannot
        determine it the declared value (possibly symbolic) stands."""
        try:
            q = self._base.grading_degree(self._Q, registry)
        except (ValueError, TypeError):
            q = None
        declared = self._degree_Q
        if q is None:
            return declared
        if (
            q.as_int() is not None
            and declared.as_int() is not None
            and q.as_int() != declared.as_int()
        ):
            raise ValueError(
                f"DerivedBracket: declared degree_Q = {declared!r} but the "
                f"generator {self._Q!r} has degree {q!r} in the base "
                "bracket's grading under this registry"
            )
        if q.as_int() is None and declared.as_int() is not None:
            return declared
        return q

    def operand_degree(
        self, x: Expr, registry: Optional[PropertyRegistry] = None
    ) -> Degree:
        """``s(x) = |x| + k`` with the derived shift ``k = |Q| + 2·k_base``
        taken from the registry-validated :meth:`generator_degree`
        (−1 in Koszul mode) — the ONE sign source of every claimed
        skew / Jacobi / Leibniz sign of this bracket."""
        if self._acting_on is not None:
            return self.grading_degree(x, registry) + Degree.const(-1)
        k_b = self._base.operand_shift
        return (
            self.grading_degree(x, registry)
            + self.generator_degree(registry) + k_b + k_b
        )

    def koszul_well_typed(
        self, a: Expr, b: Expr, registry: Optional[PropertyRegistry] = None
    ) -> bool:
        """Koszul (``acting_on``) mode is the bracket of a BIVECTOR
        ``Q`` on 1-FORMS (audit 0b00e1b K1-3 review #9): the anchor
        lift ``ρ(a)`` is a vector field and ``⟨b, ρ(a)⟩`` a pairing of
        a 1-form with it. ``True`` only when the registry-validated
        generator degree is ``2`` and both operands are certified
        1-forms by the one type source
        (:func:`~jacopy.central.objects.kind.kind_of`); anything else is
        ill-typed (default-reject)."""
        if self._acting_on is None:
            return False
        try:
            if self.generator_degree(registry).as_int() != 2:
                return False
        except ValueError:
            return False
        from jacopy.central.objects.kind import kind_of  # noqa: WPS433 - objects sit above brackets

        for x in (a, b):
            k = kind_of(x, registry)
            if k.kind != "form" or k.degree != Degree.const(1):
                return False
        return True

    def module_product(self, b: Expr, c: Expr) -> Expr:
        if self._acting_on is not None:
            from jacopy.core.wedge import Wedge

            return Wedge(b, c)
        return self._base.module_product(b, c)

    @property
    def Q(self) -> Expr:
        return self._Q

    @property
    def degree_Q(self) -> Degree:
        return self._degree_Q

    @property
    def acting_on(self) -> Optional[Derivation]:
        return self._acting_on

    # ---- core expansion -------------------------------------------- #

    def expand(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """``{a, b}_Q = [[a, Q]_base, b]_base`` (generic) or the
        anchor-lifted Koszul formula when ``acting_on`` is set.

        With ``acting_on=ρ``:
        ``{a, b}_{Q, ρ} = L_{ρa} b − L_{ρb} a − d⟨ρa, b⟩``,
        matching :class:`~jacopy.brackets.koszul.KoszulBracket(ρ)`,
        the structural equality is the content of the
        classical/derived equivalence theorem on Poisson manifolds.
        """
        if self._acting_on is not None:
            if not self.koszul_well_typed(a, b, registry):
                return BracketApply(self, a, b)  # ill-typed: stays inert
            return self._koszul_expand(a, b, registry)
        inner = self._base.expand(a, self._Q, registry)
        return self._base.expand(inner, b, registry)

    def _koszul_expand(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """Emit the Koszul 3-term formula via the anchor lift.

        Delegated out of :meth:`expand` to keep the default derived
        path clean. Cartan operators are resolved from the
        constructor overrides or from the smooth-manifold singletons;
        imports are deferred to avoid a top-level cycle between
        ``brackets`` and ``calculus``.
        """
        # v3 Cartan layer (the pre-reorg ``jacopy.calculus.*`` paths
        # died in the v3 reorg; 2026-09-07 audit, finding 7).
        from jacopy.central.tangent.exterior import CARTAN_TM, d as d_fn
        from jacopy.core.pairing import Pairing

        lie_factory = (
            self._lie_derivative_override
            if self._lie_derivative_override is not None
            else CARTAN_TM.lie
        )
        rho_a = Act(self._acting_on, a)
        rho_b = Act(self._acting_on, b)
        paired = Pairing(b, rho_a)
        d_term = (
            Act(self._d_override, paired)
            if self._d_override is not None
            else d_fn(paired)
        )
        return Sum(
            Act(lie_factory(rho_a), b),
            Neg(Act(lie_factory(rho_b), a)),
            Neg(d_term),
        )

    def leibniz_obstruction(
        self,
        a: Expr,
        b: Expr,
        c: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """As the base class — except in Koszul (``acting_on``) mode,
        where ``[a, b∧c]`` has a 2-form in its second slot and the
        anchor-lifted formula is defined on 1-forms only: the
        obstruction is ill-typed and REFUSED (:class:`ValueError`),
        never built with an undefined pairing (K1-3 review #9)."""
        if self._acting_on is not None:
            raise ValueError(
                f"{self.name}: the Koszul (acting_on) formula is defined on "
                "1-forms; the Leibniz obstruction [a, b∧c] needs a 2-form "
                "slot and is ill-typed in this mode"
            )
        return super().leibniz_obstruction(a, b, c, registry)

    def expand_definition(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """Return ``[[a, Q]_base, b]_base`` *before* base-expansion.

        Useful for proofs that want to show the derived definition
        literally, without collapsing the inner base-bracket nodes. The
        result is a :class:`BracketApply` of the base bracket applied
        to a base-bracket node.
        """
        inner = BracketApply(self._base, a, self._Q)
        return BracketApply(self._base, inner, b)

    # ---- Jacobi obstruction ---------------------------------------- #

    def jacobi_obstruction(
        self, registry: Optional[PropertyRegistry] = None
    ) -> Expr:
        """Return ``[Q, Q]_base``, the expression whose vanishing is
        the remaining hypothesis for the derived bracket's Jacobi.

        Under the Derived Bracket Theorem's PRECONDITIONS (graded-Lie
        base, odd shifted generator — and per-slot skewness for the
        cyclic Lie form, checked by the proof layer) the vanishing of
        this single expression yields Jacobi; without them it claims
        nothing (2026-09-08 audits).
        """
        return self._base.expand(self._Q, self._Q, registry)

    def jacobi_obstruction_raw(self) -> BracketApply:
        """Return the unexpanded ``[Q, Q]_base`` :class:`BracketApply`
        node, leaving the base-bracket shape intact for display or
        further pattern matching."""
        return BracketApply(self._base, self._Q, self._Q)

    def jacobi_condition(
        self, registry: Optional[PropertyRegistry] = None
    ) -> VanishingCondition:
        """Return the :class:`VanishingCondition` controlling Jacobi.

        The returned condition wraps ``[Q, Q]_base`` (expanded by the
        base bracket via :meth:`jacobi_obstruction`) together with a
        display name tied to this derived bracket. The proof layer's
        :class:`~jacopy.proof.strategies.DerivedBracketStrategy`
        consumes exactly this shape when it discharges Jacobi: one
        theorem step reduces triple-cyclic Jacobi to the
        condition's vanishing, then simplifies.
        """
        return VanishingCondition(
            obstruction=self.jacobi_obstruction(registry),
            name=f"Jacobi condition on {self.name}",
        )

    # ---- identity -------------------------------------------------- #

    def _identity_key(self) -> Any:
        # Extend the base key with the base-bracket reference, the
        # generator, and the generator's degree so that two derived
        # brackets with identical parameters compare equal and hash
        # alike. ``acting_on`` + Cartan overrides also participate,
        # two derived brackets with different anchors are distinct.
        return super()._identity_key() + (
            self._base,
            self._Q,
            self._degree_Q,
            self._acting_on,
            self._d_override,
            self._lie_derivative_override,
        )


# --------------------------------------------------------------------- #
# Factory                                                                #
# --------------------------------------------------------------------- #


def derived_bracket(
    base: GradedBracket,
    Q: Expr,
    *,
    degree_Q: Optional[DegreeLike] = None,
    name: Optional[str] = None,
) -> DerivedBracket:
    """Construct a :class:`DerivedBracket`, mirror of the class
    constructor with a friendlier functional name."""
    return DerivedBracket(base, Q, degree_Q=degree_Q, name=name)
