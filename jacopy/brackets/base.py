"""
Graded bracket framework.

A graded bracket is a bilinear operation ``[·, ·]`` on a graded module.
Each bracket carries:

* a ``degree``, shifts total grade by this amount: ``|[a, b]| = |a| + |b| + degree``.
* ``is_graded_antisymmetric``, whether ``[a, b] = −(−1)^{s(a)s(b)} [b, a]`` holds.
* ``satisfies_leibniz``, whether ``[a, b*c] = [a, b]*c + (−1)^{s(a)|b|} b*[a, c]`` holds.
* ``satisfies_graded_jacobi``, whether the graded Jacobi identity holds
  (``True``, ``False``, or ``None`` for *conditional* brackets like the
  derived bracket, whose Jacobi is controlled by a separate condition).

Here ``s(x) = |x| + degree`` is the SHIFTED degree
(:meth:`GradedBracket.operand_degree`) and ``|·|`` the module's own
grading (:meth:`GradedBracket.grading_degree`: the operator grading by
default, the multivector grading for Schouten–Nijenhuis, where
``s = m − 1``). For a degree-0 bracket in the operator grading these
are the plain ``|a||b|`` signs.

Brackets are *not* Exprs: they are Python-level operators. Applying a
bracket to two Exprs builds an inert :class:`BracketApply` node in the
expression tree, analogous to :class:`jacopy.algebra.derivation.Act`.
The expansion (turning the opaque ``B(a, b)`` node into its defining
formula) is done by :meth:`GradedBracket.expand`, which subclasses
implement.

The module also exposes *axiom obstruction* helpers. These return the
Expr that the corresponding axiom claims is zero, feed it to
``simplify`` / ``canonicalize`` to check the axiom on concrete inputs.
Mutating the tree to ``0`` is the certificate that the axiom holds;
leaving a non-trivial remainder exposes the counterexample.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from jacopy.algebra.derivation import degree_of
from jacopy.core.expr import Expr, Neg, Product, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree, DegreeLike, as_degree


# --------------------------------------------------------------------- #
# Application node                                                       #
# --------------------------------------------------------------------- #


class BracketApply(Expr):
    """Inert application of a bracket: ``B(a, b)``.

    Carries a reference to the :class:`GradedBracket` instance so the
    :func:`expand_bracket` algorithm (and :meth:`expand`) can delegate
    back to the bracket's expansion rule. The bracket itself is not an
    Expr, treating it as such would invite accidental structural
    comparisons between two different brackets that happen to share a
    name or degree.
    """

    __slots__ = ("_bracket", "_a", "_b")

    def __init__(
        self, bracket: "GradedBracket", a: Expr, b: Expr
    ) -> None:
        if not isinstance(bracket, GradedBracket):
            raise TypeError("BracketApply requires a GradedBracket instance")
        if not isinstance(a, Expr):
            raise TypeError("BracketApply left operand must be an Expr")
        if not isinstance(b, Expr):
            raise TypeError("BracketApply right operand must be an Expr")
        self._bracket = bracket
        self._a = a
        self._b = b

    @property
    def bracket(self) -> "GradedBracket":
        return self._bracket

    @property
    def a(self) -> Expr:
        return self._a

    @property
    def b(self) -> Expr:
        return self._b

    @property
    def children(self) -> Tuple[Expr, ...]:
        # The bracket reference is not a child, children are Expr
        # operands only. Tree walks (walk, find, pattern match) see a
        # binary node.
        return (self._a, self._b)

    def _rebuild(self, new_children: Tuple[Expr, ...]) -> Expr:
        # Default ``type(self)(*children)`` would drop the bracket
        # reference, since it lives outside the children tuple.
        if len(new_children) != 2:
            raise ValueError(
                "BracketApply._rebuild expects exactly 2 children "
                f"(a, b), got {len(new_children)}"
            )
        a, b = new_children
        return BracketApply(self._bracket, a, b)

    def _key(self) -> Any:
        return (self._bracket, self._a, self._b)

    def _repr_inner(self) -> str:
        return (
            f"{self._bracket.name}"
            f"({self._a._repr_inner()}, {self._b._repr_inner()})"
        )

    def expand(self, registry: Optional[PropertyRegistry] = None) -> Expr:
        """Defer to the bracket's expansion rule."""
        return self._bracket.expand(self._a, self._b, registry)


# --------------------------------------------------------------------- #
# Base class                                                             #
# --------------------------------------------------------------------- #


