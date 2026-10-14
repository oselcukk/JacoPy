# Algebraic operations

This page covers the pointwise algebra: sums and coefficients, wedge and tensor products,
pairings and evaluations, musical isomorphisms, symmetrization and the Hodge star, frame
indices, bundle endomorphisms, operator algebra, degree queries and simplification.

Every expression on this page is inert: writing it builds a node and nothing is expanded.
Expansion is done by an engine (see [Running proofs](running-proofs.md)); the one exception
is `simplify`, which can be called directly. The "LaTeX" column shows the output of
{py:func}`jacopy.to_latex` for the expression in the "In code" column.

## Setup

The objects are those of [Defining objects](objects.md); the second group of imports is
specific to this page.

```python
import jacopy
from jacopy.core import Degree, Scalar
from jacopy.central.objects.frame import FrameIndex

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
ea, eb = e.fields("a b")
s = FrameIndex("s")
D = jacopy.Derivation("D", degree=1)

from jacopy.central.objects import (tensor_product, symmetrize, antisymmetrize, hodge_star,
    partial_eval, musical_view, flat, sharp, scale, contract_all, form_on_vector,
    vector_on_form, apply_to_function, kronecker_delta, kind_of, signature_of)
from jacopy.core.indexed_sum import indexed_sum
from jacopy.central.objects.endomorphism import EndoVF, EndoForm
from jacopy.algebra.commutator import commutator, expand_commutator
from jacopy.algebra.derivation import compose, degree_of
from jacopy.algebra.grading import exterior_degree, exterior_parity
from jacopy.algorithms.simplify import simplify
from jacopy.central.tangent import d
```

## Sum, difference, coefficient

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $X+Y$ | `X + Y` | X, Y: vector fields | vector field | `X + Y` | The same for every type: forms, functions, ... |
| $X-Y$ | `X - Y` | X, Y: vector fields | vector field | `X - Y` | Stored internally as $X+(-Y)$ |
| $-\omega$ | `-omega` | omega: 2-form | 2-form | `-\omega` | |
| $fX$ | `f*X` | f: function; X: vector field | vector field | `f \, X` | $C^\infty(M)$-module multiplication; the left factor stays on the left |
| $\lambda X$ | `lam*X` | lam: constant; X: vector field | vector field | `\lambda \, X` | |
| $2X+\tfrac12X$ | `2*X + half*X` | numbers; X | vector field | `2 \, X + \frac{1}{2} \, X` | A Python number also works |
| $f\omega$ | `f*omega` | f: function; omega: $p$-form | $p$-form | `f \, \omega` | |
| $fh$ | `f*h` | f, h: functions | function | `f \, h` | |
| $f^2$ | `f**2` | f: function; integer exponent | function | `{f}^{2}` | Same as `jacopy.Power(f, 2)`; not evaluated |
| $fT$ | `scale(f, T)` | f: function; T: tensor | tensor of the same type | `f \, T` | Same as `f*T`; the type $(q,r)$ is preserved |

## Products

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\alpha\wedge\beta$ | `jacopy.wedge(alpha, beta)` | forms of any degree | $(p+q)$-form | `\alpha \wedge \beta` | Several arguments are allowed: `jacopy.wedge(alpha, beta, omega)` |
| $\alpha\wedge\eta$ | `jacopy.wedge(alpha, eta)` | alpha: 1-form; eta: form of symbolic degree $p$ | $(1+p)$-form | `\alpha \wedge \eta` | |
| $X\wedge Y$ | `jacopy.wedge(X, Y)` | X, Y: vector fields | 2-vector | `X \wedge Y` | Produces a multivector |
| $\alpha\wedge 0$ | `jacopy.wedge(alpha, jacopy.Zero)` | | 0 | `0` | 0 absorbs and 1 is the unit |
| $T\otimes\alpha$ | `tensor_product(T, alpha)` | tensors, forms or vectors (any number) | tensor | `T \otimes \alpha` | Non-commutative; the types add up |

See {py:func}`jacopy.wedge`.

