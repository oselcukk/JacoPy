# Cartan calculus on the tangent bundle

This page shows how to write the differential operators of the Cartan calculus on $TM$: the
exterior derivative $d$, the interior product $\iota_X$, the Lie derivative $\mathcal L_X$,
the Lie bracket, the Schouten–Nijenhuis bracket, derived brackets, and the covariant
derivative together with frame (anholonomy) coefficients. Torsion and curvature are not part
of this layer; they are in the [metric-affine package](metric-affine.md).

## Setup

```python
import jacopy
from jacopy.core import Degree, Scalar
from jacopy.central.objects.frame import FrameIndex

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta = jacopy.forms("alpha beta", degree=1)
(omega,) = jacopy.forms("omega", degree=2)
p = Degree.var("p"); (eta,) = jacopy.forms("eta", degree=p)
P, Q = jacopy.p_vectors("P Q", degree=2)
pi = jacopy.bivector("pi")
(T,) = jacopy.tensors("T", upper=1, lower=2)
nabla = jacopy.connection()
e = jacopy.frame("e"); ce = jacopy.coframe("e")
ea, eb = e.fields("a b")

from jacopy.central.tangent import (d, L, SN, anholonomy_coefficient, multivector_degree,
                                    CARTAN_TM, cartan_calculus)
from jacopy.central.objects import contract, contract_all, tilde_interior, tilde_contract
from jacopy.central.objects.multivector_interior import MultivectorInterior
from jacopy.algebra.lie_bracket_vf import lie_bracket_vf
from jacopy.brackets.derived import derived_bracket
```

`d(...)` from `jacopy.central.tangent` is a **shortcut function**: `d(omega)` builds the
expression $d\omega$. The operator $d$ itself is {py:func}`jacopy.exterior_d`, and functions
that expect an operator (such as `jacopy.Act`, `diagnose` or `compose`) need the operator.

## Exterior derivative and interior product

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| calculus of $(TM,\mathrm{id},[\cdot,\cdot])$ | `cartan_calculus()` | | `BracketCalculus` | | The same object as `CARTAN_TM`; provides `.d` and `.lie(X)` |
| $d$ (operator) | `jacopy.exterior_d()` | | operator of degree $+1$ | `d` | |
| $df$ | `d(f)` | f: function | 1-form | `d\!\left(f\right)` | Same as `jacopy.exterior_d()(f)` |
| $d\omega$ | `d(omega)` | omega: $p$-form | $(p+1)$-form | `d\!\left(\omega\right)` | |
| $d\eta$, $\lvert\eta\rvert=p$ | `d(eta)` | form of symbolic degree | $(p+1)$-form | `d\!\left(\eta\right)` | |
| $\langle df,X\rangle=X(f)$ | `jacopy.pairing(d(f), X)` | | function | `\langle d\!\left(f\right),\, X \rangle` | The engine reduces it to $X(f)$ |
| $\iota_X$ (operator) | `jacopy.interior(X)` | X: vector field | operator of degree $-1$ | `\iota_{X}` | |
| $\iota_X\omega$ | `jacopy.interior(X)(omega)` | X: vector field; omega: $p$-form | $(p-1)$-form | `\iota_{X}\!\left(\omega\right)` | Construct the operator, then apply it |
| $\iota_X\omega$ (single call) | `contract(X, omega)` | X; omega | $(p-1)$-form | `\iota_{X}\!\left(\omega\right)` | |
| $\iota_Y\iota_X\omega=\omega(X,Y,\dots)$ | `contract_all(omega, X, Y)` | form; vectors, from the first slot | form or function | `\iota_{Y}\!\left(\iota_{X}\!\left(\omega\right)\right)` | |
| $(\iota_X\omega)(Y)=\omega(X,Y)$ | `jacopy.pairing(jacopy.interior(X)(omega), Y)` | | function | `\langle \iota_{X}\!\left(\omega\right),\, Y \rangle` | The engine reduces it to $\omega(X,Y)$ |

See {py:func}`jacopy.exterior_d` and {py:func}`jacopy.interior`.

