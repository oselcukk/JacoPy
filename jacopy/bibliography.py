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
    #: work with no author: the (shortened) title in Title Case that
    #: APA puts in the author slot of the in-text citation
    in_text_title: str = ""
    #: an open question about the identification (shown in the docs)
    caveat: str = ""

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
            secondary="Çatal-Özer et al. (2025) ref. [67]; Çatal-Özer et al. (2024) ref. [90] (no local PDF)",
            missing=("issue", "last page", "doi"),
            caveat=(
                "AMBIGUOUS: the code cites 'Kosmann-Schwarzbach 1996' (derived "
                "brackets); no local source lists a 1996 work, only this 2004 one"
            ),
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
            secondary="Çatal-Özer et al. (2024) ref. [56]; Çatal-Özer et al. (2025) ref. [95] (no local PDF)",
            missing=("issue", "doi"),
            caveat="no local PDF: equation numbers cited from it are unverified",
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
            in_text_title="Math 595 Midterm, Spring 2026",
            kind="unpublished",
            description="Unpublished course examination, Gebze Technical University",
            pdf="Math 595 - Midterm Spring 2026 GTU.pdf",
            # the PDF names no author; the institution is from the file name
            missing=("author",),
        ),
        _r(
            key="Math595Guideline",
            alias="Guideline",
            authors=(),
            year="n.d.",
            # the PDF has no title page, author or date (its metadata title
            # is a Google Docs template name); title from the file name
            title="Math 595 – JacoPy",
            in_text_title="Math 595 – JacoPy",
            kind="unpublished",
            description="Unpublished course project guidelines",
            pdf="Math 595 -JacoPy.pdf",
            missing=("author", "date", "title (taken from the file name)"),
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

    def in_text(self, style: str = "plain") -> str:
        """APA parenthetical citation, e.g. ``(Uchino, 2002, Proposition 2.2)``."""
        return in_text(self, style)

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


def in_text(source, style: str = "plain") -> str:
    """APA 7 parenthetical citation of one or several sources.

    * works in one parenthesis, alphabetical by the (accent-folded)
      author string, separated by semicolons (§8.12);
    * several locators of one work follow its year; several years of
      the same authors are joined (``Dereli & Doğan, 2020, Definition
      3.1, 2023, Proposition 3.7``);
    * parentheses inside a locator become brackets (§6.9):
      ``Eq. (3.10)`` → ``Eq. [3.10]``;
    * a work with no author is cited by its italic Title-Case title.

    ``style``: ``"plain"`` (no markup), ``"markdown"`` or ``"latex"``
    (escaped text, ``\\textit`` titles)."""
    cits = as_citations(source)
    if not cits:
        return ""
    it, esc = _fmt(style)
    by_work: dict = {}
    for c in cits:
        locs = by_work.setdefault(c.key, [])
        if c.locator and c.locator not in locs:
            locs.append(c.locator)
    groups: dict = {}
    for k in by_work:
        groups.setdefault(_in_text_authors(BIBLIOGRAPHY[k]), []).append(k)
    parts = []
    for authors in sorted(groups, key=_fold):
        keys = sorted(groups[authors], key=lambda k: (year_label(BIBLIOGRAPHY[k]), k))
        head = it(esc(authors)) if not BIBLIOGRAPHY[keys[0]].authors else esc(authors)
        bits = [head]
        for k in keys:
            bits.append(year_label(BIBLIOGRAPHY[k]))
            bits.extend(esc(apa_locator(loc)) for loc in by_work[k])
        parts.append(", ".join(bits))
    return "(" + "; ".join(parts) + ")"


def apa_locator(locator: str) -> str:
    """APA §6.9: inside the citation's parentheses, parentheses become
    brackets — ``Eq. (3.10)`` → ``Eq. [3.10]``."""
    return locator.replace("(", "[").replace(")", "]")


# --------------------------------------------------------------------- #
# APA 7 formatting                                                       #
# --------------------------------------------------------------------- #

_TURKISH_FOLD = str.maketrans({"ı": "i", "İ": "I", "Ç": "C", "ç": "c", "Ş": "S", "ş": "s",
                               "Ğ": "G", "ğ": "g", "Ö": "O", "ö": "o", "Ü": "U", "ü": "u"})


def _fold(text: str) -> str:
    """Alphabetising key: accents folded to the base letter (Turkish
    letters explicitly), case-insensitive — ``Çatal-Özer`` sorts as
    ``catal-ozer``, ``Ševera`` as ``severa``."""
    import unicodedata

    t = unicodedata.normalize("NFKD", text.translate(_TURKISH_FOLD))
    return "".join(c for c in t if not unicodedata.combining(c)).casefold()


def _sort_name(ref: Reference) -> str:
    """APA reference-list order: author family names (then initials), or
    the title for a work with no author."""
    import re

    raw = ref.title if not ref.authors else " ".join(f"{fam} {ini}" for fam, ini in ref.authors)
    # letter by letter, punctuation ignored
    return re.sub(r"[^\w ]", "", _fold(raw))


def _ref_sort_key(ref: Reference):
    return (_sort_name(ref), "0" if ref.year == "n.d." else ref.year, _fold(ref.title))


def _initials_needed(ref: Reference) -> bool:
    """APA §8.20: first authors with the same surname but different
    initials are cited with initials."""
    if not ref.authors:
        return False
    fam, ini = ref.authors[0]
    return any(r.authors and r.authors[0][0] == fam and r.authors[0][1] != ini
               for r in BIBLIOGRAPHY.values())


def _short_authors(ref: Reference, n: int) -> str:
    """First ``n`` names then "et al." (all names, with "&", when ``n``
    reaches the list length)."""
    fam = [a[0] for a in ref.authors]
    if _initials_needed(ref):
        fam[0] = f"{ref.authors[0][1]} {fam[0]}"
    if len(fam) == 1:
        return fam[0]
    if len(fam) == 2:
        return f"{fam[0]} & {fam[1]}"
    if n >= len(fam):
        return ", ".join(fam[:-1]) + ", & " + fam[-1]
    if n == 1:
        return f"{fam[0]} et al."
    return ", ".join(fam[:n]) + ", et al."


def _in_text_authors(ref: Reference) -> str:
    """The APA in-text author string: one or two names in full, three or
    more as "First et al." — extended by as many names as it takes to
    tell apart works of the same year whose author LISTS differ but
    shorten to the same form (§8.18). No author: the title (§8.14)."""
    if not ref.authors:
        return ref.in_text_title or ref.title
    if len(ref.authors) < 3:
        return _short_authors(ref, len(ref.authors))
    rivals = [r for r in BIBLIOGRAPHY.values()
              if r is not ref and r.year == ref.year and len(r.authors) >= 3
              and r.authors != ref.authors]
    n = 1
    while n < len(ref.authors) and any(
        _short_authors(r, n) == _short_authors(ref, n) for r in rivals
    ):
        n += 1
    return _short_authors(ref, n)


def year_label(ref: Reference) -> str:
    """The year with an APA ``a``/``b`` suffix — only for works with the
    IDENTICAL author list and year, lettered by title (§8.19)."""
    same = sorted(
        (r for r in BIBLIOGRAPHY.values() if r.year == ref.year and r.authors == ref.authors),
        key=lambda r: _fold(r.title),
    )
    if len(same) <= 1:
        return ref.year
    suffix = "abcdefghijklmnopqrstuvwxyz"[same.index(ref)]
    return f"{ref.year}-{suffix}" if ref.year == "n.d." else ref.year + suffix


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
    if style == "sentinel":  # internal: italics marked by \x01 … \x02
        return (lambda s: f"\x01{s}\x02"), (lambda s: s)
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
    return tuple(sorted(refs.values(), key=_ref_sort_key))


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
    """Brace every word that carries a capital — the first word, the word
    after a colon and every proper noun (Courant, Lie, Pre-metric-Bourbaki,
    M-theory, Drinfel’d …) — so biblatex-apa's sentence casing can change
    none of them."""
    import re

    out = []
    for w in title.split(" "):
        if any(c.isupper() for c in w):
            core = w.rstrip(":,.;")
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
    if ref.year != "n.d.":
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