class GradedBracket(ABC):
    """Abstract graded bracket on a graded module.

    Subclasses declare their degree and axiom flags via ``__init__`` and
    implement :meth:`expand`. The default axiom flags reflect the most
    common case (degree 0, antisymmetric, Leibniz, Jacobi holds); override
    in subclasses for anything exotic.
    """

    def __init__(
        self,
        name: str,
        *,
        degree: DegreeLike = 0,
        is_graded_antisymmetric: bool = True,
        satisfies_leibniz: bool = True,
        satisfies_graded_jacobi: Optional[bool] = True,
    ) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("Bracket name must be a non-empty string")
        self._name = name
        self._degree = as_degree(degree)
        self._is_graded_antisymmetric = bool(is_graded_antisymmetric)
        self._satisfies_leibniz = bool(satisfies_leibniz)
        # None is allowed: conditional Jacobi (e.g. derived bracket).
        if satisfies_graded_jacobi is not None:
            satisfies_graded_jacobi = bool(satisfies_graded_jacobi)
        self._satisfies_graded_jacobi = satisfies_graded_jacobi

    # ---- read-only accessors --------------------------------------- #

    @property
    def name(self) -> str:
        return self._name

    @property
    def degree(self) -> Degree:
        return self._degree

    @property
    def is_graded_antisymmetric(self) -> bool:
        return self._is_graded_antisymmetric

    @property
    def satisfies_leibniz(self) -> bool:
        return self._satisfies_leibniz

    @property
    def satisfies_graded_jacobi(self) -> Optional[bool]:
        """True / False / None (conditional)."""
        return self._satisfies_graded_jacobi

    # ---- application ----------------------------------------------- #

    def __call__(self, a: Expr, b: Expr) -> BracketApply:
        return BracketApply(self, a, b)

    # ---- grading hooks (the ONE sign source of the obstructions) --- #
    #
    # A degree-``k`` bracket on a graded module ``A`` is a graded Lie
    # bracket on the SHIFTED module ``A[k]``: its antisymmetry and
    # Jacobi signs use the shifted degree ``s(x) = |x| + k``, while
    # its Leibniz sign over the module product pairs ``s(a)`` with the
    # UNSHIFTED ``|b|`` of the factor it passes. Which grading ``|·|``
    # is meant is the bracket's business: the operator grading
    # (:func:`degree_of`) by default, the MULTIVECTOR grading for
    # Schouten–Nijenhuis (whose vector fields have operator degree 0
    # but multivector degree 1 — audit 0b00e1b K1-3: the obstructions
    # used the operator degree and claimed ``[π, π]_SN = 0`` for every
    # bivector). Subclasses override :meth:`grading_degree` /
    # :meth:`operand_degree` / :meth:`module_product`; the three
    # obstruction helpers read their signs only through
    # :meth:`pair_swap_sign`, :meth:`jacobi_term_sign` and
    # :meth:`leibniz_term_sign`.

    def grading_degree(
        self, x: Expr, registry: Optional[PropertyRegistry] = None
    ) -> Degree:
        """``|x|`` — the operand's degree in the module's own grading
        (the grading of :meth:`module_product`). Default: the operator
        grading :func:`degree_of`. Raises :class:`ValueError` when the
        degree is undeterminable."""
        return degree_of(x, registry)

    def operand_degree(
        self, x: Expr, registry: Optional[PropertyRegistry] = None
    ) -> Degree:
        """``s(x) = |x| + k`` — the SHIFTED degree in which the bracket
        is graded antisymmetric and satisfies graded Jacobi."""
        return self.grading_degree(x, registry) + self._degree

    def module_product(self, b: Expr, c: Expr) -> Expr:
        """The product the Leibniz axiom distributes over (default:
        :class:`Product`)."""
        return Product(b, c)

    def pair_swap_sign(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Optional[int]:
        """``ε`` in the graded-antisymmetry CLAIM ``[a, b] = ε·[b, a]``:
        ``ε = −(−1)^{s(a)s(b)}`` with ``s`` = :meth:`operand_degree`.

        This is the sign the axiom states (it is what
        :meth:`graded_antisymmetry_obstruction` builds), not a
        certificate that the bracket satisfies it — consult
        :attr:`is_graded_antisymmetric` / prove the obstruction for
        that. ``None`` when the parity is symbolic; an undeterminable
        degree raises :class:`ValueError`.
        """
        p = (
            self.operand_degree(a, registry)
            * self.operand_degree(b, registry)
        ).parity()
        if p is None:
            return None
        return -1 if p == 0 else 1

    def jacobi_term_sign(
        self,
        A: Expr,
        B: Expr,
        C: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Optional[int]:
        """Sign ``(−1)^{s(A)s(C)}`` of the ``[A, [B, C]]`` summand in the
        cyclic graded Jacobi ``Σ_cyc (−1)^{s(A)s(C)} [A, [B, C]] = 0``
        (``s`` = :meth:`operand_degree`). ``None`` when symbolic."""
        p = (
            self.operand_degree(A, registry)
            * self.operand_degree(C, registry)
        ).parity()
        if p is None:
            return None
        return 1 if p == 0 else -1

    def leibniz_term_sign(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Optional[int]:
        """Sign ``(−1)^{s(a)|b|}`` of ``b·[a, c]`` in the Leibniz claim
        ``[a, b·c] = [a, b]·c + (−1)^{s(a)|b|} b·[a, c]``: ``ad_a`` has
        degree ``s(a) = |a| + k`` and passes ``b`` of UNSHIFTED degree
        ``|b|`` (audit 0b00e1b K1-4/M1X-7: the ``k`` was missing).
        ``None`` when symbolic."""
        p = (
            self.operand_degree(a, registry)
            * self.grading_degree(b, registry)
        ).parity()
        if p is None:
            return None
        return 1 if p == 0 else -1

    @abstractmethod
    def expand(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """Return the definitional expansion of ``[a, b]``.

        Subclasses implement this with their concrete formula. The
        expansion is purely syntactic, it does not invoke simplify /
        canonicalize; the caller pipes the result through whichever
        reductions they need.
        """

    # ---- axiom obstruction helpers --------------------------------- #
    #
    # Each helper returns the Expr the axiom claims is zero. Feed it to
    # simplify() / canonicalize() and collect_terms() to get a
    # verdict on concrete inputs.

    def graded_antisymmetry_obstruction(
        self,
        a: Expr,
        b: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """``[a, b] + (−1)^{s(a)s(b)} [b, a]`` (``= [a, b] − ε[b, a]``
        with ``ε`` = :meth:`pair_swap_sign`).

        Claims to be zero exactly when the bracket is graded
        antisymmetric on ``(a, b)`` in its shifted convention
        ``s = |·| + k`` (:meth:`operand_degree`; for Schouten–Nijenhuis
        ``s = m − 1``, the multivector degree minus one). Unshifted
        degrees for ``k ≠ 0`` built the WRONG obstruction (2026-09-08
        re-audit), and the operator degree for SN claimed
        ``[π, π]_SN = 0`` for every bivector (audit 0b00e1b K1-3).
        Undecidable parity raises :class:`ValueError`.
        """
        eps = self.pair_swap_sign(a, b, registry)
        if eps is None:
            raise ValueError(
                f"antisymmetry obstruction parity is symbolic for "
                f"({a!r}, {b!r}); narrow the operand degrees"
            )
        ab = BracketApply(self, a, b)
        ba = BracketApply(self, b, a)
        return Sum(ab, ba if eps == -1 else Neg(ba))

    def graded_jacobi_obstruction(
        self,
        a: Expr,
        b: Expr,
        c: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """Cyclic Jacobi with Koszul signs in the shifted convention:

            (−1)^{s(a)s(c)} [a, [b, c]]
          + (−1)^{s(b)s(a)} [b, [c, a]]
          + (−1)^{s(c)s(b)} [c, [a, b]]

        with ``s`` = :meth:`operand_degree` and each sign read from
        :meth:`jacobi_term_sign`. Undecidable parity raises
        :class:`ValueError`.
        """
        terms = []
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            sign = self.jacobi_term_sign(x, y, z, registry)
            if sign is None:
                raise ValueError(
                    "Jacobi obstruction parity is symbolic; narrow "
                    "operand degrees"
                )
            outer = BracketApply(self, x, BracketApply(self, y, z))
            terms.append(outer if sign == 1 else Neg(outer))
        return Sum(*terms)

    def leibniz_obstruction(
        self,
        a: Expr,
        b: Expr,
        c: Expr,
        registry: Optional[PropertyRegistry] = None,
    ) -> Expr:
        """``[a, b·c] − [a, b]·c − (−1)^{s(a)|b|} b·[a, c]``, ``·`` =
        :meth:`module_product`, sign from :meth:`leibniz_term_sign`.

        Claims to be zero when the bracket acts as a graded derivation
        in its second slot. Undecidable sign parity raises.
        """
        sign = self.leibniz_term_sign(a, b, registry)
        if sign is None:
            raise ValueError(
                "Leibniz obstruction parity is symbolic; narrow "
                "operand degrees"
            )
        mul = self.module_product
        left = BracketApply(self, a, mul(b, c))
        t1 = mul(BracketApply(self, a, b), c)
        t2 = mul(b, BracketApply(self, a, c))
        # Fold the sign directly rather than stacking Neg(Neg(…)).
        return Sum(left, Neg(t1), Neg(t2) if sign == 1 else t2)

    # ---- identity / hashing ---------------------------------------- #

    def _identity_key(self) -> Any:
        """Override in subclasses carrying parametric data.

        Two brackets are equal iff they share concrete type, name,
        degree, and axiom profile. Parametric brackets (e.g. derived
        bracket with a specific generator) extend this key with their
        own payload.
        """
        return (
            self._name,
            self._degree,
            self._is_graded_antisymmetric,
            self._satisfies_leibniz,
            self._satisfies_graded_jacobi,
        )

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if type(self) is not type(other):
            return NotImplemented
        return self._identity_key() == other._identity_key()

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._identity_key()))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._name!r})"


# --------------------------------------------------------------------- #
# Standalone expand                                                      #
# --------------------------------------------------------------------- #


def expand_bracket(
    node: BracketApply, registry: Optional[PropertyRegistry] = None
) -> Expr:
    """Expand a single :class:`BracketApply` via its bracket's rule.

    Matches the :func:`jacopy.algebra.commutator.expand_commutator`
    pattern, a standalone function that the rewrite layer can plug in
    as a rule, plus a :meth:`BracketApply.expand` convenience method.
    """
    return node.expand(registry)
