"""
Bibliography and source citations for rules, theorems and proof steps.

One table, :data:`BIBLIOGRAPHY`, maps a short key to the structured
fields of a reference (authors, year, title, venue, identifiers, the
local PDF the entry was checked against). Everything a reader sees is
GENERATED from those fields in APA 7 style:

* :meth:`Citation.in_text` — the parenthetical in-text citation with a
  locator, e.g. ``(Uchino, 2002, Section 1, axiom [C5])``;
* :func:`apa_reference` — the reference-list entry (plain text,
  Markdown or LaTeX).

A rule (:class:`~jacopy.proof.expansion.Definition`) or a theorem
(:class:`~jacopy.proof.theorems.Theorem`) states where it comes from
with its ``source`` attribute — a :class:`Citation` or a tuple of them,
built with :func:`cite`. The engine copies it onto every
:class:`~jacopy.proof.step.ProofStep` the rule produces, and the
display layer prints it next to the rule name. The attribute is
METADATA ONLY: no matching, rewriting or classification reads it.

Field policy (no invented data): every field below was read from the
title page of the local PDF named in ``pdf``, or — for works whose PDF
is not in the repository — from the reference list of a local paper
named in ``secondary``. A field neither source gives is left empty and
listed in ``missing``; :func:`apa_reference` prints such a gap as
``[… not in source]`` rather than guessing it. ``docs/CITATIONS.md``
records which code label was checked against which page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Tuple, Union


# --------------------------------------------------------------------- #
# reference records                                                      #
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class Reference:
    """Structured fields of one bibliography entry.

    ``authors`` is a tuple of ``(family name, initials)`` pairs, e.g.
    ``("Liu", "Z.-J.")``. ``kind`` selects the APA template:
    ``"article"``, ``"preprint"``, ``"thesis"`` or ``"unpublished"``
    (course material / project-internal compilations).
    """

    key: str
    authors: Tuple[Tuple[str, str], ...]
    year: str
    title: str  # sentence case, as APA prints it
    kind: str = "article"
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    article_number: str = ""
    doi: str = ""
    arxiv: str = ""
    institution: str = ""  # thesis: degree-granting institution
    description: str = ""  # bracketed APA description ("Doctoral dissertation")
    #: file name of the local copy (repository root, untracked), or ""
    pdf: str = ""
    #: version / edition of the local copy, e.g. "arXiv v1"
    pdf_version: str = ""
    #: where the fields come from when there is no local PDF
    secondary: str = ""
    #: fields neither the PDF nor the secondary source gives
    missing: Tuple[str, ...] = ()
    #: the short alias the code base uses in docstrings ("MC", "ADM", …)
    alias: str = ""

    @property
    def has_pdf(self) -> bool:
        return bool(self.pdf)


def _r(**kw) -> Reference:
    return Reference(**kw)


#: key → :class:`Reference`. Keys are author-year handles (stable,
#: ASCII). Aliases are the abbreviations the docstrings already use.
BIBLIOGRAPHY = {
    r.key: r
    for r in (
        _r(
            key="Uchino2002",
            alias="Uchino",
            authors=(("Uchino", "K."),),
            year="2002",
            title="Remarks on the definition of a Courant algebroid",
            kind="preprint",
            arxiv="math/0204010",
            pdf="uchino.pdf",
            pdf_version="arXiv v4, 27 Apr 2002",
        ),
        _r(
            key="DereliDogan2020",
            alias="MC",
            authors=(("Dereli", "T."), ("Doğan", "K.")),
            year="2020",
            title=(
                "Metric-connection geometries on pre-Leibniz algebroids: "
                "A search for geometrical structure in string models"
            ),
            kind="preprint",
            arxiv="2006.05957",
            pdf="metric-connection.pdf",
            pdf_version="arXiv v1, 10 Jun 2020",
        ),
        _r(
            key="CatalOzerDereliDogan2022",
            alias="B",
            authors=(("Çatal-Özer", "A."), ("Dereli", "T."), ("Doğan", "K.")),
            year="2022",
            title="Pre-metric-Bourbaki algebroids: Cartan calculus for M-theory",
            kind="preprint",
            arxiv="2210.00548",
            pdf="pre-metric-bourbaki.pdf",
            pdf_version="arXiv v1, 2 Oct 2022",
        ),
        _r(
            key="DereliDogan2023",
            alias="ADM",
            authors=(("Dereli", "T."), ("Doğan", "K.")),
            year="2023",
            title="‘Anti-commutable’ local pre-Leibniz algebroids and admissible connections",
            kind="article",
            journal="Journal of Geometry and Physics",
            volume="186",
            article_number="104752",
            doi="10.1016/j.geomphys.2023.104752",
            pdf="admissible.pdf",
            pdf_version="journal version",
        ),
        _r(
            key="CatalOzerDoganYetismisoglu2024",
            alias="DD",
            authors=(("Çatal-Özer", "A."), ("Doğan", "K."), ("Yetişmişoğlu", "C.")),
            year="2024",
            title=(
                "Drinfel’d double of bialgebroids for string and M theories: "
                "Dual calculus framework"
            ),
            kind="article",
            journal="Journal of High Energy Physics",
            volume="2024",
            issue="7",
            article_number="030",
            doi="10.1007/JHEP07(2024)030",
            arxiv="2312.06584",
            pdf="drinfeld double.pdf",
            pdf_version="journal version",
        ),
        _r(
            key="CatalOzerDoganYetismisoglu2025",
            alias="TW",
            authors=(("Çatal-Özer", "A."), ("Doğan", "K."), ("Yetişmişoğlu", "C.")),
            year="2025",
            title=(
                "Drinfel’d doubles, twists and all that… in stringy geometry "
                "and M theory"
            ),
            kind="article",
            journal="Journal of High Energy Physics",
            volume="2025",
            issue="1",
            article_number="192",
            doi="10.1007/JHEP01(2025)192",
            arxiv="2409.11973",
            pdf="drinfeld doubles twitss.pdf",
            pdf_version="journal version",
        ),
        _r(
            key="LiuWeinsteinXu1997",
            alias="LWX",
            authors=(("Liu", "Z.-J."), ("Weinstein", "A."), ("Xu", "P.")),
            year="1997",
            title="Manin triples for Lie bialgebroids",
            kind="article",
            journal="Journal of Differential Geometry",
            volume="45",
            pages="547–574",
            arxiv="dg-ga/9508013",
            secondary=(
                "Uchino (2002) ref. [2]; Dereli & Doğan (2023) ref. [28] "
                "(no local PDF)"
            ),
            missing=("issue", "doi"),
        ),
        _r(
            key="Roytenberg1999",
            alias="Roytenberg",
            authors=(("Roytenberg", "D."),),
            year="1999",
            title="Courant algebroids, derived brackets and even symplectic supermanifolds",
            kind="thesis",
            description="Doctoral dissertation",
            institution="University of California, Berkeley",
            arxiv="math/9910078",
            secondary="Uchino (2002) ref. [4]; Dereli & Doğan (2020) ref. [20] (no local PDF)",
        ),
        _r(
            key="GrabowskiMarmo2001",
            alias="Grabowski-Marmo",
            authors=(("Grabowski", "J."), ("Marmo", "G.")),
            year="2001",
            title="Non-antisymmetric versions of Nambu-Poisson and algebroid brackets",
            kind="article",
            journal="Journal of Physics A: Mathematical and General",
            volume="34",
            pages="3803–3809",
            secondary="Uchino (2002) ref. [3] (no local PDF)",
            missing=("issue", "doi"),
        ),
        _r(
            key="KosmannSchwarzbach2004",
            alias="Kosmann-Schwarzbach",
            authors=(("Kosmann-Schwarzbach", "Y."),),
            year="2004",
            title="Derived brackets",
            kind="article",
            journal="Letters in Mathematical Physics",
            volume="69",
            pages="61",
            arxiv="math/0312524",
            secondary="Çatal-Özer et al. (2025) ref. [90] (no local PDF)",
            missing=("issue", "last page", "doi"),
        ),
        _r(
            key="AsakawaMurakiSasaWatamura2015",
            alias="Watamura",
            authors=(("Asakawa", "T."), ("Muraki", "H."), ("Sasa", "S."), ("Watamura", "S.")),
            year="2015",
            title="Poisson-generalized geometry and R-flux",
            kind="article",
            journal="International Journal of Modern Physics A",
            volume="30",
            article_number="1550097",
            arxiv="1408.2649",
            secondary="Çatal-Özer et al. (2025) ref. [56]; Çatal-Özer et al. (2024) ref. [95] (no local PDF)",
            missing=("issue", "doi"),
        ),
        _r(
            key="Severa2017",
            alias="Ševera",
            authors=(("Ševera", "P."),),
            year="2017",
            title="Letters to Alan Weinstein about Courant algebroids",
            kind="preprint",
            arxiv="1707.00265",
            secondary="Çatal-Özer et al. (2022) ref. [16] (no local PDF)",
        ),
        _r(
            key="Math595Midterm2026",
            alias="Midterm",
            authors=(),
            year="2026",
            title="Math 595 midterm, Spring 2026",
            kind="unpublished",
            description="Unpublished course examination, Gebze Technical University",
            pdf="Math 595 - Midterm Spring 2026 GTU.pdf",
            # the PDF names no author; the institution is from the file name
            missing=("author",),
        ),
    )
}

#: alias (the abbreviations docstrings use) → key
ALIASES = {r.alias: r.key for r in BIBLIOGRAPHY.values() if r.alias}


def reference(key: str) -> Reference:
    """The :class:`Reference` for ``key`` (or for one of its aliases)."""
    if key in BIBLIOGRAPHY:
        return BIBLIOGRAPHY[key]
    if key in ALIASES:
        return BIBLIOGRAPHY[ALIASES[key]]
    raise KeyError(f"unknown bibliography key {key!r}; known: {sorted(BIBLIOGRAPHY)}")


# --------------------------------------------------------------------- #
# citations                                                              #
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class Citation:
    """A pointer into one reference: ``key`` plus an APA locator.

    ``locator`` is what follows the year in the in-text citation —
    ``"Proposition 2.1(i)"``, ``"Eq. (7.8)"``, ``"Section 1, axiom
    [C5]"`` — or ``""`` for a citation of the whole work. ``note`` is
    free commentary for the reader (shown in the reference block, never
    in the in-text citation)."""

    key: str
    locator: str = ""
    note: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not isinstance(self.locator, str):
            raise TypeError("Citation key and locator must be strings")
        ref = reference(self.key)  # validates; normalises an alias
        if ref.key != self.key:
            object.__setattr__(self, "key", ref.key)

    @property
    def reference(self) -> Reference:
        return BIBLIOGRAPHY[self.key]

    def author_year(self) -> str:
        """``Uchino, 2002`` — the APA author–date part."""
        return f"{_in_text_authors(self.reference)}, {year_label(self.reference)}"

    def in_text_inner(self) -> str:
        """The citation without parentheses (for grouping)."""
        s = self.author_year()
        return f"{s}, {self.locator}" if self.locator else s

    def in_text(self) -> str:
        """APA parenthetical citation, e.g. ``(Uchino, 2002, Proposition 2.2)``."""
        return f"({self.in_text_inner()})"

    def __str__(self) -> str:
        return self.in_text()


Source = Union[Citation, Tuple[Citation, ...], None]


def cite(key: str, locator: str = "", note: str = "") -> Citation:
    """Build a :class:`Citation`; ``key`` may be a key or an alias."""
    return Citation(reference(key).key, locator, note)


def as_citations(source) -> Tuple[Citation, ...]:
    """Normalise a ``source`` attribute (``None`` / one citation / an
    iterable of citations) to a tuple."""
    if source is None:
        return ()
    if isinstance(source, Citation):
        return (source,)
    out = tuple(source)
    if not all(isinstance(c, Citation) for c in out):
        raise TypeError("a source must be a Citation or a tuple of Citations")
    return out


def in_text(source) -> str:
    """APA in-text citation of one or several sources: several works in
    one parenthesis, alphabetical by first author, separated by
    semicolons — ``(Liu et al., 1997; Uchino, 2002, Section 1, [C5])``."""
    cits = as_citations(source)
    if not cits:
        return ""
    # one entry per work; several locators of the same work are listed
    # after its year: (Dereli & Doğan, 2020, Definition 3.1, Eq. (3.10))
    by_work: dict = {}
    for c in cits:
        locs = by_work.setdefault(c.key, [])
        if c.locator and c.locator not in locs:
            locs.append(c.locator)
    keys = sorted(by_work, key=lambda k: (_sort_name(BIBLIOGRAPHY[k]), BIBLIOGRAPHY[k].year))
    parts = []
    for k in keys:
        head = Citation(k).author_year()
        parts.append(", ".join([head] + by_work[k]))
    return "(" + "; ".join(parts) + ")"


# --------------------------------------------------------------------- #
# APA 7 formatting                                                       #
# --------------------------------------------------------------------- #


def _sort_name(ref: Reference) -> str:
    return ref.authors[0][0] if ref.authors else ref.title


def _in_text_authors(ref: Reference) -> str:
    fam = [a[0] for a in ref.authors]
    if not fam:  # APA: no author — the (shortened) title takes its place
        return ref.title
    if len(fam) == 1:
        return fam[0]
    if len(fam) == 2:
        return f"{fam[0]} & {fam[1]}"
    return f"{fam[0]} et al."


def year_label(ref: Reference) -> str:
    """The year with an APA ``a``/``b`` suffix when another entry has
    the same in-text author string and year (ordered by title)."""
    same = sorted(
        (r for r in BIBLIOGRAPHY.values()
         if r.year == ref.year and _in_text_authors(r) == _in_text_authors(ref)),
        key=lambda r: r.title.lower(),
    )
    if len(same) <= 1:
        return ref.year
    return ref.year + "abcdefghijklmnopqrstuvwxyz"[same.index(ref)]


def _author_list(ref: Reference) -> str:
    names = [f"{fam}, {ini}" if ini else fam for fam, ini in ref.authors]
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", . . . " + names[-1]


def _fmt(style: str):
    """Italic / escaping helpers for ``style`` in plain|markdown|latex."""
    if style == "plain":
        return (lambda s: s), (lambda s: s)
    if style == "markdown":
        return (lambda s: f"*{s}*"), (lambda s: s)
    if style == "latex":
        from jacopy.display.latex import text_to_latex

        return (lambda s: r"\textit{" + s + "}"), text_to_latex
    raise ValueError(f"unknown style {style!r}")


def _end(s: str) -> str:
    return s if s.endswith((".", "?", "!", "…")) else s + "."


def apa_reference(key_or_ref, style: str = "plain") -> str:
    """The APA 7 reference-list entry for a key / :class:`Reference`.

    ``style``: ``"plain"`` (no markup), ``"markdown"`` (``*italics*``)
    or ``"latex"`` (``\\textit``, escaped text). A field the sources do
    not give is printed as ``[<field> not in source]``."""
    ref = key_or_ref if isinstance(key_or_ref, Reference) else reference(key_or_ref)
    it, esc = _fmt(style)
    url = ""
    if ref.doi:
        url = f"https://doi.org/{ref.doi}"
    elif ref.arxiv:
        url = f"https://doi.org/10.48550/arXiv.{ref.arxiv}"
    if not ref.authors:
        # APA 7 work with no author: the title moves to the author slot
        desc = f" [{ref.description}]" if ref.description else ""
        return f"{it(esc(ref.title))}{esc(desc)}. ({year_label(ref)})."
    authors = _author_list(ref)
    if not authors.endswith("."):
        authors += "."
    head = f"{esc(authors)} ({year_label(ref)}). "
    gaps = [m for m in ref.missing if m in ("issue", "pages", "volume", "last page", "doi")]
    if ref.kind == "article":
        title = esc(_end(ref.title))
        venue = it(esc(ref.journal))
        vol = it(ref.volume) if ref.volume else ""
        if ref.issue:
            vol += f"({ref.issue})"
        bits = [venue]
        if vol:
            bits.append(vol)
        if ref.pages:
            bits.append(esc(ref.pages))
        elif ref.article_number:
            bits.append(f"Article {ref.article_number}")
        body = f"{head}{title} " + ", ".join(bits) + "."
        if gaps:
            names = ", ".join("DOI" if g == "doi" else g for g in gaps)
            body += " " + esc(f"[{names} not in source]")
        if ref.doi:
            body += f" https://doi.org/{ref.doi}"
        elif ref.arxiv:
            # no DOI in the sources: the arXiv identifier of the preprint
            body += f" arXiv:{ref.arxiv}"
        return body
    if ref.kind == "preprint":
        return f"{head}{it(esc(ref.title))} (arXiv:{ref.arxiv}). arXiv. {url}"
    if ref.kind == "thesis":
        desc = f"[{ref.description}, {ref.institution}]"
        tail = f" arXiv. {url}" if url else ""
        return f"{head}{it(esc(ref.title))} {esc(desc)}.{tail}"
    # unpublished material with an author
    desc = f" [{ref.description}]" if ref.description else ""
    return f"{head}{it(esc(ref.title))}{esc(desc)}."


# --------------------------------------------------------------------- #
# collecting the sources of a chain                                      #
# --------------------------------------------------------------------- #


def step_sources(step) -> Tuple[Citation, ...]:
    """The citations a :class:`ProofStep` carries (``()`` if none)."""
    return as_citations(getattr(step, "source", None))


def chain_sources(steps: Iterable, *, recurse: bool = True) -> Tuple[Citation, ...]:
    """Every distinct citation in ``steps`` (and, with ``recurse``,
    their children), in first-use order."""
    seen: dict = {}

    def walk(ss):
        for s in ss:
            for c in step_sources(s):
                seen.setdefault((c.key, c.locator), c)
            if recurse:
                walk(getattr(s, "children", ()))

    walk(steps)
    return tuple(seen.values())


def cited_references(citations: Iterable[Citation]) -> Tuple[Reference, ...]:
    """The distinct references behind ``citations``, APA-ordered
    (alphabetical by first author, then year)."""
    refs = {c.key: c.reference for c in citations}
    return tuple(sorted(refs.values(), key=lambda r: (_sort_name(r), r.year, r.title)))


def references_block(citations: Iterable[Citation], style: str = "plain") -> str:
    """A ``References`` block (APA list) for ``citations``."""
    refs = cited_references(citations)
    if not refs:
        return ""
    return "References\n" + "\n".join(apa_reference(r, style) for r in refs)


# --------------------------------------------------------------------- #
# BibTeX / biblatex-apa export                                           #
# --------------------------------------------------------------------- #


def _bib_protect(title: str) -> str:
    """Brace every word carrying a capital (proper nouns: Courant,
    Leibniz, M-theory …) so biblatex-apa's sentence casing keeps it."""
    import re

    words = title.split(" ")
    out = []
    for i, w in enumerate(words):
        first = i == 0 or (out and out[-1].endswith(":"))
        if not first and re.search(r"[A-Z]", w):
            core = w.rstrip(":,.")
            w = "{" + core + "}" + w[len(core):]
        out.append(w)
    return " ".join(out)


