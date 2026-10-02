"""
Structure-free TM Cartan-calculus rewrite rules (operator / slot level).

These rules state relations of the TM Cartan calculus ``CARTAN_TM``
alone — no Poisson, Nambu or Drinfeld structure enters them — but they
were first written where a package proof needed them. They live here
so that every engine builder (the packages, the research
interface's :func:`~jacopy.research.engine_assembly.assemble_engine`)
can reach them from the central layer (audit 0B00E1B-FULL T2-1):

* :class:`MagicFormulaDefinition` — ``L_X ω = ι_X(dω) + d(ι_X ω)``
  (THEOREM-classified; previously ``jacopy.packages.drinfeld.twist``);
* :class:`LieIotaCommutatorDefinition` — ``ι_{[X,Y]} = ℒ_X ι_Y −
  ι_Y ℒ_X`` (THEOREM-classified; previously
  ``jacopy.packages.drinfeld.tilde_calculus``);
* :class:`DSquaredZeroDefinition` — ``d(d(x)) = 0`` (THEOREM-classified;
  previously ``jacopy.packages.poisson.nambu``);
* :class:`DWedgeLeibnizDefinition` — graded Leibniz of ``d`` over the
  wedge (previously ``jacopy.packages.poisson.nambu``).

The class bodies are moved verbatim (their docstrings still name the
engine that first registered them); the old module paths re-export the
SAME class objects, so every existing import keeps working and the
engines that register them are unchanged.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.derivation import Act, degree_of
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition
from jacopy.central.objects.interior import Interior
from jacopy.central.tangent.exterior import CARTAN_TM, d


class MagicFormulaDefinition(Definition):
    """THEOREM-classified Cartan magic as a form-level rewrite:
    ``L_X ω → ι_X(dω) + d(ι_X ω)`` for a TM Cartan Lie derivative on
    a determinable form of degree ≥ 1.

    The magic formula is a proven theorem (Phase 2 seed + the
    higher-degree audit to p = 5); the always-on engines apply it at
    EVAL sites via the Palais route. The twist proofs need it at the
    OPERATOR level: TW (7.25) writes the twisted family through
    ``𝒦_V = −ℒ_V + dι_V`` and the equivalence with the tilde
    calculus is mediated by magic on forms sitting INSIDE sharp
    slots, where no evaluation ever happens. Guarded away from
    vectors/multivectors (``wedge_degree`` protocol) — ``L_X Y`` is a
    bracket, not a magic candidate."""

    anchor = Act

    def __init__(
        self, registry: Optional[PropertyRegistry] = None
    ) -> None:
        self._registry = registry
        self.name = (
            "theorem Cartan magic: L_X ω = ι_X(dω) + d(ι_X ω)"
        )

    def matches(self, expr: Expr) -> bool:
        from jacopy.algebra.derivation import degree_of
        from jacopy.central.calculus.bracket_calculus import (
            LieDerivative,
        )

        if not (
            isinstance(expr, Act)
            and isinstance(expr.op, LieDerivative)
            and __import__("jacopy.central.calculus.bracket_calculus", fromlist=["belongs_to"]).belongs_to(expr.op, CARTAN_TM)
        ):
            return False
        arg = expr.arg
        if hasattr(arg, "wedge_degree"):
            return False
        try:
            k = degree_of(arg, self._registry).as_int()
        except ValueError:
            return False
        return k is not None and k >= 1

    def rewrite(self, expr: Expr) -> Expr:
        X = expr.op.vector
        arg = expr.arg
        return Sum(
            Act(Interior(X), d(arg)),
            d(Act(Interior(X), arg)),
        )

    def theorem_proof_builder(self):
        from jacopy.proof.chain import ProofChain
        from jacopy.proof.step import ProofStep

        def _builder(matched: Expr) -> ProofChain:
            return ProofChain(
                [
                    ProofStep(
                        matched,
                        self.rewrite(matched),
                        rule="Cartan magic (proven, Phase 2 + audit p ≤ 5)",
                        justification=(
                            "prove_cartan_magic_* close the eval-level "
                            "statement mechanically"
                        ),
                    )
                ]
            )

        return _builder


class LieIotaCommutatorDefinition(Definition):
    """THEOREM-classified Cartan relation ``ι_{[X,Y]} = ℒ_X ι_Y −
    ι_Y ℒ_X`` as an operator-level rewrite (proved in Phase 2 — the
    ``lie_iota`` relation; the always-on engines apply it at eval
    sites). Terminating: removes a bracket from an interior
    subscript; magic then converts the ``ℒ``'s to ``ι``/``d``."""

    anchor = Act

    def __init__(self) -> None:
        self.name = (
            "theorem lie-iota: ι_{[X,Y]} x = ℒ_X(ι_Y x) − ι_Y(ℒ_X x)"
        )

    def matches(self, expr: Expr) -> bool:
        return (
            isinstance(expr, Act)
            and isinstance(expr.op, Interior)
            and isinstance(expr.op.vector, LieBracketVF)
        )

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.central.tangent.exterior import CARTAN_TM

        br = expr.op.vector
        x = expr.arg
        return Sum(
            Act(
                CARTAN_TM.lie(br.X),
                Act(Interior(br.Y), x),
            ),
            Neg(
                Act(
                    Interior(br.Y),
                    Act(CARTAN_TM.lie(br.X), x),
                )
            ),
        )

    def theorem_proof_builder(self):
        from jacopy.proof.step import ProofStep

        def _builder(matched: Expr) -> ProofChain:
            return ProofChain(
                [
                    ProofStep(
                        matched,
                        self.rewrite(matched),
                        rule="lie-iota Cartan relation (proven, Phase 2)",
                        justification=(
                            "the eval-level statement closes "
                            "mechanically in the Cartan suite"
                        ),
                    )
                ]
            )

        return _builder


