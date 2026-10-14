# The oracle: a numerical falsifier

The oracle evaluates both sides of an identity in random concrete coordinate models
(polynomial data on $\mathbb R^n$) and compares the values. A verdict of `AGREE` means
"not refuted"; it is **not a proof**. `DISAGREE` means that a counterexample was found.
The oracle uses [SymPy](https://www.sympy.org) and needs the optional `oracle` extra (see
[Installation](../installation.md)).

## Three ways to use it

- **Directly:** `check_equal(lhs, rhs, registry=reg)` for one identity, or
  `check_chain(chain, registry=reg)` for every step of a proof chain.
- **During a proof:** `jacopy.show_equal(..., oracle="warn")` or `oracle="strict"`;
  `jacopy.proof.result.prove(..., oracle=...)` takes the same option. The environment
  variable `JACOPY_ORACLE=off|warn|strict` sets the default (the library default is `off`).
- **In the test suite:** `pytest --oracle=warn` or `--oracle=strict` (see the
  [testing guide](../development/testing.md)).

## Example

```python
import jacopy
import jacopy.central.tangent as tg
from jacopy.central.tangent import tangent_engine
from jacopy.oracle import check_equal, check_chain

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y = jacopy.vector_fields("X Y")
eng = tangent_engine(registry=reg)

rep = check_equal(jacopy.lie_derivative(X)(f), X(f), registry=reg)
print(rep.verdict)                                   # not refuted (not a proof)
bad = check_equal(jacopy.lie_bracket(X, Y)(f), X(Y(f)), registry=reg)
print(bad.verdict, "|", bad.detail, "|", type(bad.witnesses[0]).__name__)
crep = check_chain(tg.prove_cartan_magic_on_functions(X, f, registry=reg), registry=reg)
print([s.verdict for s in crep.steps])
ch = jacopy.show_equal(jacopy.lie_derivative(X)(f), X(f), registry=reg, engine=eng, oracle="warn")
print(len(ch.steps))
```

```text
AGREE
DISAGREE | sides differ in R^3 seed=17924856210895507548 [value] | Witness
['AGREE', 'AGREE', 'AGREE', 'AGREE', 'AGREE', 'AGREE']
2
```

The second check is deliberately false ($[X,Y]f\ne X(Yf)$): the oracle finds a model in
which the two sides differ and returns a witness.

## Limits

- The oracle has concrete models for the tangent calculus, the Poisson and Nambu brackets
  and for algebroids built from the declared axioms. When an identity depends on an axiom of
  a user-defined structure that has no model, the verdict is `UNSUPPORTED` rather than
  `AGREE` (see [Your own structure](your-own-structure.md)).
- Symbolic degrees are sampled at a few concrete values.
- `AGREE` never upgrades a residual to a proof; only an engine chain is a proof.

The formulas the oracle models use are listed in
[Rules the engine applies automatically](automatic-rules.md).
