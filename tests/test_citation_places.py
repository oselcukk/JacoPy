"""APA 7 in-text citations, one author–date–locator item per cited
place, items separated by semicolons (display-polish 2026-10-02). The
"Sub-steps cite" row of the algebroid anchor-morphism document read
"(Çatal-Özer et al., 2022, Definition 4.1, Eq. [4.4], Definition 4.1,
2025, Eq. [3.20]; …)" — a locator may contain a comma, so merged
locators and joined years could not be read back. Also:
``in_text(style="apa")`` is accepted as an alias of ``"plain"`` and an
unknown style names the valid ones."""

from __future__ import annotations

import re

import pytest

import jacopy
from jacopy.bibliography import TEXT_STYLES, apa_reference, cite, in_text, work_locators
from jacopy.central.objects import Bundle, functions
from jacopy.display.latex import cite_to_latex, theorem_to_latex_document


@pytest.fixture(scope="module")
def anchor():
    from jacopy.central.algebroid import algebroid, prove_anchor_morphism

    reg = jacopy.PropertyRegistry()
    (f,) = functions("f", registry=reg)
    E = algebroid("E", Bundle("E"), declare=("leibniz",))
    u, v = E.sections("u v")
    return prove_anchor_morphism(E, u, v, f, registry=reg)


def test_one_item_per_place_with_semicolons():
    src = (
        cite("CatalOzerDereliDogan2022", "Definition 4.1, Eq. (4.4)"),
        cite("CatalOzerDereliDogan2022", "Definition 4.1"),
        cite("MC", "Definition 3.4, Eq. (3.10)"),
        cite("MC", "Eq. (3.20)"),
    )
    assert in_text(src) == (
        "(Çatal-Özer et al., 2022, Definition 4.1, Eq. [4.4]; "
        "Dereli & Doğan, 2020, Definition 3.4, Eq. [3.10]; "
        "Dereli & Doğan, 2020, Eq. [3.20])"
    )


def test_subsumed_locator_dropped():
    src = (cite("MC", "Definition 3.1"), cite("MC", "Definition 3.1, Eq. (3.10)"), cite("MC", "Definition 3.15"))
    assert work_locators(src) == {"DereliDogan2020": ["Definition 3.1, Eq. (3.10)", "Definition 3.15"]}


def test_biblatex_one_entry_per_place():
    src = (cite("MC", "Definition 3.1"), cite("MC", "Definition 3.15"))
    assert cite_to_latex(src, "biblatex") == r"\parencites[Definition 3.1]{DereliDogan2020}[Definition 3.15]{DereliDogan2020}"


def test_anchor_document_sub_steps_row_is_apa(anchor):
    _, thm = anchor
    doc = theorem_to_latex_document(thm, max_steps=3)
    flat = " ".join(line.removeprefix("&\\text{").removesuffix("} \\\\").removesuffix("}") for line in doc.splitlines())
    assert "Definition 4.1, 2025" not in flat
    assert "Sub-steps cite:" in flat
    assert r"\c{C}atal-\"{O}zer et al., 2025, Eq. [3.20]" in flat
    # every year inside a citation follows its author string
    for cite_text in re.findall(r"cite: \(([^)]*)\)", flat):
        for item in cite_text.split("; "):
            assert re.match(r"[^,]+, \d{4}", item), item


# ---- 4. in_text(style="apa") ------------------------------------------- #


def test_in_text_accepts_apa_alias():
    src = (cite("Uchino2002", "Section 1, axiom [C5]"), cite("LiuWeinsteinXu1997"))
    assert in_text(src, style="apa") == in_text(src) == "(Liu et al., 1997; Uchino, 2002, Section 1, axiom [C5])"
    assert apa_reference("Uchino2002", style="apa") == apa_reference("Uchino2002")
    assert cite("Uchino2002").in_text("apa") == "(Uchino, 2002)"


def test_in_text_unknown_style_names_valid_ones():
    with pytest.raises(ValueError) as e:
        in_text(cite("Uchino2002"), style="chicago")
    msg = str(e.value)
    for style in TEXT_STYLES:
        assert repr(style) in msg
    assert "APA 7" in msg and "biblatex" in msg
    # also for an empty source: the style is validated first
    with pytest.raises(ValueError):
        in_text((), style="chicago")