## Lie derivative and Lie bracket

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\mathcal L_X$ (operator) | `jacopy.lie_derivative(X)` | X: vector field | operator of degree 0 | `\mathcal{L}_{X}` | |
| $\mathcal L_Xf$ | `jacopy.lie_derivative(X)(f)` | X; f: function | function ($=X(f)$) | `\mathcal{L}_{X}\!\left(f\right)` | |
| $\mathcal L_XY$ | `jacopy.lie_derivative(X)(Y)` | X, Y: vector fields | vector field ($=[X,Y]$) | `\mathcal{L}_{X}\!\left(Y\right)` | |
| $\mathcal L_X\omega$ | `jacopy.lie_derivative(X)(omega)` | X; omega: $p$-form | $p$-form | `\mathcal{L}_{X}\!\left(\omega\right)` | |
| $\mathcal L_X\omega$ (short) | `L(X, omega)` | X; any tensor | same type | `\mathcal{L}_{X}\!\left(\omega\right)` | `L` is `jacopy.central.tangent.L` |
| $\mathcal L_XT$ | `jacopy.lie_derivative(X)(T)` | X; T: $(q,r)$-tensor | $(q,r)$-tensor | `\mathcal{L}_{X}\!\left(T\right)` | Tensorial Lie derivative law under evaluation |
| $\mathcal L_XP=[X,P]_{SN}$ | `jacopy.lie_derivative(X)(P)` | X; P: $p$-vector | $p$-vector | `\mathcal{L}_{X}\!\left(P\right)` | |
| $[X,Y]$ | `jacopy.lie_bracket(X, Y)` | X, Y: vector fields | vector field | `\left[X,\, Y\right]` | |
| $[X,Y](f)$ | `jacopy.lie_bracket(X, Y)(f)` | bracket; function | function | `\left[X,\, Y\right]\!\left(f\right)` | The engine expands it to $X(Yf)-Y(Xf)$ |
| $[X,Y]$ (low level) | `lie_bracket_vf(X, Y)` | vector fields | vector field | `\left[X,\, Y\right]` | The same node as `jacopy.lie_bracket` |
| $[X,fY]=X(f)Y+f[X,Y]$ | `jacopy.lie_bracket(X, f*Y)` | | vector field | `\left[X,\, f \, Y\right]` | Closes through the action on a function |

See {py:func}`jacopy.lie_derivative` and {py:func}`jacopy.lie_bracket`.

## Schouten–Nijenhuis bracket

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $[P,Q]_{SN}$ | `jacopy.sn_bracket(P, Q)` | P, Q: multivectors (or functions) | $(p+q-1)$-vector | `\left[P,\, Q\right]_{[\cdot,\cdot]_{SN}}` | |
| $[P,Q]_{SN}$ (bracket object) | `SN(P, Q)` | same | same | `\left[P,\, Q\right]_{[\cdot,\cdot]_{SN}}` | `SN` is a graded bracket object |
| expansion of $[X,Y\wedge Z]_{SN}$ | `SN(X, jacopy.wedge(Y, Z)).expand(reg)` | bracket node; registry | expression | `\left[X,\, Y\right] \wedge Z + Y \wedge \left[X,\, Z\right]` | Expansion by definition |
| $[X,f]_{SN}=X(f)$ | `jacopy.sn_bracket(X, f)` | X; f | function | `\left[X,\, f\right]_{[\cdot,\cdot]_{SN}}` | |
| multivector degree | `multivector_degree(jacopy.wedge(X, Y))` | multivector | int or degree | | `2` |
| $[a,b]+(-1)^{s(a)s(b)}[b,a]$ | `SN.graded_antisymmetry_obstruction(X, Y, reg)` | a, b; registry | expression | `\left[X,\, Y\right]_{[\cdot,\cdot]_{SN}} + \left[Y,\, X\right]_{[\cdot,\cdot]_{SN}}` | Antisymmetry obstruction |
| cyclic Jacobi sum | `SN.graded_jacobi_obstruction(X, Y, Z, reg)` | a, b, c; registry | expression | | |
| $[a,bc]-[a,b]c\mp b[a,c]$ | `SN.leibniz_obstruction(X, Y, Z, reg)` | a, b, c; registry | expression | | |
| shifted degree $s(x)=\lvert x\rvert-1$ | `SN.operand_degree(P, reg)` | x; registry | degree | | `1` |
| swap sign | `SN.claimed_swap_sign(P, Q, reg)` | a, b; registry | sign | | `1` |
| Jacobi and Leibniz term signs | `(SN.jacobi_term_sign(X, Y, Z, reg), SN.leibniz_term_sign(X, Y, reg))` | | signs | | `(1, 1)` |
| bracket flags | `(SN.is_graded_antisymmetric, SN.satisfies_leibniz, SN.satisfies_graded_jacobi)` | | booleans | | `(True, True, True)` |

See {py:func}`jacopy.sn_bracket`.

## Derived bracket

