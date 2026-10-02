# jacopy

jacopy is a symbolic library for graded algebra, bracket calculus and
differential geometry — on the tangent bundle `TM` and on algebroids
`E` — in which every manipulation is recorded as a step-by-step proof.
A closed identity comes with its proof chain, the rule behind each step
(definition, declared axiom or cited theorem, with its literature
source) and the list of assumptions it depends on; an identity that
does not close reports the residual that is left. An optional model
oracle checks closed identities numerically in random coordinate
models. jacopy is pure Python with no required dependencies.

Coverage today: Cartan calculus (`d`, `L`, `ι`), Lie and
Schouten–Nijenhuis brackets, algebroids with declared axioms
(Jacobiator, Derivator, Predator, locality), metric-affine geometry
(torsion, curvature, non-metricity, Bianchi, Cartan structure
equations, Koszul formula, E-connections), Poisson / symplectic /
Nambu–Poisson geometry with the Koszul bracket and tilde calculus,
Drinfel'd doubles and twists, Courant algebroids and generalized
geometry, and a research interface for user-defined brackets.

## Installation

jacopy is installed from source (it is not on PyPI). Python 3.10 or
newer.

```sh
git clone https://github.com/oselcukk/JacoPy.v.3.git
cd JacoPy.v.3
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[test]"
pytest -q                          # the fast test suite
```

Optional extras (from `pyproject.toml`):

| Extra | Installs | For |
|---|---|---|
| `test` | pytest | the test suite |
| `oracle` | sympy | the model oracle (`jacopy.oracle`, `pytest --oracle=…`) |
| `rich` | rich | coloured proof trees in the terminal (plain text without it) |
| `docs` | ipykernel | a Jupyter kernel for the example notebooks |
| `dev` | all of the above | development (`make setup` creates `.venv` with it) |

## Quick start

Cartan's formula `L_X ω = ι_X dω + d ι_X ω` on a 1-form, evaluated on a
vector field `Y`, proved from the definitions of `d`, `L` and `ι`:

```python
import jacopy
from jacopy.central.tangent import tangent_engine

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

lhs = jacopy.pairing(L_X(omega), Y)
rhs = jacopy.pairing(i_X(d(omega)), Y) + jacopy.pairing(d(i_X(omega)), Y)

chain = jacopy.show_equal(lhs, rhs, registry=reg, engine=tangent_engine(registry=reg))
print(f"closed in {len(chain.steps)} steps")
print(jacopy.to_latex(lhs), "=", jacopy.to_latex(rhs))
jacopy.print_chain(chain)   # each step with the rule that justifies it
```

Output (first lines):

```
closed in 6 steps
\langle \mathcal{L}_{X}\!\left(omega\right),\, Y \rangle = \langle \iota_{X}\!\left(d\!\left(omega\right)\right),\, Y \rangle + \langle d\!\left(\iota_{X}\!\left(omega\right)\right),\, Y \rangle
Proof (6 steps)
├── [intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = ...
```

A false identity is refused and the residual is reported:

```python
import jacopy
from jacopy.central.tangent import tangent_engine

reg = jacopy.PropertyRegistry()
X, Y = jacopy.vector_fields("X Y")
(omega,) = jacopy.forms("omega", degree=1)
d, L_X, i_X = jacopy.exterior_d(), jacopy.lie_derivative(X), jacopy.interior(X)

try:
    jacopy.show_equal(jacopy.pairing(L_X(omega), Y), jacopy.pairing(i_X(d(omega)), Y),
                      registry=reg, engine=tangent_engine(registry=reg))
except jacopy.ProofFailure as failure:
    print("residual:", failure.residual)     # residual: Y(⟨omega, X⟩)
```

The example notebooks in `examples/` go further:
`proof_system_demo.ipynb` (proof chains, results, theorems),
`algebroid_declarations_demo.ipynb` (algebroids and declared axioms),
`bracket_twist_walkthrough.ipynb` and
`bracket_twist_research_interface.ipynb` (Drinfel'd doubles, twists and
the research interface).

