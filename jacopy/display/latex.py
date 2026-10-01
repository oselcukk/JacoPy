r"""
LaTeX renderer for :class:`~jacopy.core.expr.Expr` trees,
:class:`~jacopy.proof.step.ProofStep` / :class:`~jacopy.proof.chain.ProofChain`
transcripts and :class:`~jacopy.proof.theorems.Theorem` records
(PDF item 1, "integrated with LaTeX"; ported from v2's dispatch-based
display layer, 2026-09-22).

The output is raw LaTeX math, no ``$…$`` delimiters, so the caller
chooses the surrounding environment. :func:`chain_to_latex` wraps a
chain in a ``gather*`` body; individual expressions come out as
snippets ready to splice into equations or ``\text{…}`` arguments.

Dispatch is MRO-based: the most specific registered class for
``type(expr)`` wins, so :class:`~jacopy.algebra.derivation.Derivation`
subclasses without a dedicated handler fall through to the generic
name-based one. Handlers for the domain packages (Poisson, metric-
affine, algebroid, generalized) are registered lazily on first use,
so ``import jacopy.display`` stays cheap and the display layer never
forces the package import graph.

Name sanitising (:func:`latex_name`) translates the Unicode glyphs
the code base uses in operator names (``ι_X``, ``ω₂``, ``ℒ̃``, ``⊛``,
``Π₃``) into standard LaTeX commands and braces multi-character and
nested subscripts, so the result is pdfLaTeX-safe.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, Type

from jacopy.core.expr import (
    Expr,
    Integer,
    Neg,
    Power,
    Product,
    Rational,
    Sum,
    Symbol,
)
from jacopy.proof.chain import ProofChain
from jacopy.proof.step import ProofStep
from jacopy.proof.theorems import Theorem


# --------------------------------------------------------------------- #
# Name sanitising                                                        #
# --------------------------------------------------------------------- #


_UNICODE_TO_LATEX: Dict[str, str] = {
    # lowercase Greek
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu",
    "ν": r"\nu", "ξ": r"\xi", "π": r"\pi", "ρ": r"\rho",
    "σ": r"\sigma", "τ": r"\tau", "υ": r"\upsilon", "φ": r"\phi",
    "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
    # uppercase Greek
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Υ": r"\Upsilon",
    "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega",
    # script / blackboard letters used as operator names
    "ℒ": r"\mathcal{L}", "𝒦": r"\mathcal{K}", "𝒟": r"\mathcal{D}",
    "𝒫": r"\mathcal{P}", "ℝ": r"\mathbb{R}", "ħ": r"\hbar",
    "𝔻": r"\mathbb{D}", "𝕃": r"\mathbb{L}", "𝔛": r"\mathfrak{X}",
    "𝔤": r"\mathfrak{g}", "ℓ": r"\ell",
    # musical / algebraic
    "♭": r"\flat", "♯": r"\sharp",
    "∧": r"\wedge", "∨": r"\vee", "⋆": r"\star", "⊛": r"\circledast",
    "∘": r"\circ", "⊕": r"\oplus", "⊗": r"\otimes",
    "·": r"\cdot", "∇": r"\nabla", "∂": r"\partial",
    "⟨": r"\langle", "⟩": r"\rangle",
    "∞": r"\infty", "∈": r"\in",
    "′": "'",
    # arrows / ellipsis / Unicode minus that surface in rule names
    "−": "-",
    "→": r"\to",
    "←": r"\leftarrow",
    "↔": r"\leftrightarrow",
    "↦": r"\mapsto",
    "⇒": r"\Rightarrow",
    "⟹": r"\Longrightarrow",
    "⟺": r"\Longleftrightarrow",
    "⇔": r"\Leftrightarrow",
    "…": r"\dots", "⋯": r"\cdots",
    "≤": r"\leq", "≥": r"\geq", "≠": r"\neq",
    "±": r"\pm", "×": r"\times", "÷": r"\div",
    # further glyphs that occur in rule names / statements (audit
    # 0b00e1b-FULL K1-9, T3-2): every one maps to a math command
    "ϕ": r"\phi", "ϵ": r"\epsilon", "ϑ": r"\vartheta", "ϖ": r"\varpi",
    "µ": r"\mu", "ð": r"\eth",
    "⊂": r"\subset", "⊆": r"\subseteq", "⊃": r"\supset", "∉": r"\notin",
    "∀": r"\forall", "∃": r"\exists", "¬": r"\neg",
    "≡": r"\equiv", "≈": r"\approx", "≅": r"\cong", "∼": r"\sim", "≃": r"\simeq",
    "∪": r"\cup", "∩": r"\cap", "∅": r"\emptyset", "∖": r"\setminus",
    "∑": r"\sum", "∏": r"\prod", "∫": r"\int", "√": r"\surd",
    "⊥": r"\perp", "∥": r"\parallel", "†": r"\dagger", "⋅": r"\cdot",
    "∗": r"\ast", "⊙": r"\odot", "⊖": r"\ominus", "⊞": r"\boxplus",
    "⊠": r"\boxtimes", "⋊": r"\rtimes", "⋉": r"\ltimes", "⊲": r"\triangleleft",
    "⟦": r"[\![", "⟧": r"]\!]", "⌊": r"\lfloor", "⌋": r"\rfloor",
    "⇐": r"\Leftarrow", "⟵": r"\longleftarrow", "⟶": r"\longrightarrow",
    "↪": r"\hookrightarrow", "↠": r"\twoheadrightarrow", "↑": r"\uparrow", "↓": r"\downarrow",
    "ℏ": r"\hbar", "ℓ": r"\ell", "℘": r"\wp", "ℑ": r"\Im", "ℜ": r"\Re",
    "ℂ": r"\mathbb{C}", "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}", "ℚ": r"\mathbb{Q}",
    "ℋ": r"\mathcal{H}", "ℐ": r"\mathcal{I}", "ℛ": r"\mathcal{R}", "ℬ": r"\mathcal{B}",
    "ℰ": r"\mathcal{E}", "ℱ": r"\mathcal{F}", "ℳ": r"\mathcal{M}",
    "ℭ": r"\mathfrak{C}", "ℌ": r"\mathfrak{H}", "ℨ": r"\mathfrak{Z}",
    "°": r"^{\circ}", "″": "''",
    "½": r"\tfrac{1}{2}", "⅓": r"\tfrac{1}{3}", "¼": r"\tfrac{1}{4}", "⅔": r"\tfrac{2}{3}",
    "¾": r"\tfrac{3}{4}",
    "•": r"\bullet", "§": r"\S", "⌟": r"\lrcorner", "⌞": r"\llcorner", "∓": r"\mp",
    "⟸": r"\Longleftarrow", "⟪": r"\langle\!\langle", "⟫": r"\rangle\!\rangle",
}

#: text-mode punctuation (never math)
_TEXT_PUNCT: Dict[str, str] = {
    "’": "'", "‘": "`", "“": "``", "”": "''", "–": "--", "—": "---",
    "\u00a0": "~", "\u202f": "\\,", "\u2009": "\\,",
}

_SUBSCRIPT_DIGITS = dict(zip("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
_SUPERSCRIPT_DIGITS = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"))
_SUB_RUN = re.compile("[₀₁₂₃₄₅₆₇₈₉]+")
_SUP_RUN = re.compile("[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+")

_MULTICHAR_SUB = re.compile(r"_(\w{2,})")

_COMBINING_TILDE_CHAR = "\u0303"
_COMBINING_DOT_CHAR = "\u0307"
_COMBINING_HAT_CHAR = "\u0302"
_MATH_COMBINING_TILDE_RE = re.compile(rf"([^_^{{}}\s\\])({_COMBINING_TILDE_CHAR})")
_MATH_COMBINING_DOT_RE = re.compile(rf"([^_^{{}}\s\\])({_COMBINING_DOT_CHAR})")
_MATH_COMBINING_HAT_RE = re.compile(rf"([^_^{{}}\s\\])({_COMBINING_HAT_CHAR})")


def _brace_nested_subscripts(name: str) -> str:
    """Wrap nested subscripts so pdfLaTeX doesn't see ``Base_a_b``:
    ``K_X_ι_U(μ)`` → ``K_{X_{ι_U(μ)}}``."""
    depth = 0
    positions: list[int] = []
    for i, c in enumerate(name):
        if c == "{":
            depth += 1
        elif c == "}":
            depth = max(0, depth - 1)
        elif c == "_" and depth == 0:
            positions.append(i)
    if len(positions) < 2:
        return name
    first = positions[0]
    inner = _brace_nested_subscripts(name[first + 1 :])
    return name[: first + 1] + "{" + inner + "}"


def _scripts(name: str) -> str:
    """Unicode sub/superscript digit runs → ``_{…}`` / ``^{…}``."""
    name = _SUB_RUN.sub(
        lambda m: "_{" + "".join(_SUBSCRIPT_DIGITS[c] for c in m.group(0)) + "}",
        name,
    )
    name = _SUP_RUN.sub(
        lambda m: "^{"
        + "".join(
            "-" if c == "⁻" else _SUPERSCRIPT_DIGITS[c] for c in m.group(0)
        )
        + "}",
        name,
    )
    return name


def latex_name(name: str) -> str:
    """Translate a Derivation/Symbol display name into a LaTeX snippet.

    Collapses combining diacritics (``K̃`` → ``\\tilde{K}``, ``Π̂`` →
    ``\\hat{\\Pi}``), converts Unicode sub/superscript digits
    (``ω₂`` → ``\\omega_{2}``, ``Ψ⁻¹`` → ``\\Psi^{-1}``), braces nested
    subscripts, replaces Unicode math glyphs with LaTeX commands, and
    braces multi-character subscripts (``X_ab`` → ``X_{ab}``).
    """
    if not isinstance(name, str):
        raise TypeError("latex_name: expected a str")
    name = _MATH_COMBINING_TILDE_RE.sub(
        lambda m: "\\tilde{" + m.group(1) + "}", name
    )
    name = _MATH_COMBINING_DOT_RE.sub(
        lambda m: "\\dot{" + m.group(1) + "}", name
    )
    name = _MATH_COMBINING_HAT_RE.sub(
        lambda m: "\\hat{" + m.group(1) + "}", name
    )
    name = _script_letters(name)
    name = _scripts(name)
    name = _brace_nested_subscripts(name)
    name = _glyphs(name)
    name = _MULTICHAR_SUB.sub(lambda m: "_{" + m.group(1) + "}", name)
    return _fix_scripts(_math_fallback(name))


def _take_group(s: str, i: int):
    """``(group text, end)`` for the brace group opening at ``s[i]``."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "\\":
            continue
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i : j + 1], j + 1
    return s[i:] + "}" * depth, len(s)


