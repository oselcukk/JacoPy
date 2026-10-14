# Related tools

This page places JacoPy among other software for differential geometry:
computer algebra systems, proof assistants and web calculators. It is
based on a brief survey carried out in October 2026. The numbers in
brackets refer to the {ref}`sources <related-tools-sources>` at the end. Cells marked "not
verified" could not be confirmed from a source in that survey, and
nothing was guessed. Because the survey was brief, **claims of absence
are not definitive**.

## Position

As far as this survey shows:

* No proof chain or assumption tracking was found in the documentation
  of the computer algebra systems surveyed (SageManifolds,
  sympy.diffgeom, Maple DifferentialGeometry, EinsteinPy, GRTensor,
  PoissonGeometry, …). JacoPy's step-by-step derivations and lists of
  assumptions are a feature not seen in these tools.
* Proof assistants such as Lean 4 with Mathlib provide kernel-checked
  proofs, but according to the relevant documentation, differential
  forms and the Lie derivative on manifolds are not yet available in
  Mathlib, and nothing was found for Courant or Lie algebroids [20][21].
  JacoPy stands in between: it **keeps a proof chain but has no logical
  kernel**. Its proofs rest on rewrite rules and do not give a formal
  guarantee at the level of Lean (see [Trust model](trust-model.md)).
* No ready-made package for Courant algebroids, Drinfel'd doubles or
  Nambu–Poisson structures was found. The closest pieces are the
  Schouten–Nijenhuis bracket and Poisson bivectors in SageManifolds [2]
  and local Poisson–Nijenhuis calculus in PoissonGeometry [17]. For
  Courant algebroids, only theoretical papers were found, not software
  [28]–[31].
* No mechanism that cross-checks coordinate-free proof steps against
  concrete coordinate models, like JacoPy's model oracle, was seen.
* This is not a claim that JacoPy is better. SageManifolds and Mathlib
  are far broader and more mature; JacoPy's target area (graded algebra,
  algebroids, the geometry of string and M-theory) is narrow and
  specialized.

**Tools with a web interface.** mathdf offers an ordinary differential
equation solver with step-by-step solutions, but no differential forms
or differential-geometric identities [26]. Symbolab offers calculus and
ODE solvers; no source was found for support of differential forms or
the Lie derivative [27]. WolframAlpha and matrixcalc.org could not be
checked directly in this survey, so no claims are made about them.

## Comparison

| Tool | What it does | Environment | Coordinates or abstract | Proof record, assumption tracking | Algebroid / Courant / Poisson | License | Source |
|---|---|---|---|---|---|---|---|
| SageManifolds (SageMath) | Manifolds, tensor fields, differential forms, Lie and exterior derivatives, Hodge star | Python / SageMath | Coordinate and frame components (atlas, charts) | None found | Multivectors and Schouten–Nijenhuis (Sage 9.1), Poisson bivector (9.6); algebroids and Courant not found | GPL | [1][2] |
| xAct (xTensor, xCoba) | Abstract-index tensor algebra; components with xCoba | Mathematica | Both | None found | Not verified | GPL | [3] |
| Cadabra2 | Field-theory-oriented tensor computer algebra | C++ / Python | Abstract index | Not verified | Not verified | GPL-3.0 | [4][5] |
| Maple DifferentialGeometry | Calculus on manifolds, tensors, Lie algebras and groups, jet spaces | Maple (commercial) | Coordinate-based (local) | None found | Lie algebras; no source found for algebroids or Poisson | Commercial | [6][7] |
| Maple Physics | Tensor analysis, field theory | Maple | Mainly abstract index | Not verified | Not verified | Commercial | [8] |
| sympy.diffgeom | Manifolds, coordinate systems, differential forms, Lie derivative | Python / SymPy | Coordinate-based | No | Not found | BSD (not confirmed) | [9] |
| EinsteinPy | General relativity: metric, Christoffel symbols, Riemann and Ricci tensors | Python | Coordinate-based | No | No | MIT | [10] |
| Redberry | Tensor computer algebra, Feynman diagrams | Java | Abstract index | Not verified | Not verified | Not verified | [11] |
| Atlas 2 for Mathematica | Coordinate-free differential geometry | Mathematica (commercial add-on) | Abstract | Not verified | Not verified | Commercial; appears unsupported | [12] |
| GRTensorII/III | Component computations in general relativity | Maple | Coordinate-based | No | No | Not verified | [13][14] |
| Mathematica differential-form packages | Wedge product, $d$, Lie derivative on $\mathbb{R}^n$ | Mathematica | Coordinate-based | No | Not found | Not verified | [15][16] |
| PoissonGeometry | Local Poisson–Nijenhuis calculus: Poisson bracket, Hamiltonian and modular vector fields, Jacobiator | Python | Coordinate-based (local) | No; zero testing on symbolic expressions, with the limitation stated by the authors | Poisson yes; Nambu, algebroids, Courant not found | MIT | [17][18] |
| Maple `Jacobi` package | Schouten bracket of weakly nonlocal Hamiltonian operators | Maple | Local | No | Poisson bivectors (integrable PDEs) | Not verified | [19] |
| Lean 4 Mathlib | Manifolds, Lie bracket of vector fields, $d$ on normed spaces ($d^2=0$) | Lean 4 | Abstract, type-theoretic | Yes, kernel-checked proofs | Differential forms and the Lie derivative on manifolds not in the documentation; algebroids not found | Apache-2.0 (not confirmed) | [20]–[22] |
| Isabelle/HOL | Lie groups and algebras, smooth vector fields | Isabelle | Abstract | Yes | Not found | Not verified | [23] |
| Rocq (Coq) | Pieces of analysis (for example Picard–Lindelöf) | Rocq | Abstract | Yes | Not found | Not verified | [24] |
| Alakazam | Graded symbolic tensor algebra for field theory | Julia | Abstract index | Not verified | Not verified | CC BY 4.0 | [25] |
| **JacoPy** | Coordinate-free Cartan calculus, algebroids, Poisson/Nambu, Drinfel'd doubles, Courant algebroids, metric-affine geometry | Python | **Abstract, coordinate-free** (plus a coordinate-based oracle) | **Yes:** step-by-step derivation, rule sources, list of assumptions | **Yes** (see [Capabilities](capabilities.md)) | BSD-3-Clause | this site |

