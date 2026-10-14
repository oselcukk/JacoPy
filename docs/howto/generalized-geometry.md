# Generalized geometry and Courant algebroids

The package `jacopy.packages.generalized` contains the axiomatics of Courant algebroids
(the LWX axioms [C1]–[C5], the Dorfman form [C'1]–[C'5] and the redundancy results of
Uchino), the standard, $H$-twisted, Poisson-generalized ($\theta$-double) and $R$-twisted
brackets on $TM\oplus T^*M$, Bourbaki algebroids, the general $\Psi$-twist, locality
projectors, and the exceptional structure on $TM\oplus\Lambda^2T^*M\oplus\Lambda^5T^*M$.
Source labels such as LWX, Uchino or B (with equation numbers) refer to the
[bibliography](../reference/bibliography.md).

## Setup

```python
import jacopy
reg = jacopy.PropertyRegistry()
f, g, h = jacopy.functions("f g h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta, gamma = jacopy.forms("alpha beta gamma", degree=1)

from jacopy.packages.generalized import (
    courant_context, dorfman_axiom_context, CourantD,
    courant_bracket_std, d_operator_std, courant_jacobiator_std, courant_t_scalar_std,
    courant_bracket_h,
    poisson_base, theta_anchor, theta_dorfman, theta_courant, d_operator_theta,
    r_term, r_twisted_theta_dorfman, lichnerowicz_d, lichnerowicz_calculus, RFluxClosureDeclaration,
    BourbakiPreCalculus, standard_bracket, standard_metric,
    bourbaki_structure_context, exact_bourbaki_context,
    PsiSec, PsiInvSec, twisted_bracket, twisted_anchor, twisted_metric, twisted_d,
    pi_block, pi_hat, exceptional_z_bracket, exceptional_lie_tilde, exceptional_double,
    rotated_exceptional_bracket, exceptional_r_twist, exceptional_r_twist_components,
    transported_form_pairing,
    linear_projector, b_field_projector, locally_exact_form, basis_pairing,
    courant_engine, bourbaki_engine, bourbaki_structure_engine, exact_bourbaki_engine,
    severa_engine, general_twist_engine, exceptional_rotation_engine, bridge_engine,
)
import jacopy.packages.generalized as generalized
from jacopy.packages.poisson import nambu_structure, poisson_structure
from jacopy.central.algebroid import algebroid
from jacopy.central.objects import frame, tensors
```

A few nodes of the Bourbaki structures are not exported by the facade and are imported
from submodules:

```python
from jacopy.packages.generalized.bourbaki_precalculus import (BD, BIota, BLieR, BLieZ,
    BSymbol, axiom_915_instance, Axiom914Declaration)
from jacopy.packages.generalized.bourbaki_structure import BMetric, BourbakiInvarianceDeclaration
from jacopy.packages.generalized.bourbaki_exact import PhiSec, ChiSec, IsotropyDeclaration
from jacopy.packages.generalized.bourbaki_severa import delta
```

A section $X+\alpha$ of $TM\oplus T^*M$ is passed as **two separate arguments**,
`(X, alpha)`. Brackets return a tuple of components: `(vector, form)`, or
`(vector, 2-form, 5-form)` in the exceptional case.

## How the objects are set up

```python
(H,) = jacopy.forms("H", degree=3)                  # H-flux
(B,) = jacopy.forms("B", degree=2)                  # B-field
(R,) = jacopy.p_vectors("R", degree=3)              # R-flux
theta = poisson_base()                              # Poisson bivector (Nambu, p = 1)
N1 = nambu_structure("theta", p=1)                  # the same, for the bridge theorems
P = poisson_structure()                             # pi, for the frame-component theorems
N3 = nambu_structure("Pi3", p=2)                    # Pi_3, a 3-vector
N6 = nambu_structure("Pi6", p=5)                    # Pi_6, a 6-vector
om2, et2 = jacopy.forms("omega2 eta2", degree=2)
om5, et5 = jacopy.forms("omega5 eta5", degree=5)
E = courant_context()                               # LWX Courant algebroid
x, y, z = E.sections("x y z")
Ed = dorfman_axiom_context()                        # Dorfman form, only [C'5] declared
Bp = BourbakiPreCalculus()
Eb = bourbaki_structure_context()
Ex = exact_bourbaki_context()
Eg = algebroid("E", declare=("right-leibniz", "jacobi", "symmetric-part", "metric-invariance"))
fr = frame()
(C,) = tensors("C", upper=0, lower=2)
f1, f2, g1, g2 = jacopy.functions("f1 f2 g1 g2", registry=reg)
```

The same objects, one by one:

| Math | In code | Note |
|---|---|---|
| $H\in\Omega^3(M)$ ($H$-flux) | `(H,) = jacopy.forms("H", degree=3)` | ordinary 3-form |
| $B\in\Omega^2(M)$ ($B$-field) | `(B,) = jacopy.forms("B", degree=2)` | Ševera B-transformation, the projector $P_B$ |
| $R\in\mathfrak X^3(M)$ ($R$-flux) | `(R,) = jacopy.p_vectors("R", degree=3)` | 3-vector |
| $\theta$ Poisson bivector (Nambu $p=1$) | `theta = poisson_base()` | `NambuPoissonStructure(θ, p=1)`; $(TM)_0\oplus(T^*M)_\theta$ and the $R$-flux are built on it |
| $\theta$ in the Nambu dialect | `N1 = nambu_structure("theta", p=1)` | only for the Nambu↔Poisson bridge theorems |
| $\pi$ in the Poisson dialect | `P = poisson_structure()` | for the frame-component theorems |
| $\Pi_3$ (3-vector), $\Pi_6$ (6-vector) | `N3 = nambu_structure("Pi3", p=2)`, `N6 = nambu_structure("Pi6", p=5)` | E6 block map |
| $\omega_2,\eta_2\in\Omega^2$, $\omega_5,\eta_5\in\Omega^5$ | `om2, et2 = jacopy.forms("omega2 eta2", degree=2)`, `om5, et5 = jacopy.forms("omega5 eta5", degree=5)` | form components of an E6 section |
| Abstract Courant algebroid $(E,\rho,[\cdot,\cdot],(\cdot,\cdot),\mathcal D)$, LWX | `E = courant_context()`; `x, y, z = E.sections("x y z")` | declarations: `anchor-morphism` [C2], `antisymmetric`, `courant-invariance` [C5] |
| Abstract Dorfman (non-skew) Courant algebroid | `Ed = dorfman_axiom_context()`; `Ed.sections("x y z")` | declaration: only `metric-invariance` [C'5] |
| Adding a declaration | `Ed.with_declarations("anchor-morphism")` | returns a new context; redundancy theorems raise `ValueError` if the axiom they are to prove is already declared |
| Bourbaki pre-calculus $(\iota,d,l,\mathcal L^R,\mathcal L^Z)$ | `Bp = BourbakiPreCalculus()`; `z, y = Bp.z_sections("z y")`; `(r,) = Bp.r_sections("r")` | $Z$-sections and $R$-sections |
| Bourbaki algebroid with an R-valued metric | `Eb = bourbaki_structure_context()`; `u, v = Eb.sections("u v")` | nothing declared; the (7.8) invariance is supplied via an engine parameter (`invariance=True`) |
| Exact pre-metric-Bourbaki algebroid ($\varphi,\chi$ splitting) | `Ex = exact_bourbaki_context()`; `(u,) = Ex.sections("u")` | declarations: `anchor-morphism`, `bourbaki-invariance`, `exact` |
| Initial algebroid for the general $\Psi$-twist | `Eg = algebroid("E", declare=("right-leibniz", "jacobi", "symmetric-part", "metric-invariance"))` | every property to be transported must be declared at the start |
| Frame $\{e_a\}$, coframe $\{e^a\}$ | `fr = frame()` | indices are strings: `"a"`, `"b"` |
| $(0,2)$-tensor $C$ | `(C,) = tensors("C", upper=0, lower=2)` | general locality projector $P_C$ |

### Declarations

No declaration is assumed silently. Most come into play through the `declare=` string of a
context or through the corresponding `prove_*` or engine parameter.

| Declaration (`Name`) | Axiom | How it is declared |
|---|---|---|
| `CourantInvarianceDeclaration` | [C5] $\rho(x)(y,z)=([x,y]+\mathcal D(x,y),z)+(y,[x,z]+\mathcal D(x,z))$ | inside `courant_context()` (`"courant-invariance"`); `courant_engine(E, reg, invariance=True)` |
| `C3IdentityDeclaration` | the Prop 2.1(i) identity $[x,fR]=f[x,R]+\rho(x)(f)R-(x,R)\mathcal Df$ (as a hypothesis) | `prove_leibniz_from_c3` registers it itself |
| `DNumericHomogeneityDeclaration` | $\mathcal D(c\,h)=c\,\mathcal Dh$, $\mathcal D(c)=0$ ($c$ a number) | theorem-class rule; derived by `prove_d_numeric_homogeneity` |
| `RFluxClosureDeclaration` | $d_\theta R=0$ | `RFluxClosureDeclaration(theta, R, reg)`; `prove_r_twisted_jacobi` registers it itself |
| `Axiom914Declaration` | (9.14) $\mathcal L^R_U\iota_Vz=\iota_{[U,V]}z+\iota_V\mathcal L^Z_Uz$ | inside `bourbaki_engine(reg)`; `Axiom914Declaration(bracket=...)` |
| `axiom_915_instance` | an instance of (9.15) $\iota_U(\mathcal L^Z_Vz-d\iota_Vz)+\iota_V(\mathcal L^Z_Uz-d\iota_Uz)=0$ | `axiom_915_instance(X, Y, z)` gives the expression declared to be zero: $\iota_{X}(L^Z_{Y}(z) - d(\iota_{Y}(z))) + \iota_{Y}(L^Z_{X}(z) - d(\iota_{X}(z)))$ |
| `BourbakiInvarianceDeclaration` | (7.8) $\mathcal L^R_{\rho u}g(v,w)=g([u,v],w)+g(v,[u,w])$ | `bourbaki_structure_engine(Eb, reg, invariance=True)`; `"bourbaki-invariance"` inside `exact_bourbaki_context()` |
| `IsotropyDeclaration` | $g$-isotropy of $\chi$: $g(\chi z,u)=\iota_{\rho u}z$, $g(\chi z,\chi y)=0$ | `exact_bourbaki_engine(Ex, reg, isotropic=True)` |

## Abstract Courant and Dorfman axioms

```python
x, y, z = E.sections("x y z")        # sections of the Courant algebroid E
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $[x,y]$ | `E.bracket(x, y)` | x, y: section of E | section of E: $\left[x,\, y\right]_{E}$ | In the Dorfman context `Ed.bracket` is printed the same way ($\circ$ is not written) |
| $(x,y)$ | `E.metric(x, y)` | x, y: section of E | function: $g_{E}\!\left(x,\, y\right)$ | symmetric, non-degenerate pairing |
| $\rho(x)$ | `E.anchor(x)` | x: section of E | vector field: $\rho\!\left(x\right)$ | |
| $\mathcal Df$ | `CourantD(E.name, f)` | first argument: the name of the context (str); f: function | section of E: $\mathcal{D}f$ | `E.D(f)` is a **different** node ($d_{E}f$, the algebroid coboundary); for the Courant $\mathcal D$ use `CourantD` |

The redundancy theorems are `prove_left_leibniz_c3`, `prove_anchor_annihilates_d`,
`prove_d_pairing_formula`, `prove_d_numeric_homogeneity`, `prove_leibniz_from_c3` and
`prove_bracket_with_d` on `courant_context()`, and `prove_dorfman_c3_redundant` and
`prove_dorfman_c2_redundant` on `dorfman_axiom_context()` (see the table below). For example:

```python
chain, thm = generalized.prove_left_leibniz_c3(E, x, y, f, registry=reg)
print(jacopy.to_ascii(thm.lhs), "=", jacopy.to_ascii(thm.rhs))
```

```text
[x,(f * y)]_E = f * [x,y]_E + ρ(x)(f) * y - g(x,y) * D(f)
```

## The standard Courant algebroid $TM\oplus T^*M$ and the $\mathcal D$-operator

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\mathcal D h=(0,\tfrac12dh)$ | `d_operator_std(f)` | f: function | (vector, form): $(0,\ \frac{1}{2} \, d\!\left(f\right))$ | |
| $[X+\alpha,Y+\beta]_C$ | `courant_bracket_std(X, alpha, Y, beta)` | X, Y: vector field; alpha, beta: 1-form | (vector, form): $\big(\left[X,\, Y\right],\ \mathcal{L}_{X}\beta - \mathcal{L}_{Y}\alpha + \frac{1}{2} \, d\iota_{Y}\alpha - \frac{1}{2} \, d\iota_{X}\beta\big)$ | skew (Courant) bracket; the Dorfman version is `dorfman_double` (Section 2) |
| $\sum_{\mathrm{cyc}}[[x,y]_C,z]_C$ (Courant Jacobiator) | `courant_jacobiator_std(X, alpha, Y, beta, Z, gamma)` | three sections, each (vector, 1-form) | (vector, form); vector: $\left[\left[X,\, Y\right],\, Z\right] + \left[\left[Y,\, Z\right],\, X\right] + \left[\left[Z,\, X\right],\, Y\right]$ | the form component is long |
| $T(x,y,z)=\tfrac13\sum_{\mathrm{cyc}}\langle[x,y]_C,z\rangle_+$ | `courant_t_scalar_std(X, alpha, Y, beta, Z, gamma)` | same | function: $\frac{1}{3} \, \big(\iota_{[X,Y]}\gamma + \iota_{Z}(\dots) + \dots\big)$ (abbreviated) | the $\mathcal D\,T$ term in [C1] |

## The $H$-twisted Courant algebroid

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $[X+\alpha,Y+\beta]_{C,H}$ | `courant_bracket_h(H, X, alpha, Y, beta)` | H: 3-form; X, Y: vector field; alpha, beta: 1-form | (vector, form): $\big(\left[X,\, Y\right],\ (\text{std. form}) + \iota_{Y}\iota_{X}H\big)$ | the vector component is the same as the standard one |

The related theorems are the `prove_twisted_*` builders and `prove_severa_twist_is_courant`
(the $B$-transformation, $H=dB$).

## Poisson-generalized geometry: $(TM)_0\oplus(T^*M)_\theta$

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\rho(U+\omega)=\theta^\sharp\omega$ | `theta_anchor(theta, X, alpha)` | theta: `poisson_base()`; X: vector field; alpha: 1-form | vector field: $\theta\!\left(\alpha\right)$ | $\theta^\sharp\alpha$ is printed in LaTeX as $\theta(\alpha)$ |
| tilde-Dorfman $[X+\alpha,Y+\beta]_\theta$ | `theta_dorfman(theta, X, alpha, Y, beta)` | same + Y, beta | (vector, form); form: $\mathcal{L}_{\theta(\alpha)}\beta - \dots$ (Koszul), vector: $\tilde{\mathcal L}_\alpha Y-\tilde{\mathcal L}_\beta X+\tilde d\tilde\iota_\beta X$ in expanded form | |
| tilde-Courant | `theta_courant(theta, X, alpha, Y, beta)` | same | (vector, form) | the antisymmetrization of the Dorfman bracket |
| $\mathcal D_\theta h=\tfrac12(-\theta^\sharp dh,0)$ | `d_operator_theta(theta, f)` | f: function | (vector, form): $\big(\frac{1}{2} \, (-\theta(d f)),\ 0\big)$ | |

## $R$-flux ($R$-twisted $\theta$-Dorfman bracket)

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\tilde\iota_\eta\tilde\iota_\omega R$ | `r_term(R, alpha, beta)` | R: 3-vector; alpha, beta: 1-form | vector field: $\tilde{\iota}_{\beta}\!\left(\tilde{\iota}_{\alpha}\!\left(R\right)\right)$ | |
| $[x,y]_{D,\theta,R}=[x,y]_{D,\theta}+(\tilde\iota_\eta\tilde\iota_\omega R,0)$ | `r_twisted_theta_dorfman(theta, R, X, alpha, Y, beta)` | theta, R, two sections | (vector, form); vector: $(\dots)+\tilde{\iota}_{\beta}\tilde{\iota}_{\alpha}R$ | the form component is the same as for $\theta$-Dorfman |
| $d_\theta R=[\theta,R]_{SN}$ | `lichnerowicz_d(theta, R)` | theta; R: multivector | multivector: $d_{\theta}\!\left(R\right)$ | |
| Lichnerowicz–Poisson calculus | `lichnerowicz_calculus(theta, registry=reg)` | theta | `BracketCalculus` object | the rules of $d_\theta$ |
| declaration $d_\theta R=0$ | `RFluxClosureDeclaration(theta, R, reg)` | theta, R | declaration rule | see the Declarations table above |

## The Roytenberg bracket and the Nambu–Poisson bridge

The Roytenberg bracket itself is in the [Drinfel'd package](drinfeld.md). This package
provides the identification theorems `prove_roytenberg_reduces_to_dorfman`,
`prove_roytenberg_is_theta_double_under_poisson`, `prove_roytenberg_h_is_twisted_dorfman`,
`prove_full_roytenberg_symmetric_part`, `prove_koszul_dialects_agree` and
`prove_theta_form_jacobi_by_citation`. The engine that brings the Nambu and Poisson
notations to a common normal form is `bridge_engine(N1, reg)`.

## Bourbaki algebroids

```python
z, y = Bp.z_sections("z y")          # Z-sections of the pre-calculus
(r,) = Bp.r_sections("r")            # an R-section
u, v = Eb.sections("u v")            # sections of the Bourbaki algebroid
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\iota_Uz\in\mathfrak X(R)$ | `BIota(X, z)` | U: vector field; z: Z-section | R-section: $\iota_{X}(z)$ | |
| $dr\in\mathfrak X(Z)$ | `BD(r)` | r: R-section | Z-section: $d(r)$ | |
| $l_{df}r$ (symbol) | `BSymbol(f, r)` | f: function; r: R-section | Z-section: `l_df(r)` | its LaTeX is plain text |
| $\mathcal L^R_Ur$ | `BLieR(X, r)` | U: vector field; r: R-section | R-section: `L^R_{X}(r)` | only ℝ-bilinear |
| $\mathcal L^Z_Vz$ | `BLieZ(Y, z)` | V: vector field; z: Z-section | Z-section: `L^Z_{Y}(z)` | |
| $[U+z,V+y]_S=[U,V]+\mathcal L^Z_Uy-\mathcal L^Z_Vz+d\iota_Vz$ | `standard_bracket(X, z, Y, y)` | U, V: vector field; z, y: Z-section | (vector, Z-section): $\big(\left[X,\, Y\right],\ L^Z_{X}(y) - L^Z_{Y}(z) + d(\iota_{Y}(z))\big)$ | the base bracket can be changed with `bracket=` |
| $g_S=\iota_Uy+\iota_Vz$ | `standard_metric(X, z, Y, y)` | same | R-section: $\iota_{X}(y) + \iota_{Y}(z)$ | |
| $g(u,v)\in\mathfrak X(R)$ | `BMetric(u, v)` | u, v: section of E (`Eb`) | R-section: $g(u,v)$ | `Eb.metric(u, v)` is a different node ($g_E$) |
| $\varphi(U)$ | `PhiSec(X)` | U: vector field | section of E: $\phi(X)$ | right splitting |
| $\chi(z)$ | `ChiSec(z)` | z: Z-section | section of E: $\chi(z)$ | $Z\hookrightarrow E$ |
| $\Delta(U,V)=[\varphi U,\varphi V]_E-\varphi[U,V]$ | `delta(Ex, X, Y)` | Ex: `exact_bourbaki_context()`; U, V: vector field | section of E: $\left[\phi(X),\, \phi(Y)\right]_{E} - \phi(\left[X,\, Y\right])$ | $\chi H=\Delta$ in the Ševera classification |

## The general $\Psi$-twist

```python
u, v = Eg.sections("u v")
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\Psi(u)$, $\Psi^{-1}(u)$ | `PsiSec(u)`, `PsiInvSec(u)` | u: section of E | section of E: $\Psi(u)$, $\Psi^{-1}(u)$ | $\Psi$ is opaque, invertible, $C^\infty$-linear |
| $[u,v]'=\Psi^{-1}[\Psi u,\Psi v]$ | `twisted_bracket(Eg, u, v)` | Eg: algebroid; u, v: section of E | section of E: $\Psi^{-1}(\left[\Psi(u),\, \Psi(v)\right]_{E})$ | |
| $\rho'=\rho\circ\Psi$ | `twisted_anchor(Eg, u)` | Eg; u | vector field: $\rho\!\left(\Psi(u)\right)$ | |
| $g'(u,v)=g(\Psi u,\Psi v)$ | `twisted_metric(u, v)` | u, v: section of E | $g(\Psi(u),\Psi(v))$ | |
| $\mathbb D'=\Psi^{-1}\circ\mathbb D$ | `twisted_d(f)` | a function or $R$-section | $\Psi^{-1}(\mathbb{D}(f))$ | |

## Locality projectors and frame components

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $P_C(U,\omega)=(0,\omega+C(U,\cdot))$ | `linear_projector(C, X, alpha)` | C: (0,2)-tensor (a 2-form also works); X: vector field; alpha: 1-form | (vector, form): $\big(0,\ \alpha + C\!\left(X,\, \cdot\right)\big)$ | `TypeError` if a 1-form is given |
| $P_B(U,\omega)=(0,\omega+\iota_UB)$ | `b_field_projector(B, X, alpha)` | B: 2-form; U; omega | (vector, form): $\big(0,\ \alpha + \iota_{X}\!\left(B\right)\big)$ | |
| $\sum_if_i\,dg_i$ | `locally_exact_form((f1, f2), (g1, g2))` | two sequences of functions | 1-form: $f1 \, d\!\left(g1\right) + f2 \, d\!\left(g2\right)$ | |
| $\langle e_a\oplus e^b,e_c\oplus e^d\rangle_+$ | `basis_pairing(fr, "a", "b", "c", "d")` | fr: `frame()`; four index names | (explicit pairing, value): $\big(\iota_{e_{a}}e^{d} + \iota_{e_{c}}e^{b},\ \delta^{b}_{c} + \delta^{d}_{a}\big)$ | |

## The exceptional structure $TM\oplus\Lambda^2T^*M\oplus\Lambda^5T^*M$

A section $U+\omega_2+\omega_5$ is passed as **three arguments**: `(U, om2, om5)`.

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\Delta U=\Pi_3\omega_2+\Pi_6\omega_5+(\Pi_3\circledast\Pi_3)\omega_5$ | `pi_block(N3, N6, om2, om5)` | N3, N6: Nambu ($p=2$, $p=5$); om2: 2-form; om5: 5-form | vector field: $\Pi3(\omega2) + \Pi6(\omega5) + \frac{1}{2} \, \Pi3(\iota_{\Pi3}\omega5)$ | $\circledast\omega_5=\tfrac12\Pi_3(\iota_{\Pi_3}\omega_5)$ |
| $\hat\Pi\omega_5=(\Pi_6+\Pi_3\circledast\Pi_3)\omega_5$ | `pi_hat(N3, N6, om5)` | N3, N6; om5 | vector field: $\Pi6(\omega5) + \frac{1}{2} \, \Pi3(\iota_{\Pi3}\omega5)$ | |
| $[\omega,\eta]_Z$ | `exceptional_z_bracket(N3, N6, om2, om5, et2, et5)` | two form pairs | (2-form, 5-form): $\big(\mathcal{L}_{\Pi\omega}\eta2 - \iota_{\Pi\eta}d\omega2,\ \dots\big)$ | |
| $\tilde{\mathcal L}_\omega W$ | `exceptional_lie_tilde(N3, N6, om2, om5, Y)` | form pair; W: vector field | vector field: $[\Pi\omega,\, Y] + \Pi3(\iota_{Y}d\omega2) + \dots$ | |
| Drinfel'd double $[x,y]_{\mathrm{double}}$ | `exceptional_double(N3, N6, X, om2, om5, Y, et2, et5)` | two sections (vector, 2-form, 5-form) | (vector, 2-form, 5-form); 2-form: $(\mathcal{L}_{\Pi\omega}\eta2 - \iota_{\Pi\eta}d\omega2) + \mathcal{L}_{X}\eta2 - \iota_{Y}\dots$ | |
| $\Psi_\Pi^{-1}[\Psi_\Pi x,\Psi_\Pi y]_{\mathrm{exc}}$ | `rotated_exceptional_bracket(N3, N6, X, om2, om5, Y, et2, et5)` | same | (vector, 2-form, 5-form); 2-form: $\mathcal{L}_{X + \Pi\omega}\eta2 - \iota_{Y + \Pi\eta}d\omega2$ | |
| $R'(\omega,\eta)=[\Pi\omega,\Pi\eta]-\Pi[\omega,\eta]_Z$ | `exceptional_r_twist(N3, N6, om2, om5, et2, et5)` | two form pairs | vector field: $[\Pi\omega,\Pi\eta] - \Pi3(\dots) - \dots$ | |
| $R'_{22},R'_{25},R'_{52},R'_{55}$ | `exceptional_r_twist_components(N3, N6, om2, om5, et2, et5)` | same | `dict`, keys `'22'`, `'25'`, `'52'`, `'55'` | |
| transported pairing $P'_2,P'_5$ | `transported_form_pairing(N3, N6, om2, om5, et2, et5)` | same | (function/form, …): $\iota_{\Pi\omega}\eta2 + \iota_{\Pi\eta}\omega2,\ \dots$ | |

In the results, $\Pi\omega$ abbreviates $\Pi_3\omega_2+\Pi_6\omega_5+\tfrac12\Pi_3(\iota_{\Pi_3}\omega_5)$;
the actual output writes the sum out.

## Engines

The `prove_*` builders set up their own engines. The engines below are ready-made rule sets
for trying an identity of your own with {py:func}`jacopy.show_equal` or
`jacopy.proof.result.prove`; each returns an `ExpansionEngine`.

| Engine | Call | Contents |
|---|---|---|
| LWX Courant | `courant_engine(E, reg, invariance=True)` | [C5] + (L) + skew + pairing rules |
| Bourbaki pre-calculus | `bourbaki_engine(reg)` | quintuple laws + (9.14) |
| Bourbaki structure | `bourbaki_structure_engine(Eb, reg, invariance=True)` | $\mathbb D$, $\mathcal L^R$ laws + (7.8) |
| Exact Bourbaki | `exact_bourbaki_engine(Ex, reg, isotropic=False)` | splitting ($\rho\varphi=\mathrm{id}$, $\rho\chi=0$), (8.3), (9.7), (9.9) |
| Ševera | `severa_engine(Ex, reg)` | the above + citation of the proven Leibniz rules |
| General $\Psi$-twist | `general_twist_engine(Eg, reg)` | $\Psi$ invertibility and linearity |
| E6 rotation | `exceptional_rotation_engine(N3, reg)` | Nambu/multiple interior product rules |
| Nambu↔Poisson bridge | `bridge_engine(N1, reg)` | common normal form of the two dialects |

## Theorem builders

Every builder is called as `generalized.prove_x(<arguments>, registry=reg)`. In the
$TM\oplus T^*M$ component theorems (`*_std`, `prove_twisted_*`, `prove_theta_*`, ...) the
returned `Theorem` records the difference of one component ($\dots-\dots=0$), while the
chain closes the vector and form components in separate steps. Some returned `Theorem`
records are marked `legacy=True`; such a record can be cited in another proof only with
`allow_legacy=True` (see `check_citation` on the [Running proofs](running-proofs.md) page).
The last column notes builders that rely on a declared axiom and builders that are slow.

| Builder | Identity it proves | Arguments | Returns | Note |
|---|---|---|---|---|
| `generalized.prove_anchor_annihilates_d` | [C4] $\rho(\mathcal Df)(h)=0$ (Uchino Prop 2.1(ii)) | `alg`: `courant_context()`, `x`: section of E, `y`: section of E, `f`: function, `h`: function, `c3`=None | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_bracket_with_d` | $[x,\mathcal Df]+\mathcal D(x,\mathcal Df)=\mathcal D(\rho(x)f)$; `classical=True`: $[x,\mathcal Df]=\mathcal D(x,\mathcal Df)$ (Rem 2.2) | `alg`: `courant_context()`, `x`: section of E, `y`: section of E, `f`: function, `classical`=False | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_d_numeric_homogeneity` | $\mathcal D(cf)=c\,\mathcal Df$, $c$ a number (derived, not declared) | `alg`: `courant_context()`, `y`: section of E, `f`: function, `c`: number (`Integer`/`Rational`) | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_d_pairing_formula` | $(\mathcal Df,y)=\tfrac12\rho(y)(f)$ (Uchino Prop 2.2) | `alg`: `courant_context()`, `x`: section of E, `y`: section of E, `f`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_left_leibniz_c3` | [C3] $[x,fy]=f[x,y]+\rho(x)(f)\,y-(x,y)\,\mathcal Df$ (Uchino Prop 2.1(i): from [C2]+[C5]+(L)) | `alg`: `courant_context()`, `x`: section of E, `y`: section of E, `f`: function, `w`=None, `invariance`=True | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_leibniz_from_c3` | identity (i) $\Rightarrow$ (L) $\mathcal D(fg)=f\mathcal Dg+g\mathcal Df$ (Uchino Rem 2.1) | `alg`: `courant_context()`, `x`: section of E, `y`: section of E, `f`: function, `g`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_dorfman_c2_redundant` | [C'2] $\rho(x\circ y)(f)=\rho(x)\rho(y)f-\rho(y)\rho(x)f$ | `alg`: `dorfman_axiom_context()`, `x`: section of E, `y`: section of E, `z`: section of E, `f`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_dorfman_c3_redundant` | [C'3] $x\circ(fy)=f\,(x\circ y)+\rho(x)(f)\,y$ (from [C'5] alone) | `alg`: `dorfman_axiom_context()`, `x`: section of E, `y`: section of E, `f`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_anchor_morphism_std` | [C'2] $TM\oplus T^*M$: $\rho([x,y]_D)=[\rho x,\rho y]$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_courant_c3_lwx_std` | LWX [C3] $[x,fy]_C=f[x,y]_C+(\rho(x)f)\,y-\langle x,y\rangle_+\mathcal Df$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_courant_dorfman_relation` | $[x,y]_C=[x,y]_D-\mathcal D\langle x,y\rangle_+$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_courant_jacobi_dt_std` | [C1] $\sum_{\mathrm{cyc}}[[x,y]_C,z]_C=\mathcal D\,T(x,y,z)$, $T=\tfrac13\sum_{\mathrm{cyc}}\langle[x,y]_C,z\rangle_+$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `mu`: 1-form, `f`: function, `slots`: tuple of vector fields, `max_steps`=30000 | `(ProofChain, list[Theorem])` |  |
| `generalized.prove_courant_skew_std` | $[x,y]_C+[y,x]_C=0$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_dorfman_invariance_std` | [C'5] $\rho(x)\langle y,z\rangle_+=\langle x\circ y,z\rangle_++\langle y,x\circ z\rangle_+$ | `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_severa_twist_is_courant` | if $H=dB$, Jacobi closes (Ševera B-transformation) | `B`: 2-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `mu`: 1-form, `f`: function, `slots`: tuple of vector fields, `max_steps`=60000 | `(ProofChain, list[Theorem])` |  |
| `generalized.prove_twisted_anchor_morphism` | [C'2] for the H-twisted Dorfman | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_twisted_courant_dorfman_relation` | $[x,y]_{C,H}=[x,y]_{D,H}-\mathcal D\langle x,y\rangle_+$ | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_twisted_invariance` | [C'5] (thanks to $\iota_W\iota_V\iota_UH+\iota_V\iota_W\iota_UH=0$) | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_twisted_jacobi_dh_defect` | [C'1] defect $=\iota_W\iota_V\iota_U\,dH$ | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `mu`: 1-form, `f`: function, `slots`: tuple of vector fields, `max_steps`=60000 | `(ProofChain, list[Theorem])` |  |
| `generalized.prove_twisted_right_leibniz` | [C'3] for the H-twisted Dorfman | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_twisted_symmetric_part` | [C'4] $[x,y]_H+[y,x]_H=2\mathcal D\langle x,y\rangle_+$ ($\mathcal D$ unchanged) | `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_anchor_morphism` | [C'2] for the $\theta^\sharp$-anchor $\rho([x,y]_\theta)(h)=[\rho x,\rho y](h)$ (under the Poisson declaration) | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `h`: function, `declare_poisson`=True | `ProofChain` | no `Theorem` record |
| `generalized.prove_theta_courant_skew` | the $\theta$-Courant bracket is antisymmetric | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_d_pairing_value` | $\langle\mathcal D_\theta h,x\rangle_+=\tfrac12\rho(x)(h)$ | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `h`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_invariance` | [C'5] for the $\theta$-double | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form, `declare_poisson`=True | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_jacobi` | [C'1] $\theta$-double Leibniz–Jacobi (under the Poisson declaration) | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form, `h`: function, `X`: vector field, `declare_poisson`=True, `max_rounds`=15 | `(ProofChain, Theorem)` | a declared axiom; slow |
| `generalized.prove_theta_right_leibniz` | [C'3] on $(TM)_0\oplus(T^*M)_\theta$ | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_symmetric_part` | [C'4] $[x,y]+[y,x]=2\mathcal D_\theta\langle x,y\rangle_+$ | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_derived_r_vanishes_under_poisson` | $[\theta^\sharp\omega,\theta^\sharp\eta]-\theta^\sharp[\omega,\eta]_\theta=0$ | `N`: `poisson_base()` / Nambu $p=1$, `omega`: 1-form, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_r_twisted_anchor_morphism` | [C'2] is preserved (the R-term lies in $\ker\rho$) | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `h`: function, `declare_poisson`=True, `max_steps`=60000 | `ProofChain` | no `Theorem` record |
| `generalized.prove_r_twisted_courant_relation` | R-twisted Courant = antisymmetric part of Dorfman | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_r_twisted_jacobi` | [C'1] under the Poisson + $d_\theta R=0$ declarations | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form, `h`: function, `X`: vector field, `cite_theta_jacobi`=True | `(ProofChain, Theorem)` | a declared axiom; slow |
| `generalized.prove_r_twisted_jacobi_defect_is_dtheta_r` | $\mathrm{vec}(J_R-J_\theta)(h)=(d_\theta R)(\omega,\eta,\zeta,dh)$ | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `W`: vector field, `zeta`: 1-form, `h`: function, `max_steps`=40000 | `(ProofChain, Theorem)` | slow |
| `generalized.prove_r_twisted_right_leibniz` | [C'3]: $\tilde\iota_{f\eta}\tilde\iota_\omega R=f\,\tilde\iota_\eta\tilde\iota_\omega R$ | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_r_twisted_symmetric_part` | [C'4]: $\tilde\iota_\eta\tilde\iota_\omega R+\tilde\iota_\omega\tilde\iota_\eta R=0$ | `N`: `poisson_base()` / Nambu $p=1$, `R`: 3-vector, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_full_roytenberg_symmetric_part` | all switched on: [C'4], $\mathcal D_\theta$ is preserved | `N`: `poisson_base()` / Nambu $p=1$, `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_roytenberg_h_is_twisted_dorfman` | only H switched on: Roytenberg = H-twisted Dorfman | `N`: `poisson_base()` / Nambu $p=1$, `H`: 3-form, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_roytenberg_is_theta_double_under_poisson` | tilde + R switched on, Poisson: Roytenberg = $\theta$-double | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `declare_poisson`=True | `(ProofChain, Theorem)` |  |
| `generalized.prove_roytenberg_reduces_to_dorfman` | all switches off: Roytenberg = standard Dorfman | `N`: `poisson_base()` / Nambu $p=1$, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_koszul_dialects_agree` | $\mathcal L_{\theta^\sharp\omega}\eta-\iota_{\theta^\sharp\eta}d\omega=[\omega,\eta]_\theta$ (Nambu $p=1$ ↔ Poisson dialect) | `N`: `poisson_base()` / Nambu $p=1$, `omega`: 1-form, `eta`: 1-form, `X`: vector field | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_form_jacobi_by_citation` | [C'1] form component = Koszul–Jacobi on 1-forms (by citation) | `N`: `poisson_base()` / Nambu $p=1$, `omega`: 1-form, `eta`: 1-form, `zeta`: 1-form, `X`: vector field, `f`: function, `declare_poisson`=True | `(ProofChain, Theorem)` | a declared axiom; slow |
| `generalized.prove_cartan_satisfies_914` | (9.14) $\mathcal L_U\iota_V\omega=\iota_{[U,V]}\omega+\iota_V\mathcal L_U\omega$ (ordinary Cartan) | `U`: vector field, `V`: vector field, `omega`: form, `slots`: tuple of vector fields | `ProofChain` | no `Theorem` record |
| `generalized.prove_cartan_satisfies_915` | (9.15) $\iota_U(\mathcal L_V\omega-d\iota_V\omega)=-\iota_V(\mathcal L_U\omega-d\iota_U\omega)$ | `U`: vector field, `V`: vector field, `omega`: form, `slots`: tuple of vector fields | `ProofChain` | no `Theorem` record |
| `generalized.prove_standard_metric_invariance` | (7.8) invariance $\mathcal L^R_U g_S(\cdot,\cdot)$ (with (9.14),(9.15)) | `U`: vector field, `z`: Z-section, `V`: vector field, `y`: Z-section, `W`: vector field, `x`: Z-section, `bracket`, `base_engine`=None | `(ProofChain, Theorem)` |  |
| `generalized.prove_standard_symmetric_part` | $[U+z,V+y]_S+[V+y,U+z]_S=d\,g_S$ | `U`: vector field, `z`: Z-section, `V`: vector field, `y`: Z-section, `bracket`, `base_engine`=None | `(ProofChain, Theorem)` |  |
| `generalized.prove_left_leibniz_bourbaki` | $[fu,v]=f[u,v]-\rho(v)(f)\,u+\mathbb L_{df}(g(u,v))$ | `alg`: `bourbaki_structure_context()`, `u`: section of E, `v`: section of E, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_locality_is_symbol` | $L(df,u,v)=\mathbb L_{df}(g(u,v))$ (B Cor 6.1) | `alg`: `bourbaki_structure_context()`, `u`: section of E, `v`: section of E, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_right_leibniz_from_r_invariance` | $[u,fv]=f[u,v]+\rho(u)(f)\,v$ (B (7.2)) | `alg`: `bourbaki_structure_context()`, `u`: section of E, `v`: section of E, `f`: function, `w`=None | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_911` | (9.11): the induced quintuple satisfies (9.15) | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `z`: Z-section | `(ProofChain, Theorem)` |  |
| `generalized.prove_912` | (9.12): (9.14) with isotropic $\chi$ | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `z`: Z-section | `(ProofChain, Theorem)` |  |
| `generalized.prove_lemma_91` | $\rho([u,\chi z])(h)=0$ (B Lemma 9.1) | `alg`: `exact_bourbaki_context()`, `u`: section of E, `z`: Z-section, `h`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_chi_chi_bracket_vanishes` | $[\chi z,\chi y]=0$ | `alg`: `exact_bourbaki_context()`, `z`: Z-section, `y`: Z-section, `w`=None | `(ProofChain, Theorem)` |  |
| `generalized.prove_chi_phi_bracket` | $[\chi z,\varphi V]=\chi(-\mathcal L^Z_Vz+d\iota_Vz)$ | `alg`: `exact_bourbaki_context()`, `V`: vector field, `z`: Z-section | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_delta_first_slot_anomaly` | $\Delta(fU,V)=f\,\Delta(U,V)+\chi(l_{df}F(U,V))$, $F=g(\varphi U,\varphi V)$ | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_delta_lands_in_chi` | $\rho(\Delta(U,V))=0$ | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `h`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_delta_tensorial_second_slot` | $\Delta(U,fV)=f\,\Delta(U,V)$ | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `f`: function | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_h_antisymmetric_for_isotropic_phi` | $\Delta(U,V)+\Delta(V,U)=\chi(dF(U,V))$; isotropic $\varphi$: $=0$ | `alg`: `exact_bourbaki_context()`, `U`: vector field, `V`: vector field, `isotropic_phi`=True | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_general_twist_bilinearity` | $[u+w,v]'=[u,v]'+[w,v]'$, $[u,v]'=\Psi^{-1}[\Psi u,\Psi v]$ | `alg`: `algebroid(..., declare=...)`, `u`: section of E, `v`: section of E, `w`: section of E | `(ProofChain, Theorem)` |  |
| `generalized.prove_general_twist_invariance` | $\rho'(u)g'(v,w)=g'([u,v]',w)+g'(v,[u,w]')$ | `alg`: `algebroid(..., declare=...)`, `u`: section of E, `v`: section of E, `w`: section of E, `declare_r_axioms`=False | `(ProofChain, Theorem)` |  |
| `generalized.prove_general_twist_jacobi` | twisted Jacobiator $=\Psi^{-1}$(original Jacobiator) | `alg`: `algebroid(..., declare=...)`, `u`: section of E, `v`: section of E, `w`: section of E | `(ProofChain, Theorem)` | a declared axiom |
| `generalized.prove_general_twist_right_leibniz` | $[u,fv]'=f[u,v]'+\rho'(u)(f)\,v$, $\rho'=\rho\circ\Psi$ | `alg`: `algebroid(..., declare=...)`, `u`: section of E, `v`: section of E, `f`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_general_twist_symmetric_part` | $[u,v]'+[v,u]'=\mathbb D'g'(u,v)$ | `alg`: `algebroid(..., declare=...)`, `u`: section of E, `v`: section of E, `declare_r_axioms`=False | `(ProofChain, Theorem)` |  |
| `generalized.prove_b_field_projector_is_a_locality_projector` | $P_B(U,\omega)=(0,\omega+\iota_UB)$ is a locality projector (6 conditions) | `B`: 2-form, `U`: vector field, `omega`: 1-form, `h`: function, `g`: function, `V`=None, `eta`=None | `(ProofChain, Theorem)` |  |
| `generalized.prove_linear_projector_is_a_locality_projector` | $P_C(U,\omega)=(0,\omega+C(U,\cdot))$ is a locality projector (6 conditions) | `C`: (0,2)-tensor, `U`: vector field, `omega`: 1-form, `V`: vector field, `eta`: 1-form, `h`: function, `g`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_projector_differs_from_pr2_on_a_frame` | $\langle P_B(e_0,0)-\mathrm{pr}_2(e_0,0),e_1\rangle=1$, $B=e^0\wedge e^1$ | `fr`: `frame()`, `dim`=2 | `(ProofChain, Theorem)` |  |
| `generalized.prove_projector_fixes_locally_exact_forms` | $\tilde{\mathcal P}(\sum_i f_i\,dg_i)=\sum_i f_i\,dg_i$ | `fs`: sequence of functions, `gs`: sequence of functions, `projector_name`='𝒫' | `(ProofChain, Theorem)` |  |
| `generalized.prove_anchor_components` | $\langle e^c,\pi^\sharp e^b\rangle=\pi(e^b,e^c)$ | `P`: `PoissonStructure`, `fr`: `frame()`, `b_up`: index name (str), `c_up`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_basis_pairing_components` | $\langle e_a\oplus e^b,e_c\oplus e^d\rangle_+=\delta^b_c+\delta^d_a$ | `fr`: `frame()`, `a`: index name (str), `b_up`: index name (str), `c`: index name (str), `d_up`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_boxtimes_components_are_413` | $\langle e^c,(\Pi_3\circledast\Pi_3)(e^{a_1}\wedge\dots\wedge e^{a_5})\rangle=5\,\Pi^{[a_1a_2a_3}\Pi^{a_4a_5]c}$ | `N3`: `nambu_structure(p=2)`, `fr`: `frame()`, `indices`: 5 index names (str), `c_up`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_dorfman_form_components` | $\langle\mathcal L_{e_a}e^d,e_b\rangle=-\gamma^d_{ab}$ | `fr`: `frame()`, `a`: index name (str), `d_up`: index name (str), `b`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_dorfman_vector_components` | $\langle e^u,[e_a,e_c]\rangle=\gamma^u_{ac}$ | `fr`: `frame()`, `upper`: index name (str), `a`: index name (str), `c`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_theta_koszul_components` | $\langle[e^a,e^b]_\pi,e_c\rangle=\tilde\gamma_c{}^{ab}$ | `P`: `PoissonStructure`, `fr`: `frame()`, `a_up`: index name (str), `b_up`: index name (str), `c`: index name (str) | `(ProofChain, Theorem)` |  |
| `generalized.prove_rotated_form_decomposition` | $\mathrm{form}_k'=\mathrm{form}_k+\mathcal L_{\Delta U}\eta_k-\iota_{\Delta V}d\omega_k$ ($k=2,5$) | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `U`: vector field, `om2`: 2-form, `om5`: 5-form, `V`: vector field, `et2`: 2-form, `et5`: 5-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_rotated_vector_decomposition` | $\mathrm{vec}'=[U+\Delta U,V+\Delta V]-\Pi_3(\mathrm{form}_2')-\Pi_6(\mathrm{form}_5')-\circledast(\mathrm{form}_5')$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `U`: vector field, `om2`: 2-form, `om5`: 5-form, `V`: vector field, `et2`: 2-form, `et5`: 5-form | `(ProofChain, Theorem)` |  |
| `generalized.prove_exceptional_r_twist_bidegree_split` | $R'=R'_{22}+R'_{25}+R'_{52}+R'_{55}$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `om2`: 2-form, `om5`: 5-form, `et2`: 2-form, `et5`: 5-form, `h`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_exceptional_r_twist_symmetric_part` | $R'(\omega,\eta)+R'(\eta,\omega)=-\Pi_3dP'_2-\hat\Pi dP'_5$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `om2`: 2-form, `om5`: 5-form, `et2`: 2-form, `et5`: 5-form, `h`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_r22_reduces_to_lifted_cross_term` | under the $\Pi_3$ FI declaration $R'_{22}=\hat\Pi(\eta_2\wedge d\omega_2)$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `om2`: 2-form, `et2`: 2-form, `h`: function, `declare_fi`=True | `(ProofChain, Theorem)` |  |
| `generalized.prove_r25_is_lie_tilde_equivariance_defect` | $R'_{25}=\tilde{\mathcal L}_{\omega_2}(\hat\Pi\eta_5)-\hat\Pi(\mathcal L_{\Pi_3\omega_2}\eta_5)$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `om2`: 2-form, `et5`: 5-form, `h`: function | `(ProofChain, Theorem)` |  |
| `generalized.prove_rotated_is_exceptional_double_plus_r` | $\Psi_\Pi^{-1}[\Psi_\Pi x,\Psi_\Pi y]_{\mathrm{exc}}=[x,y]_{\mathrm{double}}+(R'(\omega,\eta),0,0)$ | `N3`: Nambu $p=2$ ($\Pi_3$), `N6`: Nambu $p=5$ ($\Pi_6$), `U`: vector field, `om2`: 2-form, `om5`: 5-form, `V`: vector field, `et2`: 2-form, `et5`: 5-form, `h`: function | `(ProofChain, Theorem)` |  |

## Rules the engine applies automatically

These rules are registered by the relevant engine or by the `prove_*` builder itself.
"Citation" marks a rule that uses an already proved theorem as a rewrite rule.

| Rule | Mathematical counterpart |
|---|---|
| `DLeibnizDefinition` | (L) $\mathcal D(fg)=f\,\mathcal Dg+g\,\mathcal Df$ (the only assumed structure; no ℝ-linearity) |
| `DDZeroDefinition` | citation (Prop 2.1(ii)+2.2): $\rho\circ\mathcal D=0$, $(\mathcal Da,\mathcal Db)\to0$, $\rho(\mathcal Da)(h)\to0$ |
| `DPairingUnfoldDefinition` | citation (Prop 2.2): $(\mathcal Df,u)\to\tfrac12\rho(u)(f)$ |
| `SkewSwapCompositeDefinition` | antisymmetry in a composite left slot: $[f x,y]\to-[y,f x]$ |
| `BDFirstOrderDefinition` | $d(fr)=f\,dr+l_{df}r$ (Def 9.1) |
| `BLieZLawsDefinition` | $\mathcal L^Z_V(fz)=f\mathcal L^Z_Vz+V(f)z$, $\mathcal L^Z_{fV}z=f\mathcal L^Z_Vz+l_{df}\iota_Vz$ |
| `BDopFirstOrderDefinition` | $\mathbb D(fr)=f\,\mathbb Dr+\mathbb L_{df}r$ (6.8) |
| `BLieREDerivationDefinition` | $\mathcal L^R_{\rho u}(fr)=f\mathcal L^R_{\rho u}r+\rho(u)(f)\,r$ (7.3) |
| `SplitAnchorDefinition` | $\rho(\varphi U)=U$, $\rho(\chi z)=0$ (8.5) |
| `DopViaChiDefinition` | $\mathbb D=\chi\circ d$ (8.3) |
| `LieZDefinitionRule` | $[\varphi V,\chi z]_E\to\chi(\mathcal L^Z_Vz)$ (9.7; relies on Lemma 9.1) |
| `Iota99Definition` | $g(\chi z,\varphi V)\to\iota_Vz$ (9.9) |
| `RightLeibnizTheoremRule` | citation (7.2): $[u,fv]_E\to f[u,v]_E+\rho(u)(f)\,v$ |
| `LeftLeibnizTheoremRule` | citation: $[fu,v]_E\to f[u,v]_E-\rho(v)(f)\,u+\mathbb L_{df}(g(u,v))$ |
| `PsiInverseDefinition` | $\Psi^{-1}\Psi=\Psi\Psi^{-1}=\mathrm{id}$ |
| `PsiLinearityDefinition` | $\Psi$, $\Psi^{-1}$ are $C^\infty$-linear |
| `ProjectorAbsorbsExactFormsDefinition` | the defining hypothesis of the locality projector $C(dg)=dg$ (role `assumption`: declared as part of the projector definition) |
