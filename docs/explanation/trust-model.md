# Trust model

Why should a computer-generated proof be trusted? This page explains
what a JacoPy result means and which mechanisms keep it honest. The
answer has three parts: every result is presented **together with the
assumptions it rests on**; using a result in another context is
**rejected by default** unless its hypotheses hold there; and an
**independent numerical checker**, the model oracle, tests closed
identities on concrete examples.

This is not the guarantee of a proof assistant with a logical kernel
(such as Lean or Rocq). JacoPy's proofs rest on rewrite rules written in
Python; its position between computer algebra and proof assistants is
discussed in [Related tools](related-tools.md).

## What a result means

The outcome of a proof attempt is one of four states
(`jacopy.proof.result.ProofResult.status`):

| State | Meaning | Reading for a mathematician |
|---|---|---|
| `CLOSED` | With the given rules, both sides reduced to the same normal form. | "$A=B$ under these assumptions." The result is always shown together with its list of assumptions. |
| `RESIDUAL` | The reduction finished, but the difference is not zero; the remaining term is shown. | "No proof found." This is **not a refutation**: there is no `DISPROVED` state. |
| `BUDGET` | The step budget was exhausted (1,024 steps by default; raised for large proofs). | The computation stopped before it finished. |
| `INVALID` | The proof record is inconsistent. | The result is not used. |

**Honest failure.** When a proof does not close, JacoPy does not guess
and does not claim falsity; it reports the residual. In the example
below, the term $d\iota_X\omega$ is deliberately left out of Cartan's
formula, and the residual is exactly the missing term
$\langle d\iota_X\omega,Y\rangle=Y(\langle\omega,X\rangle)$:

```python
import jacopy
from jacopy.central.tangent import tangent_engine
from jacopy.proof.result import prove

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

lhs = jacopy.pairing(L_X(omega), Y)
wrong = jacopy.pairing(i_X(d(omega)), Y)       # the term d ι_X ω is missing

res = prove(tangent_engine(registry=reg), lhs, wrong, registry=reg)
print(res.status)
print(res.residual)
```

```text
RESIDUAL
Y(⟨omega, X⟩)
```

A large share of the test suite consists of such honest-failure tests:
they check that a claim with a wrong sign or a missing assumption does
**not** close.

**Scope of the proofs.** Proofs work on abstract terms and are
coordinate-free, but they are built for general sections, general forms
and selected concrete degrees (mostly $p=1,2$, sometimes up to 5). They
are not inductive proofs "for every $p$" or "for every dimension"; see
[Limitations](limitations.md).

## Assumption tracking: `requires`

Every result lists what it rests on. Each entry of
`ProofResult.requires` (and of `Theorem.requires`) is an `Assumption`
of one of the kinds in `jacopy.proof.result.ASSUMPTION_KINDS`:

| Kind | Meaning | Mathematical analogy |
|---|---|---|
| `declared` | A declared axiom of a structure that actually fired (owner, number of instances, the rule's structural key). | "we used the Jacobi identity" |
| `structure` | The structure object those axioms belong to. | "let $E$ be a Lie algebroid" |
| `registry` | A registry answer the steps relied on ("$x$ is `Scalar`", "$p$ has `Graded(0)`", "nothing declared", …). | "let $c$ be constant" |
| `scope` | An instance proof (generality `instance`); never upgraded to a general one. | "for $p=2$" |
| `textual` | A prose entry (`from_axioms`) that no step accounts for: kept visible, but not a verification input. | an assumption in a footnote |
| `legacy` | Recorded but not structurally verified (a step whose rule has no role, an unverified citation, a chain that does not prove its claim). | "the source says it is proved" |
| `unreplayed` | The requirements were derived, but the chain does not replay into $\text{lhs}=\text{rhs}$. | a lemma that cannot be checked line by line |

**Rule roles.** A rule's `role` decides how a fired step is classified:
`definition` produces no assumption; `assumption` (a declared axiom)
produces `declared` and `structure` entries; `theorem` (a citation)
folds in the requirements of the cited theorem, transitively. A rule
class written outside the library counts as an assumption by default,
whatever role it claims. The role of each of the 194 rule classes in the
library (144 definitions, 44 assumptions, 6 theorems) is recorded in
`tests/rule_roles_inventory.json` and checked by the test suite.

**Declarations.** In a general algebroid the bracket is only
$\mathbb{R}$-bilinear; every further property (right or left Leibniz
rule, anchor morphism, Jacobi identity, antisymmetry, metric
invariance, …) must be **declared**. Without a declaration the
corresponding rule does not exist, so the same proof closes with the
declaration and fails without it. Ready-made *levels* (`leibniz`,
`lie`, `courant`, …) bundle declarations and deliberately leave out
axioms that can be derived. For example, the `leibniz` level declares
right Leibniz and Jacobi, but not the anchor morphism, because that is a
theorem:

```python
from jacopy.central.algebroid import algebroid
from jacopy.central.algebroid.theorems import prove_anchor_morphism
from jacopy.central.objects import Bundle, functions

(f,) = jacopy.functions("f", registry=reg)
E_L = algebroid("E", Bundle("E"), declare=("leibniz",))    # right Leibniz + Jacobi
u, v = E_L.sections("u v")
chain, am = prove_anchor_morphism(E_L, u, v, f, registry=reg)
print(am.statement)
print(sorted({a.kind for a in am.requires}))

E0 = algebroid("E0", Bundle("E0"), declare=())             # nothing declared
try:
    prove_anchor_morphism(E0, *E0.sections("a b"), f, registry=reg)
except jacopy.ProofFailure as exc:
    print("ProofFailure:", exc)
```

```text
ρ([u,v]) = [ρ(u), ρ(v)] on E (every Leibniz algebroid is pre-Leibniz)
['declared', 'registry', 'structure', 'unreplayed']
ProofFailure: anchor morphism is not derivable here: the proof needs the declarations ['right-leibniz', 'jacobi'] which Algebroid('E0', bundle=Bundle('E0')) does not make
```

On the undeclared $E_0$ the library names the missing declarations
instead of producing a proof.

**The Scalar contract.** `Scalar` means a real constant. There is a
single predicate, `jacopy.central.calculus.scalars.is_real_constant`;
the engine, `product_rule`, `sort_product`, `degree_of`, `kind_of`,
`AgreementOnGenerators`, the diagnostics and the model oracle all call
it. A declaration that contradicts the contract (`Scalar` together with
`Graded(k ≠ 0)`, `NonCommuting` or `AntiCommuting`) raises
`ScalarContractError`. The registry facts the predicate read become
`registry` requirements of the step.

## Default reject: citing a theorem elsewhere

A proved result enters another proof only through a citation, and
`jacopy.proof.theorems.check_citation` refuses the citation unless:

* every `declared` / `structure` requirement is met by a structure of
  the same name in the citing engine with the same or stronger
  declarations, and the same licensing rule is registered there;
* every `registry` requirement is answered the same way by the citing
  registry (when the citing registry is unknown, a registry-dependent
  theorem is not citable);
* the record is neither `legacy` nor `unreplayed`; such a record is
  citable only with an explicit `allow_legacy=True`, and the citing
  result then carries the marker.

In case of doubt the answer is "no". This mechanism exists so that a
theorem proved in one context cannot close a false identity in
another. In the following example the Jacobi identity is proved in a
Lie algebroid and then offered to a weaker and to a stronger
structure:

```python
from jacopy.central.algebroid.engine import algebroid_engine
from jacopy.central.algebroid.operators import Jacobiator
from jacopy.proof.theorems import Theorem, check_citation

E = algebroid("E", Bundle("E"), declare=("lie",))
u, v, w = E.sections("u v w")
res = prove(algebroid_engine(E, registry=reg), Jacobiator("E", u, v, w), registry=reg)
thm = Theorem(name="jacobi_E", statement="J^E = 0", lhs=res.goal.lhs, rhs=res.goal.rhs,
              proof=res.chain, owner=E).with_structural_requires()

E_weak = algebroid("E", Bundle("E"), declare=("right-leibniz", "antisymmetric"))
E_strong = E.with_declarations("metric-invariance")
print(check_citation(thm, algebroid_engine(E_weak, registry=reg), registry=reg).ok)
print(check_citation(thm, algebroid_engine(E_strong, registry=reg), registry=reg))
```

```text
False
citable
```

The rejection message (not printed above) names each unmet requirement
and the structure that fails to provide it.

## Minting and replay

* **Minting.** Only the library's own producers (the engine, the
  normalization passes, the strategies) mark a `ProofStep` as minted
  (`jacopy.proof.step.is_minted`). A step built by hand through the
  public API is never minted, whatever metadata it carries. Minting
  certifies the **origin** of a step, not its mathematical
  correctness.
* **Replay.** `jacopy.proof.replay.chain_verdict` checks that a
  theorem's chain is connected and runs between the two sides of the
  claim. `Theorem.chain_replayed` is true only when the requirements
  were derived and no `unreplayed` or `legacy` entry remains.

Some library theorems are requirements-derived, but their intermediate
steps are hand-built (for example "agreement on generators" steps), so
the chain cannot be replayed mechanically from left to right. The
algebroid anchor-morphism theorem `am` from above is one of them: its record
carries `unreplayed`, so it is citable only on explicit request, and
every citing result inherits the marker:

```python
eng_L = algebroid_engine(E_L, registry=reg)
print(am.chain_replayed)
print(check_citation(am, eng_L, registry=reg).ok)
print(check_citation(am, eng_L, registry=reg, allow_legacy=True))
```

```text
False
False
citable
```

## The model oracle

The oracle is an independent falsifier. When the engine closes
$\text{lhs}=\text{rhs}$, it can evaluate both sides in random concrete
coordinate models and compare them: polynomial vector fields and forms
on $\mathbb{R}^n$ (coefficients derived from a seed), and algebroid
models $E=\mathbb{R}^n\times\mathbb{R}^r$ with a polynomial anchor and a
concrete bracket. It computes $d$, $\mathcal{L}_X$, $\iota_X$ and
$[X,Y]$ through coordinate formulas, independently of the rewrite
rules, and uses [SymPy](https://www.sympy.org) (Meurer et al., 2017)
for the polynomial arithmetic.

**Verdicts** (`jacopy.oracle.report.VERDICTS`):

| Verdict | Meaning |
|---|---|
| `AGREE` | Not refuted on the sampled models. This is **not a proof**: "it holds on these examples". |
| `DISAGREE` | The two sides differ on a concrete model: the claim is refuted. |
| `UNSUPPORTED` | A node the realizers do not cover (for example an abstract structure defined by the user), a dimension above the cap, … |
| `AMBIGUOUS` | The two readings of a `Product` disagree; no decision. |
| `ASSUMPTION_LEAK` | A declared Poisson property that the proof record does not use turns out to be needed: the equation fails in a non-Poisson counter-model. |

The oracle refutes the incomplete Cartan formula from the beginning of
this page and accepts the correct one:

```python
from jacopy.oracle import check_equal

right = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)
print(check_equal(lhs, right, registry=reg).verdict)
print(check_equal(lhs, wrong, registry=reg).verdict)
```

```text
AGREE
DISAGREE
```

The engine and the oracle reach the same conclusion by independent
routes: the engine shows symbolically *what is missing* (the residual),
the oracle shows numerically *that the claim is false*.

**Modes.** `JACOPY_ORACLE=off|warn|strict` (default `off`: nothing is
imported), the `oracle=` keyword of `show_equal` /
`jacopy.proof.result.prove`, or `jacopy.oracle.hook.oracle_mode`. In
`warn` mode a refutation emits `OracleWarning`; in `strict` mode it
raises `OracleDisagreement`. The test suite can run with
`pytest --oracle=warn|strict [--oracle-report PATH]`. The oracle needs
the optional `oracle` extra (SymPy).

**Coverage.** When the whole test suite was run with the oracle in
strict mode (commit `8b46a5d`, 2 October 2026), 1,042 closure events occurred: 662
`AGREE`, 374 `UNSUPPORTED`, and 6 deliberately exempted self-tests that
close a false identity on purpose; there were **no `DISAGREE` and no
`ASSUMPTION_LEAK` verdicts**. The oracle can thus test about two thirds
of the closures numerically; for the remaining third the correct
statement is "not tested", not "verified". The most frequent reasons for
`UNSUPPORTED` were an unowned assumption, an abstract derivation, the
Courant operator $\mathcal{D}$, the covariant derivative, and the
dimension cap.

## Quality process

* **Independent audit.** In September 2026 the code underwent an
  independent audit covering code, design and mathematics. Findings,
  including cases in which the engine could close a false identity
  through narrow paths, were fixed and pinned down by regression tests;
  the changes are recorded in the changelog.
* **Citation check.** The paper labels used by the code (equation,
  proposition and definition numbers) were checked against the cited
  works; labels that could not be verified are marked as such. See the
  [bibliography](../reference/bibliography.md).
* **Automated tests.** 122 test files run on every change on Python
  3.10–3.14, and again with the oracle in strict mode as a separate
  job; slow tests and the example notebooks run weekly.
* **Known open issue.** An identity proved by agreement on generators
  can still be cited outside its own algebra. Five tests that describe
  the correct behavior are marked as strict expected failures until the
  fix lands; see [Limitations](limitations.md).

## References

Meurer, A., Smith, C. P., Paprocki, M., Čertík, O., Kirpichev, S. B.,
Rocklin, M., Kumar, A., Ivanov, S., Moore, J. K., Singh, S.,
Rathnayake, T., Vig, S., Granger, B. E., Muller, R. P., Bonazzi, F.,
Gupta, H., Vats, S., Johansson, F., Pedregosa, F., … Scopatz, A.
(2017). SymPy: Symbolic computing in Python. *PeerJ Computer Science*,
*3*, e103. https://doi.org/10.7717/peerj-cs.103
