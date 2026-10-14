"""
Structure kinds and node families — the registry behind
:func:`~jacopy.research.engine_assembly.assemble_engine`.

``assemble_engine`` used to know the Nambu-Poisson structure by name: it
imported ``NambuSharpVF`` to scan, keyed structures by ``s.pi``, called
the drinfeld tilde-engine builder as the "host" and added the
sharp-slot rules under a hard-coded ``"nambu_sharp"`` tag. It now knows
only three registries, filled by whoever defines a structure:

* **node families** (:func:`register_family`) — which node classes the
  :class:`~jacopy.research.engine_assembly.Scan` detects, under which
  tag; a family may say which structure OWNS each node
  (``owner_key(node)``, e.g. a Nambu sharp's ``Π``) and whether its
  operators have additive direction slots;
* **family rules** (:func:`register_family_rule`) — a rule added when
  the scanned families satisfy a condition; ``order`` fixes its place
  among all family rules (the engine's registration order is part of
  its behaviour, so it is explicit);
* **structure kinds** (:func:`register_structure_kind`) — for a
  structure object: its tree key (matched against the scanned
  ``owner_key`` values), the base engine it builds when it is the
  first ("host") structure, and its report lines.

A structure is also a provider (:mod:`jacopy.research.providers`):
every structure after the host contributes ``engine_rules(registry)``.

Adding a structure type without editing the library::

    from jacopy.research.structure_kinds import StructureKind, register_structure_kind

    class MyKind(StructureKind):
        name = "my-structure"
        def accepts(self, s):        return isinstance(s, MyStructure)
        def key(self, s):            return s.name      # what owner_key() returns for its nodes

    register_structure_kind(MyKind())
    register_family(MySharp, "my_sharp", owner_key=lambda n: n.owner_name)   # optional
    eng = assemble_engine(expr, structures=(my_structure,))

The default :class:`StructureKind` hosts on the tangent (Cartan) engine
and adds the structure's own ``engine_rules`` (each reported); override
:meth:`StructureKind.host_engine` (with ``host_includes_rules = True``
when it already registers them) for a richer base. The built-in
Nambu-Poisson kind is :mod:`jacopy.research.nambu_kind`.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, List, Optional, Tuple

from jacopy.proof.expansion import Definition, ExpansionEngine


# ------------------------------------------------------------------ #
# Node families                                                       #
# ------------------------------------------------------------------ #


@dataclass(frozen=True)
class NodeFamily:
    """A node class the scan detects under ``tag``.

    ``owner_key(node)`` — when given, the key of the structure that
    owns ``node`` (a structure-specific node such as a sharp map); the
    engine refuses nodes whose owner is not among ``structures``.
    ``additive_slots`` — the family's operators carry additive
    direction slots (they trigger ``OperatorSlotAdditivityDefinition``).
    """

    cls: type
    tag: str
    owner_key: Optional[Callable[[Any], Any]] = None
    additive_slots: bool = False


@dataclass(frozen=True)
class FamilyRule:
    """A rule added when ``when(families)`` holds; ``build(registry)``
    makes it, ``why`` is its report reason, ``order`` its place."""

    order: float
    seq: int
    when: Callable[[FrozenSet[str]], bool] = field(compare=False)
    build: Callable[[Any], Definition] = field(compare=False)
    why: str = field(compare=False)
    #: what makes two registrations "the same" (:func:`register_family_rule`
    #: is idempotent on it): the ``when`` spec, ``build``, ``why``, ``order``
    spec: Any = field(default=None, compare=False, repr=False)


_FAMILIES: List[NodeFamily] = []
_FAMILY_RULES: List[FamilyRule] = []
_KINDS: List["StructureKind"] = []
_SEQ = itertools.count()


def register_family(
    cls: type,
    tag: str,
    *,
    owner_key: Optional[Callable[[Any], Any]] = None,
    additive_slots: bool = False,
) -> NodeFamily:
    """Register a node family; re-registering the same ``(cls, tag)``
    replaces the earlier entry in place (idempotent imports). The
    library's own families are always loaded first
    (:func:`ensure_builtin_kinds`)."""
    ensure_builtin_kinds()
    fam = NodeFamily(cls, tag, owner_key, additive_slots)
    for i, old in enumerate(_FAMILIES):
        if old.cls is cls and old.tag == tag:
            _FAMILIES[i] = fam
            return fam
    _FAMILIES.append(fam)
    return fam


def families() -> Tuple[NodeFamily, ...]:
    """The registered node families, in registration order (the
    library's own first)."""
    ensure_builtin_kinds()
    return tuple(_FAMILIES)


def additive_slot_tags() -> FrozenSet[str]:
    """Tags whose operators have additive direction slots."""
    ensure_builtin_kinds()
    return frozenset(f.tag for f in _FAMILIES if f.additive_slots)


def register_family_rule(
    when,
    build: Callable[[Any], Definition],
    why: str,
    *,
    order: float,
) -> FamilyRule:
    """Add ``build(registry)`` to an assembled engine when the scanned
    families satisfy ``when``: a tag (``"wedge"``), a set of tags (ALL
    present) or a predicate ``families -> bool``. Rules are added in
    ascending ``order`` (ties: registration order).

    Idempotent: registering the same rule again (same ``when`` tag /
    tag set / predicate object, same ``build`` object, ``why`` and
    ``order``) returns the existing entry instead of adding a second
    copy. The library's own rules are always loaded first
    (:func:`ensure_builtin_kinds`)."""
    ensure_builtin_kinds()
    if isinstance(when, str):
        tag = when
        pred = lambda fam, _t=tag: _t in fam  # noqa: E731
        when_spec = ("tag", tag)
    elif callable(when):
        pred = when
        when_spec = ("predicate", id(when))
    else:
        tags = frozenset(when)
        pred = lambda fam, _t=tags: _t <= fam  # noqa: E731
        when_spec = ("tags", tags)
    spec = (when_spec, id(build), why, order)
    for old in _FAMILY_RULES:
        if old.spec == spec and (
            when_spec[0] != "predicate" or old.when is when
        ) and old.build is build:
            return old
    rule = FamilyRule(order, next(_SEQ), pred, build, why, spec)
    _FAMILY_RULES.append(rule)
    return rule


def family_rules() -> Tuple[FamilyRule, ...]:
    """The registered family rules in the order they are applied (the
    library's own are always loaded first)."""
    ensure_builtin_kinds()
    return tuple(sorted(_FAMILY_RULES, key=lambda r: (r.order, r.seq)))


# ------------------------------------------------------------------ #
# Structure kinds                                                     #
# ------------------------------------------------------------------ #


class StructureKind:
    """How :func:`assemble_engine` treats one type of structure.

    Subclass and override :meth:`accepts` and :meth:`key` (required);
    :meth:`host_engine`, :meth:`host_report` and :meth:`member_report`
    have generic defaults that use only the provider protocol."""

    #: short label of the kind (reports, error messages)
    name: str = "structure"

    #: ``True`` when :meth:`host_engine` already registers the host's
    #: own rules; ``False`` (default) — the host contributes
    #: ``engine_rules`` like every other structure, each rule reported
    host_includes_rules: bool = False

    def accepts(self, structure) -> bool:
        raise NotImplementedError

    def key(self, structure):
        """The structure's tree key — what ``owner_key(node)`` returns
        for the nodes it owns; distinct structures need distinct keys."""
        raise NotImplementedError

    def host_engine(self, structure, registry) -> ExpansionEngine:
        """The base engine when ``structure`` is the first structure:
        by default the tangent (Cartan) engine; the structure's own
        rules (provider protocol) are then added and reported by
        ``assemble_engine`` (see :attr:`host_includes_rules`)."""
        from jacopy.central.tangent.tangent_expansion import tangent_engine

        return tangent_engine(registry=registry)

    def host_report(self, structure) -> str:
        return f"base: tangent (Cartan) engine, first structure {structure.name} [{self.name}]"

    def member_report(self, structure) -> str:
        return f"structure {structure.name}: declarations {sorted(structure.declarations) or 'none'}"


def register_structure_kind(kind: StructureKind, *, first: bool = False) -> StructureKind:
    """Register ``kind``; the first kind whose ``accepts`` is true
    handles a structure (``first=True`` puts ``kind`` in front). The
    library's own kinds are always loaded first
    (:func:`ensure_builtin_kinds`), so a kind registered without
    ``first=True`` never takes precedence over a built-in one, whatever
    the import order."""
    ensure_builtin_kinds()
    if kind in _KINDS:
        return kind
    if first:
        _KINDS.insert(0, kind)
    else:
        _KINDS.append(kind)
    return kind


def unregister_structure_kind(kind: StructureKind) -> None:
    ensure_builtin_kinds()
    if kind in _KINDS:
        _KINDS.remove(kind)


def unregister(entry) -> None:
    """Remove a family, family rule or structure kind (tests, sessions)."""
    ensure_builtin_kinds()
    for reg in (_FAMILIES, _FAMILY_RULES, _KINDS):
        if entry in reg:
            reg.remove(entry)
            return


def structure_kind_of(structure) -> StructureKind:
    """The registered kind handling ``structure``; ``TypeError`` when
    none does (the engine will not guess a structure's rules)."""
    ensure_builtin_kinds()
    for kind in _KINDS:
        if kind.accepts(structure):
            return kind
    raise TypeError(
        f"assemble_engine: no structure kind is registered for {structure!r} — "
        "register one with jacopy.research.structure_kinds.register_structure_kind"
    )


# ------------------------------------------------------------------ #
# Built-ins (loaded lazily: the central families/rules and the        #
# Nambu-Poisson kind live in modules that import the packages)        #
# ------------------------------------------------------------------ #

_BUILTINS_LOADED = False
_BUILTINS_LOADING = False


def ensure_builtin_kinds() -> None:
    """Load the library's own families, family rules and kinds once.

    Every registry function (register and read) calls this first, so
    the built-ins always precede user entries and the registries never
    depend on which was touched first (arch-core gate L1/L2). The
    built-ins' own registrations run while loading and do not recurse.
    """
    global _BUILTINS_LOADED, _BUILTINS_LOADING
    if _BUILTINS_LOADED or _BUILTINS_LOADING:
        return
    _BUILTINS_LOADING = True
    try:
        from jacopy.research import engine_assembly, nambu_kind

        engine_assembly._register_central_builtins()
        nambu_kind.register()
        _BUILTINS_LOADED = True
    finally:
        _BUILTINS_LOADING = False


__all__ = [
    "FamilyRule",
    "NodeFamily",
    "StructureKind",
    "additive_slot_tags",
    "ensure_builtin_kinds",
    "families",
    "family_rules",
    "structure_kind_of",
    "register_family",
    "register_family_rule",
    "register_structure_kind",
    "unregister",
    "unregister_structure_kind",
]
