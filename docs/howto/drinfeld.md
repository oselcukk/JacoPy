# Bialgebroids, Drinfel'd doubles and twists

The package `jacopy.packages.drinfeld` works with doubles of the form $E=A\oplus Z$, where
$A=TM$ and $Z=\Lambda^pT^*M$, or $A$ is an abstract algebroid and $Z=\Lambda^pA^*$. The
standard double is the Dorfman bracket; the Poisson (LWX) and Nambu doubles add the tilde
side ($\tilde{\mathcal L},\tilde{\mathcal K},\tilde d$). Twists ($\Psi_\Pi$, $\Psi_B$,
$\Psi_m$) change the bracket by $[e_1,e_2]_\Psi=\Psi^{-1}[\Psi e_1,\Psi e_2]$. The main
sources are DD (Çatal-Özer, Doğan and Yetişmişoğlu, 2024) and TW (the same authors, 2025);
equation labels such as DD (4.17) or TW (5.2) refer to them (see the
[bibliography](../reference/bibliography.md)).

## Setup

```python
import jacopy
reg = jacopy.PropertyRegistry()
f, g, h = jacopy.functions("f g h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")

from jacopy.packages.drinfeld import *          # builders, twists, examples, prove_*, declarations
import jacopy.packages.drinfeld as drinfeld
from jacopy.packages.poisson import poisson_structure, nambu_structure
from jacopy.packages.drinfeld.abstract_double import abstract_double
from jacopy.packages.drinfeld.tilde_calculus import iota_tilde, d_tilde, nambu_tilde_engine
from jacopy.packages.drinfeld.calculus_conditions import lie, iota
from jacopy.central.algebroid import algebroid
from jacopy import Act

U, V, W = jacopy.vector_fields("U V W")
omega, eta, mu = jacopy.forms("omega eta mu", degree=1)
om2, et2 = jacopy.forms("omega_2 eta_2", degree=2)
om5, et5 = jacopy.forms("omega_5 eta_5", degree=5)
(B,) = jacopy.forms("B", degree=2)
(H,) = jacopy.forms("H", degree=3)
slots = [Y]
slots2 = list(jacopy.vector_fields("Y_1 Y_2"))
slots5 = list(jacopy.vector_fields("Z_1 Z_2 Z_3 Z_4 Z_5"))
P = poisson_structure()
N = nambu_structure(p=1)
N2 = nambu_structure("Pi_3", p=2)
N5 = nambu_structure("Pi_6", p=5)
NFI = nambu_structure("Pi", p=1, declare=("fundamental-identity",))
PSI = nambu_structure("psi", p=2)
psiB = (lambda v, w: b_twist(B, v, w), lambda v, w: b_twist_inverse(B, v, w))
psiPi = (lambda v, w: pi_twist(N, v, w), lambda v, w: pi_twist_inverse(N, v, w))
apply_twist, invert_twist = psiB        # a twist is passed as (apply, invert)
apply1, invert1 = psiPi
apply2, invert2 = psiB
E = algebroid("E", jacopy.Bundle("E"), declare=("antisymmetric",))
u, v, w = E.sections("u v w")
a, b = jacopy.forms("a b", degree=1, bundle=E.bundle)
```

`abstract_double`, `iota_tilde`, `d_tilde`, `nambu_tilde_engine`, `lie` and `iota` are not
exported by the package facade and are imported from their submodules.
`jacopy.packages.drinfeld.tilde_calculus.d_tilde` is a different function from
`jacopy.packages.poisson.d_tilde`.

## How the objects are set up

A section $e=U+\omega$ of a double is never a single object: it is passed as two
arguments, **split into its components** (`U, omega`). Brackets return a Python tuple
`(vector, form)`; in the $B_n$ and exceptional examples the tuple has three components.

| Object | Code | Note |
|---|---|---|
| Section components $U,V,W$; $\omega,\eta,\mu\in\Omega^1$ | `U, V, W = jacopy.vector_fields("U V W")`; `omega, eta, mu = jacopy.forms("omega eta mu", degree=1)` | For a higher double use `degree=p`; the examples below use $\omega_2,\eta_2$ (`om2, et2`, degree 2) and $\omega_5,\eta_5$ (`om5, et5`, degree 5) |
| Evaluation slots | `slots = [Y]` (p=1); `slots2 = list(jacopy.vector_fields("Y_1 Y_2"))`; `slots5 = list(jacopy.vector_fields("Z_1 Z_2 Z_3 Z_4 Z_5"))` | Theorems with form components close by applying the $p$-form to $p$ vectors |
| Poisson bivector $\pi$ (Poisson/LWX double) | `P = poisson_structure()` | Nothing declared: the Poisson double theorems hold for every bivector |
| $(p+1)$-vector $\Pi$ (Nambu double, tilde calculus, twists) | `N = nambu_structure(p=1)`; `N2 = nambu_structure("Pi_3", p=2)`; `N5 = nambu_structure("Pi_6", p=5)` | `p=1` → bivector; in the E6 example $\Pi_3$ (p=2) and $\Pi_6$ (p=5) |
| $\Pi$ with the fundamental identity (FI) declared | `NFI = nambu_structure("Pi", p=1, declare=("fundamental-identity",))` | FI is never added silently |
| Free 3-vector $\psi$ ($R_\psi$, quasi-Poisson) | `PSI = nambu_structure("psi", p=2)` | The `psi_host` argument is this object |
| B-field $B\in\Omega^{p+1}$, H-flux $H\in\Omega^{p+2}$ | `(B,) = jacopy.forms("B", degree=2)`; `(H,) = jacopy.forms("H", degree=3)` | for p=1 |
| Change-of-frame twist $\Psi_m=m\oplus\tilde m$ | the name `"m"` | $m$ is an opaque, invertible bundle endomorphism; JacoPy refers to it by name |
| Twist pair (apply, inverse) | `psiB = (lambda v, w: b_twist(B, v, w), lambda v, w: b_twist_inverse(B, v, w))` | `twisted_dorfman(*psiB, U, omega, V, eta)`; for Π, `pi_twist`/`pi_twist_inverse` |
| Abstract algebroid $A$ (abstract double) | `from jacopy.central.algebroid import algebroid`; `E = algebroid("E", jacopy.Bundle("E"), declare=("antisymmetric",))`; `u, v, w = E.sections("u v w")`; `a, b = jacopy.forms("a b", degree=1, bundle=E.bundle)` | `declare=` selects which algebroid axioms are declared (`"local"`, `"antisymmetric"`, `"lie"`, `"anchor-morphism"`, ...) |
| Engine | `twist_engine(N, reg)`; tilde engine with FI: `from jacopy.packages.drinfeld.tilde_calculus import nambu_tilde_engine`; `nambu_tilde_engine(NFI, reg)` | For trying your own identity with `jacopy.show_equal(lhs, rhs, registry=reg, engine=...)` |

