# Syntax at a glance

A one-page quick reference: the most-used notations, with the mathematics on the left and
the JacoPy code on the right. All entries assume the setup block below. Each group links to
the guide page with the full table, the argument types and further variants.

## Setup

```python
import jacopy
from jacopy.core import Degree, Scalar, Closed
from jacopy.central.tangent import tangent_engine, d, SN
from jacopy.central.algebroid import algebroid, algebroid_engine, jacobiator, d_E, lie_E
from jacopy.central.objects import sharp, flat
from jacopy.proof.result import prove as prove_result
from jacopy.proof import ExplicitAssumption
import jacopy.central.tangent as tg

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta = jacopy.forms("alpha beta", degree=1)
(omega,) = jacopy.forms("omega", degree=2)
P2, Q2 = jacopy.p_vectors("P Q", degree=2)
pi = jacopy.bivector("pi")
(T,) = jacopy.tensors("T", upper=1, lower=2)
g = jacopy.metric("g")
nabla = jacopy.connection()
e = jacopy.frame("e")
E = algebroid("E", declare=("leibniz",))
u, v, w = E.sections("u v w")
(mu,) = jacopy.forms("mu", degree=1, bundle=E.bundle)
eng = tangent_engine(registry=reg)
engE = algebroid_engine(E, registry=reg)
engX = tangent_engine(registry=reg)           # an engine for extra assumptions
chain = jacopy.show_equal(jacopy.lie_derivative(X)(f), X(f), registry=reg, engine=eng)
res = prove_result(eng, jacopy.lie_derivative(X)(Y), jacopy.lie_bracket(X, Y), registry=reg)
```

## Objects

See [Defining objects](objects.md).

| Mathematics | JacoPy |
|---|---|
| property registry | `jacopy.PropertyRegistry()` |
| functions $f_1,f_2\in C^\infty(M)$ | `jacopy.functions("f1 f2", registry=reg)` |
| real constant $\lambda$ | `reg.declare(jacopy.Symbol("lambda"), Scalar())` |
| rational number $\tfrac12$ | `jacopy.Rational(1, 2)` |
| vector fields $X,Y,Z$ | `jacopy.vector_fields("X Y Z")` |
| 1-forms $\alpha,\beta$ | `jacopy.forms("alpha beta", degree=1)` |
| form of symbolic degree $p$ | `jacopy.forms("eta", degree=Degree.var("p"))` |
| 2-vectors $P,Q$ | `jacopy.p_vectors("P Q", degree=2)` |
| $(1,2)$-tensor $T$ | `jacopy.tensors("T", upper=1, lower=2)` |
| metric $g$ | `jacopy.metric("g")` |
| inverse metric $g^{-1}$ | `g.inverse()` |
| $TM$ with $\dim M=3$ | `jacopy.tangent_bundle(dim=3)` |
| connection $\nabla$ | `jacopy.connection()` |
| frame $e_a$ and coframe $e^a$ | `(e.field("a"), e.dual().field("a"))` |

## Algebraic operations

See [Algebraic operations](algebraic-operations.md).

| Mathematics | JacoPy |
|---|---|
| $fX+Y$ | `f*X + Y` |
| $\alpha\wedge\beta$ | `jacopy.wedge(alpha, beta)` |
| $\langle\alpha,X\rangle=\alpha(X)$ | `jacopy.pairing(alpha, X)` |
| $\omega(X,Y)$ | `omega(X, Y)` |
| $(\alpha\wedge\beta)(X,Y)$ | `jacopy.multi_eval(jacopy.wedge(alpha, beta), X, Y)` |
| $X(f)$ | `X(f)` |
| $g(X,Y)$ | `g(X, Y)` |
| $T(\alpha,X,Y)$ | `T(alpha, X, Y)` |
| $P(\alpha,\beta)$ | `P2(alpha, beta)` |
| $g^\flat(X)$ | `flat(g)(X)` |
| $\pi^\sharp(\alpha)$ | `sharp(pi)(alpha)` |
| $\star_g\omega$ | `jacopy.hodge(omega, g)` |
| $\langle e^a,e_b\rangle$ | `e.pairing("a", "b")` |
| normal form of $\omega(Y,X)+\omega(X,Y)$ | `jacopy.normalize(eng, omega(Y, X) + omega(X, Y), reg).expr` |

## Differential operators and brackets on $TM$

See [Cartan calculus](cartan-calculus.md).

| Mathematics | JacoPy |
|---|---|
| $d$ (operator) | `jacopy.exterior_d()` |
| $df$, $d\omega$ | `(d(f), d(omega))` |
| $\iota_X\omega$ | `jacopy.interior(X)(omega)` |
| $\mathcal L_X\omega$ | `jacopy.lie_derivative(X)(omega)` |
| $\mathcal L_Xf$ | `jacopy.lie_derivative(X)(f)` |
| $[X,Y]$ | `jacopy.lie_bracket(X, Y)` |
| $[X,Y](f)$ | `jacopy.lie_bracket(X, Y)(f)` |
| $[P,Q]_{SN}$ | `jacopy.sn_bracket(P2, Q2)` |
| $[\pi,\pi]_{SN}$ | `SN(pi, pi)` |
| $\nabla_XY$ | `nabla(X, Y)` |
| $\nabla_XT$ | `jacopy.covariant_derivative(nabla, X, T)` |
| $(d\alpha)(X,Y)$ | `jacopy.multi_eval(d(alpha), X, Y)` |

## Algebroids

