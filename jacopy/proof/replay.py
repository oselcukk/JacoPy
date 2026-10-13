"""
Chain-shape replay (audit 0b00e1b-FULL M1-5 ≡ M1-6 ≡ K2-7 ≡ M1X-4).

A theorem record claims ``lhs = rhs`` and stores a :class:`ProofChain`
as its evidence. The record is only as good as the chain is
*connected*: every step must rewrite the expression the previous step
left behind, and the chain must run between the two sides of the
claim. This module replays that SHAPE — it does not re-run the rules
(a step's ``before = after`` is the rule's responsibility; see
:mod:`jacopy.proof.step`), but it refuses a chain whose steps do not
compose into the claimed equation (an empty chain for ``1 = 0``, a
step lifted from another proof, a chain that stops short).

Replay model. The running expression ``W`` starts at an endpoint
form (below). Each top-level step either

* is a WHOLE-expression step: ``step.before == W`` → ``W := step.after``;
* or a LOCAL step (the expansion engine records the rewritten
  subterm): ``step.before`` occurs in ``W`` and its FIRST occurrence
  in the engine's own traversal order (children left to right, an
  atom's ``rewritable_slots``, then the node — the leftmost-innermost
  site :meth:`ExpansionEngine.expand_once` fires at) is replaced by
  ``step.after``, rebuilt with the node's own ``_rebuild`` /
  ``with_slots``. Replacing an occurrence of ``b`` by ``a`` is a
  congruence step for the local equation ``b = a`` whichever
  occurrence is chosen; the engine's order is used so the replay
  tracks the recorded transcript.

Accepted endpoint forms (:data:`ENDPOINT_FORMS`):

* ``"lhs→rhs"`` — ``W`` starts at ``lhs`` and ends at ``rhs``
  (:func:`~jacopy.proof.result.prove`'s ``lhs → NF ← rhs``);
* ``"rhs→lhs"`` — the same read backwards;
* ``"lhs−rhs→0"`` — ``W`` starts at the obstruction
  ``Sum(lhs, Neg(rhs))`` (as :class:`~jacopy.proof.strategies.ExpandAndSimplify`
  builds it) and ends at ``0``;
* ``"rhs−lhs→0"`` — the same with the sides swapped.

``lhs == rhs`` with an empty chain is the reflexive form. Anything
else is ``broken``: the record's chain does not establish its claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from jacopy.core.expr import Expr, Integer, Neg, Sum

ENDPOINT_FORMS = ("reflexive", "lhs→rhs", "rhs→lhs", "lhs−rhs→0", "rhs−lhs→0")


@dataclass(frozen=True)
class ChainShape:
    """The replay verdict: ``ok`` with the endpoint ``form`` it matched,
    or not ok with the ``reason`` of the first failure."""

    ok: bool
    form: Optional[str] = None
    reason: str = ""

    def __str__(self) -> str:
        return f"connected ({self.form})" if self.ok else f"not a proof of the claim: {self.reason}"


def _replace_first(expr: Expr, old: Expr, new: Expr):
    """``expr`` with the first occurrence of ``old`` (engine traversal
    order) replaced by ``new``; ``None`` when ``old`` does not occur."""
    if not expr.is_atom:
        children = list(expr.children)
        for i, c in enumerate(children):
            r = _replace_first(c, old, new)
            if r is not None:
                children[i] = r
                return expr._rebuild(tuple(children))
    else:
        slots = getattr(expr, "rewritable_slots", None)
        if slots:
            slots = tuple(slots)
            for i, sub in enumerate(slots):
                r = _replace_first(sub, old, new)
                if r is not None:
                    return expr.with_slots(*(slots[:i] + (r,) + slots[i + 1:]))
    if expr == old:
        return new
    return None


def replay(start: Expr, steps) -> Tuple[Optional[Expr], str]:
    """Run ``steps`` from ``start``; ``(final, "")`` or ``(None, reason)``."""
    cur = start
    for i, s in enumerate(steps):
        if s.before == cur:
            cur = s.after
            continue
        try:
            nxt = _replace_first(cur, s.before, s.after)
        except Exception as exc:  # a rebuild refused the substitution
            return None, f"step {i} [{s.rule}] could not be replayed: {type(exc).__name__}: {exc}"
        if nxt is None:
            return None, (
                f"step {i} [{s.rule}] rewrites {s.before._repr_inner()[:120]}, which does not occur in "
                f"the running expression {cur._repr_inner()[:120]}"
            )
        cur = nxt
    return cur, ""


def chain_shape(lhs: Expr, rhs: Expr, chain) -> ChainShape:
    """Does ``chain`` replay into a proof of ``lhs = rhs``
    (module docstring)? The first matching endpoint form wins."""
    steps = tuple(getattr(chain, "steps", chain))
    if not steps:
        if lhs == rhs:
            return ChainShape(True, "reflexive")
        return ChainShape(False, reason="empty chain for a non-trivial claim")
    candidates = (
        ("lhs→rhs", lhs, rhs),
        ("rhs→lhs", rhs, lhs),
        ("lhs−rhs→0", Sum(lhs, Neg(rhs)), Integer(0)),
        ("rhs−lhs→0", Sum(rhs, Neg(lhs)), Integer(0)),
    )
    first_reason = ""
    for form, start, end in candidates:
        if steps[0].before != start and _replace_first(start, steps[0].before, steps[0].after) is None:
            continue
        final, reason = replay(start, steps)
        if final is None:
            first_reason = first_reason or f"{form}: {reason}"
            continue
        if final == end:
            return ChainShape(True, form)
        first_reason = first_reason or (
            f"{form}: the chain ends at {final._repr_inner()[:120]}, not at {end._repr_inner()[:120]}"
        )
    if not first_reason:
        first_reason = (
            f"the first step [{steps[0].rule}] starts at {steps[0].before._repr_inner()[:120]}, "
            "which is neither side of the claim nor their difference"
        )
    return ChainShape(False, reason=first_reason)


__all__ = ["ChainShape", "ENDPOINT_FORMS", "chain_shape", "replay"]


# ------------------------------------------------------------------ #
# accountability of the steps                                        #
# ------------------------------------------------------------------ #


def accountable(step) -> bool:
    """A step is ACCOUNTABLE when something other than its author's word
    licenses it: it was MINTED by a library producer — the expansion
    engine's fired rule, a library normalization pass, a library
    strategy's inference (:func:`jacopy.proof.step.is_minted`; threat
    model there) — or it is an identity (``before == after``). Any step
    built through the public ``ProofStep`` constructor is a hand-built
    claim, whatever tag or key it carries (audit 0b00e1b M1-5:
    "unlabelled hand-built step"; review 2026-10-01 #3)."""
    from jacopy.proof.step import is_minted

    # (review 2026-10-01 #3) the caller-supplied tag / key are NOT
    # evidence: anyone can write them. Only a step minted by a library
    # producer — or an identity, which proves nothing — is accountable
    return is_minted(step) or step.before == step.after


def unaccountable_steps(steps) -> Tuple[str, ...]:
    """Rule names of the unaccountable steps (children included; the
    sub-proof under a theorem CITATION is the cited record's business)."""
    out = []

    def walk(seq):
        for s in seq:
            if not accountable(s):
                out.append(s.rule)
            if getattr(s, "cites", None) is None:
                walk(s.children)

    walk(steps)
    return tuple(out)


def _any_accountable(steps) -> bool:
    for s in steps:
        if accountable(s) and s.before != s.after:
            return True
        if _any_accountable(s.children):
            return True
    return False


@dataclass(frozen=True)
class ChainVerdict:
    """What a theorem record's chain establishes.

    * ``hard`` — a reason the record is NOT a proof at all (empty chain
      for a non-trivial claim; no machine-produced step anywhere): the
      record is legacy (refused by a TheoremBook, cited only explicitly).
    * ``soft`` — reasons the chain does not replay into the claim
      mechanically (disconnected / other endpoints / hand-built steps):
      the record's requirements are still derived, but it is
      "requirements-derived", not "replayed"; it is cited only with
      ``allow_legacy=True`` and every citing result carries the marker.
    """

    shape: ChainShape
    unaccountable: Tuple[str, ...] = ()
    hard: str = ""

    @property
    def replayed(self) -> bool:
        return not self.hard and self.shape.ok and not self.unaccountable

    @property
    def soft(self) -> Tuple[str, ...]:
        out = []
        if not self.shape.ok:
            out.append(self.shape.reason)
        if self.unaccountable:
            names = sorted(set(self.unaccountable))
            shown = ", ".join(repr(n[:60]) for n in names[:4]) + (f", … ({len(names)} rules)" if len(names) > 4 else "")
            out.append(f"{len(self.unaccountable)} hand-built step(s) not produced by a library producer: {shown}")
        return tuple(out)


def chain_verdict(lhs: Expr, rhs: Expr, chain) -> ChainVerdict:
    steps = tuple(getattr(chain, "steps", chain))
    shape = chain_shape(lhs, rhs, steps)
    hard = ""
    if not steps and lhs != rhs:
        hard = "empty chain for a non-trivial claim"
    elif steps and lhs != rhs and not _any_accountable(steps):
        hard = "no step of the chain is machine-produced (every step is a hand-built claim)"
    return ChainVerdict(shape, unaccountable_steps(steps), hard)


__all__ += ["ChainVerdict", "accountable", "chain_verdict", "unaccountable_steps"]
