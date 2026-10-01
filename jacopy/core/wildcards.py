"""
Pattern matching via wildcards.

Wildcards are Expr atoms that stand in for arbitrary subtrees. They
let rewrite rules be written as patterns: ``d(?A + ?B) -> d(?A) + d(?B)``
for linearity, ``d(?A * ?B) -> d(?A)*?B + ?A*d(?B)`` for Leibniz,
``[?X, [?Y, ?Z]] + cyclic -> 0`` for Jacobi, and so on.

Two wildcard kinds:

* :class:`Wildcard`, a single hole that matches one Expr. It may
  carry constraints:

  - ``type_filter``: a :class:`Property` class the candidate must be
    registered with. Requires a :class:`PropertyRegistry` to be passed
    to :func:`match`.
  - ``expr_type``: an :class:`Expr` subclass (or tuple of them) the
    candidate must be an instance of. Lets a rule say "match only a
    Symbol here", "match any Sum here", and so on.

* :class:`SeqWildcard`, a sequence hole that matches zero or more
  consecutive children of a Sum or Product. Multiple per level are
  allowed; matching backtracks over possible splits.

Matching is structural and order-preserving, it does not reorder
Sum or Product children. Commutative matching is the job of the
algorithms layer, which canonicalizes expressions before invoking
:func:`match`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from jacopy.core.expr import Atom, Expr
from jacopy.core.properties import Property
from jacopy.core.registry import PropertyRegistry


# --------------------------------------------------------------------- #
# Wildcard nodes                                                         #
# --------------------------------------------------------------------- #


ExprTypeFilter = Union[Type[Expr], Tuple[Type[Expr], ...]]


def _normalize_expr_type(
    expr_type: Optional[ExprTypeFilter],
) -> Optional[Tuple[Type[Expr], ...]]:
    if expr_type is None:
        return None
    if isinstance(expr_type, type):
        candidates: Tuple[Type[Expr], ...] = (expr_type,)
    elif isinstance(expr_type, tuple):
        candidates = expr_type
    else:
        raise TypeError(
            "expr_type must be an Expr subclass or a tuple of them"
        )
    for cls in candidates:
        if not (isinstance(cls, type) and issubclass(cls, Expr)):
            raise TypeError(
                "expr_type must be an Expr subclass or a tuple of them"
            )
    return candidates


class Wildcard(Atom):
    """Single-hole pattern atom.

    A wildcard with ``name`` binds that name to whatever subtree it
    matches. If the same name appears twice in a pattern, both
    occurrences must match *structurally equal* targets.

    Optional constraints:

    * ``type_filter``, a :class:`Property` class. The target must be
      registered as that property in the :class:`PropertyRegistry`
      passed to :func:`match`.
    * ``expr_type``, an :class:`Expr` subclass, or a tuple of them.
      The target must be an instance. Evaluated without the registry.
    """

    __slots__ = ("_name", "_type_filter", "_expr_type")

    def __init__(
        self,
        name: str,
        type_filter: Optional[Type[Property]] = None,
        expr_type: Optional[ExprTypeFilter] = None,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("Wildcard name must be a str")
        if not name:
            raise ValueError("Wildcard name must be non-empty")
        if type_filter is not None:
            if not (isinstance(type_filter, type) and issubclass(type_filter, Property)):
                raise TypeError("type_filter must be a Property subclass")
        self._name = name
        self._type_filter = type_filter
        self._expr_type = _normalize_expr_type(expr_type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_filter(self) -> Optional[Type[Property]]:
        return self._type_filter

    @property
    def expr_type(self) -> Optional[Tuple[Type[Expr], ...]]:
        return self._expr_type

    def _key(self) -> Any:
        return (self._name, self._type_filter, self._expr_type)

    def _repr_inner(self) -> str:
        parts = [f"?{self._name}"]
        if self._type_filter is not None:
            parts.append(f":{self._type_filter.__name__}")
        if self._expr_type is not None:
            names = "|".join(c.__name__ for c in self._expr_type)
            parts.append(f"<{names}>")
        return "".join(parts)


class SeqWildcard(Expr):
    """Sequence wildcard matching a run of Sum/Product children.

    Usage is restricted to being a direct child of :class:`Sum` or
    :class:`Product`. At most one per level: two sequence wildcards in
    the same Sum would make the match ambiguous without a disambiguation
    strategy, and that complexity doesn't pay for itself yet.
    """

    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("SeqWildcard name must be a str")
        if not name:
            raise ValueError("SeqWildcard name must be non-empty")
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> Tuple[Expr, ...]:
        return ()

    def _key(self) -> Any:
        return self._name

    def _repr_inner(self) -> str:
        return f"?*{self._name}"


# --------------------------------------------------------------------- #
# Matching                                                              #
# --------------------------------------------------------------------- #

# Bindings map names to either a single Expr (Wildcard) or a tuple of
# Exprs (SeqWildcard). Public callers treat this as opaque.
Binding = Union[Expr, Tuple[Expr, ...]]
Bindings = Dict[str, Binding]


def match(
    pattern: Expr,
    target: Expr,
    registry: Optional[PropertyRegistry] = None,
) -> Optional[Bindings]:
    """Attempt to match ``target`` against ``pattern``.

    Returns a fresh bindings dict on success, or ``None`` on failure.

    If ``pattern`` contains type-filtered wildcards, ``registry`` must
    be supplied; otherwise the filter is treated as a failure. This is
    deliberate, silently ignoring a type filter would mask bugs.
    """
    bindings: Bindings = _MatchBindings()
    if _match(pattern, target, bindings, registry):
        return bindings
    return None


#: Private bindings entry: wildcard name → the Σ dummies its value
#: mentions BOUND (the wildcard matched inside the binder). substitute()
#: refuses to place such a value outside a binder of that dummy.
_SCOPED = "\x00scoped"


class _MatchBindings(dict):
    """The bindings dict returned by :func:`match`. It compares and
    prints like its public entries; the private ``_SCOPED`` entry
    (binder bookkeeping) is restored by the same snapshots as the
    bindings themselves."""

    def __eq__(self, other):
        if isinstance(other, dict):
            return _public(self) == _public(other)
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        return eq if eq is NotImplemented else not eq

    __hash__ = None

    def __repr__(self) -> str:
        return repr(_public(self))


def _public(d: dict) -> dict:
    return {k: v for k, v in d.items() if k != _SCOPED}


def _mentions(value: Any, atom: Expr) -> bool:
    from jacopy.core.traverse import contains

    if isinstance(value, tuple):
        return any(contains(v, atom) for v in value)
    return isinstance(value, Expr) and contains(value, atom)


@lru_cache(maxsize=4096)
def wildcard_names(expr: Expr) -> frozenset:
    """Names of every Wildcard/SeqWildcard in ``expr`` — children and
    non-child payload alike (cached: called on rule patterns)."""
    out: set = set()

    def walk(e):
        if isinstance(e, (Wildcard, SeqWildcard)):
            out.add(e.name)
            return
        if e.is_atom:
            return
        walk_payload(node_payload(e))
        for c in e.children:
            walk(c)

    def walk_payload(pk):
        if isinstance(pk, Expr):
            walk(pk)
        elif type(pk) is tuple:
            for k in pk:
                walk_payload(k)

    walk(expr)
    return frozenset(out)


def _match(
    pattern: Expr,
    target: Expr,
    bindings: Bindings,
    registry: Optional[PropertyRegistry],
) -> bool:
    if isinstance(pattern, Wildcard):
        return _bind_wildcard(pattern, target, bindings, registry)
    if isinstance(pattern, SeqWildcard):
        # Outside a Sum/Product context, bind a single target.
        return _bind_single(pattern.name, target, bindings)
    if type(pattern) is not type(target):
        return False
    if pattern.is_atom:
        return pattern == target

    from jacopy.core.indexed_sum import IndexedSum

    if isinstance(pattern, IndexedSum):
        return _match_indexed_sum(pattern, target, bindings, registry)
    # Non-child identity payload first (audit 0B00E1B-FULL M1X-6): two
    # nodes of the same class with the same children can still mean
    # different things (BracketApply's bracket, MultiEval's
    # alternating flag, d's skew/calculus, a Hodge metric). A payload
    # field holding a wildcard on the pattern side binds like any other
    # hole; every other field must agree exactly. (On failure the
    # caller restores the bindings snapshot: match() discards them,
    # _match_children_rec restores its own.)
    if not _match_payload(
        _pattern_payload(pattern), node_payload(target), bindings, registry
    ):
        return False
    return _match_children(pattern.children, target.children, bindings, registry)


def _match_indexed_sum(pattern, target, bindings, registry) -> bool:
    """Σ_d body is a BINDER: compare the range, then match the bodies
    up to α-renaming — the target is renamed to the pattern's dummy (a
    wildcard dummy binds the target's). Capture is refused both ways:

    * a concrete pattern dummy may not capture a free occurrence in the
      target body, and a WILDCARD dummy's target dummy may not coincide
      with a concrete (free) atom of the pattern body;
    * a wildcard bound OUTSIDE whose value mentions the dummy cannot be
      reused inside (the free and the bound occurrence are different);
    * a wildcard bound INSIDE whose value mentions the dummy is marked
      scoped, and :func:`substitute` never places it outside a binder
      of that dummy (no binder escape)."""
    from jacopy.core.indexed_sum import _range_key
    from jacopy.core.traverse import contains

    if _range_key(pattern.range_) != _range_key(target.range_):
        return False
    pd, td = pattern.dummy, target.dummy
    body = target.body
    prior = bindings.get(pd.name) if isinstance(pd, Wildcard) else None
    if isinstance(prior, Expr) and prior.is_atom and prior != td:
        # the same ?D already names another Σ's dummy: α-rename this
        # target binder to it (two Σ_{?D} need not share a dummy name)
        if contains(body, prior) or contains(pattern.body, prior):
            return False
        body = target.with_dummy(prior).body
        dummy = prior
    elif isinstance(pd, Wildcard):
        if contains(pattern.body, td):
            return False
        if not _bind_wildcard(pd, td, bindings, registry):
            return False
        dummy = td
    else:
        if pd != td:
            if contains(body, pd):
                return False
            body = target.with_dummy(pd).body
        dummy = pd
    dname = pd.name if isinstance(pd, Wildcard) else None
    names = wildcard_names(pattern.body)
    for n in names:
        if n != dname and n in bindings and _mentions(bindings[n], dummy):
            return False
    before = set(bindings)
    if not _match(pattern.body, body, bindings, registry):
        return False
    scoped = dict(bindings.get(_SCOPED, {}))
    for n in names | ({dname} if dname else set()):
        if (n not in before or n == dname) and n in bindings and _mentions(bindings[n], dummy):
            scoped[n] = scoped.get(n, frozenset()) | {dummy}
    if scoped:
        bindings[_SCOPED] = scoped
    return True


# --------------------------------------------------------------------- #
# Non-child payload                                                     #
# --------------------------------------------------------------------- #


class _Dropped:
    """Placeholder for a child removed from a ``_key()`` payload."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return "<child>"