def _fix_scripts(s: str) -> str:
    """Make every sub/superscript well formed (audit review: no input
    may yield LaTeX that does not compile): a script with no argument
    gets ``{}``, a script whose argument is itself a script is braced
    (``x^_{i}`` → ``x^{_{i}}``), a second ``_`` (``^``) on the same base
    gets an empty base ``{}`` first (``x_{i}_j`` → ``x_{i}{}_j``)."""
    out: list[str] = []
    have: set = set()
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "_^":
            if c in have:
                out.append("{}")
                have = set()
            have.add(c)
            out.append(c)
            i += 1
            while i < n and s[i] == " ":
                i += 1
            if i >= n:
                out.append("{}")
                break
            if s[i] in "_^":
                # the argument is a script itself: brace it with its own argument
                j = i + 1
                if j < n and s[j] == "{":
                    grp, j = _take_group(s, j)
                elif j < n and s[j] == "\\":
                    m = _CMD_ARG_RE.match(s, j)
                    grp, j = m.group(0), m.end()
                elif j < n:
                    grp, j = s[j], j + 1
                else:
                    grp = "{}"
                out.append("{" + s[i] + _fix_scripts(grp) + "}")
                i = j
            elif s[i] == "{":
                grp, i = _take_group(s, i)
                out.append("{" + _fix_scripts(grp[1:-1]) + "}")
            elif s[i] == "\\":
                # braced: a macro like \\notin is not a valid bare script
                m = _CMD_ARG_RE.match(s, i)
                out.append("{" + m.group(0) + "}")
                i = m.end()
            elif s[i] == "'":
                out.append("{'}")
                i += 1
            elif s[i] == "}":
                out.append("{}")
            else:
                out.append(s[i])
                i += 1
            continue
        if c == "{":
            grp, i = _take_group(s, i)
            out.append("{" + _fix_scripts(grp[1:-1]) + "}")
            have = set()
            continue
        if c == "\\":
            m = _CMD_ARG_RE.match(s, i)
            out.append(m.group(0))
            i = m.end()
            have = set()
            continue
        if c == "'":
            # a prime IS a superscript: after one, start a new base
            if "^" in have and not (out and out[-1] == "'"):
                out.append("{}")
            out.append(c)
            have = {"'", "^"}  # a prime is a superscript (x'^2 is not x^{\prime}^2 …)
            i += 1
            continue
        if c != " ":
            have = set()
        out.append(c)
        i += 1
    return "".join(out)


#: a command with its brace argument(s) (``\\mathcal{L}``, ``\\tfrac{1}{2}``)
_CMD_ARG_RE = re.compile(r"\\(?:[A-Za-z]+|.)(?:\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})*")


#: combining marks of PRECOMPOSED letters (NFD) → text-mode accents
_TEXT_ACCENTS = {
    "̀": "\\`", "́": "\\'", "̂": "\\^", "̃": "\\~",
    "̄": "\\=", "̆": "\\u", "̇": "\\.", "̈": '\\"',
    "̊": "\\r", "̋": "\\H", "̌": "\\v", "̧": "\\c",
    "̨": "\\k",
}

_TEXT_SPECIAL_LETTERS = {
    "ı": r"{\i}", "ß": r"{\ss}", "ø": r"{\o}", "Ø": r"{\O}", "æ": r"{\ae}",
    "Æ": r"{\AE}", "œ": r"{\oe}", "Œ": r"{\OE}", "ł": r"{\l}", "Ł": r"{\L}",
    "å": r"{\aa}", "Å": r"{\AA}",
}


def _math_char(ch: str):
    """LaTeX MATH for one non-ASCII character, or ``None`` when no
    rule applies. Table first, then Unicode-name heuristics: sub- and
    superscript letters (``ᵢ`` → ``_{i}``, ``ᴸ`` → ``^{L}``) and the
    mathematical alphanumerics (``𝔖`` → ``\\mathfrak{S}``)."""
    import unicodedata

    if ch in _UNICODE_TO_LATEX:
        return _UNICODE_TO_LATEX[ch]
    try:
        uname = unicodedata.name(ch)
    except ValueError:
        return None
    base = unicodedata.normalize("NFKC", ch)
    if base == ch:
        return None
    if base.isascii() and base.isprintable():
        inner = base
    elif len(base) == 1 and base in _UNICODE_TO_LATEX:
        inner = _UNICODE_TO_LATEX[base]  # 𝜔 → ω → \omega
    else:
        return None
    if "SUBSCRIPT" in uname:
        return "_{" + inner + "}"
    if "SUPERSCRIPT" in uname or uname.startswith("MODIFIER LETTER"):
        return "^{" + inner + "}"
    if "FRAKTUR" in uname or "BLACK-LETTER" in uname:
        return r"\mathfrak{" + inner + "}"
    if "DOUBLE-STRUCK" in uname:
        return r"\mathbb{" + inner + "}"
    if "SCRIPT" in uname:
        return r"\mathcal{" + inner + "}"
    if "BOLD" in uname:
        return r"\mathbf{" + inner + "}"
    if "SANS-SERIF" in uname:
        return r"\mathsf{" + inner + "}"
    if "MONOSPACE" in uname:
        return r"\mathtt{" + inner + "}"
    if uname.startswith(("MATHEMATICAL", "FULLWIDTH")):
        return inner
    return None