## Pairing and evaluation

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\langle\alpha,X\rangle=\alpha(X)$ | `jacopy.pairing(alpha, X)` | alpha: 1-form; X: vector field | function | `\langle \alpha,\, X \rangle` | Form first, then vector |
| $\alpha(X)$ | `alpha(X)` | alpha: 1-form; X: vector field | function | `\langle \alpha,\, X \rangle` | The same node as `jacopy.pairing(alpha, X)` |
| $\alpha(X)$ (named form) | `form_on_vector(alpha, X)` | 1-form; vector field | function | `\langle \alpha,\, X \rangle` | |
| $X(\alpha)=\langle\alpha,X\rangle$ | `vector_on_form(X, alpha)` | vector field; 1-form | function | `\langle \alpha,\, X \rangle` | Reversed argument order |
| $\omega(X,Y)$ | `omega(X, Y)` | omega: 2-form; X, Y: vector fields | function | `\omega\!\left(X,\, Y\right)` | Requires exactly $p$ arguments; for partial evaluation use $\iota_X$ |
| $\omega(X,Y)$ (general form) | `jacopy.multi_eval(omega, X, Y)` | head: form, tensor, ...; slot values | function | `\omega\!\left(X,\, Y\right)` | The only way to evaluate heads that are not callable, such as $d\alpha$ or $\alpha\wedge\beta$ |
| $(\alpha\wedge\beta)(X,Y)$ | `jacopy.multi_eval(jacopy.wedge(alpha, beta), X, Y)` | wedge; vectors | function | `\left(\alpha \wedge \beta\right)\!\left(X,\, Y\right)` | Its expansion needs an optional engine rule (see [Running proofs](running-proofs.md)) |
| $(d\alpha)(X,Y)$ | `jacopy.multi_eval(d(alpha), X, Y)` | $d\alpha$: 2-form; X, Y | function | `\left(d\!\left(\alpha\right)\right)\!\left(X,\, Y\right)` | `d(alpha)(X, Y)` is not supported |
| $\omega(X,X)=0$ | `omega(X, X)` | the same argument twice | function ($=0$) | `\omega\!\left(X,\, X\right)` | A repeated argument gives zero after simplification |
| $P(\alpha,\beta)$ | `P(alpha, beta)` | P: 2-vector; alpha, beta: 1-forms | function | `P\!\left(\alpha,\, \beta\right)` | Alternating |
| $\pi(\alpha,\beta)$ | `pi(alpha, beta)` | pi: bivector; 1-forms | function | `\pi\!\left(\alpha,\, \beta\right)` | |
| $T(\alpha,X,Y)$ | `T(alpha, X, Y)` | T: $(1,2)$-tensor; one covector, then two vectors | function | `T\!\left(\alpha,\, X,\, Y\right)` | Not alternating |
| $g(X,Y)$ | `g(X, Y)` | g: metric; X, Y: vector fields | function | `g\!\left(X,\, Y\right)` | Symmetric |
| $g^{-1}(\alpha,\beta)$ | `ginv(alpha, beta)` | ginv: inverse metric; 1-forms | function | `g^{-1}\!\left(\alpha,\, \beta\right)` | |
| $X(f)$ | `X(f)` | X: vector field; f: function | function | `X\!\left(f\right)` | Directional derivative |
| $X(f)$ (named form) | `apply_to_function(X, f)` | vector field; function | function | `X\!\left(f\right)` | |

See {py:func}`jacopy.pairing` and {py:func}`jacopy.multi_eval`.

## Partial evaluation and musical isomorphisms

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $g(X,\cdot)$ | `partial_eval(g, X, None)` | head; a value or `None` (open) for each slot | partial map | `g\!\left(X,\, \cdot\right)` | |
| $g(X,\cdot)(Y)=g(X,Y)$ | `partial_eval(g, X, None)(Y)` | partial map; values of the open slots | function | `g\!\left(X,\, Y\right)` | Open slots are filled in order |
| $T(\alpha,\cdot,Y)$ | `partial_eval(T, alpha, None, Y)` | tensor; one entry per slot | partial map | `T\!\left(\alpha,\, \cdot,\, Y\right)` | |
| $T(\alpha,\cdot,\cdot)$ | `musical_view(T, alpha)` | head; values of the leading slots | partial map | `T\!\left(\alpha,\, \cdot,\, \cdot\right)` | Leading slots fixed, the rest open |
| degree of $\omega(X,\cdot)$ | `partial_eval(omega, X, None).degree` | partial map | degree | | `1`: the form degree of the open alternating map |
| $g^\flat(X)$ | `flat(g)(X)` | g: metric; X: vector field | 1-form | `g^{\flat}\!\left(X\right)` | `g.flat()(X)` also works |
| $\pi^\sharp(\alpha)$ | `sharp(pi)(alpha)` | pi: bivector or inverse metric; alpha: 1-form | vector field | `\pi^{\sharp}\!\left(\alpha\right)` | |
| $g^\sharp(\alpha)$ | `ginv.sharp()(alpha)` | inverse metric; 1-form | vector field | `g^{-1}^{\sharp}\!\left(\alpha\right)` | Known display limitation: the LaTeX contains a double superscript |

## Symmetrization and the Hodge star

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $\mathrm{Sym}(T)$ | `symmetrize(T)` | tensor or evaluation | same type | `\operatorname{Sym}\!\left(T\right)` | Expands under evaluation: $T_{(ab)}=\tfrac12(T_{ab}+T_{ba})$ |
| $\mathrm{Alt}(T(\alpha,X,Y))$ | `antisymmetrize(T(alpha, X, Y))` | evaluated tensor | function | `\operatorname{Alt}\!\left(T\!\left(\alpha,\, X,\, Y\right)\right)` | |
| $\star_g\omega$ | `jacopy.hodge(omega, g)` | omega: $p$-form; g: metric | $(n-p)$-form | `\star_{g} \omega` | Structural only: no rules such as $\star\star=\pm1$; $n$ is symbolic |
| $\star_g\omega$, $n=3$ | `jacopy.hodge(omega, g3)` | omega; metric in dimension 3 | 1-form | `\star_{g} \omega` | For concrete $p,n$, $0\le p\le n$ is checked |
| $\star\omega$ (no metric) | `hodge_star(omega, 4)` | omega; dimension (int or degree) | $(4-p)$-form | `\star \omega` | Bare structural star |

