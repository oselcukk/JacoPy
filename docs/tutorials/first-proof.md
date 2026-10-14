# Your first proof

This tutorial walks through a complete JacoPy session on the tangent bundle $TM$.
We create functions and vector fields, state the Leibniz rule of the Lie bracket,
let JacoPy prove it, read the proof chain step by step, and finally ask which
assumptions the proof depends on. Every block on this page runs as written, in
order, in one Python session.

## Objects

JacoPy works with symbolic objects, not with coordinates. Functions are declared
in a *property registry*, which records facts about objects (here: that $f$ and $g$
have degree $0$). Vector fields need no registry.

```python
import jacopy
from jacopy.central.tangent import tangent_engine

reg = jacopy.PropertyRegistry()
f, g = jacopy.functions("f g", registry=reg)
X, Y = jacopy.vector_fields("X Y")

print(f, g, X, Y)
print(jacopy.lie_bracket(X, Y))
print(jacopy.Act(X, f))
```

```text
f g X Y
[X,Y]_VF
X(f)
```

`jacopy.lie_bracket(X, Y)` is the Lie bracket $[X,Y]$ of vector fields, and
`jacopy.Act(X, f)` is the derivative $X(f)$ of $f$ along $X$. Products and sums
are written with the ordinary Python operators.

## Stating an identity

The Lie bracket satisfies the Leibniz rule in its second slot,

$$[X, fY] = X(f)\,Y + f\,[X, Y].$$

Both sides are vector fields. JacoPy compares vector fields by letting them act on
a test function, so we evaluate both sides on $g$:

$$[X, fY](g) = X(f)\,Y(g) + f\,[X, Y](g).$$

```python
lhs = jacopy.Act(jacopy.lie_bracket(X, f * Y), g)
rhs = jacopy.Act(X, f) * jacopy.Act(Y, g) + f * jacopy.Act(jacopy.lie_bracket(X, Y), g)

print(lhs)
print(rhs)
```

```text
[X,(f * Y)]_VF(g)
((X(f) * Y(g)) + (f * [X,Y]_VF(g)))
```

## Proving it

`jacopy.show_equal` tries to prove `lhs == rhs`. The *engine* is the set of
rewrite rules it may use; `tangent_engine` holds the definitions of the operators
on $TM$. If the identity closes, the result is a proof chain; if not, a
`ProofFailure` is raised (see [When a claim is false](false-claims.md)).

```python
chain = jacopy.show_equal(lhs, rhs, registry=reg, engine=tangent_engine(registry=reg))
print(f"closed in {len(chain.steps)} steps")
```

```text
closed in 6 steps
```

## Reading the chain

Each step names the rule that was applied, the subterm it was applied to and the
result. `jacopy.print_chain` prints the whole transcript:

```python
jacopy.print_chain(chain)
```

```text
Proof (6 steps)
├── [bracket orientation: [B, A] = −[A, B], [A, A] = 0] (theorem) [X,(f * Y)]_VF
│   → -[(f * Y),X]_VF , apply theorem: bracket orientation: [B, A] = −[A, B], 
│   [A, A] = 0
├── [Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))] (definition) 
│   [X,Y]_VF(g) → X(Y(g)) - Y(X(g)) , apply definition: Lie bracket definition: 
│   [X, Y](f) = X(Y(f)) - Y(X(f))
├── [product-rule] (-[(f * Y),X]_VF)(g) - (X(f) * Y(g) + f * (X(Y(g)) - 
│   Y(X(g)))) → -[(f * Y),X]_VF(g) - (X(f) * Y(g) + f * (X(Y(g)) - Y(X(g)))) , 
│   graded Leibniz + linearity
├── [Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))] (definition) [(f * 
│   Y),X]_VF(g) → (f * Y)(X(g)) - X((f * Y)(g)) , apply definition: Lie bracket 
│   definition: [X, Y](f) = X(Y(f)) - Y(X(f))
├── [product-rule] -((f * Y)(X(g)) - X((f * Y)(g))) - (X(f) * Y(g) + f * 
│   (X(Y(g)) - Y(X(g)))) → -(f * Y(X(g)) - (X(f) * Y(g) + f * X(Y(g)))) - (X(f) 
│   * Y(g) + f * (X(Y(g)) - Y(X(g)))) , graded Leibniz + linearity
└── [simplify] -(f * Y(X(g)) - (X(f) * Y(g) + f * X(Y(g)))) - (X(f) * Y(g) + f *
    (X(Y(g)) - Y(X(g)))) → 0 , canonical-form pipeline
```

