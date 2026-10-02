"""Literature sources of rules, theorems and proof steps
(:mod:`jacopy.bibliography`), their display (ASCII / terminal / LaTeX)
and the LaTeX transcript fixes of audit 0B00E1B-FULL T3-2 / K1-9.

The demo of the feature is Uchino's Proposition 2.1(i)
(``prove_left_leibniz_c3``): every axiom step of its chain must name a
paper AND a numbered place in it, in the ASCII and in the LaTeX output.
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import tempfile
import warnings
from pathlib import Path

import pytest

from jacopy.bibliography import (
    BIBLIOGRAPHY,
    cited_references,
    Citation,
    Reference,
    apa_reference,
    as_citations,
    bibtex_entries,
    chain_sources,
    cite,
    in_text,
    references_block,
)
from jacopy.central.objects import functions
from jacopy.core.expr import Integer, Sum, Symbol
from jacopy.core.registry import PropertyRegistry
from jacopy.display import chain_to_ascii, chain_to_latex, chain_to_latex_document, render_chain, step_to_latex
from jacopy.display.latex import math_lines, text_to_latex, theorem_to_latex_document
from jacopy.packages.generalized.courant_axioms import courant_context, prove_left_leibniz_c3
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.step import ProofStep

ROOT = Path(__file__).resolve().parents[1]


# ---- APA 7 formatting ------------------------------------------------ #


def test_apa_in_text_author_rules():
    # one author / two authors (&) / three or more (et al.)
    assert cite("Uchino2002", "Proposition 2.2").in_text() == "(Uchino, 2002, Proposition 2.2)"
    assert cite("DereliDogan2023", "Proposition 3.7").in_text() == "(Dereli & Doğan, 2023, Proposition 3.7)"
    assert cite("CatalOzerDereliDogan2022", "Lemma 9.1").in_text() == "(Çatal-Özer et al., 2022, Lemma 9.1)"
    assert cite("LiuWeinsteinXu1997").in_text() == "(Liu et al., 1997)"
    # aliases resolve to the key
    assert cite("MC", "Definition 3.1").key == "DereliDogan2020"


def test_apa_in_text_groups_works_alphabetically_and_merges_locators():
    src = (
        cite("Uchino2002", "Section 1, axiom [C5]"),
        cite("LiuWeinsteinXu1997"),
        cite("MC", "Definition 3.1"),
        cite("MC", "Eq. (3.10)"),
    )
    # §6.9: parentheses inside the citation's parentheses become brackets
    assert in_text(src) == (
        "(Dereli & Doğan, 2020, Definition 3.1, Eq. [3.10]; Liu et al., 1997; "
        "Uchino, 2002, Section 1, axiom [C5])"
    )


def test_apa_in_text_order_folds_accents_and_joins_years():
    src = (
        cite("Uchino2002", "Remark 1"),
        cite("Severa2017"),
        cite("Roytenberg1999"),
        cite("CatalOzerDereliDogan2022", "Lemma 9.1"),
        cite("ADM", "Proposition 3.7"),
        cite("MC", "Definition 3.1"),
    )
    # Ç sorts as C, Š as S (§8.12); same authors, several years joined
    assert in_text(src) == (
        "(Çatal-Özer et al., 2022, Lemma 9.1; "
        "Dereli & Doğan, 2020, Definition 3.1, 2023, Proposition 3.7; "
        "Roytenberg, 1999; Ševera, 2017; Uchino, 2002, Remark 1)"
    )
    order = [r.key for r in cited_references(src)]
    assert order == ["CatalOzerDereliDogan2022", "DereliDogan2020", "DereliDogan2023",
                     "Roytenberg1999", "Severa2017", "Uchino2002"]


def test_apa_no_author_work_is_cited_by_italic_title():
    assert in_text(cite("Midterm", "Problem 2"), "markdown") == "(*Math 595 Midterm, Spring 2026*, 2026, Problem 2)"
    assert in_text(cite("Guideline", "item 1"), "latex") == r"(\textit{Math 595 -- JacoPy}, n.d., item 1)"


def test_apa_et_al_disambiguation_and_initials(monkeypatch):
    def ref(key, authors, year="2010", title="T"):
        return Reference(key=key, authors=authors, year=year, title=title, kind="preprint", arxiv=key)

    # §8.18: same year, lists differ, same short form → more names
    monkeypatch.setitem(BIBLIOGRAPHY, "K1", ref("K1", (("Kapoor", "A."), ("Bloom", "B."), ("Montez", "C."), ("Z", "D."))))
    monkeypatch.setitem(BIBLIOGRAPHY, "K2", ref("K2", (("Kapoor", "A."), ("Bloom", "B."), ("Zucker", "E."), ("Z", "D."))))
    assert Citation("K1").in_text() == "(Kapoor, Bloom, Montez, et al., 2010)"
    assert Citation("K2").in_text() == "(Kapoor, Bloom, Zucker, et al., 2010)"
    # identical lists, same year → a/b by title (§8.19)
    monkeypatch.setitem(BIBLIOGRAPHY, "Y1", ref("Y1", (("Yee", "A."),), title="Beta"))
    monkeypatch.setitem(BIBLIOGRAPHY, "Y2", ref("Y2", (("Yee", "A."),), title="Alpha"))
    assert Citation("Y2").in_text() == "(Yee, 2010a)" and Citation("Y1").in_text() == "(Yee, 2010b)"
    # §8.20: same surname, different first author → initials
    monkeypatch.setitem(BIBLIOGRAPHY, "W1", ref("W1", (("Wu", "A."),), year="2001"))
    monkeypatch.setitem(BIBLIOGRAPHY, "W2", ref("W2", (("Wu", "B."),), year="2005"))
    assert Citation("W1").in_text() == "(A. Wu, 2001)" and Citation("W2").in_text() == "(B. Wu, 2005)"


def test_apa_reference_list_entries():
    assert apa_reference("Uchino2002") == (
        "Uchino, K. (2002). Remarks on the definition of a Courant algebroid "
        "(arXiv:math/0204010). arXiv. https://doi.org/10.48550/arXiv.math/0204010"
    )
    assert apa_reference("DereliDogan2023") == (
        "Dereli, T., & Doğan, K. (2023). ‘Anti-commutable’ local pre-Leibniz algebroids and "
        "admissible connections. Journal of Geometry and Physics, 186, Article 104752. "
        "https://doi.org/10.1016/j.geomphys.2023.104752"
    )
    assert apa_reference("CatalOzerDoganYetismisoglu2024", "markdown").startswith(
        "Çatal-Özer, A., Doğan, K., & Yetişmişoğlu, C. (2024). Drinfel’d double of bialgebroids "
        "for string and M theories: Dual calculus framework. *Journal of High Energy Physics*, *2024*(7), "
        "Article 030."
    )
    # a field no source gives is MARKED, never invented
    lwx = apa_reference("LiuWeinsteinXu1997")
    assert "[issue, DOI not in source]" in lwx and "45, 547–574" in lwx


def test_year_suffix_only_for_identical_author_lists(monkeypatch):
    a = Reference(key="ZzA", authors=(("Zed", "A."),), year="2001", title="Alpha", kind="preprint", arxiv="x")
    b = Reference(key="ZzB", authors=(("Zed", "A."),), year="2001", title="Beta", kind="preprint", arxiv="y")
    c = Reference(key="ZzC", authors=(("Zed", "A."), ("Q", "B.")), year="2001", title="Gamma", kind="preprint", arxiv="z")
    monkeypatch.setitem(BIBLIOGRAPHY, "ZzA", a)
    monkeypatch.setitem(BIBLIOGRAPHY, "ZzB", b)
    monkeypatch.setitem(BIBLIOGRAPHY, "ZzC", c)
    assert Citation("ZzA").in_text() == "(Zed, 2001a)" and Citation("ZzB").in_text() == "(Zed, 2001b)"
    assert Citation("ZzC").in_text() == "(Zed & Q, 2001)"


def test_bibtex_protects_capitalised_words():
    from jacopy.bibliography import bibtex_entry

    bib = bibtex_entry("CatalOzerDereliDogan2022")
    assert "title = {{Pre-metric-Bourbaki} algebroids: {Cartan} calculus for {M-theory}}" in bib
    assert "{Courant}" in bibtex_entry("Uchino2002") and "{Lie}" in bibtex_entry("LiuWeinsteinXu1997")
    assert "{Drinfel’d}" in bibtex_entry("CatalOzerDoganYetismisoglu2024")


def test_every_reference_records_its_provenance():
    for ref in BIBLIOGRAPHY.values():
        # a local PDF, or the secondary source the fields were read from
        assert ref.pdf or ref.secondary, ref.key
        assert ref.title and ref.year
        apa_reference(ref)
        apa_reference(ref, "latex").encode("ascii")  # pdfLaTeX-safe
    with pytest.raises(KeyError):
        cite("NoSuchPaper2099")
    with pytest.raises(TypeError):
        as_citations(("not a citation",))


def test_citations_doc_reference_list_is_generated():
    """docs/CITATIONS.md carries the APA list generated from the table
    (single source of truth)."""
    if not (ROOT / "docs" / "CITATIONS.md").is_file():
        pytest.skip("docs/CITATIONS.md is not next to the tests (wheel run)")
    doc = (ROOT / "docs" / "CITATIONS.md").read_text(encoding="utf-8")
    block = doc.split("<!-- references:begin -->")[1].split("<!-- references:end -->")[0]
    expected = "\n\n".join(apa_reference(r, "markdown") for r in cited_references([cite(k) for k in BIBLIOGRAPHY]))
    assert block.strip() == expected.strip()


# ---- metadata plumbing --------------------------------------------- #


class _Toy(Definition):
    name = "toy rule"
    source = cite("Uchino2002", "Remark 1")

    def matches(self, expr):
        return expr == Symbol("a")

    def rewrite(self, expr):
        return Integer(0)


def test_engine_copies_rule_source_onto_steps_and_wrappers():
    from jacopy.proof.result import _reversed_step, _whole_step

    eng = ExpansionEngine([_Toy()])
    after, step = eng.expand_once(Sum(Symbol("a"), Symbol("b")))
    assert step.source == (cite("Uchino2002", "Remark 1"),)
    whole = _whole_step(Sum(Symbol("a"), Symbol("b")), after, step)
    assert whole.source == step.source and _reversed_step(step).source == step.source
    # a step without source stays None; a hand-built step may carry one
    assert ProofStep(Symbol("a"), Integer(0), rule="x").source is None


def test_source_is_metadata_only():
    """Adding a source changes neither matching nor the step record's
    proof-relevant fields."""
    class _Bare(_Toy):
        source = None

    a, s1 = ExpansionEngine([_Toy()]).expand_once(Symbol("a"))
    b, s2 = ExpansionEngine([_Bare()]).expand_once(Symbol("a"))
    assert a == b and s1.rule == s2.rule and s1.provenance_tag == s2.provenance_tag and s1.role == s2.role


# ---- the demo: Uchino Proposition 2.1(i) ---------------------------- #


@pytest.fixture(scope="module")
def c3():
    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    E = courant_context()
    x, y = E.sections("x y")
    return prove_left_leibniz_c3(E, x, y, f, registry=reg)


def _walk(steps):
    for s in steps:
        yield s
        yield from _walk(s.children)


def test_c3_every_axiom_step_names_paper_and_number(c3):
    chain, thm = c3
    axiom_steps = [s for s in _walk(chain.steps) if s.provenance_tag == "axiom"]
    assert axiom_steps
    for s in axiom_steps:
        assert s.source, s.rule
        # at least one citation with a numbered locator (Definition 3.1,
        # Section 1, axiom [C5], Eq. (3.10), …)
        assert any(re.search(r"\d", c.locator) for c in s.source), (s.rule, s.source)
    c5 = next(s for s in axiom_steps if s.rule.startswith("[C5]"))
    assert "Uchino, 2002" in in_text(c5.source) and "[C5]" in in_text(c5.source)
    # the theorem itself cites Uchino Proposition 2.1(i)
    assert any(c.key == "Uchino2002" and "2.1" in c.locator for c in as_citations(thm.source))


def test_c3_ascii_shows_every_axiom_source(c3):
    chain, _ = c3
    text = chain_to_ascii(chain, references=True)
    for s in _walk(chain.steps):
        if s.provenance_tag == "axiom":
            assert f"[{s.rule}] (axiom) — {in_text(s.source)}" in text
    assert "\n\nReferences\n" in text
    assert "\nLiu, Z.-J., Weinstein, A., & Xu, P. (1997). Manin triples for Lie bialgebroids." in text
    assert "Uchino, K. (2002). Remarks on the definition of a Courant algebroid" in text
    plain = render_chain(chain, styles=False, references=True)
    # the rich tree wraps long lines at 120 columns
    assert "(Liu et al., 1997; Uchino, 2002," in plain and "\nReferences\n" in plain


def test_c3_latex_shows_every_axiom_source(c3):
    chain, _ = c3
    body = chain_to_latex(chain, max_depth=3)
    flat = re.sub(r"\s+", " ", body)
    for s in _walk(chain.steps):
        if s.provenance_tag == "axiom":
            for c in s.source:
                assert text_to_latex(c.author_year()) in flat, (s.rule, c)
    first = step_to_latex(chain.steps[0])
    assert r"\text{Source: (Liu et al., 1997; Uchino, 2002, Section 1, axiom [C5])}" in first
    # collapsed sub-proofs still name what they cite
    assert "Sub-steps cite:" in chain_to_latex(chain)


def test_c3_latex_document_lists_references(c3):
    chain, thm = c3
    doc = chain_to_latex_document(chain, title="Uchino Proposition 2.1(i)")
    assert r"\section*{References}" in doc
    assert r"Uchino, K. (2002). \textit{Remarks on the definition of a Courant algebroid}" in doc
    assert doc.isascii()
    bib = chain_to_latex_document(chain, references="biblatex")
    assert r"\usepackage[style=apa,backend=biber]{biblatex}" in bib
    # one \parencites group per step: all works, APA order, merged locators
    assert r"\parencites{LiuWeinsteinXu1997}[Section 1, axiom {[}C5{]}]{Uchino2002}" in bib
    assert "@online{Uchino2002," in bibtex_entries(chain_sources(chain.steps))
    assert r"\section*{References}" not in chain_to_latex_document(chain, references=None)
    assert "Uchino" in theorem_to_latex_document(thm)


def _pdflatex(doc: str):
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "doc.tex").write_text(doc, encoding="utf-8")
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
            cwd=tmp, capture_output=True, text=True, timeout=120,
        )
        log = (Path(tmp) / "doc.log").read_text(errors="replace")
    return r.returncode, log


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
@pytest.mark.parametrize("depth", [0, 3])
def test_c3_document_compiles_without_overfull_lines(c3, depth):
    chain, thm = c3
    for doc in (
        chain_to_latex_document(chain, title="Uchino Proposition 2.1(i)", max_depth=depth),
        theorem_to_latex_document(thm, max_depth=depth),
    ):
        rc, log = _pdflatex(doc)
        assert rc == 0, [l for l in log.splitlines() if l.startswith("!")]
        over = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt", log)]
        assert all(o <= 1.0 for o in over), over


# ---- LaTeX: Unicode and line breaking (T3-2, K1-9) ------------------ #


def test_text_to_latex_backslash_is_escaped_once():
    assert text_to_latex(r"a\b {c}") == r"a\textbackslash{}b \{c\}"


def test_text_to_latex_unicode():
    out = text_to_latex("(Çatal-Özer, Doğan & Yetişmişoğlu) ρ∘D ⟨x,y⟩ π♯α ∧ ᴸT 𝔖 b — ½")
    assert out.isascii()
    for piece in (r"\c{C}atal-\"{O}zer", r"Do\u{g}an", r"\&", r"\ensuremath{\rho}", r"\ensuremath{\circ}",
                  r"\ensuremath{\langle}", r"\ensuremath{\sharp}", r"\ensuremath{\wedge}",
                  r"\ensuremath{^{L}}", r"\ensuremath{\mathfrak{S}}", "---"):
        assert piece in out, piece


def _library_strings():
    """Every string literal of the library that contains non-ASCII
    text (rule names, statements, notes, docstrings)."""
    for path in sorted((ROOT / "jacopy").rglob("*.py")):
        if "oracle" in path.parts or "display" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and not node.value.isascii():
                yield path.name, node.value


def test_every_library_string_is_latex_safe():
    """K1-9 acceptance: every non-ASCII character the code base uses has
    a LaTeX mapping (no '?' fallback, no pdfLaTeX Unicode error)."""
    bad = {}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for fname, s in _library_strings():
            try:
                out = text_to_latex(s)
            except UserWarning as w:
                bad.setdefault(str(w).split("'")[1], fname)
                continue
            assert out.isascii(), (fname, s[:40])
    assert not bad, bad


def test_math_lines_break_long_sums():
    xs = [Symbol(f"x_{i}") for i in range(40)]
    lines = math_lines(Sum(*xs), width=20)
    assert len(lines) > 1 and lines[1].startswith("+ ")
    assert all(len(l) < 80 for l in lines)
    # a short expression stays on one line
    assert len(math_lines(Sum(xs[0], xs[1]))) == 1


def _random_names(n=300, seed=7):
    import random

    from jacopy.display.latex import _UNICODE_TO_LATEX

    rng = random.Random(seed)
    pool = (
        list("abcXYZ019_^ ")
        + list(_UNICODE_TO_LATEX)
        + list("₀₁₂₃⁰¹²⁻ᵢⱼₐₙᴸᵍᵀ𝔖𝕃𝒜𝐀𝜔")
        + ["\u0303", "\u0307", "\u0302"]
    )
    for _ in range(n):
        yield "".join(rng.choice(pool) for _ in range(rng.randint(1, 7)))


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
def test_latex_name_never_yields_uncompilable_math():
    """Any name — including scripts after scripts (``x^ᵢ``), trailing
    ``_``, combining marks — must give compilable LaTeX."""
    from jacopy.display.latex import latex_name

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        body = "\n".join(f"${latex_name(n)}$\\par" for n in _random_names())
    assert latex_name("x^ᵢ") == "x^{_{i}}" and latex_name("x_") == "x_{}"
    doc = (
        "\\documentclass{article}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n"
        "\\begin{document}\n" + body + "\n\\end{document}\n"
    )
    rc, log = _pdflatex(doc)
    assert rc == 0, [l for l in log.splitlines() if l.startswith("!")][:5]


# ---- hand-built axiom steps copy the source of what they cite ------ #


def _axiom_steps(chain):
    return [s for s in _walk(chain.steps) if s.provenance_tag == "axiom"]


def test_general_twist_axiom_steps_are_sourced():
    from jacopy.central.algebroid.context import algebroid
    from jacopy.packages.generalized.general_twist import (
        prove_general_twist_invariance,
        prove_general_twist_jacobi,
        prove_general_twist_symmetric_part,
    )

    reg = PropertyRegistry()
    functions("f", registry=reg)
    E = algebroid("E", declare=("right-leibniz", "jacobi", "symmetric-part", "metric-invariance"))
    u, v, w = E.sections("u v w")
    runs = (
        prove_general_twist_jacobi(E, u, v, w, registry=reg),
        prove_general_twist_symmetric_part(E, u, v, registry=reg, declare_r_axioms=True),
        prove_general_twist_invariance(E, u, v, w, registry=reg, declare_r_axioms=True),
    )
    for chain, _ in runs:
        steps = _axiom_steps(chain)
        assert steps
        for s in steps:
            assert s.source and any(re.search(r"\d", c.locator) for c in s.source), s.rule


def test_r_flux_closure_declaration_is_sourced():
    from jacopy.packages.generalized.r_twisted import RFluxClosureDeclaration

    assert RFluxClosureDeclaration.source.key == "AsakawaMurakiSasaWatamura2015"


# ---- ADM printed-sign regressions (M8-1 = M7-3; lane-C finding) ----- #


@pytest.fixture(scope="module")
def adm():
    from jacopy.central.algebroid import algebroid, locality_projector
    from jacopy.central.objects import Bundle
    from jacopy.central.objects.frame import Frame
    from jacopy.packages.metric_affine.e_connection import e_connection

    reg = PropertyRegistry()
    E = algebroid("E", Bundle("E"), declare=("local", "regular", "anchor-morphism"))
    u, v, w = E.sections("u v w")
    return reg, E, u, v, w, e_connection(E), Frame("e", bundle=E.bundle), locality_projector(E)


def test_adm_3_35_printed_signs_are_rejected(adm):
    """ADM (3.35) prints the (1−𝒫)Λ block and [[u,v]^∇,w]^∇ with +; with
    the paper's own definitions both enter with − (the library's form,
    which closes). The printed form must NOT close (admissible ∇)."""
    from jacopy.packages.metric_affine.admissible import AdmissibilityDeclaration, modified_bracket
    from jacopy.packages.metric_affine.e_bianchi import (
        _cyc,
        covariant_modified_torsion_derivative,
        prove_e_bianchi_first_identity,
    )
    from jacopy.packages.metric_affine.modified import (
        _engine,
        generalized_ricci_anomaly,
        modified_torsion,
        projected_curvature,
    )
    from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure

    reg, E, u, v, w, nabla, fr, P = adm
    assert prove_e_bianchi_first_identity(E, nabla, fr, P, u, v, w, registry=reg, admissible=True).steps
    lhs = _cyc(lambda a, b, c: projected_curvature(E, nabla, fr, P, a, b, c), u, v, w)
    printed = Sum(
        _cyc(lambda a, b, c: covariant_modified_torsion_derivative(E, nabla, fr, a, b, c), u, v, w),
        _cyc(lambda a, b, c: modified_torsion(E, nabla, fr, modified_torsion(E, nabla, fr, a, b), c), u, v, w),
        _cyc(lambda a, b, c: generalized_ricci_anomaly(E, nabla, fr, P, a, b, c), u, v, w),  # paper: +
        _cyc(lambda a, b, c: modified_bracket(E, nabla, fr, modified_bracket(E, nabla, fr, a, b), c), u, v, w),  # paper: +
    )
    engine = _engine(E, fr, reg, projectors=(P,))
    engine.register(AdmissibilityDeclaration(E, nabla, fr))
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(lhs, printed, registry=reg, engine=engine)


def test_adm_3_44_printed_sign_is_rejected(adm):
    """d̂²α(u,v,w) = +⟨α, b̂(b̂(u,v),w) − b̂(b̂(u,w),v) + b̂(b̂(v,w),u)⟩
    (Palais formula; TW (A.5)) closes; the opposite overall sign — what
    ADM (3.44) prints for an admissible ∇ — does not."""
    from jacopy.central.objects import forms
    from jacopy.core.expr import Neg
    from jacopy.core.multi_eval import MultiEval
    from jacopy.core.pairing import Pairing
    from jacopy.packages.metric_affine.derived import (
        d_derived,
        derived_algebroid,
        derived_engine,
        prove_projected_d_squared_associator,
    )
    from jacopy.packages.metric_affine.e_bianchi import projected_modified_bracket
    from jacopy.proof.strategies import ExpandAndSimplify, ProofFailure

    reg, E, u, v, w, nabla, fr, P = adm
    (alpha,) = forms("α", degree=1, bundle=E.bundle)
    assert prove_projected_d_squared_associator(E, nabla, fr, P, alpha, u, v, w, registry=reg).steps
    D = derived_algebroid(E, projected=True)

    def bhat(p, q):
        return projected_modified_bracket(E, nabla, fr, P, p, q)

    node = MultiEval(d_derived(D, d_derived(D, alpha)), u, v, w, alternating=True, slot_kind="vector")
    assoc = Sum(bhat(bhat(u, v), w), Neg(bhat(bhat(u, w), v)), bhat(bhat(v, w), u))
    with pytest.raises(ProofFailure):
        ExpandAndSimplify().prove(
            node, Neg(Pairing(alpha, assoc)), registry=reg,
            engine=derived_engine(E, D, nabla, fr, registry=reg, projector=P),
        )