_CHILD = _Dropped()


def node_payload(expr: Expr) -> Any:
    """The NON-CHILD identity payload of ``expr``.

    ``Expr`` equality is ``type + _key()``; matching walks ``children``.
    Whatever is in ``_key()`` but is not a child (a bracket object, an
    ``alternating``/``skew`` flag, a calculus name, a bound dummy, a
    metric) is the node's payload, and two same-typed nodes with equal
    children are the SAME node only when their payloads agree.

    Resolution order:

    * a class may define ``_payload_key()`` returning its payload
      explicitly (extension hook);
    * :class:`~jacopy.core.indexed_sum.IndexedSum`, whose α-canonical
      ``_key()`` does not contain its child, is ``(dummy, range-key)``;
    * otherwise ``_key()`` with every child (by identity) replaced by
      a placeholder, recursively through tuples, so the remaining
      leaves are exactly the payload fields.
    """
    hook = getattr(type(expr), "_payload_key", None)
    if hook is not None:
        return hook(expr)
    from jacopy.core.indexed_sum import IndexedSum, _range_key

    if isinstance(expr, IndexedSum):
        return (expr.dummy, _range_key(expr.range_))
    children = expr.children
    key = expr._key()
    stripped, used = _strip_in_order(key, children, 0)
    if used == len(children):
        return stripped
    # _key lists the children in another order: fall back to identity
    child_ids = {id(c) for c in children}
    return _strip_by_identity(key, child_ids)