class DSquaredZeroDefinition(Definition):
    """``d(d(x)) → 0`` — THEOREM-classified (never in the always-on
    engines; ``d² = 0`` is proven on TM up to p = 5 via cited Jacobi
    instances — the higher-degree audit). Registered opt-in by the
    Nambu engine, where ``d(dF∧…)`` shapes must die inside interior
    slots."""

    anchor = Act

    def __init__(self) -> None:
        self.name = "theorem d² = 0: d(d(x)) → 0 (proven, Phase 2/audit)"

    def matches(self, expr: Expr) -> bool:
        from jacopy.central.calculus.bracket_calculus import (
            ExteriorDerivative,
            belongs_to,
        )

        return (
            isinstance(expr, Act)
            and isinstance(expr.op, ExteriorDerivative)
            and belongs_to(expr.op, CARTAN_TM)
            and isinstance(expr.arg, Act)
            and isinstance(expr.arg.op, ExteriorDerivative)
            and belongs_to(expr.arg.op, CARTAN_TM)
        )

    def rewrite(self, expr: Expr) -> Expr:
        return Integer(0)

    def theorem_proof_builder(self):
        from jacopy.proof.chain import ProofChain
        from jacopy.proof.step import ProofStep

        def _builder(matched: Expr) -> ProofChain:
            return ProofChain(
                [
                    ProofStep(
                        matched,
                        Integer(0),
                        rule="d² = 0 (proven to p = 5, cited Jacobi)",
                        justification=(
                            "prove_with_bracket_identities closes "
                            "(ddω)(Y…) = 0 mechanically"
                        ),
                    )
                ]
            )

        return _builder


class DWedgeLeibnizDefinition(Definition):
    """``d(α₁∧…∧α_n) → Σ_i (−1)^{|α₁|+…+|α_{i−1}|} α₁∧…∧dα_i∧…∧α_n``
    — the graded Leibniz of ``d`` over the wedge, as an ENGINE rule
    (the algorithm-level twin in ``product_rule`` cannot reach
    operator-atom SLOTS; the engine's slot protocol can — Phase
    5.E.4, the ``ι_Π(d(dF∧dG))`` shapes)."""

    anchor = Act

    def __init__(
        self, registry: Optional[PropertyRegistry] = None
    ) -> None:
        self._registry = registry
        self.name = (
            "d wedge Leibniz: d(α∧β) = dα∧β + (−1)^{|α|} α∧dβ"
        )

    def matches(self, expr: Expr) -> bool:
        from jacopy.central.calculus.bracket_calculus import (
            ExteriorDerivative,
            belongs_to,
        )

        if not (
            isinstance(expr, Act)
            and isinstance(expr.op, ExteriorDerivative)
            and belongs_to(expr.op, CARTAN_TM)
            and isinstance(expr.arg, Wedge)
        ):
            return False
        for c in expr.arg.children:
            try:
                degree_of(c, self._registry)
            except ValueError:
                return False
        return True

    def rewrite(self, expr: Expr) -> Expr:
        factors = tuple(expr.arg.children)
        running = 0
        terms = []
        for i, fac in enumerate(factors):
            new_factors = list(factors)
            new_factors[i] = Act(expr.op, fac)
            term: Expr = (
                Wedge(*new_factors)
                if len(new_factors) > 1
                else new_factors[0]
            )
            if running % 2 == 1:
                term = Neg(term)
            terms.append(term)
            deg = degree_of(fac, self._registry)
            running += deg.as_int()
        return Sum(*terms)


__all__ = [
    "MagicFormulaDefinition",
    "LieIotaCommutatorDefinition",
    "DSquaredZeroDefinition",
    "DWedgeLeibnizDefinition",
]
