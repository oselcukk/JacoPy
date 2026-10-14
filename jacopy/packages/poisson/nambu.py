"""
Nambu-Poisson structures and the higher Koszul bracket
— drinfeld paper
[arXiv:2312.06584 §6] eq (6.8).

A **Nambu-Poisson structure** of order ``p`` is a ``(p+1)``-vector
``Π`` (the fundamental identity is the DECLARED axiom).
Canonical definitions:

    (Πω)(f)      := Π(α₁, …, α_p, df)   for ω = α₁∧…∧α_p
                                         (the induced vector field),
    {f₁,…,f_p,g} := Π(df₁, …, df_p, dg)  (the Nambu bracket),
    [ω, η]_Π     := L_{Πω} η − ι_{Πη} dω  (the higher Koszul bracket
                                           on p-forms — Dorfman-type).

The bracket is built ENTIRELY from the existing TM Cartan machinery
(``L``, ``ι``, ``d``) plus the single new atom ``Πω``
(:class:`NambuSharpVF`, the SharpVF pattern at arity p).

Mechanical theorems (concrete ``p``; checked for p = 2 and p = 3):

* **p = 1 consistency**: for a bivector the Dorfman-type formula
  equals the Koszul bracket on 1-forms (via the magic formula —
  definitional, 26 steps).
* **right-Leibniz**: ``[ω, f·η]_Π = f·[ω,η]_Π + (Πω)(f)·η`` —
  the Leibniz-algebroid anchor property, declaration-free.
* **exact symmetric part**: ``[ω,η]_Π + [η,ω]_Π =
  d(ι_{Πω}η + ι_{Πη}ω)`` — the bracket is NOT antisymmetric for
  p ≥ 2 (Leibniz, not Lie), but its symmetric
  part is EXACT (the Dorfman pattern); at p = 1 the inner sum
  vanishes by alternation and antisymmetry is recovered.
"""

from __future__ import annotations

from typing import Any, Optional

from jacopy.algebra.derivation import Act, Derivation, degree_of
from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.core.wedge import Wedge
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.calculus.scalars import is_scalar_function
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.multivector import PVector
from jacopy.central.tangent.exterior import CARTAN_TM, d

# Structure-free rules, moved to the central layer; re-exported here
# so every existing import path keeps the SAME class objects.
from jacopy.central.calculus.slot_rules import (  # noqa: F401  (re-export)
    TrivialZeroSumDefinition,
    WedgeZeroNegDefinition,
)
from jacopy.central.tangent.cartan_rules import (  # noqa: F401  (re-export)
    DSquaredZeroDefinition,
    DWedgeLeibnizDefinition,
)


#: The declarable axioms of a Nambu-Poisson structure:
#: ``"fundamental-identity"`` — the Nambu fundamental identity (the
#: Poisson condition for ``p = 1``): ``[Πω, Πη] = Π[ω, η]_Kos`` and its
#: pairing-swap consequence. Nothing else is ever assumed.
NAMBU_DECLARATIONS = ("fundamental-identity",)


