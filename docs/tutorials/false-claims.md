# When a claim is false

JacoPy never reports a false identity as proved. This tutorial shows what happens
instead: the prover returns the *residual*, the part of $\text{lhs} - \text{rhs}$
that its rules could not remove, and the independent *model oracle* evaluates both
sides in a random concrete coordinate model and finds two different values.

```{note}
The model oracle needs SymPy. Install it with the `oracle` extra:
`pip install -e ".[oracle]"`. The first half of this page (the residual) needs no
extra dependency.
```

## A claim with a missing term

Cartan's formula on a 1-form reads
$(\mathcal{L}_X\omega)(Y) = (\iota_X d\omega)(Y) + (d\,\iota_X\omega)(Y)$
(see [Cartan calculus on TM](cartan-calculus.md)). Suppose we forget the second
term and claim

$$(\mathcal{L}_X\omega)(Y) \overset{?}{=} (\iota_X d\omega)(Y).$$

```python
import jacopy
from jacopy.central.tangent import tangent_engine
from jacopy.proof.result import prove

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)
P = jacopy.pairing

lhs = P(L_X(omega), Y)
claim = P(i_X(d(omega)), Y)

try:
    jacopy.show_equal(lhs, claim, registry=reg, engine=tangent_engine(registry=reg))
except jacopy.ProofFailure as failure:
    print("not proved; residual:", failure.residual)
```

```text
not proved; residual: Y(⟨omega, X⟩)
```

`show_equal` raises `ProofFailure` and attaches the residual
$Y(\omega(X))$. The `ProofResult` driver reports the same thing as a status:

```python
result = prove(tangent_engine(registry=reg), lhs, claim, registry=reg)
print(result.status)
print(result.residual)
```

```text
RESIDUAL
Y(⟨omega, X⟩)
```

## Reading the residual

A residual is *not* a disproof. It says: after applying every rule in the engine,
$\text{lhs} - \text{rhs}$ reduces to this expression, and the engine cannot reduce
it to zero. Sometimes a rule is missing; sometimes the claim is false. Here the
residual is recognizable: $Y(\omega(X)) = Y(\iota_X\omega) = (d\,\iota_X\omega)(Y)$
is exactly the term we left out. JacoPy confirms this:

```python
missing = P(d(i_X(omega)), Y)
print(prove(tangent_engine(registry=reg), result.residual, missing, registry=reg).status)
```

```text
CLOSED
```

The same happens with a sign error, where the residual is twice the missing term:

```python
sign_error = P(i_X(d(omega)), Y) - P(d(i_X(omega)), Y)
print(prove(tangent_engine(registry=reg), lhs, sign_error, registry=reg).residual)
```

```text
(2 * Y(⟨omega, X⟩))
```

## The model oracle

The prover only shows that a claim *does not follow* from its rules. To show that a
claim is actually *false*, JacoPy has an independent check: `jacopy.oracle.check_equal`
builds concrete models on $\mathbb{R}^n$ (here $n = 3$) in which $X$, $Y$ and
$\omega$ are given random polynomial coefficients, computes both sides with the
coordinate formulas for $d$, $\iota_X$, $\mathcal{L}_X$ and $[\cdot,\cdot]$, and
compares the resulting polynomials.

```python
from jacopy.oracle import check_equal

report = check_equal(lhs, claim, registry=reg)
print(report.verdict)
print(report.summary())
```

```text
DISAGREE
oracle: DISAGREE (sides differ in R^3 seed=909666996476491335 [value])
```

`DISAGREE` means that in one concrete model the two sides are different
polynomials, which refutes the claim. The witness carries both values; we
evaluate them at the point $x = (1, 2, -1)$ with SymPy:

```python
import sympy

witness = report.witnesses[0]
lhs_value = sympy.sympify(witness.lhs_value)
rhs_value = sympy.sympify(witness.rhs_value)

x0, x1, x2 = sympy.symbols("x0 x1 x2")
point = {x0: 1, x1: 2, x2: -1}
print("model:", witness.model)
print("lhs at (1, 2, -1):", lhs_value.subs(point))
print("rhs at (1, 2, -1):", rhs_value.subs(point))
```

```text
model: R^3 seed=909666996476491335
lhs at (1, 2, -1): 1972
rhs at (1, 2, -1): 946
```

Two different numbers: the claim is false in this model, hence false in general.
The models are generated from a fixed seed, so the run is reproducible.

For the correct formula the oracle finds no difference:

```python
correct = P(i_X(d(omega)), Y) + P(d(i_X(omega)), Y)
print(check_equal(lhs, correct, registry=reg).summary())
```

```text
oracle: AGREE (2 model(s), seed 0)
```

`AGREE` means "not refuted in these models". It is evidence, never a proof; the
proof is the chain of [Cartan calculus on TM](cartan-calculus.md).

## Turning the oracle on for every proof

The drivers accept an `oracle` argument (`"warn"` or `"strict"`), and the
environment variable `JACOPY_ORACLE` sets it globally. With the oracle on, every
closed identity is also checked numerically: if the oracle refutes a closure,
`"warn"` emits an `OracleWarning` and `"strict"` raises `OracleDisagreement`. This
guards against a faulty rewrite rule, including one you wrote yourself.

```python
result = prove(tangent_engine(registry=reg), lhs, correct, registry=reg, oracle="strict")
print(result.status)
```

```text
CLOSED
```

## What you learned

* A false claim gives `ProofFailure` (from `show_equal`) or status `RESIDUAL`
  (from `prove`), together with the residual expression.
* A residual means "not proved with these rules"; it often names the missing term.
* `jacopy.oracle.check_equal` refutes false claims in concrete models (`DISAGREE`)
  and reports `AGREE` (not refuted) for true ones.

Next: [Algebroids and declared axioms](algebroids.md).
