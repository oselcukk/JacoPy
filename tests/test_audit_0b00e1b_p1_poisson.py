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
        # a hand-built d that would COMPARE equal to the TM d (same
        # name/degree/calculus name/skew) cannot be built at all
        with pytest.raises(ValueError, match="reserved"):
            ExteriorDerivative("Cartan-TM", skew=True)
        with pytest.raises(ValueError, match="differs"):
            ExteriorDerivative("Cartan-TM", skew=True, calculus=A)
        assert not belongs_to(Act(A.d, S.omega).op, CARTAN_TM)
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

    def test_every_tm_scoped_rule_refuses_foreign_d(self):
        # root of G10: d∘d = 0, the d-wedge Leibniz and the exactness
        # test are TM statements too — a foreign skew d is not d_TM
        from jacopy.packages.poisson.nambu import (
            DSquaredZeroDefinition,
            DWedgeLeibnizDefinition,
        )
        from jacopy.packages.poisson.showcase import _is_exact

        reg = PropertyRegistry()
        (g,) = functions("g", registry=reg)
        a, b = forms("a b", degree=1)
        S, A, _, _ = _so3_plus_r()
        dd = DSquaredZeroDefinition()
        wl = DWedgeLeibnizDefinition(reg)
        assert dd.matches(Act(CARTAN_TM.d, Act(CARTAN_TM.d, g)))
        assert not dd.matches(Act(A.d, Act(A.d, g)))
        assert not dd.matches(Act(CARTAN_TM.d, Act(A.d, g)))
        assert wl.matches(Act(CARTAN_TM.d, Wedge(a, b)))
        assert not wl.matches(Act(A.d, Wedge(a, b)))
        assert _is_exact(d(g)) and not _is_exact(Act(A.d, g))

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
        # an L that would compare like the TM one cannot be built
        with pytest.raises(ValueError, match="reserved"):
            LieDerivative("Cartan-TM", x)

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


# --------------------------------------------------------------------- #
# M3-3: Koszul Jacobi — records, witness, declaration                  #
# --------------------------------------------------------------------- #


@pytest.fixture
def poisson_setup():
    from jacopy.packages.poisson import poisson_structure

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    alpha, beta, gamma = forms("α β γ", degree=1)
    (X,) = vector_fields("X")
    return reg, f, alpha, beta, gamma, X, poisson_structure()


def _jacobiator(P, a, b, c, X):
    from jacopy.packages.poisson.koszul import KoszulBracket

    pi = P.pi
    return Sum(
        Pairing(KoszulBracket(pi, a, KoszulBracket(pi, b, c)), X),
        Pairing(KoszulBracket(pi, b, KoszulBracket(pi, c, a)), X),
        Pairing(KoszulBracket(pi, c, KoszulBracket(pi, a, b)), X),
    )


