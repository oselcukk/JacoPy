# JacoPy

JacoPy is a pure-Python library for graded algebra, bracket calculus and differential
geometry, on the tangent bundle $TM$ and on algebroids $E$, in which every manipulation
is recorded as a step-by-step proof. A closed identity comes with its proof chain, the
rule behind each step (a definition, a declared axiom or a cited theorem, with its
literature source) and the assumptions it depends on; an identity that does not close
reports the residual that is left. Coverage includes Cartan calculus, Lie and
Schouten–Nijenhuis brackets, algebroids with declared axioms, metric-affine geometry,
Poisson and Nambu–Poisson geometry, Drinfel'd doubles and twists, Courant algebroids and
generalized geometry, and a research interface for user-defined brackets. An optional
model oracle checks closed identities in random coordinate models. JacoPy requires
Python 3.10 or newer and has no required dependencies.

## What it looks like

Cartan's formula $\mathcal{L}_X = \iota_X\, d + d\, \iota_X$ on a 1-form $\omega$,
evaluated on a vector field $Y$,

$$
\langle \mathcal{L}_X \omega, Y \rangle
  = \langle \iota_X\, d\omega, Y \rangle + \langle d\, \iota_X \omega, Y \rangle ,
$$

proved from the definitions of $d$, $\mathcal{L}$ and $\iota$:

```python
import jacopy
from jacopy.central.tangent import tangent_engine

reg = jacopy.PropertyRegistry()
engine = tangent_engine(registry=reg)

X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

lhs = jacopy.pairing(L_X(omega), Y)
rhs = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)

chain = jacopy.show_equal(lhs, rhs, registry=reg, engine=engine)
print(f"closed in {len(chain.steps)} steps")
for n, step in enumerate(chain.steps, 1):
    print(f"{n}. {jacopy.to_ascii(step.before)}  ->  {jacopy.to_ascii(step.after)}")
```

```text
closed in 6 steps
1. ⟨L_X(omega), Y⟩  ->  X(⟨omega, Y⟩) - ⟨omega, [X,Y]_VF⟩
2. ⟨ι_X(d(omega)), Y⟩  ->  d(omega)(X, Y)
3. d(omega)(X, Y)  ->  X(⟨omega, Y⟩) - Y(⟨omega, X⟩) - ⟨omega, [X,Y]_VF⟩
4. ι_X(omega)  ->  ⟨omega, X⟩
5. ⟨d(⟨omega, X⟩), Y⟩  ->  Y(⟨omega, X⟩)
6. (X(⟨omega, Y⟩) - ⟨omega, [X,Y]_VF⟩) - ((X(⟨omega, Y⟩) - Y(⟨omega, X⟩) - ⟨omega, [X,Y]_VF⟩) + Y(⟨omega, X⟩))  ->  0
```

Dropping the term $\langle d\, \iota_X \omega, Y \rangle$ gives a false identity. It is
refused, and the residual that remains is reported:

```python
try:
    jacopy.show_equal(lhs, jacopy.pairing(i_X(d(omega)), Y), registry=reg, engine=engine)
except jacopy.ProofFailure as failure:
    print("residual:", jacopy.to_ascii(failure.residual))
```

```text
residual: Y(⟨omega, X⟩)
```

## Contents

```{toctree}
:maxdepth: 1

installation
tutorials/index
howto/index
explanation/index
reference/index
development/index
```
