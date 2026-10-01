"""Audit 0b00e1b-FULL — proof trust (guideline 15e: re-using proven
results is only as good as the cited record).

* P0-3 ≡ M1X-2 (with K2-16): registry declarations are requirements of
  a proof; a citation is checked against the citing registry.

Every acceptance test builds its target equation here.
"""

import pytest

from jacopy.algebra.derivation import Derivation
from jacopy.core.expr import Neg, Product, Symbol
from jacopy.core.properties import Graded, Scalar
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.expansion import ExpansionEngine
from jacopy.proof.registry_facts import registry_context
from jacopy.proof.result import prove
from jacopy.proof.theorems import Theorem, TheoremDefinition, check_citation


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
        assert not thm.legacy

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
