# Defining your own bracket

The previous tutorials used operators that ship with JacoPy. In research you
usually want to test a structure of your own: a new bracket, with axioms you are
willing to assume, to see which identities follow. This tutorial defines a bracket
on vector fields that JacoPy does not know, proves that it is antisymmetric, finds
that the Jacobi identity fails, declares an extra axiom of our own, and reads what
is still left.

For a 1-form $\varphi$ we define

$$[X, Y]_\varphi = [X, Y] + \varphi(X)\,Y - \varphi(Y)\,X .$$

Nothing in the library is changed; everything below is user code.

## Step 1: objects and an engine

```python
import jacopy
from jacopy import Expr, Act
from jacopy.central.tangent import tangent_engine
from jacopy.central.calculus import ActExpansionDefinition
from jacopy.central.calculus.slot_rules import PairingArgSplitDefinition
from jacopy.display import register, to_latex
from jacopy.proof.result import prove

reg = jacopy.PropertyRegistry()
(h,) = jacopy.functions("h", registry=reg)       # test function
X, Y, Z = jacopy.vector_fields("X Y Z")
(phi,) = jacopy.forms("phi", degree=1)
```

## Step 2: a new expression node

A new operation is a subclass of `Expr`. It stores its arguments, exposes them as
`children`, and defines how it prints. `register` adds a LaTeX rendering.

```python
class PhiBracket(Expr):
    __slots__ = ("_a", "_b")

    def __init__(self, a, b):
        self._a, self._b = a, b

    @property
    def children(self):
        return (self._a, self._b)

    def _key(self):
        return (self._a, self._b)

    def _repr_inner(self):
        return f"[{self._a._repr_inner()},{self._b._repr_inner()}]_phi"


@register(PhiBracket)
def _phi_latex(e, prec=0):
    a, b = e.children
    return r"\left[" + to_latex(a) + r",\, " + to_latex(b) + r"\right]_{\phi}"


print(PhiBracket(X, Y))
print(to_latex(PhiBracket(X, Y)))
```

```text
[X,Y]_phi
\left[X,\, Y\right]_{\phi}
```

## Step 3: the defining rule

The meaning of the bracket is a rewrite rule, a subclass of `jacopy.Definition`
with `matches` (does the rule apply to this node?) and `rewrite` (what does it
become?). We collect the rules in an engine: the definitions on $TM$, the product
rule, linearity of $\varphi$ in its argument, and our definition.

```python
class PhiDefinition(jacopy.Definition):
    name = "definition: [A,B]_φ = [A,B] + φ(A)·B − φ(B)·A"
    anchor = PhiBracket

    def matches(self, e):
        return isinstance(e, PhiBracket)

    def rewrite(self, e):
        a, b = e.children
        return jacopy.lie_bracket(a, b) + jacopy.pairing(phi, a) * b - jacopy.pairing(phi, b) * a


def make_engine(*extra_rules):
    engine = tangent_engine(registry=reg)
    engine.register(ActExpansionDefinition(reg))   # product rule
    engine.register(PairingArgSplitDefinition())   # φ(A + B) = φ(A) + φ(B)
    engine.register(PhiDefinition())
    for rule in extra_rules:
        engine.register(rule)
    return engine
```

## Step 4: antisymmetry closes

Vector fields are compared on the test function $h$. Antisymmetry,
$[X,Y]_\varphi = -[Y,X]_\varphi$:

```python
br = PhiBracket
result = prove(make_engine(), Act(br(X, Y), h), -Act(br(Y, X), h), registry=reg)
print(result.summary())
```

```text
CLOSED: [X,Y]_phi(h) = (-[Y,X]_phi(h))  — under the assumptions below
  generality: generic-function
  requires declared: definition: [A,B]_φ = [A,B] + φ(A)·B − φ(B)·A ×2
  requires registry: registry declaration: Graded(degree=0) on h
  requires registry: registry: relies on undeclared properties (⟨phi, X⟩ has no Graded declared; Y(h) has no Graded declared; ⟨phi, X⟩ has no NonCommuting declared; … (12 in all))
  via definition: Act linearity: (A + B)(x) = A(x) + B(x) ×2
  via definition: Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f)) ×2
  via definition: graded Leibniz / Act linearity (slot-reachable product rule) ×5
  via canonicalization: simplify ×2
  via theorem: bracket orientation: [B, A] = −[A, B], [A, A] = 0
  budget: 14/1024 steps; jacopy 0.1.0
```