def _warn_unmapped(ch: str) -> None:
    import warnings

    warnings.warn(
        f"jacopy.display.latex: no LaTeX mapping for {ch!r} (U+{ord(ch):04X}); rendered as '?'",
        stacklevel=4,
    )


def _math_fallback(text: str) -> str:
    """Map every remaining non-ASCII character of a MATH snippet; an
    unknown one becomes a visible ``?`` (and a warning) instead of a
    pdfLaTeX error (audit 0b00e1b-FULL K1-9)."""
    if text.isascii():
        return text
    out = []
    for ch in text:
        if ch.isascii():
            out.append(ch)
            continue
        m = _math_char(ch)
        if m is None:
            _warn_unmapped(ch)
            m = r"\text{?}"
        if m[-1].isalpha():
            m += " "  # never glue a command to a following letter
        out.append(m)
    return "".join(out)


def _text_char(ch: str) -> str:
    """LaTeX TEXT for one non-ASCII character: punctuation, accented
    letters (``ğ`` → ``\\u{g}``), math glyphs lifted with
    ``\\ensuremath``; unknown ones become a visible ``?``."""
    import unicodedata

    if ch in _TEXT_PUNCT:
        return _TEXT_PUNCT[ch]
    if ch in _TEXT_SPECIAL_LETTERS:
        return _TEXT_SPECIAL_LETTERS[ch]
    if ch in _TEXT_ACCENTS:  # a combining mark with no base letter
        return _TEXT_ACCENTS[ch] + "{}"
    m = _math_char(ch)
    if m is not None:
        return f"\\ensuremath{{{m}}}"
    nfd = unicodedata.normalize("NFD", ch)
    if len(nfd) >= 2 and nfd[0].isascii() and all(c in _TEXT_ACCENTS for c in nfd[1:]):
        out = nfd[0]
        for mark in nfd[1:]:
            out = f"{_TEXT_ACCENTS[mark]}{{{out}}}"
        return out
    _warn_unmapped(ch)
    return r"\textbf{?}"


def _script_letters(name: str) -> str:
    """Unicode sub/superscript LETTERS (``ᵢ``, ``ₐ``, ``ᴸ``, ``ᵍ``) →
    ``_{i}`` / ``^{L}``; directly after an explicit ``_`` / ``^`` only
    the letter is kept (``T_ᵢ`` → ``T_i``, never a double script)."""
    if name.isascii():
        return name
    import unicodedata

    out: list[str] = []
    for ch in name:
        if ch.isascii() or ch in _SUBSCRIPT_DIGITS or ch in _SUPERSCRIPT_DIGITS or ch == "⁻":
            out.append(ch)
            continue
        m = _math_char(ch)
        if m and m[:2] in ("_{", "^{") and ch not in _UNICODE_TO_LATEX:
            if out and out[-1] == m[0]:
                out.append(m[2:-1])
            elif out and out[-1].startswith(m[:2]) and out[-1].endswith("}"):
                out[-1] = out[-1][:-1] + m[2:]  # ᵢⱼ → _{ij}
            else:
                out.append(m)
        else:
            out.append(ch)
    return "".join(out)


def _glyphs(name: str) -> str:
    """Replace Unicode math glyphs by LaTeX commands, inserting a
    separating space only where a command would otherwise swallow a
    following letter (``\\omega X`` yes, ``\\omega}`` / ``\\omega_`` no)."""
    for glyph, cmd in _UNICODE_TO_LATEX.items():
        if glyph not in name:
            continue
        spaced = cmd[-1].isalpha()
        if spaced:
            name = re.sub(re.escape(glyph) + r"(?=[A-Za-z])", lambda m, c=cmd: c + " ", name)
        name = name.replace(glyph, cmd)
    return name


# --------------------------------------------------------------------- #
# Dispatch                                                              #
# --------------------------------------------------------------------- #


_P_ATOM = 100
_P_CALL = 90
_P_POWER = 80
_P_PRODUCT = 60
_P_WEDGE = 55
_P_NEG = 50
_P_SUM = 40


Handler = Callable[[Expr, int], str]
_HANDLERS: Dict[Type[Expr], Handler] = {}
_PACKAGE_HANDLERS_LOADED = False


def register(cls: Type[Expr]):
    """Decorator: register a LaTeX handler ``fn(expr, ctx_precedence)``
    for ``cls`` (public, so user-defined nodes can plug in)."""

    def decorator(fn: Handler) -> Handler:
        _HANDLERS[cls] = fn
        return fn

    return decorator


_register = register


def to_latex(expr: Expr, ctx_precedence: int = 0) -> str:
    """Render ``expr`` as a LaTeX math snippet (no ``$`` delimiters)."""
    if not isinstance(expr, Expr):
        raise TypeError("to_latex: expected an Expr")
    _load_package_handlers()
    for cls in type(expr).__mro__:
        h = _HANDLERS.get(cls)
        if h is not None:
            return h(expr, ctx_precedence)
    return _name_with_slots(expr)


def _name_with_slots(expr: Expr) -> str:
    """Fallback for name-carrying nodes: the display name with every
    rewritable slot's own repr replaced by that slot's LaTeX (so
    ``L^R_U(r)`` renders its ``U`` and ``r`` structurally, and a slot
    landing in a sub/superscript is braced)."""
    name = getattr(expr, "name", None) or expr._repr_inner()
    slots = tuple(getattr(expr, "rewritable_slots", ()) or ())
    tokens = []
    for i, slot in enumerate(slots):
        inner = slot._repr_inner()
        if inner and inner in name:
            token = f"\x00{i}\x00"
            name = name.replace(inner, token, 1)
            tokens.append((token, slot))
    out = latex_name(name)
    for token, slot in tokens:
        pos = out.find(token)
        rendered = to_latex(slot, 0)
        if pos > 0 and out[pos - 1] in "_^":
            rendered = "{" + rendered + "}"
        out = out.replace(token, rendered, 1)
    return out


def _wrap(text: str, own_prec: int, ctx_prec: int) -> str:
    if own_prec < ctx_prec:
        return f"\\left({text}\\right)"
    return text


def section_to_latex(section) -> str:
    """A :class:`~jacopy.research.sections.GeneralizedSection`
    ``U ⊕ ω₂ ⊕ ω₅`` as one ``\\oplus``-joined snippet (each component
    rendered through :func:`to_latex`)."""
    from jacopy.research.sections import GeneralizedSection

    if not isinstance(section, GeneralizedSection):
        raise TypeError("section_to_latex: expected a GeneralizedSection")
    return " \\oplus ".join(to_latex(c, _P_SUM + 1) for c in section.components)


def _call(head: str, *args: Expr) -> str:
    arglist = ",\\, ".join(to_latex(a, 0) for a in args)
    return f"{head}\\!\\left({arglist}\\right)"


# --------------------------------------------------------------------- #
# Core expression types                                                 #
# --------------------------------------------------------------------- #


@_register(Symbol)
def _sym(expr: Symbol, _ctx: int) -> str:
    return latex_name(expr.name)


@_register(Integer)
def _int(expr: Integer, ctx: int) -> str:
    v = expr.value
    if v < 0:
        return _wrap(str(v), _P_NEG, ctx)
    return str(v)


@_register(Rational)
def _rat(expr: Rational, ctx: int) -> str:
    p, q = expr.p, expr.q
    if p < 0:
        return _wrap(f"-\\frac{{{-p}}}{{{q}}}", _P_NEG, ctx)
    return f"\\frac{{{p}}}{{{q}}}"


@_register(Neg)
def _neg(expr: Neg, ctx: int) -> str:
    inner = to_latex(expr.arg, _P_NEG + 1)
    return _wrap(f"-{inner}", _P_NEG, ctx)


@_register(Sum)
def _sum(expr: Sum, ctx: int) -> str:
    parts: list[str] = []
    for i, child in enumerate(expr.children):
        if isinstance(child, Neg):
            inner = to_latex(child.arg, _P_NEG + 1)
            parts.append(("- " if i > 0 else "-") + inner)
        else:
            rendered = to_latex(child, _P_SUM + 1)
            parts.append(("+ " if i > 0 else "") + rendered)
    text = " ".join(parts) if len(parts) > 1 else parts[0] if parts else "0"
    return _wrap(text, _P_SUM, ctx)


