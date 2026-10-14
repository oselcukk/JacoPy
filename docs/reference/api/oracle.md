# Model oracle

The model oracle `jacopy.oracle` evaluates both sides of a closed equation in random concrete coordinate models (SymPy polynomials) and compares them. Agreement means the equation was not refuted in the models tried; it is not a proof. The oracle requires the optional `sympy` dependency.

## Entry points

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.oracle.check_equal
   jacopy.oracle.check_chain
   jacopy.oracle.OracleReport
   jacopy.oracle.ChainReport
```

## Engine hook

Called by the proof engine when an equation closes; controlled by the environment variable `JACOPY_ORACLE` (`off`, `warn` or `strict`; default `off`).

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.oracle.hook.on_closed
```
