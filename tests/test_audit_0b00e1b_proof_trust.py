"""Audit 0b00e1b-FULL — proof trust (guideline 15e: re-using proven
results is only as good as the cited record).

* P0-3 ≡ M1X-2 (with K2-16): registry declarations are requirements of
  a proof; a citation is checked against the citing registry.
* M1-5 ≡ M1-6 ≡ K2-7 ≡ M1X-4: a theorem record is judged by what its
  chain establishes (replay of connectivity + endpoints; hand-built,
  untagged, keyless steps are not evidence); ``from_chain`` refuses a
  disconnected chain and a CLOSED status the chain does not carry.

Every acceptance test builds its target equation here.
"""

import pytest

from jacopy.algebra.derivation import Act, Derivation
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.core.expr import Integer, Neg, Product, Sum, Symbol
from jacopy.core.multi_eval import MultiEval
from jacopy.core.properties import Graded, Scalar
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import ExpansionEngine, ExplicitAssumption
from jacopy.proof.registry_facts import registry_context
from jacopy.proof.replay import chain_shape
from jacopy.proof.result import Goal, ProofResult, prove
from jacopy.proof.step import ProofStep
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.proof.theorems import (
    LegacyTheoremError,
    Theorem,
    TheoremBook,
    TheoremDefinition,
    check_citation,
    cite,
)


# --------------------------------------------------------------------- #
# P0-3 ≡ M1X-2: registry declarations as requirements                    #
# --------------------------------------------------------------------- #


def _scalar_world():
    D, x = Derivation("D", 0), Symbol("x")
    src = PropertyRegistry()
    src.declare(x, Scalar())
    tgt = PropertyRegistry()
    tgt.declare(x, Graded(0))                     # x an ordinary (even) function, NOT Scalar
    lhs, rhs = Product(D, x), Product(x, D)       # D∘x = x∘D
    return D, x, src, tgt, lhs, rhs


def _scalar_theorem():
    D, x, src, tgt, lhs, rhs = _scalar_world()
    r0 = prove(ExpansionEngine(), lhs, rhs, registry=src)
    assert r0.closed
    thm = Theorem("scalar_comm", "D x = x D", lhs, rhs, r0.chain).with_structural_requires()
    return thm, src, tgt, lhs, rhs, r0


class TestRegistryRequirements:
    def test_scalar_declaration_is_a_requirement_not_assumption_free(self):
        thm, src, tgt, lhs, rhs, r0 = _scalar_theorem()
        # K2-16: the closure depends on "x is Scalar" — it is not assumption-free
        assert "assumption-free" not in r0.summary()
        assert any(a.kind == "registry" and "Scalar" in a.name and "x" in a.name for a in r0.requires)
        assert any(f.declared and f.prop_cls is Scalar for f in thm.registry_facts)
        assert not thm.legacy and thm.chain_replayed

    def test_citation_in_a_registry_without_the_declaration_is_refused(self):
        thm, src, tgt, lhs, rhs, _ = _scalar_theorem()
        assert prove(ExpansionEngine(), lhs, rhs, registry=tgt).status == "RESIDUAL"   # baseline
        eng = ExpansionEngine([TheoremDefinition(thm)])
        chk = check_citation(thm, eng, registry=tgt)
        assert not chk.ok and any("registry declaration missing" in r and "Scalar" in r for r in chk.reasons)
        cited = prove(eng, lhs, rhs, registry=tgt)
        assert cited.status == "RESIDUAL"                                               # was CLOSED (P0-3)
        assert not cited.theorems_cited
        # foundational mode too
        assert prove(eng.with_mode("foundational"), lhs, rhs, registry=tgt).status == "RESIDUAL"

    def test_unknown_citing_registry_is_refused(self):
        thm, *_ = _scalar_theorem()
        chk = check_citation(thm, ExpansionEngine())
        assert not chk.ok and any("citing registry is unknown" in r for r in chk.reasons)

    def test_citation_in_the_same_registry_still_works(self):
        thm, src, tgt, lhs, rhs, _ = _scalar_theorem()
        eng = ExpansionEngine([TheoremDefinition(thm)])
        assert check_citation(thm, eng, registry=src).ok
        res = prove(eng, lhs, rhs, registry=src)
        assert res.closed and res.theorems_cited
        assert any(a.kind == "registry" and "Scalar" in a.name for a in res.requires)
        # an equivalent registry (same answers, another object) is fine too
        other = PropertyRegistry()
        other.declare(Symbol("x"), Scalar())
        assert prove(eng, lhs, rhs, registry=other).closed

    def test_graded_parity_mismatch_is_refused(self):
        p, q = Symbol("p"), Symbol("q")
        even, odd = PropertyRegistry(), PropertyRegistry()
        for s in (p, q):
            even.declare(s, Graded(0))
            odd.declare(s, Graded(1))
        L, R = Product(p, q), Product(q, p)
        r1 = prove(ExpansionEngine(), L, R, registry=even)
        assert r1.closed
        thm = Theorem("pq", "pq = qp", L, R, r1.chain).with_structural_requires()
        eng = ExpansionEngine([TheoremDefinition(thm)])
        assert prove(eng, L, Neg(R), registry=odd).closed                # pq = −qp for odd p, q
        assert prove(eng, L, R, registry=odd).status == "RESIDUAL"        # was CLOSED: 2pq = 0
        assert prove(eng, L, R, registry=even).closed

    def test_registry_requirements_are_transitive(self):
        thm, src, tgt, lhs, rhs, _ = _scalar_theorem()
        eng = ExpansionEngine([TheoremDefinition(thm)])
        res = prove(eng, lhs, rhs, registry=src)
        thm_b = Theorem("via_scalar_comm", "D x = x D (cited)", lhs, rhs, res.chain).with_structural_requires()
        assert any(f.prop_cls is Scalar and f.declared for f in thm_b.registry_facts)
        eng_b = ExpansionEngine([TheoremDefinition(thm_b)])
        assert prove(eng_b, lhs, rhs, registry=tgt).status == "RESIDUAL"
        assert prove(eng_b, lhs, rhs, registry=src).closed

    def test_engine_expand_needs_a_known_context(self):
        thm, src, tgt, lhs, rhs, _ = _scalar_theorem()
        eng = ExpansionEngine([TheoremDefinition(thm)])
        assert eng.expand(lhs)[0] == lhs                                 # unknown context: inert
        with registry_context(src):
            assert eng.expand(lhs)[0] == rhs
        with registry_context(tgt):
            assert eng.expand(lhs)[0] == lhs