@_register(Product)
def _prod(expr: Product, ctx: int) -> str:
    parts = [to_latex(c, _P_PRODUCT + 1) for c in expr.children]
    text = " \\, ".join(parts) if parts else "1"
    return _wrap(text, _P_PRODUCT, ctx)


@_register(Power)
def _pow(expr: Power, ctx: int) -> str:
    base = to_latex(expr.base, _P_POWER + 1)
    exp = to_latex(expr.exp, 0)
    return _wrap(f"{{{base}}}^{{{exp}}}", _P_POWER, ctx)


def _load_core_handlers() -> None:
    from jacopy.algebra.commutator import Commutator
    from jacopy.algebra.derivation import Act, Derivation
    from jacopy.algebra.lie_bracket_vf import LieBracketVF
    from jacopy.brackets.base import BracketApply
    from jacopy.core.hodge import HodgeStar
    from jacopy.core.indexed_sum import IndexedSum
    from jacopy.core.multi_eval import MultiEval
    from jacopy.core.pairing import Pairing
    from jacopy.central.objects.partial_eval import PartialEval
    from jacopy.core.symmetrize import Antisymmetrization, Symmetrization
    from jacopy.core.tensor_product import TensorProduct
    from jacopy.core.wedge import Wedge
    from jacopy.core.wildcards import SeqWildcard, Wildcard

    @_register(Wedge)
    def _wedge(expr, ctx):
        parts = [to_latex(c, _P_WEDGE + 1) for c in expr.children]
        return _wrap(" \\wedge ".join(parts), _P_WEDGE, ctx)

    @_register(TensorProduct)
    def _tp(expr, ctx):
        parts = [to_latex(c, _P_WEDGE + 1) for c in expr.children]
        return _wrap(" \\otimes ".join(parts), _P_WEDGE, ctx)

    @_register(Symmetrization)
    def _symm(expr, _ctx):
        return _call("\\operatorname{Sym}", expr.arg)

    @_register(Antisymmetrization)
    def _alt(expr, _ctx):
        return _call("\\operatorname{Alt}", expr.arg)

    @_register(HodgeStar)
    def _hodge(expr, ctx):
        star = "\\star"
        if expr.metric is not None:
            star = f"\\star_{{{to_latex(expr.metric, 0)}}}"
        return _wrap(f"{star} {to_latex(expr.arg, _P_CALL)}", _P_CALL, ctx)

    @_register(IndexedSum)
    def _isum(expr, ctx):
        dummy = to_latex(expr.dummy, 0)
        rng = getattr(expr.range_, "name", None)
        sub = f"{dummy} \\in {latex_name(rng)}" if rng else dummy
        body = to_latex(expr.body, _P_SUM + 1)
        return _wrap(f"\\sum_{{{sub}}} {body}", _P_SUM, ctx)

    @_register(PartialEval)
    def _partial(expr, ctx):
        fixed = dict(expr.fixed)
        slots = ",\\, ".join(
            to_latex(fixed[i], 0) if i in fixed else "\\cdot" for i in range(expr.arity)
        )
        head = to_latex(expr.head, _P_CALL + 1)
        return _wrap(f"{head}\\!\\left({slots}\\right)", _P_CALL, ctx)

    @_register(Pairing)
    def _pairing(expr, _ctx):
        return f"\\langle {to_latex(expr.alpha, 0)},\\, {to_latex(expr.X, 0)} \\rangle"

    @_register(MultiEval)
    def _multi_eval(expr, ctx):
        head = to_latex(expr.head, _P_CALL + 1)
        return _wrap(_call(head, *expr.args), _P_CALL, ctx)

    @_register(Wildcard)
    def _wild(expr, _ctx):
        return f"\\mathord{{?}}{latex_name(expr.name)}"

    @_register(SeqWildcard)
    def _seqwild(expr, _ctx):
        return f"\\mathord{{?\\ast}}{latex_name(expr.name)}"

    @_register(Derivation)
    def _deriv(expr, _ctx):
        return _name_with_slots(expr)

    @_register(Act)
    def _act(expr, ctx):
        op = to_latex(expr.op, _P_CALL + 1)
        return _wrap(_call(op, expr.arg), _P_CALL, ctx)

    @_register(Commutator)
    def _comm(expr, _ctx):
        return f"\\left[{to_latex(expr.a, 0)},\\, {to_latex(expr.b, 0)}\\right]"

    @_register(LieBracketVF)
    def _lie_vf(expr, _ctx):
        return f"\\left[{to_latex(expr.X, 0)},\\, {to_latex(expr.Y, 0)}\\right]"

    @_register(BracketApply)
    def _bracket_apply(expr, _ctx):
        tag = latex_name(expr.bracket.name)
        return (
            f"\\left[{to_latex(expr.a, 0)},\\, {to_latex(expr.b, 0)}\\right]"
            f"_{{{tag}}}"
        )