def _collapse(items: List[Any]) -> Tuple[Any, ...]:
    out: List[Any] = []
    for item in items:
        if item is _CHILD and out and out[-1] is _CHILD:
            continue
        out.append(item)
    return tuple(out)


def _strip_in_order(key: Any, children: Tuple[Expr, ...], i: int):
    """Strip the children POSITIONALLY: walking the key left to right,
    a leaf that is the next expected child (by identity) is replaced by
    the placeholder. An object that is also a payload field (e.g.
    ``HodgeStar(g, 3, metric=g)``) stays payload past its child slot.
    Runs of consecutive children collapse to one placeholder (a
    SeqWildcard absorbs several target children)."""
    if isinstance(key, Expr):
        if i < len(children) and key is children[i]:
            return _CHILD, i + 1
        return key, i
    if type(key) is tuple:
        items: List[Any] = []
        for k in key:
            item, i = _strip_in_order(k, children, i)
            items.append(item)
        return _collapse(items), i
    return key, i


def _strip_by_identity(key: Any, child_ids: set) -> Any:
    if isinstance(key, Expr) and id(key) in child_ids:
        return _CHILD
    if type(key) is tuple:
        return _collapse([_strip_by_identity(k, child_ids) for k in key])
    return key


@lru_cache(maxsize=4096)
def _pattern_payload(pattern: Expr) -> Any:
    """Cached :func:`node_payload` for the PATTERN side (patterns are
    reused across many targets)."""
    return node_payload(pattern)


