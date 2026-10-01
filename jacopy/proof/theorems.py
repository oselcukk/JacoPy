"""
Theorem Book — registry of proven results + the derived-rule bridge
(Engine pass E.3; ported from v2 and extended for the Phase 2
definition policy).

A :class:`Theorem` stores, besides the human-readable record, the
**equation itself** (``lhs``/``rhs`` Exprs) and a **generality tag**
declaring at which level the proof closed (an operator-level identity
holds for every degree; a ``p=2`` unroll only witnesses that instance).

The bridge to the engine is :class:`TheoremDefinition`: a *derived*
:class:`~jacopy.proof.expansion.Definition` built from a proven
theorem. It rewrites ``lhs → rhs``, carries the stored proof as its
``theorem_proof_builder`` (so ``mode="foundational"`` inlines the full
derivation under the step), and is tagged ``"theorem"`` in the
resulting :class:`ProofStep`. Per the definition policy, such rules are
NEVER part of the always-on definitional engine — they enter a proof
only through explicit citation::

    eng = tangent_engine(registry=reg)
    cite(eng, book, "cartan_magic", "d_squared_zero")
    ExpandAndSimplify().prove(lhs, rhs, engine=eng, ...)

Matching is structural in v1: the rule fires on nodes structurally
equal to ``lhs`` (or, when ``both_directions`` is set, to ``rhs``,
rewriting the other way). Wildcard/pattern lhs matching is a planned
extension once the first genuinely schematic theorem needs it.
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Iterator, Optional, Tuple

from jacopy.core.expr import Expr, Integer, Sum, Neg
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition, ExpansionEngine


def _sum_multiset_contains(
    haystack: Tuple[Expr, ...], needles: Tuple[Expr, ...]
) -> bool:
    """Is every term of ``needles`` present in ``haystack`` (with
    multiplicity)?"""
    pool = list(haystack)
    for n in needles:
        try:
            pool.remove(n)
        except ValueError:
            return False
    return True


#: Recognized proof-generality tags (definition policy §3).
GENERALITY_TAGS = (
    "operator-level",   # holds for all degrees, proved on operators
    "generic-function", # proved via action on a generic scalar function
    "symbolic-p",       # proved with symbolic degree (IndexedSum route)
    "instance",         # proved for a concrete instance (e.g. p=2)
)


#: the requirement tuple :meth:`Theorem.with_structural_requires` is
#: installing right now (identity-checked: it was derived by the call)
_JUST_DERIVED = contextvars.ContextVar("jacopy_theorem_just_derived", default=None)


def _requirement_signature(reqs):
    """A multiset of the requirement records with ALL their content."""
    from collections import Counter

    def norm(x):
        try:
            hash(x)
            return x
        except TypeError:
            return repr(x)

    return Counter(
        (a.kind, a.name, norm(a.key), id(a.owner) if a.owner is not None else None,
         norm(a.example), a.instances)
        for a in reqs
    )


@dataclass(frozen=True)
class Theorem:
    """A named, proven equation.

    Parameters
    ----------
    name
        Unique short handle (``"cartan_magic"``), the Book lookup key.
    statement
        Human-readable statement, e.g. ``"L_X = d ι_X + ι_X d"``.
    lhs, rhs
        The two sides of the proven equation, as Exprs. ``lhs`` is the
        side a citation rewrites *from* by default.
    proof
        The :class:`ProofChain` establishing ``lhs = rhs``.
    generality
        One of :data:`GENERALITY_TAGS` — at which level the proof
        closed.
    from_axioms
        Descriptive tuple of the definitional-rule names the proof
        relies on.
    notes
        Optional exposition.
    """

    name: str
    statement: str
    lhs: Expr
    rhs: Expr
    proof: ProofChain
    generality: str = "generic-function"
    from_axioms: Tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""
    #: The structure the theorem was proved in (Faz 8 step 2c);
    #: ``None`` = unowned / legacy record (step 3b marks these).
    owner: object = field(default=None, compare=False)
    #: STRUCTURAL requirements (Faz 8 step 3b): the
    #: :class:`~jacopy.proof.result.Assumption` records the proof
    #: depends on — declared axiom instances with their owners, the
    #: structures behind them, the scope, and anything legacy —
    #: including, transitively, the requirements of every theorem the
    #: proof cites. Derived from the chain by
    #: :meth:`with_structural_requires`; never parsed from text.
    requires: Tuple[object, ...] = field(default=(), compare=False)
    #: True only when ``requires`` was derived structurally (or supplied
    #: as such by a 3b-aware prover). A record without it is a LEGACY /
    #: unverified-requirements record: it is not cited automatically
    #: (``TheoremDefinition(..., allow_legacy=True)`` is the explicit
    #: opt-in, and the result then carries the marker).
    requires_verified: bool = field(default=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Theorem.name must be a non-empty string")
        if not isinstance(self.statement, str):
            raise TypeError("Theorem.statement must be a string")
        if not isinstance(self.lhs, Expr) or not isinstance(self.rhs, Expr):
            raise TypeError("Theorem.lhs / Theorem.rhs must be Exprs")
        if not isinstance(self.proof, ProofChain):
            raise TypeError("Theorem.proof must be a ProofChain")
        if self.generality not in GENERALITY_TAGS:
            raise ValueError(
                f"Theorem.generality must be one of {GENERALITY_TAGS}, "
                f"got {self.generality!r}"
            )
        if not isinstance(self.from_axioms, tuple) or not all(
            isinstance(a, str) for a in self.from_axioms
        ):
            raise TypeError("Theorem.from_axioms must be a tuple of strings")
        if not isinstance(self.notes, str):
            raise TypeError("Theorem.notes must be a string")
        from jacopy.proof.result import Assumption

        if not isinstance(self.requires, tuple) or not all(isinstance(a, Assumption) for a in self.requires):
            raise TypeError("Theorem.requires must be a tuple of Assumption records")
        if not isinstance(self.requires_verified, bool):
            raise TypeError("Theorem.requires_verified must be a bool")
        if self.requires_verified and _JUST_DERIVED.get() is not self.requires:
            # "derived" is a property of the record, not a flag a caller
            # sets (audit 0b00e1b-FULL M1-5): the requirements must be
            # EXACTLY what the chain yields — kind, name, key, owner,
            # example and count of every record, structures included
            # (review 2026-10-01 #2: a registry record with its key set
            # to None kept requires_verified and lost its facts)
            from jacopy.proof.result import structural_requires

            if _requirement_signature(self.requires) != _requirement_signature(structural_requires(self)):
                raise ValueError(
                    "Theorem.requires_verified=True but `requires` is not what the chain yields; "
                    "use Theorem.with_structural_requires()"
                )

    def __reduce__(self):
        """Copies and pickles are REBUILT (review 2026-10-01 r3 #7): a
        deep copy's chain holds new step objects, which are not minted,
        so a copied verdict (``chain_replayed`` …) would be stale. A
        record with derived requirements is re-derived from its copied
        chain — consistently requirements-derived / unreplayed / legacy
        as the copy's provenance allows; an underived one keeps its
        requirements as recorded."""
        import dataclasses as _dc

        fields = {f.name: getattr(self, f.name) for f in _dc.fields(self)}
        return (_rebuild_theorem, (fields,))

    # ---- Faz 8 step 3b ------------------------------------------------ #

    @property
    def legacy(self) -> bool:
        """True when the requirements are not structurally verified —
        an unmigrated record, or one whose verified requirements
        contain a legacy entry (a hand-built assumption step, an
        unmatched ``from_axioms`` text, an unverified citation)."""
        return (not self.requires_verified) or any(getattr(a, "legacy", False) for a in self.requires)

    def with_structural_requires(self) -> "Theorem":
        """The record with ``requires`` derived from its own chain:
        declared axiom instances (owner + count), the structures behind
        them, the scope, the transitive requirements of cited theorems,
        and legacy entries for what the chain does not account for.
        Marks ``requires_verified``; the record is still ``legacy`` if
        a legacy entry survives — that is the honest state."""
        import dataclasses

        from jacopy.proof.result import structural_requires

        derived = structural_requires(self)
        # the tuple just derived here is installed without re-deriving it
        # in __post_init__ (review 2026-10-01 #7); any other tuple is checked
        token = _JUST_DERIVED.set(derived)
        try:
            return dataclasses.replace(self, requires=derived, requires_verified=True)
        finally:
            _JUST_DERIVED.reset(token)

    @property
    def requirements_derived(self) -> bool:
        """The honest name of ``requires_verified`` (audit 0b00e1b-FULL
        M1-5): the requirement records were DERIVED from the chain — it
        says nothing about whether the chain proves the claim (that is
        :attr:`chain_replayed`)."""
        return self.requires_verified

    @property
    def chain_replayed(self) -> bool:
        """True when the requirements were derived AND the chain (and,
        transitively, every cited record's chain) replays into
        ``lhs = rhs`` with accountable steps only
        (:func:`jacopy.proof.replay.chain_verdict`)."""
        return self.requires_verified and not any(
            getattr(a, "kind", None) in ("unreplayed", "legacy") for a in self.requires
        )

    def unreplayed_reasons(self) -> Tuple[str, ...]:
        return tuple(a.name for a in self.requires if getattr(a, "kind", None) == "unreplayed")

    @property
    def registry_facts(self) -> tuple:
        """The registry answers the proof relied on (audit 0b00e1b-FULL
        P0-3): a citation must happen in a registry that agrees."""
        from jacopy.proof.registry_facts import facts_of

        return facts_of(self.requires)

    def unverified_reasons(self) -> Tuple[str, ...]:
        if not self.requires_verified:
            return ("requirements were never derived structurally (pre-3b record); "
                    "call Theorem.with_structural_requires() in the prover",)
        return tuple(a.name for a in self.requires if getattr(a, "legacy", False))


def _rebuild_theorem(fields: dict) -> "Theorem":
    """Inverse of :meth:`Theorem.__reduce__`."""
    fields = dict(fields)
    if fields.get("requires_verified"):
        fields["requires"], fields["requires_verified"] = (), False
        return Theorem(**fields).with_structural_requires()
    return Theorem(**fields)


class TheoremBook:
    """Ordered registry of :class:`Theorem` records keyed by name.

    Insertion order is preserved (a rendered "table of results" reads
    in registration order). Duplicate names raise on :meth:`add`; use
    :meth:`replace` for a deliberate override.
    """

    __slots__ = ("_theorems", "_unverified")

    def __init__(self) -> None:
        self._theorems: dict = {}
        self._unverified: set = set()

    def add(self, theorem: Theorem, *, unverified: bool = False) -> None:
        """Register ``theorem``; raise :class:`KeyError` on name clash.

        A ``legacy`` record (requirements not structurally verified,
        Faz 8 step 3b) is NOT accepted as a verified theorem: it raises
        :class:`LegacyTheoremError` unless ``unverified=True`` records
        it explicitly as an unverified assumption — every result that
        cites it then depends on that assumption visibly."""
        if type(theorem) is not Theorem:
            # exact type: a subclass could override the verdict
            # properties (legacy, chain_replayed, requires) — review r3 #8
            raise TypeError("TheoremBook.add expects a Theorem (not a subclass)")
        if theorem.name in self._theorems:
            raise KeyError(
                f"Theorem {theorem.name!r} is already registered; "
                f"use replace() to override"
            )
        if theorem.legacy and not unverified:
            raise LegacyTheoremError(
                f"theorem {theorem.name!r} has unverified requirements "
                f"({'; '.join(theorem.unverified_reasons())}); a TheoremBook takes "
                "it only as an explicit unverified assumption: add(theorem, unverified=True)"
            )
        self._theorems[theorem.name] = theorem
        if theorem.legacy or unverified:
            self._unverified.add(theorem.name)

    def replace(self, theorem: Theorem, *, unverified: bool = False) -> None:
        """Register ``theorem``, overwriting an existing same-name entry."""
        if type(theorem) is not Theorem:
            # exact type: a subclass could override the verdict
            # properties (legacy, chain_replayed, requires) — review r3 #8
            raise TypeError("TheoremBook.replace expects a Theorem (not a subclass)")
        if theorem.legacy and not unverified:
            # validate BEFORE touching the existing record (audit dc44f79 F6)
            raise LegacyTheoremError(
                f"theorem {theorem.name!r} has unverified requirements "
                f"({'; '.join(theorem.unverified_reasons())}); replace(theorem, unverified=True) "
                "records it as an explicit unverified assumption; the existing record is kept"
            )
        self._theorems.pop(theorem.name, None)
        self._unverified.discard(theorem.name)
        self.add(theorem, unverified=unverified)

    def is_verified(self, name: str) -> bool:
        """True when the record was accepted with DERIVED requirements
        (not as an explicit unverified assumption). Historical name:
        it does not mean the chain was replayed — see
        :meth:`is_chain_replayed` (audit 0b00e1b-FULL M1-5)."""
        if name not in self._theorems:
            raise KeyError(f"no theorem named {name!r}; known: {self.names()}")
        return name not in self._unverified

    def is_requirements_derived(self, name: str) -> bool:
        """The honest name of :meth:`is_verified`."""
        return self.is_verified(name)

    def is_chain_replayed(self, name: str) -> bool:
        """Accepted with derived requirements AND a chain that replays
        into its claim (:attr:`Theorem.chain_replayed`)."""
        return self.is_verified(name) and self._theorems[name].chain_replayed

    def unverified_names(self) -> Tuple[str, ...]:
        return tuple(n for n in self._theorems if n in self._unverified)

    def get(self, name: str, *, owner=None) -> Theorem:
        """The theorem ``name``; with ``owner`` given, only when the
        record is owned by that structure (an owned record asked for
        under a different same-named structure is refused, never
        silently reused — Faz 8 step 2c)."""
        if name not in self._theorems:
            raise KeyError(f"no theorem named {name!r}; known: {self.names()}")
        thm = self._theorems[name]
        if owner is not None and thm.owner is not None and thm.owner is not owner and thm.owner != owner:
            from jacopy.proof.ownership import AmbiguousOwnerError

            raise AmbiguousOwnerError(
                f"theorem {name!r} is owned by {thm.owner!r}, not by {owner!r}; "
                "the same-named structures are different — transfer it explicitly"
            )
        return thm

    def names(self) -> Tuple[str, ...]:
        return tuple(self._theorems)

    def remove(self, name: str) -> None:
        if name not in self._theorems:
            raise KeyError(f"no theorem named {name!r}")
        del self._theorems[name]
        self._unverified.discard(name)

    def clear(self) -> None:
        self._theorems.clear()
        self._unverified.clear()

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._theorems

    def __len__(self) -> int:
        return len(self._theorems)

    def __iter__(self) -> Iterator[Theorem]:
        return iter(self._theorems.values())

    def __repr__(self) -> str:
        return f"TheoremBook({len(self)} theorems: {', '.join(self.names())})"


class LegacyTheoremError(ValueError):
    """A record with unverified requirements was used where only a
    verified theorem is accepted (automatic citation, a TheoremBook)."""


@dataclass(frozen=True)
class CitationCheck:
    """Whether ``theorem`` may be cited in an engine (Faz 8 step 3b)."""

    ok: bool
    reasons: Tuple[str, ...] = ()
    legacy: bool = False
    missing: Tuple[object, ...] = ()

    def __str__(self) -> str:
        return "citable" if self.ok else "not citable: " + "; ".join(self.reasons)


#: ``check_citation(registry=…)`` sentinels: use the current proof
#: registry context / skip the registry requirements (the engine-bound
#: verdict; the registry part is checked per proof at match time).
REGISTRY_FROM_CONTEXT = object()
REGISTRY_SKIP = object()


def check_citation(theorem: Theorem, engine, *, allow_legacy: bool = False, registry=REGISTRY_FROM_CONTEXT) -> CitationCheck:
    """Compare the theorem's STRUCTURAL requirements with the engine's
    structures and declared rules.

    * a legacy record is citable only with ``allow_legacy=True`` (and
      then the citing result carries the marker);
    * every ``declared`` / ``structure`` requirement with an owner must
      be met by an engine structure of the same tree-visible name that
      the owner is a sub-structure of (same bundle, declarations ⊆) —
      the right NAME on a different structure is not enough;
    * a requirement without an owner (a structure-free declared rule)
      must be present as a registered assumption rule of the same name;
    * requirements are already transitive (``with_structural_requires``
      folds cited theorems' requirements in);
    * a record whose chain does not replay into its claim (``unreplayed``,
      audit 0b00e1b-FULL M1-5) is citable only with ``allow_legacy=True``;
    * every ``registry`` requirement (a registry answer the proof relied
      on, audit 0b00e1b-FULL P0-3) must be answered the same way by the
      citing ``registry`` — by default the current proof context
      (:func:`jacopy.proof.registry_facts.registry_context`); when no
      context is known a registry-dependent theorem is NOT citable."""
    from jacopy.proof.ownership import is_substructure, owner_name

    reasons = []
    missing = []
    legacy = theorem.legacy
    if legacy and not allow_legacy:
        reasons.append(
            f"theorem {theorem.name!r} has unverified requirements "
            f"({'; '.join(theorem.unverified_reasons())}); pass allow_legacy=True to cite "
            "it explicitly — the result will carry the 'unverified citation' marker"
        )
    unreplayed = theorem.unreplayed_reasons()
    if unreplayed and not legacy:
        legacy = True  # (reported like a legacy record: explicit opt-in only)
        if not allow_legacy:
            reasons.append(
                f"theorem {theorem.name!r} is requirements-derived but its chain is not replayed "
                f"({'; '.join(unreplayed)}); pass allow_legacy=True to cite it explicitly — "
                "every citing result carries the 'unreplayed' record"
            )
    if registry is not REGISTRY_SKIP:
        reasons.extend(_registry_reasons(theorem, registry))
    owners = dict(getattr(engine, "owners", {}) or {})
    rules = tuple(getattr(engine, "definitions", ()) or ())
    from jacopy.proof.expansion import effective_role

    keys = {getattr(r, "key", None) for r in rules if effective_role(r) == "assumption"}
    for a in theorem.requires:
        kind = getattr(a, "kind", None)
        if kind not in ("declared", "structure"):
            continue
        owner = getattr(a, "owner", None)
        if owner is not None:
            name = owner_name(owner)
            have = owners.get(name)
            if have is None:
                reasons.append(f"requires {a.name} of {owner!r}, but this engine has no structure named {name!r}")
                missing.append(a)
                continue
            if not is_substructure(owner, have):
                reasons.append(
                    f"requires {a.name} of {owner!r}; the engine's {name!r} is {have!r}"
                    + (f" with declarations {sorted(have.declarations)}" if getattr(have, "declarations", None) is not None else "")
                    + " — the right name on a different or weaker structure does not satisfy it"
                )
                missing.append(a)
                continue
        if kind == "declared":
            # the owner is necessary, not sufficient: the SAME licensing
            # rule (its structural key — class, structure, parameters such
            # as a connection or a frame) must be registered here
            # (audit dc44f79 F2)
            rkey = getattr(a, "key", None)
            if rkey is None or rkey not in keys:
                reasons.append(
                    f"requires the declared rule {a.name!r}"
                    + (f" of {owner!r}" if owner is not None else "")
                    + ", which this engine does not register (the structure alone does not license it)"
                )
                missing.append(a)
    return CitationCheck(ok=not reasons, reasons=tuple(reasons), legacy=legacy, missing=tuple(missing))


def _registry_reasons(theorem: Theorem, registry=REGISTRY_FROM_CONTEXT) -> Tuple[str, ...]:
    """Why the citing registry does not satisfy the theorem's registry
    requirements (``()`` when it does)."""
    from jacopy.proof.registry_facts import answer, current_context, unmet

    facts = theorem.registry_facts
    if not facts:
        return ()
    if registry is REGISTRY_FROM_CONTEXT:
        ctx = current_context()
        if ctx is None:
            shown = "; ".join(f.describe() for f in facts[:3])
            return (
                f"theorem {theorem.name!r} depends on registry declarations ({shown}"
                + (f"; … {len(facts)} in all" if len(facts) > 3 else "")
                + ") but the citing registry is unknown — cite it under prove/normalize/a strategy "
                "with registry=…, or check_citation(..., registry=…)",
            )
        registry = ctx[0]
    bad = unmet(facts, registry)
    if not bad:
        return ()
    out = []
    for f in bad[:5]:
        here = answer(registry, f)
        now = "nothing declared" if here is None else f"{here[0].__name__}{dict(here[1]) or ''}"
        out.append(f"registry declaration missing: the proof relied on {f.describe()}; the citing registry has {now}")
    if len(bad) > 5:
        out.append(f"… {len(bad)} registry requirements unmet in all")
    return tuple(out)


# --------------------------------------------------------------------- #
# Derived-rule bridge                                                    #
# --------------------------------------------------------------------- #


class TheoremDefinition(Definition):
    """A derived rewrite rule backed by a proven :class:`Theorem`.

    Rewrites nodes structurally equal to ``theorem.lhs`` into
    ``theorem.rhs``. With ``reverse=True`` the orientation flips
    (``rhs → lhs``) — some citations close a proof only in the other
    direction. ``theorem_proof_builder`` returns the stored chain, so
    the engine tags the step ``"theorem"`` and, in foundational mode,
    inlines the derivation.
    """

    #: Re-entrancy guard for modulo-normalization matching: while a
    #: nested normalization runs, every TheoremDefinition falls back
    #: to exact matching (sound — the nested pass just sees fewer
    #: rewrites), preventing infinite regress.
    _IN_MODULO = False

    role = "theorem"

    def __init__(
        self,
        theorem: Theorem,
        *,
        reverse: bool = False,
        modulo=None,
        modulo_max_steps: int = 4096,
        allow_legacy: bool = False,
        unverified: bool = False,
    ) -> None:
        if type(theorem) is not Theorem:
            # exact type: a subclass could override the verdict
            # properties (legacy, chain_replayed, requires) — review r3 #8
            raise TypeError("TheoremDefinition expects a Theorem (not a subclass)")
        self._theorem = theorem
        self._reverse = bool(reverse)
        self._modulo = modulo
        self._modulo_max_steps = modulo_max_steps
        self._modulo_cache = None
        self._allow_legacy = bool(allow_legacy)
        # the record was taken from a TheoremBook under its explicit
        # ``unverified`` flag: the citation is a legacy assumption of the
        # citing proof, whatever the record's own requirements say
        self.unverified = bool(unverified)
        # citation check (Faz 8 step 3b): None = not bound to an engine
        # yet — only the legacy rule applies; a bound copy carries the
        # engine's verdict
        self._check: Optional[CitationCheck] = None
        self._checked_against = None
        self._engine = None
        direction = "⇐" if self._reverse else "⇒"
        self.name = f"theorem {theorem.name} {direction}: {theorem.statement}"
        if theorem.legacy:
            self.name += "  [LEGACY: unverified requirements]"
        elif self.unverified:
            self.name += "  [UNVERIFIED: recorded as an assumption]"
        self.owner = theorem.owner  # a citation is owned by the theorem's structure
        src = theorem.rhs if self._reverse else theorem.lhs
        self.anchor = type(src)

    @property
    def theorem(self) -> Theorem:
        return self._theorem

    @property
    def allow_legacy(self) -> bool:
        return self._allow_legacy

    # ---- Faz 8 step 3b: binding to an engine ---------------------------- #

    def bound_to(self, engine) -> "TheoremDefinition":
        """A copy bound to ``engine``, with the citation check run
        against that engine's structures (the caller's object stays
        unbound and reusable). A blocked citation stays inert and the
        engine's ``assembly_report`` says why."""
        import copy

        bound = copy.copy(self)
        bound._engine = engine
        bound._check = None
        bound._checked_against = None
        bound._modulo_cache = None
        bound._recheck()
        return bound

    def _recheck(self) -> CitationCheck:
        """(Re)run the check when the bound engine's structures changed
        since the last verdict — citations are often registered BEFORE
        the structure's own rules, so the verdict must follow the
        engine's current owners, not the registration moment."""
        engine = self._engine
        owners = getattr(engine, "owners", {}) or {}
        key = (getattr(engine, "version", None), tuple((n, id(o)) for n, o in owners.items()))
        if self._check is not None and key == self._checked_against:
            return self._check
        self._check = check_citation(self._theorem, engine, allow_legacy=self._allow_legacy, registry=REGISTRY_SKIP)
        self._checked_against = key
        report = getattr(engine, "assembly_report", None)
        if report is not None:
            if not self._check.ok:
                report.append(f"theorem {self._theorem.name!r}: NOT citable here — " + "; ".join(self._check.reasons))
            elif self._check.legacy:
                report.append(f"theorem {self._theorem.name!r}: LEGACY citation allowed explicitly (unverified requirements)")
            else:
                report.append(f"theorem {self._theorem.name!r}: citable (requirements met)")
        return self._check

    @property
    def check(self) -> CitationCheck:
        """The citation verdict: the bound engine's (against its current
        structures), or (unbound) the legacy rule alone."""
        if self._engine is not None:
            return self._recheck()
        if self._theorem.legacy and not self._allow_legacy:
            return CitationCheck(False, (f"theorem {self._theorem.name!r} has unverified requirements; "
                                         "pass allow_legacy=True to cite it explicitly",), legacy=True)
        if self._theorem.unreplayed_reasons() and not self._allow_legacy:
            return CitationCheck(False, (f"theorem {self._theorem.name!r}: chain not replayed; "
                                         "pass allow_legacy=True to cite it explicitly",), legacy=True)
        return CitationCheck(True, legacy=self._theorem.legacy or bool(self._theorem.unreplayed_reasons()))

    @property
    def citable(self) -> bool:
        return self.check.ok

    @property
    def blocked(self) -> Tuple[str, ...]:
        return self.check.reasons

    def _source(self) -> Expr:
        return self._theorem.rhs if self._reverse else self._theorem.lhs

    def _target(self) -> Expr:
        return self._theorem.lhs if self._reverse else self._theorem.rhs

    def matches(self, expr: Expr) -> bool:
        # An identity rewrite (lhs == rhs — degenerate instances can
        # normalize to 0 = 0) would fire forever; stay inert instead
        # (caught by the Phase 5 edge-case audit).
        if self._source() == self._target():
            return False
        if not self.citable:
            return False  # requirements not met here, or a legacy record without the opt-in
        if not (expr == self._source() or self._matches_sum_subset(expr) or self._matches_modulo(expr)):
            return False
        # the registry requirements are checked per PROOF against the
        # citing registry context (audit 0b00e1b-FULL P0-3): a theorem
        # proved with ``x`` Scalar does not fire where ``x`` is not
        if _registry_reasons(self._theorem):
            self._modulo_cache = None
            return False
        return True

    @staticmethod
    def _term_count(expr: Expr) -> int:
        if expr == Integer(0):
            return 0
        if isinstance(expr, Sum):
            return len(expr.children)
        return 1

    def _matches_sum_subset(self, expr: Expr) -> bool:
        # Sum-subset citation (Phase 5.E.2b): a proven Sum instance
        # covers a subset of a larger Sum's terms —
        # Σ(A ∪ B) = Σ(A) + Σ(B) and Σ(A) = rhs replaces A by rhs.
        # Admitted only when the rhs has STRICTLY FEWER terms than
        # the covered subset (rhs = 0, or e.g. a 2→1 bracket
        # rearrangement), so the total term count strictly decreases
        # and the rewrite terminates.
        src = self._source()
        return (
            isinstance(src, Sum)
            and isinstance(expr, Sum)
            and self._term_count(self._target())
            < len(src.children)
            and len(expr.children) > len(src.children)
            and _sum_multiset_contains(expr.children, src.children)
        )



    def _matches_modulo(self, expr: Expr) -> bool:
        """Phase 6.J — MODULO-NORMALIZATION matching: the candidate
        Sum matches when ``NF(expr − lhs)`` (normalized by the
        ``modulo`` engine) has STRICTLY fewer terms than ``expr``
        (counting the rhs about to be added back). Soundness: the
        rewrite emits ``NF(expr − lhs) + rhs``, and
        ``expr = (expr − lhs) + lhs = NF(expr − lhs) + rhs`` — every
        equality is a registered-rule application plus the cited
        theorem. Termination: strict term-count decrease. No new
        mathematical content: this only lets an already-proven
        instance be RECOGNIZED where normal-form timing hid it."""
        if self._modulo is None or TheoremDefinition._IN_MODULO:
            return False
        src = self._source()
        if not (isinstance(expr, Sum) and isinstance(src, Sum)):
            return False
        if len(expr.children) < 2:
            return False
        # Cost gate: modulo matching runs a full normalization per
        # attempt, so restrict it to STALL-SIZED sums (residual
        # shapes) — never the giant intermediate sums of a hot
        # expansion loop (measured: minutes instead of seconds).
        if len(expr.children) > len(src.children) + 4:
            return False
        diff_seed = Sum(
            *expr.children,
            *(Neg(t) for t in src.children),
        )
        TheoremDefinition._IN_MODULO = True
        # every step of the modulo normalization is RECORDED (audit
        # 0b00e1b-FULL M1X-3): the modulo engine's rules may be explicit
        # assumptions — they become children of the citation step, so
        # the citing result's requirements include them
        recorded = []
        try:
            from jacopy.algorithms.product_rule import product_rule
            from jacopy.algorithms.simplify import simplify
            from jacopy.proof.step import ProofStep, _mint

            cur = diff_seed
            for _ in range(12):
                nxt, steps = self._modulo.expand(
                    cur, max_steps=self._modulo_max_steps
                )
                recorded.extend(steps)
                for rule, fn in (("product-rule", product_rule), ("simplify", simplify)):
                    after = fn(nxt, None)
                    if after != nxt:
                        recorded.append(_mint(ProofStep(nxt, after, rule=rule, justification="modulo normalization pass",
                                                        key=("pass", rule))))
                    nxt = after
                if nxt == cur:
                    break
                cur = nxt
            diff = cur
        except Exception:
            return False
        finally:
            TheoremDefinition._IN_MODULO = False
        if (
            self._term_count(diff)
            + self._term_count(self._target())
            >= len(expr.children)
        ):
            return False
        self._modulo_cache = (expr, diff, diff_seed, tuple(recorded))
        return True

    def rewrite(self, expr: Expr) -> Expr:
        if expr == self._source():
            return self._target()
        if (
            self._modulo_cache is not None
            and self._modulo_cache[0] == expr
        ):
            _, diff, seed, recorded = self._modulo_cache
            self._modulo_cache = None
            from jacopy.proof.step import ProofStep, _mint

            self._side = (expr, (_mint(ProofStep(
                seed, diff, rule=f"modulo normalization for theorem {self._theorem.name}",
                justification="NF(expr − lhs) by the modulo engine; expr = NF(expr − lhs) + rhs",
                children=list(recorded), key=("theorem-modulo", self._theorem.name),
            )),))
            target = self._target()
            parts = []
            for piece in (diff, target):
                if piece == Integer(0):
                    continue
                parts.extend(
                    piece.children
                    if isinstance(piece, Sum)
                    else [piece]
                )
            return Sum.make(*parts)
        remaining = list(expr.children)
        for t in self._source().children:
            remaining.remove(t)
        target = self._target()
        if target == Integer(0):
            return Sum.make(*remaining)
        extra = (
            list(target.children)
            if isinstance(target, Sum)
            else [target]
        )
        return Sum.make(*remaining, *extra)

    #: the side derivation of the last modulo rewrite (consumed by
    #: :meth:`side_steps`)
    _side = None

    def side_steps(self, expr: Expr):
        """The recorded modulo normalization of the rewrite just made at
        ``expr`` (attached under the citation step by the engine)."""
        side, self._side = self._side, None
        if side is not None and side[0] == expr:
            return side[1]
        return ()

    def theorem_proof_builder(self):
        chain = self._theorem.proof

        def _builder(_matched: Expr) -> ProofChain:
            return chain

        return _builder


def cite(
    engine: ExpansionEngine,
    book: TheoremBook,
    *names: str,
    reverse: bool = False,
    allow_legacy: bool = False,
) -> ExpansionEngine:
    """Register the named theorems on ``engine`` as derived rules.

    Mutates and returns ``engine`` for chaining. Citation is the ONLY
    sanctioned way a proven result enters a proof (definition policy
    §2) — derived rules are never part of the always-on engines.

    A record the book holds as UNVERIFIED (legacy requirements) is
    cited only with ``allow_legacy=True`` — explicitly, never silently
    (:class:`LegacyTheoremError` otherwise); the citing result then
    carries the "unverified citation" marker (Faz 8 step 3b).
    """
    for n in names:
        thm = book.get(n)
        unverified = not book.is_verified(n)
        unreplayed = thm.unreplayed_reasons()
        if (thm.legacy or unverified or unreplayed) and not allow_legacy:
            why = (
                "; ".join(thm.unverified_reasons()) if thm.legacy
                else "the book holds it as an explicit unverified assumption" if unverified
                else "its chain is not replayed: " + "; ".join(unreplayed)
            )
            raise LegacyTheoremError(
                f"theorem {n!r} is not a verified record ({why}); "
                "cite it explicitly with allow_legacy=True — the result will carry the marker"
            )
        engine.register(TheoremDefinition(thm, reverse=reverse, allow_legacy=allow_legacy, unverified=unverified))
    return engine


#: Process-wide default book. Central-code modules register their
#: proven theorems here; proofs cite them by name.
theorem_book = TheoremBook()
