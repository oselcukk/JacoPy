# Limitations

This page answers the question "what can JacoPy not do?" as plainly as
possible. It covers limitations of the method, of the trust mechanisms,
of the mathematical scope, of the user side, and of the code base
itself. Planned work is collected in the [roadmap](roadmap.md).

## Methodological limitations

* **No proofs for general $p$.** Proofs are built for concrete degrees.
  $d^2=0$ and the Cartan formula are proved on $TM$ for $p\le5$, one
  separate proof per degree; there is no $d^2=0$ builder for symbolic
  $p$. The builder for $[\mathcal{L}_X,\iota_Y]=\iota_{[X,Y]}$ exists
  only on 1-forms, and the one for $\iota_X\iota_Y+\iota_Y\iota_X=0$
  only on 2-forms. In the packages the default test suite mostly runs
  $p=1,2$; claims for higher $p$ (for example $p=7$ for the Dorfman
  Jacobi identity) exist only in docstrings.
* **Operator-level equality is weak.** The engine works at the level of
  evaluation: for a 3-form $w$, $\iota_X\iota_Yw+\iota_Y\iota_Xw=0$ does
  not close unless it is evaluated on arguments. Proofs are therefore
  mostly built in the form "applied to a generic $f$ or $Y$"
  (generality `generic-function`).
* **The repair loop has limits.** Higher-degree proofs of $d^2=0$ and
  $[\mathcal{L},d]=0$ add Lie–Jacobi instances as citations; the engine
  does not generate the Jacobi identity internally. The default number
  of repairs is 3; $[\mathcal{L}_X,d]=0$ on 2-forms needs 8.
* **Proofs close on probe arguments.** In the concrete packages, vector
  components are proved by applying them to a generic function $h$,
  and form components by evaluating them on chosen slots; there is no
  form-valued version of these equations (for example, the $E$-Cartan
  equations are evaluated on a frame).
* **Undecidable signs.** If a parity cannot be decided, the commutator
  is not expanded, and a factor of undetermined degree raises an error
  in the product rule. Scalar homogeneity of the Lie bracket is proved
  only for integer constants.

## Limitations of the trust mechanisms

* **Unreplayed theorem records.** Several library theorems (for example
  the algebroid theorems relating the axioms, and `poisson_jacobi`)
  derive their requirements, but their chains do not replay into the
  claim. They carry an `unreplayed` requirement, are citable only with
  `allow_legacy=True`, and pass the marker on to every citing result.
  The Nambu double Jacobi chain obtained through a twist is not fully
  replayed either. See [Trust model](trust-model.md).
* **Known open issue: agreement on generators.** An identity proved by
  `AgreementOnGenerators` can still be cited outside its own algebra.
  The five tests that describe the correct behavior are strict expected
  failures in the test suite until the fix lands.
* **Oracle coverage.** The model oracle has no concrete model for about
  one third of the closures (`UNSUPPORTED`); abstract structures defined
  by the user belong to this group. For those closures the correct
  statement is "not numerically tested".
* **Research results.** `AxiomSuite` reports its own `CheckResult`
  (`CLOSED` / `RESIDUAL` / `FAILED`), not a `ProofResult` with
  requirements.
* **Sources that could not be verified.**
  * Some code comments cite a source referred to as "the E6 paper"
    whose bibliographic data has not yet been identified; the equation
    numbers (4.10)–(4.15) cited from it are unverified, and they are not
    the numbers of TW.
  * The equation and section numbers cited from Asakawa, Muraki, Sasa
    and Watamura (2015) have not been checked against the paper.
  * The code cites a derived-bracket source as "Kosmann-Schwarzbach
    1996"; the bibliography lists the 2004 paper "Derived brackets", and
    it is not certain that this is the work meant.
  * The identities of the Poisson package are standard results, but the
    code does not yet cite classical references for them.
* **An open question of convention.** In the Nambu double, the factor
  $\tfrac12$ can be placed on $g_Z$ or on $\mathbb{D}_Z$; the product
  $\mathbb{D}_Zg_Z$ is the same either way, so the mathematics is not
  affected, but the notation has not been settled.