def _match_payload(
    pk: Any,
    tk: Any,
    bindings: Bindings,
    registry: Optional[PropertyRegistry],
) -> bool:
    if pk is _CHILD or tk is _CHILD:
        return pk is tk
    if isinstance(pk, (Wildcard, SeqWildcard)) or (
        isinstance(pk, Expr) and isinstance(tk, Expr)
    ):
        if not isinstance(tk, Expr):
            return False
        return _match(pk, tk, bindings, registry)
    if type(pk) is tuple and type(tk) is tuple:
        if len(pk) != len(tk):
            return False
        return all(
            _match_payload(a, b, bindings, registry) for a, b in zip(pk, tk)
        )
    if isinstance(tk, Expr) or type(pk) is not type(tk):
        return False
    return pk == tk


def _match_children(
    pchildren: Tuple[Expr, ...],
    tchildren: Tuple[Expr, ...],
    bindings: Bindings,
    registry: Optional[PropertyRegistry],
) -> bool:
    """Backtracking match over a run of pattern children against targets.

    Non-seq pattern children consume exactly one target each; SeqWildcards
    can consume any number (0..remaining). With multiple SeqWildcards in
    the same run we try all splits, left-to-right, restoring bindings on
    failure so each candidate gets a clean slate.
    """
    return _match_children_rec(
        list(pchildren), 0, list(tchildren), 0, bindings, registry
    )


def _match_children_rec(
    ps: List[Expr],
    pi: int,
    ts: List[Expr],
    ti: int,
    bindings: Bindings,
    registry: Optional[PropertyRegistry],
) -> bool:
    if pi == len(ps):
        return ti == len(ts)

    p = ps[pi]
    if isinstance(p, SeqWildcard):
        remaining = len(ts) - ti
        # Try every length k in 0..remaining; leftmost-shortest first so
        # the match order is predictable and stable.
        for k in range(0, remaining + 1):
            snapshot = dict(bindings)
            seq = tuple(ts[ti:ti + k])
            if _bind_sequence(p.name, seq, bindings):
                if _match_children_rec(
                    ps, pi + 1, ts, ti + k, bindings, registry
                ):
                    return True
            bindings.clear()
            bindings.update(snapshot)
        return False

    if ti == len(ts):
        return False

    snapshot = dict(bindings)
    if _match(p, ts[ti], bindings, registry):
        if _match_children_rec(
            ps, pi + 1, ts, ti + 1, bindings, registry
        ):
            return True
    bindings.clear()
    bindings.update(snapshot)
    return False


def _bind_wildcard(
    wild: Wildcard,
    target: Expr,
    bindings: Bindings,
    registry: Optional[PropertyRegistry],
) -> bool:
    if wild.expr_type is not None:
        if not isinstance(target, wild.expr_type):
            return False
    if wild.type_filter is not None:
        if registry is None:
            return False
        if not registry.has(target, wild.type_filter):
            return False
    return _bind_single(wild.name, target, bindings)


