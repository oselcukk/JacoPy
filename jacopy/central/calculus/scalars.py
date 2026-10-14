"""
Conservative scalar-function recognition (shared by calculus rules).

Moved here from :mod:`jacopy.central.tangent.definitions` (which
re-exports it) so the generic calculus layer can use it without
importing the tangent instantiation.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.commutator import is_certified_derivation
from jacopy.core.expr import Expr, Integer, Neg, Product, Rational, Sum
from jacopy.core.properties import (
    AntiCommuting,
    Graded,
    NonCommuting,
    Scalar,
    plain_degree_zero,
    scalar_contract_certified,
)
from jacopy.core.registry import PropertyRegistry


def is_scalar_function(
    expr: Expr, registry: Optional[PropertyRegistry] = None
) -> bool:
    """Conservative check: is ``expr`` certainly a ``C^∞(M)`` function?

    A thin wrapper over the ONE type source,
    :func:`~jacopy.central.objects.kind.kind_of` (a single source
    avoids two type sources disagreeing): ``True`` exactly when the
    kind is ``"function"`` (or the zero function). There, recursively:
    numerals; symbols declared ``Scalar``/``Graded(0)``; degree-0
    atoms that are not operators (0-forms, Kronecker delta, …);
    evaluations ``⟨α, X⟩``, ``ω(Y…)``; a degree-0 derivation or a
    vector field applied to a function; ``ι_X α`` for a certified
    vector ``X`` and a 1-form ``α``; ``f^n`` with ``n ≥ 0`` an integer;
    bracket values of a bracket declared ``function_valued`` on
    functions; and sums / products / negations of these. Anything
    unrecognized is ``False`` — soundness over completeness.
    """
    from jacopy.central.objects.kind import kind_of  # noqa: WPS433 - central objects sit above this module

    return kind_of(expr, registry).kind in ("function", "zero")


def declared_real_constant(
    expr: Expr, registry: Optional[PropertyRegistry], *, record: bool = True
) -> bool:
    """The REGISTRY half of :func:`is_real_constant` (the type source
    :func:`~jacopy.central.objects.kind.kind_of` calls this one, since
    the structural half is ``kind_of`` itself): the effective answers
    for ``expr`` certify an ℝ-constant —
    :func:`~jacopy.core.properties.scalar_contract_certified` on
    ``Scalar`` (shadowing already applied by the registry), ``Graded``,
    ``NonCommuting``, ``AntiCommuting``.

    Reads. A NEGATIVE Scalar answer is pre-filtered with
    :meth:`~jacopy.core.registry.PropertyRegistry.peek` and NOT
    recorded as a hypothesis; a positive one is re-queried with ``get``
    (the visible Scalar) and the three clash answers are read RAW
    (:meth:`~jacopy.core.registry.PropertyRegistry.lookup`, recorded as
    raw facts — a visibility filter never hides a clash), so
    all four become the hypotheses of the step that relies on them. Why the negative is not
    a hypothesis (the documented contract, locked by
    ``test_m1_1_negative_scalar_answers_are_not_hypotheses``): constants
    are functions, so every rewrite the engine performs for a
    non-constant atom stays valid when that atom is later declared
    Scalar — the only rule a Scalar declaration switches ON is the
    contract step ``D(c) = 0``, which runs before every other rule and
    records "``c`` is Scalar"; nothing fires BECAUSE an atom is not a
    constant. The converse direction (a step that used "``c`` is
    Scalar", cited where ``c`` is a function) is refused by the recorded
    positive fact. ``record=False`` (the model oracle) records nothing.
    """
    if registry is None:
        return False
    from contextlib import nullcontext

    with (nullcontext() if record else registry.untracked()):
        if registry.peek(expr, Scalar) is None:
            return False
        # the clash is decided on the RAW declarations: a
        # visibility filter (axioms whitelist / strict mode) narrows
        # which Scalar declaration may be USED, it never hides the
        # Graded / NonCommuting / AntiCommuting that make the
        # expression a non-constant — shadowing in the registry uses
        # the raw declarations for the same reason
        scalar = registry.get(expr, Scalar)  # the visible Scalar: a recorded hypothesis
        raw = tuple(
            registry.lookup(expr, cls, record=record).prop  # recorded as RAW facts
            for cls in (Graded, NonCommuting, AntiCommuting)
        )
        return scalar_contract_certified(scalar, *raw)


def is_real_constant(
    expr: Expr, registry: Optional[PropertyRegistry] = None, *, record: bool = True
) -> bool:
    """THE ℝ-constant test of the Scalar contract (ONE meaning,
    ONE predicate). Every consumer calls
    it: product_rule's ``D(c) = 0`` and the engine's contract step
    (through :func:`annihilates`), sort_product (the free swap and the
    degree), :func:`~jacopy.algebra.derivation.degree_of`,
    AgreementOnGenerators (dropped generators, ``f·D`` coefficients),
    the diagnostics, the Koszul generic-function minting and the model
    oracle (``record=False``).

    ``True`` for a numeral, or for an ATOM that is (1) certified by the
    registry (:func:`declared_real_constant`: effective ``Scalar`` —
    shadowing applied — and no ``Graded(k ≠ 0)`` / symbolic degree /
    ``NonCommuting`` / ``AntiCommuting``) and (2) of ``function`` kind
    for the ONE type source :func:`~jacopy.central.objects.kind.kind_of`
    (a vector field, an operator or a form of non-zero degree declared
    Scalar is NOT a constant — default-reject). Anything else: ``False``.
    """
    if isinstance(expr, (Integer, Rational)):
        return True
    if isinstance(expr, (Neg, Sum, Product)):
        # structural closure: a negation / sum / product
        # whose every leaf is an ℝ-constant is one (constants form a
        # ring) — unless the node ITSELF carries a raw declaration that
        # contradicts constancy (e.g. ``declare(c·k, Graded(1))``)
        if not all(is_real_constant(c, registry, record=record) for c in expr.children):
            return False  # (a negative answer records nothing)
        if registry is not None:
            own = tuple(registry.lookup(expr, cls, record=record).prop
                        for cls in (Graded, NonCommuting, AntiCommuting))
            if not plain_degree_zero(*own):
                return False
        return True
    if registry is None or not expr.is_atom:
        return False
    if not declared_real_constant(expr, registry, record=record):
        return False
    from contextlib import nullcontext
    from jacopy.central.objects.kind import kind_of  # noqa: WPS433 - central objects sit above this module

    with (nullcontext() if record else registry.untracked()):
        return kind_of(expr, registry).kind == "function"


def annihilates(
    op: Expr, arg: Expr, registry: Optional[PropertyRegistry] = None
) -> bool:
    """``op(arg) = 0`` by the Scalar contract: ``op`` a certified
    derivation (:func:`~jacopy.algebra.commutator.is_certified_derivation`)
    and ``arg`` an ℝ-constant (:func:`is_real_constant`). The ONE
    predicate behind product_rule's ``D(c) = 0`` and the engine's
    :class:`~jacopy.proof.expansion.ScalarConstantContract`. The cheap
    structural test runs first."""
    return is_certified_derivation(op) and is_real_constant(arg, registry)
