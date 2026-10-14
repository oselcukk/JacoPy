# Architecture

This page describes how the JacoPy code is organized: the layers and the
rule that governs their imports, what each layer contains, what happens
when an identity is proved, and where a user can extend the library.
It describes what the code does today; anything that is not implemented
yet is marked *planned*. The trust model (assumption tracking, citation
checks, the model oracle) has its own page: [Trust model](trust-model.md).

```{note}
**Measured on commit `9a11e9b` (14 October 2026).** 186 Python modules
and 70,799 lines under `jacopy/` (a scan of every file with Python's own
`ast` module); 122 test files under `tests/`; the fast test suite
(`pytest tests -q`) gives 2,572 passed, 12 skipped (slow tests) and 5
expected failures that document a known open issue. These numbers change
with every merge. The layer boundaries and the trust model are the parts
of this page that are meant to stay true. The four diagrams on this page
were generated from the code at the same commit, not drawn by hand.
```

## Layers

The code is divided into tiers, like the chapters of a textbook: the
lower tiers contain definitions, the upper tiers the results that use
them. The rule is **"arrows point down"**: a module may import from its
own tier and from the tiers below it, just as a lemma may rest only on
lemmas proved earlier.

| Tier | Layer (folder) | Modules | Lines | Role |
|--:|---|--:|--:|---|
| 7 | `jacopy/__init__.py` | 1 | 255 | The public face: 66 stable names |
| 6 | `display/` | 5 | 2,423 | Renders terms and proofs as text, LaTeX and Jupyter output; changes nothing |
| 5 | `research/` | 9 | 2,436 | Builds the engine a user question needs; axiom-suite checks |
| 4 | `packages/` (4 packages and a facade) | 60 | 31,099 | Concrete geometries: Poisson/Nambu, Drinfel'd doubles and twists, Courant, metric-affine |
| 3 | `central/` | 48 | 14,454 | Objects and calculus shared by $TM$ and an algebroid $E$ ($d$, $\mathcal{L}$, $\iota$, brackets) |
| 2 | `proof/` | 16 | 6,248 | Proof engine: rules, strategies, derivations, results, theorems, citation |
| 1 | `algebra/`, `algorithms/`, `brackets/`, `bibliography.py` | 21 | 5,005 | Graded algebra, simplification passes (Leibniz rule, Koszul signs), abstract brackets, bibliography |
| 0 | `core/` | 15 | 3,996 | Expression tree, properties, registry, pattern matching |
| side | `oracle/` (with `models/`) | 11 | 4,883 | Tests closed identities numerically on concrete coordinate models |
| | **Total** | **186** | **70,799** | |

```{figure} ../_static/diagrams/layers.svg
:alt: Layer-level dependency graph of JacoPy
:width: 100%

Layer map. Gray arrows point down (solid: imported when the file is
loaded; dashed: only when a function runs). Blue arcs connect layers in
the same tier, red dashed arrows are the deferred upward exceptions,
green arrows go to the oracle. The number on an arrow is the number of
links.
```

In compact form:

```text
                         display            (reads everything, changes nothing)
                            │
                         research           (assemble an engine for a user question)
                            │
   packages:  poisson ── drinfeld ── generalized        metric_affine
                            │
   central:   objects ── calculus ── tangent ── algebroid
                            │
                          proof             (engine, strategies, results, theorems)
                            │
   foundation: algebra · algorithms · brackets · bibliography
                            │
                           core             (expression tree, properties, registry)

   oracle  — a separate falsifier; the proof layer imports only its
             engine-free hook (jacopy/oracle/hook.py)
```

### Measured import structure

A module uses another module through an `import` statement. Inside
`jacopy/` there are 2,418 import statements that target `jacopy`
modules: 1,344 run when the file is loaded, 1,068 only when the
enclosing function is called (*deferred*), and 6 only for type
checking. Together they give 1,841 distinct module-to-module links.

