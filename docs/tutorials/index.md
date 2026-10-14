# Tutorials

These tutorials are lessons: you follow along in a Python session, every code block
runs as written, and each page ends with a working result. They assume familiarity
with differential geometry (vector fields, forms, Cartan calculus) but none with
JacoPy. Work through them in order; each page is self-contained in code but builds
on the ideas of the previous one.

All tutorials need only JacoPy itself, except [When a claim is false](false-claims.md),
whose second half uses the model oracle and therefore SymPy (the `oracle` extra).

```{toctree}
:maxdepth: 1

first-proof
cartan-calculus
false-claims
algebroids
own-bracket
dorfman-showcase
```

* [Your first proof](first-proof.md): objects, an identity, the step-by-step proof
  chain, and the assumptions a result depends on.
* [Cartan calculus on TM](cartan-calculus.md): $d$, $\iota_X$, $\mathcal{L}_X$,
  Cartan's magic formula and its proof chain, $d^2 = 0$, LaTeX export.
* [When a claim is false](false-claims.md): the residual of a false identity, and
  the model oracle showing two different values in a concrete model.
* [Algebroids and declared axioms](algebroids.md): an identity that closes with a
  declaration, fails without it, and closes again by citing a derived theorem.
* [Defining your own bracket](own-bracket.md): a new bracket node and rule, your own
  axioms, what closes and what leaves a residual.
* [Showcase: the Dorfman bracket](dorfman-showcase.md): the research interface
  checks the Courant-type axioms of the Dorfman bracket and of its bivector twist.