def _load_central_handlers() -> None:
    from jacopy.central.algebroid.context import (
        AlgebroidBracket,
        AnchoredVF,
        CoboundaryForm,
        EMetric,
        LocalityOperator,
        MetricSharp,
    )
    from jacopy.central.algebroid.operators import (
        Derivator,
        Jacobiator,
        MappedSection,
        Predator,
    )
    from jacopy.central.calculus.bracket_calculus import (
        ExteriorDerivative,
        LieDerivative,
    )
    from jacopy.central.objects.connection import CovariantOp
    from jacopy.central.objects.endomorphism import EndoForm, EndoVF
    from jacopy.central.objects.frame import (
        CoframeField,
        FrameField,
        KroneckerDelta,
    )
    from jacopy.central.objects.interior import Interior
    from jacopy.central.objects.metric import InverseMetric, Metric
    from jacopy.central.objects.multivector_interior import (
        MultivectorInterior,
    )
    from jacopy.central.objects.musical import Flat, Sharp
    from jacopy.central.objects.tilde_interior import TildeInterior
    from jacopy.central.tangent.anholonomy import AnholonomyCoefficient

    def _index(s) -> str:
        inner = getattr(s, "_repr_inner", None)
        return latex_name(inner() if callable(inner) else str(s))

    @_register(Interior)
    def _iota(expr, _ctx):
        return f"\\iota_{{{to_latex(expr.vector, 0)}}}"

    @_register(TildeInterior)
    def _tilde_iota(expr, _ctx):
        return f"\\tilde{{\\iota}}_{{{to_latex(expr.form, 0)}}}"

    @_register(MultivectorInterior)
    def _mv_iota(expr, _ctx):
        return f"\\iota_{{{to_latex(expr.multivector, 0)}}}"

    @_register(LieDerivative)
    def _lie(expr, _ctx):
        op_name = getattr(expr, "_op_name", "L")
        head = "\\tilde{\\mathcal{L}}" if _COMBINING_TILDE_CHAR in op_name else "\\mathcal{L}"
        if op_name not in ("L", "L" + _COMBINING_TILDE_CHAR, "ℒ", "ℒ" + _COMBINING_TILDE_CHAR):
            head = latex_name(op_name)
        return f"{head}_{{{to_latex(expr.vector, 0)}}}"

    @_register(ExteriorDerivative)
    def _d(expr, _ctx):
        return latex_name(expr.name)

    @_register(CovariantOp)
    def _nabla(expr, _ctx):
        head = latex_name(expr.connection_name) if expr.connection_name != "∇" else "\\nabla"
        return f"{head}_{{{to_latex(expr.vector, 0)}}}"

    @_register(EndoVF)
    def _endo_vf(expr, _ctx):
        head = latex_name(expr.endo_name) + ("^{-1}" if expr.inverted else "")
        return _call(head, expr.arg)

    @_register(EndoForm)
    def _endo_form(expr, _ctx):
        head = "\\tilde{" + latex_name(expr.endo_name) + "}" + ("^{-1}" if expr.inverted else "")
        return _call(head, expr.arg)

    @_register(FrameField)
    def _frame(expr, _ctx):
        return f"{latex_name(expr.base_name)}_{{{_index(expr.index)}}}"

    @_register(CoframeField)
    def _coframe(expr, _ctx):
        return f"{latex_name(expr.base_name)}^{{{_index(expr.index)}}}"

    @_register(KroneckerDelta)
    def _delta(expr, _ctx):
        return f"\\delta^{{{_index(expr.upper)}}}_{{{_index(expr.lower)}}}"

    @_register(AnholonomyCoefficient)
    def _anhol(expr, _ctx):
        a, b = expr.lower
        head = "\\gamma" if expr.frame_name == "e" else f"\\gamma^{{({latex_name(expr.frame_name)})}}"
        return f"{head}^{{{_index(expr.upper)}}}_{{{_index(a)}{_index(b)}}}"

    @_register(Flat)
    def _flat(expr, _ctx):
        return f"{to_latex(expr.metric, _P_CALL + 1)}^{{\\flat}}"

    @_register(Sharp)
    def _musical_sharp(expr, _ctx):
        return f"{to_latex(expr.bivector, _P_CALL + 1)}^{{\\sharp}}"

    @_register(Metric)
    def _metric(expr, _ctx):
        return latex_name(expr.name)

    @_register(InverseMetric)
    def _inv_metric(expr, _ctx):
        # the default name already carries the ⁻¹ (``g⁻¹``); a custom
        # name is the user's choice — never add a second inverse
        # (2026-09-23 audit, F4: ``g^{-1}^{-1}`` is a pdflatex error)
        return latex_name(expr.name)

    @_register(AlgebroidBracket)
    def _alg_bracket(expr, _ctx):
        return (
            f"\\left[{to_latex(expr.u, 0)},\\, {to_latex(expr.v, 0)}\\right]"
            f"_{{{latex_name(expr.algebroid_name)}}}"
        )

    @_register(AnchoredVF)
    def _anchor(expr, _ctx):
        return _call("\\rho", expr.section)

    @_register(CoboundaryForm)
    def _cobound(expr, _ctx):
        return f"d_{{{latex_name(expr.algebroid_name)}}}{to_latex(expr.function, _P_CALL)}"

    @_register(EMetric)
    def _emetric(expr, _ctx):
        return _call(latex_name(expr.metric_name) + f"_{{{latex_name(expr.algebroid_name)}}}", expr.u, expr.v)

    @_register(MetricSharp)
    def _msharp(expr, _ctx):
        return _call(latex_name(expr.metric_name) + "^{-1}", expr.form)

    @_register(LocalityOperator)
    def _locality(expr, _ctx):
        return _call("L", expr.form, expr._u, expr._v)

    @_register(Jacobiator)
    def _jac(expr, _ctx):
        return _call(f"J_{{{latex_name(expr.algebroid_name)}}}", *expr.sections)

    @_register(Derivator)
    def _derivator(expr, _ctx):
        return _call(f"D_{{{latex_name(expr.map_name)}}}", *expr.sections)

    @_register(Predator)
    def _predator(expr, _ctx):
        return _call(f"P_{{{latex_name(expr.map_name)}}}", *expr.sections)

    @_register(MappedSection)
    def _mapped(expr, _ctx):
        return _call(latex_name(expr.map_name), expr.section)


def _load_package_handlers() -> None:
    """Register the domain-package handlers once (lazy: keeps
    ``import jacopy.display`` light and tolerates a package that fails
    to import — the generic name handler then applies)."""
    global _PACKAGE_HANDLERS_LOADED
    if _PACKAGE_HANDLERS_LOADED:
        return
    _PACKAGE_HANDLERS_LOADED = True
    _load_core_handlers()
    _load_central_handlers()
    try:
        _load_poisson_handlers()
    except ImportError:  # pragma: no cover
        pass
    try:
        _load_metric_affine_handlers()
    except ImportError:  # pragma: no cover
        pass
    try:
        _load_generalized_handlers()
    except ImportError:  # pragma: no cover
        pass


def _load_poisson_handlers() -> None:
    from jacopy.packages.poisson.core import (
        HamiltonianVF,
        PoissonBracketValue,
        SharpVF,
    )
    from jacopy.packages.poisson.koszul import KoszulBracket
    from jacopy.packages.poisson.nambu import NambuSharpVF
    from jacopy.packages.poisson.symplectic import SymplecticHamiltonianVF
    from jacopy.packages.poisson.tilde import TildeAnholonomyCoefficient

    @_register(SharpVF)
    def _sharp(expr, _ctx):
        return _call(f"{to_latex(expr.pi, _P_CALL + 1)}^{{\\sharp}}", expr.alpha)

    @_register(NambuSharpVF)
    def _nsharp(expr, _ctx):
        return _call(to_latex(expr.pi, _P_CALL + 1), expr.omega)

    @_register(HamiltonianVF)
    def _ham(expr, _ctx):
        return f"X_{{{to_latex(expr.f, 0)}}}"

    @_register(SymplecticHamiltonianVF)
    def _sham(expr, _ctx):
        return f"X_{{{to_latex(expr.f, 0)}}}"

    @_register(PoissonBracketValue)
    def _pbv(expr, _ctx):
        return f"\\{{{to_latex(expr.f, 0)},\\, {to_latex(expr.g, 0)}\\}}"

    @_register(KoszulBracket)
    def _koszul(expr, _ctx):
        return (
            f"\\left[{to_latex(expr.alpha, 0)},\\, {to_latex(expr.beta, 0)}\\right]"
            f"_{{{to_latex(expr.pi, 0)}}}"
        )

    @_register(TildeAnholonomyCoefficient)
    def _tanhol(expr, _ctx):
        up = "".join(latex_name(str(i)) for i in expr.upper)
        return f"\\tilde{{\\gamma}}_{{{latex_name(str(expr.lower))}}}^{{{up}}}"


def _load_metric_affine_handlers() -> None:
    from jacopy.packages.metric_affine.frame_components import (
        ConnectionCoefficient,
        ConnectionForm,
    )
    from jacopy.packages.metric_affine.metric import (
        InverseMetricComponent,
        MetricValue,
        NonMetricity,
    )
    from jacopy.packages.metric_affine.torsion_curvature import (
        Curvature,
        Torsion,
    )

    @_register(MetricValue)
    def _mval(expr, _ctx):
        return _call(latex_name(expr.metric_name), expr.X, expr.Y)

    @_register(InverseMetricComponent)
    def _invcomp(expr, _ctx):
        a, b = expr.upper
        return f"{latex_name(expr.metric_name)}^{{{latex_name(str(a))}{latex_name(str(b))}}}"

    @_register(NonMetricity)
    def _nonmet(expr, _ctx):
        return _call("Q", *expr.arguments)

    @_register(Torsion)
    def _torsion(expr, _ctx):
        return _call("T", *expr.arguments)

    @_register(Curvature)
    def _curv(expr, _ctx):
        X, Y, Z = expr.arguments
        return f"{_call('R', X, Y)}{to_latex(Z, _P_CALL)}"

    @_register(ConnectionCoefficient)
    def _gamma(expr, _ctx):
        a, b = expr.lower
        return (
            f"\\Gamma^{{{latex_name(str(expr.upper))}}}"
            f"_{{{latex_name(str(a))}{latex_name(str(b))}}}"
        )

    @_register(ConnectionForm)
    def _omega_ab(expr, _ctx):
        return (
            f"\\omega^{{{latex_name(str(expr.upper))}}}"
            f"_{{{latex_name(str(expr.lower))}}}"
        )


def _load_generalized_handlers() -> None:
    from jacopy.packages.generalized.courant_axioms import CourantD

    @_register(CourantD)
    def _courant_d(expr, _ctx):
        return f"\\mathcal{{D}}{to_latex(expr.function, _P_CALL)}"


# --------------------------------------------------------------------- #
# Proof transcript                                                      #
# --------------------------------------------------------------------- #


