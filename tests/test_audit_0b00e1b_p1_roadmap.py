"""Audit 0b00e1b-FULL, P1 roadmap lane: M7-4, M4-3 and the calculus
scope of ``FISharpPairingSwapDefinition``.

* M7-4: the two-fold E-Cartan structure equations [ADM Prop 3.9,
  (3.48)] and the non-metricity 1-forms ``Q_ab`` [ADM (2.12)-(2.13);
  guideline item 11l] — mechanical, replayed, wrong variants refused.
* M4-3: the Nambu double's Leibniz-Jacobi (form component) via the
  Π-twist (SLOW: ``JACOPY_RUN_SLOW=1``).
* FI pairing swap: fires under the TM Cartan ``d`` only.
"""

import os

import pytest

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Integer, Neg, Product, Sum
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure
from jacopy.proof.theorems import Theorem
from jacopy.central.objects import Bundle, forms, functions, vector_fields
from jacopy.central.objects.connection import connection
from jacopy.central.objects.frame import Frame, FrameIndex
from jacopy.central.objects.interior import Interior
from jacopy.central.algebroid import algebroid, locality_projector
from jacopy.packages.metric_affine.e_connection import e_connection
from jacopy.packages.metric_affine.metric import MetricValue, metric

SLOW = pytest.mark.skipif(
    not os.environ.get("JACOPY_RUN_SLOW"),
    reason="minutes (the Nambu-double Jacobi bridge); set JACOPY_RUN_SLOW=1",
)


def _replayed(lhs, rhs, chain, **kw) -> Theorem:
    return Theorem("t", "t", lhs, rhs, chain, **kw).with_structural_requires()


# --------------------------------------------------------------------- #
# M7-4 — E-Cartan structure equations [ADM Prop 3.9]                     #
# --------------------------------------------------------------------- #


@pytest.fixture()
def alg():
    reg = PropertyRegistry()
    E = algebroid("E", Bundle("E"), declare=("local", "regular"))
    nabla = e_connection(E)
    fr = Frame("e", bundle=E.bundle)
    P = locality_projector(E)
    return reg, E, nabla, fr, P


class TestECartanFirst:
    def test_closes_declaration_free_and_replays(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_first_sides,
            prove_e_cartan_first,
        )

        reg, E, nabla, fr, _ = alg
        chain = prove_e_cartan_first(E, nabla, fr, "a", "b", "c", registry=reg)
        lhs, rhs, _ = e_cartan_first_sides(E, nabla, fr, "a", "b", "c")
        t = _replayed(lhs, rhs, chain)
        assert t.chain_replayed and not t.legacy
        # no declared axiom: an identity for an arbitrary E-connection
        assert not any(a.kind == "declared" for a in t.requires)

    def test_even_without_algebroid_declarations(self):
        from jacopy.packages.metric_affine.e_cartan import prove_e_cartan_first

        reg = PropertyRegistry()
        E = algebroid("F", Bundle("F"))
        nabla = e_connection(E)
        fr = Frame("c", bundle=E.bundle)
        assert prove_e_cartan_first(E, nabla, fr, "a", "b", "d", registry=reg).steps

    def test_wrong_wedge_sign_is_refused(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_first_sides,
        )

        reg, E, nabla, fr, _ = alg
        lhs, rhs, derived = e_cartan_first_sides(E, nabla, fr, "a", "b", "c")
        d_term, wedge = rhs.children
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs,
                Sum(d_term, Neg(wedge)),
                registry=reg,
                engine=e_cartan_engine(E, derived, nabla, fr, registry=reg),
            )

    def test_projected_d_is_the_wrong_derivative(self, alg):
        """ᴸT is built with the UNPROJECTED modified bracket: with d̂(∇)
        the (1−𝒫)Λ anomaly is left over — why ADM needs two d's."""
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_first_sides,
        )

        reg, E, nabla, fr, P = alg
        lhs, rhs, derived = e_cartan_first_sides(
            E, nabla, fr, "a", "b", "c", projected_d=True
        )
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs,
                rhs,
                registry=reg,
                engine=e_cartan_engine(
                    E, derived, nabla, fr, registry=reg, projector=P
                ),
            )

    def test_bound_index_collision(self, alg):
        from jacopy.packages.metric_affine.e_cartan import prove_e_cartan_first

        reg, E, nabla, fr, _ = alg
        with pytest.raises(ValueError):
            prove_e_cartan_first(E, nabla, fr, "s", "b", "c", registry=reg)