* **No module-level import points up.** Importing `jacopy.proof` loads
  `core`, `algebra`, `algorithms`, `brackets`, `proof` and
  `jacopy.oracle.hook`; it does not load `central`, the packages or
  SymPy.
* **29 deferred import statements point up.** They run only inside a
  function body, so the load order is intact, but conceptually the
  dependency order is not completely clean. They are the known
  exceptions:

  | From → to | Count | Where |
  |---|--:|---|
  | `core` → `algebra` | 1 | `core/multi_eval.py` |
  | `algebra` → `central` | 4 | `algebra/derivation.py`, `algebra/grading.py`, `algebra/lie_bracket_vf.py` |
  | `algorithms` → `central` | 9 | `algorithms/product_rule.py`, `algorithms/sort_product.py`, `algorithms/factor_terms.py` |
  | `brackets` → `central` | 2 | `brackets/derived.py` |
  | `bibliography` → `display` | 1 | `bibliography.py` |
  | `proof` → `central` | 7 | `proof/strategies.py`, `proof/diagnostic_rules.py`, `proof/result.py` |
  | `proof` → `jacopy` | 1 | `proof/result.py` (version fallback) |
  | `central.objects` → `packages.metric_affine` | 1 | `central/objects/metric.py` (recognizes the metric-affine `Metric`) |
  | `packages` → `research` | 3 | `packages/drinfeld/examples.py`, `packages/generalized/frame_evaluation.py`, `packages/generalized/exceptional_double.py` |

* **Sideways edges inside a tier.** Among the packages, `drinfeld`
  imports `poisson` at module level, and `generalized` imports
  `drinfeld` and `poisson` at module level; the reverse directions
  (`poisson` → `drinfeld`/`generalized`, `drinfeld` → `generalized`,
  `metric_affine` → `poisson`, `generalized` → `metric_affine`) are
  deferred only, so the cycles between packages close only through
  deferred imports. Inside `central` (order `objects` → `calculus` →
  `tangent` → `algebroid`, upper imports lower), the edges against that
  order, `objects` → `calculus` and `calculus` → `tangent`, are
  deferred only; `algebroid` → `tangent` is deferred as well, so
  loading the algebroid layer does not load the tangent one.
* **Oracle edges.** The proof layer (`proof/result.py`, `search.py`,
  `strategies.py`, `verifier.py`) imports `oracle.hook` at module
  level; two more modules call the hook: `research/axiom_suite.py`
  (module level) and `packages/poisson/koszul_jacobi.py` (deferred).
  All of them reach only `jacopy/oracle/hook.py`, which imports no
  engine code. The rest of `oracle/` imports `core`, `algebra`,
  `brackets`, `central` and `packages.poisson` at module level to build
  its models, and is never imported by the library itself. The oracle
  is therefore not a tier but a separate checker standing beside the
  engine; it computes terms in its own way, through coordinate
  formulas.
* There is **no automated layering test yet** (*planned*: an import
  linter with an explicit allow-list of the edges above).

## File layout

Repository root:

```text
JacoPy/
├── jacopy/              186 .py files: the library itself (below)
├── tests/               122 test_*.py files, the oracle pytest plugin, rule_roles_inventory.json
├── examples/            4 Jupyter notebooks
├── docs/                this documentation (Sphinx and MyST Markdown)
├── scripts/             run_notebooks.py (runs the notebooks in order)
├── .github/workflows/   automated tests (Python 3.10–3.14, oracle job, weekly slow tests)
├── README.md, CHANGELOG.md, CITATION.cff, LICENSE
└── pyproject.toml, requirements.txt, Makefile
```

The library itself, folder by folder (modules and lines measured at
`9a11e9b`):