### Declarations

Declarations are axioms chosen by the user. An engine uses them only once they are
registered, and they appear in the `requires` list of the result.

| Declaration (`Name`) | Axiom | How it is declared | `.name` |
|---|---|---|---|
| `NambuMorphismDeclaration` | $[\Pi\omega,\Pi\eta]=\Pi[\omega,\eta]_{\mathrm{Kos}}$ (the bracket-morphism face of FI, $R'=0$) | On the structure: `nambu_structure(p=1, declare=("fundamental-identity",))`, then `nambu_tilde_engine(NFI, reg)`; or `declare_fi=True` (default) in a `prove_*` call | `'declared FI (bracket morphism): [Πω, Πη] = Π[ω,η]_Kos'` |
| `TwistedFIDeclaration` | $[\Pi\omega,\Pi\eta]=\Pi[\omega,\eta]_{\mathrm{Kos}}+\Pi\big(\iota_{\Pi\eta}\iota_{\Pi\omega}H\big)$ | `eng = nambu_tilde_engine(N, reg)`; `eng.register(TwistedFIDeclaration(N, H))` | `'declared H-twisted FI: [Πω,Πη] = Π[ω,η]_Kos + Π H(Πω,Πη)'` |
| `PsiTwistedFIDeclaration` | $[\pi^\sharp\omega,\pi^\sharp\eta]=\pi^\sharp[\omega,\eta]_\pi+\psi^\sharp(\omega\wedge\eta)$ (quasi-Poisson) | `PsiTwistedFIDeclaration(P, PSI)`; `prove_psi_twisted_fi_consistency` registers it itself | `'declared ψ-twisted FI: [π♯ω,π♯η] = π♯[ω,η]_π + ψ♯(ω∧η)'` |

Using them:

| Math | In code | Result |
|---|---|---|
| $R'(\omega,\eta)(h)=0$ under FI | `jacopy.show_equal(Act(r_twist(NFI, omega, eta), h), jacopy.Integer(0), registry=reg, engine=nambu_tilde_engine(NFI, reg))` | closes |
| $R'_H(\omega,\eta)(h)=0$ under H-twisted FI | `eng = nambu_tilde_engine(N, reg); eng.register(TwistedFIDeclaration(N, H))`; `jacopy.show_equal(Act(r_twist_h(N, H, omega, eta), h), jacopy.Integer(0), registry=reg, engine=eng)` | closes |

`Act` (`jacopy.Act`) applies a vector field to the function $h$.

## Standard double = Dorfman bracket

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\langle U+\omega,V+\eta\rangle_+=\iota_U\eta+\iota_V\omega$ | `canonical_pairing(U, omega, V, eta)` | U, V: vector field; omega, eta: p-form | form (a function at $p=1$): $\iota_{U}(\eta) + \iota_{V}(\omega)$ | Canonical symmetric pairing |
| $[U+\omega,V+\eta]_D$ | `dorfman_double(U, omega, V, eta)` | U, V: vector field; omega, eta: p-form | (vector, form) pair: $([U,V],\ \mathcal{L}_{U}(\eta) - \mathcal{L}_{V}(\omega) + d(\iota_{V}(\omega)))$ | Sections are passed split into components; the name "double" reflects that the standard Drinfel'd double = Dorfman. The degree is general: with `omega_2, eta_2` one gets $TM\oplus\Lambda^2$ |
| $[U+\omega,V+\eta]_H$ (H-twisted Dorfman) | `dorfman_double_h(H, U, omega, V, eta)` | H: $(p+2)$-form; others as above | (vector, form): $+\iota_{V}(\iota_{U}(H))$ is added to the form | |
| $H(U,V)=\iota_V\iota_UH$ | `h_term(H, U, V)` | H: form; U, V: vector | form: $\iota_{V}(\iota_{U}(H))$ | |
| component of $\mathrm{Jac}(e_1,e_2,e_3)$ | `bracket_jacobiator(dorfman_double, (U, omega), (V, eta), (W, mu), component=1)` | bracket: any component-bracket function; e1..e3: (vector, form) tuples; component: 0 vector / 1 form | form: the explicit (long) form of $[e_1,[e_2,e_3]]-[[e_1,e_2],e_3]-[e_2,[e_1,e_3]]$ | Also works for your own bracket |
| $\mathrm{Jac}$, Nambu double | `nambu_double_jacobiator(N, (U, omega), (V, eta), (W, mu), component=0)` | N: Nambu structure | vector component (very long, explicit) | |

## Poisson (LWX) and Nambu double

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $[U+\omega,V+\eta]_\pi$ (LWX double) | `poisson_double(P, U, omega, V, eta)` | P: Poisson structure; U, V: vector; omega, eta: 1-form | (vector, form): vector $[U,V]+\tilde{\mathcal L}_\omega V-\tilde{\mathcal L}_\eta U-\pi^\sharp(d\langle\eta,U\rangle)$, form $[\omega,\eta]_{\pi} + \mathcal{L}_{U}(\eta) - \mathcal{L}_{V}(\omega) + d(\iota_{V}(\omega))$ | For every bivector; no $[\pi,\pi]$ declaration needed |
| $\rho(U+\omega)(f)=U(f)+(\pi^\sharp\omega)(f)$ | `poisson_double_anchor_action(P, U, omega, f)` | P; U: vector; omega: 1-form; f: function | function: $U(f) + \pi^{\sharp}(\omega)(f)$ | Total anchor |
| $[U+\omega,V+\eta]_\Pi$ (Nambu double) | `nambu_double(N, U, omega, V, eta)` | N: Nambu structure; omega, eta: p-form | (vector, form): vector $[U,V]+([\Pi(\omega),V]+\Pi(\iota_V d\omega))-\dots-\Pi(d(\iota_U\eta))$, form $(\mathcal{L}_{\Pi(\omega)}(\eta) - \iota_{\Pi(\eta)}(d\omega)) + \mathcal{L}_{U}(\eta) - \mathcal{L}_{V}(\omega) + d(\iota_{V}(\omega))$ | The first parenthesized term of the form part is the higher Koszul bracket |
| $\rho(U+\omega)(f)=U(f)+(\Pi\omega)(f)$ | `nambu_double_anchor_action(N, U, omega, f)` | | function: $U(f) + \Pi(\omega)(f)$ | |
| $g_Z(a,b)=\iota_{\Pi a}b+\iota_{\Pi b}a$ | `g_z_pairing(N, omega, eta)` | a, b: p-form | form: $\iota_{\Pi(\omega)}(\eta) + \iota_{\Pi(\eta)}(\omega)$ | JacoPy's normalization ($\mathcal D_Z=d$): one half of the pairing $g_Z$ of DD (6.17) |
| $g_E(e_2,e_3)=\iota_{U_2}\eta_3+\iota_{U_3}\eta_2+g_Z(\eta_2,\eta_3)$ | `double_metric(N, U, omega, V, eta)` | U2, eta2, U3, eta3 respectively | form: $\iota_{U}(\eta) + \iota_{V}(\omega) + (\iota_{\Pi(\omega)}(\eta) + \iota_{\Pi(\eta)}(\omega))$ | The metric of the double |

## Bialgebroid calculus: $\mathcal K$ and the tilde operators

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\mathcal K_X x=-\mathcal L_Xx+d\iota_Xx$ | `kappa(X, omega)` | X: vector; x: form | form: $-\mathcal{L}_{X}(\omega) + d(\iota_{X}(\omega))$ | DD (4.14) |
| $\mathcal K_W\omega=-\iota_Wd\omega$ (Cartan) | `kappa_cartan(W, omega)` | | form: $-\iota_{W}(d(\omega))$ | Equal to the one above by the magic formula |
| $\mathcal L_X x$, $\iota_X x$ (shorthands) | `lie(X, omega)`, `iota(X, omega)` | | $\mathcal{L}_{X}(\omega)$, $\iota_{X}(\omega)$ | Imported from a submodule (see Setup) |
| $\tilde{\mathcal L}_\omega V=[\pi^\sharp\omega,V]+\pi^\sharp(\iota_Vd\omega)$ | `lie_tilde_vf(P, omega, V)` | P: Poisson; omega: 1-form; V: vector | vector: $[\pi^{\sharp}(\omega), V] + \pi^{\sharp}(\iota_{V}(d\omega))$ | DD (4.41) |
| $\tilde{\mathcal K}_\eta V=[V,\pi^\sharp\eta]-\pi^\sharp(\mathcal L_V\eta)$ | `kappa_tilde(P, eta, V)` | | vector: $[V, \pi^{\sharp}(\eta)] - \pi^{\sharp}(\mathcal{L}_{V}(\eta))$ | DD (6.6) |
| $\tilde{\mathcal L}_\omega W=[\Pi\omega,W]+\Pi(\iota_Wd\omega)$ | `lie_tilde_nambu(N, omega, W)` | N: Nambu; omega: p-form | vector: $[\Pi(\omega), W] + \Pi(\iota_{W}(d\omega))$ | |
| $\tilde{\mathcal K}_\eta W=-\tilde{\mathcal L}_\eta W+\tilde d\tilde\iota_\eta W$ | `kappa_tilde_nambu(N, eta, W)` | | vector: $-([\Pi(\eta), W] + \Pi(\iota_{W}(d\eta))) - \Pi(d(\iota_{W}(\eta)))$ | DD (4.16) |
| $\tilde\iota_\eta U=\iota_U\eta$ | `iota_tilde(U, eta)`  | | $\iota_{U}(\eta)$ | Imported from a submodule (see Setup) |
| $\tilde d x=-\Pi\,dx$ | `d_tilde(N, f)`  | N; x: form/function | vector: $-\Pi(d(f))$ | A different function from `d_tilde` in the Poisson package |
| Abstract double $[u+a,v+b]$ on $A\oplus\Lambda^pA^*$ | `abstract_double(E, u, a, v, b)`  | E: algebroid; u, v: section; a, b: $E^*$-form | (section, form): $([u, v]_{E},\ L^E_{u}(b) - L^E_{v}(a) + d_{E}(\iota_{v}(a)))$ | Imported from `jacopy.packages.drinfeld.abstract_double` |
| $\langle e_1,e_2\rangle_+=\iota_u b+\iota_v a$ (abstract) | `abstract_pairing(u, a, v, b)` | | $\iota_{u}(b) + \iota_{v}(a)$ | |

## Twists: $\Psi_\Pi$, $\Psi_B$, $\Psi_m$, R-twist, H-twist

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\Psi_\Pi(U\oplus\omega)=(U+\Pi\omega)\oplus\omega$ | `pi_twist(N, U, omega)` | N: Nambu; vec, form | (vector, form): $(U + \Pi(\omega),\ \omega)$ | TW (7.11) |
| $\Psi_\Pi^{-1}$ | `pi_twist_inverse(N, U, omega)` | | $(U - \Pi(\omega),\ \omega)$ | TW (7.12) |
| $\Psi_B(U\oplus\omega)=U\oplus(\iota_UB+\omega)$ | `b_twist(B, U, omega)` | B: $(p+1)$-form | $(U,\ \iota_{U}(B) + \omega)$ | |
| $\Psi_B^{-1}$ | `b_twist_inverse(B, U, omega)` | | $(U,\ \omega - \iota_{U}(B))$ | |
| $\Psi_m=m\oplus\tilde m$ | `m_twist("m", U, omega)` | name: name of the endomorphism (str) | $(m(U),\ \tilde{m}(\omega))$ | |
| $\Psi_m^{-1}$ | `m_twist_inverse("m", U, omega)` | | $(m^{-1}(U),\ \tilde{m}^{-1}(\omega))$ | |
| $[e_1,e_2]_\Psi=\Psi^{-1}[\Psi e_1,\Psi e_2]_D$ | `twisted_dorfman(apply_twist, invert_twist, U, omega, V, eta)` | apply_twist, invert_twist: `(vec, form) -> (vec, form)` functions | (vector, form); for $\Psi_B$: $([U,V],\ \mathcal{L}_{U}(\iota_{V}B + \eta) - \mathcal{L}_{V}(\iota_{U}B + \omega) + d(\iota_{V}(\iota_{U}B + \omega)) - \iota_{[U,V]}(B))$ | You pass the twist as two functions (the `psiB` tuple above) |
| $[e_1,e_2]_{\Psi_m}$ | `twisted_dorfman_m("m", U, omega, V, eta)` | | $(m^{-1}([m(U), m(V)]),\ \tilde{m}^{-1}(\mathcal{L}_{m(U)}(\tilde{m}\eta) - \dots))$ | |
| $\Psi^{-1}[\Psi e_1,\Psi e_2]_H$ | `twisted_dorfman_h(H, apply_twist, invert_twist, U, omega, V, eta)` | H: form; twist pair | (vector, form), with $\Psi_\Pi$: vector $[U + \Pi(\omega), V + \Pi(\eta)] - \Pi(\dots)$ | |
| $\Psi_1\circ\Psi_2$ | `compose_twists(apply1, invert1, apply2, invert2)` | four functions | (apply, invert) pair; used with `twisted_dorfman(*compose_twists(...), U, omega, V, eta)` | JacoPy's composition law |
| $R'(\omega,\eta)=[\Pi\omega,\Pi\eta]-\Pi[\omega,\eta]_{\mathrm{Kos}}$ | `r_twist(N, omega, eta)` | | vector: $[\Pi(\omega), \Pi(\eta)] - \Pi(\mathcal{L}_{\Pi(\omega)}(\eta) - \iota_{\Pi(\eta)}(d\omega))$ | FI ⇔ $R'=0$ |
| $R'_H=R'-\Pi\,H(\Pi\omega,\Pi\eta)$ | `r_twist_h(N, H, omega, eta)` | | vector: $R'(\omega,\eta) - \Pi(\iota_{\Pi(\eta)}(\iota_{\Pi(\omega)}(H)))$ | |
| $R_\psi(\omega,\eta)=\psi^\sharp(\omega\wedge\eta)$ | `r_twist_psi(PSI, omega, eta)` | psi_host: 3-vector structure | vector: $\psi(\omega \wedge \eta)$ | |

## The general Roytenberg bracket and H-closedness

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $[U+\omega,V+\eta]_E=[U,V]+\tilde{\mathcal L}_\omega V+\tilde{\mathcal K}_\eta U+R(\omega,\eta)\ \oplus\ [\omega,\eta]_Z+\mathcal L_U\eta+\mathcal K_V\omega+H(U,V)$ | `roytenberg_bracket(N, U, omega, V, eta, H=H)` | N; H: keyword (optional); `with_tilde=`, `with_r=`: switches | (vector, form): each a sum of 4 terms (the form ends with $+\iota_{V}(\iota_{U}(H))$) | TW (5.2) |
| Tilde and R switched off → Dorfman | `roytenberg_bracket(N, U, omega, V, eta, with_tilde=False, with_r=False)` | | $([U,V],\ \mathcal{L}_{U}(\eta) + (-\mathcal{L}_{V}(\omega) + d(\iota_{V}(\omega))))$ | |
| TW (5.13) defect | `h_closure_defect(H, U, V, W)` | H; U, V, W: vector | form: $\iota_{[V,W]}(\iota_{U}H) - \iota_{W}(\iota_{[U,V]}H) - \dots$ (6 terms) | `prove_h_closure_measures_dh` shows that this is $\iota_W\iota_V\iota_U dH$ |
| TW (5.12) Jacobiator obstruction | `jacobiator_a_obstruction(N, H, U, V, W)` | | vector (long) | |
| TW (5.9) first twisted calculus obstruction | `twisted_calculus_obstruction_one(N, H, U, V, mu)` | | form (long) | |
| carrier of $[\pi,\psi]_{SN}$ | `sn_compat_node(P, PSI)` | P: Poisson; psi_host | 4-vector node: $[\pi, \psi]_{[\cdot,\cdot]_{SN}}$ | TW (3.15) |

## Examples: $B_n$ and exceptional (E6)

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $B_n$ bracket, $E=TM\oplus C^\infty M\oplus T^*M$ | `bn_bracket(U, f, omega, V, g, eta)` | U, V: vector; f, g: function; omega, eta: 1-form | (vector, function, form): $([U,V],\ U(g) - V(f),\ \mathcal{L}_{U}(\eta) - \mathcal{L}_{V}(\omega) + d(\iota_{V}\omega) + g\,df)$ | TW (8.15) |
| $g_E=\iota_U\eta+\iota_V\omega+fg$ | `bn_pairing(U, f, omega, V, g, eta)` | | $\iota_{U}(\eta) + \iota_{V}(\omega) + f\,g$ | $SO(n+1,n)$ |
| $g\,df$ (twist core) | `bn_scalar_twist(f, g)` | | $g\,d(f)$ | |
| Splitting 1 Z-bracket | `bn_split1_z_bracket(f, omega, g, eta)` | | $g\,d(f)$ | TW (8.18) |
| Splitting 2 calculus | `bn_split2_calculus(U, f, eta)` | | pair: $(\mathcal{L}_{U}(\eta),\ \iota_{U}(\eta))$ | TW (8.21) |
| Splitting 3 anchor action | `bn_split3_anchor_action(U, omega, f)` | | $U(f)$ | TW (8.26) |
| Exceptional Courant bracket, $TM\oplus\Lambda^2\oplus\Lambda^5$ | `exceptional_courant_bracket(U, om2, om5, V, et2, et5)` | om2, et2: 2-form; om5, et5: 5-form | triple: $([U,V],\ \mathcal{L}_{U}\eta_2 - \iota_{V}d\omega_2,\ \mathcal{L}_{U}\eta_5 - \iota_{V}d\omega_5 - \eta_2 \wedge d\omega_2)$ | TW (8.1) |
| 1-form pairing | `exceptional_pairing_two(U, om2, V, et2)` | | $\iota_{U}(\eta_2) + \iota_{V}(\omega_2)$ | |
| 4-form pairing | `exceptional_pairing_five(U, om2, om5, V, et2, et5)` | | $\iota_{U}(\eta_5) + \iota_{V}(\omega_5) - \omega_2 \wedge \eta_2$ | |
| H-reading of the cross term | `exceptional_h_reading(U, om2, V, et2)` | | $-\eta_2 \wedge d(\omega_2)$ | TW (8.2) |
| $(\Pi_3\circledast\Pi_3)(\omega_5)=\tfrac12\Pi_3(\iota_{\Pi_3}\omega_5)$ | `boxtimes(N2, om5)` | N3: $p=2$ Nambu structure; omega5 | $\frac{1}{2}\,\Pi_3(\iota_{\Pi_3}(\omega_5))$ | |
| Exceptional $\Psi_\Pi$ | `exceptional_pi_twist(N2, N5, U, om2, om5)` | N3, N6: $p=2$ and $p=5$ Nambu structures; U, om2, om5 | triple: $(U + \Pi_3(\omega_2) + \Pi_6(\omega_5) + \frac{1}{2}\Pi_3(\iota_{\Pi_3}\omega_5),\ \omega_2,\ \omega_5)$ | |
| Exceptional $\Psi_\Pi^{-1}$ | `exceptional_pi_twist_inverse(N2, N5, U, om2, om5)` | | $(U - \Pi_3(\omega_2) - \Pi_6(\omega_5) - \frac{1}{2}\Pi_3(\iota_{\Pi_3}\omega_5),\ \omega_2,\ \omega_5)$ | |

## A worked example

The $B$-twisted Dorfman bracket, written out, and the Ševera identity for it:

```python
vec, form = twisted_dorfman(*psiB, U, omega, V, eta)
print(jacopy.to_latex(vec))
chain = drinfeld.prove_b_twist_severa(B, U, omega, V, eta, slots, registry=reg)
print(len(chain.steps) > 0, jacopy.to_ascii(chain.initial)[:60])
```

```text
\left[U,\, V\right]
True L_U((ι_V(B) + eta))
```

## Theorem builders

None of the Drinfel'd builders returns its own `Theorem` record. A builder returns a
`ProofChain`, a pair `(ProofChain, List[Theorem])` whose list contains the theorems **cited**
in the proof, or a tuple of chains, one per component. Most builders prove an identity by
evaluating it on probe objects: a $p$-form component on `slots` ($p$ vector fields), a
vector component on a probe function `h` (or a probe 1-form `gamma`). All of them take an
optional `registry=` and most take `max_steps=`; in those that require the fundamental
identity (FI), `declare_fi=True` is the default. The last column names the declaration the
proof relies on, or the source equation.

| Builder | Identity it proves | Arguments | Returns | Uses / source |
|---|---|---|---|---|
| `drinfeld.prove_dorfman_symmetric_part` | $[e_1,e_2]+[e_2,e_1]=(0,\,d\langle e_1,e_2\rangle_+)$ (form component) | `U, V`: vector; `omega, eta`: p-form; `f`: function; `slots`: p vectors | `(ProofChain, List[Theorem])` | none |
| `drinfeld.prove_dorfman_right_leibniz_form` | $[e_1,fe_2]=f[e_1,e_2]+(Uf)e_2$, $\rho(U+\omega)=U$ (form) | `U, omega, V, eta, f, slots` | `(ProofChain, List[Theorem])` | none |
| `drinfeld.prove_dorfman_jacobi_form` | $[e_1,[e_2,e_3]]=[[e_1,e_2],e_3]+[e_2,[e_1,e_3]]$ (form) | `U, omega, V, eta, W, mu` (three sections), `f`, `slots` | `(ProofChain, List[Theorem])` | none; the vector part cites the Jacobi identity for vector fields |
| `drinfeld.prove_poisson_double_symmetric_part_form` | $[e_1,e_2]+[e_2,e_1]=\mathcal D\langle e_1,e_2\rangle_+$, $\mathcal D=d+\tilde d$ (form) | `P`: Poisson; `U, omega, V, eta`; `slots` | `ProofChain` | for every bivector |
| `drinfeld.prove_poisson_double_symmetric_part_vec` | vector part: $\tilde d\langle e_1,e_2\rangle_+=-\pi^\sharp d\langle e_1,e_2\rangle_+$ | `P, U, omega, V, eta`; `gamma`: probe 1-form | `ProofChain` |  |
| `drinfeld.prove_poisson_double_right_leibniz_form` | $[e_1,fe_2]=f[e_1,e_2]+(\rho(e_1)f)e_2$, $\rho=U+\pi^\sharp\omega$ (form) | `P, U, omega, V, eta, f, slots` | `ProofChain` |  |
| `drinfeld.prove_poisson_double_right_leibniz_vec` | the same, vector component | `P, U, omega, V, eta, f, gamma` | `ProofChain` |  |
| `drinfeld.prove_nambu_double_symmetric_part_form` | $[e_1,e_2]+[e_2,e_1]=\mathcal D\langle e_1,e_2\rangle_+$ (form; for $p\ge2$, $+d\,g_Z(\omega,\eta)$) | `N`: Nambu; `U, omega, V, eta`; `slots` | `ProofChain` | none |
| `drinfeld.prove_nambu_double_symmetric_part_vec` | vector part $-\Pi d(\iota_U\eta+\iota_V\omega)$ | `N, U, omega, V, eta, h` | `ProofChain` | none |
| `drinfeld.prove_nambu_double_right_leibniz_form` | right-Leibniz, $\rho=U+\Pi\omega$ (form) | `N, U, omega, V, eta, f, slots` | `ProofChain` | none |
| `drinfeld.prove_nambu_double_right_leibniz_vec` | right-Leibniz (vector component) | `N, U, omega, V, eta, f, h` | `ProofChain` | none |
| `drinfeld.prove_compat_condition_one` | $\mathcal D^Z_{\mathcal L_U}(\eta,\mu)=\mathcal L_{\tilde{\mathcal K}_\eta U}\mu+\mathcal K_{\tilde{\mathcal K}_\mu U}\eta$ | `P`; `eta, mu`: 1-form; `U`: vector; `Y`: probe vector | `ProofChain` | DD (4.36), derivator condition |
| `drinfeld.prove_compat_condition_two` | $\mathcal L_{\tilde d\tilde\iota_\eta U}\mu+[d\iota_U\eta,\mu]_\pi=0$ | `P, eta, mu, U, Y` | `ProofChain` | none |
| `drinfeld.prove_compat_condition_three_p1` | $d\iota_{\tilde{\mathcal L}_\omega W}\eta-d\iota_{\tilde d\tilde\iota_\eta W}\omega+d\iota_W[\omega,\eta]_\pi=0$ ($p=1$) | `P, omega, eta, W, Y` | `ProofChain` |  |
| `drinfeld.prove_calculus_condition_one` | $\mathcal L_U\mathcal L_V\mu=\mathcal L_V\mathcal L_U\mu+\mathcal L_{[U,V]}\mu$ | `U, V`; `mu`: p-form; `f`; `slots` | `(ProofChain, List[Theorem])` |  |
| `drinfeld.prove_calculus_condition_two` | $\mathcal L_Ud\iota_W\eta=d\iota_{[U,W]}\eta+d\iota_W\mathcal L_U\eta$ | `U, W, eta, f, slots` | `(ProofChain, List[Theorem])` |  |
| `drinfeld.prove_calculus_condition_three` | $\mathcal L_Wd\iota_V\omega=d\iota_Wd\iota_V\omega$ | `W, V, omega, f, slots` | `(ProofChain, List[Theorem])` |  |
| `drinfeld.prove_kappa_kappa` | $\mathcal K_U\mathcal K_V\omega=-\mathcal K_U\mathcal L_V\omega$ | `U, V, omega, f, slots` | `(ProofChain, List[Theorem])` | DD (4.4) |
| `drinfeld.prove_kappa_bracket` | $\mathcal K_{[U,V]}\omega=\mathcal K_V\mathcal K_U\omega+\mathcal L_U\mathcal K_V\omega$ | `U, V, omega, f, slots` | `(ProofChain, List[Theorem])` | DD (4.4) |
| `drinfeld.prove_abstract_double_symmetric_part` | $[e_1,e_2]+[e_2,e_1]=(0,\,d_E\langle e_1,e_2\rangle_+)$ | `alg`: algebroid; `u, v, w`: section; `alpha, beta`: $E^*$-form; `f` | `(ProofChain, ProofChain)` (vector, form) | the vector leg requires the `"antisymmetric"` declaration |
| `drinfeld.prove_abstract_double_right_leibniz` | form defect $=\langle\alpha,L(df,v,w)\rangle$ (locality term) | `alg, u, alpha, v, beta, f, w` | `(ProofChain, ProofChain)` | requires the `"local"` declaration; otherwise `ProofFailure` |
| `drinfeld.prove_abstract_double_jacobi_form` | Leibniz–Jacobi of the double (form) | `alg, u, alpha, v, beta, w, gamma`; `probe`: section; `f` | `(ProofChain, List[Theorem])` | `"lie"`, `"anchor-morphism"` declarations |
| `drinfeld.prove_jacobi_compat_d8` | $\mathcal L_U[\eta,\mu]-[\mathcal L_U\eta,\mu]-[\eta,\mathcal L_U\mu]=\mathcal L_{\tilde{\mathcal K}_\eta U}\mu+\mathcal K_{\tilde{\mathcal K}_\mu U}\eta$ | `N, U, eta, mu` | `ProofChain` | DD (D.8) |
| `drinfeld.prove_jacobi_compat_d9` | $\mathcal L_{\tilde d\tilde\iota_\eta U}\mu+[d\iota_U\eta,\mu]_{\mathrm{Kos}}+\mathcal K_{\Pi\mu}(d\iota_U\eta)=0$ | `N, U, eta, mu, slots` | `ProofChain` | DD (D.9) |
| `drinfeld.prove_jacobi_compat_d10` | $d\iota_{\tilde{\mathcal L}_\omega W}\eta-d\iota_{\tilde d\tilde\iota_\eta W}\omega+d\iota_W[\omega,\eta]+d\,g_Z(\mathcal K_W\omega,\eta)-d\,g_Z(d\iota_W\eta,\omega)=0$ | `N, omega, eta, W` | `ProofChain` | DD (D.10) |
| `drinfeld.prove_jacobi_compat_d11` | $\tilde{\mathcal L}_\omega[V,W]-[\tilde{\mathcal L}_\omega V,W]-[V,\tilde{\mathcal L}_\omega W]-\tilde{\mathcal L}_{\mathcal K_V\omega}W-\tilde{\mathcal K}_{\mathcal K_W\omega}V=0$ | `N, omega, V, W, f, h` | `(ProofChain, List[Theorem])` | DD (D.11) |
| `drinfeld.prove_jacobi_compat_d12` | $\tilde{\mathcal L}_{d\iota_V\omega}W+[\tilde d\tilde\iota_\omega V,W]=0$ | `N, omega, V, W, h` | `ProofChain` | DD (D.12) |
| `drinfeld.prove_jacobi_compat_d13` | $\tilde d\tilde\iota_{\mathcal L_U\mu}V-\tilde d\tilde\iota_{d\iota_V\mu}U+\tilde d\tilde\iota_\mu[U,V]=0$ | `N, mu, U, V, h` | `ProofChain` | DD (D.13) |
| `drinfeld.prove_tilde_calculus_condition_one` | $\tilde{\mathcal L}_\omega\tilde{\mathcal L}_\eta W-\tilde{\mathcal L}_\eta\tilde{\mathcal L}_\omega W=\tilde{\mathcal L}_{[\omega,\eta]}W$ | `N, omega, eta, W, f, h` | `(ProofChain, List[Theorem])` | FI required (`declare_fi=True`) |
| `drinfeld.prove_tilde_calculus_condition_two` | $\tilde{\mathcal L}_\omega\tilde{\mathcal K}_\eta W-\tilde{\mathcal K}_\eta\tilde{\mathcal L}_\omega W=\tilde{\mathcal K}_{[\omega,\eta]}W$ | `N, omega, eta, W, f, h` | `(ProofChain, List[Theorem])` | FI |
| `drinfeld.prove_tilde_calculus_condition_three` | $\tilde{\mathcal L}_\omega\tilde{\mathcal K}_\eta W+\tilde{\mathcal K}_\eta\tilde{\mathcal K}_\omega W=\tilde{\mathcal K}_{[\omega,\eta]}W$ | `N, omega, eta, W, f, h` | `(ProofChain, List[Theorem])` | FI |
| `drinfeld.prove_z_metric_invariance` | $g_Z([\omega,\eta],\mu)+g_Z(\eta,[\omega,\mu])=\mathcal L_{\Pi\omega}g_Z(\eta,\mu)$ | `N, omega, eta, mu, slots` | `ProofChain` | FI; DD (D.14) |
| `drinfeld.prove_a_mixing_condition` | $\mathcal L_U\iota_V\mu=\iota_{[U,V]}\mu+\iota_V\mathcal L_U\mu$ | `N, U, V, mu, slots` | `ProofChain` | DD (D.16) |
| `drinfeld.prove_a_invariance_of_gz` | $\mathcal L_Ug_Z(\eta,\mu)=g_Z(\mathcal L_U\eta,\mu)+g_Z(\eta,\mathcal L_U\mu)+\iota_{\tilde{\mathcal K}_\eta U}\mu+\iota_{\tilde{\mathcal K}_\mu U}\eta$ | `N, U, eta, mu, slots` | `ProofChain` | DD (D.17) |
| `drinfeld.prove_dual_mixing_condition` | $\mathcal L_{\Pi\omega}\iota_W\eta=\iota_W\mathcal L_{\Pi\omega}\eta+\iota_{\tilde{\mathcal L}_\omega W}\eta-\iota_{\Pi(\iota_Wd\omega)}\eta$ | `N, omega, eta, W, slots` | `ProofChain` |  |
| `drinfeld.prove_double_metric_invariance` | $\mathcal L_{U_1+\Pi\omega_1}g_E(e_2,e_3)=g_E([e_1,e_2],e_3)+g_E(e_2,[e_1,e_3])$ | `N`; `U1, om1, U2, om2, U3, om3`; `slots` | `ProofChain` | FI; DD (D.19) |
| `drinfeld.prove_morphism_compat_condition` | $\tilde{\mathcal K}_\eta U+\Pi(\mathcal L_U\eta)=[U,\Pi\eta]$ | `N, U, eta, h` | `ProofChain` | TW (4.20) |
| `drinfeld.prove_morphism_compat_condition_dual` | $\tilde{\mathcal L}_\omega V+\Pi(\mathcal K_V\omega)=[\Pi\omega,V]$ | `N, omega, V, h` | `ProofChain` |  |
| `drinfeld.prove_phi_z_is_morphism` | $\Pi[\omega,\eta]_{\mathrm{Kos}}=[\Pi\omega,\Pi\eta]$ | `N, omega, eta, h` | `ProofChain` | FI; `declare_fi=False` → `ProofFailure` |
| `drinfeld.prove_total_anchor_is_bracket_morphism` | $\rho([e_1,e_2])=[\rho e_1,\rho e_2]$, $\rho=U+\Pi\omega$ | `N, U1, om1, U2, om2, h` | `ProofChain` | FI; TW (4.19) |
| `drinfeld.prove_pi_twist_form_is_nambu` | form$([e_1,e_2]_{\Psi_\Pi})$ = form(Nambu double) | `N, U, omega, V, eta, slots` | `ProofChain` | none |
| `drinfeld.prove_pi_twist_vec_is_nambu_plus_r` | vec$([e_1,e_2]_{\Psi_\Pi})$ = vec(Nambu) $+R'(\omega,\eta)$ | `N, U, omega, V, eta, h` | `ProofChain` | none |
| `drinfeld.prove_pi_twist_h_form` | form$([e_1,e_2]_{\Psi_\Pi,H})$ = form(Nambu) $+H(U+\Pi\omega,V+\Pi\eta)$ | `N, H, U, omega, V, eta, slots` | `ProofChain` |  |
| `drinfeld.prove_pi_twist_h_vec` | vec$([e_1,e_2]_{\Psi_\Pi,H})$ = vec(Nambu) $+R'-\Pi H(U+\Pi\omega,V+\Pi\eta)$ | `N, H, U, omega, V, eta, h` | `ProofChain` |  |
| `drinfeld.prove_twisted_lie_tilde` | $[\Pi\omega,V]-\Pi(\mathcal K_V\omega)=\tilde{\mathcal L}_\omega V$ | `N, omega, V, h` | `ProofChain` | TW (7.25) |
| `drinfeld.prove_twisted_kappa_tilde` | $[U,\Pi\eta]-\Pi(\mathcal L_U\eta)=-\tilde{\mathcal L}_\eta U+\tilde d(\iota_U\eta)$ | `N, eta, U, h` | `ProofChain` |  |
| `drinfeld.prove_twisted_z_bracket_is_koszul` | $\mathcal L_{\Pi\omega}\eta+\mathcal K_{\Pi\eta}\omega=[\omega,\eta]_{\mathrm{Kos}}$ | `N, omega, eta, slots` | `ProofChain` |  |
| `drinfeld.prove_b_twist_vec_unchanged` | vec$([e_1,e_2]_{\Psi_B})=[U,V]$ | `B, U, omega, V, eta, h` | `ProofChain` |  |
| `drinfeld.prove_b_twist_severa` | form$([e_1,e_2]_{\Psi_B})-$form$([e_1,e_2])=\iota_V\iota_U\,dB$ | `B, U, omega, V, eta, slots` | `ProofChain` | none (Ševera) |
| `drinfeld.prove_b_twist_severa_h` | form$([e_1,e_2]_{\Psi_B,H})$ = form$([e_1,e_2]_{H+dB})$ | `H, B, U, omega, V, eta, slots` | `ProofChain` |  |
| `drinfeld.prove_b_twists_compose_additively` | $[e_1,e_2]_{\Psi_{B_1}\circ\Psi_{B_2}}=[e_1,e_2]_{\Psi_{B_1+B_2}}$ | `B1, B2, U, omega, V, eta, slots` | `ProofChain` | JacoPy's composition law |
| `drinfeld.prove_r_twist_second_entry_linear` | $R'(\omega,f\eta)=fR'(\omega,\eta)$ | `N, omega, eta, f, h` | `ProofChain` |  |
| `drinfeld.prove_r_twist_first_entry_obstruction` | $R'(f\omega,\eta)=fR'(\omega,\eta)-\Pi\big(df\wedge(\iota_{\Pi\omega}\eta+\iota_{\Pi\eta}\omega)\big)$ | `N, omega, eta, f, h` | `ProofChain` | TW (7.26) |
| `drinfeld.prove_m_is_bracket_morphism` | $m([U,V]'_A)=[mU,mV]$ | `name`: str; `U, V, h` | `ProofChain` |  |
| `drinfeld.prove_m_twist_right_leibniz_vec` | $[e_1,fe_2]_\Psi=f[e_1,e_2]_\Psi+(\rho'(e_1)f)e_2$, $\rho'=m$ (vector) | `name, U, omega, V, eta, f, h` | `ProofChain` |  |
| `drinfeld.prove_m_twist_right_leibniz_form` | the same (form) | `name, U, omega, V, eta, f` | `ProofChain` |  |
| `drinfeld.prove_m_twist_symmetric_part_form` | form$([e_1,e_2]_\Psi+[e_2,e_1]_\Psi)=\tilde m^{-1}d(\iota_{mU}\tilde m\eta+\iota_{mV}\tilde m\omega)$ | `name, U, omega, V, eta` | `ProofChain` |  |
| `drinfeld.prove_nambu_double_jacobi_via_twist` | Leibniz–Jacobi of the Nambu double (form), via the twist argument | `N` (must have FI declared), `U, omega, V, eta, W, mu, f, slots` | `(ProofChain, List[Theorem])` | FI declared on `N` (`ValueError` otherwise); slow |
| `drinfeld.prove_h_bilinearity` | $H(U,V)=\iota_V\iota_UH$ is $C^\infty$-linear in both slots | `H, U, V, f, slots` | `(ProofChain, ProofChain)` | TW (5.6)–(5.7) |
| `drinfeld.prove_h_closure_measures_dh` | TW (5.13) defect $=\iota_W\iota_V\iota_U\,dH$ | `N, H, U, V, W, slots` | `ProofChain` | none |
| `drinfeld.prove_h_closure_for_exact_h` | if $H=dB$, TW (5.13) holds | `N, B, U, V, W, slots` | `ProofChain` | slow for $p=2$ |
| `drinfeld.prove_h_twisted_jacobi_measures_dh` | form$(\mathrm{Jac}_H(e_1,e_2,e_3))=\iota_W\iota_V\iota_U\,dH$ | `N, H, U, omega, V, eta, W, mu, f, slots` | `(ProofChain, List[Theorem])` | "twisted Courant ⇔ $dH=0$" |
| `drinfeld.prove_fi_collapses_twisted_compat` | $H(U,R(\eta,\mu))=0$ under FI | `N, H, U, eta, mu, slots` | `ProofChain` | FI |
| `drinfeld.prove_twisted_fi_kills_r_twist_h` | $R'_H(\omega,\eta)=0$ under H-twisted FI | `N, H, omega, eta, h` | `ProofChain` | `TwistedFIDeclaration` |
| `drinfeld.prove_r_twist_h_correction_bilinear` | $\Pi H(\Pi\omega,\Pi\eta)$ is $C^\infty$-bilinear | `N, H, omega, eta, f, h` | `(ProofChain, ProofChain)` |  |
| `drinfeld.prove_r_twist_psi_properties` | $R_\psi$ is antisymmetric and $C^\infty$-bilinear | `psi_host, omega, eta, f, h` | `(ProofChain, ProofChain, ProofChain)` |  |
| `drinfeld.prove_psi_twisted_fi_consistency` | $R'(\omega,\eta)-R_\psi(\omega,\eta)=0$ under ψ-twisted FI | `P, psi_host, omega, eta, h` | `ProofChain` | `PsiTwistedFIDeclaration` |
| `drinfeld.prove_bn_symmetric_part` | symmetric part of $B_n$ $=(0,0,dg_E)$ | `U, f, omega, V, g, eta`; `Y`: probe | `(ProofChain, ProofChain, ProofChain)` |  |
| `drinfeld.prove_bn_right_leibniz` | $[e_1,se_2]=s[e_1,e_2]+(Us)e_2$ | `U, f, omega, V, g, eta`; `s`: function; `Y` | `(ProofChain, ProofChain, ProofChain)` |  |
| `drinfeld.prove_bn_twist_symmetric_part` | $g\,df+f\,dg=d(fg)$ | `f, g, Y` | `ProofChain` | TW (5.21) |
| `drinfeld.prove_bn_split1_z_symmetric_part` | symmetric part of the splitting-1 Z-bracket, $g_Z=fg$ | `f, omega, g, eta, Y` | `ProofChain` | TW (8.19) |
| `drinfeld.prove_exceptional_symmetric_part` | symmetric part $=d$(1-form pairing), $d$(4-form pairing) | `N, U, om2, om5, V, et2, et5, slots2, slots5` | `(ProofChain, ProofChain)` | none |
| `drinfeld.prove_exceptional_right_leibniz` | right-Leibniz, $\rho(e_1)=U$ (two form components) | `N, U, om2, om5, V, et2, et5, f, slots2, slots5` | `(ProofChain, ProofChain)` |  |
| `drinfeld.prove_exceptional_h_second_entry_linear` | $H(e_1,fe_2)=fH(e_1,e_2)$ | `U, om2, V, et2, f, slots5` | `ProofChain` | TW (8.2) |
| `drinfeld.prove_exceptional_h_first_entry_symbol` | $H(fe_1,e_2)-fH(e_1,e_2)=-\eta_2\wedge df\wedge\omega_2$ | `U, om2, V, et2, f, slots5` | `ProofChain` |  |
| `drinfeld.prove_top_slot_jacobi` | $[x,[y,z]]_{\mathrm{top}}-[[x,y],z]_{\mathrm{top}}-[y,[x,z]]_{\mathrm{top}}=0$ ($TM\oplus\Lambda^p\oplus\Lambda^{2p+1}$) | `N, U, om2, om5, V, et2, et5, W, ze2, ze5, slots_top`; `cite_dorfman=` | `(ProofChain, Tuple[str, ...])` | closes for even $p$ and does not close for odd $p$; with `cite_dorfman=True` the Dorfman Jacobi identity is cited and listed in the returned assumption texts |
| `drinfeld.prove_exceptional_jacobi_five` | the $p=2$ (E6, $\Lambda^2\oplus\Lambda^5$) case of `prove_top_slot_jacobi` | `*args, **kwargs` → same as `prove_top_slot_jacobi` | `(ProofChain, Tuple[str, ...])` | wrapper with the arguments of `prove_top_slot_jacobi` |
| `drinfeld.prove_exceptional_twist_inverse` | $\Psi_\Pi^{-1}\circ\Psi_\Pi=\mathrm{id}$ (vector) | `N3, N6, U, om2, om5, h` | `ProofChain` |  |
| `drinfeld.prove_exceptional_twist_linear` | $\Psi_\Pi(fe)=f\Psi_\Pi(e)$ (vector) | `N3, N6, U, om2, om5, f, h` | `ProofChain` |  |

## Rules the engine applies automatically

These rules are registered by `twist_engine`, `nambu_tilde_engine` and by the `prove_*`
builders. They live in submodules and are not exported by the facade.

| Rule | Mathematical counterpart |
|---|---|
| `InteriorAnticommuteDefinition` | $\iota_X\iota_Y x\to-\iota_Y\iota_X x$ (canonical order; alternation of forms) |
| `FISharpPairingSwapDefinition` | consequence of FI, used as a theorem: $\Pi(d(\iota_{\Pi a}b))\to-\Pi(d(\iota_{\Pi b}a))$ (only under the Cartan $d$ of $TM$) |
| `NambuSharpPairingEvalDefinition` | $\langle\beta,\Pi\omega\rangle\to\Pi(\alpha_1,\dots,\alpha_p,\beta)$ for $\omega=\alpha_1\wedge\dots\wedge\alpha_p$ |
| `SharpSlotWedgeNormalizeDefinition` | canonical wedge order in the form slot of sharp: $\psi^\sharp(\eta\wedge\omega)\to-\psi^\sharp(\omega\wedge\eta)$ |