class TestM33SeedRecords:
    """Fast: the seed families' zero theorems are replayed library
    chains; the defect slices depend on the declaration — and fail
    without it."""

    def test_defect_slice_needs_and_names_the_declaration(self, poisson_setup):
        from jacopy.packages.poisson.koszul_jacobi import (
            _SeedProvers,
            _rich_engine,
        )

        reg, f, a, b, c, X, P = poisson_setup
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        lhs = Pairing(c, pv.defect(a, b))  # ⟨γ, [α♯,β♯] − ♯[α,β]_π⟩
        t = pv.zero_pair_defect(c, a, b)
        assert t.lhs == lhs and t.rhs == Integer(0)
        assert t.chain_replayed and not t.legacy
        assert any("[π, π]_SN = 0" in n for n in _declared(t.requires))
        # brD / dpairD lift through the same record
        brd = pv.zero_bracket_defect(c, a, b, X)
        assert brd.chain_replayed
        assert any("[π, π]_SN = 0" in n for n in _declared(brd.requires))
        # WITHOUT the declaration the same claim does not close
        bare = _SeedProvers(P, _rich_engine(P, reg, declare=False), reg)
        with pytest.raises(ProofFailure):
            bare.zero_pair_defect(c, a, b)

    def test_bridge_and_jacobi_seeds_are_assumption_free(self, poisson_setup):
        from jacopy.central.tangent.lie_bracket import lie_bracket
        from jacopy.packages.poisson.koszul_jacobi import (
            _SeedProvers,
            _rich_engine,
        )

        reg, f, a, b, c, X, P = poisson_setup
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        V, W = pv._sharp(a), pv._sharp(b)
        sbr = pv.zero_sbr(a, b, c)
        assert sbr.lhs == Sum(
            Pairing(c, lie_bracket(V, W)),
            Neg(Act(V, pv._pp(b, c))),
            pv._pp(b, Act(CARTAN_TM.lie(V), c)),
        )
        J = Sum(
            lie_bracket(X, lie_bracket(V, W)),
            lie_bracket(V, lie_bracket(W, X)),
            lie_bracket(W, lie_bracket(X, V)),
        )
        jac = pv.zero_vf_jacobi(J)
        for t in (sbr, jac):
            assert t.chain_replayed and not t.legacy
            assert not _declared(t.requires)

    def test_vf_zero_needs_a_genuinely_generic_function(self, poisson_setup):
        # gate probe: agreement on a CONSTANT "generator" made [X,Y] = 0
        from jacopy.central.tangent.lie_bracket import lie_bracket
        from jacopy.packages.poisson.koszul_jacobi import (
            _GenericFunction,
            _SeedProvers,
            _rich_engine,
        )
        from jacopy.core.expr import Symbol
        from jacopy.core.properties import Scalar

        reg, f, a, b, c, X, P = poisson_setup
        (Y,) = vector_fields("Y")
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        with pytest.raises(ProofFailure):
            pv.zero_vf_jacobi(lie_bracket(X, Y))
        # the generic function is fresh: it avoids the names in the
        # claim and anything the registry already constrains
        reg.declare(Symbol("𝔣0"), Scalar())
        g = _GenericFunction(lie_bracket(X, Y), reg).f
        assert g != Symbol("𝔣0") and not reg.has(g, Scalar)

    def test_instance_of_keeps_the_wrapped_rule_role(self, poisson_setup):
        # the inventory lists _InstanceOf's CLASS default; each instance
        # carries the effective role of the rule it restricts
        from jacopy.central.calculus.bracket_calculus import IntrinsicLDefinition
        from jacopy.packages.poisson.core import PoissonSNDeclaration
        from jacopy.packages.poisson.koszul_jacobi import _InstanceOf
        from jacopy.proof.expansion import ExplicitAssumption, effective_role

        reg, f, a, b, c, X, P = poisson_setup
        node = Pairing(Act(CARTAN_TM.lie(X), a), X)
        for rule in (
            IntrinsicLDefinition(CARTAN_TM, reg),
            PoissonSNDeclaration(P),
            ExplicitAssumption(node, Integer(0)),
        ):
            inst = _InstanceOf(rule, node)
            assert inst.role == effective_role(rule)
            assert effective_role(inst) == effective_role(rule)

    def test_two_nf_seed_is_lazy_and_memoized(self, poisson_setup):
        from jacopy.central.objects.interior import Interior
        from jacopy.packages.poisson.core import SharpEvaluationDefinition
        from jacopy.packages.poisson.koszul_jacobi import (
            _SeedProvers,
            _rich_engine,
        )

        reg, f, a, b, c, X, P = poisson_setup
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        node = Pairing(Act(Interior(pv._sharp(c)), d(a)), pv._sharp(b))
        expr, prover = pv.zero_two_nf(
            node, ExpansionEngine([SharpEvaluationDefinition(P)])
        )
        t = prover()
        assert t is prover() and t.lhs == expr and t.chain_replayed

    def test_certificate_accepts_only_checked_library_seeds(self, poisson_setup):
        from fractions import Fraction

        from jacopy.packages.poisson.koszul_jacobi import (
            _SEED_TOKEN,
            KoszulJacobiCertificate,
            ZeroSeed,
            _SeedProvers,
            _rich_engine,
            prove_koszul_zero_by_certificate,
        )

        reg, f, a, b, c, X, P = poisson_setup
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        S = Pairing(c, pv.defect(a, b))
        # a seed cannot be minted outside the library's seed space
        with pytest.raises(TypeError):
            ZeroSeed("fake", S, S, "caller", lambda: None)
        # S + S = 0 "proved" by a theorem about another expression
        other = pv.zero_pair_defect(b, a, c)
        bad = ZeroSeed("pairD", S, S, "t", lambda: other, _token=_SEED_TOKEN)
        with pytest.raises(ProofFailure, match="not"):
            prove_koszul_zero_by_certificate(
                P, Sum(S, S), KoszulJacobiCertificate(((Fraction(2), bad),)),
                registry=reg,
            )
        # one seed, coefficient 1, expr == target: no self-citation loop
        good = ZeroSeed(
            "pairD", S, S, "t", lambda: pv.zero_pair_defect(c, a, b),
            _token=_SEED_TOKEN,
        )
        chain = prove_koszul_zero_by_certificate(
            P, S, KoszulJacobiCertificate(((Fraction(1), good),)), registry=reg
        )
        assert chain.initial == S and chain.final == Integer(0)
        r = ProofResult.from_chain(chain, Goal(S, Integer(0)))
        assert r.closed and not r.legacy
        assert any("[π, π]_SN = 0" in n for n in _declared(r.requires))
        # a wrong combination (S counted twice) does not reduce S
        with pytest.raises(ProofFailure):
            prove_koszul_zero_by_certificate(
                P, S, KoszulJacobiCertificate(((Fraction(2), good),)), registry=reg
            )

    def test_a_wrong_seed_claim_fails(self, poisson_setup):
        # ⟨c,[a♯,b♯]⟩ − a♯π(b,c) − π(b, L_{a♯}c): sign of the last term
        # flipped — not a zero; the bridge must not close it
        from jacopy.central.tangent.lie_bracket import lie_bracket
        from jacopy.packages.poisson.koszul_jacobi import (
            _InstanceOf,
            _SeedProvers,
            _rich_engine,
        )
        from jacopy.central.calculus.bracket_calculus import IntrinsicLDefinition

        reg, f, a, b, c, X, P = poisson_setup
        pv = _SeedProvers(P, _rich_engine(P, reg, declare=True), reg)
        V, W = pv._sharp(a), pv._sharp(b)
        LVc = Act(CARTAN_TM.lie(V), c)
        wrong = Sum(
            Pairing(c, lie_bracket(V, W)),
            Neg(Act(V, Pairing(c, W))),
            Neg(Pairing(LVc, W)),
        )
        eng = ExpansionEngine(
            [_InstanceOf(IntrinsicLDefinition(CARTAN_TM, reg), Pairing(LVc, W))]
        )
        with pytest.raises(ProofFailure):
            ExpandAndSimplify().prove(wrong, Integer(0), registry=reg, engine=eng)