(limitations-open-items)=
## Open items in the mathematical scope

| Area | Not yet available |
|---|---|
| Core | Proof of the graded Jacobi identity for the Schouten–Nijenhuis bracket. |
| Core | On an algebroid, $d_E^2=0$ only for $p=0,1$; $[\mathcal{L}_u,\mathcal{L}_v]=\mathcal{L}_{[u,v]}$ only in defect form. |
| Core | The Hodge star is structural only: no $\star\star=\pm1$, no component computation, codifferential or Laplacian. |
| Core | Wedge evaluation is not registered in the $TM$ engine: $(\alpha\wedge\beta)(X,Y)$ stays unexpanded there (the rule exists only in some package engines). |
| Metric-affine | The projected $E$-torsion $\hat T$ and ADM Prop. 3.10–3.11; non-metricity forms $Q_{ab}$ on $E$. |
| Metric-affine | The full form of MC Prop. 4.2 ($\mathcal{P}=\mathrm{pr}_2\circ\tau$ on an exact almost-Courant algebroid); today only the part showing that two projectors agree on coboundary values exists. |
| Metric-affine | MC Prop. 3.5–3.6 (connection shift, $E$-contortion) and MC Prop. 4.3–4.5 (orthonormal frames). |
| Metric-affine | Trace identities (they need symbolic dimension), an Einstein tensor theorem (the Einstein tensor is a definition only), pair symmetry $R_{abcd}=R_{cdab}$, the Weyl tensor, conformal and projective geometry. |
| Poisson/Nambu | The Koszul–Brylinski bracket of mixed degrees $[\Omega^p,\Omega^q]_\pi$; Nambu Leibniz–Jacobi only on exact wedge generators and for concrete $p$. |
| Poisson/Nambu | Non-degeneracy of a symplectic form is not a rule; no Darboux theorem, symplectic reduction, moment map or Poisson cohomology. |
| Drinfel'd | The vector component of the double's Leibniz–Jacobi identity, and $p\ge2$ for the Poisson and Nambu doubles. |
| Drinfel'd | General $2\times2$ $\Psi$ composition (TW (7.7)–(7.10) in full generality); the master equations of proto-bialgebroids (TW (3.11)–(3.15)). |
| Drinfel'd | The calculus elements of the three decompositions of $B_n$ are structural only. |
| Generalized | Dirac structures, the generalized metric, generalized Levi-Civita and Bismut connections, generalized complex structures, T-duality. |
| Generalized | A fully mechanical form of the general decomposition of B §6–8; a full derivation of the anchor morphism at the Courant level; transport without declarations; general hypotheses with bound variables; in the Dorfman axiomatics, the $\mathcal{D}$-formula (polarization needs $\mathbb{R}$-additivity of $\mathcal{D}$). |

## The user side

* **Interface.** JacoPy is a Python library with example notebooks. A
  web interface is planned. There is no parser that reads expressions
  from text or LaTeX, and no single "front door" research context yet;
  users import from several modules and pass infrastructure such as the
  registry by hand.
* **Error messages.** When a proof does not close, the library shows
  the residual, but it does not yet say *why* the engine got stuck (for
  example, which certificate was missing).
* **Docstrings.** Some docstrings lag behind the code, and several refer
  to planning documents that are not part of the repository. When a
  docstring and the code disagree, the code and its tests are
  authoritative.

## The code base

* **Layering.** 29 deferred import statements point upward, and the
  packages form cycles that close only through deferred imports (see
  [Architecture](architecture.md)). There is no automated layering test
  yet.
* **Large modules.** Eight modules exceed 1,000 lines
  (`generalized/courant_axioms.py` 1,789, `display/latex.py` 1,659,
  `central/calculus/bracket_calculus.py` 1,287, `drinfeld/twist.py`
  1,190, `central/algebroid/theorems.py` 1,081,
  `drinfeld/tilde_calculus.py` 1,078, `poisson/tilde.py` 1,059,
  `poisson/koszul_jacobi.py` 1,031; measured at `9a11e9b`). Splitting
  them is planned.
* **Private imports.** Some modules still import `_`-prefixed names
  from other subpackages; the example notebooks use none.
