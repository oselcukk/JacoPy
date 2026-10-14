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
