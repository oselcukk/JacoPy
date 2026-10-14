# Poisson, symplectic and Nambu–Poisson geometry

The package `jacopy.packages.poisson` provides Poisson structures $(M,\pi)$, symplectic
structures $(M,\omega)$ and Nambu–Poisson structures $(M,\Pi)$: the Poisson bracket,
Hamiltonian vector fields, $\pi^\sharp$, the Koszul bracket and the cotangent algebroid
$(T^*M,\pi^\sharp,[\cdot,\cdot]_\pi)$, the tilde calculus $(\tilde d,\tilde{\mathcal L},\tilde\iota)$
and the higher Koszul bracket of a Nambu structure. The Roytenberg brackets are in the
[Drinfel'd](drinfeld.md) and [generalized geometry](generalized-geometry.md) packages.

Axioms such as $[\pi,\pi]_{SN}=0$, $d\omega=0$ or the fundamental identity are used in a
proof only when they are **explicitly declared**.

## Setup

```python
import jacopy
reg = jacopy.PropertyRegistry()
f, g, h = jacopy.functions("f g h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta, gamma = jacopy.forms("alpha beta gamma", degree=1)

from jacopy.packages.poisson import (
    poisson_structure, symplectic_structure, nambu_structure,
    poisson_engine, showcase_engine, tilde_engine, symplectic_engine, nambu_engine,
    koszul_bracket, d_tilde, lie_tilde, tilde_calculus, nambu_koszul_bracket,
    tilde_anholonomy_coefficient, tilde_multivector_degree, poisson_view,
    koszul_jacobi_certificate,
)
import jacopy.packages.poisson as poisson
from jacopy.central.objects.tilde_interior import TildeInterior   # not in the facade
from jacopy import Act, Wedge, Integer, exterior_d, interior, multi_eval, pairing
d = exterior_d()
```

## How the objects are set up

The package has three structure objects. Each carries its own data (a bivector, a 2-form,
a $(p+1)$-vector) and brings its axioms into a proof only if they are declared.

```python
P  = poisson_structure("pi", declare=("poisson",))   # (M, pi) with [pi, pi]_SN = 0 declared
P0 = poisson_structure("pi")                         # the same bivector, nothing declared
S  = symplectic_structure("omega")                   # (M, omega), omega a 2-form
N  = nambu_structure("Pi", p=2)                      # Nambu-Poisson, Pi a 3-vector (p + 1 = 3)
omega2, eta2 = jacopy.forms("omega2 eta2", degree=2) # the Nambu bracket takes p-forms
Y1, Y2 = jacopy.vector_fields("Y1 Y2")

E_P  = poisson_engine(registry=reg, structures=(P,))            # {f,g}, X_f, pi-sharp
E_sc = showcase_engine(P, registry=reg)                         # + Koszul bracket
E_t  = tilde_engine(P, registry=reg)                            # + tilde calculus
E_S  = symplectic_engine(S, registry=reg, poisson_bridge=P)     # + omega and pi = omega^-1
E_N  = nambu_engine(N, registry=reg)                            # Nambu sharp rules
```

| Object | Signature | Arguments | What it gives | Note |
|---|---|---|---|---|
| $(M,\pi)$ Poisson structure | `poisson_structure(name, declare=())` | `name`: name of the bivector; `declare`: `("poisson",)` or empty | `PoissonStructure`; `P.pi` is $\pi$ | `P.with_declarations("poisson")` adds the declaration later; `P.declares("poisson")` queries it |
| $(M,\omega)$ symplectic structure | `symplectic_structure(name)` | `name`: str | `SymplecticStructure`; `S.omega` is $\omega$ | $d\omega=0$ is declared on the engine (below), not on the structure |
| $(M,\Pi)$ Nambu–Poisson structure | `nambu_structure(name, p=2, declare=())` | `p`: order ($\Pi$ is a $(p+1)$-vector); `declare`: `("fundamental-identity",)` | `NambuPoissonStructure`; `N.pi` is $\Pi$ | `N.with_declarations("fundamental-identity")` |
| $p=1$ Nambu as Poisson | `poisson_view(N1)` | a Nambu structure with `p=1` | `PoissonStructure` | Reads the same bivector as a Poisson structure |
| engines | `poisson_engine(registry=, structures=(P,), declare_sn=True)`, `showcase_engine(P, registry=, declare_poisson=True)`, `tilde_engine(P, registry=, declare_poisson=True)`, `symplectic_engine(S, registry=, declare_closed=True, poisson_bridge=None)`, `nambu_engine(N, registry=)` | structure and registry | `ExpansionEngine` | `engine.expand(expr)` returns `(expanded expression, steps)`. In `poisson_engine` the default `declare_sn=True` treats every structure passed as Poisson; use `declare_sn=False` to work without the declaration |

### Declarations

| Declaration class | Axiom | How it is declared |
|---|---|---|
| `PoissonSNDeclaration` | $[\pi,\pi]_{SN}=0$ | `poisson_structure(..., declare=("poisson",))`; or `poisson_engine(..., declare_sn=True)` (default); in `showcase_engine` and `tilde_engine`, `declare_poisson=True` |
| `SymplecticClosedDeclaration` | $d\omega=0$ | `symplectic_engine(S, declare_closed=True)` (default) |
| `SharpFlatIdentityDeclaration` | $\pi^\sharp(\iota_X\omega)=X$ (the bridge $\pi=\omega^{-1}$) | `symplectic_engine(S, poisson_bridge=P)` |
| `PoissonOmegaBridgeDeclaration` | $\pi(df,dg)=\omega(X_g,X_f)$ | `symplectic_engine(S, poisson_bridge=P)` |
| `NambuFIDeclaration` | fundamental identity in bracket-morphism form, $[\Pi\omega,\Pi\eta]=\Pi[\omega,\eta]_\Pi$ (on exact generators) | `nambu_structure(..., declare=("fundamental-identity",))`; `prove_nambu_leibniz_jacobi_on_exacts(..., declare_fi=True)` (default) |

## Poisson bracket, Hamiltonian vector field, $\pi^\sharp$

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\{f,g\}$ | `P.bracket(f, g)` | f, g: functions | $\{f,\, g\}$ | `E_P.expand(P.bracket(f, g))[0]` gives $\pi(d(f),\, d(g))$ |
| $\pi(\alpha,\beta)$ | `multi_eval(P.pi, alpha, beta, slot_kind="covector")` | alpha, beta: 1-forms | $\pi(\alpha,\, \beta)$ | The bivector is evaluated on 1-forms; `slot_kind="covector"` is required |
| $X_f$ | `P.hamiltonian(f)` | f: function | $X_{f}$ | A vector field |
| $X_f(g)$ | `Act(P.hamiltonian(f), g)` | f, g: functions | $X_{f}(g)$ | Expands to $\pi(d(f),\, d(g))$, i.e. $X_f(g)=\{f,g\}$ |
| $\pi^\sharp$ (operator) | `P.sharp()` | | $\pi^{\sharp}$ | Musical operator on forms |
| $\pi^\sharp\alpha$ | `P.sharp_vf(alpha)` | alpha: 1-form | $\pi^{\sharp}(\alpha)$ | A vector field (the anchor of the cotangent algebroid) |
| $\langle\beta,\pi^\sharp\alpha\rangle$ | `pairing(beta, P.sharp_vf(alpha))` | beta, alpha: 1-forms | $\langle \beta,\, \pi^{\sharp}(\alpha) \rangle$ | Expands to $\pi(\alpha,\, \beta)$ |
| $(\pi^\sharp\alpha)(f)$ | `Act(P.sharp_vf(alpha), f)` | alpha: 1-form; f: function | | Expands to $\pi(\alpha,\, d(f))$ |

## Koszul bracket and the cotangent algebroid

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $[\alpha,\beta]_\pi$ | `koszul_bracket(P, alpha, beta)` | P: Poisson structure; alpha, beta: **1-forms** | $\left[\alpha,\, \beta\right]_{\pi}$ | `ValueError` for a 2-form (the higher-degree version is the Nambu bracket below) |
| $[df,dg]_\pi$ | `koszul_bracket(P, d(f), d(g))` | f, g: functions | $\left[d(f),\, d(g)\right]_{\pi}$ | |
| $\langle[\alpha,\beta]_\pi,X\rangle$ expanded | `E_sc.expand(pairing(koszul_bracket(P, alpha, beta), X))[0]` | X: vector field | $\pi(\alpha, d\langle\beta,X\rangle) + \langle\beta,[X,\pi^\sharp\alpha]\rangle - \pi(\beta, d\langle\alpha,X\rangle) - \langle\alpha,[X,\pi^\sharp\beta]\rangle - X(\pi(\alpha,\beta))$ | Shown after collecting signs |
| cotangent algebroid engine | `showcase_engine(P, registry=reg)` | P; `declare_poisson` | `ExpansionEngine` | Anchor $\pi^\sharp$, bracket $[\cdot,\cdot]_\pi$ |
| Koszul–Jacobi certificate | `koszul_jacobi_certificate(P, alpha, beta, gamma, X, f, target=None, registry=reg)` | 1-forms; X: probe vector field; f: function | `KoszulJacobiCertificate` ($\mathrm{Jac}=\sum_ic_iS_i$) | Used by `prove_general_koszul_jacobi`; slow |

## Symplectic form, $\omega^\flat$, symplectic Hamiltonian

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\omega^\flat(X)=\iota_X\omega$ | `S.flat(X)` | X: vector field | $\iota_{X}(\omega)$ | 1-form |
| $X_f$ with $\iota_{X_f}\omega=df$ | `S.hamiltonian(f)` | f: function | $X_{f}$ | A different node from the Poisson `P.hamiltonian(f)` (shown as `X^ω_f` in text) |
| $\omega(X,Y)$ | `multi_eval(S.omega, X, Y)` | X, Y: vector fields | $\omega(X,\, Y)$ | |
| $\iota_{X_f}\omega$ expanded | `E_S.expand(Act(interior(S.hamiltonian(f)), S.omega))[0]` | | $d(f)$ | Rule `SymplecticHamiltonianDefinition` |

## Tilde calculus $(\tilde d,\tilde{\mathcal L},\tilde\iota)$

This is the calculus of the cotangent algebroid: its "sections" are 1-forms and its "forms"
are multivectors (functions have degree 0, vector fields degree 1).

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| tilde calculus | `tilde_calculus(P)` | P | `BracketCalculus` | The pair $(\pi^\sharp,[\cdot,\cdot]_\pi)$ |
| $\tilde d f$, $\tilde d X$ | `d_tilde(P, f)`, `d_tilde(P, X)` | function or multivector | $\tilde{d}(f)$, $\tilde{d}(X)$ | $\tilde d:\mathfrak X^p\to\mathfrak X^{p+1}$ |
| $\tilde{\mathcal L}_\alpha X$ | `Act(lie_tilde(P, alpha), X)` | alpha: 1-form; X: multivector | $\tilde{\mathcal{L}}_{\alpha}(X)$ | |
| $\tilde\iota_\alpha X$ | `Act(TildeInterior(alpha), X)` | alpha: 1-form | $\tilde{\iota}_{\alpha}(X)$ | `TildeInterior` is imported from `jacopy.central.objects.tilde_interior` |
| $\langle\tilde df,\alpha\rangle$ expanded | `E_t.expand(pairing(d_tilde(P, f), alpha))[0]` | | $\pi(\alpha,\, d(f))$ | |
| $\tilde\gamma_c{}^{ab}=\langle[e^a,e^b]_\pi,e_c\rangle$ | `tilde_anholonomy_coefficient(P, jacopy.frame("e"), "a", "b", "c")` | frame; indices a, b, c | $\tilde{\gamma}_{c}^{ab}$ | `"b", "a", "c"` gives $-\tilde{\gamma}_{c}^{ab}$; `"a", "a", "c"` gives 0 |
| tilde degree $\lvert\tilde dX\rvert$ | `tilde_multivector_degree("tilde-pi", d_tilde(P, X), reg)` | calculus name; expression; registry | `2` | $\lvert\tilde d x\rvert=\lvert x\rvert+1$, $\lvert\tilde\iota x\rvert=\lvert x\rvert-1$ |

## Nambu–Poisson structures and the higher Koszul bracket

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\Pi\omega$ | `N.sharp_vf(omega2)` | a $p$-form | $\Pi(\omega2)$ | For an atomic $\omega$, $(\Pi\omega)(f)$ is deliberately not expanded |
| $(\Pi(df\wedge dg))(h)$ | `Act(N.sharp_vf(Wedge(d(f), d(g))), h)` | f, g, h: functions | | `E_N` expands it to $\Pi(d(f),\, d(g),\, d(h))$, the Nambu bracket $\{f,g,h\}$ |
| $[\omega,\eta]_\Pi=\mathcal L_{\Pi\omega}\eta-\iota_{\Pi\eta}d\omega$ | `nambu_koszul_bracket(N, omega2, eta2)` | $p$-forms | $\mathcal{L}_{\Pi(\omega2)}(\eta2) - \iota_{\Pi(\eta2)}(d(\omega2))$ | Not antisymmetric: a Leibniz algebroid bracket |

## Trying your own identity

The `prove_*` builders below cover ready-made identities. To try an identity of your own
with a package engine, use `jacopy.proof.result.prove`, which reports the status and the
assumptions used:

```python
from jacopy.proof.result import prove
r = prove(poisson_engine(registry=reg, structures=(P,), declare_sn=False),
          P.bracket(f, g), -P.bracket(g, f), registry=reg)
print(r.status, r.requires)
```

```text
CLOSED ()
```

Antisymmetry of the Poisson bracket holds for every bivector, so it closes without any
assumption. The Jacobi identity needs the declaration $[\pi,\pi]_{SN}=0$:

```python
chain, thm = poisson.prove_poisson_jacobi(P, f, g, h, registry=reg)
print(len(chain.steps), "steps;", [a.kind for a in thm.requires])
chain = poisson.prove_bracket_via_omega(P, S, f, g, registry=reg)
print(jacopy.to_latex(chain.initial))
```

```text
3 steps; ['declared', 'structure', 'scope', 'unreplayed']
\{f,\, g\}
```

## Theorem builders

All builders are imported from `jacopy.packages.poisson` and take `registry=reg`. Every
builder except `prove_poisson_jacobi` returns only a `ProofChain`. The last column states
which declaration the proof relies on ("none" means it holds for every bivector, 2-form or
Nambu tensor).

| Builder | Identity it proves | Arguments | Returns | Uses |
|---|---|---|---|---|
| `poisson.prove_poisson_antisymmetry` | $\{f,g\}=-\{g,f\}$ | P: Poisson structure; f, g: functions | `ProofChain` | none |
| `poisson.prove_poisson_leibniz` | $\{f,gh\}=g\{f,h\}+h\{f,g\}$ | P; f, g, h | `ProofChain` | none |
| `poisson.prove_poisson_constant` | $\{f,c\}=0$ | P; f; c: numeric constant (for example `Integer(3)`) | `ProofChain` | none |
| `poisson.prove_hamiltonian_is_sharp` | $\langle dg,\pi^\sharp df\rangle=X_f(g)$ | P; f, g | `ProofChain` | none |
| `poisson.prove_poisson_jacobi` | $\{f,\{g,h\}\}+\{g,\{h,f\}\}+\{h,\{f,g\}\}=0$ | P; f, g, h | `(ProofChain, Theorem)` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_koszul_antisymmetry` | $[\alpha,\beta]_\pi=-[\beta,\alpha]_\pi$ | P; alpha, beta: 1-forms | `ProofChain` | none |
| `poisson.prove_koszul_on_exact_forms` | $\langle[df,dg]_\pi,Y\rangle=\langle d\{f,g\},Y\rangle$ | P; f, g; Y: vector field | `ProofChain` | none |
| `poisson.prove_koszul_right_leibniz` | $\langle[\alpha,f\beta]_\pi,Y\rangle=\langle f[\alpha,\beta]_\pi+(\pi^\sharp\alpha)(f)\beta,Y\rangle$ | P; alpha, beta; f; Y | `ProofChain` | none |
| `poisson.prove_hamiltonian_morphism` | $X_{\{f,g\}}(h)=[X_f,X_g](h)$ | P; f, g, h | `ProofChain` | $[\pi,\pi]_{SN}=0$ (cites the Jacobi instance) |
| `poisson.prove_sn_eval_views_agree_on_exacts` | $2\langle dh,[\pi^\sharp df,\pi^\sharp dg]-\pi^\sharp[df,dg]_\pi\rangle=2\sum_{\mathrm{cyc}}\pi(df,d\pi(dg,dh))$ | P; f, g, h | `ProofChain` | none (the two evaluations of $[\pi,\pi]_{SN}$ agree) |
| `poisson.prove_general_koszul_jacobi` | $\langle[\alpha,[\beta,\gamma]_\pi]_\pi+[\beta,[\gamma,\alpha]_\pi]_\pi+[\gamma,[\alpha,\beta]_\pi]_\pi,X\rangle=0$ | P; alpha, beta, gamma: 1-forms; X: vector field; f: function; `declare_poisson=True`, `max_rounds=40` | `ProofChain` | $[\pi,\pi]_{SN}=0$; slow (certificate search) |
| `poisson.prove_koszul_zero_by_certificate` | $\mathrm{target}=\sum_ic_iS_i=0$ | P; target; certificate from `koszul_jacobi_certificate`; `max_steps=20000` | `ProofChain` | the declarations of the certificate seeds |
| `poisson.prove_hamiltonian_flow_invariance` | $(\mathcal L_{X_f}\omega)(Y,Z)=0$ | S: symplectic structure; f; Y, Z | `ProofChain` | $d\omega=0$ |
| `poisson.prove_bracket_via_omega` | $\{f,g\}=\omega(X_g,X_f)$ | P; S; f, g | `ProofChain` | bridge $\pi=\omega^{-1}$ |
| `poisson.prove_bracket_via_iota` | $\{f,g\}=\iota_{X_f}dg$ | P; S; f, g | `ProofChain` | bridge |
| `poisson.prove_bracket_via_double_iota` | $\{f,g\}=\iota_{X_f}\iota_{X_g}\omega$ | P; S; f, g | `ProofChain` | bridge |
| `poisson.prove_sharp_flat_identity` | $\langle\beta,\pi^\sharp(\iota_X\omega)\rangle=\langle\beta,X\rangle$ | P; S; X; beta | `ProofChain` | `SharpFlatIdentityDeclaration` |
| `poisson.prove_d_tilde_on_functions` | $\langle\tilde df,\alpha\rangle=\pi(\alpha,df)$ | P; f; alpha | `ProofChain` | none |
| `poisson.prove_d_tilde_palais_on_vectors` | $(\tilde dX)(\alpha,\beta)=(\pi^\sharp\alpha)\langle X,\beta\rangle-(\pi^\sharp\beta)\langle X,\alpha\rangle-\langle X,[\alpha,\beta]_\pi\rangle$ | P; X; alpha, beta | `ProofChain` | none |
| `poisson.prove_tilde_magic_on_functions` | $\tilde{\mathcal L}_\alpha f=(\tilde d\tilde\iota_\alpha+\tilde\iota_\alpha\tilde d)f$ | P; alpha; f | `ProofChain` | none |
| `poisson.prove_tilde_magic_on_vectors` | $\langle\tilde{\mathcal L}_\alpha X,\beta\rangle=\langle(\tilde d\tilde\iota_\alpha+\tilde\iota_\alpha\tilde d)X,\beta\rangle$ | P; alpha; X; beta | `ProofChain` | none |
| `poisson.prove_d_tilde_squared_on_exacts` | $(\tilde d\tilde df)(dg,dh)=0$ | P; f, g, h | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_lie_tilde_iota_commutator_on_vectors` | $\tilde{\mathcal L}_\alpha(\tilde\iota_\beta X)-\tilde\iota_\beta(\tilde{\mathcal L}_\alpha X)=\tilde\iota_{[\alpha,\beta]_\pi}X$ | P; alpha, beta; X | `ProofChain` | none |
| `poisson.prove_lie_tilde_commutator_on_exacts` | $\langle(\tilde{\mathcal L}_{df}\tilde{\mathcal L}_{dg}-\tilde{\mathcal L}_{dg}\tilde{\mathcal L}_{df}-\tilde{\mathcal L}_{[df,dg]_\pi})X,dh\rangle=0$ | P; f, g; X; h | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_lie_tilde_d_iota_commutation_on_exacts` | $\langle\tilde{\mathcal L}_{df}\tilde d\tilde\iota_{dg}X-\tilde d\tilde\iota_{[df,dg]_\pi}X-\tilde d\tilde\iota_{dg}\tilde{\mathcal L}_{df}X,dh\rangle=0$ | P; f, g; X; h | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_lie_tilde_d_iota_commutation_general` | $\langle\tilde{\mathcal L}_\alpha\tilde d\tilde\iota_\beta X-\tilde d\tilde\iota_{[\alpha,\beta]_\pi}X-\tilde d\tilde\iota_\beta\tilde{\mathcal L}_\alpha X,\gamma\rangle=0$ | P; alpha, beta; X; gamma | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_lie_tilde_d_iota_exact_on_exacts` | $\langle\tilde{\mathcal L}_{dg}\tilde d\tilde\iota_{df}X-\tilde d\tilde\iota_{dg}\tilde d\tilde\iota_{df}X,dh\rangle=0$ | P; f, g; X; h | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_lie_tilde_d_iota_exact_general` | $\langle\tilde{\mathcal L}_\beta\tilde d\tilde\iota_\alpha X-\tilde d\tilde\iota_\beta\tilde d\tilde\iota_\alpha X,\gamma\rangle=0$ | P; alpha, beta; X; gamma | `ProofChain` | $[\pi,\pi]_{SN}=0$ |
| `poisson.prove_tilde_gamma_antisymmetry` | $\langle[e^a,e^b]_\pi,e_c\rangle=-\langle[e^b,e^a]_\pi,e_c\rangle$ | P; frame (`jacopy.frame("e")`); indices a, b, c | `ProofChain` | none |
| `poisson.prove_nambu_right_leibniz` | $[\omega,f\eta]_\Pi=f[\omega,\eta]_\Pi+(\Pi\omega)(f)\eta$ (evaluated on slots) | N: Nambu structure; omega, eta: $p$-forms; f; slots: $p$ vector fields, for example `(Y1, Y2)` | `ProofChain` | none |
| `poisson.prove_nambu_symmetric_part_exact` | $[\omega,\eta]_\Pi+[\eta,\omega]_\Pi=d(\iota_{\Pi\omega}\eta+\iota_{\Pi\eta}\omega)$ | N; omega, eta; slots | `ProofChain` | none |
| `poisson.prove_nambu_leibniz_jacobi_on_exacts` | $[\omega,[\eta,\mu]_\Pi]_\Pi=[[\omega,\eta]_\Pi,\mu]_\Pi+[\eta,[\omega,\mu]_\Pi]_\Pi$ for $\omega=dF_1\wedge\dots\wedge dF_p$ etc. | N; F, G, H: tuples of $p$ functions, for example `(F1, F2)`; slots; `declare_fi=True`, `max_steps=20000` | `ProofChain` | fundamental identity; with `declare_fi=False` it does not close |
| `poisson.prove_dorfman_form_reduces_to_koszul_at_p1` | $\langle\mathcal L_{\pi^\sharp\alpha}\beta-\iota_{\pi^\sharp\beta}d\alpha,Y\rangle=\langle[\alpha,\beta]_\pi,Y\rangle$ | P ($p=1$); alpha, beta; Y | `ProofChain` | none (Cartan magic formula) |

## Rules the engine applies automatically

These rules are registered when the corresponding engine (`poisson_engine`,
`showcase_engine`, `tilde_engine`, `symplectic_engine`, `nambu_engine`) is set up. They
appear as step names in proof chains.

| Rule | Mathematical counterpart |
|---|---|
| `PoissonBracketDefinition` | $\{f,g\}\to\pi(df,dg)$ |
| `HamiltonianActionDefinition` | $X_f(g)\to\{f,g\}$ ($g$ a function) |
| `SharpEvaluationDefinition` | $\langle\beta,\pi^\sharp\alpha\rangle\to\pi(\alpha,\beta)$ |
| `SharpActionDefinition` | $(\pi^\sharp\alpha)(g)\to\pi(\alpha,dg)$ |
| `PVectorEvalLinearityDefinition` | multilinearity of the $p$-vector evaluation in its form slots |
| `KoszulBracketDefinition` | $[\alpha,\beta]_\pi\to\mathcal L_{\pi^\sharp\alpha}\beta-\mathcal L_{\pi^\sharp\beta}\alpha-d\,\pi(\alpha,\beta)$ |
| `SharpVFLinearityDefinition` | $\pi^\sharp(f\alpha+\beta)\to f\pi^\sharp\alpha+\pi^\sharp\beta$ |
| `SharpPairingLinearityDefinition` | linearity of the pairing in the vector slot (guarded for $\pi^\sharp$ slots) |
| `SNBivectorExactEvalDefinition` | $[\pi,\pi](df,dg,dh)\to2\sum_{\mathrm{cyc}}\pi(df,d\pi(dg,dh))$ |
| `SNBivectorGeneralEvalDefinition` | $[\pi,\pi](\alpha,\beta,\gamma)\to2(\langle\gamma,[\pi^\sharp\alpha,\pi^\sharp\beta]\rangle-\langle\gamma,\pi^\sharp[\alpha,\beta]_\pi\rangle)$ |
| `SymplecticHamiltonianDefinition` | $\iota_{X_f}\omega\to df$ |
| `LieDCommutationDefinition` | $\mathcal L_X(df)\to d(X(f))$ |
| `TildeAnholonomyDefinition` | $\langle[e^a,e^b]_\pi,e_c\rangle\to\tilde\gamma_c{}^{ab}$ |
| `TildeInteriorActDefinition` | $\tilde\iota_\alpha f\to0$, $\tilde\iota_\alpha X\to\langle X,\alpha\rangle$ |
| `TildeInteriorEvalDefinition` | $(\tilde\iota_\alpha V)(\beta,\dots)\to V(\alpha,\beta,\dots)$ |
| `NambuSharpActionDefinition` | $(\Pi\omega)(f)\to\Pi(\alpha_1,\dots,\alpha_p,df)$ for $\omega=\alpha_1\wedge\dots\wedge\alpha_p$ |
| `NambuSharpLinearityDefinition` | $\mathbb R$- and $C^\infty$-linearity of $\Pi\omega$ in its form slot |
| `NambuToPoissonSharpDefinition` | at $p=1$, $\Pi(\omega)\to\pi^\sharp\omega$ |
