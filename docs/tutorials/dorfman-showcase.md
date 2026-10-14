# Showcase: the Dorfman bracket

This tutorial uses the research interface `jacopy.research` to check the axioms
of the Dorfman bracket on the generalized tangent bundle $TM \oplus T^*M$, to
transport the whole structure by a bivector twist, and to see what happens with a
wrong anchor. The longest check, the Leibniz–Jacobi identity on the form
component, is a proof of several hundred steps that runs in about a second.

## The data

A section of $TM \oplus T^*M$ is a pair $U + \omega$ of a vector field and a
1-form. The Dorfman bracket, its anchor, its pairing and its coboundary are

$$[U+\omega, V+\eta] = [U,V] + \mathcal{L}_U\eta - \iota_V d\omega, \qquad
\rho(U+\omega) = U,$$

$$\langle U+\omega, V+\eta\rangle = \iota_U\eta + \iota_V\omega, \qquad
D g = dg .$$

In JacoPy these are given component by component to `AlgebroidData`:

```python
import jacopy
from jacopy.central.tangent import d
from jacopy.packages.drinfeld import canonical_pairing, dorfman_double
from jacopy.packages.poisson import nambu_structure
from jacopy.research import AlgebroidData, AxiomSuite, BlockMatrix, Bracket, Map, SectionType

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
U, V, W = jacopy.vector_fields("U V W")
omega, eta, mu = jacopy.forms("omega eta mu", degree=1)

T = SectionType.generalized_tangent()          # TM ⊕ T*M
dorfman = AlgebroidData(
    bracket=Bracket.from_components(T, dorfman_double, name="Dorfman"),
    anchor=lambda e: e[0],
    pairing=lambda a, b: (canonical_pairing(*a, *b),),
    D=lambda g: T.section(jacopy.Zero, d(g)),
    lie_R=lambda e, g: (jacopy.Act(e[0], g),),
    name="standard",
)

e1, e2, e3 = T.section(U, omega), T.section(V, eta), T.section(W, mu)
print(T)
print(dorfman.bracket(e1, e2))
```

```text
TM ⊕ Λ¹T*M
[U,V]_VF ⊕ (L_U(eta) + (-L_V(omega)) + d(ι_V(omega)))
```

JacoPy writes the form component as
$\mathcal{L}_U\eta - \mathcal{L}_V\omega + d\,\iota_V\omega$, which equals
$\mathcal{L}_U\eta - \iota_V d\omega$ by Cartan's formula.

## The axiom suite

`AxiomSuite.run` checks, component by component,

* right Leibniz: $[e_1, f e_2] = f[e_1,e_2] + (\rho(e_1)f)\,e_2$,
* symmetric part: $[e_1,e_2] + [e_2,e_1] = D\langle e_1,e_2\rangle$,
* anchor morphism: $\rho([e_1,e_2]) = [\rho e_1, \rho e_2]$,

and, when a third section is given,

* metric invariance:
  $\rho(e_1)\langle e_2,e_3\rangle = \langle [e_1,e_2], e_3\rangle + \langle e_2, [e_1,e_3]\rangle$,
* Leibniz–Jacobi: $[e_1,[e_2,e_3]] = [[e_1,e_2],e_3] + [e_2,[e_1,e_3]]$.

`probe=h` is the test function on which vector-valued components are compared.
The `structures` argument lists the structures in scope. `nambu_structure("theta", p=1)`
creates a bivector $\theta$ (a $(p+1)$-vector with $p = 1$) for the next section; it
declares nothing, in particular not the Poisson condition.

```python
theta = nambu_structure("theta", p=1)

report = AxiomSuite(dorfman, registry=reg, probe=h, structures=(theta,)).run(e1, e2, f, e3=e3)
print(report)
```

