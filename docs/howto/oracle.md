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

## Settings

| Setting | Where | Default | Meaning |
|---|---|---|---|
| `oracle=` | `jacopy.show_equal`, `jacopy.proof.result.prove` | `None` (use the current mode) | `"off"`, `"warn"` or `"strict"` for this call only |
| `oracle_mode(mode)` | context manager in `jacopy.oracle.hook` | | sets the mode for a block of code; `None` keeps the current mode |
| `JACOPY_ORACLE` | environment variable | `off` | the default mode; `0`, `false`, `no`, `none` and the empty string also mean off; an unknown value warns once and means off |
| `JACOPY_ORACLE_SAMPLES` | environment variable | `2` | models per closed equation during a proof; a value that is not a positive integer warns once and leaves the oracle off |
| `JACOPY_ORACLE_SEED` | environment variable | `0` | base seed of the models during a proof; an invalid value is replaced by `0` |
| `samples=`, `seed=` | `check_equal` | `2`, `0` | models per check and base seed; `samples` must be a positive integer |
| `timeout=` | `check_equal` | `20.0` | seconds allowed for one check |
| `--oracle`, `--oracle-samples`, `--oracle-seed`, `--oracle-report` | pytest options of the JacoPy test suite | `off` (or `JACOPY_ORACLE`), `2`, `0`, `.oracle/report.json` | see the [testing guide](../development/testing.md) |

The precedence is: the `oracle=` keyword, then an enclosing `oracle_mode`, then
`JACOPY_ORACLE`. `jacopy.prove` and the strategy classes have no `oracle=` keyword; wrap the
call in `oracle_mode` instead. In `warn` mode a refutation emits `OracleWarning`; in `strict`
mode it raises `OracleDisagreement`.

```python
from jacopy.oracle.hook import oracle_mode, current_mode

rep = check_equal(jacopy.lie_derivative(X)(f*h), X(f)*h + f*X(h), registry=reg,
                  samples=3, seed=5)
print(rep.verdict, rep.samples, rep.seed)
print(current_mode())
with oracle_mode("warn"):
    print(current_mode())
    jacopy.prove(jacopy.lie_derivative(X)(f), X(f), registry=reg, engine=eng)
print(current_mode())
```

```text
AGREE 3 5
off
warn
off
```

## Limits

- The oracle has concrete models for the tangent calculus, the Poisson and Nambu brackets
  and for algebroids built from the declared axioms. When an identity depends on an axiom of
  a user-defined structure that has no model, the verdict is `UNSUPPORTED` rather than
  `AGREE` (see [Your own structure](your-own-structure.md)).
- Symbolic degrees are sampled at a few concrete values.
- `AGREE` never upgrades a residual to a proof; only an engine chain is a proof.

The formulas the oracle models use are listed in
[Rules the engine applies automatically](automatic-rules.md).