class NambuPoissonStructure:
    """``(M, Π)`` — a Nambu-Poisson structure of order ``p``
    (``Π`` a ``(p+1)``-vector). The fundamental identity is a DECLARED
    axiom carried BY THE STRUCTURE (``declare=(…)`` /
    :meth:`with_declarations`); a structure without it assumes
    nothing. Two structures with the same ``Π`` and different
    declarations are different owners (the weaker one is a
    sub-structure of the stronger one, see
    :func:`jacopy.proof.ownership.is_substructure`)."""

    __slots__ = ("_pi", "_p", "_declarations")

    def __init__(self, pi: PVector, *, declare=()) -> None:
        if not isinstance(pi, PVector):
            raise TypeError(
                "NambuPoissonStructure requires a PVector"
            )
        order = pi.degree.as_int() - 1
        if order < 1:
            raise ValueError(
                "a Nambu-Poisson structure needs a (p+1)-vector "
                "with p ≥ 1"
            )
        self._pi = pi
        self._p = order
        decl = frozenset(declare)
        unknown = sorted(decl - set(NAMBU_DECLARATIONS))
        if unknown:
            raise ValueError(f"unknown Nambu declaration(s) {unknown}; known: {NAMBU_DECLARATIONS}")
        self._declarations = decl

    @property
    def pi(self) -> PVector:
        return self._pi

    @property
    def p(self) -> int:
        """The form degree the bracket acts on."""
        return self._p

    @property
    def name(self) -> str:
        """The tree-visible name of the structure (its multivector)."""
        return self._pi._repr_inner()

    @property
    def declarations(self) -> frozenset:
        return self._declarations

    def declares(self, key: str) -> bool:
        return key in self._declarations

    def with_declarations(self, *declare: str) -> "NambuPoissonStructure":
        """The same structure with additional declared axioms."""
        return NambuPoissonStructure(self._pi, declare=tuple(self._declarations) + tuple(declare))

    def sharp_vf(self, omega: Expr) -> "NambuSharpVF":
        """``Πω`` — the induced vector field of a p-form."""
        return NambuSharpVF(self._pi, omega)

    # ---- structure provider ------------------------------------------- #

    def engine_rules(self, registry=None, *, phase=None):
        """The rules THIS structure contributes to an engine, each
        owned by the structure and keyed by ``(class, Π)``:

        * phase ``"sharp"`` — the definitional sharp rules (action,
          linearity);
        * phase ``"pairing"`` — the sharp pairing evaluation;
        * phase ``"declared"`` — the fundamental-identity rules, ONLY
          when the structure declares ``"fundamental-identity"``.

        ``phase=None`` returns all three in that order. Structure-free
        rules (the Cartan base, wedge/slot laws) are not the
        structure's business — the engine builders add them once."""
        from jacopy.packages.drinfeld.tilde_calculus import (
            FISharpPairingSwapDefinition,
            NambuMorphismDeclaration,
            NambuSharpPairingEvalDefinition,
        )

        groups = {
            "sharp": lambda: [NambuSharpActionDefinition(self, registry), NambuSharpLinearityDefinition(self, registry)],
            "pairing": lambda: [NambuSharpPairingEvalDefinition(self, registry)],
            "declared": lambda: (
                [NambuMorphismDeclaration(self), FISharpPairingSwapDefinition(self)]
                if self.declares("fundamental-identity") else []
            ),
        }
        if phase is not None and phase not in groups:
            raise ValueError(f"unknown phase {phase!r}; known: {tuple(groups)}")
        out = []
        for ph in ([phase] if phase is not None else list(groups)):
            for rule in groups[ph]():
                rule.owner = self
                rule.identity = (type(rule).__name__, self.name)
                out.append(rule)
        return out

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NambuPoissonStructure)
            and self._pi == other._pi
            and self._declarations == other._declarations
        )

    def __hash__(self) -> int:
        return hash(("nambu-structure", self._pi, self._declarations))

    def __repr__(self) -> str:
        decl = f", declare={sorted(self._declarations)}" if self._declarations else ""
        return f"NambuPoissonStructure({self._pi!r}, p={self._p}{decl})"


def nambu_structure(
    name: str = "Π", *, p: int = 2, declare=()
) -> NambuPoissonStructure:
    """Create a Nambu-Poisson structure with a fresh
    ``(p+1)``-vector; ``declare=("fundamental-identity",)`` opts into
    the fundamental identity as the structure's own assumption."""
    return NambuPoissonStructure(PVector(name, degree=p + 1), declare=declare)


