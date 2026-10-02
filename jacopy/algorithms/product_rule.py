"""
Graded Leibniz expansion.

Rewrites every :class:`Act` node ``D(x)`` by pushing the operator
through sums (R-linearity) and products (graded Leibniz):

* ``D(a + b) → D(a) + D(b)``
* ``D(−a) → −D(a)``
* ``D(a*b*c) → D(a)*b*c + (−1)^{|D||a|} a*D(b)*c
               + (−1)^{|D|(|a|+|b|)} a*b*D(c)``

For the Leibniz expansion the degrees of the factors must be
determinable, either because the factor is a :class:`Derivation`
(self-describing), a numeric literal (degree 0), or registered as
:class:`Scalar`/:class:`Graded` in the supplied registry. An
undetermined factor raises :class:`ValueError`: the modelling gap is
something the user needs to fix, not something we should silently paper
over with a zero-degree assumption.

Who is split (default-reject; audit 0b00e1b P0-2 and its code
review): the graded Leibniz rule is applied only to a certified
derivation — a :class:`Derivation` not marked ``leibniz = False``, an
operator declaring ``leibniz = True``, or a commutator of two such. An
operator may take the decision itself through the PROTOCOL

    ``op.splits_over_product(arg, registry) -> bool``

(``arg`` the Product/Wedge operand): ``False`` keeps ``Act(op, arg)``
unexpanded (e.g. a Lie-derivative model that is not Leibniz in that
slot), ``True`` splits; a :class:`Derivation` without the method
behaves as ``True``. ``leibniz = False`` operators are C∞-linear
(scalars pull out); ``section_value = True`` (from which a
:class:`Derivation`'s ``leibniz`` is derived) marks a section-valued
atom that is a Derivation only for slot plumbing — its ``Act`` stays
inert. A certified scalar function in operator position
multiplies; every other operator is only ℝ-linear (sums, signs and
numeric factors pass through). :class:`~jacopy.central.calculus.bracket_calculus.ActExpansionDefinition`
delegates here, so the engine rule follows the same protocol.

The pass is bottom-up and inert on nodes that aren't :class:`Act` at
their head: inner structure inside the argument is expanded first, so
``D(E(a*b))`` first expands the inner ``E`` Leibniz then the outer
``D``. Outer derivation degrees see the *expanded* operand structure.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from jacopy.algebra.commutator import is_certified_derivation
from jacopy.algebra.derivation import Act, Derivation, degree_of
from jacopy.algorithms.base import Algorithm
from jacopy.core.expr import Expr, Integer, Neg, Product, Rational, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree


# --------------------------------------------------------------------- #
# Public entry                                                           #
# --------------------------------------------------------------------- #


def product_rule(
    expr: Expr, registry: Optional[PropertyRegistry] = None
) -> Expr:
    """Recursively expand every ``Act`` via graded Leibniz and linearity.

    Bottom-up: children are expanded first, so inner ``Act`` nodes are
    simplified before their outer enclosing ``Act`` looks at them.
    Atoms pass through untouched.
    """
    if expr.is_atom:
        return expr

    new_children = tuple(product_rule(c, registry) for c in expr.children)

    if isinstance(expr, Act):
        op, arg = new_children
        return _expand_act(op, arg, registry)

    return expr._rebuild(new_children)


# --------------------------------------------------------------------- #
# Act-specific expansion                                                 #
# --------------------------------------------------------------------- #


def _expand_act(
    op: Expr, arg: Expr, registry: Optional[PropertyRegistry]
) -> Expr:
    """Apply linearity + graded Leibniz to a single ``Act`` node.

    When ``op`` is itself a :class:`Product` of operators, i.e. an
    explicit composition ``D1 ∘ D2 ∘ … ∘ Dn``, the application is
    unfolded right-to-left into nested ``Act`` nodes and each layer is
    expanded in turn. That is the only place in the algorithm where
    derivation composition actually acts on an operand; at
    :class:`Act` construction it stays inert.

    Scalar-level linearity on the operator side, ``Neg(op)`` and the
    zero operator ``Integer(0)``, is peeled here too. Commutator
    expansion routinely generates ``Act(Neg(compose(D1, D2)), x)``
    shapes; pulling the sign out and recursing lets the composition
    unfold through the negation instead of stalling.
    """
    if isinstance(op, Neg):
        return Neg(_expand_act(op.arg, arg, registry))
    if isinstance(op, Sum):
        # Operator-side additivity: a sum of operators acts pointwise,
        # (D1 + D2)(x) = D1(x) + D2(x). Slot rewrites routinely leave
        # Sum-headed operators inside Act nodes (e.g. a sharp whose
        # 1-form slot expanded into a sum).
        return Sum.make(
            *(_expand_act(o, arg, registry) for o in op.children)
        )
    if isinstance(op, Integer) and op == Integer(0):
        return Integer(0)
    if isinstance(arg, Integer) and arg == Integer(0):
        # Every graded derivation is linear, so D(0) = 0 regardless of
        # the specific operator. Dropping this eagerly keeps axiom
        # residues like Act(d, Act(d², x))=Act(d, 0) from surviving into
        # later passes that would otherwise stall waiting for an engine
        # rewrite that never fires on this surviving shape.
        return Integer(0)
    if isinstance(arg, (Integer, Rational)) and _is_certified_derivation(op):
        # Derivations annihilate numeric constants: D(1) = D(1·1) =
        # 2·D(1) forces D(1) = 0, and linearity gives D(c) = 0. This is
        # what makes ℝ-homogeneity [c·X, Y] = c·[X, Y] close — the
        # Leibniz split of Y(c·g) leaves a Y(c)·g term that must die.
        return Integer(0)
    if registry is not None and arg.is_atom and _annihilates(op, arg, registry):
        # The Scalar CONTRACT (core.properties.Scalar, audit 0b00e1b
        # M1-1 ≡ M1-2): a Scalar-declared atom
        # (scalars.is_real_constant) is an ℝ-constant,
        # so a derivation kills it exactly like a numeral — the same
        # contract under which sort_product lets it commute past a
        # derivation (D∘c = c∘D + D(c) = c∘D). Declaring Scalar on a
        # symbol with a non-zero derivative is a contradiction (use
        # Graded(0) for a function).
        return Integer(0)
    if getattr(arg, "is_constant", False) and _is_certified_derivation(op):
        # The is_constant protocol: atoms marking themselves constant
        # (e.g. the Kronecker delta) are likewise annihilated. This is
        # what closes frame identities like de^c(e_a, e_b) = -γ^c_ab,
        # whose Palais unroll produces e_a(δ^c_b) terms.
        return Integer(0)
    if isinstance(op, Product) and op.children:
        result = arg
        for d in reversed(op.children):
            result = _expand_act(d, result, registry)
        return result
    from jacopy.central.calculus.scalars import is_scalar_function

    if not isinstance(op, Derivation) and is_scalar_function(op, registry):
        # A CERTIFIED scalar function in operator position is a
        # coefficient (compositions like f·X put scalars there): it
        # acts by multiplication, NEVER by Leibniz — splitting s(ab)
        # into s(a)b + a·s(b) double-counts to 2s·ab. "Degree 0" alone
        # is NOT that certificate (audit 0b00e1b P0-2, M1-3): Λ♯(dh)
        # from the public Sharp has degree −1+1 = 0 but is a vector
        # field.
        return Product(op, arg)
    # Every operator in Act position is additive (ℝ-linear).
    if isinstance(arg, Sum):
        return Sum.make(
            *(_expand_act(op, c, registry) for c in arg.children)
        )
    if isinstance(arg, Neg):
        inner = _expand_act(op, arg.arg, registry)
        return Neg(inner)
    from jacopy.core.wedge import Wedge as _Wedge

    if isinstance(arg, (Product, _Wedge)):
        mode = _product_mode(op, arg, registry)
        if mode == "leibniz":
            try:
                if isinstance(arg, Product):
                    return _expand_leibniz(op, arg, registry)
                # Graded Leibniz over the WEDGE product (the wedge is
                # the graded product of forms — Phase 5.E.4):
                # D(α∧β) = D(α)∧β + (−1)^{|D||α|} α∧D(β) + …
                return _expand_wedge_leibniz(op, arg, registry)
            except ValueError:
                if isinstance(op, Derivation):
                    raise  # documented contract for derivation atoms
                # a certified composite (commutator) with a symbolic
                # sign parity: leave it inert rather than raise from
                # inside an engine rule's matches()
                return Act(op, arg)
        if mode == "cinf-linear" and isinstance(arg, Product):
            # LINEAR-ONLY C∞-linear operator (e.g. the multivector
            # interior ι_P for p ≥ 2 — a COMPOSITION of derivations,
            # not a derivation): scalar factors pull out, no Leibniz
            # split (6.H.2 soundness catch, 2026-09-07). Over a Wedge
            # it stays inert (2026-09-09 catch).
            return _pull_out(op, arg, registry, is_scalar_function)
        if mode == "linear" and isinstance(arg, Product):
            # uncertified operator: ℝ-linearity only — NUMERIC factors
            # pull out (X_h(2·a) = 2·X_h(a)), functions do not.
            return _pull_out(
                op, arg, registry,
                lambda c, _r: isinstance(c, (Integer, Rational)),
            )
        # "blocked" (the operator declined via splits_over_product),
        # or a Wedge under a non-Leibniz operator: inert.
        return Act(op, arg)
    # Atom or other compound (Power, Act, Commutator, ...): leave inert.
    return Act(op, arg)


def _pull_out(op: Expr, prod: Product, registry, is_coefficient) -> Expr:
    """``op(c₁⋯c_k·r) → c₁⋯c_k·op(r)`` for the factors accepted by
    ``is_coefficient`` (requires at least one coefficient and one
    remaining factor; otherwise inert). One classification pass."""
    coeffs: List[Expr] = []
    rest: List[Expr] = []
    for c in prod.children:
        (coeffs if is_coefficient(c, registry) else rest).append(c)
    if coeffs and rest:
        core = rest[0] if len(rest) == 1 else Product(*rest)
        return Product(*coeffs, _expand_act(op, core, registry))
    return Act(op, prod)


_ANNIHILATES = None


def _annihilates(op: Expr, arg: Expr, registry: PropertyRegistry) -> bool:
    """:func:`jacopy.central.calculus.scalars.annihilates`, resolved
    once (the calculus layer sits above the algorithms, so the import
    is late — but cached: no import machinery on the hot path)."""
    global _ANNIHILATES
    if _ANNIHILATES is None:
        from jacopy.central.calculus.scalars import annihilates  # noqa: WPS433

        _ANNIHILATES = annihilates
    return _ANNIHILATES(op, arg, registry)


#: the Leibniz certificate (one definition, in the algebra layer)
_is_certified_derivation = is_certified_derivation


def _product_mode(op: Expr, arg: Expr, registry) -> str:
    """How ``op`` acts on the product ``arg`` (a Product or Wedge):

    * ``"blocked"`` — ``op.section_value`` (a value, not an operator:
      ``Act`` on it is undefined);
    * ``"cinf-linear"`` — ``op.leibniz is False`` (C∞-linear, not a
      derivation: scalars pull out, no split);
    * the operator PROTOCOL ``op.splits_over_product(arg, registry)``
      when the operator defines it: ``True`` → ``"leibniz"``,
      ``False`` → ``"blocked"`` (the Act stays inert — e.g. a
      Lie-derivative model that is not Leibniz in that slot);
    * ``"leibniz"`` for a certified derivation
      (:func:`_is_certified_derivation`; the protocol's default for a
      :class:`Derivation` is ``True``, the pre-protocol behaviour);
    * ``"linear"`` otherwise (numeric factors pull out only).
    """
    if getattr(op, "section_value", False):
        # a section-VALUED atom (bracket, Jacobiator, g⁻¹ω, …) that
        # subclasses Derivation only for slot plumbing: Act(value, ·)
        # has no meaning, so neither Leibniz nor a C∞ pull-out applies
        # — inert (default reject). The marker alone suffices.
        return "blocked"
    if getattr(op, "leibniz", None) is False:
        return "cinf-linear"
    hook = getattr(op, "splits_over_product", None)
    if callable(hook):
        return "leibniz" if hook(arg, registry) else "blocked"
    if _is_certified_derivation(op):
        if not isinstance(op, Derivation):
            # a certified composite (commutator of derivations) splits
            # only when its degree is determinable and when NEITHER
            # component vetoes the split through the protocol —
            # otherwise stay linear instead of raising from inside an
            # engine match
            from jacopy.algebra.commutator import Commutator

            if isinstance(op, Commutator):
                for comp in (op.a, op.b):
                    if _product_mode(comp, arg, registry) != "leibniz":
                        return "linear"
            try:
                degree_of(op, registry)
            except ValueError:
                return "linear"
        return "leibniz"
    return "linear"


def _expand_wedge_leibniz(op: Expr, wedge: Expr, registry) -> Expr:
    """``D(a₁∧…∧a_n) → Σ_i sign_i · a₁∧…∧D(a_i)∧…∧a_n`` with
    ``sign_i = (−1)^{|D|·(|a₁|+…+|a_{i−1}|)}`` — the Wedge twin of
    :func:`_expand_leibniz`.

    WHICH degree ``|a_j|``: the Wedge is the graded product of the
    exterior algebra (forms, or multivectors), so the sign is computed
    in the EXTERIOR grading — the one :func:`degree_of` already uses
    for the Wedge node itself (the ``wedge_degree`` lift). A vector
    field is a 1-vector there (``|X| = 1``) even though its OPERATOR
    degree (as a derivation of functions) is 0; reading the operator
    degree made ``d̃(X∧Y)`` expand to ``d̃X∧Y + X∧d̃Y`` instead of the
    correct ``d̃X∧Y − X∧d̃Y`` (audit 0b00e1b P0-1: K1-2 ≡ M1X-1). See
    :func:`_wedge_factor_degree`. ``|D|`` is the operator's own degree
    (``degree_of(op)``): for the operators that act on a wedge algebra
    that IS their shift in the exterior grading (``d``, ``d̃``: +1;
    ``ι``, ``ι̃_ω``: −1; ``ℒ``: 0).

    A factor whose exterior degree is not determinable (a mixed sum
    ``X + u``, a composition ``X∘Y``, an unknown operator) has no
    well-defined sign: the node is left INERT — never graded by the
    operator degree (default-reject)."""
    from jacopy.core.wedge import Wedge as _Wedge

    factors = tuple(wedge.children)
    deg_op = degree_of(op, registry)
    deg_op_is_zero = deg_op == Degree.const(0)
    degrees: List[Degree] = []
    if not deg_op_is_zero:
        try:
            degrees = [
                _wedge_factor_degree(f, registry) for f in factors[:-1]
            ]
        except ValueError:
            return Act(op, wedge)
    running = Degree.const(0)
    terms: List[Expr] = []
    for i, fac in enumerate(factors):
        if deg_op_is_zero:
            parity = 0
        else:
            sign_exp = deg_op * running
            parity = sign_exp.parity()
            if parity is None:
                raise ValueError(
                    f"Cannot expand wedge Leibniz at factor {i} of "
                    f"{wedge!r}: sign parity is symbolic."
                )
        new_factors = list(factors)
        new_factors[i] = _expand_act(op, fac, registry)
        term: Expr = (
            _Wedge(*new_factors)
            if len(new_factors) > 1
            else new_factors[0]
        )
        if parity == 1:
            term = Neg(term)
        terms.append(term)
        if not deg_op_is_zero and i + 1 < len(factors):
            running = running + degrees[i]
    return Sum.make(*terms)


def _wedge_factor_degree(fac: Expr, registry) -> Degree:
    """Exterior degree of a wedge factor / the sole non-scalar factor
    of a scalar product — the shared rule
    :func:`jacopy.central.objects.kind.wedge_factor_degree` (also used
    by ``degree_of`` of a Wedge). Raises :class:`ValueError` when not
    determinable; never falls back to the operator degree of a
    vector-carrying factor."""
    from jacopy.central.objects.kind import wedge_factor_degree  # noqa: WPS433

    return wedge_factor_degree(fac, registry)


# --- factor classification (one pass per product) --------------------- #

_SCALAR, _FORM, _MULTI, _OTHER = "scalar", "form", "multi", "other"


def _classify(c: Expr, registry) -> Tuple[str, Optional[Degree]]:
    """``(class, exterior degree or None)`` of a product factor, from
    the one type source :func:`~jacopy.central.objects.kind.kind_of`:
    ``scalar`` (function / zero), ``form``, ``multi`` (vector /
    multivector — where a Product would read as a composition), or
    ``other`` (unknown, operator, tensor, mismatch)."""
    from jacopy.central.objects.kind import kind_of  # noqa: WPS433

    k = kind_of(c, registry)
    if k.kind in ("function", "zero"):
        return _SCALAR, Degree.const(0)
    deg = k.degree if isinstance(k.degree, Degree) else None
    if k.kind == "form" and deg is not None:
        return _FORM, deg
    if k.kind in ("vector", "multivector") and deg is not None:
        return _MULTI, deg
    if isinstance(getattr(c, "wedge_degree", None), Degree):
        return _MULTI, c.wedge_degree
    return _OTHER, None


def _has_multivector_content(c: Expr, registry) -> bool:
    from jacopy.central.objects.kind import has_vector_content  # noqa: WPS433

    return has_vector_content(c, registry)


def _product_degrees(
    factors: Tuple[Expr, ...], classes, registry
) -> Optional[List[Degree]]:
    """Leibniz degrees ``|a_1|, …, |a_{n−1}|`` of a Product, from ONE
    source, or ``None`` when no sound grading exists (the caller then
    distributes a Sum factor or leaves the node inert):

    * scalars count 0; forms their degree (their Product is their
      wedge); a vector / multivector its exterior degree — but only as
      the SOLE non-scalar factor (``s·X`` is the module product ``X∧s``;
      ``X·Y`` is a composition: ``None``);
    * an untyped factor: without vector/multivector content both
      gradings agree and :func:`degree_of` is used (abstract graded
      algebras, operator products — raises when undetermined, as
      before); with such content, the structural exterior degree
      (:func:`_wedge_factor_degree`, e.g. ``d̃X``) when it is the sole
      non-scalar factor, else ``None`` — never the operator degree.
    """
    geometric = sum(1 for cls, _ in classes if cls != _SCALAR)
    out: List[Degree] = []
    for fac, (cls, deg) in zip(factors[:-1], classes[:-1]):
        if cls in (_SCALAR, _FORM):
            out.append(deg)
        elif cls == _MULTI:
            if geometric > 1:
                return None
            out.append(deg)
        elif not _has_multivector_content(fac, registry):
            out.append(_factor_degree(fac, registry))
        elif geometric == 1:
            try:
                out.append(_wedge_factor_degree(fac, registry))
            except ValueError:
                return None
        else:
            return None
    return out


def _distribute_sum_factor(
    op: Expr, prod: Product, registry
) -> Optional[Expr]:
    """ℝ-bilinearity fallback: ``D(a·(b+c)·e) = D(a·b·e) + D(a·c·e)``
    for the first Sum factor (every Act operator is additive and the
    product is multilinear), so a sum of pieces with different
    gradings expands piecewise instead of stalling — consistently with
    the already-split right-hand side."""
    for i, c in enumerate(prod.children):
        if isinstance(c, Sum):
            pieces = []
            for t in c.children:
                kids = list(prod.children)
                kids[i] = t
                pieces.append(_expand_act(op, Product(*kids), registry))
            return Sum.make(*pieces)
    return None


def _expand_leibniz(
    op: Expr, prod: Product, registry: Optional[PropertyRegistry]
) -> Expr:
    """``D(a1*...*an) → Σ_i sign_i * a1*...*D(a_i)*...*an``.

    ``sign_i = (−1)^{|D| * (|a1|+...+|a_{i−1}|)}``, the degrees from
    :func:`_product_degrees` (one source with the Wedge path: the
    exterior grading wherever a vector/multivector is involved).
    Without a sound grading a Sum factor is distributed
    (:func:`_distribute_sum_factor`), otherwise the node stays inert.
    Undecidable sign parity raises. When ``D`` turns a scalar into a
    second (multi)vector next to the existing one, that term is
    rebuilt as their wedge (``d̃(X·u) = d̃X·u − X∧d̃u``).
    """
    factors: Tuple[Expr, ...] = prod.children
    if not factors:
        # Empty product, D(1) = 0. Shouldn't normally arise but
        # handle defensively; Sum.make([]) returns Zero.
        return Integer(0)

    deg_op = degree_of(op, registry)
    # When the derivation has degree 0 the sign vanishes identically,
    # so we don't need factor degrees at all. This is the common case
    # for ordinary (ungraded) derivations and spares the caller from
    # declaring a grading for operand factors that don't have one.
    deg_op_is_zero = deg_op == Degree.const(0)

    from jacopy.central.objects.kind import kind_cache  # noqa: WPS433

    with kind_cache(registry):
        classes = [_classify(c, registry) for c in factors]
        found = (
            None
            if deg_op_is_zero
            else _product_degrees(factors, classes, registry)
        )
    degrees: List[Degree] = []
    if not deg_op_is_zero:
        if found is None:
            distributed = _distribute_sum_factor(op, prod, registry)
            return distributed if distributed is not None else Act(op, prod)
        degrees = found

    running = Degree.const(0)  # |a_1| + ... + |a_{i-1}|
    terms: List[Expr] = []
    for i, fac in enumerate(factors):
        if deg_op_is_zero:
            parity = 0
        else:
            sign_exp = deg_op * running
            parity = sign_exp.parity()
            if parity is None:
                raise ValueError(
                    f"Cannot expand Leibniz at factor index {i} of "
                    f"{prod!r}: sign parity is symbolic. Narrow the "
                    "degrees of the left-of-split factors."
                )
        new_factors = list(factors)
        # Recurse on the freshly created Act (the composition branch
        # already does): numeric factors annihilate and Sum factors
        # distribute in the same pass instead of stranding
        # ``D(2)``/``D(a+b)`` nodes into the simplify pipeline.
        new_factors[i] = _expand_act(op, fac, registry)
        term = _leibniz_term(new_factors, i, classes, registry)
        if parity == 1:
            term = Neg(term)
        terms.append(term)
        if not deg_op_is_zero and i + 1 < len(factors):
            running = running + degrees[i]

    return Sum.make(*terms)


def _leibniz_term(
    new_factors: List[Expr], i: int, classes, registry
) -> Expr:
    """Rebuild one Leibniz term. When the product had at most one
    non-scalar factor and ``D(a_i)`` created a second one next to a
    vector/multivector (``X·d̃u``), the product of the two is their
    WEDGE (``X∧d̃u``, order kept, scalars in front) — a Product there
    would read as a composition. A Product of forms stays a Product
    (the library's accepted transient wedge spelling). Only the new
    factor is reclassified."""
    from jacopy.core.wedge import Wedge as _Wedge

    if len(new_factors) == 1:
        return new_factors[0]
    cls = list(classes)
    cls[i] = _classify(new_factors[i], registry)
    geometric = [j for j, (c, _) in enumerate(cls) if c != _SCALAR]
    if len(geometric) <= 1 or not any(
        cls[j][0] == _MULTI for j in geometric
    ):
        return Product(*new_factors)
    if sum(1 for c, _ in classes if c != _SCALAR) > 1:
        return Product(*new_factors)  # was already a multi-factor product
    scalars = [new_factors[j] for j, (c, _) in enumerate(cls) if c == _SCALAR]
    w = _Wedge(*(new_factors[j] for j in geometric))
    return Product(*scalars, w) if scalars else w


def _factor_degree(fac: Expr, registry) -> Degree:
    """``degree_of`` plus the homogeneous-Sum policy the sign
    bookkeeping needs (degree_of deliberately leaves Sums to the
    caller): a Sum whose children all share one determinable degree
    has that degree."""
    try:
        return degree_of(fac, registry)
    except ValueError:
        if isinstance(fac, Sum) and fac.children:
            degs = []
            for c in fac.children:
                degs.append(_factor_degree(c, registry))
            first = degs[0]
            if all(d == first for d in degs[1:]):
                return first
        raise


# --------------------------------------------------------------------- #
# Algorithm wrapper                                                      #
# --------------------------------------------------------------------- #


class ProductRule(Algorithm):
    """:class:`Algorithm` wrapper around :func:`product_rule`.

    ``registry`` is stored on the instance so the generic
    :meth:`Algorithm.run` plumbing stays registry-free.
    """

    def __init__(self, registry: Optional[PropertyRegistry] = None) -> None:
        self._registry = registry

    def can_apply(self, expr: Expr) -> bool:
        for node in expr.walk():
            if isinstance(node, Act):
                return True
        return False

    def apply(self, expr: Expr) -> Expr:
        return product_rule(expr, self._registry)