```text
jacopy/                                  root: public API (__init__.py, 255) + bibliography.py (770)
├── core/            15 modules  3,996   terms (expr.py), properties, registry,
│                                        pattern matching; ⟨α,X⟩, ω(Y₁…Y_k), ∧, ⊗, Sym/Alt, ⋆ nodes
├── algebra/          5 modules    758   derivations and the application D(x), degree, graded commutator
├── algorithms/      12 modules  2,459   simplification pipeline: flatten, canonicalize, distribute, collect,
│                                        sort_product (Koszul sign), product_rule (Leibniz)
├── brackets/         3 modules  1,018   abstract graded bracket, derived bracket
├── proof/           16 modules  6,248   engine (expansion.py), strategies, ProofStep/ProofChain,
│                                        ProofResult (result.py), Theorem/cite (theorems.py), replay
├── central/          1 module      21   facade
│   ├── objects/     17 modules  4,001   bundle, function, vector field, form, p-vector, tensor,
│   │                                    metric, Hodge, connection, frame, interior product, musical maps
│   ├── calculus/     9 modules  2,758   calculus of an (anchor, bracket) pair: d, L; rule sets
│   ├── tangent/     10 modules  2,759   TM: Lie bracket, d, L, Cartan relations, Schouten–Nijenhuis
│   └── algebroid/   11 modules  4,915   algebroid E: declarations, Jacobiator/Derivator, locality
├── packages/         1 module      25   facade
│   ├── poisson/      9 modules  5,163   Poisson, Koszul bracket and its Jacobi identity, tilde calculus, Nambu
│   ├── drinfeld/    11 modules  6,353   Drinfel'd doubles, π/B/H/R/m twists, Roytenberg bracket
│   ├── generalized/ 19 modules 11,775   Courant/Dorfman axioms, twisted Courant, Bourbaki, exceptional
│   └── metric_affine/ 20 modules 7,783  torsion, curvature, Bianchi, Koszul formula, E-connections
├── research/         9 modules  2,436   engine assembly, AxiomSuite, structure-kind registry, block matrices
├── display/          5 modules  2,423   ascii, latex, jupyter, terminal
└── oracle/           8 modules  3,776   hook, checking, model building, report
    └── models/       3 modules  1,107   concrete coordinate models: TM and algebroid
```

Five files are 13-line compatibility aliases that keep old module paths
importable (`poisson/koszul.py`, `metric_affine/koszul.py`,
`metric_affine/engine.py`, `central/tangent/engine.py`,
`central/algebroid/engine.py`); each alias *is* the renamed module.
Eight modules exceed 1,000 lines (see [Limitations](limitations.md)).
Every module is described, file by file, in the
[mathematical content table](../reference/math-content-table.md).

```{figure} ../_static/diagrams/file-map-core.svg
:alt: File map of the core, foundation, proof, research, display and oracle folders
:width: 100%

File map, part 1: core, foundation, proof engine, research interface,
display and oracle. Each card is a folder; red numbers mark modules
over 1,000 lines.
```

```{figure} ../_static/diagrams/file-map-packages.svg
:alt: File map of the central layer and the geometry packages
:width: 100%

File map, part 2: the central layer and the four geometry packages.
Gray italic entries are compatibility aliases.
```

## What each layer does

### `core/`: expression tree, properties, registry

| Module | Role |
|---|---|
| `expr.py` | `Expr`, `Atom`, `Symbol`, `Integer`, `Rational`, `Sum`, `Product`, `Power`, `Neg`. Nodes are inert: construction never computes. |
| `symbolic_degree.py` | `Degree`, a symbolic degree polynomial (forms of arbitrary degree $p$). |
| `properties.py`, `registry.py` | `Property` types (`Scalar`, `Graded`, `NonCommuting`, …) and `PropertyRegistry`, which attaches them to expressions from the outside. |
| `pairing.py`, `multi_eval.py`, `wedge.py`, `tensor_product.py`, `symmetrize.py`, `hodge.py`, `indexed_sum.py` | Algebraic node types: $\langle\alpha,X\rangle$, $\omega(Y_1,\dots,Y_k)$, $\wedge$, $\otimes$, Sym/Alt, $\star$, $\sum_i$. |
| `wildcards.py`, `traverse.py`, `equality.py` | Pattern matching, the read-only walker, equality helpers. |

### Foundation: `algebra/`, `algorithms/`, `brackets/`, `bibliography.py`

