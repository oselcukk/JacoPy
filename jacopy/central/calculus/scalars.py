"""
Conservative scalar-function recognition (shared by calculus rules).

Moved here from :mod:`jacopy.central.tangent.definitions` (which
re-exports it) so the generic calculus layer can use it without
importing the tangent instantiation.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.derivation import Act, Derivation, degree_of
from jacopy.core.expr import Expr, Integer, Neg, Power, Product, Rational, Sum, Symbol
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree


def is_scalar_function(
    expr: Expr, registry: Optional[PropertyRegistry] = None
) -> bool:
    """Conservative check: is ``expr`` certainly a ``C^∞(M)`` function?

    Recognized shapes (recursively): registered degree-0 scalar
    symbols, numeric literals, :class:`Pairing` / :class:`MultiEval`
    (scalars by construction), a degree-0 :class:`Derivation` applied
    to a scalar function (``X(f)``, ``∇_X f``, ``[X,Y](f)``,
    ``L_X f``), sums / products / negations of scalar functions,
    powers ``f^n`` with a numeric exponent, bracket values of a bracket
    DECLARED function-valued (``function_valued``) on scalars, and
    anything :func:`~jacopy.central.objects.kind.kind_of` types as a
    function (``ι_X α`` for a 1-form ``α``).
    Returns ``False`` on anything unrecognized — soundness over
    completeness.
    """
    if isinstance(expr, (Integer, Rational)):
        return True
    if isinstance(expr, (Pairing, MultiEval)):
        return True
    if isinstance(expr, Symbol):
        if registry is None:
            return False
        try:
            return degree_of(expr, registry) == Degree.const(0)
        except ValueError:
            return False
    if expr.is_atom and not isinstance(expr, Derivation):
        # Atoms carrying their own degree (Kronecker delta, anholonomy
        # coefficients, 0-forms) are functions exactly when that degree
        # is 0. Derivations are operators, never functions.
        deg = getattr(expr, "degree", None)
        if isinstance(deg, Degree):
            return deg == Degree.const(0)
    if isinstance(expr, Neg):
        return is_scalar_function(expr.arg, registry)
    if isinstance(expr, (Sum, Product)):
        return all(is_scalar_function(c, registry) for c in expr.children)
    if isinstance(expr, Act):
        op = expr.op
        if (
            isinstance(op, Derivation)
            and op.degree == Degree.const(0)
            and is_scalar_function(expr.arg, registry)
        ):
            return True
        # else: the TYPE certificate below (e.g. ι_X α for a 1-form α)
    if isinstance(expr, Power):
        # f^n with a scalar base and a NUMERIC exponent
        return isinstance(expr.exp, (Integer, Rational)) and (
            is_scalar_function(expr.base, registry)
        )
    from jacopy.brackets.base import BracketApply  # noqa: WPS433 - brackets layer sits above algebra

    if isinstance(expr, BracketApply):
        # A bracket is function-valued only by DECLARATION
        # (``bracket.function_valued`` — a bool, or a callable
        # ``(a, b, registry) -> bool``) and on scalar operands: its
        # degree alone does not tell a function from a vector field.
        decl = getattr(expr.bracket, "function_valued", False)
        if callable(decl):
            decl = decl(expr.a, expr.b, registry)
        if decl is True and is_scalar_function(
            expr.a, registry
        ) and is_scalar_function(expr.b, registry):
            return True
    # Type certificate: the common type query says "function" — derived
    # from the nodes' own metadata, never guessed (ι_X α with α a
    # 1-form: degree 1 − 1 = 0 on a form; X(f) for a vector field X).
    # A vector-valued degree-0 expression such as Λ♯(dh) is "vector"
    # there and stays rejected.
    from jacopy.central.objects.kind import kind_of  # noqa: WPS433 - kind_of imports this module

    return kind_of(expr, registry).kind == "function"
