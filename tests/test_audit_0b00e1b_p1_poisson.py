"""Audit 0b00e1b-FULL — P1, Poisson / symplectic lane.

* M3-1 ≡ M3-2 (group G10): a rule that holds for ONE calculus — the
  declared closedness ``dω = 0`` of a symplectic form, the Nambu
  fundamental identity — is scoped to the TM Cartan calculus by
  operator identity (:func:`belongs_to`), not by the node shape; the
  ``d``/``L`` of another Lie algebroid is a different operator.
* M3-3: the general Koszul Jacobi chain is assembled from replayed
  records only — every zero seed carries its own theorem, the linear
  combination is the claim of an explicit step, and the ``[π,π] = 0``
  declaration is a structural requirement of the result.

Every acceptance test builds its target equation here.
"""

import os

import pytest

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Integer, Neg, Product, Sum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.central.calculus.bracket_calculus import (
    BracketCalculus,
    ExteriorDerivative,
    IntrinsicDDefinition,
    LieDerivative,
    belongs_to,
)
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.tangent.exterior import CARTAN_TM, d
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.normalize import normalize
from jacopy.proof.replay import chain_shape
from jacopy.proof.result import Goal, ProofResult, prove
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.proof.theorems import Theorem


def _declared(requires):
    return [a.name for a in requires if a.kind == "declared"]


# --------------------------------------------------------------------- #
# M3-1: SymplecticClosedDeclaration is a statement about d_TM          #
# --------------------------------------------------------------------- #


def _so3_plus_r():
    """A = so(3) ⊕ ℝ, zero anchor: [e1,e2]=e3, [e2,e3]=e1, [e3,e1]=e2,
    e4 central; ω = e¹² + e³⁴ (as components)."""
    from jacopy.packages.poisson.symplectic import symplectic_structure

    e1, e2, e3, e4 = vector_fields("e1 e2 e3 e4")
    S = symplectic_structure()
    table = {(e1, e2): e3, (e2, e3): e1, (e3, e1): e2}

    def br(u, v):
        if (u, v) in table:
            return table[(u, v)]
        if (v, u) in table:
            return Neg(table[(v, u)])
        return Integer(0)

    A = BracketCalculus(
        "audit-so3+R", anchor=lambda u: Integer(0), bracket=br, skew=True
    )

    class Components(Definition):
        anchor = MultiEval
        name = "data: ω = e¹² + e³⁴"

        def matches(self, q):
            return (
                isinstance(q, MultiEval)
                and q.head == S.omega
                and q.arity == 2
                and all(v in (e1, e2, e3, e4) for v in q.args)
            )

        def rewrite(self, q):
            if q.args in ((e1, e2), (e3, e4)):
                return Integer(1)
            if q.args in ((e2, e1), (e4, e3)):
                return Integer(-1)
            return Integer(0)

    return S, A, Components(), (e1, e2, e3, e4)