class TestECartanSecond:
    def test_closes_under_frame_decomposition_and_replays(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_second_sides,
            prove_e_cartan_second,
        )

        reg, E, nabla, fr, P = alg
        chain = prove_e_cartan_second(
            E, nabla, fr, P, "a", "b", "c", "d", registry=reg
        )
        lhs, rhs, _ = e_cartan_second_sides(E, nabla, fr, P, "a", "b", "c", "d")
        t = _replayed(lhs, rhs, chain)
        assert t.chain_replayed and not t.legacy
        declared = [a for a in t.requires if a.kind == "declared"]
        assert declared and all("frame decomposition" in a.name for a in declared)
        # every axiom (assumption) step carries an APA source
        assumption_steps = [s for s in chain.steps if s.role == "assumption"]
        assert assumption_steps and all(s.source for s in assumption_steps)

    def test_wrong_wedge_sign_is_refused(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_second_sides,
        )

        reg, E, nabla, fr, P = alg
        lhs, rhs, derived = e_cartan_second_sides(E, nabla, fr, P, "a", "b", "c", "d")
        d_term, wedge = rhs.children
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs,
                Sum(d_term, Neg(wedge)),
                registry=reg,
                engine=e_cartan_engine(
                    E, derived, nabla, fr, registry=reg,
                    projector=P, decomposed=True,
                ),
            )

    def test_unprojected_d_is_the_wrong_derivative(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_second_sides,
        )

        reg, E, nabla, fr, P = alg
        lhs, rhs, derived = e_cartan_second_sides(
            E, nabla, fr, P, "a", "b", "c", "d", projected_d=False
        )
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs,
                rhs,
                registry=reg,
                engine=e_cartan_engine(
                    E, derived, nabla, fr, registry=reg,
                    projector=P, decomposed=True,
                ),
            )

    def test_honest_without_frame_decomposition(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_second_sides,
        )

        reg, E, nabla, fr, P = alg
        lhs, rhs, derived = e_cartan_second_sides(E, nabla, fr, P, "a", "b", "c", "d")
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs,
                rhs,
                registry=reg,
                engine=e_cartan_engine(
                    E, derived, nabla, fr, registry=reg, projector=P
                ),
            )


# --------------------------------------------------------------------- #
# M7-4 — non-metricity 1-forms Q_ab [ADM (2.12)-(2.13)]                  #
# --------------------------------------------------------------------- #


@pytest.fixture()
def tm():
    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    (X,) = vector_fields("X")
    return reg, f, X, connection(), metric(), Frame("e")


