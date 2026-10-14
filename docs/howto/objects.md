# Defining objects

Every JacoPy computation starts by naming the objects it talks about: functions, vector
fields, forms, tensors, a metric, a connection, a frame, an algebroid. This page shows how
each of them is written and fixes the names that the other pages on the core layer use.

## Reading conventions

- **Objects are defined once.** The names below are reused throughout the guide:
  `f, h` functions, `X, Y, Z` vector fields, `alpha, beta` 1-forms, `omega` a 2-form,
  `eta` a form of symbolic degree $p$, `P, Q, pi` 2-vectors, `T` a $(1,2)$-tensor,
  `g` a metric, `nabla` a connection, `e` a frame, `E` an algebroid and `u, v, w` its sections.
- **Factory functions return tuples**, even for a single name:
  `(omega,) = jacopy.forms("omega", degree=2)`.
- **Operators are constructed first, then applied.** $\mathcal L_X\omega$ is written
  `jacopy.lie_derivative(X)(omega)`: `jacopy.lie_derivative(X)` is the operator $\mathcal L_X$
  and `(omega)` applies it.
- **Expressions are inert.** Writing `X(f)` or `jacopy.lie_bracket(X, Y)` builds an expression
  and performs no computation. Expansion, simplification and proof are done by an engine
  (see [Running proofs](running-proofs.md)).
- Several names are given in one string separated by spaces (`"X Y Z"`). Greek names are
  spelled out (`"alpha"`) and are rendered as $\alpha$ in LaTeX.

## The standard setup

The block below creates every object used on the core-layer pages. Each of those pages repeats
it at the top, so that every page can be run on its own.

```python
import jacopy
from jacopy.core import Degree, Scalar
from jacopy.core import (Closed, NonDegenerate, Poisson, Symmetric, Antisymmetric,
                         GradedAntisymmetric, AntiCommuting, GradedCommutative, Graded)
from jacopy.central.objects.frame import FrameIndex
from jacopy.central.algebroid import (algebroid, tangent_algebroid, section_map,
                                      locality_projector, DECLARATIONS, LEVELS)

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
lam = jacopy.Symbol("lambda"); reg.declare(lam, Scalar())
two, half = jacopy.Integer(2), jacopy.Rational(1, 2)
M3 = jacopy.tangent_bundle(dim=3)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta = jacopy.forms("alpha beta", degree=1)
(omega,) = jacopy.forms("omega", degree=2)
p = Degree.var("p"); (eta,) = jacopy.forms("eta", degree=p)
P, Q = jacopy.p_vectors("P Q", degree=2)
pi = jacopy.bivector("pi")
(T,) = jacopy.tensors("T", upper=1, lower=2)
g = jacopy.metric("g"); ginv = g.inverse()
g3 = jacopy.metric("g", bundle=M3)
nabla = jacopy.connection()
e = jacopy.frame("e"); ce = jacopy.coframe("e")
ea, eb = e.fields("a b"); ea_up = ce.field("a")
s = FrameIndex("s")
D = jacopy.Derivation("D", degree=1)
```

## Objects

The table lists the same objects one by one.