# --------------------------------------------------------------------- #
# M1-5 ≡ M1-6 ≡ K2-7 ≡ M1X-4: what the chain establishes                 #
# --------------------------------------------------------------------- #


class TestChainReplay:
    def test_empty_chain_one_equals_zero_is_not_a_theorem(self):
        t = Theorem("one_zero", "1 = 0", Integer(1), Integer(0), ProofChain()).with_structural_requires()
        assert t.legacy and not t.chain_replayed
        with pytest.raises(LegacyTheoremError):
            TheoremBook().add(t)

    @pytest.mark.parametrize("tag", [None, "theorem", "axiom"])
    def test_hand_built_trust_me_step_is_legacy(self, tag):
        x = Symbol("x")
        kw = {"provenance_tag": tag} if tag else {}
        step = ProofStep(x, Integer(0), rule="trust me", justification="hand-built leap", **kw)
        t = Theorem(f"x_zero_{tag}", "x = 0", x, Integer(0), ProofChain([step])).with_structural_requires()
        assert t.legacy
        with pytest.raises(LegacyTheoremError):
            TheoremBook().add(t)

    def test_disconnected_chain_is_not_a_theorem(self):
        p, q, r = Symbol("p"), Symbol("q"), Symbol("r")
        steps = [ProofStep(r, q, rule="lemma A (made up)"), ProofStep(Integer(7), Integer(7), rule="reflexivity")]
        t = Theorem("pq_is_five", "p q = 5", Product(p, q), Integer(5), ProofChain(steps)).with_structural_requires()
        assert t.legacy
        with pytest.raises(LegacyTheoremError):
            TheoremBook().add(t)
        assert not chain_shape(Product(p, q), Integer(5), steps).ok

    def test_disconnected_keyed_chain_is_requirements_derived_only(self):
        # a keyed (machine-looking) step that has nothing to do with the claim
        p, q, a, b = (Symbol(n) for n in "pqab")
        steps = [ProofStep(a, b, rule="simplify", key=("pass", "simplify"))]
        t = Theorem("pq_ab", "p = q", p, q, ProofChain(steps)).with_structural_requires()
        assert not t.legacy and t.requirements_derived and not t.chain_replayed
        book = TheoremBook()
        book.add(t)                                           # accepted as requirements-derived …
        assert book.is_requirements_derived("pq_ab") and not book.is_chain_replayed("pq_ab")
        with pytest.raises(LegacyTheoremError):
            cite(ExpansionEngine(), book, "pq_ab")            # … but never cited silently
        eng = cite(ExpansionEngine(), book, "pq_ab", allow_legacy=True)
        res = prove(eng, p, q)
        assert res.closed and any(a.kind == "unreplayed" for a in res.requires)
        assert "assumption-free" not in res.summary()

    def test_prove_and_expand_and_simplify_transcripts_replay(self):
        reg = PropertyRegistry()
        p, q = Symbol("p"), Symbol("q")
        for s in (p, q):
            reg.declare(s, Graded(0))
        L, R = Product(p, q), Product(q, p)
        r = prove(ExpansionEngine(), L, R, registry=reg)
        assert chain_shape(L, R, r.chain).form == "lhs→rhs"
        chain = ExpandAndSimplify().prove(L, R, registry=reg, engine=ExpansionEngine())
        assert chain_shape(L, R, chain).form == "lhs−rhs→0"
        t = Theorem("pq_eas", "pq = qp", L, R, chain).with_structural_requires()
        assert t.chain_replayed

    def test_local_engine_steps_replay(self):
        a, b, c = Symbol("a"), Symbol("b"), Symbol("c")
        eng = ExpansionEngine([ExplicitAssumption(a, b), ExplicitAssumption(b, c)])
        expr = Sum(Product(a, c), a)
        out, steps = eng.expand(expr)
        assert out == Sum(Product(c, c), c)
        assert all(s.before in (a, b) for s in steps)                      # local steps
        assert chain_shape(expr, out, steps).ok
        t = Theorem("abc", "ac + a = cc + c", expr, out, ProofChain(steps)).with_structural_requires()
        assert t.chain_replayed and len([r for r in t.requires if r.kind == "declared"]) == 2

    def test_requires_verified_cannot_be_set_by_hand(self):
        x = Symbol("x")
        with pytest.raises(ValueError, match="not what the chain yields"):
            Theorem("fake", "x = 0", x, Integer(0), ProofChain(), requires_verified=True)

    def test_from_chain_refuses_disconnected_and_overridden_status(self):
        X, Y, Z = Symbol("X"), Symbol("Y"), Symbol("Z")
        s = ProofStep(X, Y, rule="r", key=("pass", "r"))
        with pytest.raises(ValueError, match="CLOSED"):
            ProofResult.from_chain(ProofChain([s]), Goal(X, Z), status="CLOSED")
        with pytest.raises(ValueError, match="not connected"):
            ProofResult.from_chain(ProofChain([s, ProofStep(Z, X, rule="r2", key=("pass", "r2"))]), Goal(X, X))
        with pytest.raises(ValueError, match="status"):
            ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="INVALID")
        ok = ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="CLOSED")
        assert ok.closed and ok.requires == ()
        assert ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="RESIDUAL").status == "RESIDUAL"

    def test_from_theorem_reports_the_chain_verdict(self):
        p, q, a, b = (Symbol(n) for n in "pqab")
        t = Theorem("pq_ab", "p = q", p, q, ProofChain([ProofStep(a, b, rule="s", key=("pass", "s"))])).with_structural_requires()
        res = ProofResult.from_theorem(t)
        assert any(r.kind == "unreplayed" for r in res.requires)


