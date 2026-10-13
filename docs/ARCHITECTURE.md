# jacopy v3 — Architecture

*Measured on 2026-10-02 (branch `fix/display-polish`, based on `main`
at `8b46a5d`): 186 Python modules, about 70,800 lines under `jacopy/`;
122 test files; the fast suite is
2,572 passed, 12 skipped, 5 xfailed (`pytest tests -q`). These numbers change with every merge;
the layer boundaries and the trust model below are the part of this
document that is meant to stay true.*

This document describes what the code does **today**. Anything that
is not implemented yet is marked *planned*.

---

## 1. Layer map

```
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

The rule is **"arrows point down"**: a module may import from its own
layer and from the layers below it. Measured with an AST scan of every
`import` under `jacopy/` (2026-10-02):

* **No module-level import points up.** Importing `jacopy.proof` loads
  `core`, `algebra`, `algorithms`, `brackets`, `proof` and
  `jacopy.oracle.hook` — no `central`, no `packages`, no sympy.
* **29 deferred imports point up** (inside a function body, executed
  only when that function runs). They are the known exceptions of
  audit finding T2-2:

  | From → to | Count | Where |
  |---|---|---|
  | `core` → `algebra` | 1 | `core/multi_eval.py` |
  | `algebra` → `central` | 4 | `algebra/grading.py`, `algebra/derivation.py`, `algebra/lie_bracket_vf.py` |
  | `algorithms` → `central` | 9 | `algorithms/product_rule.py`, `algorithms/sort_product.py`, `algorithms/factor_terms.py` |
  | `brackets` → `central` | 2 | `brackets/derived.py` |
  | `bibliography` → `display` | 1 | `bibliography.py` |
  | `proof` → `central` | 7 | `proof/strategies.py`, `proof/diagnostic_rules.py`, `proof/result.py` |
  | `proof` → `jacopy` | 1 | `proof/result.py` (version fallback) |
  | `central.objects` → `packages.metric_affine` | 1 | `central/objects/metric.py` (recognises the metric-affine `Metric`) |
  | `packages` → `research` | 3 | `packages/drinfeld/examples.py`, `packages/generalized/frame_evaluation.py`, `packages/generalized/exceptional_double.py` |

* **Sideways edges inside a layer** exist too. Among the packages,
  `drinfeld` imports `poisson` at module level and `generalized`
  imports `drinfeld` at module level; the reverse directions
  (`poisson` → `drinfeld`/`generalized`, `drinfeld` → `generalized`,
  `metric_affine` → `poisson`, `generalized` → `metric_affine`) are
  deferred imports. Inside `central` (order `objects` → `calculus` →
  `tangent` → `algebroid`, upper imports lower), two edges against
  that order are deferred only: `objects` → `calculus` (7, in
  `objects/endomorphism.py`, `objects/kind.py`,
  `objects/multivector_interior.py`) and `calculus` → `tangent` (1,
  `calculus/tensor_calculus.py`, the TM `d` of the tensor calculus);
  `algebroid` → `tangent` (8) is deferred as well, so loading the
  algebroid layer does not load the tangent one.
* **Oracle edges.** Besides the proof layer (`proof/result.py`,
  `search.py`, `strategies.py`, `verifier.py` → `oracle.hook`, module
  level), two more modules call the hook: `research/axiom_suite.py`
  (module level) and `packages/poisson/koszul_jacobi.py` (deferred).
  All three reach only `jacopy/oracle/hook.py`, which imports no
  engine code; the rest of `oracle/` imports `core`, `algebra`,
  `brackets`, `central` and `packages.poisson` at module level and is
  never imported by the library itself.
* Of all 2,412 `jacopy` imports, 1,068 are deferred; most of them are
  not upward, they keep `import jacopy` light.
* There is **no automated layering test yet** (*planned*: an import
  linter with an explicit allow-list of the edges above, as proposed in
  T2-2).

## 2. What each layer does

### `core/` — expression tree, properties, registry

| Module | Role |
|---|---|
| `expr.py` | `Expr`, `Atom`, `Symbol`, `Integer`, `Rational`, `Sum`, `Product`, `Power`, `Neg`. Nodes are inert: construction never computes. |
| `symbolic_degree.py` | `Degree`, a symbolic degree polynomial (arbitrary-p forms). |
| `properties.py`, `registry.py` | `Property` types (`Scalar`, `Graded`, `NonCommuting`, …) and `PropertyRegistry`, which attaches them to expressions from the outside. |
| `pairing.py`, `multi_eval.py`, `wedge.py`, `tensor_product.py`, `symmetrize.py`, `hodge.py`, `indexed_sum.py` | Algebraic node types: `⟨α, X⟩`, `ω(Y₁,…,Y_k)`, `∧`, `⊗`, Sym/Alt, `⋆`, `Σ_i`. |
| `wildcards.py`, `traverse.py`, `equality.py` | Pattern matching, the read-only walker, equality helpers. |

### Foundation: `algebra/`, `algorithms/`, `brackets/`, `bibliography.py`

* `algebra/` — `Derivation` and `Act` (the inert application `D(x)`),
  `degree_of`, the exterior-degree contract (`grading.py`), the graded
  `Commutator`, the opaque vector-field bracket `LieBracketVF`.
* `algorithms/` — structural passes that hold in every geometry:
  `simplify` (flatten, canonicalize, normalize alternating forms,
  distribute, sort, collect), the graded Leibniz `product_rule`,
  Koszul-signed `sort_product`, `factor_terms`, `rewrite_to_fixpoint`.
* `brackets/` — the abstract `GradedBracket`, `BracketApply` and the
  derived-bracket machinery (`DerivedBracket`, `VanishingCondition`).
* `bibliography.py` — the reference table and APA 7 rendering
  (`cite`, `apa_reference`, `references_block`, `bibtex_entry`).

### `proof/` — the proof engine

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
| `normalize.py`, `diagnostics.py`, `diagnostic_rules.py`, `recognizers.py` | Normal forms, residual diagnostics, shape recognisers. |

### `central/` — objects and calculus valid on `TM` and on an algebroid `E`

The central-code principle (course guideline, item 8a): every object is
defined so that `E = TM`, `ρ_E = id`, `[·,·]_E = [·,·]_Lie` gives back
the usual tangent-bundle version.

* `central/objects/` — building blocks, no rewrite rules:
  `Bundle`/`TM`, functions, vector fields, forms, p-vectors, tensors,
  metric and inverse metric, Hodge star, connection, frame/coframe,
  interior and tilde interior, multivector interior, musical maps,
  partial evaluation, endomorphisms, and `kind.py` (the shared type
  query).
* `central/calculus/` — the calculus of an `(anchor, bracket)` pair,
  independent of `TM`: `BracketCalculus`, `ExteriorDerivative`,
  `LieDerivative` and their intrinsic definitions
  (`bracket_calculus.py`); interior, symmetrization, partial-evaluation,
  indexed-sum and tensor rules; `scalars.py` with `is_real_constant`,
  the single "Scalar = ℝ-constant" predicate; and `slot_rules.py`, the
  structure-free slot-hygiene rules (`PairingArgSplitDefinition`,
  `FormProductToWedgeDefinition`, …) moved here from the packages
  (audit T2-1).
* `central/tangent/` — the `TM` instance: `lie_bracket.py`,
  `anholonomy.py` (`γ^c_ab`), `exterior.py` (`d`), `cartan.py` (`L`
  and the Cartan relations, proved as theorems), `cartan_rules.py`
  (structure-free Cartan rewrite rules such as
  `MagicFormulaDefinition`, moved here in T2-1), `schouten.py`
  (Schouten–Nijenhuis), `definitions.py`, and `tangent_expansion.py`
  with `tangent_engine()`, the assembly point of the definitional
  rules.
* `central/algebroid/` — the algebroid instance: `context.py`
  (anchored bundle, opaque bracket, coboundary), `declarations.py`
  (declared axioms: right/left Leibniz, Jacobi, …), `operators.py`
  (Jacobiator, Derivator, Predator), `locality.py` (locality
  projector), `calculus.py` (`d_E`, `L^E`), `theorems.py` (relations
  between the axioms), `defect_formulas.py`, `rules.py`, and
  `algebroid_expansion.py` with `algebroid_engine()`.

### `packages/` — geometry built on the central code

Each package has a facade (`from jacopy.packages.<name> import …`).

* `poisson/` — `core.py` (Poisson bivector, `{f,g}`, `π♯`),
  `koszul_forms.py` (Koszul bracket on 1-forms), `koszul_jacobi.py`
  (its general Jacobi identity), `tilde.py` (tilde calculus),
  `symplectic.py`, `nambu.py` (Nambu–Poisson and the higher Koszul
  bracket), `showcase.py`.
* `drinfeld/` — calculus on algebroids and Drinfel'd doubles:
  `calculus_conditions.py` (𝒦 operator), `double.py`,
  `poisson_bialgebroid.py`, `tilde_calculus.py`, `twist.py`
  (π/B/H/R/M twists), `roytenberg.py`, `bracket_morphism.py`,
  `metric_invariance.py`, `abstract_double.py`, `examples.py`.
* `generalized/` — Courant algebroids: `courant_axioms.py` and
  `dorfman_axioms.py` (Uchino redundancy theorems),
  `standard_courant.py`, `twisted_courant.py`, `general_twist.py`,
  `poisson_generalized.py`, `r_twisted.py`, `roytenberg_courant.py`,
  the Bourbaki family (`bourbaki_*.py`), `exact_locality_projector.py`,
  `exceptional_double.py`, `exceptional_rotation.py`,
  `frame_evaluation.py`, `dialect_bridge.py`; `_cited_rule.py` is the
  internal `CitedTheoremMixin` for rules that rewrite by a proven,
  cited theorem (role `theorem`, the citation's requirements flow on).
* `metric_affine/` — `torsion_curvature.py`, `metric.py`,
  `metric_koszul.py` (Koszul formula), `bianchi.py`,
  `nonmetricity_forms.py`, `frame_components.py`,
  `component_workflow.py` (concrete component input), `rules.py`
  (the connection's linearity / Leibniz rules), `decomposition.py`
  (opt-in frame decompositions and the `IndexedSum` operator pushes),
  the
  E-connection family (`e_connection.py`, `e_bianchi.py`,
  `e_cartan.py`, `e_koszul.py`, `admissible.py`, `modified.py`,
  `derived.py`), and `metric_affine_expansion.py` with the package
  engine.

The old module paths `poisson/koszul.py`, `metric_affine/koszul.py`,
`metric_affine/engine.py`, `central/tangent/engine.py` and
`central/algebroid/engine.py` still import: each is a compatibility
alias that *is* the renamed module.

### `research/` — the research interface (guideline item 15)

`sections.py` (generalized sections `U ⊕ ω₂ ⊕ …`), `block_matrix.py`
(block-operator automorphisms `Ψ`), `engine_assembly.py`
(`Scan`, `assemble_engine`, `assembly_report`: build the engine from
the expressions to be checked), `axiom_suite.py` (`AlgebroidData`,
`AxiomSuite`: run the Courant-type conditions), `antisymmetrize.py`
(`antisymmetrize_indices`), `providers.py` (the structure-provider
protocol), `structure_kinds.py` (the registry `assemble_engine` reads)
and `nambu_kind.py` (the built-in Nambu–Poisson kind).

### `display/` — rendering

`ascii.py`, `latex.py` (expressions, `gather*` proof transcripts,
theorem paragraphs, standalone documents, TikZ), `jupyter.py`
(`_repr_latex_` / `_repr_html_`), `terminal.py` (coloured trees with
the optional `rich`). The display layer reads expressions and chains;
it never changes them. New node types register a LaTeX handler with
`jacopy.display.register`.

### `oracle/` — the model oracle

`hook.py` (engine-side entry point, no engine imports), `check.py`
(`check_equal`, `check_chain`), `realize.py` / `realize_e.py`
(expression → concrete values), `models/` (tangent and algebroid
models), `select.py`, `values.py`, `report.py`. See section 5.

## 3. How a proof runs

```
expression ──► engine rules (Definitions) ──► ExpansionEngine ──► ProofChain / ProofResult
                                                                        │
                                   Theorem (+ requires) ◄───────────────┘
                                        │
                  cite() into another engine, or display: LaTeX + APA references
