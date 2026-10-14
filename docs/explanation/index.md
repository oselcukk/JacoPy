# Explanation

These pages explain what JacoPy is, how it is built and why its results
can be trusted, and where its limits lie. They are meant to be read,
not followed step by step; for hands-on instructions see the
[tutorials](../tutorials/index.md) and the [how-to guides](../howto/index.md).

## What JacoPy is

JacoPy is a pure-Python library that proves identities of differential
geometry **symbolically and without coordinates**, and records every
proof step by step. A proof reads like a textbook derivation: each line
states which definition, which declared axiom or which previously
proved theorem it uses, and the assumptions on which the result rests
are listed separately.

Four ideas shape the library:

* **Objects are abstract terms.** Functions, vector fields, forms and
  tensors are terms of a formal language, not expressions in $x^i$ or
  $\partial_i$; even the dimension may be symbolic. Constructing a term
  computes nothing; computation happens only when rules are applied.
* **"Proved" means "reduced to the same normal form".** Both sides are
  rewritten with rules that come from definitions and from explicitly
  declared axioms. If the reduction does not close, the library does not
  say "false"; it shows the remaining term, the *residual*.
* **One general machine.** The exterior derivative $d$ and the Lie
  derivative $\mathcal{L}$ are built from an anchor $\rho$ and a bracket
  $[\cdot,\cdot]$. The tangent bundle $TM$ is the special case
  $\rho=\mathrm{id}$ with the Lie bracket; an algebroid $E$ uses the
  same machine. For $E=TM$ the algebroid calculus is the ordinary Cartan
  calculus itself.
* **A research tool.** JacoPy aims to reproduce the long but mechanical
  computations in research papers (the Jacobi defect of a bracket, the
  transport of axioms under a twist, the compatibility conditions of a
  Drinfel'd double) step by step, with sources and explicit
  assumptions, and to let users test their own structures with the same
  machine.

## Pages

* [Capabilities](capabilities.md): the mathematics JacoPy covers today,
  from the Cartan calculus to Courant algebroids.
* [Architecture](architecture.md): layers, file layout, how a proof
  runs, extension points, and the public API levels, with diagrams
  generated from the code.
* [Trust model](trust-model.md): what a result means, assumption
  tracking, default rejection of citations, minting and replay, and
  the model oracle.
* [Limitations](limitations.md): what JacoPy cannot do yet.
* [Related tools](related-tools.md): how JacoPy relates to computer
  algebra systems and proof assistants.
* [Roadmap](roadmap.md): plans and ideas.

```{toctree}
:hidden:
:maxdepth: 1

capabilities
architecture
trust-model
limitations
related-tools
roadmap
```