# --------------------------------------------------------------------- #
# library records: requirements-derived, transitive, oracle-checked      #
# --------------------------------------------------------------------- #


def test_library_citation_keeps_transitive_requirements_under_the_oracle():
    """A library record (narrative chain) is cited explicitly; the citing
    result carries the cited record's requirements — the declared
    Poisson structure and the 'unreplayed' marker — and the model oracle
    (strict) finds no DISAGREE and no ASSUMPTION_LEAK on it."""
    from jacopy.central.objects import functions
    from jacopy.oracle.hook import REPORTS, oracle_mode
    from jacopy.packages.poisson.core import poisson_structure
    from jacopy.packages.poisson.showcase import prove_hamiltonian_morphism, prove_poisson_jacobi, showcase_engine

    reg = PropertyRegistry()
    f, g, h = functions("f g h", registry=reg)
    P = poisson_structure()
    _, thm = prove_poisson_jacobi(P, f, g, h, registry=reg)
    assert thm.requirements_derived and not thm.chain_replayed
    book = TheoremBook()
    book.add(thm)
    with pytest.raises(LegacyTheoremError):
        cite(showcase_engine(P, registry=reg), book, thm.name)       # never silently
    lhs = Act(P.hamiltonian(P.bracket(f, g)), h)
    rhs = Act(LieBracketVF(P.hamiltonian(f), P.hamiltonian(g)), h)
    REPORTS.clear()
    with oracle_mode("strict"):                    # raises on DISAGREE / ASSUMPTION_LEAK
        chain = prove_hamiltonian_morphism(P, f, g, h, registry=reg)
        t = Theorem("ham_morphism", "X_{f,g} h = [X_f, X_g] h", lhs, rhs, chain).with_structural_requires()
        res = ProofResult.from_theorem(t, registry=reg, owners=showcase_engine(P, registry=reg).owners)
    assert res.closed and res.theorems_cited
    assert t.chain_replayed is False                                                   # inherits the marker
    assert any(a.kind == "unreplayed" and "poisson_jacobi" in a.name for a in res.requires)
    assert any(a.kind == "declared" and "Poisson" in a.name for a in res.requires)     # transitive axiom
    assert REPORTS and not any(r.refutes for r in REPORTS)