class TestNonMetricityForms:
    def test_symmetric_on_arbitrary_vector(self, tm):
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            prove_nonmetricity_form_symmetric,
        )

        reg, f, X, nabla, g, fr = tm
        assert prove_nonmetricity_form_symmetric(nabla, g, fr, "a", "b", X, registry=reg).steps

    def test_tensorial(self, tm):
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            prove_nonmetricity_form_tensorial,
        )

        reg, f, X, nabla, g, fr = tm
        assert prove_nonmetricity_form_tensorial(nabla, g, fr, "a", "b", X, f, registry=reg).steps

    def test_components_replay(self, tm):
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            nonmetricity_form,
            nonmetricity_form_component_formula,
            prove_nonmetricity_form_components,
        )

        reg, f, X, nabla, g, fr = tm
        chain = prove_nonmetricity_form_components(nabla, g, fr, "a", "b", "c", registry=reg)
        lhs = Pairing(nonmetricity_form(nabla, g, fr, "a", "b"), fr.field("c"))
        rhs = nonmetricity_form_component_formula(nabla, g, fr, "a", "b", "c")
        t = _replayed(lhs, rhs, chain)
        assert t.chain_replayed and not t.legacy
        assert any(s.source for s in chain.steps if "non-metricity form" in s.rule)

    def test_cartan_form_with_connection_forms(self, tm):
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            prove_nonmetricity_form_cartan,
        )

        reg, f, X, nabla, g, fr = tm
        assert prove_nonmetricity_form_cartan(nabla, g, fr, "a", "b", "c", registry=reg).steps

    def test_wrong_sign_component_formula_refused(self, tm):
        from jacopy.packages.metric_affine.frame_components import (
            connection_coefficient,
        )
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            _engine,
            nonmetricity_form,
        )

        reg, f, X, nabla, g, fr = tm
        ea, eb, ec, es = (fr.field(i) for i in "abcs")
        s = FrameIndex("s")
        wrong = Sum(
            Act(ec, MetricValue(g.name, ea, eb)),
            IndexedSum(s, fr, Product(connection_coefficient(nabla, fr, "s", "c", "a"), MetricValue(g.name, es, eb))),
            IndexedSum(s, fr, Product(connection_coefficient(nabla, fr, "s", "c", "b"), MetricValue(g.name, ea, es))),
        )
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                Pairing(nonmetricity_form(nabla, g, fr, "a", "b"), ec),
                wrong,
                registry=reg,
                engine=_engine(reg, nabla, g, fr, decomposed=True),
            )

    def test_slot_is_the_direction_not_a_frame_leg(self, tm):
        """Q_ab(v) = Q(v, e_a, e_b) [ADM (2.12)] — NOT Q(e_a, ·, ·)
        (an earlier, wrong reading): Q_ab(e_c) ≠ Q(e_a, e_b, e_c)."""
        from jacopy.packages.metric_affine.metric import nonmetricity
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            _engine,
            nonmetricity_form,
        )

        reg, f, X, nabla, g, fr = tm
        ea, eb, ec = (fr.field(i) for i in "abc")
        eng = _engine(reg, nabla, g, fr)
        q = Pairing(nonmetricity_form(nabla, g, fr, "a", "b"), ec)
        assert ExpandAndSimplify().prove(q, nonmetricity(nabla, g, ec, ea, eb), registry=reg, engine=eng).steps
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                q, nonmetricity(nabla, g, ea, eb, ec), registry=reg,
                engine=_engine(reg, nabla, g, fr),
            )

    def test_tm_only(self):
        from jacopy.packages.metric_affine.nonmetricity_forms import (
            nonmetricity_form,
        )

        E = algebroid("E", Bundle("E"), declare=("local",))
        with pytest.raises(ValueError):
            nonmetricity_form(e_connection(E), metric(), Frame("e", bundle=E.bundle), "a", "b")

    def test_metric_sum_push_is_capture_guarded(self, tm):
        from jacopy.packages.metric_affine.decomposition import (
            MetricIndexedSumPushDefinition,
        )

        reg, f, X, nabla, g, fr = tm
        rule = MetricIndexedSumPushDefinition()
        s = FrameIndex("s")
        node = MetricValue(g.name, IndexedSum(s, fr, fr.field("s")), fr.field("s"))
        out = rule.rewrite(node)
        # the bound index is renamed, never captured by the free e_s
        assert isinstance(out, MetricValue) and out.Y == fr.field("s")
        assert out.X != IndexedSum(s, fr, fr.field("s")) or out.X.dummy != s
        pushed = rule.rewrite(out)
        assert isinstance(pushed, IndexedSum) and pushed.dummy != s


# --------------------------------------------------------------------- #
# M4-3 — Nambu double Jacobi via the Π-twist                             #
# --------------------------------------------------------------------- #


def _nambu_setup(p=1, *, fi=True):
    from jacopy.packages.poisson.nambu import nambu_structure

    reg = PropertyRegistry()
    f, h = functions("f h", registry=reg)
    U, V, W = vector_fields("U V W")
    om, et, mu = forms("ω η μ", degree=p)
    slots = list(vector_fields(" ".join(f"Y{i}" for i in range(1, p + 1))))
    N = nambu_structure(p=p, declare=("fundamental-identity",) if fi else ())
    return reg, f, U, V, W, om, et, mu, slots, N


def test_via_twist_refuses_a_structure_without_fi():
    from jacopy.packages.drinfeld.twist import prove_nambu_double_jacobi_via_twist

    reg, f, U, V, W, om, et, mu, slots, N = _nambu_setup(fi=False)
    with pytest.raises(ValueError):
        prove_nambu_double_jacobi_via_twist(N, U, om, V, et, W, mu, f, slots, registry=reg)


def test_dorfman_jacobi_form_unchanged_by_the_shared_jacobiator():
    """``bracket_jacobiator`` refactor: the Dorfman Jacobi still closes
    and its lhs is the shared construction (citations match it)."""
    from jacopy.packages.drinfeld.double import (
        prove_dorfman_jacobi_form,
    )

    reg, f, U, V, W, om, et, mu, slots, _ = _nambu_setup()
    chain, used = prove_dorfman_jacobi_form(U, om, V, et, W, mu, f, slots, registry=reg)
    assert chain.steps and used


