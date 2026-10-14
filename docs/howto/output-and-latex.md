# Output: LaTeX, text, documents and citations

JacoPy renders expressions, proof chains and theorems as LaTeX, as plain text, in the
terminal and in Jupyter, and can write a complete LaTeX document for a theorem. It also
keeps an APA-style bibliography of the works its definitions come from. This page shows
the calls.

## Setup

```python
import jacopy
import jacopy.central.tangent as tg

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y = jacopy.vector_fields("X Y")
alpha, beta = jacopy.forms("alpha beta", degree=1)
(omega,) = jacopy.forms("omega", degree=2)

book = jacopy.TheoremBook()
tg.register_cartan_theorems(book, alpha, X, Y, f, registry=reg)

from jacopy.display.latex import chain_to_latex, theorem_to_latex
from jacopy.display.ascii import step_to_ascii, chain_to_ascii
import jacopy.bibliography as bib

expr = jacopy.lie_derivative(X)(omega)                           # an expression
chain = tg.prove_cartan_magic_on_functions(X, f, registry=reg)    # a proof chain
thm = book.get("cartan_magic_on_functions")                      # a theorem
```

There are two different functions called `cite`. {py:func}`jacopy.cite` adds a theorem to
an engine as a rule (see [Running proofs](running-proofs.md)); `jacopy.bibliography.cite`
builds a literature citation (below).

## Expressions

| Output | In code | Result |
|---|---|---|
| LaTeX string | `jacopy.to_latex(expr)` | `\mathcal{L}_{X}\!\left(\omega\right)` for $\mathcal L_X\omega$ |
| plain text | `jacopy.to_ascii(expr)` | `L_X(omega)` |
| print to the terminal | `jacopy.print_expr(expr)` | prints the text form |
| display object | `jacopy.display_expr(expr)` | rendered as math in Jupyter; a LaTeX string in the terminal |

```python
print(jacopy.to_latex(expr))
print(jacopy.to_ascii(expr))
jacopy.print_expr(expr)
print(jacopy.display_expr(expr))
```

```text
\mathcal{L}_{X}\!\left(\omega\right)
L_X(omega)
L_X(omega)
\mathcal{L}_{X}\!\left(\omega\right)
```

See {py:func}`jacopy.to_latex`, {py:func}`jacopy.to_ascii`, {py:func}`jacopy.print_expr`
and {py:func}`jacopy.display_expr`.

## Proof chains and theorems

| Output | In code | Result |
|---|---|---|
| chain as text | `chain_to_ascii(chain)` | one line per step: rule, provenance, before and after |
| one step as text | `step_to_ascii(chain.steps[0])` | a single line |
| chain as a tree in the terminal | `jacopy.print_chain(chain)` | printed |
| chain in Jupyter | `jacopy.display_chain(chain)` | a LaTeX display object |
| theorem in Jupyter | `jacopy.display_theorem(thm)` | an HTML display object |
| chain as LaTeX | `chain_to_latex(chain)` | a LaTeX string |
| theorem as LaTeX | `theorem_to_latex(thm)` | a LaTeX string |
| stand-alone LaTeX document | `jacopy.theorem_to_latex_document(thm, author="A. Author")` | a complete `article` document |

```python
print(chain_to_ascii(chain).splitlines()[0][:72])
print(step_to_ascii(chain.steps[0])[:60])
dc = jacopy.display_chain(chain)
dt = jacopy.display_theorem(thm)
print(type(dc).__name__, type(dt).__name__)
```

```text
[intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = 
[intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L
LatexDisplay HtmlDisplay
```

A theorem can be written to a LaTeX file and compiled with `pdflatex`:

```python
tex_chain = chain_to_latex(chain)
tex_thm = theorem_to_latex(thm)
doc = jacopy.theorem_to_latex_document(thm, author="A. Author")
print(doc.splitlines()[0])
```

```text
\documentclass{article}
```

<!-- no-run -->
```python
with open("cartan.tex", "w") as fh:
    fh.write(doc)          # then: pdflatex cartan.tex
```

See {py:func}`jacopy.display_chain`, {py:func}`jacopy.display_theorem` and
{py:func}`jacopy.theorem_to_latex_document`.

