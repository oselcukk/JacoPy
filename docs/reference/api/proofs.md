# Proofs

Proof entry points, proof chains, results, theorems and the rewrite engine. Every name on this page is importable directly from `jacopy`.

## Proving an identity

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.show_equal
   jacopy.prove
   jacopy.normalize
   jacopy.NormalForm
```

## Proof chains and results

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.ProofChain
   jacopy.ProofStep
   jacopy.ProofFailure
   jacopy.ProofResult
   jacopy.Goal
   jacopy.Assumption
```

## Proof strategies

Strategies decide the order in which sound rules fire; see [Choosing a proof strategy](../../howto/proof-strategies.md). These names are imported from their modules.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.proof.strategies.Strategy
   jacopy.proof.strategies.ExpandAndSimplify
   jacopy.proof.search.SearchStrategy
   jacopy.proof.strategies.PortfolioStrategy
   jacopy.proof.strategies.UnrollToFoundations
   jacopy.proof.strategies.AgreementOnGenerators
   jacopy.proof.strategies.DerivedBracketStrategy
```

## Theorems

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.Theorem
   jacopy.TheoremBook
   jacopy.cite
```

## Rules and engines

`Definition` is the extension protocol for new rewrite rules.

```{eval-rst}
.. autosummary::
   :toctree: generated

   jacopy.Definition
   jacopy.ExpansionEngine
```