```

1. **Build an expression** from the factories (`functions`,
   `vector_fields`, `forms`, `exterior_d()`, `lie_derivative(X)`,
   `interior(X)`, `pairing`, …). Operators are applied by calling
   them: `d(omega)`, `L_X(omega)`.
2. **Choose an engine.** `tangent_engine()`, `algebroid_engine(E)`, a
   package engine, or `research.assemble_engine(expr, structures=…)`.
   An engine is a list of `Definition` rules; the base engine contains
   no geometry, each layer registers its own.
3. **Run a strategy.** `show_equal(lhs, rhs, engine=…)` uses
   `ExpandAndSimplify` and returns a `ProofChain` or raises
   `ProofFailure` with the residual. `jacopy.proof.result.prove(engine,
   lhs, rhs)` returns a `ProofResult` that also lists what the result
   depends on.
4. **Record a theorem.** A `Theorem` stores `lhs`, `rhs`, its chain, a
   generality tag (`operator-level`, `generic-function`, `symbolic-p`,
   `instance`) and its requirements; `TheoremBook` holds them and
   `cite(engine, book, name)` turns one into a derived rule of another
   engine. Citation is the only way a proven result enters a proof.
5. **Display.** `to_latex`, `print_chain`, `chain_to_latex`,
   `theorem_to_latex_document(..., references="apa")`. A rule's
   `source` (a `bibliography.cite(...)` citation) is copied onto every
   step it produces and printed with it.

Runnable example (Cartan's formula on a 1-form, evaluated on a vector
field):

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
print(res.summary())   # "... — assumption-free", the definitions used, the budget
```

