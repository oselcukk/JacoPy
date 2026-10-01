"""Audit 0b00e1b-FULL — proof trust (guideline 15e: re-using proven
results is only as good as the cited record).

* P0-3 ≡ M1X-2 (with K2-16): registry declarations are requirements of
  a proof; a citation is checked against the citing registry.
* M1-5 ≡ M1-6 ≡ K2-7 ≡ M1X-4: a theorem record is judged by what its
  chain establishes (replay of connectivity + endpoints; hand-built,
  untagged, keyless steps are not evidence); ``from_chain`` refuses a
  disconnected chain and a CLOSED status the chain does not carry.
* M1X-3 (with K2-13, M1-8): a modulo citation records the modulo
  engine's steps, so its explicit assumptions reach the citing result.

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
        # a GENUINE engine step that has nothing to do with the claim
        p, q, a, b = (Symbol(n) for n in "pqab")
        hyp = ExplicitAssumption(a, b)
        _, steps = ExpansionEngine([hyp]).expand(a)
        t = Theorem("pq_ab", "p = q", p, q, ProofChain(steps)).with_structural_requires()
        assert not t.legacy and t.requirements_derived and not t.chain_replayed
        book = TheoremBook()
        book.add(t)                                           # accepted as requirements-derived …
        assert book.is_requirements_derived("pq_ab") and not book.is_chain_replayed("pq_ab")
        with pytest.raises(LegacyTheoremError):
            cite(ExpansionEngine([hyp]), book, "pq_ab")       # … but never cited silently
        eng = cite(ExpansionEngine([hyp]), book, "pq_ab", allow_legacy=True)
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
        (s,) = ExpansionEngine([ExplicitAssumption(X, Y)]).expand(X)[1]          # a genuine engine step
        with pytest.raises(ValueError, match="CLOSED"):
            ProofResult.from_chain(ProofChain([s]), Goal(X, Z), status="CLOSED")
        with pytest.raises(ValueError, match="not connected"):
            ProofResult.from_chain(ProofChain([s, ProofStep(Z, X, rule="r2", key=("pass", "r2"))]), Goal(X, X))
        with pytest.raises(ValueError, match="status"):
            ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="INVALID")
        ok = ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="CLOSED")
        assert ok.closed and not ok.legacy and [a.name for a in ok.declared] == ["explicit assumption: X = Y"]
        assert ProofResult.from_chain(ProofChain([s]), Goal(X, Y), status="RESIDUAL").status == "RESIDUAL"

    def test_from_theorem_reports_the_chain_verdict(self):
        p, q, a, b = (Symbol(n) for n in "pqab")
        _, steps = ExpansionEngine([ExplicitAssumption(a, b)]).expand(a)
        t = Theorem("pq_ab", "p = q", p, q, ProofChain(steps)).with_structural_requires()
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


# --------------------------------------------------------------------- #
# M1X-3: modulo citations record the modulo engine's assumptions         #
# --------------------------------------------------------------------- #


class TestModuloRecordsAssumptions:
    def _ysub(self):
        y = Symbol("y")
        r = prove(ExpansionEngine(), Sum(y, Neg(y)), Integer(0))
        return Theorem("ysub", "y - y = 0", Sum(y, Neg(y)), Integer(0), r.chain).with_structural_requires()

    def test_explicit_assumptions_of_the_modulo_engine_reach_the_result(self):
        t = self._ysub()
        assert t.requires == ()
        b, c = Symbol("b"), Symbol("c")
        modeng = ExpansionEngine([ExplicitAssumption(b), ExplicitAssumption(c)])
        outer = ExpansionEngine([TheoremDefinition(t, modulo=modeng)])
        assert prove(ExpansionEngine(), Sum(b, c), Integer(0)).status == "RESIDUAL"
        res = prove(outer, Sum(b, c), Integer(0))
        assert res.closed
        names = {a.name for a in res.declared}
        assert "explicit assumption: b = 0" in names and "explicit assumption: c = 0" in names
        assert "assumption-free" not in res.summary()

    def test_modulo_laundering_of_p_equals_minus_q(self):
        t = self._ysub()
        P, Q = Symbol("P"), Symbol("Q")
        outer = ExpansionEngine([TheoremDefinition(t, modulo=ExpansionEngine([ExplicitAssumption(P, Neg(Q))]))])
        res = prove(outer, Sum(P, Q), Integer(0))
        assert res.closed and any("P = (-Q)" in a.name for a in res.declared)
        thm = Theorem("pq0", "P + Q = 0", Sum(P, Q), Integer(0), res.chain).with_structural_requires()
        assert any(a.kind == "declared" and "P = (-Q)" in a.name for a in thm.requires)


# --------------------------------------------------------------------- #
# code-review probes (2026-10-01, high) — each closed wrongly on this    #
# branch's earlier commits (8b498a2 and before)                         #
# --------------------------------------------------------------------- #


class TestReviewProbes:
    def _modulo_engine(self):
        y = Symbol("y")
        r = prove(ExpansionEngine(), Sum(y, Neg(y)), Integer(0))
        t = Theorem("ysub", "y - y = 0", Sum(y, Neg(y)), Integer(0), r.chain).with_structural_requires()
        b, c = Symbol("b"), Symbol("c")
        return b, c, ExpansionEngine([TheoremDefinition(t, modulo=ExpansionEngine([ExplicitAssumption(b), ExplicitAssumption(c)]))])

    @pytest.mark.parametrize("shape", ["product", "neg"])
    def test_modulo_citation_at_a_subterm_keeps_its_assumptions(self, shape):
        # 8b498a2: prove(outer, z·(b+c), 0) closed "assumption-free" with
        # requires == () and the record was chain_replayed / citable
        b, c, outer = self._modulo_engine()
        z = Symbol("z")
        goal = Product(z, Sum(b, c)) if shape == "product" else Neg(Sum(b, c))
        res = prove(outer, goal, Integer(0))
        assert res.closed
        names = {a.name for a in res.declared}
        assert {"explicit assumption: b = 0", "explicit assumption: c = 0"} <= names
        assert "assumption-free" not in res.summary()
        thm = Theorem("sub", "z(b+c) = 0", goal, Integer(0), res.chain).with_structural_requires()
        assert {"explicit assumption: b = 0", "explicit assumption: c = 0"} <= {a.name for a in thm.requires if a.kind == "declared"}
        assert not check_citation(thm, ExpansionEngine(), registry=None).ok   # the assumptions are not registered there

    def test_unreadable_registry_record_is_not_dropped(self):
        # 8b498a2: _classify deleted a registry record it could not parse
        from jacopy.proof.result import Assumption, _classify

        x = Symbol("x")
        fake = Theorem("lemma", "x = x", x, x, ProofChain())
        object.__setattr__(fake, "requires", (Assumption("registry", "registry declaration: something", key=None),))
        object.__setattr__(fake, "requires_verified", True)
        cite_step = ProofStep(x, x, rule="cite lemma", provenance_tag="theorem", cites=fake)
        req, _ = _classify((cite_step,))
        assert any(a.legacy and "unverifiable registry requirement" in a.name for a in req)

    def test_forged_registry_record_cannot_keep_requires_verified(self):
        # 047ddc8: the forgery check compared only (kind, name) — a registry
        # record with key=None kept requires_verified, registry_facts == ()
        # and the Scalar theorem was citable where x is not Scalar (P0-3 back)
        import dataclasses

        from jacopy.proof.result import Assumption

        thm, src, tgt, lhs, rhs, _ = _scalar_theorem()
        forged = tuple(
            Assumption(a.kind, a.name, a.owner, a.instances, a.example, None) if a.kind == "registry" else a
            for a in thm.requires
        )
        with pytest.raises(ValueError, match="not what the chain yields"):
            dataclasses.replace(thm, requires=forged)
        with pytest.raises(ValueError, match="not what the chain yields"):
            dataclasses.replace(thm, requires=tuple(a for a in thm.requires if a.kind != "registry"))
        with pytest.raises(ValueError, match="not what the chain yields"):
            Theorem("x", "D x = x D", lhs, rhs, thm.proof, requires=forged, requires_verified=True)

    def test_with_structural_requires_derives_once(self, monkeypatch):
        import jacopy.proof.result as R

        calls = []
        orig = R.structural_requires
        monkeypatch.setattr(R, "structural_requires", lambda t: calls.append(1) or orig(t))
        _scalar_theorem()
        assert len(calls) == 1

    @pytest.mark.parametrize("forge", [{"key": ("pass", "simplify")}, {"provenance_tag": "computation"},
                                       {"key": ("strategy", "agreement-on-generators")}])
    def test_caller_supplied_tag_or_key_is_not_provenance(self, forge):
        # 5600f83: ProofStep(x, 0, key=("pass", "simplify")) (or tag
        # "computation") was accountable: chain_replayed, citable, and
        # x = 0 closed "assumption-free"
        x = Symbol("x")
        step = ProofStep(x, Integer(0), rule="simplify", **forge)
        t = Theorem("x_zero", "x = 0", x, Integer(0), ProofChain([step])).with_structural_requires()
        assert t.legacy and not t.chain_replayed
        with pytest.raises(LegacyTheoremError):
            TheoremBook().add(t)
        assert not TheoremDefinition(t).citable
        res = ProofResult.from_chain(ProofChain([step]), Goal(x, Integer(0)))
        assert any(a.legacy and "hand-built" in a.name for a in res.requires)
        assert "assumption-free" not in res.summary()

    def test_forged_step_spliced_into_a_genuine_chain(self):
        # a genuine engine step followed by a forged keyed step
        a, b = Symbol("a"), Symbol("b")
        hyp = ExplicitAssumption(a, b)
        (good,) = ExpansionEngine([hyp]).expand(a)[1]
        bad = ProofStep(b, Integer(0), rule="simplify", key=("pass", "simplify"))
        t = Theorem("a_zero", "a = 0", a, Integer(0), ProofChain([good, bad])).with_structural_requires()
        assert not t.chain_replayed and any("hand-built" in r for r in t.unreplayed_reasons())

    def test_user_pass_callable_is_not_a_library_pass(self):
        # 5600f83: normalize(passes=(user_fn,)) stamped the step ("pass", name)
        from jacopy.proof.normalize import normalize
        from jacopy.proof.replay import accountable

        x = Symbol("x")

        def simplify(expr, registry):  # same NAME as the library pass
            return Integer(0)

        nf = normalize(ExpansionEngine(), x, passes=(simplify,), record=True)
        (step,) = nf.chain
        assert step.key is None and not accountable(step)
        t = Theorem("x0", "x = 0", x, Integer(0), ProofChain(nf.chain)).with_structural_requires()
        assert t.legacy
        lib = normalize(ExpansionEngine(), Sum(x, Neg(x)), passes=("simplify",), record=True)
        assert all(accountable(s) for s in lib.chain) and lib.chain[0].key == ("pass", "simplify")

    def test_modulo_match_is_normalized_once_per_firing(self):
        # 967f8f3: the engine re-ran matches under the read recorder, so a
        # modulo match (a full normalization) ran twice per firing
        y = Symbol("y")
        r = prove(ExpansionEngine(), Sum(y, Neg(y)), Integer(0))
        t = Theorem("ysub", "y - y = 0", Sum(y, Neg(y)), Integer(0), r.chain).with_structural_requires()
        b, c = Symbol("b"), Symbol("c")
        calls = []

        class Counting(ExpansionEngine):
            __slots__ = ()

            def expand(self, expr, **kw):
                calls.append(expr)
                return super().expand(expr, **kw)

        modeng = Counting([ExplicitAssumption(b), ExplicitAssumption(c)])
        outer = ExpansionEngine([TheoremDefinition(t, modulo=modeng)])
        _, step = outer.expand_once(Sum(b, c))
        assert step is not None and len(calls) == 2      # one normalization: 2 rounds (change, fix-point)
        calls.clear()
        from jacopy.proof.search import _definition_moves

        moves = _definition_moves(outer, Sum(b, c))
        assert moves and len(calls) == 2

    def test_cited_textual_requirements_flow_to_the_citing_proof(self):
        # 4b1cff9: _classify passed only declared/legacy/scope/registry/
        # unreplayed of a cited record — its "textual" from_axioms entries
        # (and everything of a legacy record) were dropped
        y = Symbol("y")
        r = prove(ExpansionEngine(), Sum(y, Neg(y)), Integer(0))
        t = Theorem("ysub", "y - y = 0", Sum(y, Neg(y)), Integer(0), r.chain,
                    from_axioms=("exactness ρ∘χ = 0 (8.5)",)).with_structural_requires()
        assert [a.kind for a in t.requires] == ["textual"]
        res = prove(ExpansionEngine([TheoremDefinition(t)]), Sum(y, Neg(y)), Integer(0))
        assert res.closed and res.theorems_cited
        assert any(a.kind == "textual" and "exactness" in a.name for a in res.requires)

    def test_lemma_91_textual_requirements_reach_the_citation(self):
        from jacopy.central.objects import functions
        from jacopy.packages.generalized.bourbaki_exact import exact_bourbaki_context, prove_lemma_91
        from jacopy.packages.generalized.bourbaki_precalculus import BourbakiPreCalculus

        reg = PropertyRegistry()
        (h,) = functions("h", registry=reg)
        E = exact_bourbaki_context()
        (z,) = BourbakiPreCalculus().z_sections("z")
        (u,) = E.sections("u")
        _, thm = prove_lemma_91(E, u, z, h, registry=reg)
        assert any(a.kind == "textual" and "exactness" in a.name for a in thm.requires)
        res = prove(ExpansionEngine([TheoremDefinition(thm, allow_legacy=True)]), thm.lhs, thm.rhs, registry=reg)
        assert res.closed and res.theorems_cited
        assert any(a.kind == "textual" and "exactness ρ∘χ = 0 (8.5)" in a.name for a in res.requires)
        assert any(a.legacy and "unverified citation" in a.name for a in res.requires)


class TestReviewRound3:
    def test_transfer_keeps_an_underived_records_requirements(self):
        # 4435c08: OwnerScope.transfer set requires=() on a record whose
        # requires were never derived — its explicit requirements vanished
        from jacopy.central.algebroid import algebroid
        from jacopy.central.objects import Bundle
        from jacopy.proof.ownership import OwnerScope
        from jacopy.proof.result import Assumption

        E1 = algebroid("E", Bundle("E"), declare=("lie",))
        E3 = E1.with_declarations("metric-invariance")
        x = Symbol("x")
        req = (Assumption("textual", "from_axioms: something", E1), Assumption("legacy", "hand claim"))
        thm = Theorem("t", "x = 0", x, Integer(0), ProofChain(), owner=E1, requires=req)
        moved = OwnerScope().transfer(thm, E3)
        assert [a.name for a in moved.requires] == ["from_axioms: something", "hand claim"]
        assert moved.requires[0].owner is E3 and not moved.requires_verified

    def test_user_definition_class_is_an_assumption(self):
        # 15e6032: class Bogus(Definition) rewriting y → 0 inherited role
        # "definition": prove CLOSED "assumption-free", record chain_replayed
        from jacopy.proof.expansion import Definition, effective_role

        y = Symbol("y")

        class Bogus(Definition):
            name = "bogus: y = 0"

            def matches(self, expr):
                return expr == y

            def rewrite(self, expr):
                return Integer(0)

        assert effective_role(Bogus()) == "assumption"
        res = prove(ExpansionEngine([Bogus()]), y, Integer(0))
        assert res.closed and "assumption-free" not in res.summary()
        assert [a.name for a in res.declared] == ["bogus: y = 0"]
        thm = Theorem("bogus", "y = 0", y, Integer(0), res.chain).with_structural_requires()
        assert not check_citation(thm, ExpansionEngine(), registry=None).ok
        assert check_citation(thm, ExpansionEngine([Bogus()]), registry=None).ok

    def test_cited_structure_requirements_flow(self):
        # 4ba1c20: inherit() dropped the cited record's "structure"
        # requirements (regenerating only those of declared owners)
        from jacopy.central.algebroid import algebroid
        from jacopy.central.objects import Bundle
        from jacopy.proof.result import Assumption, _classify

        E = algebroid("E", Bundle("E"), declare=("lie",))
        x = Symbol("x")
        lemma = Theorem("lemma", "x = x", x, x, ProofChain())
        object.__setattr__(lemma, "requires", (Assumption("structure", "E declaring ['lie']", E),))
        object.__setattr__(lemma, "requires_verified", True)
        step = ProofStep(x, x, rule="cite lemma", provenance_tag="theorem", cites=lemma)
        req, _ = _classify((step,))
        assert [a for a in req if a.kind == "structure" and a.owner is E]

    def test_search_move_at_a_later_occurrence_is_minted(self):
        # cb078f8: _whole_step minted by first-occurrence replay, so the
        # search's (correct) rewrite of the SECOND a in a·a was unminted
        from jacopy.proof.search import _definition_moves
        from jacopy.proof.step import is_minted

        a, b = Symbol("a"), Symbol("b")
        moves = _definition_moves(ExpansionEngine([ExplicitAssumption(a, b)]), Product(a, a))
        assert {m[0] for m in moves} == {Product(b, a), Product(a, b)}
        assert all(is_minted(step) for _, step in moves)

    def test_end_reads_removes_by_identity(self):
        # 40ce6c7: end_reads used stack.remove(log) — by VALUE: with
        # mismatched nesting an equal (empty) outer log was removed
        from jacopy.core.registry import _READS, begin_reads, end_reads

        base = begin_reads()
        outer = begin_reads()
        inner = begin_reads()
        try:
            end_reads(outer)                       # out of order; base == outer == [] by value
            assert any(l is base for l in _READS.stack)
            assert _READS.stack[-1] is inner and all(l is not outer for l in _READS.stack)
        finally:
            end_reads(inner)
            end_reads(base)
        assert not any(l is inner or l is outer or l is base for l in _READS.stack)

    def test_inner_engine_reads_reach_the_enclosing_decision(self):
        # main 75acc5a: only the FIRED inner candidate's reads reached the
        # enclosing log, so an outer rule whose decision depends on an inner
        # rule NOT firing (x not Scalar) recorded no registry fact: the
        # theorem a = b proved where x is Graded(0) was cited CLOSED where
        # x is Scalar (there Outer itself does not fire)
        from jacopy.proof.expansion import Definition
        from jacopy.proof.registry_facts import current_context

        a, b, c, x = Symbol("a"), Symbol("b"), Symbol("c"), Symbol("x")

        class GuardIfScalar(Definition):   # fires (a → c) only when x is Scalar
            name = "guard"

            def matches(self, expr):
                return expr == a and current_context()[0].get(x, Scalar) is not None

            def rewrite(self, expr):
                return c

        inner = ExpansionEngine([GuardIfScalar(), ExplicitAssumption(b, c)])

        class Outer(Definition):
            name = "outer: a = b when a is inner-normal"

            def matches(self, expr):
                return expr == a and inner.expand(expr)[0] == a

            def rewrite(self, expr):
                return b

        R1, R2 = PropertyRegistry(), PropertyRegistry()
        R1.declare(x, Graded(0))
        R2.declare(x, Scalar())
        res = prove(ExpansionEngine([Outer()]), a, b, registry=R1)
        assert res.closed
        thm = Theorem("t", "a = b", a, b, res.chain).with_structural_requires()
        assert any(f.expr == x and f.prop_cls is Scalar and not f.declared for f in thm.registry_facts)
        assert not check_citation(thm, ExpansionEngine([Outer()]), registry=R2).ok
        assert prove(ExpansionEngine([Outer(), TheoremDefinition(thm)]), a, b, registry=R2).status == "RESIDUAL"
        # a fired inner step's OWN facts are its rule's slice only
        with registry_context(R1):
            _, (st,) = ExpansionEngine([GuardIfScalar(), ExplicitAssumption(b, c)]).expand(b)
        assert not any(f.expr == x for f in st.registry_facts)

    def test_subclasses_cannot_impersonate_minted_steps_or_theorems(self):
        # 2270a83: is_minted used WeakSet membership (__eq__/__hash__), and
        # TheoremBook / TheoremDefinition / _classify accepted Theorem
        # subclasses whose verdict properties can be overridden
        from jacopy.proof.result import _classify
        from jacopy.proof.step import is_minted

        a, b = Symbol("a"), Symbol("b")
        (real,) = ExpansionEngine([ExplicitAssumption(a, b)]).expand(a)[1]
        assert is_minted(real)

        class Twin(ProofStep):
            __slots__ = ()

            def __eq__(self, other):
                return True

            def __hash__(self):
                return hash(real)

        assert not is_minted(Twin(a, Integer(0), rule="r"))

        class Liar(Theorem):
            @property
            def legacy(self):
                return False

        x = Symbol("x")
        liar = Liar("liar", "x = 0", x, Integer(0), ProofChain())
        with pytest.raises(TypeError):
            TheoremBook().add(liar)
        with pytest.raises(TypeError):
            TheoremDefinition(liar)
        req, _ = _classify((ProofStep(x, Integer(0), rule="cite", provenance_tag="theorem", cites=liar),))
        assert any(r.legacy and "not a Theorem record" in r.name for r in req)

    @pytest.mark.parametrize("how", ["deepcopy", "pickle", "copy"])
    def test_copies_are_rebuilt_consistently(self, how):
        # d72e36c: a deep copy / pickle kept chain_replayed=True although its
        # (new, unminted) steps re-derive as unreplayed — replace() then
        # raised ValueError on the copy
        import copy
        import dataclasses
        import pickle

        p, q = Symbol("p"), Symbol("q")
        reg = PropertyRegistry()
        for s in (p, q):
            reg.declare(s, Graded(0))
        r = prove(ExpansionEngine(), Product(p, q), Product(q, p), registry=reg)
        t = Theorem("pq", "pq = qp", Product(p, q), Product(q, p), r.chain).with_structural_requires()
        assert t.chain_replayed
        c = {"deepcopy": copy.deepcopy, "pickle": lambda o: pickle.loads(pickle.dumps(o)), "copy": copy.copy}[how](t)
        assert type(c) is Theorem and c.requirements_derived
        dataclasses.replace(c, notes="still consistent")          # no ValueError
        assert c.chain_replayed == (how == "copy")                 # a shallow copy shares the minted steps
        assert c.registry_facts == t.registry_facts


class TestProofTrust2:
    def test_end_reads_hands_to_the_enclosing_log_only(self):
        # main 75acc5a: with mismatched nesting end_reads appended to
        # stack[-1] (a log opened LATER), and a log that was never opened
        # or closed twice still extended the top log
        from jacopy.core.registry import _READS, begin_reads, end_reads

        base = begin_reads()
        outer = begin_reads()
        inner = begin_reads()
        outer.append("o")
        try:
            end_reads(outer)                       # out of order
            assert base == ["o"] and inner == []
            end_reads(outer)                       # closed twice: no effect
            end_reads(["stray"])                   # never opened: no effect
            assert base == ["o"] and inner == []
        finally:
            end_reads(inner)
            end_reads(base)
        assert not any(l is inner or l is outer or l is base for l in getattr(_READS, "stack", []))