See [Algebroids](algebroids.md).

| Mathematics | JacoPy |
|---|---|
| Leibniz algebroid $(E,\rho,[\cdot,\cdot]_E)$ | `algebroid("E", declare=("leibniz",))` |
| algebroid with no axioms | `algebroid("A")` |
| sections $u,v,w$ | `E.sections("u v w")` |
| $\rho(u)$ | `E.anchor(u)` |
| $\rho(u)(f)$ | `E.act(u, f)` |
| $[u,v]_E$ | `E.bracket(u, v)` |
| $Df$ | `E.D(f)` |
| $d_E\mu$ | `d_E(E, mu)` |
| $\mathcal L^E_uv$ | `lie_E(E, u)(v)` |
| $J^E(u,v,w)$ | `jacobiator(E, u, v, w)` |

## Declaring axioms

See [Defining objects](objects.md) and [Algebroids](algebroids.md).

| Mathematics | JacoPy |
|---|---|
| algebroid axioms | `algebroid("C", declare=("courant",))` |
| add an axiom later | `E.with_declarations("antisymmetric")` |
| $d\omega=0$ (recorded) | `reg.declare(omega, Closed())` |
| is $\omega$ closed? | `reg.has(omega, Closed)` |
| a single assumption $[X,Y]=0$ | `engX.register(ExplicitAssumption(jacopy.lie_bracket(X, Y), jacopy.Zero))` |

## Asking for a proof

See [Running proofs](running-proofs.md).

| Mathematics | JacoPy |
|---|---|
| prove $\mathcal L_Xf=X(f)$ | `jacopy.show_equal(jacopy.lie_derivative(X)(f), X(f), registry=reg, engine=eng)` |
| shortest proof | `jacopy.prove(jacopy.lie_bracket(X, Y)(f), -jacopy.lie_bracket(Y, X)(f), registry=reg, engine=eng, prefer="shortest")` |
| status and assumptions | `prove_result(eng, d(f*h), f*d(h) + h*d(f), registry=reg)` |
| proof on an algebroid | `jacopy.show_equal(lie_E(E, u)(v), E.bracket(u, v), registry=reg, engine=engE)` |
| normal form | `jacopy.normalize(eng, jacopy.lie_derivative(X)(f*h), reg).expr` |
| ready-made theorem $\mathcal L_Xf=\iota_Xdf+d\iota_Xf$ | `tg.prove_cartan_magic_on_functions(X, f, registry=reg)` |
| ready-made theorem $(d\,df)(X,Y)=0$ | `tg.prove_d_squared_zero_on_functions(f, X, Y, registry=reg)` |

## Reading the result

| Mathematics | JacoPy |
|---|---|
| number of steps | `len(chain.steps)` |
| rule of the first step | `chain.steps[0].rule` |
| status (`CLOSED`, `RESIDUAL`, ...) | `res.status` |
| assumptions used | `res.requires` |
| residual of an open proof | `res.residual` |
| summary | `res.summary()` |

## Display and LaTeX

See [Output](output-and-latex.md).

| Mathematics | JacoPy |
|---|---|
| LaTeX string | `jacopy.to_latex(jacopy.lie_derivative(X)(omega))` |
| plain text | `jacopy.to_ascii(jacopy.lie_derivative(X)(omega))` |
| print a proof | `jacopy.print_chain(chain)` |
| Jupyter display | `jacopy.display_chain(chain)` |

## Packages

See [Poisson](poisson.md), [Drinfel'd doubles](drinfeld.md),
[generalized geometry](generalized-geometry.md), [metric-affine geometry](metric-affine.md)
and [your own structure](your-own-structure.md). The imports for this group are:

```python
from jacopy.packages.poisson import poisson_structure, koszul_bracket, prove_poisson_jacobi
from jacopy.packages.drinfeld import dorfman_double
from jacopy.packages.generalized import courant_bracket_std
import jacopy.packages.metric_affine as MA
from jacopy.research import SectionType
(k,) = jacopy.functions("k", registry=reg)
Ps = poisson_structure("pi", declare=("poisson",))
gm = MA.metric("g")
TT = SectionType.generalized_tangent()
```

| Mathematics | JacoPy |
|---|---|
| Poisson structure with $[\pi,\pi]_{SN}=0$ | `poisson_structure("pi", declare=("poisson",))` |
| $\{f,h\}$ | `Ps.bracket(f, h)` |
| Hamiltonian vector field $X_f$ | `Ps.hamiltonian(f)` |
| $[\alpha,\beta]_\pi$ | `koszul_bracket(Ps, alpha, beta)` |
| Jacobi identity for $\{\cdot,\cdot\}$ | `prove_poisson_jacobi(Ps, f, h, k, registry=reg)` |
| Dorfman bracket $[X+\alpha,Y+\beta]$ | `dorfman_double(X, alpha, Y, beta)` |
| Courant bracket on $TM\oplus T^*M$ | `courant_bracket_std(X, alpha, Y, beta)` |
| torsion $T(X,Y)$ | `MA.torsion(nabla, X, Y)` |
| curvature $R(X,Y)Z$ | `MA.curvature(nabla, X, Y, Z)` |
| non-metricity $Q(X,Y,Z)$ | `MA.nonmetricity(nabla, gm, X, Y, Z)` |
| Koszul formula | `MA.prove_koszul_formula(nabla, gm, X, Y, Z, registry=reg)` |
| section $X\oplus\alpha$ of $TM\oplus T^*M$ | `TT.section(X, alpha)` |