## 4. Trust model

**What a closed result means.** `CLOSED` says the engine rewrote both
sides to the same normal form using the rules it was given. It is
always shown *under its assumptions*. There is no `DISPROVED`: a
residual is not a certificate that an identity is false.

**Requirements (`ProofResult.requires`, `Theorem.requires`).** Every
`Assumption` has one of the kinds in
`jacopy.proof.result.ASSUMPTION_KINDS`:

| Kind | Meaning |
|---|---|
| `declared` | A declared axiom of a structure that actually fired (owner, number of instances, the rule's structural key). |
| `structure` | The structure object those axioms belong to. |
| `registry` | A registry answer the steps relied on (`x` is `Scalar`, `p` has `Graded(0)`, "nothing declared" …). |
| `scope` | An instance proof (generality `instance`); never upgraded to a general one. |
| `textual` | A `from_axioms` prose entry no step accounts for: kept visible, not a verification input. |
| `legacy` | Recorded but not structurally verified (a step whose rule has no role, an unverified citation, a chain that does not prove its claim). |
| `unreplayed` | The requirements were derived, but the chain does not replay into `lhs = rhs`. |

A rule's `role` decides how a fired step is classified: `definition`
(no assumption), `assumption` (a declared axiom, giving `declared` and
`structure` entries), `theorem` (a citation; its requirements are
folded in transitively).

**Minting.** Only the library's own producers (engine, normalization
passes, strategies) mark a `ProofStep` as minted
(`jacopy.proof.step.is_minted`). A step built by hand through the
public API is never minted, whatever metadata it carries. Minting
certifies origin, not mathematical correctness.

