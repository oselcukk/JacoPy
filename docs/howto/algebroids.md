# Algebroids

An algebroid $(E,\rho,[\cdot,\cdot]_E)$ is a vector bundle with an anchor $\rho:E\to TM$ and
a bracket on sections. In JacoPy the axioms an algebroid satisfies are chosen explicitly:
nothing beyond the definitions holds unless it is declared. This page shows how to declare
axioms, how to write the structure maps, the algebroid calculus $d_E$, $\mathcal L^E$,
$\iota^E$, the Jacobiator, Derivator and Predator, the locality operator, and the reduction
to $E=TM$.

## Setup

```python
import jacopy
from jacopy.central.algebroid import (algebroid, tangent_algebroid, section_map,
                                      locality_projector, DECLARATIONS, LEVELS)

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y = jacopy.vector_fields("X Y")

E = algebroid("E", declare=("leibniz",))
u, v, w = E.sections("u v w")
(mu,) = jacopy.forms("mu", degree=1, bundle=E.bundle)
A = algebroid("A")
a1, a2, a3 = A.sections("u v w")
C = algebroid("C", declare=("courant",))
c1, c2, c3 = C.sections("u v w")
R = algebroid("R", declare=("local", "regular"))
r1, r2 = R.sections("u v")
(muR,) = jacopy.forms("mu", degree=1, bundle=R.bundle)
Pr = locality_projector(R)
Phi = section_map("Phi", A.bundle, A.bundle)
psi = section_map("psi", A.bundle, jacopy.TM)
TMa = tangent_algebroid()

from jacopy.central.algebroid import (d_E, lie_E, jacobiator, derivator, predator,
    anchor_predator, locality_term, LocalityOperator, algebroid_engine)
from jacopy.central.algebroid.calculus import evaluate, algebroid_calculus
```

## Declaring axioms

`algebroid("E", declare=(...))` takes a subset of axiom names. Declared axioms enter the
engine as axioms and are reported as such in every proof that uses them. The individual
axioms (`DECLARATIONS`) are:

```python
print(DECLARATIONS)
```

```text
('right-leibniz', 'left-leibniz', 'anchor-morphism', 'jacobi', 'antisymmetric', 'symmetric-part', 'metric-invariance', 'regular', 'bourbaki-invariance', 'courant-invariance', 'exact')
```

Level names (`LEVELS`) switch on several axioms at once. Axioms that can be derived from the
others are deliberately left out of the levels; they are provided as theorems instead.

| Level | Axioms it switches on |
|---|---|
| `almost-leibniz` | right-leibniz |
| `local` | right-leibniz, left-leibniz |
| `pre-leibniz` | right-leibniz, anchor-morphism |
| `leibniz` | right-leibniz, jacobi |
| `lie` | right-leibniz, antisymmetric, jacobi |
| `almost-courant` | right-leibniz, symmetric-part |
| `metric` | symmetric-part, metric-invariance |
| `pre-courant` | symmetric-part, metric-invariance, anchor-morphism |
| `courant` | symmetric-part, metric-invariance, jacobi |

## Structure maps

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\rho(u)$ | `E.anchor(u)` | u: section of E | vector field | `\rho\!\left(u\right)` | |
| $u(f)=\rho(u)(f)$ | `E.act(u, f)` | u; f | function | `\rho\!\left(u\right)\!\left(f\right)` | |
| $[u,v]_E$ | `E.bracket(u, v)` | u, v: sections of E | section of E | `\left[u,\, v\right]_{E}` | Sections do not act on functions directly |
| $Df=\rho^*df$ | `E.D(f)` | f | $E$-1-form | `d_{E}f` | |
| $\langle Df,u\rangle=\rho(u)f$ | `jacopy.pairing(E.D(f), u)` | | function | `\langle d_{E}f,\, u \rangle` | The engine reduces it to $\rho(u)(f)$ |
| $[u,fv]_E=\rho(u)(f)v+f[u,v]_E$ | `E.bracket(u, f*v)` | | section of E | `\left[u,\, f \, v\right]_{E}` | Expanded under the `right-leibniz` declaration |
| $g_C(u,v)$ | `C.metric(u, v)` | algebroid with fibre metric; sections | function | `g_{C}\!\left(u,\, v\right)` | Symmetric and non-degenerate by definition |
| $g^{-1}(Df)$ | `C.sharp(C.D(f))` | $E$-1-form | section of E | `g^{-1}\!\left(d_{C}f\right)` | |
| declaration query | `E.declares("jacobi")` | axiom name | bool | | `True` |
| adding a declaration | `A.with_declarations("jacobi")` | axiom names | a new algebroid | | The original algebroid is unchanged |

## Calculus: $d_E$, $\mathcal L^E$, $\iota^E$

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $d_E\mu$ | `d_E(E, mu)` | algebroid; $E$-form | $E$-form of degree $+1$ | `d_E\!\left(\mu\right)` | Palais formula under evaluation |
| $(d_E\mu)(u,v)$ | `evaluate(d_E(E, mu), u, v)` | head; sections | function | `\left(d_E\!\left(\mu\right)\right)\!\left(u,\, v\right)` | Same as `jacopy.multi_eval` |
| $\mathcal L^E_u$ | `lie_E(E, u)` | algebroid; section | operator | `L^E_{u}` | |
| $\mathcal L^E_uv=[u,v]_E$ | `lie_E(E, u)(v)` | | section of E | `L^E_{u}\!\left(v\right)` | |
| $\iota_u\mu$ | `jacopy.interior(u)(mu)` | section of E; $E$-form | $E$-form of degree $-1$ | `\iota_{u}\!\left(\mu\right)` | The same `interior` as on $TM$ |
| calculus object | `algebroid_calculus(E)` | algebroid | `BracketCalculus` | | Provides `.d` and `.lie(u)` |