The derived bracket $\{a,b\}_Q=[[a,Q],b]$ is built from a base bracket and a generator.

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\{\alpha,\beta\}_\pi=[[\alpha,\pi],\beta]_{SN}$ | `derived_bracket(SN, pi)(alpha, beta)` | base bracket; generator; two arguments | expression | `\left[\alpha,\, \beta\right]_{{\cdot,\cdot}_{\pi}}` | |
| expansion by definition | `derived_bracket(SN, pi)(alpha, beta).expand(reg)` | | expression | `\left[\left[\alpha,\, \pi\right]_{[\cdot,\cdot]_{SN}},\, \beta\right]_{[\cdot,\cdot]_{SN}}` | |
| $[[a,Q],b]$ without expanding the base | `derived_bracket(SN, pi).expand_definition(alpha, beta)` | a, b | expression | `\left[\left[\alpha,\, \pi\right]_{[\cdot,\cdot]_{SN}},\, \beta\right]_{[\cdot,\cdot]_{SN}}` | |
| the condition $[Q,Q]=0$ | `derived_bracket(SN, pi).jacobi_condition()` | | vanishing condition | | `.holds(reg)` checks whether it is 0 after simplification |
| does the condition hold? | `derived_bracket(SN, pi).jacobi_condition().holds(reg)` | registry | bool | | `False` here: nothing says $\pi$ is Poisson |
| Jacobi obstruction $[Q,Q]$ | `derived_bracket(SN, pi).jacobi_obstruction()` | | expression | `\left[\pi,\, \pi\right]_{[\cdot,\cdot]_{SN}}` | |
| $\lvert Q\rvert$ | `derived_bracket(SN, pi).generator_degree(reg)` | registry | degree | | `2` |

## Covariant derivative, frames, anholonomy

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\nabla_XY$ | `nabla(X, Y)` | X: vector field; Y: tensor | type of Y | `\nabla_{X}\!\left(Y\right)` | |
| $\nabla_XT$ | `jacopy.covariant_derivative(nabla, X, T)` | connection; X; T | type of T | `\nabla_{X}\!\left(T\right)` | |
| $\nabla_Xf=X(f)$ | `nabla(X, f)` | X; f | function | `\nabla_{X}\!\left(f\right)` | |
| $\nabla_X(fY)$ | `nabla(X, f*Y)` | | vector field | `\nabla_{X}\!\left(f \, Y\right)` | Expanded by the Leibniz rule |
| $[e_a,e_b]$ | `jacopy.lie_bracket(ea, eb)` | frame fields | vector field | `\left[e_{a},\, e_{b}\right]` | |
| $\gamma^c_{ab}$ | `anholonomy_coefficient(e, "c", "a", "b")` | frame; upper, lower, lower index | function | `\gamma^{c}_{ab}` | Gives $-\gamma^c_{ba}$ if $a>b$ and 0 if $a=b$ |
| $\langle e^c,[e_a,e_b]\rangle=\gamma^c_{ab}$ | `jacopy.pairing(ce.field("c"), jacopy.lie_bracket(ea, eb))` | | function | `\langle e^{c},\, \left[e_{a},\, e_{b}\right] \rangle` | The engine reduces it to $\gamma^c_{ab}$ |

See {py:func}`jacopy.connection` and {py:func}`jacopy.covariant_derivative`.

## Other interior products

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\tilde\iota_\alpha\pi$ | `tilde_interior(alpha)(pi)` | alpha: 1-form; pi: multivector | multivector | `\tilde{\iota}_{\alpha}\!\left(\pi\right)` | |
| $\tilde\iota_\alpha\pi$ (single call) | `tilde_contract(alpha, pi)` | | multivector | `\tilde{\iota}_{\alpha}\!\left(\pi\right)` | |
| $\iota_P\omega$ | `MultivectorInterior(pi)(omega)` | P: $p$-vector; omega: $q$-form | $(q-p)$-form | `\iota_{\pi}\!\left(\omega\right)` | Expanded by optional rules (see [Automatic rules](automatic-rules.md)) |

## Checking the meaning of an entry

Each "the engine reduces it to" note above can be confirmed with {py:func}`jacopy.show_equal`
and the tangent engine (see [Running proofs](running-proofs.md)):

```python
from jacopy.central.tangent import tangent_engine
eng = tangent_engine(registry=reg)
for lhs, rhs in [
    (jacopy.pairing(d(f), X), X(f)),
    (jacopy.pairing(jacopy.interior(X)(omega), Y), omega(X, Y)),
    (jacopy.lie_derivative(X)(Y), jacopy.lie_bracket(X, Y)),
    (jacopy.lie_bracket(X, f*Y)(h), X(f)*Y(h) + f*jacopy.lie_bracket(X, Y)(h)),
    (nabla(X, f), X(f)),
    (jacopy.pairing(ce.field("c"), jacopy.lie_bracket(ea, eb)), anholonomy_coefficient(e, "c", "a", "b")),
]:
    chain = jacopy.show_equal(lhs, rhs, registry=reg, engine=eng)
    print(jacopy.to_ascii(lhs), "closes in", len(chain.steps), "steps")
```

```text
⟨d(f), X⟩ closes in 2 steps
⟨ι_X(omega), Y⟩ closes in 2 steps
L_X(Y) closes in 2 steps
[X,(f * Y)]_VF(h) closes in 6 steps
∇_X(f) closes in 2 steps
⟨e^c, [e_a,e_b]_VF⟩ closes in 2 steps
```
