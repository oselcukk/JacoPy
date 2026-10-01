"""
The result / assumption / provenance model (Faz 8 step 3a).

A proof attempt answers three different questions, and this module
keeps the answers apart:

* WHAT was attempted — :class:`Goal` (``lhs = rhs``) and the
  :class:`ProofResult.status`: ``CLOSED`` (the two sides met),
  ``RESIDUAL`` (the engine reached a fix-point with a surviving
  difference — NOT a disproof, see below), ``BUDGET`` (the step budget
  ran out before a fix-point) or ``INVALID`` (the goal is ill-typed:
  a 1-form equated to a 2-form, a vector to a function …; nothing was
  run). There is no ``DISPROVED``: an unreduced residual is never a
  certificate of non-zero (audit 2026-09-23, 0058df0).
* WHAT IT DEPENDS ON — ``requires``: the :class:`Assumption` records.
  ``declared`` — a declared axiom of a structure that actually fired
  (with its owner and the number of instances); ``structure`` — the
  structure objects those axioms belong to; ``scope`` — the proof's
  generality when it is an instance proof (an instance certificate is
  never upgraded to a general one); ``legacy`` — an assumption that is
  RECORDED but not structurally verified: a step whose rule carries no
  role, an unverified citation. ``textual`` — a ``from_axioms`` prose
  entry no step accounts for: kept visible, NOT a verification input
  (prose is not a trust boundary; the structural record is). Also a
  theorem record whose chain does not literally run ``lhs → rhs``.
  Legacy entries are kept, never dropped (step 3b decides what may
  cite them).
* HOW it was derived — ``provenance``: cited theorems, definitional
  unfoldings, canonicalizations, plain engine steps, computations.
  These are not assumptions: a definition assumes nothing.

``CLOSED`` is always shown "under" its assumptions (:meth:`summary`).
The result carries the build version from the package metadata (no
``.git`` needed) and the step :class:`Budget`.

The old ``(chain, theorem)`` returns of the provers are untouched:
:meth:`ProofResult.from_theorem` and :meth:`ProofResult.from_chain`
wrap them, and :func:`prove` is the small driver that produces a
result directly from an engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from jacopy.core.expr import Expr, Integer
from jacopy.oracle.hook import on_closed
from jacopy.proof.chain import ProofChain
from jacopy.proof.step import ProofStep, _mint, is_minted

STATUSES = ("CLOSED", "RESIDUAL", "BUDGET", "INVALID")
ASSUMPTION_KINDS = ("declared", "structure", "scope", "legacy", "textual", "registry", "unreplayed")
PROVENANCE_KINDS = ("theorem", "definition", "canonicalization", "engine-step", "computation")

_CANONICAL_RULES = ("simplify", "canonicalize", "normalize", "collect", "sort", "flatten", "distribute")


def package_version() -> str:
    """The installed package version from the build metadata (the
    ``jacopy.__version__`` fallback when not installed)."""
    try:
        from importlib.metadata import version

        return version("jacopy")
    except Exception:  # pragma: no cover - not installed as a distribution
        import jacopy

        return getattr(jacopy, "__version__", "unknown")


@dataclass(frozen=True)
class Goal:
    lhs: Expr
    rhs: Expr

    def __post_init__(self) -> None:
        if not isinstance(self.lhs, Expr) or not isinstance(self.rhs, Expr):
            raise TypeError("Goal sides must be Exprs")

    def __str__(self) -> str:
        return f"{self.lhs._repr_inner()} = {self.rhs._repr_inner()}"


@dataclass(frozen=True)
class Assumption:
    """One logical dependency of a result (module docstring)."""

    kind: str
    name: str
    owner: object = field(default=None, compare=False)
    instances: int = field(default=0, compare=False)
    example: Optional[Expr] = field(default=None, compare=False)
    #: structural key of the licensing rule (``Definition.key``); a
    #: ``declared`` entry always has one — a citation checks that a rule
    #: with the same key is registered in the citing engine
    key: object = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.kind not in ASSUMPTION_KINDS:
            raise ValueError(f"Assumption.kind must be one of {ASSUMPTION_KINDS}, got {self.kind!r}")

    @property
    def legacy(self) -> bool:
        return self.kind == "legacy"

    def __str__(self) -> str:
        who = f" [{self.owner!r}]" if self.owner is not None else ""
        times = f" ×{self.instances}" if self.instances > 1 else ""
        return f"{self.kind}: {self.name}{who}{times}"


@dataclass(frozen=True)
class Provenance:
    """One derivation ingredient (not an assumption)."""

    kind: str
    name: str
    owner: object = field(default=None, compare=False)
    count: int = field(default=1, compare=False)

    def __post_init__(self) -> None:
        if self.kind not in PROVENANCE_KINDS:
            raise ValueError(f"Provenance.kind must be one of {PROVENANCE_KINDS}, got {self.kind!r}")

    def __str__(self) -> str:
        times = f" ×{self.count}" if self.count > 1 else ""
        return f"{self.kind}: {self.name}{times}"


@dataclass(frozen=True)
class Budget:
    steps: int
    max_steps: Optional[int] = None
    exhausted: bool = False

    def __str__(self) -> str:
        cap = f"/{self.max_steps}" if self.max_steps is not None else ""
        return f"{self.steps}{cap} steps" + (" (exhausted)" if self.exhausted else "")


# ------------------------------------------------------------------ #
# classification of a chain                                          #
# ------------------------------------------------------------------ #


def _dominant(owner, candidates):
    """The structure among ``candidates`` that ``owner`` is a
    SUB-STRUCTURE of — same tree-visible name and bundle, declarations
    a subset of the candidate's — with the most declarations; a proof
    run under fewer axioms of the same structure (the provers' reduced
    twins, e.g. "E without jacobi") depends on that structure, not on a
    second same-named owner. ``owner`` itself when none dominates."""
    from jacopy.proof.ownership import owner_name

    decl = getattr(owner, "declarations", None)
    if decl is None:
        return owner
    best, best_size = owner, len(decl)
    for c in candidates:
        cdecl = getattr(c, "declarations", None)
        if cdecl is None or c is owner:
            continue
        if (
            owner_name(c) == owner_name(owner)
            and getattr(c, "bundle", None) == getattr(owner, "bundle", None)
            and set(decl) <= set(cdecl)
            and len(cdecl) >= best_size
        ):
            best, best_size = c, len(cdecl)
    return best


def _classify(steps: Iterable[ProofStep], principal=None):
    """Walk the steps (children included) and bucket them into
    assumptions and provenance, aggregated by (kind, name, owner).
    Owners that are sub-structures of another owner seen in the proof
    (or of ``principal``) are folded into it (:func:`_dominant`)."""
    assumptions: dict = {}
    provenance: dict = {}
    owners_seen: list = [] if principal is None else [principal]

    def collect(seq):
        for s in seq:
            o = getattr(s, "owner", None)
            if o is not None and not any(o is x for x in owners_seen):
                owners_seen.append(o)
            collect(s.children)

    collect(steps)
    canon = {id(o): _dominant(o, owners_seen) for o in owners_seen}

    def bump(table, kind, name, owner, example=None, rkey=None):
        owner = canon.get(id(owner), owner) if owner is not None else None
        key = (kind, name, id(owner) if owner is not None else None, _hashable(rkey))
        if key in table:
            k, n, o, c, ex, rk = table[key]
            table[key] = (k, n, o, c + 1, ex, rk)
        else:
            table[key] = (kind, name, owner, 1, example, rkey)

    def declared_or_legacy(s, owner):
        # a declared assumption must name its licensing rule (key); a
        # hand-built assumption step without one cannot be located in
        # another engine and stays a legacy record (audit dc44f79 F2)
        rkey = getattr(s, "key", None)
        if rkey is None:
            bump(assumptions, "legacy", f"assumption instance without a licensing rule: {s.rule}", owner, s.before)
        else:
            bump(assumptions, "declared", s.rule, owner, s.before, rkey)

    def inherit(cited):
        # every requirement kind of the cited record flows to the citing
        # proof — "textual" from_axioms entries included (review
        # 2026-10-01 rules-match) and "structure" (review r3 #3: also a
        # structure no inherited declared record names); an unknown kind
        # is kept as legacy, never dropped
        for a in getattr(cited, "requires", ()) or ():
            kind = getattr(a, "kind", None)
            if kind in ASSUMPTION_KINDS:
                bump(assumptions, kind, a.name, a.owner, a.example, a.key)
            else:
                bump(assumptions, "legacy", f"unrecognized requirement kind {kind!r} of theorem "
                     f"{getattr(cited, 'name', '?')}: {getattr(a, 'name', a)!r}", getattr(a, "owner", None))

    def visit(seq):
        for s in seq:
            tag, role = s.provenance_tag, getattr(s, "role", None)
            owner = getattr(s, "owner", None)
            if role == "assumption":
                declared_or_legacy(s, owner)
                if tag == "theorem":
                    bump(provenance, "theorem", s.rule, owner)
            elif tag == "theorem":
                bump(provenance, "theorem", s.rule, owner)
                cited = getattr(s, "cites", None)
                if role == "unverified-citation":
                    # a TheoremBook record cited under its explicit
                    # ``unverified`` flag (audit dc44f79 F5)
                    bump(assumptions, "legacy", f"unverified citation (record marked unverified): {s.rule}", owner, s.before)
                    if cited is not None:
                        inherit(cited)
                elif cited is not None and type(cited) is _theorem_class():
                    # TRANSITIVE requirements (Faz 8 step 3b): a citation
                    # contributes ALL its own requirements; an unverified
                    # (legacy) one is, in addition, a legacy assumption
                    if getattr(cited, "legacy", True):
                        bump(assumptions, "legacy", f"unverified citation: theorem {cited.name}", getattr(cited, "owner", None), s.before)
                    inherit(cited)
                elif cited is not None:
                    # not an exact Theorem record: its verdict properties
                    # are not trusted (review r3 #8) — legacy, its
                    # requirements still carried
                    bump(assumptions, "legacy", f"unverified citation: {type(cited).__name__} is not a Theorem record: {s.rule}", owner, s.before)
                    inherit(cited)
                elif getattr(s, "key", None) is None and not s.children:
                    # a HAND-BUILT theorem claim with neither the cited object
                    # nor an attached derivation: not verifiable here (audit
                    # dc44f79 F1). A step fired by a registered theorem-
                    # classified rule carries the rule's key: its derivation
                    # is the rule's proof builder (foundational mode inlines
                    # it) — provenance, not an assumption.
                    bump(assumptions, "legacy", f"unverified citation: {s.rule}", owner, s.before)
            elif tag == "axiom":
                if role == "definition":
                    bump(provenance, "definition", s.rule, owner)
                else:
                    # the rule recorded no role: a hand-built or unmigrated
                    # step — kept as an assumption, marked legacy
                    bump(assumptions, "legacy", s.rule, owner, s.before)
            elif tag == "computation":
                bump(provenance, "computation", s.rule, owner)
            else:
                low = s.rule.lower()
                kind = "canonicalization" if any(low.startswith(c) or f" {c}" in low for c in _CANONICAL_RULES) else "engine-step"
                bump(provenance, kind, s.rule, owner)
            # a whole-expression wrapper carries its local step as the only
            # child: that child is the SAME event (same rule and metadata)
            # and is not counted twice — but ITS children (a modulo
            # citation's recorded normalization, a foundational sub-proof)
            # are always visited: skipping the wrapper's twin must never
            # drop a sub-step's requirements (review 2026-10-01 #1)
            kids = []
            for c in s.children:
                if len(s.children) == 1 and _same_event(c, s):
                    kids.extend(c.children)
                else:
                    kids.append(c)
            visit(kids)

    visit(steps)
    # registry answers the steps relied on (audit 0b00e1b-FULL P0-3):
    # recorded on the steps by their producers; a cited theorem's own
    # registry records arrived through its requires above
    from jacopy.proof.registry_facts import facts_of, requirement_records, step_facts

    cited_registry = []
    for key in [k for k in assumptions if k[0] == "registry"]:
        k_, n_, o_, c_, ex_, rk_ = assumptions[key]
        parsed = facts_of([Assumption(k_, n_, o_, c_, ex_, rk_)])
        if parsed:
            cited_registry.extend(parsed)
            del assumptions[key]
        else:
            # a registry record whose facts cannot be read back cannot be
            # checked at a citation: never dropped silently — legacy
            # (review 2026-10-01 #5)
            del assumptions[key]
            bump(assumptions, "legacy", f"unverifiable registry requirement (no readable facts): {n_}", o_, ex_)
    cited_registry = tuple(cited_registry)
    req = [Assumption(k, n, o, c, ex, rk) for (k, n, o, c, ex, rk) in assumptions.values()]
    req.extend(requirement_records(tuple(step_facts(steps)) + cited_registry))
    prov = [Provenance(k, n, o, c) for (k, n, o, c, _, _) in provenance.values()]
    # the structures behind the declared axioms are assumptions too
    seen_owners: list = []
    for a in req:
        if a.kind == "declared" and a.owner is not None and not any(a.owner is o or a.owner == o for o in seen_owners):
            seen_owners.append(a.owner)
    for o in seen_owners:
        decl = getattr(o, "declarations", None)
        text = f"{o!r}" + (f" declaring {sorted(decl)}" if decl is not None else "")
        # the proof's OWN structure record is always produced; only an
        # exact duplicate (same text, same owner) of an inherited one is
        # dropped (proof-trust-2 #5: an inherited record of the same
        # owner with other declarations no longer suppresses it)
        if any(a.kind == "structure" and a.name == text and a.owner is o for a in req):
            continue
        req.append(Assumption("structure", text, o))
    return tuple(req), tuple(prov)


def _theorem_class():
    from jacopy.proof.theorems import Theorem

    return Theorem


def _same_event(child: ProofStep, parent: ProofStep) -> bool:
    """``child`` is the local twin of the whole-expression wrapper
    ``parent`` (:func:`_whole_step`): identical rule and metadata."""
    return (
        child.rule == parent.rule
        and child.provenance_tag == parent.provenance_tag
        and getattr(child, "role", None) == getattr(parent, "role", None)
        and getattr(child, "key", None) == getattr(parent, "key", None)
        and getattr(child, "owner", None) is getattr(parent, "owner", None)
        and getattr(child, "cites", None) is getattr(parent, "cites", None)
    )


def _hashable(x):
    try:
        hash(x)
        return x
    except TypeError:
        return repr(x)


def _whole_step(before: Expr, after: Expr, local: ProofStep, *, at_site: bool = False) -> ProofStep:
    """A whole-expression step carrying the engine's local step (a
    subterm rewrite) as its child; the same rule, tag, owner, role and
    citation, so classification is unchanged."""
    if local.before == before and local.after == after:
        return local
    wrapper = ProofStep(
        before, after, rule=local.rule, justification=local.justification, children=[local],
        provenance_tag=local.provenance_tag, owner=local.owner, role=getattr(local, "role", None),
        cites=getattr(local, "cites", None), key=getattr(local, "key", None),
        registry_facts=getattr(local, "registry_facts", ()),
        source=getattr(local, "source", None),
    )
    # minted only when the local step is AND the caller's own rewrite
    # produced ``after`` at the local step's site (``at_site``: the
    # engine's expand_once / the search's path rewrite) — review
    # 2026-10-01 #3, r3 #4: no first-occurrence guess, no extra walk
    if at_site and is_minted(local):
        _mint(wrapper)
    return wrapper


def _reversed_step(s: ProofStep) -> ProofStep:
    """The step read backwards, with ALL its semantic metadata (owner,
    role, citation, key, children) — reversing an equation must not
    drop what it depends on (audit dc44f79 F1)."""
    rev = ProofStep(
        s.after, s.before, rule=s.rule, justification=(s.justification + " (reversed)").strip(),
        children=list(s.children), provenance_tag=s.provenance_tag, owner=s.owner, role=getattr(s, "role", None),
        cites=getattr(s, "cites", None), key=getattr(s, "key", None),
        registry_facts=getattr(s, "registry_facts", ()),
        source=getattr(s, "source", None),
    )
    return _mint(rev) if is_minted(s) else rev


# ------------------------------------------------------------------ #
# the result                                                         #
# ------------------------------------------------------------------ #


@dataclass(frozen=True)
class ProofResult:
    goal: Goal
    status: str
    requires: Tuple[Assumption, ...] = ()
    provenance: Tuple[Provenance, ...] = ()
    chain: Optional[ProofChain] = field(default=None, compare=False)
    residual: Optional[Expr] = None
    budget: Budget = field(default_factory=lambda: Budget(0))
    generality: str = "generic-function"
    owner: object = field(default=None, compare=False)
    reason: str = ""
    version: str = field(default_factory=package_version, compare=False)

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"ProofResult.status must be one of {STATUSES}, got {self.status!r}")
        from jacopy.proof.theorems import GENERALITY_TAGS

        if self.generality not in GENERALITY_TAGS:
            raise ValueError(f"ProofResult.generality must be one of {GENERALITY_TAGS}, got {self.generality!r}")
        if self.status == "CLOSED" and self.residual is not None:
            raise ValueError("a CLOSED result has no residual")
        if self.status in ("RESIDUAL", "BUDGET") and self.residual is None:
            raise ValueError(f"a {self.status} result must record its residual")

    # ---- views ------------------------------------------------------- #

    @property
    def closed(self) -> bool:
        return self.status == "CLOSED"

    @property
    def declared(self) -> Tuple[Assumption, ...]:
        return tuple(a for a in self.requires if a.kind == "declared")

    @property
    def legacy(self) -> Tuple[Assumption, ...]:
        """The recorded-but-unverified assumptions (never dropped)."""
        return tuple(a for a in self.requires if a.legacy)

    @property
    def textual(self) -> Tuple[Assumption, ...]:
        """The record's ``from_axioms`` prose no step accounts for:
        visible, never dropped, NOT a verification input (prose is not
        a trust boundary; the chain's structural record is)."""
        return tuple(a for a in self.requires if a.kind == "textual")

    @property
    def theorems_cited(self) -> Tuple[Provenance, ...]:
        return tuple(p for p in self.provenance if p.kind == "theorem")

    def summary(self) -> str:
        """``CLOSED`` always reads "under" its assumptions; an instance
        proof says so; a residual is shown as a residual, not as a
        counterexample."""
        lines = [f"{self.status}: {self.goal}"]
        if self.status == "CLOSED":
            lines[0] += "  — under the assumptions below" if self.requires else "  — assumption-free"
        if self.status in ("RESIDUAL", "BUDGET"):
            lines.append(f"  residual (unreduced, NOT a disproof): {self.residual._repr_inner()}")
        if self.status == "INVALID":
            lines.append(f"  reason: {self.reason}")
        if self.generality == "instance":
            lines.append("  generality: instance — this certificate is not a general theorem")
        else:
            lines.append(f"  generality: {self.generality}")
        for a in self.requires:
            lines.append(f"  requires {a}")
        for p in self.provenance:
            lines.append(f"  via {p}")
        lines.append(f"  budget: {self.budget}; jacopy {self.version}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()

    # ---- constructors ------------------------------------------------ #

    @classmethod
    def invalid(cls, goal: Goal, reason: str, **kw) -> "ProofResult":
        return cls(goal=goal, status="INVALID", reason=reason, **kw)

    @classmethod
    def from_chain(
        cls,
        chain: ProofChain,
        goal: Goal,
        *,
        status: Optional[str] = None,
        max_steps: Optional[int] = None,
        generality: str = "generic-function",
        owner=None,
        extra: Sequence[Assumption] = (),
        reason: str = "",
        side_steps: Sequence[ProofStep] = (),
    ) -> "ProofResult":
        """Classify ``chain`` against ``goal``. The chain must start at
        ``goal.lhs``; its final expression decides ``CLOSED`` (equal to
        ``goal.rhs``) or ``RESIDUAL``; ``status="BUDGET"`` records an
        exhausted budget. ``side_steps`` are a SEPARATE computation
        (e.g. the right-hand side's normalization) whose assumptions and
        provenance count but which is not part of the transcript.
        Assumptions the chain does not record structurally are kept as
        ``legacy``, never ignored."""
        if not isinstance(chain, ProofChain):
            raise TypeError("from_chain expects a ProofChain")
        if not isinstance(goal, Goal):
            raise TypeError("from_chain expects a Goal")
        if status not in (None, "CLOSED", "RESIDUAL", "BUDGET"):
            raise ValueError(
                f"from_chain status must be None, 'CLOSED', 'RESIDUAL' or 'BUDGET', got {status!r} "
                "(an ill-typed goal is ProofResult.invalid)"
            )
        if len(chain) and chain.initial != goal.lhs:
            raise ValueError(
                f"the chain starts at {chain.initial._repr_inner()}, not at the goal's "
                f"left-hand side {goal.lhs._repr_inner()}"
            )
        # the transcript must be CONNECTED (audit 0b00e1b-FULL M1-6 ≡
        # K2-7): every step rewrites what the previous one left (a
        # whole-expression step, or a local step at its first site)
        from jacopy.proof.replay import replay

        replayed, why = replay(goal.lhs, chain.steps)
        if replayed is None:
            raise ValueError(f"the chain is not connected: {why}")
        if status == "CLOSED" and replayed != goal.rhs:
            # a CLOSED status is a claim the transcript must carry, not a
            # flag the caller sets (audit 0b00e1b-FULL M1-6)
            raise ValueError(
                f"status='CLOSED' but the chain ends at {replayed._repr_inner()[:200]}, "
                f"not at the goal's right-hand side {goal.rhs._repr_inner()[:200]}"
            )
        final = replayed
        req, prov = _classify(tuple(chain.steps) + tuple(side_steps), principal=owner)
        # a hand-built step (not minted by a library producer) is the
        # author's word, not a licensed rewrite: a legacy assumption
        # (audit 0b00e1b-FULL M1-5), never silent provenance
        from jacopy.proof.replay import unaccountable_steps

        hand: dict = {}
        for rule in unaccountable_steps(tuple(chain.steps) + tuple(side_steps)):
            hand[rule] = hand.get(rule, 0) + 1
        req = req + tuple(
            Assumption("legacy", f"hand-built step (not produced by a library producer): {rule}", instances=n)
            for rule, n in hand.items()
        )
        req = req + tuple(extra)
        if generality == "instance":
            req = req + (Assumption("scope", "instance proof — the certificate is not generalized"),)
        exhausted = status == "BUDGET"
        if status is None:
            status = "CLOSED" if final == goal.rhs else "RESIDUAL"
        residual = None if status == "CLOSED" else final
        return cls(
            goal=goal, status=status, requires=req, provenance=prov, chain=chain, residual=residual,
            budget=Budget(len(chain) + len(side_steps), max_steps, exhausted), generality=generality, owner=owner, reason=reason,
        )

    @classmethod
    def from_theorem(cls, theorem, *, registry=None, owners=None) -> "ProofResult":
        """Wrap a :class:`~jacopy.proof.theorems.Theorem` (the old
        ``(chain, theorem)`` return shape). The record's closure is
        taken as CLOSED; textual ``from_axioms`` entries no step
        accounts for, and a chain that does not literally run
        ``lhs → rhs``, are kept as ``legacy`` assumptions. ``registry`` /
        ``owners`` only inform the model oracle (default off)."""
        from jacopy.proof.theorems import Theorem

        if not isinstance(theorem, Theorem):
            raise TypeError("from_theorem expects a Theorem")
        goal = Goal(theorem.lhs, theorem.rhs)
        chain = theorem.proof
        # the record's requirements, its chain verdict included (audit
        # 0b00e1b-FULL M1-5): a chain that does not replay into
        # ``lhs = rhs`` is an ``unreplayed`` record, an empty / purely
        # hand-built one a legacy record
        req, prov = _theorem_requirements(theorem)
        if owners is None:
            # the structures the record itself names (its owner and the
            # owners of its steps); none at all → unknown to the oracle
            from jacopy.proof.ownership import chain_owners

            found = ([theorem.owner] if theorem.owner is not None else []) + [
                o for o in chain_owners(chain) if o is not theorem.owner]
            owners = found or None
        on_closed(theorem.lhs, theorem.rhs, source="from_theorem", registry=registry, owners=owners, requires=req)
        return cls(
            goal=goal, status="CLOSED", requires=req, provenance=prov, chain=chain, residual=None,
            budget=Budget(len(chain)), generality=theorem.generality, owner=theorem.owner,
        )


def _theorem_requirements(theorem):
    """``(requires, provenance)`` of a theorem record derived from its
    OWN chain (shared by :func:`structural_requires` and
    :meth:`ProofResult.from_theorem`)."""
    from jacopy.proof.replay import chain_verdict

    req, prov = _classify(theorem.proof.steps, principal=theorem.owner)
    known = {a.name for a in req} | {p.name for p in prov}
    out = list(req)
    for text in theorem.from_axioms:
        if text not in known and not any(text in k for k in known):
            out.append(Assumption("textual", f"from_axioms: {text}", theorem.owner))
    if theorem.generality == "instance" and not any(a.kind == "scope" for a in out):
        out.append(Assumption("scope", "instance proof — the certificate is not generalized"))
    verdict = chain_verdict(theorem.lhs, theorem.rhs, theorem.proof)
    if verdict.hard:
        out.append(Assumption("legacy", f"theorem {theorem.name}: not a proof of its claim — {verdict.hard}", theorem.owner))
    elif not verdict.replayed:
        out.append(Assumption(
            "unreplayed",
            f"theorem {theorem.name}: chain does not replay into its claim — " + "; ".join(verdict.soft),
            theorem.owner, key=("unreplayed", theorem.name),
        ))
    return tuple(out), prov


def structural_requires(theorem) -> Tuple[Assumption, ...]:
    """The requirement records of a theorem derived from its OWN chain
    (Faz 8 step 3b): declared axiom instances, the structures behind
    them, the transitive requirements of cited theorems, the registry
    answers the steps relied on (``registry``, audit 0b00e1b-FULL
    P0-3), a scope entry for an instance proof, a legacy entry for
    every ``from_axioms`` text no step accounts for — and the chain
    verdict (audit 0b00e1b-FULL M1-5, :func:`jacopy.proof.replay.chain_verdict`):
    ``legacy`` for an empty / purely hand-built chain, ``unreplayed``
    for a chain that does not replay into ``lhs = rhs``."""
    return _theorem_requirements(theorem)[0]


# ------------------------------------------------------------------ #
# the driver                                                         #
# ------------------------------------------------------------------ #


def check_goal(lhs: Expr, rhs: Expr, registry=None) -> Optional[str]:
    """The reason a goal is ill-typed, or ``None`` when its two sides
    have compatible kinds (:func:`~jacopy.central.objects.kind.kind_of`;
    zero fits every kind, unknown is not judged)."""
    from jacopy.central.objects.kind import kind_of

    a, b = kind_of(lhs, registry), kind_of(rhs, registry)
    for side, k in (("left", a), ("right", b)):
        if k.kind == "mismatch":
            return f"the {side}-hand side is a sum of different known types"
    if a.kind == "zero" or b.kind == "zero" or not (a.known and b.known):
        return None
    if a.kind != b.kind:
        return f"the sides have different kinds: {a.kind} vs {b.kind}"
    ca, cb = a.concrete_degree, b.concrete_degree
    if ca is not None and cb is not None and ca != cb:
        return f"the sides have different degrees: {ca} vs {cb}"
    if a.signature is not None and b.signature is not None and a.signature != b.signature:
        return f"the sides have different tensor signatures: {a.signature} vs {b.signature}"
    return None


def prove(
    engine,
    lhs: Expr,
    rhs: Expr = Integer(0),
    *,
    registry=None,
    max_steps: int = 1024,
    generality: str = "generic-function",
    owner=None,
    simplify_normal_forms: bool = True,
    oracle: Optional[str] = None,
) -> "ProofResult":
    """Normalize both sides with ``engine`` (optionally followed by the
    algebraic simplifier) and compare. Returns a :class:`ProofResult`:
    ``INVALID`` without running when the goal is ill-typed, ``BUDGET``
    when ``max_steps`` runs out, ``CLOSED`` when the normal forms
    agree, else ``RESIDUAL`` with the surviving difference. The chain
    runs ``lhs → normal form ← rhs`` (the right side's steps reversed).
    ``oracle`` overrides ``JACOPY_ORACLE`` for this call (model-oracle
    falsifier on CLOSED results; default off, :mod:`jacopy.oracle`)."""
    goal = Goal(lhs, rhs)
    reason = check_goal(lhs, rhs, registry)
    if reason is not None:
        return ProofResult.invalid(goal, reason, generality=generality, owner=owner)
    # the citing registry context (audit 0b00e1b-FULL P0-3): a cited
    # theorem's registry requirements are checked against ``registry``
    from jacopy.proof.registry_facts import registry_context

    with registry_context(registry):
        return _prove(engine, goal, lhs, rhs, registry, max_steps, generality, owner, simplify_normal_forms, oracle)


def _tracked_simplify(expr: Expr, registry):
    """``simplify(expr, registry)`` and the registry facts it consulted."""
    from jacopy.algorithms.simplify import simplify
    from jacopy.core.registry import track_reads
    from jacopy.proof.registry_facts import facts_from_log

    with track_reads() as log:
        out = simplify(expr, registry)
    return out, facts_from_log(log)


def _prove(engine, goal, lhs, rhs, registry, max_steps, generality, owner, simplify_normal_forms, oracle):

    from jacopy.proof.expansion import is_library_engine

    # the library engine returns the whole expression rewritten at the
    # step's site; an engine overriding its path is not trusted to (the
    # wrapper is then not minted) — one gate with the search
    engine_rewrites_at_site = is_library_engine(engine)

    def run(expr: Expr, cap: int):
        steps: List[ProofStep] = []
        cur = expr
        for _ in range(cap):
            nxt, step = engine.expand_once(cur)
            if step is None:
                break
            # the engine's step is LOCAL (the rewritten subterm); the
            # result's chain is a whole-expression transcript, so wrap it
            # — the local step rides along as the child that names the site
            steps.append(_whole_step(cur, nxt, step, at_site=engine_rewrites_at_site))
            cur = nxt
        else:
            nxt, step = engine.expand_once(cur)
            if step is not None:
                return cur, steps, True
        if simplify_normal_forms:
            simplified, facts = _tracked_simplify(cur, registry)
            if simplified != cur:
                steps.append(_mint(ProofStep(cur, simplified, rule="simplify", justification="canonical form",
                                             key=("pass", "simplify"), registry_facts=facts)))
                cur = simplified
        return cur, steps, False

    left, lsteps, lexh = run(lhs, max_steps)
    if lexh:
        chain = ProofChain(lsteps)
        return ProofResult.from_chain(chain, goal, status="BUDGET", max_steps=max_steps, generality=generality, owner=owner)
    remaining = max(max_steps - len(lsteps), 1)
    right, rsteps, rexh = run(rhs, remaining)
    if rexh:
        # the right-hand side ran out of budget: the goal is unchanged, the
        # left computation is the transcript, the right one a side
        # computation whose assumptions still count (audit dc44f79 F7)
        chain = ProofChain(lsteps)
        return ProofResult.from_chain(
            chain, goal, status="BUDGET", max_steps=max_steps, generality=generality, owner=owner,
            side_steps=rsteps, reason=f"the right-hand side's normalization exhausted the budget at {right._repr_inner()}",
        )
    if left == right:
        chain = ProofChain(lsteps + [_reversed_step(s) for s in reversed(rsteps)])
        result = ProofResult.from_chain(chain, goal, status="CLOSED", max_steps=max_steps, generality=generality, owner=owner)
        on_closed(lhs, rhs, registry=registry, source="prove", engine=engine, requires=result.requires, mode=oracle)
        return result
    from jacopy.core.expr import Neg, Sum

    diff = Sum(left, Neg(right)) if right != Integer(0) else left
    facts = ()
    if simplify_normal_forms:
        diff, facts = _tracked_simplify(diff, registry)
    steps = list(lsteps)
    if diff != left:
        # the right-hand side's normalization is attached to the residual
        # step so its assumptions and citations count (audit dc44f79 F1)
        steps.append(_mint(ProofStep(left, diff, rule="residual: lhs − rhs", justification="normal forms differ; the difference is the residual",
                               key=("pass", "residual"),
                               children=list(rsteps), registry_facts=facts)))
        rside = ()
    else:
        rside = tuple(rsteps)
    chain = ProofChain(steps)
    return ProofResult.from_chain(chain, goal, status="RESIDUAL", max_steps=max_steps, generality=generality, owner=owner, side_steps=rside)


__all__ = [
    "ASSUMPTION_KINDS",
    "Assumption",
    "Budget",
    "Goal",
    "PROVENANCE_KINDS",
    "ProofResult",
    "Provenance",
    "STATUSES",
    "check_goal",
    "package_version",
    "prove",
    "structural_requires",
]