* `algebra/`: `Derivation` and `Act` (the inert application $D(x)$),
  `degree_of`, the exterior-degree contract (`grading.py`), the graded
  `Commutator`, the opaque vector-field bracket `LieBracketVF`.
* `algorithms/`: structural passes that hold in every geometry:
  `simplify` (flatten, canonicalize, normalize alternating forms,
  distribute, sort, collect), the graded Leibniz `product_rule`,
  Koszul-signed `sort_product`, `factor_terms`, `rewrite_to_fixpoint`.
* `brackets/`: the abstract `GradedBracket`, `BracketApply` and the
  derived-bracket machinery (`DerivedBracket`, `VanishingCondition`).
* `bibliography.py`: the reference table and APA 7 rendering (`cite`,
  `apa_reference`, `references_block`, `bibtex_entry`); see the
  [bibliography](../reference/bibliography.md).

### `proof/`: the proof engine

| Module | Role |
|---|---|
| `expansion.py` | `Definition` (one rewrite rule: `matches` / `rewrite`, `anchor`, `role`, `owner`, `identity`, `source`) and `ExpansionEngine` (registers rules, fires the leftmost-innermost match, records each firing as a `ProofStep`). |
| `strategies.py` | `ExpandAndSimplify`, `AgreementOnGenerators`, `UnrollToFoundations`, `PortfolioStrategy`; `ProofFailure` carries the surviving residual. |
| `verifier.py`, `search.py` | `show_equal`; `prove` (deterministic, or `SearchStrategy` with `prefer="shortest"`, `"readable"` or `"elementary"`). |
| `result.py` | `ProofResult` (`CLOSED` / `RESIDUAL` / `BUDGET` / `INVALID`), `Goal`, `Assumption`, `Provenance`; the driver `prove(engine, lhs, rhs)`. |
| `theorems.py` | `Theorem`, `TheoremBook`, `TheoremDefinition`, `cite`, `check_citation`. |
| `step.py`, `chain.py` | `ProofStep` / `ProofChain`; minting of library-produced steps. |
| `replay.py` | Chain-shape replay: does a theorem's chain really run from `lhs` to `rhs`? |
| `registry_facts.py` | Registry answers a proof relied on, recorded as requirements. |
| `ownership.py` | Which structure owns a rule, theorem or step. |
| `normalize.py`, `diagnostics.py`, `diagnostic_rules.py`, `recognizers.py` | Normal forms, residual diagnostics, shape recognizers. |

### `central/`: objects and calculus valid on $TM$ and on an algebroid $E$

The design principle of the central layer: every object is defined so
that taking $E=TM$, $\rho_E=\mathrm{id}$ and
$[\cdot,\cdot]_E=[\cdot,\cdot]_{\mathrm{Lie}}$ gives back the usual
tangent-bundle version.

* `central/objects/`: building blocks, no rewrite rules:
  `Bundle`/`TM`, functions, vector fields, forms, $p$-vectors, tensors,
  metric and inverse metric, Hodge star, connection, frame/coframe,
  interior and tilde interior products, multivector interior product,
  musical maps, partial evaluation, endomorphisms, and `kind.py` (the
  shared type query).
* `central/calculus/`: the calculus of an (anchor, bracket) pair,
  independent of $TM$: `BracketCalculus`, `ExteriorDerivative`,
  `LieDerivative` and their intrinsic definitions
  (`bracket_calculus.py`); interior, symmetrization,
  partial-evaluation, indexed-sum and tensor rules; `scalars.py` with
  `is_real_constant`, the single "Scalar means a real constant"
  predicate; and `slot_rules.py`, the structure-free slot-hygiene rules
  (`PairingArgSplitDefinition`, `FormProductToWedgeDefinition`, …).
