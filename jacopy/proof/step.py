"""
Single proof step.

A :class:`ProofStep` records one rewrite: ``before`` is the expression
before the rule fired, ``after`` is the expression after, and ``rule``
/ ``justification`` name what was applied and why. Steps nest, a
strategy that decomposes its work into sub-proofs records them under
:attr:`children`, which lets the transcript be rendered at any
verbosity level by choosing how deep to unfold each step.

The class is deliberately thin: no checks beyond type validation on
``before`` / ``after``, no automatic semantic interpretation of
``rule``. The proof-validity invariant, that ``after`` actually
follows from ``before`` under ``rule``, is the responsibility of
whatever code constructed the step. This keeps the data type a pure
record that tracers, strategies, and display modules can all share
without coupling.
"""

from __future__ import annotations

import weakref
from typing import List, Optional, Tuple

from jacopy.core.expr import Expr


#: Steps MINTED by the library's own producers.
#:
#: Threat model. Ordinary use of the public API — accidental or
#: deliberate — cannot claim provenance: a step's provenance (that the engine, a library
#: normalization pass or a library strategy produced it from an actual
#: computation) must not be claimable through the public API: a
#: ``ProofStep(..., key=..., provenance_tag=...)`` built by any caller —
#: by accident or deliberately — is NEVER minted, whatever metadata it
#: carries; copies are not minted either. Only producer code inside
#: :mod:`jacopy.proof` calls :func:`_mint` (the trusted computing base;
#: patching module internals is outside the model, as in any Python
#: library). Membership is by object IDENTITY and exact type
#: (``type(step) is ProofStep``): a subclass cannot impersonate a minted
#: step through ``__eq__`` / ``__hash__``. Out of scope (the Python
#: limit): code that subclasses, monkeypatches or imports the private
#: minting function on purpose. Minting certifies ORIGIN only — that
#: the step is the producer's record — not that the rule is
#: mathematically right: the step's ``before = after`` is the rule's
#: responsibility, checked independently by the model oracle
#: (``check_chain``).
_MINTED: dict = {}


def _mint(step: "ProofStep") -> "ProofStep":
    """Record ``step`` as produced by a library producer (private)."""
    if type(step) is ProofStep:
        k = id(step)

        def _forget(ref, k=k):
            if _MINTED.get(k) is ref:
                del _MINTED[k]

        _MINTED[k] = weakref.ref(step, _forget)
    return step


def is_minted(step) -> bool:
    """True when ``step`` was produced by the library's own producers
    (engine, normalization passes, strategies) — see :data:`_MINTED`."""
    if type(step) is not ProofStep:
        return False
    ref = _MINTED.get(id(step))
    return ref is not None and ref() is step


def classification_label(provenance_tag: Optional[str], role: Optional[str]) -> Optional[str]:
    """The reader-facing classification of a step, in the terms
    :class:`~jacopy.proof.result.ProofResult` counts it with.

    ``provenance_tag`` alone says only whether a rule fired as given
    (``"axiom"``) or as derivable (``"theorem"``); the rule's logical
    ``role`` refines it:

    * role ``"assumption"`` → ``"assumption"`` (a declared axiom, even
      when theorem-tagged);
    * tag ``"theorem"`` → ``"theorem"``;
    * tag ``"axiom"`` with role ``"definition"`` → ``"definition"``
      (ProofResult lists it under provenance, not as an assumption);
    * tag ``"axiom"`` with no recorded role → ``"axiom"`` (a hand-built
      or unmigrated step; ProofResult counts it as a legacy assumption);
    * otherwise the tag itself (``"computation"`` / ``None``).

    Display metadata only: nothing in the proof logic reads it."""
    if role == "assumption":
        return "assumption"
    if provenance_tag == "theorem":
        return "theorem"
    if provenance_tag == "axiom" and role == "definition":
        return "definition"
    return provenance_tag