JacoPy uses SymPy (Meurer et al., 2017) as an optional dependency of
its model oracle; the proof engine itself has no dependencies.

(related-tools-sources)=
## Sources

Accessed October 2026. For sources 5, 11, 18, 19, 22, 23, 25, 29 and 31
the authors and titles were not fully verified in the survey; only the
topic of the page and its link are given.

1. SageManifolds. <https://sagemanifolds.obspm.fr/>
2. SageManifolds changelog. <https://sagemanifolds.obspm.fr/changelog.html>
3. xAct: xCoba and xTensor. <https://xact.es/xCoba/>; <https://www.xact.es/xTensor/>
4. Cadabra2 (GitHub). <https://github.com/kpeeters/cadabra2>
5. Cadabra2 (JOSS paper). <https://joss.theoj.org/papers/10.21105/joss.01118>
6. Maple DifferentialGeometry help page. <https://www.maplesoft.com/support/help/maple/view.aspx?path=DifferentialGeometry>
7. Anderson & Torre, DifferentialGeometry (arXiv:1103.1608). <https://arxiv.org/abs/1103.1608>
8. Maple Physics. <https://www.maplesoft.com/products/maple/features/physics.aspx>
9. sympy.diffgeom documentation. <https://docs.sympy.org/latest/modules/diffgeom.html>
10. EinsteinPy (GitHub). <https://github.com/einsteinpy/einsteinpy>
11. Redberry (arXiv:1302.1219). <https://arxiv.org/pdf/1302.1219>
12. Atlas 2 for Mathematica. <https://sites.google.com/view/atlas-2-for-mathematica>
13. GRTensor. <http://grtensor.phy.queensu.ca/>
14. GRTensor (GitHub). <https://github.com/grtensor/grtensor>
15. Wolfram Library Archive, MathSource 683. <https://library.wolfram.com/infocenter/MathSource/683>
16. Wolfram Library Archive, MathSource 482. <https://library.wolfram.com/infocenter/MathSource/482/>
17. PoissonGeometry (GitHub). <https://github.com/appliedgeometry/poissongeometry>
18. On Computational Poisson Geometry I: Symbolic Foundations (arXiv:1912.01746). <https://arxiv.org/pdf/1912.01746>
19. Maple `Jacobi` package (arXiv:2101.06467). <https://arxiv.org/pdf/2101.06467>
20. Mathlib: DifferentialForm/Basic. <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/DifferentialForm/Basic.html>
21. Mathlib: VectorField/LieBracket. <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Geometry/Manifold/VectorField/LieBracket.html>
22. The Stokes / chain-level $d^2=0$ bridge in Lean 4 (arXiv:2605.01028). <https://arxiv.org/html/2605.01028v1>
23. Lie groups and algebras in Isabelle/HOL (arXiv:2407.19211). <https://arxiv.org/abs/2407.19211>
24. Rocq (Coq). <https://madiot.fr/coq100/>; <https://ncatlab.org/nlab/show/Rocq>
25. Alakazam (arXiv:2608.20452). <https://arxiv.org/pdf/2608.20452>
26. mathdf. <https://www.mathdf.com/dif/>
27. Symbolab. <https://www.symbolab.com/solver/calculus-calculator>
28. Li-Bland & Meinrenken, Courant algebroids and Poisson geometry (arXiv:0811.4554). <https://arxiv.org/pdf/0811.4554>
29. Courant cohomology and Cartan calculus (arXiv:1911.05898). <https://arxiv.org/pdf/1911.05898>
30. Çatal-Özer, Dereli & Doğan, Pre-metric-Bourbaki algebroids (arXiv:2210.00548). <https://arxiv.org/html/2210.00548>
31. Courant–Dorfman algebras (arXiv:0902.4862). <https://arxiv.org/pdf/0902.4862>

Meurer, A., Smith, C. P., Paprocki, M., Čertík, O., Kirpichev, S. B.,
Rocklin, M., Kumar, A., Ivanov, S., Moore, J. K., Singh, S.,
Rathnayake, T., Vig, S., Granger, B. E., Muller, R. P., Bonazzi, F.,
Gupta, H., Vats, S., Johansson, F., Pedregosa, F., … Scopatz, A.
(2017). SymPy: Symbolic computing in Python. *PeerJ Computer Science*,
*3*, e103. <https://doi.org/10.7717/peerj-cs.103>
