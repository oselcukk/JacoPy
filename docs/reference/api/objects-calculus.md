# Objects and calculus

The expression tree, the property registry, the object factories and the tangent-bundle operators of Cartan calculus. Every name on this page is importable directly from `jacopy`.

## Expressions

The core expression classes and the property registry. `Expr` and `Atom` are the extension protocol for new expression nodes.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.Expr
   jacopy.Atom
   jacopy.Symbol
   jacopy.Integer
   jacopy.Rational
   jacopy.Sum
   jacopy.Product
   jacopy.Power
   jacopy.Neg
   jacopy.Zero
   jacopy.One
   jacopy.NegOne
   jacopy.Wedge
   jacopy.MultiEval
   jacopy.PropertyRegistry
   jacopy.default_registry
```

## Operator application

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.Act
   jacopy.Derivation
```

## Object factories

Factories for functions, vector fields, forms, tensors, metrics, connections and frames on the tangent bundle.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.Bundle
   jacopy.TM
   jacopy.tangent_bundle
   jacopy.functions
   jacopy.vector_fields
   jacopy.forms
   jacopy.p_vectors
   jacopy.bivector
   jacopy.tensors
   jacopy.metric
   jacopy.Metric
   jacopy.hodge
   jacopy.connection
   jacopy.covariant_derivative
   jacopy.frame
   jacopy.coframe
   jacopy.pairing
   jacopy.Pairing
   jacopy.wedge
   jacopy.multi_eval
   jacopy.interior
```

## Cartan calculus operators

The Lie derivative and the exterior derivative. The interior product is `interior` above.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.lie_derivative
   jacopy.exterior_d
```