class ProofStep:
    """One rewrite: ``before → after`` under ``rule``."""

    __slots__ = (
        "_before",
        "_after",
        "_rule",
        "_justification",
        "_children",
        "_provenance_tag",
        "_owner",
        "_role",
        "_cites",
        "_key",
        "_registry_facts",
        "_source",
        "__weakref__",
    )

    #: Recognised provenance tags. ``None`` means the step carries no
    #: provenance claim (e.g. a structural rewrite like ``product-rule``).
    #:
    #: * ``"axiom"``, primitive equation accepted as input.
    #: * ``"theorem"``, derived from other primitives; foundational
    #:   mode can recover the sub-proof.
    #: * ``"computation"``, a frame-component / numerical-symbolic
    #:   step (typically Stage G of :mod:`jacopy.frame_calc`); not a
    #:   citation but a calculation. Carries the same paper-grade
    #:   render path as axiom / theorem.
    _VALID_TAGS = (None, "axiom", "theorem", "computation")

    def __init__(
        self,
        before: Expr,
        after: Expr,
        rule: str,
        justification: str = "",
        children: Optional[List["ProofStep"]] = None,
        *,
        provenance_tag: Optional[str] = None,
        owner=None,
        role: Optional[str] = None,
        cites=None,
        key=None,
        registry_facts=(),
        source=None,
    ) -> None:
        if not isinstance(before, Expr):
            raise TypeError("ProofStep.before must be an Expr")
        if not isinstance(after, Expr):
            raise TypeError("ProofStep.after must be an Expr")
        if not isinstance(rule, str):
            raise TypeError("ProofStep.rule must be a str")
        if not isinstance(justification, str):
            raise TypeError("ProofStep.justification must be a str")
        if provenance_tag not in self._VALID_TAGS:
            raise ValueError(
                f"provenance_tag must be one of {self._VALID_TAGS}, "
                f"got {provenance_tag!r}"
            )
        self._before = before
        self._after = after
        self._rule = rule
        self._justification = justification
        self._provenance_tag = provenance_tag
        # the structure whose rule fired (None = structure-free)
        self._owner = owner
        # the logical role of the fired rule:
        # "definition" | "assumption" | "theorem" | None (unrecorded)
        self._role = role
        # the cited Theorem record when this step is a citation:
        # its requirements propagate to the citing proof
        self._cites = cites
        # the structural key of the licensing rule (Definition.key); an
        # assumption step without one cannot be located in another engine
        self._key = key
        # the registry answers the step's producer consulted:
        # ``RegistryFact`` records; a theorem whose
        # steps carry them is citable only where the registry agrees
        self._registry_facts = tuple(registry_facts or ())
        # literature source of the licensing rule (metadata only: a
        # :class:`jacopy.bibliography.Citation` or a tuple of them,
        # copied from ``Definition.source`` / ``Theorem.source``); no
        # proof logic reads it
        if source is not None:
            from jacopy.bibliography import as_citations

            source = as_citations(source)
        self._source = source or None
        self._children: List[ProofStep] = []
        if children:
            for ch in children:
                self.add_child(ch)

    @property
    def before(self) -> Expr:
        return self._before

    @property
    def after(self) -> Expr:
        return self._after

    @property
    def rule(self) -> str:
        return self._rule

    @property
    def justification(self) -> str:
        return self._justification

    @property
    def children(self) -> Tuple["ProofStep", ...]:
        return tuple(self._children)

    @property
    def provenance_tag(self) -> Optional[str]:
        """Classification of this step: ``"axiom"``, ``"theorem"``, or ``None``.

        Set by the expansion engine when a :class:`Definition` fires, the
        tag records whether the rewrite was taken axiomatically or whether
        it's derivable, which :class:`UnrollToFoundations` reads to decide
        whether to attach a sub-proof.
        """
        return self._provenance_tag

    @property
    def classification(self) -> Optional[str]:
        """Reader-facing label: ``"definition"``, ``"assumption"``,
        ``"theorem"``, ``"axiom"`` (no role recorded), ``"computation"``
        or ``None`` — see :func:`classification_label`. The renderers
        print it as ``(definition)`` etc."""
        return classification_label(self._provenance_tag, self._role)

    @property
    def owner(self):
        """The structure whose rule fired this step (``None`` when the
        rule is structure-free or the step was built by hand)."""
        return self._owner

    @property
    def role(self) -> Optional[str]:
        """Logical role of the fired rule: ``"definition"``,
        ``"assumption"`` (a declared axiom), ``"theorem"``, or ``None``
        when the step recorded none (hand-built / legacy)."""
        return self._role

    @property
    def cites(self):
        """The cited :class:`~jacopy.proof.theorems.Theorem` when this
        step is a theorem citation, else ``None``."""
        return self._cites

    @property
    def key(self):
        """Structural key of the rule that fired (``Definition.key``);
        ``None`` for a hand-built step."""
        return self._key

    @property
    def registry_facts(self) -> tuple:
        """The registry answers (:class:`~jacopy.proof.registry_facts.RegistryFact`)
        this step's computation consulted; ``()`` when it consulted none
        or its producer does not record them."""
        return self._registry_facts

    @property
    def source(self):
        """The literature citations of the rule that fired — a tuple of
        :class:`jacopy.bibliography.Citation`, or ``None`` when the rule
        names no source (structural rewrites, hand-built steps).
        Display metadata only."""
        return self._source

    def add_child(self, step: "ProofStep") -> None:
        """Nest ``step`` under this one as a sub-proof."""
        if not isinstance(step, ProofStep):
            raise TypeError("ProofStep.add_child expects a ProofStep")
        self._children.append(step)

    def format(self, indent: int = 0, max_depth: int = 64) -> str:
        """Render this step as text; recurse into children up to ``max_depth``."""
        pad = "  " * indent
        label = self.classification
        tag = f" ({label})" if label else ""
        head = (
            f"{pad}[{self._rule}]{tag} "
            f"{self._before._repr_inner()} → {self._after._repr_inner()}"
        )
        if self._justification:
            head = f"{head} , {self._justification}"
        lines = [head]
        if max_depth > 0 and self._children:
            for ch in self._children:
                lines.append(ch.format(indent + 1, max_depth - 1))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"ProofStep(rule={self._rule!r}, "
            f"{self._before!r} → {self._after!r})"
        )