slow = pytest.mark.skipif(
    not os.environ.get("JACOPY_RUN_SLOW"),
    reason="certificate search ~1 min; set JACOPY_RUN_SLOW=1",
)


@pytest.fixture(scope="module")
def koszul_run():
    from jacopy.packages.poisson import poisson_structure
    from jacopy.packages.poisson.koszul_jacobi import koszul_jacobi_certificate

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    alpha, beta, gamma = forms("α β γ", degree=1)
    (X,) = vector_fields("X")
    P = poisson_structure()
    jac = _jacobiator(P, alpha, beta, gamma, X)
    cert = koszul_jacobi_certificate(
        P, alpha, beta, gamma, X, f, target=jac, registry=reg
    )
    return reg, P, (alpha, beta, gamma, X, f), jac, cert


@slow
class TestM33KoszulChain:
    def test_chain_proves_the_jacobiator_and_replays(self, koszul_run):
        from jacopy.packages.poisson.koszul_jacobi import (
            prove_koszul_zero_by_certificate,
        )

        reg, P, _, jac, cert = koszul_run
        chain = prove_koszul_zero_by_certificate(P, jac, cert, registry=reg)
        assert chain_shape(jac, Integer(0), chain).ok
        r = ProofResult.from_chain(chain, Goal(jac, Integer(0)))
        assert r.closed and not r.legacy
        assert any("[π, π]_SN = 0" in n for n in _declared(r.requires))
        t = Theorem("koszul_jacobi_general", "Jac_π(α,β,γ;X) = 0", jac, Integer(0), chain).with_structural_requires()
        assert t.chain_replayed and not t.legacy
        # the witness: the first step rewrites Jac to Σ c_i S_i, the
        # certificate's combination, as a cited replayed reduction
        first = chain.steps[0]
        assert first.before == jac and first.after == cert.combination()
        assert first.cites is not None and first.cites.chain_replayed
        # every seed is a record with its own replayed zero theorem
        assert cert.terms
        for c, seed in cert.terms:
            assert c != 0 and seed.theorem.lhs == seed.expr
            assert seed.theorem.chain_replayed and seed.origin

    def test_public_prover_returns_the_same_shape(self, koszul_run):
        from jacopy.packages.poisson.koszul_jacobi import (
            prove_general_koszul_jacobi,
        )

        reg, P, (a, b, c, X, f), jac, _ = koszul_run
        chain = prove_general_koszul_jacobi(P, a, b, c, X, f, registry=reg)
        assert chain.initial == jac and chain.final == Integer(0)

    def test_wrong_target_or_tampered_certificate_fails(self, koszul_run):
        from jacopy.packages.poisson.koszul import KoszulBracket
        from jacopy.packages.poisson.koszul_jacobi import (
            KoszulJacobiCertificate,
            prove_koszul_zero_by_certificate,
        )

        reg, P, (a, b, c, X, f), jac, cert = koszul_run
        wrong = Sum(jac, Pairing(KoszulBracket(P.pi, a, b), X))
        with pytest.raises(ProofFailure):
            prove_koszul_zero_by_certificate(P, wrong, cert, registry=reg)
        tampered = KoszulJacobiCertificate(cert.terms[1:])
        with pytest.raises(ProofFailure):
            prove_koszul_zero_by_certificate(P, jac, tampered, registry=reg)