```text
axiom suite for standard on TM ⊕ Λ¹T*M
  CLOSED   right-Leibniz          TM             ( 0.00s)
  CLOSED   right-Leibniz          Λ¹T*M          ( 0.04s)
  CLOSED   symmetric part         TM             ( 0.00s)
  CLOSED   symmetric part         Λ¹T*M          ( 0.01s)
  CLOSED   anchor morphism        ρ on probe     ( 0.00s)
  CLOSED   metric invariance      pairing component 1 (scalar) ( 0.02s)
  CLOSED   Leibniz-Jacobi         TM             ( 0.01s 18 steps)
  CLOSED   Leibniz-Jacobi         Λ¹T*M          ( 1.09s 445 steps)
  → ALL CLOSED
```

Every condition closes, and no axiom was declared for any structure: the checks
rest on the definitions of the operators. The step counts show the size of the Leibniz–Jacobi proofs. (The
timings in the report vary from run to run.)

## Twisting by a bivector

For a bivector $\theta$ let $\theta^\sharp: T^*M \to TM$ be its contraction and

$$\Psi = \begin{pmatrix} 1 & \theta^\sharp \\ 0 & 1 \end{pmatrix}.$$

`transport` moves the whole structure along $\Psi$:
$[\cdot,\cdot]' = \Psi^{-1}[\Psi\cdot,\Psi\cdot]$, $\rho' = \rho\circ\Psi$,
$\langle\cdot,\cdot\rangle' = \langle\Psi\cdot,\Psi\cdot\rangle$ and
$D' = \Psi^{-1}\circ D$. The inverse of $\Psi$ is derived, not typed in.

```python
Psi = BlockMatrix(T, [[1, Map(theta.sharp_vf, "θ♯")], [0, 1]], name="Ψ")
print(Psi)

twisted = dorfman.transport(Psi)
print(AxiomSuite(twisted, registry=reg, probe=h, structures=(theta,)).run(e1, e2, f))
```

```text
Ψ =
( 1   θ♯ )
( 0   1  )
axiom suite for standard_Ψ on TM ⊕ Λ¹T*M
  CLOSED   right-Leibniz          TM             ( 0.23s)
  CLOSED   right-Leibniz          Λ¹T*M          ( 0.11s)
  CLOSED   symmetric part         TM             ( 0.12s)
  CLOSED   symmetric part         Λ¹T*M          ( 0.06s)
  CLOSED   anchor morphism        ρ on probe     ( 0.11s)
  → ALL CLOSED
```

Right Leibniz, the symmetric part and the anchor morphism property hold for the
twisted structure for every bivector $\theta$; no Poisson condition was declared or
needed.

## A wrong anchor

If the anchor is changed to $\rho(U+\omega) = U + \theta^\sharp\omega$ while the
bracket stays the Dorfman bracket, the suite does not close, and each residual
names the defect:

```python
wrong = AlgebroidData(
    bracket=Bracket.from_components(T, dorfman_double, name="Dorfman"),
    anchor=lambda e: e[0] + theta.sharp_vf(e[1]),
    name="wrong anchor",
)
report = AxiomSuite(wrong, registry=reg, probe=h, structures=(theta,)).run(e1, e2, f)
print(report.all_closed)
for r in report.results[:2]:
    print(r.status, "|", r.residual)
```

```text
False
RESIDUAL | (V(h) * theta(d(f), omega))
RESIDUAL | (theta(d(f), omega) * ⟨eta, ξ₁⟩)
```

Both residuals come from right Leibniz: the extra anchor term
$\theta^\sharp\omega$ differentiates $f$, and the resulting factor
$\theta(df, \omega)$ is not matched by anything in the Dorfman bracket. The vector
component is tested on the probe $h$; the form component is evaluated on a fresh
vector field $\xi_1$.

## Where to go next

* The notebooks in the repository's `examples/` directory continue from here:
  `bracket_twist_research_interface.ipynb` covers higher-degree versions of this
  construction, $TM \oplus \Lambda^2 T^*M \oplus \Lambda^5 T^*M$, and frame
  formulas.
* [Defining your own bracket](own-bracket.md) shows the lower-level route for
  brackets that do not fit a component formula.