## Bibliography and citations

`jacopy.bibliography` holds the references of the works JacoPy's definitions and theorems
follow (the list is reproduced in the [bibliography](../reference/bibliography.md)).

| Purpose | In code | Result |
|---|---|---|
| full APA reference | `bib.apa_reference("DereliDogan2020")` | a string |
| citation with a locator | `c = bib.cite("DereliDogan2020", "Definition 3.10")` | a `Citation` |
| in-text form | `bib.in_text(c)` | `(Dereli & Doğan, 2020, Definition 3.10)` |
| sources cited by a chain | `bib.chain_sources(chain.steps)` | the references attached to the rules used |

```python
print(bib.apa_reference("DereliDogan2020")[:60])
c = bib.cite("DereliDogan2020", "Definition 3.10")
print(bib.in_text(c), "|", c.author_year())
print(len(bib.chain_sources(chain.steps)), "sources in this chain")
```

```text
Dereli, T., & Doğan, K. (2020). Metric-connection geometries
(Dereli & Doğan, 2020, Definition 3.10) | Dereli & Doğan, 2020
0 sources in this chain
```

## Rendering options

The renderers share a few keyword options. All of them are keyword-only and change only the
output, never the chain. The full list is on the
[Common parameters and settings](../reference/parameters.md#display-latex-and-citations)
page.

| Keyword | Accepted by | Default | Effect |
|---|---|---|---|
| `verbosity` | `chain_to_ascii`, `step_to_ascii`, `jacopy.print_chain`, `ProofChain.format` | `"full"` | `"full"`: rule, classification, before and after, justification; `"summary"`: without the justification; `"compact"`: rule and classification only (`ProofChain.format` keeps before and after) |
| `max_depth` | text and terminal renderers; LaTeX renderers | `64` (text), `0` (LaTeX) | how many levels of sub-steps are shown; LaTeX shows top-level steps only unless you raise it |
| `max_steps` | `chain_to_latex`, `theorem_to_latex`, `jacopy.display_chain`, `jacopy.display_theorem`, the document builders | `None` (`40` for `display_theorem`) | show only the first steps and end with a "more steps" row |
| `cite_style` | `chain_to_latex`, `step_to_latex`, `theorem_to_latex` | `"apa"` | `"apa"` writes the in-text citation; `"biblatex"` writes `\parencites` commands |
| `references` | `chain_to_ascii` (`True`/`False`); `jacopy.theorem_to_latex_document`, `chain_to_latex_document` (`"apa"`, `"biblatex"`, `None`) | `False`; `"apa"` | append the reference list of the works the rules cite; in a document `"apa"` typesets a References section, `"biblatex"` embeds a `.bib` file (compile with biber), `None` omits the list |
| `with_proof` | `theorem_to_latex`, `jacopy.theorem_to_latex_document`, `jacopy.display_theorem` | `True` | include the proof transcript after the statement |
| `style` | `bib.in_text`, `bib.apa_reference`, `bib.references_block` | `"plain"` | `"plain"`, `"markdown"` or `"latex"` (LaTeX escapes for accented names) |

```python
from jacopy.central.algebroid import algebroid
from jacopy.central.algebroid.theorems import prove_anchor_morphism

E = algebroid("E", declare=("leibniz",))
u, v = E.sections("u v")
ach, _ = prove_anchor_morphism(E, u, v, f, registry=reg)    # a chain whose rules cite sources

for mode in ("full", "summary", "compact"):
    print(mode, len(chain_to_ascii(chain, verbosity=mode)), "characters")
print(chain_to_latex(chain, max_steps=2).count(r"\vdots"), "ellipsis row")
print(chain_to_latex(ach, cite_style="biblatex").count(r"\parencites") > 0)
print(chain_to_ascii(ach, references=True).splitlines()[-1][:60])
print(len(theorem_to_latex(thm, with_proof=False)) < len(theorem_to_latex(thm)))
print(bib.in_text(c, "latex"))
```

```text
full 1060 characters
summary 554 characters
compact 453 characters
1 ellipsis row
True
Dereli, T., & Doğan, K. (2020). Metric-connection geometries
True
(Dereli \& Do\u{g}an, 2020, Definition 3.10)
```
