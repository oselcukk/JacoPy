# Common parameters and settings

This page collects the keyword parameters and environment variables that recur across the
public API, with their defaults and their meaning. Each table names the functions that accept
the parameter; the linked how-to page shows it in use, and the
[API reference](api/index.md) documents every function in full. All defaults on this page
are read from the source of the current version.

## Objects and the registry

| Parameter | Accepted by | Default | Meaning | See |
|---|---|---|---|---|
| `registry=` | `jacopy.functions` (required); almost every engine builder, proof function and theorem builder | `None` (where optional) | the `PropertyRegistry` that holds the declarations (degrees, closedness, axioms). Pass the same registry to the object factories, the engine and the proof call | [Objects](../howto/objects.md) |
| `degree=` | `jacopy.forms`, `jacopy.p_vectors` (required); `jacopy.functions` | `0` for functions | the form or multivector degree; an integer or a symbolic degree | [Objects](../howto/objects.md) |
| `bundle=` | `jacopy.vector_fields`, `forms`, `p_vectors`, `bivector`, `tensors`, `metric`, `connection`, `frame`, `coframe` | `None` (the tangent bundle) | the bundle the object lives on, for example `E.bundle` of an algebroid | [Algebroids](../howto/algebroids.md) |
| `dim=` | `jacopy.tangent_bundle`, `jacopy.Bundle` | `None` (symbolic) | a fixed rank, needed only where a dimension enters a formula | [Objects](../howto/objects.md) |
| `name=` | `jacopy.metric` (`"g"`), `jacopy.connection` (`"∇"`), `jacopy.frame` and `coframe` (`"e"`) | as shown | the printed symbol | [Objects](../howto/objects.md) |
| `strict_axioms_only=` | `jacopy.PropertyRegistry(...)`; `reg.set_strict(...)` | `False` | when true, declarations with `DERIVED` provenance are invisible, so only axioms are used | [API](api/objects-calculus.md) |
| `reg.scope()` | context manager on `PropertyRegistry` | | every declaration made inside the block is rolled back at the end | [Objects](../howto/objects.md) |
| `reg.axioms([...])` | context manager on `PropertyRegistry` | | inside the block only the listed property types are visible | [Objects](../howto/objects.md) |
| `declare=` | `jacopy.central.algebroid.algebroid`; `poisson_structure`, `nambu_structure` | `()` | the axioms the structure satisfies, as atomic names (`DECLARATIONS`) or level names (`LEVELS`, for example `"leibniz"` = right Leibniz + Jacobi) | [Algebroids](../howto/algebroids.md), [Poisson](../howto/poisson.md) |
| `anchor_name=` | `algebroid` | `"ρ"` | the printed name of the anchor | [Algebroids](../howto/algebroids.md) |

## Engines