def _bind_single(name: str, target: Expr, bindings: Bindings) -> bool:
    prior = bindings.get(name)
    if prior is None:
        bindings[name] = target
        return True
    if isinstance(prior, tuple):
        return False
    return prior == target


def _bind_sequence(
    name: str, seq: Tuple[Expr, ...], bindings: Bindings
) -> bool:
    prior = bindings.get(name)
    if prior is None:
        bindings[name] = seq
        return True
    if not isinstance(prior, tuple):
        return False
    return prior == seq


# --------------------------------------------------------------------- #
# Substitution back into a pattern                                      #
# --------------------------------------------------------------------- #


def substitute(pattern: Expr, bindings: Bindings) -> Expr:
    """Replace every wildcard in ``pattern`` with its binding.

    Unbound CHILD wildcards are left in place (a pattern may be
    instantiated partially; :class:`~jacopy.algorithms.rewrite.Rule`
    refuses a result that still contains wildcards). SeqWildcards must
    be inside a Sum/Product; using one elsewhere is rejected at the
    Expr-building level.

    Wildcards in a node's non-child PAYLOAD (an IndexedSum dummy, a
    Hodge metric — :func:`node_payload`) are filled too (audit
    0B00E1B-FULL M1X-6 review): :func:`match` binds them, so a rule's
    right-hand side must be able to use them. A payload wildcard that
    is unbound, or that sits on a node class without a payload
    substitution (``_substitute_payload(bindings)`` hook or a built-in
    handler), raises :class:`PayloadSubstitutionError` — never a
    silent literal ``?G`` in the result.
    """
    return _subst(pattern, bindings, frozenset())


def _scoped_ok(name: str, bindings: Bindings, scope: frozenset) -> None:
    need = bindings.get(_SCOPED, {}).get(name, frozenset())
    if not need <= scope:
        raise BinderEscapeError(
            f"?{name} mentions the bound dummy "
            f"{', '.join(d._repr_inner() for d in need - scope)} and would "
            "be placed outside its binder"
        )


def _subst(pattern: Expr, bindings: Bindings, scope: frozenset) -> Expr:
    if isinstance(pattern, Wildcard):
        bound = bindings.get(pattern.name)
        if bound is None or isinstance(bound, tuple):
            return pattern
        _scoped_ok(pattern.name, bindings, scope)
        return bound
    if isinstance(pattern, SeqWildcard):
        return pattern
    if pattern.is_atom:
        return pattern
    from jacopy.core.indexed_sum import IndexedSum

    if isinstance(pattern, IndexedSum):
        return _subst_indexed_sum(pattern, bindings, scope)

    new_children: list[Expr] = []
    for child in pattern.children:
        if isinstance(child, SeqWildcard):
            bound = bindings.get(child.name)
            if bound is None:
                new_children.append(child)
            elif isinstance(bound, tuple):
                _scoped_ok(child.name, bindings, scope)
                new_children.extend(bound)
            else:
                _scoped_ok(child.name, bindings, scope)
                new_children.append(bound)
        else:
            new_children.append(_subst(child, bindings, scope))

    # Rebuild via the same constructor. Smart constructors live on
    # Sum/Product via `.make()`, but we want structural preservation
    # here, not simplification. Direct constructor call via _rebuild
    # so types whose __init__ diverges from children (BracketApply
    # carries its bracket outside children) reconstruct correctly.
    rebuilt = pattern._rebuild(tuple(new_children))
    if _payload_has_wildcard(_pattern_payload(pattern)):
        rebuilt = _substitute_payload(rebuilt, bindings)
    return rebuilt


def _fresh_like(atom: Expr, avoid) -> Expr:
    from jacopy.core.traverse import contains

    cls = type(atom)
    base = getattr(atom, "name", None) or atom._repr_inner()
    for n in range(1, 1000):
        name = f"{base}_{n}"
        try:
            cand = cls(name, "bound")
        except TypeError:
            cand = cls(name)
        if not any(contains(e, cand) for e in avoid):
            return cand
    raise BinderEscapeError("no fresh dummy name")  # pragma: no cover