The proof expands the bracket with its definition $[A,B](h) = A(B(h)) - B(A(h))$,
distributes the derivatives with the product rule, and the final `simplify` step
cancels the remaining terms. Each step also carries a *role*, which records what
kind of justification it uses:

```python
for i, step in enumerate(chain.steps, 1):
    print(i, step.role, "|", step.rule)
```

```text
1 theorem | bracket orientation: [B, A] = −[A, B], [A, A] = 0
2 definition | Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))
3 None | product-rule
4 definition | Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f))
5 None | product-rule
6 None | simplify
```

A `definition` step unfolds the definition of an operator. A `theorem` step cites
a result that JacoPy has proved separately (here the antisymmetry
$[B,A] = -[A,B]$ of the bracket). Steps with no role (`None`) are algebraic
bookkeeping: the product rule and canonical simplification.

## Assumptions

A closed proof is only as general as what it relied on. The driver
`jacopy.proof.result.prove` normalizes both sides with an engine and returns a
`ProofResult` that lists these requirements. We add the product rule to the
engine as an explicit rewrite rule, because this driver works by rewriting each
side separately:

```python
from jacopy.central.calculus import ActExpansionDefinition
from jacopy.proof.result import prove

def engine():
    e = tangent_engine(registry=reg)
    e.register(ActExpansionDefinition(reg))
    return e

result = prove(engine(), lhs, rhs, registry=reg)
print(result.summary())
```

```text
CLOSED: [X,(f * Y)]_VF(g) = ((X(f) * Y(g)) + (f * [X,Y]_VF(g)))  — under the assumptions below
  generality: generic-function
  requires registry: registry declaration: Graded(degree=0) on f
  requires registry: registry declaration: Graded(degree=0) on g
  requires registry: registry: relies on undeclared properties (X(f) has no Graded declared; Y(g) has no Graded declared; X(Y(g)) has no Graded declared; … (9 in all))
  via theorem: bracket orientation: [B, A] = −[A, B], [A, A] = 0
  via definition: graded Leibniz / Act linearity (slot-reachable product rule) ×4
  via definition: Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f)) ×2
  via canonicalization: simplify ×2
  budget: 9/1024 steps; jacopy 0.1.0a1
```

The `requires` lines say that the proof used the registry entries "$f$ and $g$
have degree $0$", that is, that $f$ and $g$ are functions. The last `requires`
line collects the registry queries that came back "not declared" (for example, no
grading is declared for $X(f)$, so it is treated as degree $0$). These answers are
hypotheses of the proof as well: the result may be reused only where the registry
gives the same answers. The `via` lines count the rules used.

For comparison, the Jacobi identity

$$[X,[Y,Z]](h) + [Y,[Z,X]](h) + [Z,[X,Y]](h) = 0$$

follows from the definition of the bracket alone and closes *assumption-free*:

```python
(Z,) = jacopy.vector_fields("Z")
(h,) = jacopy.functions("h", registry=reg)
br, act = jacopy.lie_bracket, jacopy.Act
jacobi = act(br(X, br(Y, Z)), h) + act(br(Y, br(Z, X)), h) + act(br(Z, br(X, Y)), h)

print(prove(engine(), jacobi, jacopy.Zero, registry=reg).summary())
```

```text
CLOSED: ([X,[Y,Z]_VF]_VF(h) + [Y,[Z,X]_VF]_VF(h) + [Z,[X,Y]_VF]_VF(h)) = 0  — assumption-free
  generality: generic-function
  via definition: Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f)) ×9
  via definition: graded Leibniz / Act linearity (slot-reachable product rule) ×6
  via theorem: bracket orientation: [B, A] = −[A, B], [A, A] = 0 ×2
  via canonicalization: simplify
  budget: 18/1024 steps; jacopy 0.1.0a1
```

## LaTeX

Every expression can be printed as LaTeX:

```python
print(jacopy.to_latex(lhs))
print(jacopy.to_latex(rhs))
```

```text
\left[X,\, f \, Y\right]\!\left(g\right)
X\!\left(f\right) \, Y\!\left(g\right) + f \, \left[X,\, Y\right]\!\left(g\right)
```

## What you learned

* Objects are created with factories such as `jacopy.functions` and
  `jacopy.vector_fields`; functions are recorded in a `PropertyRegistry`.
* `jacopy.show_equal` returns a proof chain whose steps name their rules and roles.
* `jacopy.proof.result.prove` returns a `ProofResult`: its status (`CLOSED` or
  `RESIDUAL`) and the assumptions the proof depends on.

Next: [Cartan calculus on TM](cartan-calculus.md).