class NambuSharpVF(Derivation):
    """``Πω`` — the vector field induced by contracting the
    ``(p+1)``-vector with a p-form (degree-0 derivation, wedge
    degree 1 — the SharpVF pattern at arity p)."""

    __slots__ = ("_pi", "_omega")

    def __init__(
        self, pi: PVector, omega: Expr, *, name: Optional[str] = None
    ) -> None:
        if not isinstance(pi, PVector):
            raise TypeError("NambuSharpVF requires a PVector")
        if not isinstance(omega, Expr):
            raise TypeError("NambuSharpVF requires an Expr form")
        display = (
            name
            if name is not None
            else f"{pi._repr_inner()}({omega._repr_inner()})"
        )
        super().__init__(display, degree=0)
        self._pi = pi
        self._omega = omega

    @property
    def pi(self) -> PVector:
        return self._pi

    @property
    def omega(self) -> Expr:
        return self._omega

    @property
    def wedge_degree(self) -> Degree:
        return Degree.const(1)

    @property
    def rewritable_slots(self):
        return (self._omega,)

    def with_slots(self, omega: Expr) -> "NambuSharpVF":
        return NambuSharpVF(self._pi, omega)

    def _key(self) -> Any:
        return (self._name, self._degree, self._pi, self._omega)


class NambuSharpActionDefinition(Definition):
    """``(Πω)(f) → Π(α₁,…,α_p, df)`` when ``ω = α₁∧…∧α_p``
    decomposes into determinable 1-form factors (a single 1-form at
    p = 1). Opaque p-forms stay INERT — honest: the contraction of
    an atomic ``Π`` with an atomic p-form has nothing to expand
    into."""

    anchor = Act

    def __init__(
        self,
        structure: NambuPoissonStructure,
        registry: Optional[PropertyRegistry] = None,
    ) -> None:
        self._N = structure
        self._registry = registry
        self.name = (
            f"Nambu sharp action ({structure.pi._repr_inner()}): "
            "(Πω)(f) = Π(α₁,…,α_p, df) on decomposable ω"
        )

    def _legs(self, omega: Expr):
        p = self._N.p
        if p == 1:
            factors = [omega]
        elif isinstance(omega, Wedge) and len(omega.children) == p:
            factors = list(omega.children)
        else:
            return None
        for leg in factors:
            try:
                if degree_of(leg, self._registry) != Degree.const(1):
                    return None
            except ValueError:
                return None
        return factors

    def matches(self, expr: Expr) -> bool:
        return (
            isinstance(expr, Act)
            and isinstance(expr.op, NambuSharpVF)
            and expr.op.pi == self._N.pi
            and self._legs(expr.op.omega) is not None
        )

    def rewrite(self, expr: Expr) -> Expr:
        legs = self._legs(expr.op.omega)
        return MultiEval(
            self._N.pi,
            *legs,
            d(expr.arg),
            alternating=True,
            slot_kind="covector",
        )


class NambuSharpLinearityDefinition(Definition):
    """ℝ/C∞-structure of ``Πω`` in the form slot: sums, negations,
    zeros and certainly-scalar factors pull out (the contraction is
    tensorial — the SharpVFLinearity pattern)."""

    anchor = NambuSharpVF

    def __init__(
        self,
        structure: NambuPoissonStructure,
        registry: Optional[PropertyRegistry] = None,
    ) -> None:
        self._N = structure
        self._registry = registry
        self.name = (
            "Nambu sharp linearity: Π(fω + η) = f·Πω + Πη"
        )

    def _scalar_split(self, a: Expr):
        """``(scalars, core)`` — pull ALL certainly-scalar factors
        out of a Product slot, whatever their position (scalars are
        central: degree-0 factors commute with everything, so the
        split is value-preserving)."""
        from jacopy.core.expr import Product

        if not (
            isinstance(a, Product) and len(a.children) >= 2
        ):
            return None
        scalars = [
            c
            for c in a.children
            if is_scalar_function(c, self._registry)
        ]
        if not scalars or len(scalars) == len(a.children):
            return None
        rest = [
            c
            for c in a.children
            if not is_scalar_function(c, self._registry)
        ]
        core = rest[0] if len(rest) == 1 else Product(*rest)
        return scalars, core

    def matches(self, expr: Expr) -> bool:
        if not (
            isinstance(expr, NambuSharpVF)
            and expr.pi == self._N.pi
        ):
            return False
        a = expr.omega
        if isinstance(a, (Sum, Neg)) or a == Integer(0):
            return True
        return self._scalar_split(a) is not None

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.core.expr import Product

        a = expr.omega
        if a == Integer(0):
            return Integer(0)
        if isinstance(a, Sum):
            return Sum(*(expr.with_slots(c) for c in a.children))
        if isinstance(a, Neg):
            return Neg(expr.with_slots(a.arg))
        scalars, core = self._scalar_split(a)
        return Product(*scalars, expr.with_slots(core))