_COMBINING_TILDE_RE = re.compile(rf"(.)({_COMBINING_TILDE_CHAR})")
_COMBINING_DOT_RE = re.compile(rf"(.)({_COMBINING_DOT_CHAR})")
_COMBINING_HAT_RE = re.compile(rf"(.)({_COMBINING_HAT_CHAR})")


def _escape_text(text: str) -> str:
    """Escape LaTeX-special characters and lift Unicode math glyphs
    into ``\\ensuremath{…}`` so a ``\\text{…}`` argument built from a
    rule name or a theorem statement is pdfLaTeX-safe."""
    text = (
        text.replace("\\", "\x00")  # placeholder: escaped braces must not hit it
        .replace("_", r"\_")
        .replace("#", r"\#")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("$", r"\$")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("^", r"\^{}")
        .replace("~", r"\textasciitilde{}")
        .replace("<", r"\textless{}")
        .replace(">", r"\textgreater{}")
        .replace("\x00", r"\textbackslash{}")
    )
    text = _COMBINING_TILDE_RE.sub(
        lambda m: f"\\ensuremath{{\\tilde{{{m.group(1)}}}}}", text
    )
    text = _COMBINING_DOT_RE.sub(
        lambda m: f"\\ensuremath{{\\dot{{{m.group(1)}}}}}", text
    )
    text = _COMBINING_HAT_RE.sub(
        lambda m: f"\\ensuremath{{\\hat{{{m.group(1)}}}}}", text
    )
    text = _SUB_RUN.sub(
        lambda m: "\\ensuremath{_{"
        + "".join(_SUBSCRIPT_DIGITS[c] for c in m.group(0))
        + "}}",
        text,
    )
    text = _SUP_RUN.sub(
        lambda m: "\\ensuremath{^{"
        + "".join("-" if c == "⁻" else _SUPERSCRIPT_DIGITS[c] for c in m.group(0))
        + "}}",
        text,
    )
    for glyph, cmd in _UNICODE_TO_LATEX.items():
        if glyph in text:
            text = text.replace(glyph, f"\\ensuremath{{{cmd}}}")
    if not text.isascii():
        text = "".join(c if c.isascii() else _text_char(c) for c in text)
    return text


def text_to_latex(text: str) -> str:
    """Public: escape free text (a rule name, a statement, a citation)
    for LaTeX TEXT mode — special characters escaped, accented letters
    as accent commands, Unicode math glyphs as ``\\ensuremath{…}``.
    The result is pure ASCII and pdfLaTeX-safe."""
    if not isinstance(text, str):
        raise TypeError("text_to_latex: expected a str")
    return _escape_text(text)


# ---- line breaking (audit 0b00e1b-FULL T3-2) ----------------------- #

#: default line budget of a transcript row, in "visible units" (about
#: one glyph each; sub/superscripts count less) — calibrated against
#: pdfLaTeX's ``article`` text width at ``\small``
DEFAULT_WIDTH = 62

_CMD_RE = re.compile(r"\\([A-Za-z]+|.)")
_INVISIBLE_CMDS = {
    "left", "right", "bigl", "bigr", "Bigl", "Bigr", ",", "!", ";", ":", " ",
    "quad", "qquad", "mathcal", "mathbb", "mathfrak", "mathbf", "mathrm",
    "mathsf", "mathtt", "text", "operatorname", "tilde", "hat", "dot", "bar",
    "overline", "widetilde", "widehat", "ensuremath", "textit", "textbf",
}


def _visible_len(latex: str) -> float:
    """A rough width estimate of a LaTeX math snippet: commands count
    as one glyph (spacing / delimiter-sizing ones as none), braces as
    none, sub/superscript material as 0.7."""
    n = 0.0
    depth_script = 0
    i = 0
    stack: list[bool] = []
    script_next = False
    while i < len(latex):
        c = latex[i]
        if c == "\\":
            m = _CMD_RE.match(latex, i)
            name = m.group(1)
            i = m.end()
            if name not in _INVISIBLE_CMDS:
                n += 0.7 if depth_script else 1.0
            continue
        if c in "_^":
            script_next = True
            i += 1
            continue
        if c == "{":
            stack.append(script_next)
            if script_next:
                depth_script += 1
            script_next = False
            i += 1
            continue
        if c == "}":
            if stack and stack.pop():
                depth_script -= 1
            i += 1
            continue
        if c != " ":
            n += 0.7 if (depth_script or script_next) else 1.0
        script_next = False
        i += 1
    return n


def _pieces(expr: Expr, width: float) -> list[str]:
    """Break ``expr`` into pieces that may be set on separate lines:
    the summands of a top-level sum; a long parenthesised sum inside a
    summand (``f·(a + b + …)``, ``−(a + b + …)``) is opened up with
    ``\\bigl( … \\bigr)`` (which, unlike ``\\left/\\right``, may span
    lines)."""
    whole = to_latex(expr)
    if _visible_len(whole) <= width:
        return [whole]
    if isinstance(expr, Sum):
        out: list[str] = []
        for i, child in enumerate(expr.children):
            sign = ""
            body = child
            if isinstance(child, Neg):
                sign, body = ("- " if i > 0 else "-"), child.arg
            elif i > 0:
                sign = "+ "
            rendered = to_latex(body, (_P_NEG if sign.strip() == "-" else _P_SUM) + 1)
            if _visible_len(rendered) <= width:
                out.append(sign + rendered)
                continue
            sub = _open_up(body, width)
            if sub is None:
                out.append(sign + rendered)
            else:
                sub[0] = sign + sub[0]
                out.extend(sub)
        return out
    if isinstance(expr, Neg):
        sub = _open_up(expr.arg, width)
        if sub is not None:
            sub[0] = "-" + sub[0]
            return sub
    sub = _open_up(expr, width)
    return sub if sub is not None else [whole]


def _open_up(expr: Expr, width: float):
    """Pieces of a too-long non-sum term, or ``None`` if it cannot be
    opened: a sum is parenthesised with ``\\bigl(…\\bigr)``; a product
    with sum factors opens each long sum factor in place."""
    if isinstance(expr, Sum):
        inner = _pieces(expr, width)
        if len(inner) == 1:
            return None
        inner[0] = "\\bigl(" + inner[0]
        inner[-1] = inner[-1] + "\\bigr)"
        return inner
    if isinstance(expr, Product):
        out: list[str] = []
        prefix = ""
        opened = False
        for c in expr.children:
            r = to_latex(c, _P_PRODUCT + 1)
            if isinstance(c, Sum) and _visible_len(r) > width / 2:
                inner = _pieces(c, width)
                if len(inner) > 1:
                    inner[0] = prefix + "\\bigl(" + inner[0]
                    inner[-1] = inner[-1] + "\\bigr)"
                    out.extend(inner[:-1])
                    prefix = inner[-1] + " \\, "
                    opened = True
                    continue
            prefix += r + " \\, "
        if not opened:
            return None
        out.append(prefix[: -len(" \\, ")])
        return out
    return None


def _fill(pieces: list[str], width: float) -> list[str]:
    """Greedy line filling of breakable pieces."""
    lines: list[str] = []
    cur = ""
    for p in pieces:
        if cur and _visible_len(cur) + _visible_len(p) + 1 > width:
            lines.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}" if cur else p
    if cur:
        lines.append(cur)
    # a dangling \bigl( / \bigr) pair split over lines is balanced by
    # construction (each piece list opens and closes once)
    return lines


def math_lines(expr: Expr, width: float = DEFAULT_WIDTH) -> list[str]:
    """``expr`` rendered as LaTeX math, broken into lines of about
    ``width`` visible units at summand boundaries (public; used by the
    transcript renderers)."""
    if not isinstance(expr, Expr):
        raise TypeError("math_lines: expected an Expr")
    return _fill(_pieces(expr, width), width)