* `central/tangent/`: the $TM$ instance: `lie_bracket.py`,
  `anholonomy.py` ($\gamma^c{}_{ab}$), `exterior.py` ($d$), `cartan.py`
  ($\mathcal{L}$ and the Cartan relations, proved as theorems),
  `cartan_rules.py` (structure-free Cartan rewrite rules such as
  `MagicFormulaDefinition`), `schouten.py` (Schouten–Nijenhuis
  bracket), `definitions.py`, and `tangent_expansion.py` with
  `tangent_engine()`, the assembly point of the definitional rules.
* `central/algebroid/`: the algebroid instance: `context.py` (anchored
  bundle, opaque bracket, coboundary), `declarations.py` (declared
  axioms: right/left Leibniz, Jacobi, …), `operators.py` (Jacobiator,
  Derivator, Predator), `locality.py` (locality projector),
  `calculus.py` ($d_E$, $\mathcal{L}^E$), `theorems.py` (relations
  between the axioms), `defect_formulas.py`, `rules.py`, and
  `algebroid_expansion.py` with `algebroid_engine()`.

### `packages/`: geometry built on the central layer

Each package has a facade (`from jacopy.packages.<name> import …`).

* `poisson/`: `core.py` (Poisson bivector, $\{f,g\}$, $\pi^\sharp$),
  `koszul_forms.py` (Koszul bracket on 1-forms), `koszul_jacobi.py`
  (its general Jacobi identity), `tilde.py` (tilde calculus),
  `symplectic.py`, `nambu.py` (Nambu–Poisson structures and the higher
  Koszul bracket), `showcase.py`.
* `drinfeld/`: calculus on algebroids and Drinfel'd doubles:
  `calculus_conditions.py` ($\mathcal{K}$ operator), `double.py`,
  `poisson_bialgebroid.py`, `tilde_calculus.py`, `twist.py`
  ($\pi$/$B$/$H$/$R$/$m$ twists), `roytenberg.py`,
  `bracket_morphism.py`, `metric_invariance.py`, `abstract_double.py`,
  `examples.py`.