| Object (mathematics) | In code | What it does | Typical name |
|---|---|---|---|
| Property registry | `reg = jacopy.PropertyRegistry()` | Stores declarations ("$f$ is a function", "$\lambda$ is a constant", "$\omega$ is closed"). Every proof is given `registry=reg`; there is no hidden global registry. | `reg` |
| Functions $f,h\in C^\infty(M)$ | `f, h = jacopy.functions("f h", registry=reg)` | Smooth functions of degree 0, recorded in `reg` as `Graded(0)`. A tuple is returned even for one name: `(f,) = jacopy.functions("f", registry=reg)`. | `f g h` |
| Real constant $\lambda\in\mathbb R$ | `lam = jacopy.Symbol("lambda"); reg.declare(lam, Scalar())` | A constant, not a function: every derivation kills it ($X(\lambda)=0$) and it commutes freely in products. | `lam`, `c` |
| Numbers $2,\ \tfrac12$ | `two, half = jacopy.Integer(2), jacopy.Rational(1, 2)` | Integer and rational coefficients. Python numbers also work directly: `2*X`. | |
| Tangent bundle $TM$ (symbolic dimension $n$) | `jacopy.TM` | The ready-made $TM$; its dimension is a symbolic $n$. Every object created without an explicit bundle lives on it. | `TM` |
| $TM$ of concrete dimension ($\dim M=3$) | `M3 = jacopy.tangent_bundle(dim=3)` | $TM$ of fixed dimension (for example $n=3$ for the Hodge star). | `M3` |
| Vector fields $X,Y,Z\in\mathfrak X(M)$ | `X, Y, Z = jacopy.vector_fields("X Y Z")` | Sections of $TM$; they act on functions as derivations: `X(f)`. No registry is needed. | `X Y Z U V W` |
| 1-forms $\alpha,\beta\in\Omega^1(M)$ | `alpha, beta = jacopy.forms("alpha beta", degree=1)` | Greek names may be spelled out (`"alpha"` gives $\alpha$). | `alpha beta` |
| 2-form $\omega\in\Omega^2(M)$ | `(omega,) = jacopy.forms("omega", degree=2)` | Alternating; evaluated on exactly two vectors. | `omega` |
| Form of symbolic degree $\eta\in\Omega^p(M)$ | `p = Degree.var("p"); (eta,) = jacopy.forms("eta", degree=p)` | Its degree is a symbolic $p$; Koszul signs are resolved through its parity. Do not call the variable `n`: that name is used for the Hodge dimension. | `eta`, `p` |
| 2-vectors $P,Q\in\Gamma(\Lambda^2TM)$ | `P, Q = jacopy.p_vectors("P Q", degree=2)` | Evaluated on covectors: `P(alpha, beta)`. | `P Q` |
| Bivector $\pi$ | `pi = jacopy.bivector("pi")` | Shortcut for a single 2-vector (for example a Poisson bivector). | `pi` |
| $(1,2)$-tensor $T$ | `(T,) = jacopy.tensors("T", upper=1, lower=2)` | `upper` is the number $q$ of covector slots, `lower` the number $r$ of vector slots; covectors come first: `T(alpha, X, Y)`. | `T S` |
| Metric $g$ and its inverse $g^{-1}$ | `g = jacopy.metric("g"); ginv = g.inverse()` | Symmetric $g(X,Y)$; `g.inverse()` gives $g^{-1}(\alpha,\beta)$. Since the metric uses the name `g`, the functions are called `f, h`. | `g`, `ginv` |
| Metric $g$ in dimension 3 | `g3 = jacopy.metric("g", bundle=M3)` | Makes $n=3$ concrete in the Hodge star. | `g3` |
| Connection $\nabla$ | `nabla = jacopy.connection()` | Default name $\nabla$. `nabla(X, T)` is $\nabla_XT$. | `nabla` |
| Frame $(e_a)$ and coframe $(e^a)$ | `e = jacopy.frame("e"); ce = jacopy.coframe("e")` | Context objects, not expressions. A frame and a coframe with the same name are dual to each other (`e.dual() == ce`). | `e`, `ce` |
| Frame fields $e_a,e_b$ and $e^a$ | `ea, eb = e.fields("a b"); ea_up = ce.field("a")` | Indexed vector fields and 1-forms. | `ea eb` |
| Bound (dummy) index $s$ | `s = FrameIndex("s")` | Index used in sums $\sum_s$. | `s` |
| Graded derivation $D$, $\lvert D\rvert=1$ | `D = jacopy.Derivation("D", degree=1)` | A named graded derivation; `D(f)` applies it and the graded Leibniz rule is automatic. | `D` |
| Leibniz algebroid $(E,\rho,[\cdot,\cdot]_E)$ | `E = algebroid("E", declare=("leibniz",))` | `declare` switches axioms on, individually (`DECLARATIONS`) or by level name (`LEVELS`; `leibniz` = right-leibniz + jacobi). See [Algebroids](algebroids.md). | `E` |
| Sections $u,v,w\in\Gamma(E)$ | `u, v, w = E.sections("u v w")` | Sections of the bundle $E$; they act on functions only through the anchor. | `u v w` |
| $E$-1-form $\mu\in\Gamma(E^*)$ | `(mu,) = jacopy.forms("mu", degree=1, bundle=E.bundle)` | The form bundle is selected with `bundle=E.bundle`. | `mu` |
| Algebroid without axioms $A$ and its sections | `A = algebroid("A"); a1, a2, a3 = A.sections("u v w"); (muA,) = jacopy.forms("mu", degree=1, bundle=A.bundle)` | No axioms at all, only definitions. The defect formulas live here. | `A` |
| Lie algebroid with anchor morphism $K$ | `K = algebroid("K", declare=("lie", "anchor-morphism")); k1, k2, k3 = K.sections("u v w"); (muK,) = jacopy.forms("mu", degree=1, bundle=K.bundle)` | `lie` = right-leibniz + antisymmetric + jacobi. | `K` |
| Courant algebroid $C$ (with fibre metric) | `C = algebroid("C", declare=("courant",)); c1, c2, c3 = C.sections("u v w")` | `courant` = symmetric-part + metric-invariance + jacobi; fibre metric $g_C$. | `C` |
| Local, regular algebroid $R$ and locality projector $\mathcal P$ | `R = algebroid("R", declare=("local", "regular")); r1, r2 = R.sections("u v"); (muR,) = jacopy.forms("mu", degree=1, bundle=R.bundle); Pr = locality_projector(R)` | `locality_projector` can only be built on an algebroid declared `regular`. | `R`, `Pr` |
| Section maps $\Phi:E\to E$, $\psi:E\to TM$ | `Phi = section_map("Phi", A.bundle, A.bundle); psi = section_map("psi", A.bundle, jacopy.TM)` | $C^\infty$-linear bundle maps ($E\to E$ for the Derivator, $E\to TM$ for the Predator). | `Phi`, `psi` |
| Local pre-Leibniz algebroid $L_p$, antisymmetric algebroid $A_s$ | `Lp = algebroid("Lp", declare=("local", "anchor-morphism")); l1, l2 = Lp.sections("u v"); As = algebroid("As", declare=("antisymmetric",)); s1, s2, s3 = As.sections("u v w"); (muS,) = jacopy.forms("mu", degree=1, bundle=As.bundle)` | Used to supply the hypotheses of some ready-made theorems. | `Lp`, `As` |
| Tangent algebroid $(TM,\mathrm{id},[\cdot,\cdot])$ | `TMa = tangent_algebroid()` | The case $E=TM$: the anchor is the identity and the bracket is the Lie bracket. It has no declarations; everything is a theorem. | `TMa` |