def _wrap_words(text: str, width: float) -> list[str]:
    """Split plain text into lines of about ``width`` characters at
    spaces (before escaping, so no command is cut)."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines or [""]


# ---- citations -------------------------------------------------------- #

#: in-text citation styles: ``"apa"`` prints the APA string (one
#: pdfLaTeX pass, no extra tools); ``"biblatex"`` emits
#: ``\parencite`` commands for ``biblatex`` + ``style=apa`` + biber
CITE_STYLES = ("apa", "biblatex")


def _bib_postnote(locator: str) -> str:
    # brackets in a biblatex postnote must be braced
    return text_to_latex(locator).replace("[", "{[}").replace("]", "{]}")


def cite_to_latex(source, style: str = "apa") -> str:
    """The in-text citation of a ``source`` (a
    :class:`~jacopy.bibliography.Citation` or a tuple of them) in TEXT
    mode: APA string, or biblatex ``\\parencites`` commands."""
    from jacopy.bibliography import as_citations, in_text

    if style not in CITE_STYLES:
        raise ValueError(f"cite style must be one of {CITE_STYLES}, got {style!r}")
    cits = as_citations(source)
    if not cits:
        return ""
    if style == "apa":
        return in_text(cits, "latex")
    return _parencites(cits)


def _parencites(cits) -> str:
    """ONE ``\\parencites`` group for all works of a source: works in APA
    order, the locators of one work merged into one postnote."""
    from jacopy.bibliography import BIBLIOGRAPHY, _ref_sort_key, apa_locator

    by_work: dict = {}
    for c in cits:
        locs = by_work.setdefault(c.key, [])
        if c.locator and c.locator not in locs:
            locs.append(c.locator)
    parts = []
    for k in sorted(by_work, key=lambda k: _ref_sort_key(BIBLIOGRAPHY[k])):
        note = ", ".join(apa_locator(l) for l in by_work[k])
        parts.append((f"[{_bib_postnote(note)}]" if note else "") + f"{{{k}}}")
    return "\\parencites" + "".join(parts)


#: line budget of TEXT rows (rule names, citations, justifications),
#: in characters at ``\\small`` on the default page
TEXT_WIDTH = 78


def _cite_rows(ind: str, label: str, source, style: str) -> list[str]:
    """Aligned TEXT rows ``label (Author, year, locator; …)`` wrapped at
    :data:`TEXT_WIDTH` (APA; an italic no-author title split across rows
    is closed and reopened), or one ``\\parencites`` row (biblatex)."""
    from jacopy.bibliography import as_citations, in_text

    cits = as_citations(source)
    if not cits:
        return []
    if style != "apa":
        return [f"&{ind}\\textit{{{_escape_text(label)} {cite_to_latex(cits, style)}}}"]
    # \x01 … \x02 mark italic (no-author) titles through wrapping and
    # escaping; a title split across rows is closed and reopened
    marked = in_text(cits, "sentinel")
    rows, open_it = [], False
    for line in _wrap_words(f"{label} {marked}", TEXT_WIDTH):
        out = ["\\textit{"] if open_it else []
        for ch in _escape_text(line):
            if ch == "\x01":
                out.append("\\textit{")
                open_it = True
            elif ch == "\x02":
                out.append("}")
                open_it = False
            else:
                out.append(ch)
        if open_it:
            out.append("}")
        rows.append(f"&{ind}\\text{{{''.join(out)}}}")
    return rows


def _sub_sources(step: ProofStep):
    from jacopy.bibliography import chain_sources

    return chain_sources(step.children)


# ---- steps, chains, theorems ------------------------------------------ #


def _step_rows(step: ProofStep, *, width: float, cite_style: str, depth: int, max_depth: int) -> list[str]:
    """The ``aligned`` rows of one step (and, up to ``max_depth``, of
    its sub-steps, indented)."""
    ind = "\\quad " * depth
    rows: list[str] = []
    tag = f" ({step.provenance_tag})" if step.provenance_tag else ""
    for line in _wrap_words(f"[{step.rule}]{tag}", TEXT_WIDTH):
        rows.append(f"&{ind}\\text{{{_escape_text(line)}}}")
    rows.extend(_cite_rows(ind, "Source:", step.source, cite_style))
    before = math_lines(step.before, width - 3 * depth)
    after = math_lines(step.after, width - 3 * depth)
    for k, line in enumerate(before):
        rows.append(f"&{ind}\\quad {line}" if k == 0 else f"&{ind}\\qquad {line}")
    for k, line in enumerate(after):
        rows.append(f"&{ind}\\to {line}" if k == 0 else f"&{ind}\\qquad {line}")
    just = step.justification or ""
    just_strip = just.removeprefix("apply axiom: ").removeprefix("apply theorem: ").removeprefix("apply ")
    if just and just_strip != step.rule:
        for line in _wrap_words(f"--- {just}", TEXT_WIDTH):
            rows.append(f"&{ind}\\textit{{{_escape_text(line)}}}")
    if step.children:
        if depth < max_depth:
            for ch in step.children:
                rows.extend(_step_rows(ch, width=width, cite_style=cite_style, depth=depth + 1, max_depth=max_depth))
        else:
            rows.extend(_cite_rows(ind, "Sub-steps cite:", _sub_sources(step), cite_style))
    return rows


def step_to_latex(
    step: ProofStep, *, width: float = DEFAULT_WIDTH, cite_style: str = "apa", max_depth: int = 0
) -> str:
    r"""Render a :class:`ProofStep` as an ``aligned`` block (math mode):
    the rule name and provenance tag (``\text{[rule] (axiom)}``), the
    literature source of the rule (APA in-text citation), ``before`` and
    ``\to after`` broken at summand boundaries into lines of about
    ``width`` visible units, and the justification. Sub-steps are shown
    indented up to ``max_depth``; deeper ones are summarised by the
    sources they cite."""
    if not isinstance(step, ProofStep):
        raise TypeError("step_to_latex: expected a ProofStep")
    rows = _step_rows(step, width=width, cite_style=cite_style, depth=0, max_depth=max_depth)
    return "\\begin{aligned}[t]\n" + " \\\\\n".join(rows) + "\n\\end{aligned}"


def chain_to_latex(
    chain: ProofChain,
    *,
    max_steps: int | None = None,
    width: float = DEFAULT_WIDTH,
    cite_style: str = "apa",
    max_depth: int = 0,
) -> str:
    r"""Render a :class:`ProofChain` as a ``gather*`` block, one
    :func:`step_to_latex` row per top-level step (page breaks allowed
    between steps). ``max_steps`` truncates long transcripts with an
    explicit ellipsis row; ``max_depth`` unfolds sub-proofs."""
    if not isinstance(chain, ProofChain):
        raise TypeError("chain_to_latex: expected a ProofChain")
    if len(chain) == 0:
        return "\\begin{gather*}\n\\text{(empty proof chain)}\n\\end{gather*}"
    steps = list(chain.steps)
    shown = steps if max_steps is None else steps[:max_steps]
    rows = [
        f"\\text{{\\textbf{{({i})}}}}\\ {step_to_latex(s, width=width, cite_style=cite_style, max_depth=max_depth)}"
        for i, s in enumerate(shown, 1)
    ]
    if max_steps is not None and len(steps) > max_steps:
        rows.append(f"\\vdots \\quad \\text{{({len(steps) - max_steps} more steps)}}")
    body = " \\\\[1ex]\n".join(rows)
    return (
        "{\\allowdisplaybreaks\\small\n"
        f"\\begin{{gather*}}\n{body}\n\\end{{gather*}}\n"
        "}"
    )


def theorem_to_latex(
    theorem: Theorem,
    *,
    with_proof: bool = True,
    max_steps: int | None = None,
    cite_style: str = "apa",
    max_depth: int = 0,
) -> str:
    r"""Render a :class:`Theorem` as a ``theorem``-style paragraph:
    the statement (escaped text) with the theorem's literature source,
    the proven equation ``lhs = rhs`` in display math (broken into
    lines when long), the assumptions it depends on, and (optionally)
    the proof transcript."""
    if not isinstance(theorem, Theorem):
        raise TypeError("theorem_to_latex: expected a Theorem")
    src = cite_to_latex(getattr(theorem, "source", None), cite_style)
    head = (
        f"\\paragraph{{Theorem ({_escape_text(theorem.name)}).}} "
        f"{_escape_text(theorem.statement)}"
    )
    if src:
        head += f" {src}"
    lhs = math_lines(theorem.lhs)
    rhs = math_lines(theorem.rhs)
    eq_rows = [f"&{l}" if k == 0 else f"&\\quad {l}" for k, l in enumerate(lhs)]
    eq_rows += [f"&= {r}" if k == 0 else f"&\\quad {r}" for k, r in enumerate(rhs)]
    lines = [
        head,
        "\\begin{align*}\n" + " \\\\\n".join(eq_rows) + "\n\\end{align*}",
        f"\\noindent\\textit{{Generality:}} {_escape_text(theorem.generality)}.",
    ]
    if theorem.from_axioms:
        items = "".join(f"\\item {_escape_text(a)}\n" for a in theorem.from_axioms)
        lines.append("\\noindent\\textit{Depends on:}\n\\begin{itemize}\n" + items + "\\end{itemize}")
    if theorem.notes:
        lines.append(f"\\noindent\\textit{{Notes:}} {_escape_text(theorem.notes)}")
    if with_proof:
        lines.append("\\noindent\\textit{Proof.}")
        lines.append(chain_to_latex(theorem.proof, max_steps=max_steps, cite_style=cite_style, max_depth=max_depth))
    return "\n".join(lines)


# --------------------------------------------------------------------- #
# Standalone document export                                             #
# --------------------------------------------------------------------- #


_DEFAULT_PREAMBLE = (
    r"\usepackage[utf8]{inputenc}" "\n"
    r"\usepackage[T1]{fontenc}" "\n"
    r"\usepackage{amsmath}" "\n"
    r"\usepackage{amssymb}" "\n"
    r"\usepackage[margin=2.5cm]{geometry}" "\n"
)


#: how a document lists its references: ``"apa"`` (a ``References``
#: section typeset from :mod:`jacopy.bibliography`, one pdfLaTeX pass),
#: ``"biblatex"`` (an embedded ``.bib`` + ``biblatex``/``style=apa``;
#: needs pdflatex → biber → pdflatex), or ``None`` (no list)
REFERENCE_MODES = ("apa", "biblatex", None)


def references_to_latex(citations) -> str:
    """A ``References`` section (APA 7, hanging indent) for the works
    behind ``citations``; ``""`` when there are none."""
    from jacopy.bibliography import apa_reference, cited_references

    refs = cited_references(citations)
    if not refs:
        return ""
    items = "\n".join(f"\\par {apa_reference(r, 'latex')}" for r in refs)
    return (
        "\\section*{References}\n"
        "{\\setlength{\\parindent}{-2em}\\setlength{\\leftskip}{2em}\\raggedright\n"
        f"{items}\\par}}\n"
    )


def _document(
    body: str,
    *,
    title: str,
    author: str,
    preamble_extras: str,
    citations=(),
    references: str | None = "apa",
) -> str:
    if references not in REFERENCE_MODES:
        raise ValueError(f"references must be one of {REFERENCE_MODES}, got {references!r}")
    from jacopy.bibliography import bibtex_entries

    lines = [r"\documentclass{article}", _DEFAULT_PREAMBLE.rstrip()]
    if references == "biblatex" and citations:
        lines.append("\\begin{filecontents*}[overwrite]{\\jobname.bib}\n"
                     + bibtex_entries(citations) + "\\end{filecontents*}")
        lines.append(r"\usepackage[style=apa,backend=biber]{biblatex}")
        lines.append(r"\addbibresource{\jobname.bib}")
    if preamble_extras:
        lines.append(preamble_extras.rstrip())
    if title:
        lines.append(f"\\title{{{_escape_text(title)}}}")
    if author:
        lines.append(f"\\author{{{_escape_text(author)}}}")
    lines.append(r"\begin{document}")
    if title or author:
        lines.append(r"\maketitle")
    lines.append(body)
    if references == "apa" and citations:
        lines.append(references_to_latex(citations).rstrip())
    elif references == "biblatex" and citations:
        lines.append(r"\printbibliography")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


def _cite_style_for(references: str | None) -> str:
    return "biblatex" if references == "biblatex" else "apa"


def chain_to_latex_document(
    chain: ProofChain,
    *,
    title: str = "",
    author: str = "",
    preamble_extras: str = "",
    max_steps: int | None = None,
    references: str | None = "apa",
    max_depth: int = 0,
) -> str:
    r"""Wrap :func:`chain_to_latex` in a pdfLaTeX-ready ``article`` that
    ends with the reference list of every source the chain cites (sub-
    steps included). ``references="apa"`` (default) compiles in one
    pdfLaTeX run; ``"biblatex"`` uses ``biblatex-apa`` + biber."""
    if not isinstance(chain, ProofChain):
        raise TypeError("chain_to_latex_document: expected a ProofChain")
    from jacopy.bibliography import chain_sources

    return _document(
        chain_to_latex(chain, max_steps=max_steps, cite_style=_cite_style_for(references), max_depth=max_depth),
        title=title, author=author, preamble_extras=preamble_extras,
        citations=chain_sources(chain.steps), references=references,
    )


def theorem_to_latex_document(
    theorem: Theorem,
    *,
    author: str = "",
    preamble_extras: str = "",
    with_proof: bool = True,
    max_steps: int | None = None,
    references: str | None = "apa",
    max_depth: int = 0,
) -> str:
    r"""Wrap :func:`theorem_to_latex` in a pdfLaTeX-ready ``article``
    titled by the theorem's name, with its reference list."""
    if not isinstance(theorem, Theorem):
        raise TypeError("theorem_to_latex_document: expected a Theorem")
    from jacopy.bibliography import as_citations, chain_sources

    cits = as_citations(getattr(theorem, "source", None)) + (chain_sources(theorem.proof.steps) if with_proof else ())
    return _document(
        theorem_to_latex(theorem, with_proof=with_proof, max_steps=max_steps,
                         cite_style=_cite_style_for(references), max_depth=max_depth),
        title=theorem.name, author=author, preamble_extras=preamble_extras,
        citations=cits, references=references,
    )