* `generalized/`: Courant algebroids: `courant_axioms.py` and
  `dorfman_axioms.py` (Uchino's redundancy theorems),
  `standard_courant.py`, `twisted_courant.py`, `general_twist.py`,
  `poisson_generalized.py`, `r_twisted.py`, `roytenberg_courant.py`,
  the Bourbaki family (`bourbaki_*.py`), `exact_locality_projector.py`,
  `exceptional_double.py`, `exceptional_rotation.py`,
  `frame_evaluation.py`, `dialect_bridge.py`; `_cited_rule.py` is the
  internal `CitedTheoremMixin` for rules that rewrite by a proven,
  cited theorem (role `theorem`; the citation's requirements are passed
  on).
* `metric_affine/`: `torsion_curvature.py`, `metric.py`,
  `metric_koszul.py` (Koszul formula), `bianchi.py`,
  `nonmetricity_forms.py`, `frame_components.py`,
  `component_workflow.py` (concrete component input), `rules.py` (the
  connection's linearity and Leibniz rules), `decomposition.py`
  (opt-in frame decompositions and the `IndexedSum` operator pushes),
  the $E$-connection family (`e_connection.py`, `e_bianchi.py`,
  `e_cartan.py`, `e_koszul.py`, `admissible.py`, `modified.py`,
  `derived.py`), and `metric_affine_expansion.py` with the package
  engine.

The mathematics of each package is summarized in
[Capabilities](capabilities.md).

### `research/`: the research interface

`sections.py` (generalized sections $U\oplus\omega_2\oplus\cdots$),
`block_matrix.py` (block-operator automorphisms $\Psi$),
`engine_assembly.py` (`Scan`, `assemble_engine`, `assembly_report`:
build the engine from the expressions to be checked), `axiom_suite.py`
(`AlgebroidData`, `AxiomSuite`: run the Courant-type conditions),
`antisymmetrize.py` (`antisymmetrize_indices`), `providers.py` (the
structure-provider protocol), `structure_kinds.py` (the registry
`assemble_engine` reads) and `nambu_kind.py` (the built-in
Nambu–Poisson kind).

### `display/`: rendering

`ascii.py`, `latex.py` (expressions, `gather*` proof transcripts,
theorem paragraphs, standalone documents, TikZ), `jupyter.py`
(`_repr_latex_` / `_repr_html_`), `terminal.py` (colored trees with the
optional `rich` package). The display layer reads expressions and
chains; it never changes them. New node types register a LaTeX handler
with `jacopy.display.register`.

### `oracle/`: the model oracle

`hook.py` (engine-side entry point, no engine imports), `check.py`
(`check_equal`, `check_chain`), `realize.py` / `realize_e.py`
(expression to concrete values), `models/` (tangent and algebroid
models), `select.py`, `values.py`, `report.py`. What the oracle does
and what its verdicts mean is explained in
[Trust model](trust-model.md).

## How a proof runs

```{figure} ../_static/diagrams/processing-flow.svg
:alt: The path of an expression through the proof pipeline
:width: 100%

Processing flow. The top row (1–4) reads left to right, the bottom row
(5–8) right to left; a citation feeds back into the engine as a new
rule; the oracle branches off from a `CLOSED` result. The worked example
at the bottom was produced by running the code at `9a11e9b`.
```

1. **Build an expression** (`core`, `central/objects`) from the
   factories (`functions`, `vector_fields`, `forms`, `exterior_d()`,
   `lie_derivative(X)`, `interior(X)`, `pairing`, …). Operators are
   applied by calling them: `d(omega)`, `L_X(omega)`. Constructors do
   not compute; the result is a formal term.
2. **State the hypotheses** (`core/registry.py`). The registry
   attaches properties to terms from the outside ("$c$ is a real
   constant"). If a step relies on an answer from the registry, that
   answer appears as a requirement of the result.
3. **Choose an engine** (`central/tangent`, `proof/expansion.py`):
   `tangent_engine()`, `algebroid_engine(E)`, a package engine, or
   `research.assemble_engine(expr, structures=…)`. An engine is a list
   of `Definition` rules. The base engine contains no geometry; each
   layer registers its own rules (`tangent_engine()` has 25).
4. **Run a strategy** (`proof/expansion.py`, `proof/strategies.py`).
   The engine finds the leftmost-innermost matching subterm, applies
   the rule and repeats. `ExpandAndSimplify` expands both sides,
   reduces them to normal form with the simplification pipeline
   (`algorithms`) and checks whether the difference is zero.
   `show_equal(lhs, rhs, engine=…)` returns a `ProofChain` or raises
   `ProofFailure` with the residual; `jacopy.proof.result.prove(engine,
   lhs, rhs)` returns a `ProofResult` that also lists what the result
   depends on.
5. **Record the derivation** (`proof/step.py`, `chain.py`,
   `result.py`). Each rule application is a step: before, after, rule,
   source.
6. **Record a theorem** (`proof/theorems.py`). A `Theorem` stores
   `lhs`, `rhs`, its chain, a generality tag (`operator-level`,
   `generic-function`, `symbolic-p`, `instance`) and its requirements;
   `TheoremBook` holds theorems by name.
7. **Cite it** (`cite`). `cite(engine, book, name)` turns a theorem
   into a derived rule of another engine. Citation is the only way a
   proven result enters another proof, and it is rejected by default
   when the theorem's hypotheses are not met there.
8. **Display** (`display`). `to_latex`, `print_chain`,
   `chain_to_latex`, `theorem_to_latex_document(..., references="apa")`.
   A rule's `source` (a `bibliography.cite(...)` citation) is copied
   onto every step it produces and printed with it.

A runnable example: Cartan's formula on a 1-form, evaluated on a vector
field, $\langle\mathcal{L}_X\omega,Y\rangle=\langle\iota_Xd\omega,Y\rangle+\langle d\iota_X\omega,Y\rangle$.

```python
import jacopy
from jacopy.central.tangent import tangent_engine
from jacopy.proof.result import prove as prove_result

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

lhs = jacopy.pairing(L_X(omega), Y)
rhs = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)

res = prove_result(tangent_engine(registry=reg), lhs, rhs, registry=reg)
assert res.status == "CLOSED"
print(res.summary())
```

```text
CLOSED: ⟨L_X(omega), Y⟩ = (⟨ι_X(d(omega)), Y⟩ + ⟨d(ι_X(omega)), Y⟩)  — assumption-free
  generality: generic-function
  via definition: intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = ρ(X)(ω(Y…)) − Σ ω(…,[X,Y_i],…)
  via canonicalization: simplify
  via definition: intrinsic d (Cartan-TM): Palais formula dω(X_0,…,X_p) = Σ(−1)^i ρ(X_i)(ω(…)) + Σ(−1)^{i+j} ω([X_i,X_j],…) ×2
  via definition: interior product: ι_X f = 0, ι_X ω = ⟨ω, X⟩ (deg 0 / 1)
  via definition: interior product evaluation: (ι_X ω)(Y_1,…,Y_k) = ω(X, Y_1,…,Y_k)
  budget: 6/1024 steps; jacopy 0.0.1
```

The result is *assumption-free*: it rests on no declared axiom and uses
only the definitions of $d$ (Palais formula), $\mathcal{L}$ and
$\iota$. The six steps of the chain are:

| Step | Rule applied | Effect on the term |
|--:|---|---|
| 1 | definition of $\mathcal{L}$ (Cartan, $TM$) | $\langle\mathcal{L}_X\omega,Y\rangle\to X(\langle\omega,Y\rangle)-\langle\omega,[X,Y]\rangle$ |
| 2 | evaluation of the interior product | $\langle\iota_Xd\omega,Y\rangle\to d\omega(X,Y)$ |
| 3 | $d$: Palais formula | $d\omega(X,Y)\to X(\langle\omega,Y\rangle)-Y(\langle\omega,X\rangle)-\langle\omega,[X,Y]\rangle$ |
| 4 | interior product | $\iota_X\omega\to\langle\omega,X\rangle$ |
| 5 | $d$: Palais formula | $\langle d\langle\omega,X\rangle,Y\rangle\to Y(\langle\omega,X\rangle)$ |
| 6 | simplification | difference $\to 0$ |

(architecture-extension-points)=
## Extension points

**A new rule: subclass `Definition`.** Give it `matches` and
`rewrite`. A rule that is a hypothesis of the user's structure sets
`role = "assumption"` and an `owner`; it then appears in `requires`.

```python
import jacopy
from jacopy.central.tangent import tangent_engine
from jacopy.proof.result import prove as prove_result

class Flux(jacopy.Symbol):
    """A new atom: the flux H of a user structure."""
    __slots__ = ()

class FluxIsClosed(jacopy.Definition):
    """The user's axiom dH = 0."""
    name = "user axiom: dH = 0"
    role = "assumption"

    def matches(self, expr):
        return (isinstance(expr, jacopy.Act) and isinstance(expr.arg, Flux)
                and expr.op == jacopy.exterior_d())

    def rewrite(self, expr):
        return jacopy.Integer(0)

class HStructure:
    name = "H-structure"
    def __repr__(self):
        return "HStructure"

reg = jacopy.PropertyRegistry()
eng = tangent_engine(registry=reg)
rule = FluxIsClosed()
rule.owner = HStructure()
eng.register(rule)

d = jacopy.exterior_d()
res = prove_result(eng, d(Flux("H")), jacopy.Integer(0), registry=reg)
assert res.status == "CLOSED"
assert {a.kind for a in res.requires} == {"declared", "structure"}
print(res.summary())
```

```text
CLOSED: d(H) = 0  — under the assumptions below
  generality: generic-function
  requires declared: user axiom: dH = 0 [HStructure]
  requires structure: HStructure [HStructure]
  budget: 1/1024 steps; jacopy 0.0.1
```

**A new structure type for `assemble_engine`: register a
`StructureKind`.** No library file changes. A structure is a provider
(`name`, `declarations`, `declares`, `with_declarations`,
`engine_rules`); its kind tells the assembler how to recognize it and
which key its nodes carry. The built-in kinds, families and family
rules always load first, whenever the user registers (unless
`first=True` is passed on purpose), and `register_family_rule` is
idempotent.

```python
import jacopy
from jacopy.proof.result import prove as prove_result
from jacopy.research import assemble_engine, assembly_report
from jacopy.research.structure_kinds import (
    StructureKind, register_family, register_structure_kind, unregister,
)

class Flux(jacopy.Symbol):
    """A node owned by the structure of the same name."""
    __slots__ = ()

class FluxVanishes(jacopy.Definition):
    name = "flux vanishes: H = 0"
    role = "assumption"
    anchor = Flux
    def matches(self, expr):
        return isinstance(expr, Flux)
    def rewrite(self, expr):
        return jacopy.Integer(0)

class FluxStructure:
    def __init__(self, name, declarations=()):
        self.name, self.declarations = name, frozenset(declarations)
    def declares(self, key):
        return key in self.declarations
    def with_declarations(self, *keys):
        return FluxStructure(self.name, self.declarations | set(keys))
    def engine_rules(self, registry=None, *, phase=None):
        rule = FluxVanishes()
        rule.owner, rule.identity = self, ("FluxVanishes", self.name)
        return [rule]

class FluxKind(StructureKind):
    name = "flux"
    def accepts(self, s):
        return isinstance(s, FluxStructure)
    def key(self, s):
        return s.name

kind = register_structure_kind(FluxKind())
family = register_family(Flux, "flux", owner_key=lambda node: node.name)
try:
    reg = jacopy.PropertyRegistry()
    H = FluxStructure("H")
    eng = assemble_engine(Flux("H"), registry=reg, structures=(H,))
    print("\n".join(assembly_report(eng)))   # which rules were added, and why
    assert prove_result(eng, Flux("H"), jacopy.Integer(0), registry=reg).status == "CLOSED"
finally:
    for entry in (family, kind):
        unregister(entry)
```

```text
scanned 1 expression(s): Scan(families=['flux'], sharps=["'H'"])
base: tangent (Cartan) engine, first structure H [flux]
+ flux vanishes: H = 0  [rules of H]
structure H: declarations none
+ zero product: 0·x = 0 (slot-reachable)  [always: zero products inside operator slots]
```

**A new node type in the display:** `jacopy.display.register` adds
its LaTeX handler.

**A new theorem:** a proved result is recorded as a `Theorem`, added to
a `TheoremBook` and enters other engines through `cite`; the citation
check described in [Trust model](trust-model.md) applies.

## Public surface and support levels

The levels are those of the `jacopy` module docstring:

1. **Stable: `jacopy.__all__`** (66 names): expression classes, object
   factories, tangent operators, proof entry points (`show_equal`,
   `prove`, `ProofChain`, `ProofResult`, `Theorem`, `cite`,
   `Definition`, `ExpansionEngine`, …) and display helpers. Each name
   is the very object its subpackage defines; everything except the
   expression classes loads lazily.
2. **Stable extension protocols:** `Expr` / `Atom`, `Definition`,
   `jacopy.display.register`.
3. **Public, still evolving:** the subpackage facades
   (`jacopy.research`, `jacopy.packages.<name>`,
   `jacopy.central.objects`, `jacopy.central.tangent`, `jacopy.proof`,
   `jacopy.display`), that is, each package's `__all__`.
4. **Internal:** every other module path and every `_`-prefixed name.

Same name, different object (also listed in the docstring):
`jacopy.cite` is `proof.theorems.cite` (not `bibliography.cite`);
`jacopy.prove` is `proof.search.prove` (not `proof.result.prove`);
`jacopy.Zero` is the expression zero (not `research.ZeroOperator`);
`jacopy.normalize` is `proof.normalize` (not
`algorithms.rewrite_to_fixpoint`); `Metric`/`metric` are the central
metric atom (not the metric-affine context).

The full API is listed in the [reference](../reference/index.md).
