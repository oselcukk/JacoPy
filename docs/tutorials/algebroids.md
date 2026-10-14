# Algebroids and declared axioms

On $TM$ every identity follows from definitions. On a general anchored bundle
$E \to M$, with a bracket $[\cdot,\cdot]_E$ on sections and an anchor
$\rho: E \to TM$, most familiar identities hold only if the bracket satisfies
certain axioms. In JacoPy you *declare* those axioms. This tutorial proves an
identity that closes with a declaration, watches it fail without one, and then
derives the missing axiom as a theorem from weaker declarations.

## An algebroid and its declarations

`algebroid(name, declare=...)` creates an anchored bundle. Each declaration is an
axiom the bracket is assumed to satisfy; *levels* bundle common combinations.

```python
import textwrap

import jacopy
import jacopy.central.algebroid as ag
from jacopy.central.algebroid import algebroid, algebroid_engine
from jacopy.proof.result import prove

print(ag.DECLARATIONS)
print(ag.LEVELS["lie"])
print(ag.LEVELS["leibniz"])
```

```text
('right-leibniz', 'left-leibniz', 'anchor-morphism', 'jacobi', 'antisymmetric', 'symmetric-part', 'metric-invariance', 'regular', 'bourbaki-invariance', 'courant-invariance', 'exact')
('right-leibniz', 'antisymmetric', 'jacobi')
('right-leibniz', 'jacobi')
```

We take a Lie algebroid $K$ and additionally declare that the anchor is a
morphism of brackets, $\rho([u,v]_K) = [\rho u, \rho v]$.

```python
reg = jacopy.PropertyRegistry()
(f,) = jacopy.functions("f", registry=reg)

K = algebroid("K", declare=("lie", "anchor-morphism"))
u, v = K.sections("u v")

print(sorted(K.declarations))
print(K.bracket(u, v), K.anchor(u), jacopy.Act(K.anchor(u), f))
```

```text
['anchor-morphism', 'antisymmetric', 'jacobi', 'right-leibniz']
[u,v]_K ρ(u) ρ(u)(f)
```

## $d_K^2 = 0$ with the declaration

The differential $d_K$ of an algebroid is defined by the same Palais formula as on
$TM$, with $\rho$ in place of the identity. On functions,

$$(d_K d_K f)(u, v) = \rho(u)\big(\rho(v)f\big) - \rho(v)\big(\rho(u)f\big) - \rho([u,v]_K)f .$$

`algebroid_engine(K)` contains the definitions and the rules for every axiom $K$
declares.

```python
ddf = jacopy.multi_eval(ag.d_E(K, ag.d_E(K, f)), u, v)

result = prove(algebroid_engine(K, registry=reg), ddf, jacopy.Zero, registry=reg)
print(result.summary())
```

```text
CLOSED: d_K(d_K(f))(u, v) = 0  — under the assumptions below
  generality: generic-function
  requires declared: anchor morphism (K): ρ([u,v]) = [ρ(u), ρ(v)] [Algebroid('K', bundle=Bundle('K'))]
  requires registry: registry declaration: Graded(degree=0) on f
  requires structure: Algebroid('K', bundle=Bundle('K')) declaring ['anchor-morphism', 'antisymmetric', 'jacobi', 'right-leibniz'] [Algebroid('K', bundle=Bundle('K'))]
  via definition: intrinsic d (Cartan-K): Palais formula dω(X_0,…,X_p) = Σ(−1)^i ρ(X_i)(ω(…)) + Σ(−1)^{i+j} ω([X_i,X_j],…) ×4
  via definition: Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))
  via canonicalization: simplify
  budget: 7/1024 steps; jacopy 0.0.1
```

The result is closed *under assumptions*, and the first `requires` line names the
one axiom that was used: the anchor morphism property. The chain shows where:

```python
for step in result.chain.steps:
    print(f"{step.role!s:11} {step.rule.split(':')[0]}")
```

```text
definition  intrinsic d (Cartan-K)
definition  intrinsic d (Cartan-K)
definition  intrinsic d (Cartan-K)
definition  intrinsic d (Cartan-K)
assumption  anchor morphism (K)
definition  Lie bracket definition
None        simplify
```

## Without the declaration

Now the same identity on an algebroid that declares only the `lie` level:

```python
K0 = algebroid("K0", declare=("lie",))
u0, v0 = K0.sections("u v")
ddf0 = jacopy.multi_eval(ag.d_E(K0, ag.d_E(K0, f)), u0, v0)

result0 = prove(algebroid_engine(K0, registry=reg), ddf0, jacopy.Zero, registry=reg)
print(result0.status)
print(result0.residual)
```

```text
RESIDUAL
((-ρ([u,v]_K0)(f)) + ρ(u)(ρ(v)(f)) + (-ρ(v)(ρ(u)(f))))
```

The proof does not close, and the residual is exactly the failure of the anchor to
preserve brackets, $\big([\rho u, \rho v] - \rho([u,v])\big)f$. JacoPy does not
silently assume an axiom you did not declare.

## Deriving the missing axiom

In a Leibniz algebroid (right Leibniz rule and Jacobi identity declared) the anchor
morphism property is not an axiom but a theorem. The builder
`prove_anchor_morphism` proves it and returns the chain together with a citable
`Theorem`:

```python
L = algebroid("L", declare=("leibniz",))
a, b = L.sections("u v")

chain, theorem = ag.prove_anchor_morphism(L, a, b, f, registry=reg)
print(theorem.statement)
print(len(chain.steps), "steps")
for req in theorem.requires:
    print(req.kind, "|", textwrap.shorten(req.name, width=70, placeholder=" ..."))
```

```text
ρ([u,v]) = [ρ(u), ρ(v)] on L (every Leibniz algebroid is pre-Leibniz)
8 steps
declared | Leibniz-Jacobi (L): J(u,v,w) = 0
declared | right-Leibniz (L): [u, fv] = ρ(u)(f)v + f[u,v]
registry | registry declaration: Graded(degree=0) on f
registry | registry: relies on undeclared properties (f has no NonCommuting ...
structure | Algebroid('L', bundle=Bundle('L')) declaring ['jacobi', 'right- ...
unreplayed | theorem anchor_morphism_L_u_v: chain does not replay into its ...
```

The theorem rests on the two declarations of $L$. The `unreplayed` entry is
JacoPy's own bookkeeping: some top-level steps of this proof are assembled by the
builder (for example "agreement on generators") instead of being replayed by the
rewrite engine, and the record says so.

On an algebroid with no declarations the same builder refuses and names what is
missing:

```python
E0 = algebroid("E0", declare=())
try:
    ag.prove_anchor_morphism(E0, *E0.sections("u v"), f, registry=reg)
except jacopy.ProofFailure as failure:
    print(failure)
```

```text
anchor morphism is not derivable here: the proof needs the declarations ['right-leibniz', 'jacobi'] which Algebroid('E0', bundle=Bundle('E0')) does not make
```

## Citing the theorem

A proved theorem enters another proof only by explicit citation. We put it in a
`TheoremBook` and cite it into the engine of $L$. Because the record is
`unreplayed`, JacoPy refuses to cite it silently; we must pass
`allow_legacy=True`, and the citing result then carries the marker.

```python
book = jacopy.TheoremBook()
book.add(theorem)

engine = algebroid_engine(L, registry=reg)
jacopy.cite(engine, book, theorem.name, allow_legacy=True)

ddfL = jacopy.multi_eval(ag.d_E(L, ag.d_E(L, f)), a, b)
resultL = prove(engine, ddfL, jacopy.Zero, registry=reg)
print(resultL.status)
for req in resultL.requires:
    print(req.kind, "|", textwrap.shorten(req.name, width=70, placeholder=" ..."))
```

```text
CLOSED
declared | Leibniz-Jacobi (L): J(u,v,w) = 0
declared | right-Leibniz (L): [u, fv] = ρ(u)(f)v + f[u,v]
structure | Algebroid('L', bundle=Bundle('L')) declaring ['jacobi', 'right- ...
unreplayed | theorem anchor_morphism_L_u_v: chain does not replay into its ...
registry | registry declaration: Graded(degree=0) on f
registry | registry: relies on undeclared properties (f has no NonCommuting ...
```

Now $d_L^2 f = 0$ closes on a Leibniz algebroid, and its assumptions are traced
through the citation back to right Leibniz and Jacobi.

## What you learned

* `algebroid(name, declare=...)` creates an anchored bundle whose axioms you choose,
  atomically or by level.
* An identity closes only if the declared axioms suffice; the result names the
  axioms it used.
* Without a needed declaration the residual shows the missing piece.
* A theorem proved from declarations can be cited into another proof; its
  requirements travel with it.

Next: [Defining your own bracket](own-bracket.md).