def nambu_koszul_bracket(
    N: NambuPoissonStructure, omega: Expr, eta: Expr
) -> Expr:
    """``[ω, η]_Π := L_{Πω} η − ι_{Πη} dω`` — the higher Koszul
    bracket on p-forms (Dorfman-type; a Leibniz-algebroid bracket,
    NOT antisymmetric for p ≥ 2)."""
    return Sum(
        Act(CARTAN_TM.lie(N.sharp_vf(omega)), eta),
        Neg(Act(Interior(N.sharp_vf(eta)), d(omega))),
    )


def nambu_engine(
    N: NambuPoissonStructure,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ExpansionEngine:
    """The tangent engine + the Nambu sharp rules."""
    from jacopy.central.calculus import (
        HeadScalarDefinition,
        MultiEvalArgLinearityDefinition,
    )
    from jacopy.central.calculus.indexed_rules import (
        WedgeEvalDefinition,
    )
    from jacopy.central.tangent.tangent_expansion import tangent_engine
    from jacopy.central.tangent.lie_bracket import (
        LieBracketLeibnizDefinition,
    )

    engine = tangent_engine(registry=registry)
    for rule in N.engine_rules(registry, phase="sharp"):
        engine.register(rule)
    engine.register(HeadScalarDefinition(registry))
    engine.register(MultiEvalArgLinearityDefinition(registry))
    engine.register(WedgeEvalDefinition(registry))
    engine.register(DSquaredZeroDefinition())
    engine.register(DWedgeLeibnizDefinition(registry))
    engine.register(WedgeZeroNegDefinition())
    engine.register(TrivialZeroSumDefinition())
    engine.register(LieBracketLeibnizDefinition(registry))
    return engine


# --------------------------------------------------------------------- #
# Theorems                                                               #
# --------------------------------------------------------------------- #


def _ev(expr: Expr, slots) -> Expr:
    from jacopy.core.pairing import Pairing

    if len(slots) == 1:
        return Pairing(expr, slots[0])
    return MultiEval(
        expr, *slots, alternating=True, slot_kind="vector"
    )


def prove_nambu_right_leibniz(
    N: NambuPoissonStructure,
    omega: Expr,
    eta: Expr,
    f: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``[ω, f·η]_Π = f·[ω,η]_Π + (Πω)(f)·η`` evaluated on the given
    vector slots — the Leibniz-algebroid anchor property of ``Πω``,
    declaration-free."""
    from jacopy.core.expr import Product

    lhs = _ev(
        nambu_koszul_bracket(N, omega, Product(f, eta)), slots
    )
    rhs = _ev(
        Sum(
            Product(f, nambu_koszul_bracket(N, omega, eta)),
            Product(Act(N.sharp_vf(omega), f), eta),
        ),
        slots,
    )
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=nambu_engine(N, registry=registry),
    )


def prove_nambu_symmetric_part_exact(
    N: NambuPoissonStructure,
    omega: Expr,
    eta: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``[ω,η]_Π + [η,ω]_Π = d(ι_{Πω}η + ι_{Πη}ω)`` — the symmetric
    part is EXACT (Dorfman pattern; via the magic formula,
    declaration-free). For p ≥ 2 the right side is genuinely nonzero
    (Leibniz, not Lie); at p = 1 it vanishes by alternation."""
    lhs = _ev(
        Sum(
            nambu_koszul_bracket(N, omega, eta),
            nambu_koszul_bracket(N, eta, omega),
        ),
        slots,
    )
    rhs = _ev(
        d(
            Sum(
                Act(Interior(N.sharp_vf(omega)), eta),
                Act(Interior(N.sharp_vf(eta)), omega),
            )
        ),
        slots,
    )
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=nambu_engine(N, registry=registry),
    )


def prove_dorfman_form_reduces_to_koszul_at_p1(
    P,
    alpha: Expr,
    beta: Expr,
    Y: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """p = 1 consistency: for a Poisson bivector the Dorfman-type
    formula equals the Koszul bracket on 1-forms,
    ``⟨L_{π♯α}β − ι_{π♯β}dα, Y⟩ = ⟨[α,β]_π, Y⟩`` (via the magic
    formula — definitional)."""
    from jacopy.core.pairing import Pairing
    from jacopy.packages.poisson.core import SharpVF
    from jacopy.packages.poisson.koszul_forms import koszul_bracket
    from jacopy.packages.poisson.showcase import showcase_engine

    lhs = Sum(
        Pairing(
            Act(CARTAN_TM.lie(SharpVF(P.pi, alpha)), beta), Y
        ),
        Neg(
            Pairing(
                Act(Interior(SharpVF(P.pi, beta)), d(alpha)), Y
            )
        ),
    )
    rhs = Pairing(koszul_bracket(P, alpha, beta), Y)
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=showcase_engine(
            P, registry=registry, declare_poisson=False
        ),
    )


class NambuFIDeclaration(Definition):
    """The DECLARED fundamental identity, in its bracket-morphism
    face on exact generators [DD (6.9), arXiv:2312.06584: the R-twist
    ``[Πω,Πη] − Π[ω,η]``; that it vanishes iff ``Π`` is Nambu-Poisson
    is the remark after DD (6.13), citing their ref. [122]]:

        (Π(L_{Πω} η))(h) → (Πω)(Πη(h)) − (Πη)(Πω(h))

    for ``ω, η`` wedges of EXACT 1-forms (where ``dω = 0`` collapses
    the bracket to its ``L``-piece, so ``L_{Πω}η = [ω,η]_Π``).
    Expansion direction: the output is nested sharp actions, which
    the action rule turns into nested Nambu brackets — no ``L``-slot
    sharp survives, so the rewrite terminates."""

    role = "assumption"  # a declared axiom, not a definition

    anchor = Act

    def __init__(
        self,
        structure: NambuPoissonStructure,
        registry: Optional[PropertyRegistry] = None,
    ) -> None:
        self._N = structure
        self._registry = registry
        self.name = (
            f"declared Nambu FI ({structure.pi._repr_inner()}): "
            "Π(L_{Πω}η) = [Πω, Πη] on exact generators"
        )

    def _exact_wedge(self, omega: Expr) -> bool:
        from jacopy.packages.poisson.showcase import is_exact_form

        p = self._N.p
        if p == 1:
            return is_exact_form(omega)
        return (
            isinstance(omega, Wedge)
            and len(omega.children) == p
            and all(is_exact_form(c) for c in omega.children)
        )

    def _split(self, expr: Expr):
        from jacopy.central.calculus.bracket_calculus import (
            LieDerivative,
            belongs_to,
        )

        if not (
            isinstance(expr, Act)
            and isinstance(expr.op, NambuSharpVF)
            and expr.op.pi == self._N.pi
        ):
            return None
        w = expr.op.omega
        # the FI is a statement about the ORDINARY Lie derivative
        # L^{TM}; the L of another calculus in the same direction is a
        # different operator (e.g. a zero-anchor,
        # zero-bracket B has L^B η = 0 while [Πω, Πη](h) ≠ 0)
        if not (
            isinstance(w, Act)
            and isinstance(w.op, LieDerivative)
            and belongs_to(w.op, CARTAN_TM)
        ):
            return None
        inner_vf = w.op.vector
        if not (
            isinstance(inner_vf, NambuSharpVF)
            and inner_vf.pi == self._N.pi
        ):
            return None
        omega1 = inner_vf.omega
        omega2 = w.arg
        if not (
            self._exact_wedge(omega1) and self._exact_wedge(omega2)
        ):
            return None
        return omega1, omega2, expr.arg

    def matches(self, expr: Expr) -> bool:
        return self._split(expr) is not None

    def rewrite(self, expr: Expr) -> Expr:
        omega1, omega2, h = self._split(expr)
        X1 = NambuSharpVF(self._N.pi, omega1)
        X2 = NambuSharpVF(self._N.pi, omega2)
        return Sum(
            Act(X1, Act(X2, h)), Neg(Act(X2, Act(X1, h)))
        )


def prove_nambu_leibniz_jacobi_on_exacts(
    N: NambuPoissonStructure,
    F,
    G,
    H,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    declare_fi: bool = True,
    max_steps: int = 20000,
) -> ProofChain:
    """The Leibniz-Jacobi identity of the higher
    Koszul bracket on EXACT wedge generators
    (``ω = dF₁∧…∧dF_p`` etc.), under the DECLARED fundamental
    identity:

        [ω, [η, μ]_Π]_Π = [[ω, η]_Π, μ]_Π + [η, [ω, μ]_Π]_Π.

    ``F, G, H`` are p-tuples of functions; honest fail without the
    FI declaration (tested)."""
    def wedge_of(fs):
        legs = [d(f) for f in fs]
        return legs[0] if len(legs) == 1 else Wedge(*legs)

    om, et, mu = wedge_of(F), wedge_of(G), wedge_of(H)
    lhs = _ev(
        nambu_koszul_bracket(
            N, om, nambu_koszul_bracket(N, et, mu)
        ),
        slots,
    )
    rhs = _ev(
        Sum(
            nambu_koszul_bracket(
                N, nambu_koszul_bracket(N, om, et), mu
            ),
            nambu_koszul_bracket(
                N, et, nambu_koszul_bracket(N, om, mu)
            ),
        ),
        slots,
    )
    engine = nambu_engine(N, registry=registry)
    if declare_fi:
        engine.register(NambuFIDeclaration(N, registry))
    return ExpandAndSimplify().prove(
        lhs,
        rhs,
        registry=registry,
        engine=engine,
        max_steps=max_steps,
    )


# ------------------------------------------------------------------- #
# Dialect bridge: the order-1 Nambu sharp IS the Poisson sharp         #
# ------------------------------------------------------------------- #


def poisson_view(structure: NambuPoissonStructure):
    """The order-1 Nambu structure read as a
    :class:`~jacopy.packages.poisson.core.PoissonStructure` on the
    SAME bivector (so Poisson-package theorems — the general Koszul
    Jacobi theorem, the tilde calculus — can be cited against
    Nambu-dialect expressions through
    :class:`NambuToPoissonSharpDefinition`)."""
    from jacopy.packages.poisson.core import PoissonStructure

    if structure.p != 1:
        raise ValueError(
            "only an order-1 Nambu structure (a bivector) has a "
            "Poisson view"
        )
    return PoissonStructure(structure.pi)


class NambuToPoissonSharpDefinition(Definition):
    """THE DIALECT BRIDGE: at p = 1 the Nambu sharp node
    ``Π(ω)`` and the Poisson sharp node ``π♯(ω)`` denote the same
    vector field ``θ♯ω`` (both act as ``f ↦ −θ(df, ω) = θ(ω, df)``);
    the two packages grew separate node families (Nambu:
    ``NambuSharpVF`` + the ``ℒ_{Πω}η − ι_{Πη}dω`` Koszul formula;
    Poisson: ``SharpVF`` + the ``KoszulBracket`` atom). This rule
    rewrites the Nambu node into the Poisson node, so Poisson-dialect
    theorems can be cited on Nambu-dialect expressions:

        Π(ω) → π♯(ω)      (same bivector, p = 1 only)."""

    anchor = NambuSharpVF

    def __init__(self, structure: NambuPoissonStructure) -> None:
        if structure.p != 1:
            raise ValueError("the dialect bridge is a p = 1 statement")
        self._N = structure
        self.name = (
            f"dialect bridge ({structure.pi._repr_inner()}): "
            "Nambu sharp Π(ω) → Poisson sharp π♯(ω)"
        )

    def matches(self, expr: Expr) -> bool:
        return isinstance(expr, NambuSharpVF) and expr.pi == self._N.pi

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.packages.poisson.core import SharpVF

        return SharpVF(expr.pi, expr.omega)
