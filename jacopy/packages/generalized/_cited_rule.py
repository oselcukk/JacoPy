"""
Theorem-citing rewrite rules (audit 0B00E1B-FULL M1-4).

A rule that rewrites by a PROVEN result (Uchino Prop 2.2, the (7.2)
right-Leibniz, ...) is a citation, not a definitional unfolding: its
steps must carry the cited :class:`~jacopy.proof.theorems.Theorem` so
the theorem's own requirements (the declared axioms it was proved
from) flow transitively into every result that uses the rule.

:class:`CitedTheoremMixin` gives a ``Definition`` subclass that
contract:

* ``role = "theorem"`` and a non-``None`` :meth:`theorem_proof_builder`
  (the engine then tags the step ``"theorem"`` and records
  ``cites=rule.theorem``; foundational mode inlines the cited chain);
* the cited theorem is PROVED ON THE RULE'S OWN STRUCTURE, lazily, on
  the first candidate match — and when that proof fails (the structure
  does not support the theorem) the rule never fires: default reject.

The mixin is deliberately NOT a ``Definition`` subclass (it is not a
rule by itself, so it has no entry in the role inventory).
"""

from __future__ import annotations

from typing import Optional

from jacopy.proof.chain import ProofChain
from jacopy.proof.strategies import ProofFailure

_UNBUILT = object()


class CitedTheoremMixin:
    """Mixin for theorem-citing rules; subclasses implement
    :meth:`_prove_cited` (returning the cited ``Theorem``) and call
    :meth:`_licensed` inside ``matches``."""

    role = "theorem"

    _cited_theorem = _UNBUILT

    def _prove_cited(self):  # pragma: no cover - abstract
        raise NotImplementedError

    def _cited(self):
        if self._cited_theorem is _UNBUILT:
            try:
                self._cited_theorem = self._prove_cited()
            except (NotImplementedError, RecursionError):
                # programming errors (both are RuntimeError subclasses):
                # never swallowed into an inert rule
                raise
            except (ProofFailure, ValueError, RuntimeError):
                # the structure does not support the cited theorem, or
                # the lazy prover did not converge (RuntimeError): the
                # verdict is cached and the rule stays inert (default
                # reject) — never re-attempted on every candidate
                self._cited_theorem = None
        return self._cited_theorem

    def _licensed(self) -> bool:
        return self._cited() is not None

    @property
    def theorem(self):
        """The cited :class:`Theorem` (``None`` when it could not be
        proved on this structure — the rule then never matches)."""
        return self._cited()

    def theorem_proof_builder(self):
        def build(_expr) -> ProofChain:
            t = self._cited()
            return t.proof if t is not None else ProofChain([])

        return build


def private_function(name: str = "f"):
    """A generic scalar function declared in a PRIVATE registry, for
    proving a cited theorem without writing helper symbols into the
    caller's registry. Returns ``(function, registry)``."""
    from jacopy.central.objects import functions
    from jacopy.core.registry import PropertyRegistry

    reg = PropertyRegistry()
    fns = functions(name, registry=reg)
    return fns, reg


__all__ = ["CitedTheoremMixin", "private_function"]