def _subst_indexed_sum(pattern, bindings: Bindings, scope: frozenset) -> Expr:
    """Capture-avoiding substitution under a Σ binder: when a value
    that is NOT bound by this Σ (a free term from elsewhere) mentions
    the binder's dummy, the dummy is renamed to a fresh atom (in the
    pattern body and in the values scoped to it)."""
    from jacopy.core.indexed_sum import IndexedSum

    pd = pattern.dummy
    if isinstance(pd, Wildcard):
        dummy = bindings.get(pd.name)
        if dummy is None or isinstance(dummy, tuple):
            raise PayloadSubstitutionError(f"unbound Σ dummy ?{pd.name}")
        if not dummy.is_atom:
            raise PayloadSubstitutionError(
                "an IndexedSum dummy must be bound to an atom"
            )
    else:
        dummy = pd
    scoped = bindings.get(_SCOPED, {})
    names = wildcard_names(pattern.body)
    values = [bindings[n] for n in names if n in bindings and n != getattr(pd, "name", None)]
    free_clash = [
        n for n in names
        if n in bindings and n != getattr(pd, "name", None)
        and dummy not in scoped.get(n, frozenset())
        and _mentions(bindings[n], dummy)
    ]
    body_pat = pattern.body
    if free_clash:
        flat = []
        for v in values:
            flat.extend(v if isinstance(v, tuple) else (v,))
        fresh = _fresh_like(dummy, flat + [body_pat])
        new_b = _MatchBindings(bindings)
        new_scoped = {}
        for n, ds in scoped.items():
            if dummy in ds:
                v = bindings.get(n)
                if isinstance(v, tuple):
                    new_b[n] = tuple(x.substitute_atom(dummy, fresh) for x in v)
                elif isinstance(v, Expr):
                    new_b[n] = v.substitute_atom(dummy, fresh)
                ds = (ds - {dummy}) | {fresh}
            new_scoped[n] = ds
        if new_scoped:
            new_b[_SCOPED] = new_scoped
        if isinstance(pd, Wildcard):
            new_b[pd.name] = fresh
        else:
            body_pat = body_pat.substitute_atom(pd, fresh)
        bindings, dummy = new_b, fresh
    body = _subst(body_pat, bindings, scope | {dummy})
    return IndexedSum(dummy, pattern.range_, body)


class PayloadSubstitutionError(ValueError):
    """A payload wildcard cannot be filled (unbound, or no handler)."""


class BinderEscapeError(PayloadSubstitutionError):
    """A value matched inside a Σ binder (it mentions the bound dummy)
    would be placed outside that binder."""


def has_wildcard(expr: Expr) -> bool:
    """True when ``expr`` contains a Wildcard/SeqWildcard anywhere —
    in its children or in a node's non-child payload."""
    if isinstance(expr, (Wildcard, SeqWildcard)):
        return True
    if expr.is_atom:
        return False
    if _payload_has_wildcard(node_payload(expr)):
        return True
    return any(has_wildcard(c) for c in expr.children)


def _payload_has_wildcard(pk: Any) -> bool:
    if pk is _CHILD:
        return False
    if isinstance(pk, Expr):
        return has_wildcard(pk)
    if type(pk) is tuple:
        return any(_payload_has_wildcard(k) for k in pk)
    return False


def _fill(e: Expr, bindings: Bindings) -> Expr:
    if not wildcard_names(e) <= set(bindings):
        raise PayloadSubstitutionError(
            f"unbound payload wildcard in {e._repr_inner()}"
        )
    return substitute(e, bindings)


def _substitute_payload(node: Expr, bindings: Bindings) -> Expr:
    hook = getattr(type(node), "_substitute_payload", None)
    if hook is not None:
        return hook(node, bindings)
    from jacopy.core.hodge import HodgeStar
    from jacopy.core.indexed_sum import IndexedSum

    if isinstance(node, IndexedSum):
        dummy = _fill(node.dummy, bindings)
        if not dummy.is_atom:
            raise PayloadSubstitutionError(
                "an IndexedSum dummy must be bound to an atom"
            )
        return IndexedSum(dummy, node.range_, node.body)
    if isinstance(node, HodgeStar):
        return HodgeStar(node.arg, node.dim, metric=_fill(node.metric, bindings))
    raise PayloadSubstitutionError(
        f"{type(node).__name__} has a wildcard in its payload but no "
        "payload substitution"
    )
