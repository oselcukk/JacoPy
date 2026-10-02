"""
Registry declarations as proof requirements (audit 0b00e1b-FULL P0-3
≡ M1X-2, with K2-16).

A proof step's validity can depend on what the property registry
ANSWERS: ``x`` is :class:`~jacopy.core.properties.Scalar` (so it
commutes past an operator), ``p`` carries ``Graded(0)`` (so ``pq = qp``),
``q`` has NO grading declared (so it defaults to degree 0) … Such an
answer is a hypothesis of the proof exactly like a declared axiom; a
theorem proved under it must not be cited where the registry answers
differently.

Model.

* :class:`RegistryFact` — one answer ``(expr, property class, visible
  value)``; the value is the property's mathematical content (its
  class and payload fields; provenance / proof references are not
  content) or ``None`` for "not declared".
* Producers that run registry-aware computations record the answers
  their computation consulted on the step they emit
  (:attr:`ProofStep.registry_facts`): the expansion engine for the
  rule that fired (its ``matches`` and ``rewrite``), the
  normalization passes and :func:`~jacopy.proof.result.prove`'s
  simplify steps. The recording is :func:`jacopy.core.registry.track_reads`.
* :func:`~jacopy.proof.result._classify` turns them into requirement
  records of kind ``"registry"`` — a record per declared property, one
  aggregated record for the "not declared" answers.
* A citation is valid only in a registry context that answers every
  recorded query the same way (:func:`unmet`). The citing context is
  the registry the citing driver runs under (:func:`registry_context`,
  entered by ``prove`` / ``normalize`` / the strategies); when it is
  unknown, a registry-dependent theorem is NOT citable (default
  reject). ``None`` as the context registry means "nothing declared".

Soundness argument: a recorded step depends on the registry only
through the answers its producer consulted; a context that gives the
same answers reproduces the same step.
"""

from __future__ import annotations

import contextvars
import dataclasses
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from jacopy.core.expr import Expr

_UNSET = object()
_CONTEXT = contextvars.ContextVar("jacopy_proof_registry_context", default=_UNSET)

#: Assumption key tags for the two record shapes.
DECLARED_TAG = "registry"
UNDECLARED_TAG = "registry-undeclared"


def _hashable(x):
    try:
        hash(x)
        return x
    except TypeError:
        return repr(x)


def property_content(prop) -> Optional[tuple]:
    """The mathematical content of a visible property, ``None`` for
    "not declared": its class and payload fields (``provenance`` /
    ``proof`` are bookkeeping, not content)."""
    if prop is None:
        return None
    payload = ()
    if dataclasses.is_dataclass(prop):
        payload = tuple(
            (f.name, _hashable(getattr(prop, f.name)))
            for f in dataclasses.fields(prop)
            if f.name not in ("provenance", "proof")
        )
    return (type(prop), payload)


@dataclass(frozen=True)
class RegistryFact:
    """One registry answer a proof step relied on."""

    expr: Expr
    prop_cls: type
    value: Optional[tuple]
    #: a RAW-declaration fact (:meth:`PropertyRegistry.lookup`): the
    #: Scalar contract's clash check reads the raw declarations, so its
    #: hypotheses are checked against the raw declarations of the
    #: citing registry, not its filtered view (gate-6 cr6/p05)
    raw: bool = False

    @property
    def declared(self) -> bool:
        return self.value is not None

    def describe(self) -> str:
        what = self.prop_cls.__name__
        tag = " (raw declaration)" if self.raw else ""
        if self.value is None:
            return f"{self.expr._repr_inner()} has no {what} declared{tag}"
        payload = ", ".join(f"{k}={v}" for k, v in self.value[1])
        return f"{what}({payload}) on {self.expr._repr_inner()}{tag}"

    def __str__(self) -> str:
        return self.describe()