## Packages and the course guideline (Math 595)

The project follows the Math 595 "JacoPy" guideline. Where each item
lives today:

| Guideline item | Where | Status |
|---|---|---|
| 1. English, integrated with LaTeX | `jacopy.display` (LaTeX, proof transcripts, standalone documents), `jacopy.bibliography` (APA 7 sources) | done |
| 2. Coherent definitions of every object and operation | one canonical `Definition` per operator; everything else is a proved theorem | done |
| 3. Page-based interface (Dorfman/Courant blocks, proof buttons) | — | *planned* (today: Python API and notebooks) |
| 4, 15. Research interface | `jacopy.research` (`assemble_engine`, `AxiomSuite`, `BlockMatrix`, `register_structure_kind`) | available, evolving |
| 5. Compatible packages | all packages share one expression tree, registry and engine model | partial: cross-package use is tested in places, no documented combined workflow yet |
| 6. Two-fold packages (`TM` and `E`) | `jacopy.central` (`tangent` and `algebroid`), E-versions in `metric_affine` | done for the central code and metric-affine |
| 7f, 8. Central code: basic objects | `jacopy.central.objects`, `jacopy.central.calculus` | done |
| 9. Tangent-bundle case | `jacopy.central.tangent` | done |
| 10. Algebroid case | `jacopy.central.algebroid` | done |
| 7g, 11. Metric-affine geometry | `jacopy.packages.metric_affine` | done |
| 7h, 12. Symplectic, Poisson, Nambu–Poisson | `jacopy.packages.poisson` | done |
| 7a, 13. Calculus on algebroids, Drinfel'd doubles, twists | `jacopy.packages.drinfeld` | done |
| 7b, 14. Generalized geometry | `jacopy.packages.generalized` | done |
| 7d. Exceptional generalized geometry | `exceptional_double`, `exceptional_rotation` in `jacopy.packages.generalized` | first examples; full package *planned* |
| 7i, 7j. Conformal/projective geometry, various tensors | — | *planned* |
| 16. Euler–Lagrange, SUGRA, dualities, spinors, … | — | *planned* |

"Done" means implemented and covered by tests; the known limits are
listed in `docs/ARCHITECTURE.md`, section 8.

## Proof trust and the model oracle

A closed result is shown *under its assumptions*:
`jacopy.proof.result.prove(engine, lhs, rhs)` returns a `ProofResult`
whose `requires` lists the declared axioms and structures that fired,
the property-registry answers the steps relied on, and markers for
instance proofs or unverified citations. A theorem can be cited into
another proof only where the same requirements hold. Steps are minted
by the library's own producers, and a theorem's chain is replayed
against its claim. Details: `docs/ARCHITECTURE.md`, section 4.

The model oracle (`pip install -e ".[oracle]"`) is an independent
falsifier: it evaluates both sides of a closed identity in random
concrete coordinate models. `AGREE` means "not refuted", never
"proved". Turn it on per call (`show_equal(..., oracle="warn")`), with
`JACOPY_ORACLE=warn|strict`, or for the test suite with
`pytest --oracle=strict`.

## Documentation

* `docs/ARCHITECTURE.md` — layers, proof flow, trust model, oracle,
  extension points, known limits.
* `docs/TESTING.md` — the fast suite, slow suites, the oracle, notebook
  and wheel checks.
* `docs/CITATIONS.md` — which code label was checked against which
  page of which paper.
* `CHANGELOG.md` — changes since `0.0.1`.

## License

jacopy is **source-available, not open source**: you may read, run and
cite it for personal, educational or research use; modification for
anything beyond local experimentation, redistribution and commercial
use need written permission. See [LICENSE](LICENSE).

## Citing

Please cite jacopy using the metadata in [CITATION.cff](CITATION.cff).