@SLOW
def test_nambu_double_jacobi_form_via_twist_p1():
    from jacopy.packages.drinfeld.double import _ev
    from jacopy.packages.drinfeld.twist import (
        nambu_double_jacobiator,
        prove_nambu_double_jacobi_via_twist,
    )

    reg, f, U, V, W, om, et, mu, slots, N = _nambu_setup()
    chain, used = prove_nambu_double_jacobi_via_twist(N, U, om, V, et, W, mu, f, slots, registry=reg)
    bridge, dorfman = used[0], used[1]
    assert bridge.chain_replayed and not bridge.legacy
    # the Dorfman Jacobi cites repair-loop bracket identities (V = 0 from
    # V(f) = 0): requirements-derived, not replayed — reported, not hidden
    assert not dorfman.legacy and not dorfman.chain_replayed
    cited = [s for s in chain.steps if s.rule.startswith("theorem ")]
    assert [s.rule.split()[1] for s in cited] == [bridge.name, dorfman.name]
    assert all(s.source for s in cited)
    lhs = _ev(nambu_double_jacobiator(N, (U, om), (V, et), (W, mu), component=1), slots)
    t = _replayed(lhs, Integer(0), chain, owner=N)
    assert not t.legacy and t.requirements_derived and not t.chain_replayed
    assert any(a.kind == "declared" and "FI" in a.name for a in t.requires)


@SLOW
def test_nambu_double_jacobi_bridge_honestly_fails_without_fi():
    from jacopy.packages.drinfeld.double import (
        _ev,
        bracket_jacobiator,
        dorfman_double,
    )
    from jacopy.packages.drinfeld.twist import (
        _jacobi_bridge_engine,
        nambu_double_jacobiator,
        pi_twist,
    )

    reg, f, U, V, W, om, et, mu, slots, N = _nambu_setup(fi=False)
    e = ((U, om), (V, et), (W, mu))
    pe = tuple(pi_twist(N, *x) for x in e)
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(
            _ev(nambu_double_jacobiator(N, *e, component=1), slots),
            _ev(bracket_jacobiator(dorfman_double, *pe, component=1), slots),
            registry=reg,
            engine=_jacobi_bridge_engine(N, reg),
            max_steps=400000,
        )


# --------------------------------------------------------------------- #
# FISharpPairingSwapDefinition — calculus scope (M3-1/2 family)          #
# --------------------------------------------------------------------- #


class TestFISwapScope:
    def _node(self, N, dop):
        (a, b) = forms("α β", degree=N.p)
        # repr(β) > repr(α): the canonical-order swap wants to fire
        inner = Act(Interior(N.sharp_vf(b)), a)
        return N.sharp_vf(Act(dop, inner))

    def _rule(self, N):
        from jacopy.packages.drinfeld.tilde_calculus import (
            FISharpPairingSwapDefinition,
        )

        return FISharpPairingSwapDefinition(N)

    def test_fires_under_the_cartan_tm_d(self):
        from jacopy.central.tangent.exterior import CARTAN_TM
        from jacopy.packages.poisson.nambu import nambu_structure

        N = nambu_structure(p=1, declare=("fundamental-identity",))
        assert self._rule(N).matches(self._node(N, CARTAN_TM.d))

    def test_not_under_an_algebroid_d(self):
        from jacopy.central.algebroid.calculus import algebroid_calculus
        from jacopy.packages.poisson.nambu import nambu_structure

        N = nambu_structure(p=1, declare=("fundamental-identity",))
        E = algebroid("E", Bundle("E"))
        assert not self._rule(N).matches(self._node(N, algebroid_calculus(E).d))

    def test_not_under_a_foreign_calculus_d(self):
        from jacopy.central.calculus.bracket_calculus import BracketCalculus
        from jacopy.central.tangent.lie_bracket import lie_bracket
        from jacopy.packages.poisson.nambu import nambu_structure

        N = nambu_structure(p=1, declare=("fundamental-identity",))
        foreign = BracketCalculus("Foreign-TM", anchor=lambda X: X, bracket=lie_bracket)
        assert not self._rule(N).matches(self._node(N, foreign.d))

    def test_not_under_a_non_skew_namesake(self):
        from jacopy.central.calculus.bracket_calculus import ExteriorDerivative
        from jacopy.packages.poisson.nambu import nambu_structure

        N = nambu_structure(p=1, declare=("fundamental-identity",))
        # the reserved name cannot even be spoofed by hand (central guard)
        with pytest.raises(ValueError):
            ExteriorDerivative("Cartan-TM", skew=False)
        # an ownerless look-alike under another name is refused too
        fake = ExteriorDerivative("Cartan-TM'", skew=True)
        assert not self._rule(N).matches(self._node(N, fake))

    def test_engine_leaves_the_foreign_d_alone(self):
        """In the FI-declaring tilde engine, a foreign-d node is not
        rewritten by the swap (it stays a different node from its
        Cartan counterpart)."""
        from jacopy.central.algebroid.calculus import algebroid_calculus
        from jacopy.packages.drinfeld.tilde_calculus import (
            FISharpPairingSwapDefinition,
            _tilde_engine,
        )
        from jacopy.packages.poisson.nambu import nambu_structure

        N = nambu_structure(p=1, declare=("fundamental-identity",))
        E = algebroid("E", Bundle("E"))
        node = self._node(N, algebroid_calculus(E).d)
        eng = _tilde_engine(N, PropertyRegistry())
        _, steps = eng.expand(node)
        assert not any(
            "FI consequence" in getattr(s, "rule", "") for s in steps
        )
        assert any(isinstance(r, FISharpPairingSwapDefinition) for r in eng.definitions)


