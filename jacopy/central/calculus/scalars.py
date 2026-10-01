"""
Conservative scalar-function recognition (shared by calculus rules).

Moved here from :mod:`jacopy.central.tangent.definitions` (which
re-exports it) so the generic calculus layer can use it without
importing the tangent instantiation.
"""

from __future__ import annotations

from typing import Optional

from jacopy.core.expr import Expr
from jacopy.core.registry import PropertyRegistry


def is_scalar_function(
    expr: Expr, registry: Optional[PropertyRegistry] = None
) -> bool:
    """Conservative check: is ``expr`` certainly a ``C^∞(M)`` function?

    A thin wrapper over the ONE type source,
    :func:`~jacopy.central.objects.kind.kind_of` (audit 0b00e1b code
    review: two type sources disagreed): ``True`` exactly when the
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


def is_real_constant(
    expr: Expr, registry: Optional[PropertyRegistry] = None
) -> bool:
    """THE ℝ-constant test of the Scalar contract (audit 0b00e1b M1-1;
    one definition for product_rule's ``D(c) = 0``, the engine's
    contract step and sort_product's free swap).

    ``True`` for a numeral, or for an ATOM carrying an EXACT
    :class:`~jacopy.core.properties.Scalar` declaration whose kind is
    ``function`` and that has no ``Graded(k ≠ 0)``. Class / predicate
    Scalar declarations are NOT trusted (``declare_for_class(Symbol,
    Scalar())`` must not make a 1-form ``w`` constant). The exact
    pre-filter is not recorded as a registry read; a positive answer is
    re-queried so "``c`` is Scalar" becomes the step's hypothesis.
    """
    from jacopy.core.expr import Integer, Rational

    if isinstance(expr, (Integer, Rational)):
        return True
    if registry is None or not expr.is_atom:
        return False
    from jacopy.core.properties import Graded, Scalar

    if not registry.declared_exact(expr, Scalar):
        return False
    registry.get(expr, Scalar)  # record the hypothesis
    graded = registry.get(expr, Graded)
    if graded is not None and graded.degree.as_int() != 0:
        return False
    from jacopy.central.objects.kind import kind_of  # noqa: WPS433

    return kind_of(expr, registry).kind == "function"
