# Brackets and algebroids

Graded brackets on the tangent bundle, the generic bracket machinery, and the algebroid layer on which brackets with declared axioms are defined.

## Tangent-bundle brackets

The Lie bracket of vector fields and the Schouten–Nijenhuis bracket of multivector fields (importable from `jacopy`).

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.lie_bracket
   jacopy.sn_bracket
```

## Graded and derived brackets

The bracket base classes in `jacopy.brackets`.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.brackets.GradedBracket
   jacopy.brackets.BracketApply
   jacopy.brackets.expand_bracket
   jacopy.brackets.DerivedBracket
   jacopy.brackets.VanishingCondition
   jacopy.brackets.derived_bracket
```

## Algebroids

Algebroid objects, the algebroid engine and the Jacobiator, Derivator and Predator in `jacopy.central.algebroid`. The module exports further declarations and `prove_*` functions; see its source.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.central.algebroid.Algebroid
   jacopy.central.algebroid.algebroid
   jacopy.central.algebroid.tangent_algebroid
   jacopy.central.algebroid.AlgebroidBracket
   jacopy.central.algebroid.AnchoredVF
   jacopy.central.algebroid.algebroid_engine
   jacopy.central.algebroid.algebroid_calculus
   jacopy.central.algebroid.d_E
   jacopy.central.algebroid.lie_E
   jacopy.central.algebroid.Jacobiator
   jacopy.central.algebroid.jacobiator
   jacopy.central.algebroid.Derivator
   jacopy.central.algebroid.derivator
   jacopy.central.algebroid.Predator
   jacopy.central.algebroid.predator
```