Note the first `requires` line. JacoPy cannot check a rule written outside the
library, so it treats every such rule as a *declared assumption*, whatever the rule
calls itself. Your definition appears in the requirements of every result that
uses it.

## Step 5: the Jacobi identity fails

$$\sum_{\text{cyc}} [[X,Y]_\varphi, Z]_\varphi = 0 \quad ?$$

```python
jacobi = Act(br(br(X, Y), Z), h) + Act(br(br(Y, Z), X), h) + Act(br(br(Z, X), Y), h)

result_jacobi = prove(make_engine(), jacobi, jacopy.Zero, registry=reg)
print(result_jacobi.status, len(result_jacobi.chain.steps), "steps")
```

```text
RESIDUAL 65 steps
```

The residual is long. By hand, the cyclic sum reduces to two kinds of terms,

$$\sum_{\text{cyc}} [[X,Y]_\varphi, Z]_\varphi
= \sum_{\text{cyc}} \varphi(X)\,[Y,Z] \;-\; \sum_{\text{cyc}} d\varphi(X,Y)\, Z ,$$

and in the residual $d\varphi(X,Y)$ appears unfolded as
$X(\varphi(Y)) - Y(\varphi(X)) - \varphi([X,Y])$.

## Step 6: declaring $d\varphi = 0$

Suppose we restrict to closed $\varphi$. We declare $d\varphi = 0$ as our own axiom
in the form the engine can use,
$\varphi([A,B]) = A(\varphi(B)) - B(\varphi(A))$, and mark it with
`role = "assumption"`:

```python
from jacopy.algebra.lie_bracket_vf import LieBracketVF


class DPhiZero(jacopy.Definition):
    name = "declared dφ = 0:  φ([A,B]) = A(φ(B)) − B(φ(A))"
    role = "assumption"
    anchor = jacopy.Pairing

    def matches(self, e):
        return isinstance(e, jacopy.Pairing) and e.alpha == phi and isinstance(e.X, LieBracketVF)

    def rewrite(self, e):
        a, b = e.X.X, e.X.Y
        return Act(a, jacopy.pairing(phi, b)) - Act(b, jacopy.pairing(phi, a))


result_closed = prove(make_engine(DPhiZero()), jacobi, jacopy.Zero, registry=reg)
print(result_closed.status)
print(result_closed.residual)
```

```text
RESIDUAL
⟨phi, ((X(Y(h)) * Z) + (-(X(Z(h)) * Y)) + (-(Y(X(h)) * Z)) + (Y(Z(h)) * X) + (Z(X(h)) * Y) + (-(Z(Y(h)) * X)))⟩
```

The $d\varphi$ terms are gone, but the identity still does not close. The residual
is $\varphi$ applied to a combination of second derivatives; JacoPy confirms that
it equals the first sum above, $\sum_{\text{cyc}} \varphi(X)\,[Y,Z](h)$:

```python
P, lb = jacopy.pairing, jacopy.lie_bracket
expected = (P(phi, X) * Act(lb(Y, Z), h)
            + P(phi, Y) * Act(lb(Z, X), h)
            + P(phi, Z) * Act(lb(X, Y), h))

check = prove(make_engine(), result_closed.residual, expected, registry=reg)
print(check.status)
```

```text
CLOSED
```

This term does not depend on $d\varphi$, so no condition on $d\varphi$ can remove it.
It is a genuine obstruction, not a missing rule: on $\mathbb{R}^2$ take
$\varphi = dx^1$ (closed), $X = \partial_1$, $Y = \partial_2$, $Z = x^2\partial_2$;
then $\varphi(Y) = \varphi(Z) = 0$ and the sum is
$[\partial_2, x^2\partial_2] = \partial_2 \neq 0$. So $[\cdot,\cdot]_\varphi$ is not a
Lie bracket even for closed $\varphi \neq 0$.

## The research loop

The pattern of this page is the general one:

1. Define the new objects (`Expr` subclasses) and their meaning (`Definition` rules).
2. Collect the rules you allow in an engine, together with any axioms you are
   willing to assume (`role = "assumption"`).
3. Prove: a `CLOSED` result lists every assumption it used; a `RESIDUAL` is exactly
   what is left, and it can be analysed further with JacoPy itself.

For brackets on generalized tangent bundles, the research interface
`jacopy.research` automates much of this; see
[Showcase: the Dorfman bracket](dorfman-showcase.md).
