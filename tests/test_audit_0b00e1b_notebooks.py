"""Audit 0B00E1B-FULL — notebook regressions (fix/notebooks lane).

``bracket_twist_research_interface.ipynb`` §1.5 stopped closing DD (D.19)
at p = 3 after fc0e9d8 (M2-1 follow-up: ``admits_alternation`` is
DEFAULT REJECT). Vector-slot linearity rewrites ``L_{U+Πω}`` to the
operator sum ``(L_U + L_Πω)``; ``Act(Sum(L_U, L_Πω), g)`` was not
certified, so the enclosing alternating ``MultiEval`` was rebuilt plain
and the alternation of the forms η, μ inside was lost for good (the
residual is a list of cyclic permutations ``η(A,B,C) − η(B,C,A)``).

An operator sum inherits alternation when every summand does:
``(A + B)α = Aα + Bα`` and a sum of alternating values is alternating.
Everything else stays rejected (tensors, the ``d`` of a non-skew
calculus, mixed sums).
"""

import pytest

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Integer, Neg, Sum
from jacopy.core.multi_eval import MultiEval, admits_alternation
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.central.calculus.bracket_calculus import BracketCalculus
from jacopy.central.objects import forms, tensors, vector_fields
from jacopy.central.tangent.exterior import CARTAN_TM
from jacopy.central.tangent.lie_bracket import lie_bracket


def _L(X):
    return CARTAN_TM.lie(X)


class TestOperatorSumCertification:
    def test_sum_of_lie_derivatives_of_a_form_is_alternating(self):
        U, V = vector_fields("U V")
        (om,) = forms("ω", degree=2)
        assert admits_alternation(Act(Sum(_L(U), _L(V)), om))
        assert admits_alternation(Act(Neg(_L(U)), om))
        assert admits_alternation(Act(Sum(_L(U), Neg(_L(V))), om))
        Y1, Y2 = vector_fields("Y1 Y2")
        assert MultiEval(Act(Sum(_L(U), _L(V)), om), Y1, Y2).alternating

    def test_operator_sum_of_a_tensor_is_rejected(self):
        U, V = vector_fields("U V")
        (T,) = tensors("T", upper=0, lower=2)
        assert not admits_alternation(Act(Sum(_L(U), _L(V)), T))
        Y1, Y2 = vector_fields("Y1 Y2")
        assert not MultiEval(Act(Sum(_L(U), _L(V)), T), Y1, Y2).alternating

    def test_operator_sum_with_a_non_skew_d_is_rejected(self):
        # dα(u,u) = −α([u,u]) for a non-skew bracket: d declares False,
        # so a sum containing it must not be certified.
        U, V = vector_fields("U V")
        (om,) = forms("ω", degree=1)
        calc = BracketCalculus("nsk_nb", anchor=lambda s: s, bracket=lie_bracket)
        assert not calc.skew
        assert not admits_alternation(Act(Sum(_L(U), calc.d), om))
        assert not admits_alternation(Act(Neg(calc.d), om))


class TestDoubleMetricInvarianceP3:
    """DD (D.19) / Claim 6 at p = 3 on two slots — the notebook check."""

    def _setup(self):
        from jacopy.packages.poisson.nambu import nambu_structure

        reg = PropertyRegistry()
        U, V, W = vector_fields("U V W")
        N = nambu_structure("Π", p=3)
        a, b, c = forms("ω η μ", degree=3)
        slots = tuple(vector_fields("Y1 Y2"))
        return reg, N, U, a, V, b, W, c, slots

    def test_closes(self):
        import jacopy.packages.drinfeld.metric_invariance as mi

        reg, N, U, a, V, b, W, c, slots = self._setup()
        chain = mi.prove_double_metric_invariance(
            N, U, a, V, b, W, c, slots, registry=reg
        )
        assert chain.steps

    def test_wrong_sign_does_not_close(self):
        # ℒ_ρ g(e₂,e₃) − g([e₁,e₂],e₃) + g(e₂,[e₁,e₃]) = 2 g(e₂,[e₁,e₃]) ≠ 0.
        import jacopy.packages.drinfeld.metric_invariance as mi
        from jacopy.packages.drinfeld.double import (
            evaluate_on_slots,
            nambu_double,
        )
        from jacopy.packages.drinfeld.metric_invariance import double_metric

        reg, N, U, a, V, b, W, c, slots = self._setup()
        rho1 = Sum(U, N.sharp_vf(a))
        v12, f12 = nambu_double(N, U, a, V, b)
        v13, f13 = nambu_double(N, U, a, W, c)
        node = evaluate_on_slots(
            Sum(
                Act(CARTAN_TM.lie(rho1), double_metric(N, V, b, W, c)),
                Neg(double_metric(N, v12, f12, W, c)),
                double_metric(N, V, b, v13, f13),
            ),
            slots,
        )
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                node,
                Integer(0),
                registry=reg,
                engine=mi.nambu_tilde_engine(N, reg, declare_fi=True),
                max_steps=90000,
            )