# --------------------------------------------------------------------- #
# TikZ chain diagram                                                     #
# --------------------------------------------------------------------- #


def chain_to_tikz(chain: ProofChain, *, node_distance: str = "1.2cm") -> str:
    r"""Render a :class:`ProofChain` as a vertical TikZ diagram: boxed
    expression nodes joined by arrows labelled with the rule names."""
    if not isinstance(chain, ProofChain):
        raise TypeError("chain_to_tikz: expected a ProofChain")
    if len(chain) == 0:
        return (
            f"\\begin{{tikzpicture}}[node distance={node_distance}]\n"
            "\\node {(empty proof chain)};\n"
            "\\end{tikzpicture}"
        )
    lines = [f"\\begin{{tikzpicture}}[node distance={node_distance}]"]
    lines.append(f"\\node[draw, rectangle] (e0) {{${to_latex(chain.steps[0].before)}$}};")
    for i, step in enumerate(chain.steps):
        lines.append(
            f"\\node[draw, rectangle, below=of e{i}] (e{i + 1}) {{${to_latex(step.after)}$}};"
        )
    for i, step in enumerate(chain.steps):
        tag = f" ({step.provenance_tag})" if step.provenance_tag else ""
        rule = _escape_text(f"{step.rule}{tag}")
        lines.append(f"\\draw[->] (e{i}) -- node[right] {{\\small {rule}}} (e{i + 1});")
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)


def chain_to_tikz_document(
    chain: ProofChain,
    *,
    title: str = "",
    author: str = "",
    node_distance: str = "1.2cm",
) -> str:
    r"""Standalone ``article`` wrapper around :func:`chain_to_tikz`."""
    if not isinstance(chain, ProofChain):
        raise TypeError("chain_to_tikz_document: expected a ProofChain")
    body = "\\begin{center}\n" + chain_to_tikz(chain, node_distance=node_distance) + "\n\\end{center}"
    return _document(
        body,
        title=title,
        author=author,
        preamble_extras="\\usepackage{tikz}\n\\usetikzlibrary{positioning}",
    )