| Parameter | Accepted by | Default | Meaning | See |
|---|---|---|---|---|
| `mode=` | `tangent_engine`, `algebroid_engine`, `default_engine`, `ExpansionEngine`, `poisson_engine`, `metric_affine_engine`, `e_connection_engine` | `"efficient"` | `"efficient"`: a theorem cited into the engine is one step. `"foundational"`: the step also carries the theorem's own proof as sub-steps (`jacopy.proof.MODES`) | [Choosing a proof strategy](../howto/proof-strategies.md) |
| `holonomic_frames=` | `tangent_engine`, `metric_affine_engine` | `()` | frames whose vectors commute, $[e_a,e_b]=0$ | [Running proofs](../howto/running-proofs.md) |
| `projectors=` | `algebroid_engine`, `e_connection_engine` | `()` | projector rules made from `locality_projector` | [Running proofs](../howto/running-proofs.md) |
| `compatible=`, `torsion_free=`, `decompositions=` | `metric_affine_engine` | `()` | `(connection, metric)` pairs declared metric-compatible ($\nabla g=0$), connections declared torsion-free, and `(connection, frame)` pairs that declare frame completeness | [Metric-affine geometry](../howto/metric-affine.md) |
| `declare_fi=`, `declare_poisson=` | engine builders and theorem builders of `jacopy.packages` | `True` in most builders | switch on the fundamental identity of a Nambu structure, or the Poisson condition $[\pi,\pi]=0$; with `False` the proofs that need it do not close | [Poisson](../howto/poisson.md), [Drinfel'd doubles](../howto/drinfeld.md) |
| `structures=`, `declare_fi=`, `extra=` | `jacopy.research.assemble_engine` | `()`, `False`, `()` | the structures whose rules are assembled, the fundamental identity, extra rules | [Your own structure](../howto/your-own-structure.md) |

## Proving

| Parameter | Accepted by | Default | Meaning | See |
|---|---|---|---|---|
| `engine=` | `jacopy.show_equal`, `jacopy.prove`, every `Strategy.prove`, `prove_equivalence`, `prove_jacobi`, `prove_operator_equation`, `diagnose` | `None` (`default_engine()`, the structural rule only) | the rules a proof may use | [Running proofs](../howto/running-proofs.md) |
| `strategy=` | `jacopy.show_equal`, `prove_equivalence`, `prove_jacobi` | `None` (`ExpandAndSimplify()`) | the strategy object that orders the rules | [Choosing a proof strategy](../howto/proof-strategies.md) |
| `prefer=` | `jacopy.prove`; `SearchStrategy` | `None` (no search); `"shortest"` on `SearchStrategy` | `"shortest"`, `"readable"` or `"elementary"` (`jacopy.proof.SCORERS`); any other value raises `ValueError` | [Choosing a proof strategy](../howto/proof-strategies.md) |
| `max_depth=` | `SearchStrategy`; `jacopy.prove` with `prefer` | `12` | the largest number of moves in a proof | [Choosing a proof strategy](../howto/proof-strategies.md#bounding-the-search) |
| `max_states=` | as above | `5000` | distinct expressions explored before the beam fallback takes over | as above |
| `beam_width=` | as above | `32` | candidates kept per level by the beam fallback | as above |
| `max_solutions=` | as above | `16` | proofs collected before the best is returned | as above |
| `sub_strategy=` | `AgreementOnGenerators`, `prove_operator_equation` | `None` (`ExpandAndSimplify()`) | the strategy used on each generator | [Choosing a proof strategy](../howto/proof-strategies.md) |
| `max_steps=` | `ExpandAndSimplify().prove` | `1024` | rule applications per expansion pass; exhaustion raises `RuntimeError` | [Choosing a proof strategy](../howto/proof-strategies.md#the-strategy-classes) |
| `max_steps=` | `jacopy.proof.result.prove` | `1024` | rule applications for both sides together; exhaustion gives the status `BUDGET` | [Running proofs](../howto/running-proofs.md#reading-the-result) |
| `max_steps=` | `ExpansionEngine.expand`, `jacopy.normalize` | `1024` | rule applications per expansion; `expand` raises `RuntimeError` when it runs out, `normalize` never raises and reports `stopped_by` | [Running proofs](../howto/running-proofs.md) |
| `max_steps=`, `max_rounds=` | theorem builders of `jacopy.packages` and `jacopy.research.AxiomSuite` | builder-specific, for example `20000`, `30000`, `60000` | the budget of the expansion inside the builder; raise it only if a builder stops on its budget | [Poisson](../howto/poisson.md), [Generalized geometry](../howto/generalized-geometry.md) |
| `rounds=`, `passes=`, `inner_rounds=`, `record=`, `stop_when=` | `jacopy.normalize` | `10`, `("product_rule", "simplify")`, `None`, `False`, `None` | outer rounds, the passes run after each expansion, an optional inner fixed point, whether to keep the steps, an early-stop predicate | [Running proofs](../howto/running-proofs.md) |
| `generality=` | `jacopy.proof.result.prove`, `jacopy.Theorem` | `"generic-function"` | one of `jacopy.proof.GENERALITY_TAGS`: `"operator-level"`, `"generic-function"`, `"symbolic-p"`, `"instance"` | [Running proofs](../howto/running-proofs.md) |
| `simplify_normal_forms=` | `jacopy.proof.result.prove` | `True` | run the simplifier on each side's normal form before comparing | [Running proofs](../howto/running-proofs.md) |

Two cases are easy to miss. `jacopy.prove` without `prefer` runs `ExpandAndSimplify` and
ignores every other keyword, including the search options and `oracle=`. With `prefer` it
passes the extra keywords to `SearchStrategy`, which rejects `oracle=` with `TypeError`. Use
`jacopy.show_equal(..., oracle=...)` or the `oracle_mode` context manager instead.

## Theorems and citation

| Parameter | Accepted by | Default | Meaning | See |
|---|---|---|---|---|
| `*names` | `jacopy.cite(engine, book, *names)` | | the theorems to add to the engine as rules | [Running proofs](../howto/running-proofs.md) |
| `reverse=` | `jacopy.cite` | `False` | add the theorem as the rule rhs $\to$ lhs instead of lhs $\to$ rhs | [Running proofs](../howto/running-proofs.md) |
| `allow_legacy=` | `jacopy.cite`, `check_citation` | `False` | allow citing a record whose chain is not replayed; the citing result carries the "unverified citation" marker | [Trust model](../explanation/trust-model.md) |
| `unverified=` | `TheoremBook.add`, `TheoremBook.replace` | `False` | store the theorem as an explicit unverified assumption | [Trust model](../explanation/trust-model.md) |

## Display, LaTeX and citations

| Parameter | Accepted by | Default | Meaning | See |
|---|---|---|---|---|
| `verbosity=` | `chain_to_ascii`, `step_to_ascii`, `jacopy.print_chain`, `ProofChain.format`, the collapsible Jupyter views | `"full"` | `"full"`, `"summary"` (no justification) or `"compact"` (rule and classification) | [Output](../howto/output-and-latex.md#rendering-options) |
| `max_depth=` | text, terminal and Jupyter renderers; LaTeX renderers | `64`; `0` for LaTeX | levels of sub-steps shown | as above |
| `max_steps=` | `chain_to_latex`, `theorem_to_latex`, `jacopy.display_chain`, `jacopy.display_theorem`, the document builders | `None`; `40` for `display_theorem` | show only the first steps, then a "more steps" row | as above |
| `title=` | `jacopy.print_chain`, `render_chain`, `display_chain_collapsible` | `True` | print a heading line above the tree | as above |
| `console=` | `jacopy.print_chain`, `print_step` | `None` (a new `rich` console) | the `rich` console to print to; without the optional `rich` package the plain-text form is printed | [Installation](../installation.md) |
| `width=` | `chain_to_latex`, `step_to_latex` | `62` | the approximate line width, in visible units, at which long formulas are broken between summands | as above |
| `cite_style=` | `chain_to_latex`, `step_to_latex`, `theorem_to_latex` | `"apa"` | `"apa"` (in-text citation) or `"biblatex"` (`\parencites`) | as above |
| `references=` | `chain_to_ascii`, `render_chain` | `False` | append the reference list of the cited works | as above |
| `references=` | `jacopy.theorem_to_latex_document`, `chain_to_latex_document` | `"apa"` | `"apa"`, `"biblatex"` (embedded `.bib`; compile with biber) or `None` | as above |
| `with_proof=` | `theorem_to_latex`, `jacopy.theorem_to_latex_document`, `jacopy.display_theorem` | `True` | include the proof transcript | as above |
| `author=`, `title=`, `preamble_extras=` | the document builders | `""` | document metadata and extra preamble lines | as above |
| `node_distance=` | `chain_to_tikz`, `chain_to_tikz_document` | `"1.2cm"` | the spacing of the TikZ nodes | as above |
| `style=` | `jacopy.bibliography.in_text`, `apa_reference`, `references_block` | `"plain"` | `"plain"`, `"markdown"` or `"latex"` | as above |
| `locator=`, `note=` | `jacopy.bibliography.cite` | `""` | the part of the work cited, for example `"Definition 3.10"`, and a free note | as above |

## The model oracle

| Setting | Where | Default | Meaning | See |
|---|---|---|---|---|
| `oracle=` | `jacopy.show_equal`, `jacopy.proof.result.prove` | `None` (current mode) | `"off"`, `"warn"` or `"strict"` for this call | [Oracle](../howto/oracle.md#settings) |
| `oracle_mode(mode)` | `jacopy.oracle.hook` | | the mode for a block of code | as above |
| `samples=`, `seed=`, `timeout=` | `jacopy.oracle.check_equal` (and `check_chain`) | `2`, `0`, `20.0` | models per check, base seed, seconds allowed | as above |
| `--oracle=off\|warn\|strict` | pytest, in the JacoPy test suite | `off` (or `JACOPY_ORACLE`) | run the oracle on every closed equation | [Testing](../development/testing.md) |
| `--oracle-samples`, `--oracle-seed`, `--oracle-report` | pytest, in the JacoPy test suite | `2`, `0`, `.oracle/report.json` | models per closure, base seed, JSON report path | as above |

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `JACOPY_ORACLE` | `off` | default oracle mode: `off`, `warn` or `strict`. `0`, `false`, `no`, `none` and the empty string also mean off; any other value warns once and means off. Read at every closed equation, so it can be changed while a program runs |
| `JACOPY_ORACLE_SAMPLES` | `2` | models per closed equation; a value that is not a positive integer warns once and leaves the oracle off |
| `JACOPY_ORACLE_SEED` | `0` | base seed for the models; an invalid value is replaced by `0` |

JacoPy reads no other environment variables. The oracle needs the optional `oracle` extra
(SymPy); with the oracle off, SymPy is not imported.
