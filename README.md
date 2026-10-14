# JacoPy

**Graded algebra, bracket calculus and differential geometry in Python,
with a step-by-step proof for every result.**

[![tests](https://github.com/oselcukk/JacoPy/actions/workflows/tests.yml/badge.svg)](https://github.com/oselcukk/JacoPy/actions/workflows/tests.yml)
[![docs](https://github.com/oselcukk/JacoPy/actions/workflows/docs.yml/badge.svg)](https://oselcukk.github.io/JacoPy/)
[![PyPI](https://img.shields.io/pypi/v/jacopy)](https://pypi.org/project/jacopy/)
[![Python 3.10-3.14](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue)](https://oselcukk.github.io/JacoPy/installation.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23361717.svg)](https://doi.org/10.5281/zenodo.23361717)
[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-blue)](LICENSE)

JacoPy is a symbolic library for graded algebra, bracket calculus and
differential geometry, on the tangent bundle `TM` and on algebroids `E`,
in which every manipulation is recorded as a step-by-step proof. A
closed identity comes with its proof chain, the rule behind each step
(a definition, a declared axiom or a cited theorem, with its literature
source) and the list of assumptions it depends on. An identity that does
not close reports the residual that is left. An optional model oracle
checks closed identities numerically in random coordinate models.
JacoPy is pure Python with no required dependencies.

JacoPy is alpha software (version 0.1.0): the public API may still
change between minor versions, and every change is recorded in the
[changelog](CHANGELOG.md).

## Installation

JacoPy needs Python 3.10 or newer and has no required dependencies:

```sh
pip install jacopy
```

Optional extras: `oracle` (SymPy, for the model oracle), `rich`
(colored proof trees in the terminal), `test` (pytest) and `dev` (all
of these), for example `pip install "jacopy[oracle]"`. See the
[installation guide](https://oselcukk.github.io/JacoPy/installation.html)
for details and the
[development guide](https://oselcukk.github.io/JacoPy/development/index.html)
for an editable checkout.

## Quick example

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

# A false identity is refused, and the residual is reported.
try:
    jacopy.show_equal(lhs, jacopy.pairing(i_X(d(omega)), Y),
                      registry=reg, engine=tangent_engine(registry=reg))
except jacopy.ProofFailure as failure:
    print("residual:", failure.residual)
```

Output (the middle four proof steps are omitted here):

```text
closed in 6 steps
\langle \mathcal{L}_{X}\!\left(\omega\right),\, Y \rangle = \langle \iota_{X}\!\left(d\!\left(\omega\right)\right),\, Y \rangle + \langle d\!\left(\iota_{X}\!\left(\omega\right)\right),\, Y \rangle
Proof (6 steps)
├── [intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = 
│   ρ(X)(ω(Y…)) − Σ ω(…,[X,Y_i],…)] (definition) ⟨L_X(omega), Y⟩ → X(⟨omega, Y⟩)
│   - ⟨omega, [X,Y]_VF⟩ , apply definition: intrinsic L (Cartan-TM): L_X f = 
│   ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = ρ(X)(ω(Y…)) − Σ ω(…,[X,Y_i],…)
...
└── [simplify] (X(⟨omega, Y⟩) - ⟨omega, [X,Y]_VF⟩) - ((X(⟨omega, Y⟩) - Y(⟨omega,
    X⟩) - ⟨omega, [X,Y]_VF⟩) + Y(⟨omega, X⟩)) → 0 , canonical-form pipeline
residual: Y(⟨omega, X⟩)
```

The notebooks in [`examples/`](examples/) go further: proof chains,
results and theorems; algebroids and declared axioms; Drinfel'd doubles,
twists and the research interface.

## Features

- **Cartan calculus** on `TM` and on algebroids: `d`, `L` and `ι`, with
  Lie and Schouten-Nijenhuis brackets.
- **Algebroids with declared axioms**: Jacobiator, Derivator, Predator
  and locality, so that a proof states exactly which axioms it used.
- **Metric-affine geometry**: torsion, curvature, non-metricity, the
  Bianchi identities, the Cartan structure equations, the Koszul
  formula and E-connections.
- **Poisson, symplectic and Nambu-Poisson geometry**, with the Koszul
  bracket and tilde calculus.
- **Drinfel'd doubles and twists, Courant algebroids and generalized
  geometry.**
- **A research interface** (`jacopy.research`) for user-defined
  brackets: assemble an engine and check the bracket axioms.
- **Proofs you can inspect and reuse**: each step names its rule and
  source; `jacopy.proof.result.prove` returns a `ProofResult` whose
  `requires` lists the axioms, structures and registry facts the proof
  relied on, and a proved theorem can be cited into another proof only
  where the same requirements hold.
- **Output** as plain text, LaTeX (including standalone documents),
  HTML for Jupyter, and colored terminal trees, with APA 7 citations.
- **A model oracle** (`jacopy.oracle`) that evaluates both sides of a
  closed identity in random coordinate models. `AGREE` means "not
  refuted", never "proved".

## Documentation

The documentation is at **https://oselcukk.github.io/JacoPy/**. It
contains tutorials, how-to guides, explanations of the architecture and
the trust model, the API reference, and the development guides
(testing, citations, changelog).

## Citing JacoPy

If you use JacoPy in your research, please cite it. The metadata is in
[CITATION.cff](CITATION.cff) (GitHub shows it under "Cite this
repository"). Every release is archived on Zenodo; the DOI
[10.5281/zenodo.23361717](https://doi.org/10.5281/zenodo.23361717)
always points to the latest version. In BibTeX:

```bibtex
@software{Selcuk_JacoPy,
  author  = {Sel{\c{c}}uk, O{\u{g}}uzhan},
  title   = {{JacoPy}},
  version = {0.1.0},
  year    = {2026},
  doi     = {10.5281/zenodo.23361717},
  url     = {https://github.com/oselcukk/JacoPy},
  license = {BSD-3-Clause}
}
```

## Acknowledgments

JacoPy builds on the work of others:

- The model oracle uses [SymPy](https://www.sympy.org) to evaluate
  expressions in coordinate models: A. Meurer et al., "SymPy: symbolic
  computing in Python", *PeerJ Computer Science* 3:e103 (2017),
  https://doi.org/10.7717/peerj-cs.103.
- The definitions, axioms and theorems that JacoPy's rules implement are
  drawn from the mathematical literature on Lie and Courant algebroids,
  derived brackets, metric-affine and generalized geometry, and
  Drinfel'd doubles. Each rule cites its source, and the full list is on
  the [bibliography page](https://oselcukk.github.io/JacoPy/reference/bibliography.html).

## Contributing

Bug reports, mathematical corrections and pull requests are welcome.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Ask questions in
[GitHub Discussions](https://github.com/oselcukk/JacoPy/discussions),
and report security problems as described in [SECURITY.md](SECURITY.md).

## License

JacoPy is distributed under the [BSD 3-Clause License](LICENSE).
Copyright (c) 2026, Oğuzhan Selçuk.
