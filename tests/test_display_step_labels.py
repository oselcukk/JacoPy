"""A proof step is labelled with the term ProofResult counts it
under — ``(definition)`` / ``(assumption)`` / ``(theorem)`` — in every
renderer (ASCII, terminal tree, LaTeX, Jupyter HTML, ``ProofStep.format``),
and an engine step's justification reads ``apply definition: …``
(display-polish 2026-10-02). Before, every definition step printed
``(axiom) … apply axiom`` while ProofResult called the same proof
"assumption-free". Display only: roles and tags are unchanged."""

from __future__ import annotations

import contextlib
import io

import pytest

import jacopy
from jacopy.central.objects import Bundle, forms, functions, vector_fields
from jacopy.display import chain_to_ascii, chain_to_latex, display_step, print_chain, render_chain, step_to_latex
from jacopy.display.jupyter import _step_summary_html
from jacopy.proof.step import ProofStep, classification_label


def _walk(steps):
    for s in steps:
        yield s
        yield from _walk(s.children)


@pytest.mark.parametrize(
    "tag, role, label",
    [
        ("axiom", "definition", "definition"),
        ("axiom", "assumption", "assumption"),
        ("theorem", "assumption", "assumption"),
        ("theorem", "theorem", "theorem"),
        ("theorem", "unverified-citation", "theorem"),
        ("theorem", None, "theorem"),
        ("axiom", None, "axiom"),
        ("computation", None, "computation"),
        (None, None, None),
    ],
)
def test_classification_label_table(tag, role, label):
    assert classification_label(tag, role) == label


@pytest.fixture(scope="module")
def lie_jacobi():
    from jacopy.central.tangent import prove_lie_jacobi

    reg = jacopy.PropertyRegistry()
    X, Y, Z = vector_fields("X Y Z")
    (f,) = functions("f", registry=reg)
    return prove_lie_jacobi(X, Y, Z, f, registry=reg)


@pytest.fixture(scope="module")
def cartan_result():
    from jacopy.central.tangent import tangent_engine
    from jacopy.proof.result import prove as prove_result

    reg = jacopy.PropertyRegistry()
    X, Y = vector_fields("X Y")
    (omega,) = forms("omega", degree=1)
    d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)
    lhs = jacopy.pairing(L_X(omega), Y)
    rhs = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)
    return prove_result(tangent_engine(registry=reg), lhs, rhs, registry=reg)


@pytest.fixture(scope="module")
def anchor():
    from jacopy.central.algebroid import algebroid, prove_anchor_morphism

    reg = jacopy.PropertyRegistry()
    (f,) = functions("f", registry=reg)
    E = algebroid("E", Bundle("E"), declare=("leibniz",))
    u, v = E.sections("u v")
    return prove_anchor_morphism(E, u, v, f, registry=reg)


def test_print_chain_labels_definitions(lie_jacobi):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_chain(lie_jacobi)
    out = buf.getvalue()
    assert "[Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))] (definition)" in out
    assert "apply definition: Lie" in out
    assert "(axiom)" not in out and "apply axiom" not in out
    # the cited antisymmetry is still a theorem
    assert "(theorem)" in out
    assert "(axiom)" not in render_chain(lie_jacobi, styles=False)


def test_labels_agree_with_proof_result(cartan_result):
    res = cartan_result
    assert res.closed and not res.requires  # "assumption-free"
    defs = {p.name for p in res.provenance if p.kind == "definition"}
    labelled = {s.rule for s in _walk(res.chain.steps) if s.classification == "definition"}
    assert defs and labelled == defs
    ascii_ = chain_to_ascii(res.chain)
    latex = chain_to_latex(res.chain, max_depth=2)
    assert "(definition)" in ascii_ and "(axiom)" not in ascii_
    assert "(definition)" in latex and "(axiom)" not in latex
    # ProofStep.format (the proof layer's own text) uses the same term
    assert "(definition)" in res.chain.steps[0].format()
    html = _step_summary_html(res.chain.steps[0], "full")
    assert "(definition)" in html
    assert r"\omega" in display_step(res.chain.steps[0])._repr_latex_()


def test_declared_axiom_is_an_assumption(anchor):
    chain, thm = anchor
    steps = [s for s in _walk(chain.steps) if s.role == "assumption"]
    assert steps
    for s in steps:
        assert s.classification == "assumption"
        assert s.justification.startswith("apply assumption: ")
        assert f"[{s.rule}] (assumption)" in chain_to_ascii(chain)
    assert "(assumption)" in step_to_latex(steps[0])


def test_hand_built_axiom_step_keeps_axiom_label():
    from jacopy.core.expr import Symbol

    s = ProofStep(Symbol("a"), Symbol("b"), rule="r", provenance_tag="axiom")
    assert s.classification == "axiom"
    assert "(axiom)" in chain_to_ascii(jacopy.ProofChain([s]))