See {py:func}`jacopy.hodge`.

## Frames, indices, Kronecker delta

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $e_a$ | `e.field("a")` | index name (str or int) | vector field | `e_{a}` | |
| $e^a$ | `ce.field("a")` | index name | 1-form | `e^{a}` | |
| $\langle e^a,e_b\rangle$ | `e.pairing("a", "b")` | upper index, lower index | function | `\langle e^{a},\, e_{b} \rangle` | The engine reduces it to $\delta^a_b$ |
| $\delta^a_b$ | `kronecker_delta("a", "b")` | upper, lower index | constant | `\delta^{a}_{b}` | 1 for equal indices |
| $\sum_s\langle e^s,X\rangle e_s$ | `indexed_sum(s, e, ce.field("s")(X) * e.field("s"))` | dummy index; range (a frame); body | type of the body | `\sum_{s \in e} \langle e^{s},\, X \rangle \, e_{s}` | Equality is up to renaming of the dummy index |

## Bundle endomorphisms

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $m(X)$ | `EndoVF("m", X)` | name; vector field | vector field | `m\!\left(X\right)` | |
| $m^{-1}(X)$ | `EndoVF("m", X, inverted=True)` | name; vector field; `inverted` | vector field | `m^{-1}\!\left(X\right)` | The rule $m^{-1}(m(x))=x$ is optional (see [Automatic rules](automatic-rules.md)) |
| $\tilde m(\alpha)$ | `EndoForm("m", alpha)` | name; form | form of the same degree | `\tilde{m}\!\left(\alpha\right)` | |

## Operator algebra

| Mathematics | In code | Arguments | Result | LaTeX | Note |
|---|---|---|---|---|---|
| $D(f)$ | `D(f)` | D: derivation; f | expression | `D\!\left(f\right)` | Same as `jacopy.Act(D, f)` (inert application) |
| $D(fh)=D(f)h+fD(h)$ | `D(f*h)` | D: derivation of degree 1 | expression | `D\!\left(f \, h\right)` | The graded Leibniz rule is applied by the engine |
| $A\circ B$ | `compose(jacopy.lie_derivative(X), jacopy.interior(Y))` | operators | operator | `\mathcal{L}_{X} \, \iota_{Y}` | The composition is a product node |
| $[A,B]$ (graded commutator) | `commutator(jacopy.lie_derivative(X), jacopy.interior(Y))` | operators | operator | `\left[\mathcal{L}_{X},\, \iota_{Y}\right]` | Inert node |
| $[A,B]=AB-(-1)^{\lvert A\rvert\lvert B\rvert}BA$ | `expand_commutator(commutator(jacopy.lie_derivative(X), jacopy.interior(Y)), reg)` | commutator; registry | operator | `\mathcal{L}_{X} \, \iota_{Y} - \iota_{Y} \, \mathcal{L}_{X}` | The sign is computed from the degrees |

## Degree and type queries

| Mathematics | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\lvert d\rvert=1$ | `degree_of(jacopy.exterior_d(), reg)` | expression or operator; registry | degree | `1` |
| $\lvert\iota_X\rvert=-1$ | `degree_of(jacopy.interior(X), reg)` | | degree | `-1` |
| $\lvert\eta\rvert=p$ | `degree_of(eta, reg)` | | degree | `p` |
| $p+1$ | `p + 1` | degree plus an integer | degree | `1 + p`: degrees are integer polynomials |
| $2p \bmod 2$ | `(2*p).parity()` | degree | `0`, `1` or `None` | `0`; `None` if undetermined |
| $\lvert\alpha\wedge\omega\rvert$ | `exterior_degree(jacopy.wedge(alpha, omega), reg)` | expression; registry | degree or unknown | `3` |
| $\lvert\alpha\wedge\omega\rvert\bmod 2$ | `exterior_parity(jacopy.wedge(alpha, omega), reg)` | expression; registry | `0`, `1` or `None` | `1` |
| type judgment | `kind_of(jacopy.lie_bracket(X, Y), reg)` | expression; registry | `Kind` | `kind='vector', degree=1` |
| $(q,r)$ signature | `signature_of(scale(f, T))` | tensor expression | `(q, r)` | `(1, 2)` |

## Simplification

`simplify` collects terms, reorders the arguments of alternating maps and applies Koszul
signs. It can be called on any expression:

```python
print(simplify(omega(Y, X) + omega(X, Y) + 2*X(f) - X(f) - X(f), reg))
print(degree_of(jacopy.interior(X), reg), (2*p).parity(), signature_of(scale(f, T)))
```

```text
0
-1 0 (1, 2)
```