**Replay.** `jacopy.proof.replay.chain_verdict` checks that a
theorem's chain is connected and runs between the two sides of the
claim. `Theorem.chain_replayed` is true only when the requirements were
derived and no `unreplayed` or `legacy` entry remains.

**Citation — default reject.** `check_citation` refuses a citation
unless every `declared`/`structure` requirement is met by a structure
of the same name in the citing engine (same or stronger declarations)
*and* the same licensing rule is registered there, and every
`registry` requirement is answered the same way by the citing registry
(when the citing registry is unknown, a registry-dependent theorem is
not citable). A `legacy` or `unreplayed` record is citable only with an
explicit `allow_legacy=True`, and the citing result then carries the
marker.

**The Scalar contract.** `Scalar` means a real constant. The single
predicate is `jacopy.central.calculus.scalars.is_real_constant`; the
engine, `product_rule`, `sort_product`, `degree_of`, `kind_of`,
`AgreementOnGenerators`, the diagnostics and the model oracle all call
it. A declaration that contradicts the contract (Scalar together with
`Graded(k ≠ 0)`, `NonCommuting` or `AntiCommuting`) raises
`ScalarContractError`. The facts the predicate read become `registry`
requirements of the step.

## 5. The model oracle

The oracle is an independent falsifier. When the engine closes
`lhs = rhs`, it can evaluate both sides in random concrete coordinate
models (sympy polynomials on `ℝⁿ`; algebroid models `E = ℝⁿ × ℝʳ`
with a polynomial anchor and a concrete bracket) and compare them.

* **Verdicts** (`jacopy.oracle.report.VERDICTS`): `AGREE` (not refuted
  in the sampled models — never a proof), `DISAGREE`, `UNSUPPORTED`
  (a node the realizers do not cover, a dimension above the cap, …),
  `AMBIGUOUS` (the two readings of a `Product` disagree),
  `ASSUMPTION_LEAK` (a declared Poisson property the proof record does
  not use turns out to be needed: the equation fails in a non-Poisson
  counter-model).
* **Modes.** `JACOPY_ORACLE=off|warn|strict` (default `off`: nothing
  is imported), the `oracle=` keyword of `show_equal` /
  `proof.result.prove`, or `jacopy.oracle.hook.oracle_mode`. `warn`
  emits `OracleWarning` on a refutation; `strict` raises
  `OracleDisagreement`.
* **Tests.** `pytest --oracle=warn|strict [--oracle-report PATH]`
  (see `docs/TESTING.md`).
