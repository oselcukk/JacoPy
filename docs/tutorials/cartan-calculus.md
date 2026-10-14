# Cartan calculus on TM

This tutorial introduces the three operators of Cartan calculus on the tangent
bundle: the exterior derivative $d$, the interior product $\iota_X$ and the Lie
derivative $\mathcal{L}_X$. We prove Cartan's magic formula
$\mathcal{L}_X = \iota_X d + d\,\iota_X$ on functions and on 1-forms, read its proof
chain, look at $d^2 = 0$, and export a proof as LaTeX.

## The operators

The operators are created once and then applied like functions. `d`, `L_X` and
`i_X` below stand for $d$, $\mathcal{L}_X$ and $\iota_X$.

```python
import jacopy
from jacopy.central.tangent import tangent_engine
from jacopy.proof.result import prove

reg = jacopy.PropertyRegistry()
(f,) = jacopy.functions("f", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
(omega,) = jacopy.forms("omega", degree=1)

d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

print(d(f), d(omega), i_X(omega), L_X(omega))
print(jacopy.to_latex(L_X(omega)))
```

```text
d(f) d(omega) ι_X(omega) L_X(omega)
\mathcal{L}_{X}\!\left(\omega\right)
```

JacoPy uses the intrinsic definitions. For a $p$-form, $d$ is given by the Palais
formula,

$$d\omega(X_0,\dots,X_p) = \sum_i (-1)^i X_i\big(\omega(\dots,\widehat{X_i},\dots)\big)
+ \sum_{i<j} (-1)^{i+j}\,\omega([X_i,X_j],\dots,\widehat{X_i},\dots,\widehat{X_j},\dots),$$

$\iota_X$ inserts $X$ into the first slot, and
$(\mathcal{L}_X\omega)(Y_1,\dots) = X(\omega(Y_1,\dots)) - \sum_i \omega(\dots,[X,Y_i],\dots)$.
These definitions are the rewrite rules of `tangent_engine`.

## Cartan's formula on functions

On a function, $\mathcal{L}_X f = \iota_X df + d\,\iota_X f$ reduces to
$X(f) = df(X) + d(0)$. The library ships this proof as a ready-made builder:

```python
import jacopy.central.tangent as tg

chain = tg.prove_cartan_magic_on_functions(X, f, registry=reg)
for step in chain.steps:
    print(step.role, "|", step.before, "->", step.after)
```

```text
definition | L_X(f) -> X(f)
definition | ι_X(d(f)) -> ⟨d(f), X⟩
definition | ⟨d(f), X⟩ -> X(f)
definition | ι_X(f) -> 0
definition | d(0) -> 0
None | (X(f) + (-(X(f) + 0))) -> 0
```

## Cartan's formula on 1-forms

For a 1-form we compare both sides on a vector field $Y$:

$$(\mathcal{L}_X\omega)(Y) = (\iota_X d\omega)(Y) + (d\,\iota_X\omega)(Y).$$

`jacopy.pairing(alpha, Y)` is the evaluation $\langle\alpha, Y\rangle = \alpha(Y)$.

```python
P = jacopy.pairing
lhs = P(L_X(omega), Y)
rhs = P(i_X(d(omega)), Y) + P(d(i_X(omega)), Y)

result = prove(tangent_engine(registry=reg), lhs, rhs, registry=reg)
print(result.summary())
```

```text
CLOSED: ⟨L_X(omega), Y⟩ = (⟨ι_X(d(omega)), Y⟩ + ⟨d(ι_X(omega)), Y⟩)  — assumption-free
  generality: generic-function
  via definition: intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = ρ(X)(ω(Y…)) − Σ ω(…,[X,Y_i],…)
  via canonicalization: simplify
  via definition: intrinsic d (Cartan-TM): Palais formula dω(X_0,…,X_p) = Σ(−1)^i ρ(X_i)(ω(…)) + Σ(−1)^{i+j} ω([X_i,X_j],…) ×2
  via definition: interior product: ι_X f = 0, ι_X ω = ⟨ω, X⟩ (deg 0 / 1)
  via definition: interior product evaluation: (ι_X ω)(Y_1,…,Y_k) = ω(X, Y_1,…,Y_k)
  budget: 6/1024 steps; jacopy 0.1.0a1
```

The result is *assumption-free*: no axiom and no registry entry was used, only the
definitions of $d$, $\iota$ and $\mathcal{L}$. The driver rewrites the left-hand
side to a normal form and then reads the right-hand side's rewriting backwards;
steps of the second kind are marked `(reversed)`. Here is the chain, one line per
step:

```python
for i, step in enumerate(result.chain.steps, 1):
    print(i, step.rule.split(":")[0], "|", step.after)
```

```text
1 intrinsic L (Cartan-TM) | (X(⟨omega, Y⟩) + (-⟨omega, [X,Y]_VF⟩))
2 simplify | ((X(⟨omega, Y⟩) + (-Y(⟨omega, X⟩)) + (-⟨omega, [X,Y]_VF⟩)) + Y(⟨omega, X⟩))
3 intrinsic d (Cartan-TM) | ((X(⟨omega, Y⟩) + (-Y(⟨omega, X⟩)) + (-⟨omega, [X,Y]_VF⟩)) + ⟨d(⟨omega, X⟩), Y⟩)
4 interior product | ((X(⟨omega, Y⟩) + (-Y(⟨omega, X⟩)) + (-⟨omega, [X,Y]_VF⟩)) + ⟨d(ι_X(omega)), Y⟩)
5 intrinsic d (Cartan-TM) | (d(omega)(X, Y) + ⟨d(ι_X(omega)), Y⟩)
6 interior product evaluation | (⟨ι_X(d(omega)), Y⟩ + ⟨d(ι_X(omega)), Y⟩)
```