class TestM31ClosedFormScope:
    def test_rule_matches_only_the_tm_d_on_both_paths(self):
        from jacopy.packages.poisson import poisson_structure
        from jacopy.packages.poisson.symplectic import (
            SymplecticClosedDeclaration,
        )
        from jacopy.packages.poisson.tilde import tilde_calculus

        S, A, _, (e1, e2, e3, _e4) = _so3_plus_r()
        rule = SymplecticClosedDeclaration(S)
        tm = Act(CARTAN_TM.d, S.omega)
        foreign = Act(A.d, S.omega)
        tilde = Act(tilde_calculus(poisson_structure()).d, S.omega)
        # direct Act path
        assert rule.matches(tm)
        assert not rule.matches(foreign)
        assert not rule.matches(tilde)
        # evaluated-head path
        assert rule.matches(MultiEval(tm, e1, e2, e3))
        assert not rule.matches(MultiEval(foreign, e1, e2, e3))
        # a hand-built d that merely COMPARES equal to the TM d (same
        # name/degree/calculus name/skew) is not the TM calculus' d
        spoof = ExteriorDerivative("Cartan-TM", skew=True)
        assert spoof == CARTAN_TM.d
        assert not belongs_to(spoof, CARTAN_TM)
        assert not rule.matches(Act(spoof, S.omega))
        # the TM calculus' OTHER operator is not d: L_Y ω is not closed
        Y = vector_fields("Y")[0]
        assert not rule.matches(Act(CARTAN_TM.lie(Y), S.omega))
        assert not rule.matches(MultiEval(Act(CARTAN_TM.lie(Y), S.omega), e1, e2))

    def test_foreign_algebroid_d_omega_is_not_closed(self):
        from jacopy.packages.poisson.symplectic import symplectic_engine

        S, A, data, (e1, e2, _e3, e4) = _so3_plus_r()
        reg = PropertyRegistry()
        # (d_A ω)(e1,e2,e4) = −ω([e1,e2],e4) + ω([e1,e4],e2) − ω([e2,e4],e1)
        #                  = −ω(e3,e4) = −1
        node = MultiEval(Act(A.d, S.omega), e1, e2, e4)
        eng = symplectic_engine(S, registry=reg, declare_closed=True)
        eng.register(IntrinsicDDefinition(A, reg))
        eng.register(data)
        assert normalize(eng, node, reg).expr == Integer(-1)
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(node, Integer(0), registry=reg, engine=eng)
        r = prove(eng, node, Integer(-1), registry=reg)
        assert r.closed

    def test_tm_closedness_still_closes_and_is_declared(self):
        from jacopy.packages.poisson.symplectic import symplectic_engine

        S, _, _, _ = _so3_plus_r()
        reg = PropertyRegistry()
        X, Y, Z = vector_fields("X Y Z")
        eng = symplectic_engine(S, registry=reg, declare_closed=True)
        for lhs in (d(S.omega), MultiEval(d(S.omega), X, Y, Z)):
            r = prove(eng, lhs, Integer(0), registry=reg)
            assert r.closed
            assert any("dω = 0" in n for n in _declared(r.requires))

    def test_tm_calculus_name_is_reserved(self):
        with pytest.raises(ValueError, match="reserved"):
            BracketCalculus(
                "Cartan-TM", anchor=lambda u: u, bracket=lambda u, v: Integer(0),
                skew=True, right_leibniz=True,
            )


# --------------------------------------------------------------------- #
# M3-2: the Nambu FI is a statement about L_TM                         #
# --------------------------------------------------------------------- #


class TestM32NambuFIScope:
    @staticmethod
    def _setup():
        reg = PropertyRegistry()
        x, y, z = functions("x y z", registry=reg)
        B = BracketCalculus(
            "audit-B", anchor=lambda u: Integer(0), bracket=lambda u, v: Integer(0)
        )
        return reg, (x, y, z), B

    def test_fi_rule_refuses_a_foreign_lie_derivative(self):
        from jacopy.packages.poisson.nambu import (
            NambuFIDeclaration,
            nambu_structure,
        )

        reg, (x, y, _z), B = self._setup()
        for N, om, et in (
            (nambu_structure(p=1), d(y), d(Product(x, x))),
        ):
            rule = NambuFIDeclaration(N, reg)
            for calc, ok in ((B, False), (CARTAN_TM, True)):
                e = Act(N.sharp_vf(Act(calc.lie(N.sharp_vf(om)), et)), x)
                assert rule.matches(e) is ok
        # an L that only COMPARES like the TM one (no owning calculus)
        spoof = LieDerivative("Cartan-TM", x)
        assert not belongs_to(spoof, CARTAN_TM)

    def test_p2_foreign_and_tm_no_longer_share_a_normal_form(self):
        from jacopy.packages.poisson.nambu import (
            NambuFIDeclaration,
            nambu_engine,
            nambu_structure,
        )

        reg, (x, y, z), B = self._setup()
        N = nambu_structure("Pi3", p=2)
        om = Wedge(d(y), d(z))
        et = Wedge(d(x), d(Product(x, z)))

        def node(calc):
            return Act(N.sharp_vf(Act(calc.lie(N.sharp_vf(om)), et)), y)

        def engine():
            eng = nambu_engine(N, registry=reg)
            eng.register(NambuFIDeclaration(N, reg))
            return eng

        tm_nf = normalize(engine(), node(CARTAN_TM), reg).expr
        assert "L_" not in str(tm_nf)  # the FI fired for L_TM
        foreign = node(B)
        assert "L_" in str(normalize(engine(), foreign, reg).expr)
        # before the fix: the foreign side "proved" equal to the TM value
        # (−1 on Π = ∂x∧∂y∧∂z, while L^B η = 0 gives 0)
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(foreign, tm_nf, registry=reg, engine=engine())
