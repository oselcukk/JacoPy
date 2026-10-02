# Changelog

All notable changes to jacopy are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The version
is defined once, in `jacopy/__init__.py` (`__version__`); no release
has been tagged yet, so everything below is unreleased on top of
`0.0.1`.

Finding labels such as `P0-1` or `M1X-5` refer to the full audit of
commit `0b00e1b` ("DENETİM 0B00E1B-FULL", 2026-09-30).

## [Unreleased]

### Documentation and test portability (audit T2-8)

- `README.md` rewritten in English: what jacopy is, installation with
  the extras, a quick start through the top-level surface, the
  packages mapped to the Math 595 guideline items (planned items
  marked), proof trust and the oracle, licence and citation.
- `docs/ARCHITECTURE.md` rewritten for the current tree: measured layer
  map with the 29 deferred upward imports listed (T2-2), the proof
  flow, the trust model (requirement kinds, minting, replay,
  default-reject citation, the Scalar contract), the model oracle,
  extension points (`Definition`, `StructureKind`) with runnable
  examples, the support levels and known limits.
- `docs/TESTING.md`: sympy is the `oracle` extra; `--oracle`,
  `--oracle-report`, the `oracle_exempt` and `contract_table` markers,
  the wheel run and the merge gate.
- `docs/CITATIONS.md`: file paths follow the renamed modules.
- The `jacopy` docstring names the `cite` / `prove` homonyms.
- The fast suite runs from a sympy-free wheel (CI job `wheel`): the
  module-level sympy import of `tests/test_audit_0b00e1b_metric_affine.py`
  moved into the four tests that use it (`pytest.importorskip`), and the
  tests that call the oracle or need a repository file skip with a
  reason.
- `CITATION.cff` keeps its `version`; `tests/test_citation_metadata.py`
  checks that it equals `jacopy.__version__`.
- The research-interface notebook uses `antisymmetrize_indices`.

### Unambiguous names (audit T2 names, T2-4; arch-core follow-up), 2026-10-02

- Module files that shared a basename were renamed; each old path is a
  compatibility alias that *is* the moved module:
  `metric_affine/koszul.py` → `metric_affine/metric_koszul.py`,
  `poisson/koszul.py` → `poisson/koszul_forms.py`,
  `central/tangent/engine.py` → `central/tangent/tangent_expansion.py`,
  `central/algebroid/engine.py` → `central/algebroid/algebroid_expansion.py`,
  `metric_affine/engine.py` → `metric_affine/metric_affine_expansion.py`.
- A name that two different objects carried across subpackage
  `__all__` lists has an unambiguous alias (same object) in the second
  package; the old name stays importable: `research.ZeroOperator`,
  `research.antisymmetrize_indices`, `algorithms.rewrite_to_fixpoint`,
  `core.PropertyProvenance`, `central.tangent.prove_lie_jacobi`,
  `central.algebroid.prove_algebroid_*`. The known collisions shrink
  from 11 to 2 (`Metric` / `metric`).
  The old names left their subpackage `__all__` lists, so a star
  import (`from jacopy.core import *`, `jacopy.research`,
  `jacopy.central.tangent`, …) no longer brings them; import them by
  name, or use the new aliases.
- Public names for private helpers used across packages and by the
  notebooks (same objects; the private names stay):
  `poisson.tilde.normalized_by`, `drinfeld.tilde_calculus.nambu_tilde_engine`,
  `central.objects.frame.frame_index_str`, `drinfeld.double.evaluate_on_slots`,
  `drinfeld.double.double_engine`, `poisson.showcase.is_exact_form`,
  `drinfeld.twist_engine`, `generalized.exceptional_rotation_engine`,
  `algorithms.normalize_alternating.structural_sort_key`,
  `proof.search.node_count`. Private from-imports inside the library:
  150 → 80 (across subpackages 74 → 28); the notebooks import no
  private name.
- `jacopy.research.structure_kinds`: the built-in families, family
  rules and kinds load before any user entry, whenever the user
  registers (a kind registered before first use no longer displaces
  Nambu–Poisson; `first=True` still puts a kind in front on purpose);
  `families()`, `family_rules()` and `additive_slot_tags()` load the
  built-ins; `register_family_rule` is idempotent for the same
  condition, builder, reason and order.

### Architecture (audit T2-1, T2-3), merged 2026-10-02

- Nine structure-free rule classes moved, byte-identical, into the
  central layer: `central.tangent.cartan_rules`
  (`MagicFormulaDefinition`, `LieIotaCommutatorDefinition`,
  `DSquaredZeroDefinition`, `DWedgeLeibnizDefinition`) and
  `central.calculus.slot_rules` (`PairingArgSplitDefinition`,
  `FormProductToWedgeDefinition`, `WedgeSumScalarDefinition`,
  `WedgeZeroNegDefinition`, `TrivialZeroSumDefinition`). The old
  modules (`drinfeld.twist`, `drinfeld.tilde_calculus`,
  `poisson.nambu`) re-export the same class objects; no engine changes
  which rules it registers or in which order.
- `assemble_engine` and `Scan` no longer name Nambu–Poisson. They read
  a registry in `jacopy.research.structure_kinds`: node families
  (`register_family`), family rules (`register_family_rule`, explicit
  order) and structure kinds (`StructureKind`,
  `register_structure_kind`). The Nambu–Poisson kind lives in
  `jacopy.research.nambu_kind`. A structure without a registered kind
  raises a `TypeError` that names `register_structure_kind`.

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