## Jacobiator, Derivator, Predator

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $J^E(u,v,w)$ | `jacobiator(E, u, v, w)` | algebroid; three sections | section of E | `J_{E}\!\left(u,\, v,\, w\right)` | On $E$ (declared `jacobi`) the engine reduces it to 0; on $A$ (no axioms) it expands to $[u,[v,w]]-[[u,v],w]-[v,[u,w]]$ |
| $D^E_\Phi(u,v)$ | `derivator(A, Phi, a1, a2)` | algebroid; $\Phi:E\to E$; two sections | section of E | `D_{\Phi}\!\left(u,\, v\right)` | Build $\Phi$ first with `section_map` |
| $P^E_\psi(u,v)$ | `predator(A, psi, a1, a2)` | algebroid; $\psi:E\to TM$; two sections | vector field | `P_{\psi}\!\left(u,\, v\right)` | |
| $P^E_\rho(u,v)$ | `anchor_predator(A, a1, a2)` | algebroid; two sections | vector field | `P_{\rho}\!\left(u,\, v\right)` | $P_\rho\equiv0$ if and only if the anchor is a morphism |
| $\Phi(u)$ | `Phi(a1)` | map; section | section | `\Phi\!\left(u\right)` | |

`section_map("Phi", source, target)` takes **bundles** (`A.bundle`, `jacopy.TM`), not
algebroids.

## Locality

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $L(Df,u,v)$ | `locality_term(R, f, r1, r2)` | algebroid; f; u, v | section of E | `L\!\left(d_{R}f,\, u,\, v\right)` | The correction term of the left Leibniz rule |
| $L(\mu,u,v)$ (general form) | `LocalityOperator("R", muR, r1, r2)` | algebroid **name** (str); form; u, v | section of E | `L\!\left(\mu,\, u,\, v\right)` | Takes the name string, not the algebroid object |
| $\mathcal P(L(Df,u,v))$ | `Pr(locality_term(R, f, r1, r2))` | projector; section | section of E | `P\!\left(L\!\left(d_{R}f,\, u,\, v\right)\right)` | The engine with the projector reduces it to $L(Df,u,v)$ |
| $\rho(\mathcal P L(\mu,u,v))=0$ | `R.anchor(Pr(LocalityOperator("R", muR, r1, r2)))` | | vector field | `\rho\!\left(P\!\left(L\!\left(\mu,\, u,\, v\right)\right)\right)` | Kernel rule of the projector |

## Reduction to $TM$

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\rho=\mathrm{id}$ | `TMa.anchor(X)` | section of $TM$ | the same X | `X` | Returns `X` itself |
| $[\cdot,\cdot]_{TM}$ is the Lie bracket | `TMa.bracket(X, Y)` | | vector field | `\left[X,\, Y\right]` | |
| $D=d$ | `TMa.D(f)` | f | 1-form ($=df$) | `d\!\left(f\right)` | |
| $d_{TM}=d$ | `d_E(TMa, f)` | | 1-form | `d\!\left(f\right)` | `algebroid_engine(TMa)` is the tangent engine |

## Checking the entries with the engine

`algebroid_engine(E, registry=reg)` loads the definitions of $E$ together with its declared
axioms; `projectors=(Pr,)` adds the rules of a locality projector.

```python
engE = algebroid_engine(E, registry=reg)
engA = algebroid_engine(A, registry=reg)
engR = algebroid_engine(R, registry=reg, projectors=(Pr,))
checks = [
    (engE, jacopy.pairing(E.D(f), u), E.act(u, f)),
    (engE, E.bracket(u, f*v), E.act(u, f)*v + f*E.bracket(u, v)),
    (engE, lie_E(E, u)(v), E.bracket(u, v)),
    (engE, jacobiator(E, u, v, w), jacopy.Zero),
    (engR, Pr(locality_term(R, f, r1, r2)), locality_term(R, f, r1, r2)),
    (engR, R.anchor(Pr(LocalityOperator("R", muR, r1, r2))), jacopy.Zero),
]
for eng, lhs, rhs in checks:
    chain = jacopy.show_equal(lhs, rhs, registry=reg, engine=eng)
    print(jacopy.to_ascii(lhs), "closes in", len(chain.steps), "steps")
print(jacopy.to_ascii(engA.expand(jacobiator(A, a1, a2, a3))[0]))
```

```text
⟨Df, u⟩ closes in 2 steps
[u,(f * v)]_E closes in 2 steps
L^E_u(v) closes in 2 steps
J_E(u,v,w) closes in 2 steps
P(L(Df,u,v)) closes in 2 steps
ρ(P(L(mu,u,v))) closes in 2 steps
[u,[v,w]_A]_A - [[u,v]_A,w]_A - [v,[u,w]_A]_A
```
