# Changelog

All notable changes to jacopy are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The version
is defined once, in `jacopy/__init__.py` (`__version__`); no release
has been tagged yet, so everything below is unreleased on top of
`0.0.1`.

Finding labels such as `P0-1` or `M1X-5` refer to the full audit of
commit `0b00e1b` ("DENETİM 0B00E1B-FULL", 2026-09-30).

## [Unreleased]

### Public surface and packaging (audit T2-5, T2-6, T2-7, T2-9)

- Top-level `jacopy` now exposes a stable, documented surface
  (`jacopy.__all__`, 66 names): the expression classes, the object
  factories, the tangent operators, the proof entry points (`show_equal`,
  `prove`, `ProofChain`, `ProofResult`, `Theorem`, …) and the display
  helpers. Names beyond the expression classes load lazily, so
  `import jacopy.core` costs what it did before. The module docstring
  states four support levels and the canonical binding of shared names.
- Package facades aligned: `jacopy.packages.drinfeld` now covers all of
  its modules (twists, Roytenberg bracket, examples, tilde calculus,
  metric invariance, bracket morphisms); `poisson`, `generalized` and
  `metric_affine` gained their missing user-path entry points. Old deep
  import paths keep working.
- Removed the empty placeholder packages `jacopy.packages.algebroid_calculus`
  (item 13 lives in `jacopy.packages.drinfeld`) and
  `jacopy.packages.research` (item 15 lives in `jacopy.research`).
- Packaging: single version source; extras match real use (`oracle` =
  sympy replaces the unused `components`; the unused `parallel`/joblib
  extra and the unused nbformat/nbclient pins are gone); `py.typed`
  marker; `[project.urls]`; `requirements.txt` reduced to `-e .[dev]`;
  this changelog and `CITATION.cff`.

### Fixed — audit fixes merged 2026-09-30 … 2026-10-02

- **Metric-affine** (P0-6 / M7-1, M7-2): `CoframeRecombinationDefinition`
  no longer fires at non-linear positions (it closed a false equality);
  `ComponentInput.set_anholonomy` no longer swallows data given in a
  non-canonical index order.
- **Core product rule** (P0-1 / K1-2, M1X-1; P0-2 / M1-3; K1-1 / M1X-5):
  the wedge Leibniz rule takes factor degrees, not the operator degree
  (sign on multivector factors); a degree-0 non-derivation operator is
  no longer treated as a multiplier; `collect_pairings` keeps
  non-scalar coefficients out of the pairing slot.
- **Algebroid `d_E`** (P0-4 / M2-1, P0-5 / M2-2, M2-3, M7-1 root): no
  unconditional alternation of `d_E` on a non-antisymmetric bracket;
  `LieDerivative` needs a declared right Leibniz rule before using the
  product rule on sections; indexed-sum ordering.
- **Integration** (P0-5 / M2-2 end to end): non-derivation section
  values, the metric-affine registry, `ConnectionForm` alternation,
  `EndoForm` kind.
- **Proof trust** (P0-3 / M1X-2, K2-16; M1-5 group / M1-6, K2-7,
  M1X-4; M1X-3 / K2-13, M1-8): a theorem record carries the registry
  declarations it relied on as requirements, so citing it in another
  context cannot close a false identity; follow-ups add registry read
  propagation, `end_reads` by identity, the exact `Theorem` type in
  classification, a single minting gate, structure records and a cheap
  `__copy__`.
- **Rule matching** (M1X-6 / K1-12, M1-4): payload-aware matching,
  cited theorem rules, LieZ Lemma 9.1, declaration gates and a narrow
  Σ-binder contract.
- **Citations** (M8, M4-1, M4-2, T3-2 / K1-9): APA 7 rule sources
  (bibliography plus `Definition`/`Theorem` sources on proof steps),
  LaTeX rendering fixes, `docs/CITATIONS.md`.
- **Poisson** (M3-1 / M3-2, M3-3): calculus-scoped TM rules (reserved
  Cartan-TM, `belongs_to`) and the Koszul–Jacobi certificate with
  replayed seeds.
- **Roadmap items** (M7-4, M4-3): ADM Prop. 3.9 E-Cartan structure
  equations with `Q_ab` one-forms; Nambu double Jacobi via the twist
  (p = 1 form part); `FISharpPairingSwap` calculus scope.
- **Core contracts** (K1-3 / K1-4, M1X-7; M1-1 / M1-2): Schouten and
  derived-bracket degree hooks; the "Scalar = R-constant" contract end
  to end (one predicate, specificity shadowing, raw-clash checks on
  every path, `f·D` on one plain symbol, an independent oracle
  restatement). The AoG-domain cases are deferred to their own lane and
  kept as strict-xfail known bugs.

### Added — model oracle

- Model oracle F0 + F1 (audit K4-2 direction): a coordinate falsifier
  for engine closures, off by default (`jacopy.oracle`).
- Oracle F2: algebroid model families with self-checked axiom
  separation, E-form realizers, counter-model selection and leak checks.
- `oracle_exempt` test marker (reasoned, reported as `EXEMPT`) and a
  strict-oracle CI job that uploads its JSON report.