**Scalar or function?** {py:func}`jacopy.functions` defines smooth functions
$f\in C^\infty(M)$. A derivation either kills them or expands them by the Leibniz rule,
$X(fh)=X(f)h+fX(h)$. A real constant is a `jacopy.Symbol` declared with
`reg.declare(lam, Scalar())`; after this declaration every derivation kills it
($X(\lambda)=0$, $d\lambda=0$) and it commutes freely in products. Numbers such as `2` or
`jacopy.Rational(1, 2)` are already constants.

**Symbolic dimension.** The dimension of `jacopy.TM` is a symbolic $n$, and every object
created without an explicit bundle is built on it, so proofs run in this abstract setting.
When a concrete dimension is needed (for example $n=3$ in the Hodge star), create
`M3 = jacopy.tangent_bundle(dim=3)` and pass `bundle=M3` to the object.

## Property declarations

Declarations are written `reg.declare(object, Property())`. The central engines and the
simplifier read `Scalar`, `Graded`, `AntiCommuting` and `GradedCommutative`. The other
properties are recorded in the registry and can be queried, but no engine currently acts on
them: declaring `Closed`, for example, does not make the tangent engine reduce $d\omega$ to
zero. Package axioms such as $[\pi,\pi]_{SN}=0$ are declared on the package structures
instead (see [Poisson](poisson.md)). Declaring the same property twice on the same object
raises `ValueError`.

| Mathematics | In code | Meaning | Read by the engines |
|---|---|---|---|
| Is $\lambda$ constant? | `reg.has(lam, Scalar)` | query for the constant declared above (returns `True`) | yes: $D(\lambda)=0$, free commutation |
| $\lvert\varphi\rvert=1$ | `reg.declare(jacopy.Symbol("phi"), Graded(1))` | degree declaration (`functions` already records degree 0) | yes: Koszul signs |
| $d\omega=0$ | `reg.declare(omega, Closed())` | closed form | recorded only |
| $\omega$ non-degenerate | `reg.declare(omega, NonDegenerate())` | $X\mapsto\iota_X\omega$ is injective | recorded only |
| $[\pi,\pi]_{SN}=0$ | `reg.declare(pi, Poisson())` | Poisson bivector | recorded only |
| $B(a,b)=B(b,a)$ | `reg.declare(P, Symmetric())` | symmetry | recorded only |
| $B(a,b)=-B(b,a)$ | `reg.declare(Q, Antisymmetric())` | antisymmetry | recorded only |
| $B(a,b)=-(-1)^{\lvert a\rvert\lvert b\rvert}B(b,a)$ | `reg.declare(T, GradedAntisymmetric())` | graded antisymmetry | recorded only |
| $ab=-ba$ | `reg.declare(jacopy.Symbol("theta"), AntiCommuting())` | ungraded anticommutation | yes: product sorting in the simplifier |
| $ab=(-1)^{\lvert a\rvert\lvert b\rvert}ba$ | `reg.declare(jacopy.Symbol("xi"), GradedCommutative())` | graded commutativity | yes: product sorting in the simplifier |
| Is $\omega$ closed? | `reg.has(omega, Closed)` | declaration query (returns `True` after the declaration above) | |
| The declaration itself | `reg.get(omega, Closed)` | the property object, with provenance `AXIOM` | |

The same queries in a script:

```python
print(reg.has(lam, Scalar), reg.has(omega, Closed))
print(reg.get(omega, Closed))
```

```text
True True
Closed(provenance=<Provenance.AXIOM: 'axiom'>, proof=None)
```

### Bulk and temporary declarations

A registry can also declare a property for a whole class or for every object matching a
predicate, roll declarations back at the end of a `with` block, or hide all properties
except a chosen set:

```python
reg2 = jacopy.PropertyRegistry()
reg2.declare_for_class(jacopy.Symbol, Scalar())               # every Symbol is a constant
reg2.declare_for_predicate(lambda x: getattr(x, "name", "") == "q", Graded(1))
c0 = jacopy.Symbol("c0")
print(reg2.has(c0, Scalar))                                    # inherited from the class
with reg2.scope():                                             # rolled back at the end
    reg2.declare(c0, Closed())
    print(reg2.has(c0, Closed))
print(reg2.has(c0, Closed))
with reg2.axioms([Graded]):                                    # only Graded is visible
    print(reg2.get(c0, Scalar))
```

```text
True
True
False
None
```