# --------------------------------------------------------------------- #
# Gate 2026-10-01: derived context ↔ bridge consistency, bound guards    #
# --------------------------------------------------------------------- #


class TestDerivedContextConsistency:
    """A mismatched (derived context, bracket bridge) pair used to
    CLOSE wrong statements (R̂ = d_{E^∇}ω + ω∧ω, T = d_{E^∇̂}e + ω∧e):
    the bridge is now derived from the context itself."""

    def test_wrong_d_in_second_equation_fails_even_with_projector(self, alg):
        from jacopy.packages.metric_affine.e_cartan import (
            e_cartan_engine,
            e_cartan_second_sides,
        )

        reg, E, nabla, fr, P = alg
        lhs, rhs, derived = e_cartan_second_sides(
            E, nabla, fr, P, "a", "b", "c", "d", projected_d=False
        )
        assert derived.name.endswith("∇")
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(
                lhs, rhs, registry=reg,
                engine=e_cartan_engine(E, derived, nabla, fr, registry=reg, projector=P, decomposed=True),
            )

    def test_projected_context_needs_its_projector(self, alg):
        from jacopy.packages.metric_affine.derived import derived_algebroid
        from jacopy.packages.metric_affine.e_cartan import e_cartan_engine

        reg, E, nabla, fr, _ = alg
        with pytest.raises(ValueError):
            e_cartan_engine(E, derived_algebroid(E, projected=True), nabla, fr, registry=reg)

    def test_foreign_context_refused(self, alg):
        from jacopy.packages.metric_affine.e_cartan import e_cartan_engine

        reg, E, nabla, fr, P = alg
        other = algebroid("X", Bundle("E"))
        with pytest.raises(ValueError):
            e_cartan_engine(E, other, nabla, fr, registry=reg, projector=P)

    def test_derived_engine_refuses_mismatch(self, alg):
        from jacopy.packages.metric_affine.derived import (
            derived_algebroid,
            derived_engine,
        )

        reg, E, nabla, fr, P = alg
        with pytest.raises(ValueError):
            derived_engine(E, derived_algebroid(E), nabla, fr, registry=reg, projector=P)
        with pytest.raises(ValueError):
            derived_engine(E, derived_algebroid(E, projected=True), nabla, fr, registry=reg)


def test_component_formula_guards_the_bound_index(tm):
    from jacopy.packages.metric_affine.nonmetricity_forms import (
        nonmetricity_form_component_formula,
    )

    reg, f, X, nabla, g, fr = tm
    with pytest.raises(ValueError):
        nonmetricity_form_component_formula(nabla, g, fr, "s", "b", "c")


def test_metric_push_registered_with_decompositions():
    from jacopy.packages.metric_affine.decomposition import (
        MetricIndexedSumPushDefinition,
    )
    from jacopy.packages.metric_affine.engine import metric_affine_engine

    nabla, fr = connection(), Frame("e")
    with_dec = metric_affine_engine(decompositions=((nabla, fr),))
    plain = metric_affine_engine()
    assert any(isinstance(r, MetricIndexedSumPushDefinition) for r in with_dec.definitions)
    assert not any(isinstance(r, MetricIndexedSumPushDefinition) for r in plain.definitions)