def bibtex_entry(key_or_ref) -> str:
    """One biblatex entry (UTF-8, for ``biblatex`` + ``style=apa`` +
    biber), generated from the same structured fields as
    :func:`apa_reference`."""
    ref = key_or_ref if isinstance(key_or_ref, Reference) else reference(key_or_ref)
    fields = []
    if ref.authors:
        fields.append(("author", " and ".join(f"{fam}, {ini}" if ini else "{" + fam + "}" for fam, ini in ref.authors)))
    fields.append(("title", _bib_protect(ref.title)))
    fields.append(("date", ref.year))
    if ref.kind == "article":
        etype = "article"
        fields.append(("journaltitle", ref.journal))
        if ref.volume:
            fields.append(("volume", ref.volume))
        if ref.issue:
            fields.append(("number", ref.issue))
        if ref.pages:
            fields.append(("pages", ref.pages.replace("–", "--")))
        elif ref.article_number:
            fields.append(("eid", ref.article_number))
    elif ref.kind == "preprint":
        etype = "online"
        fields.append(("eprinttype", "arxiv"))
        fields.append(("eprint", ref.arxiv))
    elif ref.kind == "thesis":
        etype = "thesis"
        fields.append(("type", "phdthesis"))
        fields.append(("institution", ref.institution))
    else:
        etype = "unpublished"
        if ref.description:
            fields.append(("note", ref.description))
    if ref.doi:
        fields.append(("doi", ref.doi))
    elif ref.arxiv and ref.kind != "preprint":
        fields.append(("eprinttype", "arxiv"))
        fields.append(("eprint", ref.arxiv))
    if ref.kind in ("preprint", "thesis") and ref.arxiv and not ref.doi:
        fields.append(("doi", f"10.48550/arXiv.{ref.arxiv}"))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields)
    return f"@{etype}{{{ref.key},\n{body}\n}}\n"


def bibtex_entries(citations: Iterable[Citation]) -> str:
    """The ``.bib`` text of the works behind ``citations``."""
    return "".join(bibtex_entry(r) for r in cited_references(citations))


__all__ = [
    "ALIASES",
    "BIBLIOGRAPHY",
    "Citation",
    "Reference",
    "apa_reference",
    "as_citations",
    "bibtex_entries",
    "bibtex_entry",
    "chain_sources",
    "cite",
    "cited_references",
    "in_text",
    "reference",
    "references_block",
    "step_sources",
    "year_label",
]