* **Requires** the `oracle` extra (`pip install -e ".[oracle]"`).

```python
import jacopy
from jacopy.oracle import check_equal

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)
lhs = jacopy.pairing(L_X(omega), Y)

good = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)
bad = jacopy.pairing(i_X(d(omega)), Y)
assert check_equal(lhs, good, registry=reg).verdict == "AGREE"
assert check_equal(lhs, bad, registry=reg).verdict == "DISAGREE"
```

## 6. Extension points

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
```

**A new structure type for `assemble_engine`: register a
`StructureKind`.** No library file changes. A structure is a provider
(`name`, `declarations`, `declares`, `with_declarations`,
`engine_rules`); its kind tells the assembler how to recognise it and
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

**A new node type in the display:** `jacopy.display.register` adds
its LaTeX handler.

## 7. Public surface and support levels

The levels are those of the `jacopy` module docstring:

1. **Stable — `jacopy.__all__`** (66 names): expression classes,
   object factories, tangent operators, proof entry points
   (`show_equal`, `prove`, `ProofChain`, `ProofResult`, `Theorem`,
   `cite`, `Definition`, `ExpansionEngine`, …) and display helpers.
   Each name is the very object its subpackage defines; everything but
   the expression classes loads lazily.
2. **Stable extension protocols:** `Expr` / `Atom`, `Definition`,
   `jacopy.display.register`.
3. **Public, still evolving:** the subpackage facades
   (`jacopy.research`, `jacopy.packages.<name>`,
   `jacopy.central.objects`, `jacopy.central.tangent`, `jacopy.proof`,
   `jacopy.display`) — each package's `__all__`.
4. **Internal:** every other module path and every `_`-prefixed name.

Same name, different object (also listed in the docstring):
`jacopy.cite` is `proof.theorems.cite` (not `bibliography.cite`);
`jacopy.prove` is `proof.search.prove` (not `proof.result.prove`);
`jacopy.Zero` is the expression zero (not `research.ZeroOperator`);
`jacopy.normalize` is `proof.normalize` (not
`algorithms.rewrite_to_fixpoint`); `Metric`/`metric` are the central
metric atom (not the metric-affine context).

## 8. Known limits (2026-10-02)

* **AoG domain** — an `AgreementOnGenerators` identity can still be
  cited outside its own algebra (audit cases cr7/p06, cr8/p02). The
  five tests that describe the correct behaviour are strict `xfail`
  in `tests/test_audit_0b00e1b_p1_core_tur4.py`; the fix has its own
  lane.
* **Legacy and unreplayed theorem chains** — several library theorems
  (for example algebroid theorems and `poisson_jacobi`) are
  requirements-derived but their chains do not replay into the claim.
  They carry an `unreplayed` requirement, are citable only with
  `allow_legacy=True`, and pass the marker on to every citing result.
* **Layering** — the 29 deferred upward imports and the package
  cycles of section 1 (audit T2-2); no layering test yet (*planned*).
* **Large modules** — eight modules exceed 1,000 lines
  (`generalized/courant_axioms.py` 1,789, `display/latex.py` 1,659,
  `central/calculus/bracket_calculus.py` 1,287, `drinfeld/twist.py`
  1,190, `central/algebroid/theorems.py` 1,081,
  `drinfeld/tilde_calculus.py` 1,078, `poisson/tilde.py` 1,059,
  `poisson/koszul_jacobi.py` 1,031). Splitting them (audit T2-11) is
  *planned*.
* **Private imports** — 80 `from jacopy… import _name` imports remain
  inside the library, 28 of them across subpackages; the notebooks use
  none.
* **Research results** — `AxiomSuite` reports its own `CheckResult`
  (`CLOSED` / `RESIDUAL` / `FAILED`), not a `ProofResult` with
  requirements (audit T2-10).
* **Web interface** — the course guideline's page-based interface
  (item 3) is *planned*; today jacopy is a Python library with example
  notebooks.
* **Notebook smoke run** — all four notebooks run to the end
  (2026-10-02, `main` at `8b46a5d`). `algebroid_declarations_demo.ipynb`
  cites the anchor-morphism record explicitly with `allow_legacy=True`
  and shows its `unreplayed` requirement (M1-5);
  `bracket_twist_research_interface.ipynb` closes D.19 at p = 3
  (Claim 6) again since operator sums inherit alternation (M2-1
  follow-up).
* Several docstrings refer to `ROADMAP.md` and
  to "PDF item N" (the Math 595 guideline); neither file is part of
  the repository.
