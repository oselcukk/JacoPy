"""
Property registry, the binding between expressions and their properties.

The registry answers two questions:

1. *Does this expression have property X?* Asked constantly by
   algorithms: ``is this a scalar?``, ``what's this operator's
   degree?``, ``is this bracket graded-antisymmetric?``.
2. *Why does it have property X?* Asked when writing proofs: was it
   an axiom the user declared, or derived earlier? If derived, by
   what rule?

Three ways to attach a property:

* :meth:`declare`, exact expression → property. Highest priority.
* :meth:`declare_for_class`, every instance of an :class:`Expr`
  subclass carries the property. Subclasses inherit via MRO.
* :meth:`declare_for_predicate`, any expression matching a
  user-supplied predicate carries the property. Checked last, in
  registration order.

Two scoping mechanisms support the foundational / custom proof modes:

* :meth:`scope`, rolls back every mutation inside the block on exit.
  Useful for hypothetical experiments and bracketing a proof inside a
  temporary declaration.
* :meth:`axioms`, narrows the visible property types to a whitelist.
  Within the block, any property whose type is not in the whitelist
  looks as if it had never been declared. This is how the ``custom``
  axiom mode from plan.md is implemented.

``strict_axioms_only`` is orthogonal to :meth:`axioms`: the former
filters by provenance (axiom vs derived), the latter by property
type.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from contextlib import contextmanager
from typing import Callable, Iterable, Iterator, List, Optional, Set, Tuple, Type, TypeVar

from jacopy.core.expr import Expr
from jacopy.core.properties import Property, Provenance

P = TypeVar("P", bound=Property)

#: Read tracking (audit 0b00e1b-FULL P0-3 / M1X-2): a proof step's
#: validity can depend on registry ANSWERS (``x`` is Scalar, ``p`` has
#: no Graded declaration …). :meth:`PropertyRegistry.get` is the single
#: query choke point; while a :func:`track_reads` block is open on this
#: thread, every answer is appended to the block's log as
#: ``(expr, property class, visible property or None)``. Off by
#: default: one attribute lookup per query.
_READS = threading.local()


def begin_reads() -> list:
    """Open a read log on this thread without a context manager (the
    expansion engine's hot path); close it with :func:`end_reads`."""
    stack = getattr(_READS, "stack", None)
    if stack is None:
        stack = _READS.stack = []
    log: list = []
    stack.append(log)
    return log


def end_reads(log: list, keep=None) -> None:
    """Close the log opened by :func:`begin_reads` and hand the reads
    that COUNT — ``keep`` (default: the whole log) — to the enclosing
    log. A read is appended only to the innermost open log; a consumer
    that discards part of its log (the engine drops the reads of the
    candidate rules that did not fire) keeps them out of every outer
    log too (review 2026-10-01 r3 #6)."""
    stack = getattr(_READS, "stack", None) or []
    # find THIS log by identity (list.remove compares by value — an
    # equal, e.g. empty, log would go); a log that is not open (never
    # opened, or closed twice) hands nothing to anyone
    for i in range(len(stack) - 1, -1, -1):
        if stack[i] is log:
            del stack[i]
            if i > 0:
                # the log it was opened INSIDE — not a later-opened one
                stack[i - 1].extend(log if keep is None else keep)
            return


@contextmanager
def track_reads():
    """Record every :meth:`PropertyRegistry.get` answer given inside the
    block (on this thread, any registry); yields the log list. On exit
    the block's reads are handed to the enclosing log, so nested blocks
    are seen by the outer ones."""
    log = begin_reads()
    try:
        yield log
    finally:
        end_reads(log)

Predicate = Callable[[Expr], bool]


#: Declaration LEVELS, most specific first: exact ``(0, 0)``, class
#: ``(1, mro index)``, predicate ``(2, 0)`` — every predicate is the
#: same level (registration order is a tie-break of the lookup, not a
#: specificity, so shadowing stays order-independent). A smaller tuple
#: is a strictly more specific declaration (the registry's own lookup
#: priority, applied ACROSS the Scalar-contract property types for
#: shadowing — see :class:`~jacopy.core.properties.Scalar`).
_EXACT = (0, 0)
_PREDICATE = (2, 0)


def _contract_types():
    from jacopy.core.properties import AntiCommuting, Graded, NonCommuting, Scalar

    return Scalar, Graded, NonCommuting, AntiCommuting


class PropertyRegistry:
    """Stores properties keyed by expression, class, or predicate.

    Lookup order in :meth:`get`:

    1. Exact expression match.
    2. Class-based: walks :attr:`type.__mro__` from most specific to
       :class:`Expr`.
    3. Predicate-based: first registered predicate whose property type
       matches wins.

    An expression or class may hold multiple *distinct* property types,
    but at most one of any given property-type from the same source
    (exact / class / predicate). Duplicate declarations at the same
    source raise :class:`ValueError`, the intended fix is an explicit
    :meth:`retract`.
    """

    def __init__(self, *, strict_axioms_only: bool = False) -> None:
        self._props: dict[Expr, dict[type, Property]] = defaultdict(dict)
        self._by_class: dict[type, dict[type, Property]] = defaultdict(dict)
        self._by_predicate: List[Tuple[Predicate, Property]] = []
        self._strict = strict_axioms_only
        self._axiom_whitelist: Optional[Set[type]] = None

    # ---- mode ------------------------------------------------------ #

    @property
    def strict_axioms_only(self) -> bool:
        return self._strict

    def set_strict(self, strict: bool) -> None:
        self._strict = bool(strict)

    # ---- mutation: exact --------------------------------------------- #

    def declare(self, expr: Expr, prop: Property) -> None:
        """Attach ``prop`` to the exact expression ``expr``."""
        if not isinstance(expr, Expr):
            raise TypeError("Registry key must be an Expr")
        if not isinstance(prop, Property):
            raise TypeError("Can only declare Property instances")
        bucket = self._props[expr]
        if type(prop) in bucket:
            raise ValueError(
                f"{type(prop).__name__} already declared on {expr!r}"
            )
        bucket[type(prop)] = prop
        if self._contract_relevant(prop):
            # the EFFECTIVE state after the mutation is validated; on a
            # contradiction the mutation is undone (order-independent:
            # whichever declaration comes last is the one refused)
            try:
                self._validate_contract(exprs=(expr,))
            except Exception:
                del bucket[type(prop)]
                raise

    # ---- Scalar contract (M1-1): levels, shadowing, validation ------- #

    @staticmethod
    def _contract_relevant(prop) -> bool:
        return isinstance(prop, _contract_types())

    def _raw(self, expr, prop_cls, mro=None):
        """``(property, level)`` of the UNFILTERED declaration that
        :meth:`get` would use for ``expr`` (or for a generic instance of
        the class whose ``mro`` is given when ``expr`` is ``None`` —
        predicates cannot be evaluated then). ``(None, None)`` when
        nothing is declared."""
        if expr is not None:
            prop = self._props.get(expr, {}).get(prop_cls)
            if prop is not None:
                return prop, _EXACT
            if mro is None:
                mro = type(expr).__mro__
        for i, cls in enumerate(mro):
            prop = self._by_class.get(cls, {}).get(prop_cls)
            if prop is not None:
                return prop, (1, i)
        if expr is not None:
            for pred, p in self._by_predicate:
                if isinstance(p, prop_cls) and pred(expr):
                    return p, _PREDICATE
        return None, None

    def _scalar_shadowed(self, expr, mro, level) -> bool:
        """Is a Scalar found at ``level`` shadowed by a STRICTLY more
        specific Graded / NonCommuting / AntiCommuting declaration?
        (Raw declarations: a visibility filter must not turn a declared
        function into a constant.)"""
        if level == _EXACT:
            return False
        for other in _contract_types()[1:]:
            _, other_level = self._raw(expr, other, mro)
            if other_level is not None and other_level < level:
                return True
        return False

    def _effective_scalar(self, expr, mro=None):
        """The effective (shadowing applied, unfiltered) Scalar answer."""
        scalar_cls = _contract_types()[0]
        prop, level = self._raw(expr, scalar_cls, mro)
        if prop is None or self._scalar_shadowed(expr, mro, level):
            return None
        return prop

    def _check_contract(self, expr, mro=None) -> None:
        """Refuse the EFFECTIVE answers for ``expr`` (or a generic
        instance of ``mro[0]``) when an unshadowed Scalar meets a
        clashing declaration (:func:`~jacopy.core.properties.scalar_contract_clash`)."""
        from jacopy.core.properties import ScalarContractError, scalar_contract_clash

        if expr is not None and mro is None:
            mro = type(expr).__mro__
        scalar = self._effective_scalar(expr, mro)
        if scalar is None:
            return
        _, graded_cls, nc_cls, ac_cls = _contract_types()
        clash = scalar_contract_clash(
            self._raw(expr, graded_cls, mro)[0],
            self._raw(expr, nc_cls, mro)[0],
            self._raw(expr, ac_cls, mro)[0],
        )
        if clash is not None:
            where = expr if expr is not None else f"<{mro[0].__name__}>"
            raise ScalarContractError(
                f"{where!r}: Scalar contradicts {clash!r} — Scalar means an "
                "ℝ-constant (degree 0, commutes with every operator); "
                "declare a function Graded(0) instead of Scalar"
            )

    def _validate_contract(self, *, exprs=(), classes=()) -> None:
        """Validate the effective state for the given exact expressions
        and for generic instances of the given classes (plus every
        registered subclass and every exact-declared instance)."""
        for e in exprs:
            self._check_contract(e)
        for cls in classes:
            seen = set()
            for sub in [cls] + [c for c in self._by_class if issubclass(c, cls)]:
                if sub not in seen:
                    seen.add(sub)
                    self._check_contract(None, mro=sub.__mro__)
            for e in list(self._props):
                if isinstance(e, cls):
                    self._check_contract(e)

    def retract(
        self, expr: Expr, prop_cls: Type[Property]
    ) -> Optional[Property]:
        """Remove the exact-expression property of type ``prop_cls``.
        A retract that would EXPOSE a Scalar contradiction (the removed
        declaration was shadowing one, or was the ``Graded(0)`` hiding
        a class-level ``Graded(k)``) is refused and leaves the registry
        unchanged."""
        bucket = self._props.get(expr)
        if bucket is None:
            return None
        prop = bucket.pop(prop_cls, None)
        if prop is not None and self._contract_relevant(prop):
            try:
                self._validate_contract(exprs=(expr,))
            except Exception:
                bucket[prop_cls] = prop
                raise
        return prop

    # ---- mutation: class-based -------------------------------------- #

    def declare_for_class(
        self, cls: Type[Expr], prop: Property
    ) -> None:
        """Attach ``prop`` to every instance of ``cls`` (subclasses inherit).

        Exact-expression declarations still take priority over class-based
        ones. An explicit :meth:`retract` on a particular expression does
        NOT remove the class-based fallback, it only clears an exact
        binding.
        """
        if not (isinstance(cls, type) and issubclass(cls, Expr)):
            raise TypeError("declare_for_class: `cls` must be an Expr subclass")
        if not isinstance(prop, Property):
            raise TypeError("declare_for_class: `prop` must be a Property")
        bucket = self._by_class[cls]
        if type(prop) in bucket:
            raise ValueError(
                f"{type(prop).__name__} already declared for class "
                f"{cls.__name__}"
            )
        bucket[type(prop)] = prop
        if self._contract_relevant(prop):
            # the EFFECTIVE answers after this declaration: a generic
            # instance of cls and of every registered subclass, and
            # every exact-declared instance (exact entries shadow)
            try:
                self._validate_contract(classes=(cls,))
            except Exception:
                del bucket[type(prop)]
                raise

    def retract_for_class(
        self, cls: Type[Expr], prop_cls: Type[Property]
    ) -> Optional[Property]:
        bucket = self._by_class.get(cls)
        if bucket is None:
            return None
        prop = bucket.pop(prop_cls, None)
        if prop is not None and self._contract_relevant(prop):
            try:
                self._validate_contract(classes=(cls,))
            except Exception:
                bucket[prop_cls] = prop
                raise
        return prop

    # ---- mutation: predicate-based ---------------------------------- #

    def declare_for_predicate(
        self, predicate: Predicate, prop: Property
    ) -> None:
        """Attach ``prop`` to every expression satisfying ``predicate``.

        Predicates are matched in registration order; the first matching
        entry whose property type is being queried wins. Use sparingly,
        a badly-written predicate is the usual way to silently poison a
        registry.
        """
        if not callable(predicate):
            raise TypeError(
                "declare_for_predicate: `predicate` must be callable"
            )
        if not isinstance(prop, Property):
            raise TypeError(
                "declare_for_predicate: `prop` must be a Property"
            )
        self._by_predicate.append((predicate, prop))
        if self._contract_relevant(prop):
            # the effective answers of every exact-declared expression
            # the predicate covers; a predicate cannot be enumerated
            # further, so the predicate-level contract is ALSO enforced
            # at query time (scalar_contract_certified default-rejects)
            try:
                self._validate_contract(
                    exprs=[e for e in list(self._props) if predicate(e)]
                )
            except Exception:
                self._by_predicate.pop()
                raise

    # ---- query ----------------------------------------------------- #

    def _filter(self, prop: Optional[Property]) -> Optional[Property]:
        """Apply strict-mode and axiom-whitelist visibility filters."""
        if prop is None:
            return None
        if self._strict and prop.provenance is Provenance.DERIVED:
            return None
        if (
            self._axiom_whitelist is not None
            and type(prop) not in self._axiom_whitelist
        ):
            return None
        return prop

    def get(
        self, expr: Expr, prop_cls: Type[P]
    ) -> Optional[P]:
        """Return the property of type ``prop_cls`` on ``expr``, or ``None``.

        Lookup cascades: exact → class (MRO) → predicate. The first
        hit, after applying visibility filters, is returned — except
        that a class/predicate-level :class:`~jacopy.core.properties.Scalar`
        shadowed by a strictly more specific ``Graded`` / ``NonCommuting``
        / ``AntiCommuting`` declaration answers ``None`` (the Scalar
        contract's specificity rule).
        """
        prop, level = self._raw(expr, prop_cls)
        if (
            prop is not None
            and level != _EXACT
            and isinstance(prop, _contract_types()[0])
            and self._scalar_shadowed(expr, None, level)
        ):
            # Scalar contract (M1-1): a generic-level Scalar is shadowed
            # by a strictly more specific Graded / NonCommuting /
            # AntiCommuting declaration — the expression is a graded
            # element (a function for Graded(0)), not a constant
            prop = None
        visible = self._filter(prop)
        stack = getattr(_READS, "stack", None)
        if stack:
            stack[-1].append((expr, prop_cls, visible))
        return visible  # type: ignore[return-value]

    def has(self, expr: Expr, prop_cls: Type[Property]) -> bool:
        return self.get(expr, prop_cls) is not None

    def peek(self, expr: Expr, prop_cls: Type[P]) -> Optional[P]:
        """:meth:`get`'s answer WITHOUT recording a read: a pre-filter
        for a caller whose result depends only on a POSITIVE answer,
        which it then re-queries with :meth:`get` so the answer becomes
        the step's hypothesis (negative answers do not pile up)."""
        with self.untracked():
            return self.get(expr, prop_cls)

    @contextmanager
    def untracked(self):
        """Suspend read recording on this thread for the block (the
        model oracle restates registry data without minting
        hypotheses; :meth:`peek`)."""
        stack = getattr(_READS, "stack", None)
        _READS.stack = None
        try:
            yield self
        finally:
            _READS.stack = stack

    def all_for(self, expr: Expr) -> Iterator[Property]:
        """Yield every property visible for ``expr`` (after filters).

        Collects candidate property types across all three sources and
        resolves each via :meth:`get` so priority and filters apply
        uniformly.
        """
        candidate_types: Set[type] = set()
        candidate_types.update(self._props.get(expr, {}).keys())
        for cls in type(expr).__mro__:
            candidate_types.update(self._by_class.get(cls, {}).keys())
        for pred, p in self._by_predicate:
            if pred(expr):
                candidate_types.add(type(p))
        for prop_cls in candidate_types:
            prop = self.get(expr, prop_cls)
            if prop is not None:
                yield prop

    # ---- scope / axiom context managers ----------------------------- #

    def _snapshot(self):
        return (
            {k: dict(v) for k, v in self._props.items()},
            {k: dict(v) for k, v in self._by_class.items()},
            list(self._by_predicate),
            self._strict,
            self._axiom_whitelist,
        )

    def _restore(self, snap) -> None:
        props, by_class, preds, strict, whitelist = snap
        self._props = defaultdict(dict, props)
        self._by_class = defaultdict(dict, by_class)
        self._by_predicate = preds
        self._strict = strict
        self._axiom_whitelist = whitelist

    @contextmanager
    def scope(self):
        """Roll back every registry mutation made inside the block.

        Designed for hypothetical edits: declare a property, run a proof,
        and have the declaration vanish afterwards even if the proof
        raised. Safe to nest.
        """
        snap = self._snapshot()
        try:
            yield self
        finally:
            self._restore(snap)

    @contextmanager
    def axioms(self, allowed: Iterable[Type[Property]]):
        """Narrow the visible property types to ``allowed`` during the block.

        Within the block, :meth:`get` returns ``None`` for any property
        whose type is not in ``allowed``, as if it had not been
        declared. Complements :attr:`strict_axioms_only`, which filters
        by provenance rather than type.

        Nests correctly: an inner ``axioms()`` overrides the outer
        whitelist for its scope and restores on exit.
        """
        allowed_set: Set[type] = set(allowed)
        for c in allowed_set:
            if not (isinstance(c, type) and issubclass(c, Property)):
                raise TypeError(
                    "axioms: every entry must be a Property subclass"
                )
        prev = self._axiom_whitelist
        self._axiom_whitelist = allowed_set
        try:
            yield self
        finally:
            self._axiom_whitelist = prev

    # ---- dunder ---------------------------------------------------- #

    def __len__(self) -> int:
        return (
            sum(len(b) for b in self._props.values())
            + sum(len(b) for b in self._by_class.values())
            + len(self._by_predicate)
        )

    def __contains__(self, expr: object) -> bool:
        if not isinstance(expr, Expr):
            return False
        if self._props.get(expr):
            return True
        for cls in type(expr).__mro__:
            if self._by_class.get(cls):
                return True
        for pred, _ in self._by_predicate:
            if pred(expr):
                return True
        return False


# --------------------------------------------------------------------- #
# Module-level default                                                  #
# --------------------------------------------------------------------- #

_default_registry: PropertyRegistry = PropertyRegistry()


def default_registry() -> PropertyRegistry:
    """Return the process-wide default registry.

    Convenient for quick interactive use. For serious work, construct
    an explicit :class:`PropertyRegistry` so contexts don't bleed
    across computations.
    """
    return _default_registry


def reset_default_registry() -> None:
    """Replace the default registry with a fresh, empty one."""
    global _default_registry
    _default_registry = PropertyRegistry()