def facts_from_log(log: Iterable[tuple]) -> Tuple[RegistryFact, ...]:
    """Deduplicated facts of a :func:`track_reads` log (first-seen order)."""
    out: dict = {}
    for entry in log:
        expr, prop_cls, visible = entry[:3]
        f = RegistryFact(expr, prop_cls, property_content(visible), raw=len(entry) > 3)
        out.setdefault(f, None)
    return tuple(out)


def answer(registry, fact: RegistryFact) -> Optional[tuple]:
    """What ``registry`` answers to ``fact``'s query (``None`` registry:
    nothing declared)."""
    if registry is None:
        return None
    if fact.raw:
        return property_content(registry.lookup(fact.expr, fact.prop_cls)[0])
    return property_content(registry.get(fact.expr, fact.prop_cls))


def unmet(facts: Iterable[RegistryFact], registry) -> Tuple[RegistryFact, ...]:
    """The facts ``registry`` answers differently."""
    return tuple(f for f in facts if answer(registry, f) != f.value)


# ------------------------------------------------------------------ #
# the citing context                                                 #
# ------------------------------------------------------------------ #


@contextmanager
def registry_context(registry):
    """Run the block with ``registry`` as the proof's registry context
    (the registry a citation's registry requirements are checked
    against). ``None`` is a valid context: nothing declared."""
    token = _CONTEXT.set((registry,))
    try:
        yield registry
    finally:
        _CONTEXT.reset(token)


def in_registry_context(method):
    """Decorator for a strategy's ``prove(self, lhs, rhs, *, registry=…)``:
    the body runs with its ``registry`` keyword as the proof context."""
    import functools

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        with registry_context(kwargs.get("registry")):
            return method(*args, **kwargs)

    return wrapper


def current_context():
    """``(registry,)`` when a context is set, else ``None`` (unknown)."""
    v = _CONTEXT.get()
    return None if v is _UNSET else v


# ------------------------------------------------------------------ #
# requirement records                                                #
# ------------------------------------------------------------------ #


def requirement_records(facts: Iterable[RegistryFact]):
    """The ``"registry"`` :class:`~jacopy.proof.result.Assumption`
    records of a set of facts: one per declared property, one
    aggregate for the "not declared" answers."""
    from jacopy.proof.result import Assumption

    facts = tuple(dict.fromkeys(facts))
    out = [
        Assumption("registry", f"registry declaration: {f.describe()}", example=f.expr, key=(DECLARED_TAG, f))
        for f in facts if f.declared
    ]
    undeclared = tuple(f for f in facts if not f.declared)
    if undeclared:
        shown = "; ".join(f.describe() for f in undeclared[:3])
        more = f"; … ({len(undeclared)} in all)" if len(undeclared) > 3 else ""
        out.append(Assumption(
            "registry", f"registry: relies on undeclared properties ({shown}{more})",
            key=(UNDECLARED_TAG, undeclared),
        ))
    return tuple(out)


def facts_of(requires) -> Tuple[RegistryFact, ...]:
    """The facts carried by the ``"registry"`` records of ``requires``."""
    out: dict = {}
    for a in requires or ():
        if getattr(a, "kind", None) != "registry":
            continue
        key = getattr(a, "key", None)
        if not isinstance(key, tuple) or len(key) != 2:
            continue
        if key[0] == DECLARED_TAG:
            out.setdefault(key[1], None)
        elif key[0] == UNDECLARED_TAG:
            for f in key[1]:
                out.setdefault(f, None)
    return tuple(out)


def step_facts(steps) -> Tuple[RegistryFact, ...]:
    """Every fact recorded on ``steps`` and their children."""
    out: dict = {}

    def walk(seq):
        for s in seq:
            for f in getattr(s, "registry_facts", ()) or ():
                out.setdefault(f, None)
            walk(s.children)

    walk(steps)
    return tuple(out)


__all__ = [
    "RegistryFact",
    "answer",
    "current_context",
    "facts_from_log",
    "facts_of",
    "property_content",
    "registry_context",
    "requirement_records",
    "step_facts",
    "unmet",
]