Mathematically: step 1 applies the definition of $\mathcal{L}_X$,
$(\mathcal{L}_X\omega)(Y) = X(\omega(Y)) - \omega([X,Y])$; steps 3 to 6 recognize
$Y(\omega(X)) = (d\,\iota_X\omega)(Y)$ and
$X(\omega(Y)) - Y(\omega(X)) - \omega([X,Y]) = d\omega(X,Y) = (\iota_X d\omega)(Y)$.

## A longer proof: $d^2 = 0$

Evaluated on three vector fields, $d(d\omega)(X,Y,Z)$ expands by the Palais formula
into derivative terms and brackets. We add the product rule to the engine so that
the derivatives are distributed:

```python
from jacopy.central.calculus import ActExpansionDefinition

engine = tangent_engine(registry=reg)
engine.register(ActExpansionDefinition(reg))

dd = jacopy.multi_eval(d(d(omega)), X, Y, Z)
print(prove(engine, dd, jacopy.Zero, registry=reg).summary())
```

```text
RESIDUAL: d(d(omega))(X, Y, Z) = 0
  residual (unreduced, NOT a disproof): ⟨omega, ((-[X,[Y,Z]_VF]_VF) + [Y,[X,Z]_VF]_VF + (-[Z,[X,Y]_VF]_VF))⟩
  generality: generic-function
  via definition: intrinsic d (Cartan-TM): Palais formula dω(X_0,…,X_p) = Σ(−1)^i ρ(X_i)(ω(…)) + Σ(−1)^{i+j} ω([X_i,X_j],…) ×7
  via definition: graded Leibniz / Act linearity (slot-reachable product rule) ×3
  via definition: Lie bracket definition: [X, Y](f) = X(Y(f)) - Y(X(f)) ×3
  via theorem: bracket orientation: [B, A] = −[A, B], [A, A] = 0 ×3
  via definition: slot linearity: Neg pulls out of evaluation slots ×3
  via canonicalization: simplify
  budget: 20/1024 steps; jacopy 0.1.0a1
```

The status is `RESIDUAL`, which means "not closed with these rules", not "false".
The residual is exactly $\omega$ applied to the Jacobiator,

$$\big\langle \omega,\; -[X,[Y,Z]] + [Y,[X,Z]] - [Z,[X,Y]] \big\rangle,$$

and the bracket combination vanishes by the Jacobi identity for vector fields. The
library's builder `prove_d_squared_zero_on_one_forms` does this second step for
you: it proves the vector-level identity as a lemma and uses it.

```python
chain, lemmas = tg.prove_d_squared_zero_on_one_forms(omega, X, Y, Z, f, registry=reg)
print(f"closed: {chain.final == jacopy.Zero}, {len(chain.steps)} steps")
for lemma in lemmas:
    print("lemma:", lemma.statement)
```

```text
closed: True, 20 steps
lemma: ((-[X,[Y,Z]_VF]_VF) + [Y,[X,Z]_VF]_VF + (-[Z,[X,Y]_VF]_VF)) = 0 (vector-level bracket identity)
```

## LaTeX output

`jacopy.to_latex` renders single expressions; `jacopy.display.chain_to_latex`
renders a whole proof chain as a LaTeX fragment (one numbered block per step), and
`chain_to_latex_document` wraps it in a complete LaTeX document.

```python
from jacopy.display import chain_to_latex, chain_to_latex_document

print(jacopy.to_latex(lhs), "=", jacopy.to_latex(rhs))

fragment = chain_to_latex(result.chain)
print("\n".join(fragment.splitlines()[:8]))
```

```text
\langle \mathcal{L}_{X}\!\left(\omega\right),\, Y \rangle = \langle \iota_{X}\!\left(d\!\left(\omega\right)\right),\, Y \rangle + \langle d\!\left(\iota_{X}\!\left(\omega\right)\right),\, Y \rangle
{\allowdisplaybreaks\small
\begin{gather*}
\text{\textbf{(1)}}\ \begin{aligned}[t]
&\text{[intrinsic L (Cartan-TM): L\_X f = \ensuremath{\rho}(X)(f), L\_X Y = [X,Y], (L\_X \ensuremath{\omega})(Y\ensuremath{\dots}) =} \\
&\text{\ensuremath{\rho}(X)(\ensuremath{\omega}(Y\ensuremath{\dots})) \ensuremath{-} \ensuremath{\Sigma} \ensuremath{\omega}(\ensuremath{\dots},[X,Y\_i],\ensuremath{\dots})] (definition)} \\
&\quad \langle \mathcal{L}_{X}\!\left(\omega\right),\, Y \rangle \\
&\to X\!\left(\langle \omega,\, Y \rangle\right) - \langle \omega,\, \left[X,\, Y\right] \rangle
\end{aligned} \\[1ex]
```

```python
document = chain_to_latex_document(result.chain, title="Cartan formula on a 1-form")
print(document.splitlines()[0])
print(len(document.splitlines()), "lines")
```

```text
\documentclass{article}
57 lines
```

## What you learned

* `jacopy.exterior_d()`, `jacopy.interior(X)` and `jacopy.lie_derivative(X)` build
  the Cartan operators; their intrinsic definitions are the rules of `tangent_engine`.
* Forms are compared by evaluating them on vector fields (`jacopy.pairing`,
  `jacopy.multi_eval`).
* A `RESIDUAL` is a precise statement of what is left; often it names the missing
  lemma.
* `chain_to_latex` and `chain_to_latex_document` export proofs.

Next: [When a claim is false](false-claims.md).
