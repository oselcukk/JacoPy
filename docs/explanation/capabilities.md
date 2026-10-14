# Capabilities

This page gives an overview of the mathematics JacoPy can do today: the
objects and operators it knows, the identities it proves in the core
(the tangent bundle $TM$ and a general algebroid $E$), the four geometry
packages, and the research interface for structures defined by the
user. It is a map, not a manual: for step-by-step instructions see the
[how-to guides](../howto/index.md) and the [tutorials](../tutorials/index.md);
for the file in which each result lives see the
[mathematical content table](../reference/math-content-table.md).

Paper abbreviations used below (full references in the
[bibliography](../reference/bibliography.md)):
**MC** Dereli & Doğan (2020); **ADM** Dereli & Doğan (2023);
**B** Çatal-Özer, Dereli & Doğan (2022); **DD** Çatal-Özer, Doğan &
Yetişmişoğlu (2024); **TW** Çatal-Özer, Doğan & Yetişmişoğlu (2025);
**U** Uchino (2002); **LWX** Liu, Weinstein & Xu (1997).

## At a glance

* **Coordinate-free and symbolic.** Functions, vector fields, forms and
  tensors are terms of a formal language, not component arrays; even
  the dimension may be symbolic. Proofs reduce both sides to the same
  normal form with rules that come from definitions and from explicitly
  declared axioms, and record every step.
* **One general machine.** The exterior derivative $d$ and the Lie
  derivative $\mathcal{L}$ are derived from a pair (anchor $\rho$,
  bracket $[\cdot,\cdot]$). The tangent bundle ($\rho=\mathrm{id}$,
  Lie bracket) is a special case; an algebroid $E$ uses the same
  machine. For $E=TM$ the algebroid calculus *is* the ordinary Cartan
  calculus, as the same object, not just an equal one.
* **Size.** 303 proof builders (`prove_*` functions: 58 in the core,
  245 in the packages) and 194 rewrite-rule classes, each with a
  classified role (144 definitions, 44 assumptions, 6 theorems),
  measured at commit `9a11e9b`.
* **Sources.** Package results come mainly from the papers MC, ADM, B,
  DD and TW; each proof step records its source, including the equation
  number.

## Objects and operators

**Graded algebra.** One Koszul sign rule holds throughout: exchanging
elements of degrees $|a|$ and $|b|$ produces $(-1)^{|a||b|}$. Degrees
may be symbolic; the sign is still decided when the exponent is even
(for example $(-1)^{2|\alpha||\beta|}=1$), and otherwise the rule is
not applied. The graded commutator, the graded Leibniz rule, the
exterior product and product ordering all follow this rule.

**Geometric objects.** Vector bundles and $TM$ (with symbolic
dimension), functions, vector fields acting as derivations, $p$-forms
(with symbolic $p$), multivectors and bivectors, tensors, metric and
inverse metric with musical maps, the Hodge star (structure and degree
only), connections, frames and coframes, endomorphisms, interior
products ($\iota_X$, $\tilde\iota_\omega$, $\iota_{X_1\wedge\cdots\wedge X_p}$)
and partial evaluation. Algebroids $(E,\rho,[\cdot,\cdot]_E)$ have an
**opaque** bracket that is only $\mathbb{R}$-bilinear; every further
property must be declared. They also carry the coboundary
$D=\rho^*\circ d$, the locality operator $L(\omega,u,v)$ and an
optional $E$-metric.

**Operators.** Lie bracket; exterior derivative by the Palais formula
$d\omega(X_0,\dots,X_p)=\sum_i(-1)^i\rho(X_i)\,\omega(\dots\hat X_i\dots)+\sum_{i<j}(-1)^{i+j}\omega([X_i,X_j],\dots)$;
Lie derivative of functions, vector fields, forms and tensors; interior
product; wedge, tensor product, Sym and Alt; pairings and multi-argument
evaluation; covariant derivative; Schouten–Nijenhuis bracket;
anholonomy $\gamma^c{}_{ab}$; the algebroid $d_E$ and
$\mathcal{L}^E$; Jacobiator, Derivator and Predator; the locality
projector; derived brackets. Concrete brackets such as Courant and
Dorfman live in the packages.

## Core identities on $TM$

The Cartan calculus is **not axiomatic**: its relations are theorems
derived from the Palais formula for $d$ and the definition of
$\mathcal{L}$.

* **Lie bracket:** antisymmetry, the Jacobi identity (applied to a
  generic function), the Leibniz rules $[X,fY]=X(f)Y+f[X,Y]$ and
  $[fX,Y]=f[X,Y]-Y(f)X$; a claim with the wrong sign is rejected.
* **$d^2=0$:** on functions from the definition; on 1-forms through a
  *repair loop* that recognizes the Lie–Jacobi expression in the
  residual, proves it separately and cites it; on $p$-forms for
  $p=1,\dots,5$, with $\binom{p+2}{3}$ Jacobi citations.
* **Cartan relations:** $\mathcal{L}_X=d\iota_X+\iota_Xd$ (for
  $p=1,\dots,5$), $[\mathcal{L}_X,d]=0$,
  $[\mathcal{L}_X,\iota_Y]=\iota_{[X,Y]}$,
  $[\mathcal{L}_X,\mathcal{L}_Y]=\mathcal{L}_{[X,Y]}$,
  $\iota_X\iota_Y+\iota_Y\iota_X=0$, each in the degrees listed in the
  [content table](../reference/math-content-table.md).
* **Frames and connections:** antisymmetry of the anholonomy, the
  Maurer–Cartan relation $de^c(e_a,e_b)=-\gamma^c{}_{ab}$, vanishing
  anholonomy in a holonomic frame (as an assumption), the defining
  rules of $\nabla$.
* **Schouten–Nijenhuis bracket:** base cases, the wedge-Leibniz rule,
  $\mathcal{L}_XP=[X,P]_{SN}$, and graded antisymmetry on decomposable
  multivectors of low degree. The graded Jacobi identity is not yet
  proved.

## Core identities on an algebroid $E$

**Declarations and levels.** The axioms right Leibniz, left Leibniz,
anchor morphism, Jacobi, antisymmetry, metric invariance and symmetric
part are declared one by one, or in ready-made levels
(`almost-leibniz`, `local`, `pre-leibniz`, `leibniz`, `lie`,
`almost-courant`, `metric`, `pre-courant`, `courant`) that deliberately
leave out derivable axioms.

**Theorems relating the axioms**, each closing only under the stated
declarations:

* right Leibniz and Jacobi imply the anchor morphism
  $\rho[u,v]=[\rho u,\rho v]$ ("every Leibniz algebroid is
  pre-Leibniz"; B §4);
* metric invariance with non-degeneracy implies right Leibniz
  (B (4.11)), and the left Leibniz rule
  $[fu,v]=f[u,v]-\rho(v)(f)u+g(u,v)\,g^{-1}(Df)$ follows from the
  symmetric-part and invariance axioms (B (4.11), MC Prop. 4.1);
* $\rho(L(Df,u,v))=0$ on a local pre-Leibniz algebroid (MC §3); the
  properties of the locality projector.

**Algebroid calculus.** For every $\mathbb{R}$-bilinear bracket, without
declarations: $d_Ef=Df$, the Palais formula on 1-forms,
$\mathcal{L}^E_uf=\rho(u)f$, $\mathcal{L}^E_uv=[u,v]_E$, the Cartan
formula ($p=0,\dots,5$) and $[\mathcal{L}_u,\iota_v]=\iota_{[u,v]}$.
Conditionally: $d_E^2f=0$ needs the anchor morphism, and $d_E^2\alpha=0$
on 1-forms needs anchor morphism, Jacobi and antisymmetry together. The
**defect formulas** of TW Appendix A express the failure of these
relations in terms of the anchor defect and the Jacobiator, and close
without declarations.

How to declare a structure and read the result is shown in the
[how-to guides](../howto/index.md).

## Packages

**Metric-affine geometry** (`jacopy.packages.metric_affine`). On $TM$:
tensoriality and antisymmetry of torsion and curvature, the Ricci
identity, Bianchi I and II with torsion, non-metricity, the generalized
Koszul formula for an arbitrary connection, the classical Koszul
formula and the uniqueness of the Levi-Civita connection, frame
components and the Cartan structure equations, concrete evaluation with
user-supplied components. On an algebroid $E$ (MC, ADM): $E$-connections,
modified torsion ${}^LT$ and projected curvature ${}^L\hat R$,
admissible connections, the generalized Ricci identity, the $E$-Koszul
family and uniqueness under null locality, $E$-Bianchi and $E$-Cartan
equations, the derived calculus.

**Poisson, symplectic and Nambu–Poisson geometry**
(`jacopy.packages.poisson`). Poisson bracket identities, Hamiltonian
vector fields, the Koszul bracket on 1-forms and its general Jacobi
identity under $[\pi,\pi]_{SN}=0$, Poisson–Jacobi, the symplectic case
(flow invariance of $\omega$, the bracket chain through $\pi=\omega^{-1}$),
the tilde calculus of the cotangent Lie algebroid, and Nambu–Poisson
structures with the higher Koszul bracket (DD (6.8)–(6.9)). The Poisson
condition, $d\omega=0$, $\pi=\omega^{-1}$ and the Nambu fundamental
identity are user declarations, and each declaration-dependent result
is also tested to fail without it.

**Algebroid calculus, Drinfel'd doubles and twists**
(`jacopy.packages.drinfeld`; DD, TW). Calculus conditions and the
$\mathcal{K}$ operator, abstract doubles, the standard (Dorfman),
Poisson and Nambu doubles, bialgebroid compatibility conditions, the
Nambu tilde calculus and its Jacobi compatibility conditions, metric
invariance (DD Appendix D, including (D.19) for $p=3$), bracket
morphisms, $\Pi$/$B$/$m$/$R$ twists and their composition, the
Roytenberg bracket, $B_n$-generalized geometry and an exceptional
Courant bracket on $TM\oplus\Lambda^2T^*M\oplus\Lambda^5T^*M$.

**Generalized geometry and Courant algebroids**
(`jacopy.packages.generalized`; LWX, U, B, TW). Uchino's redundancy
results for the Courant and Dorfman axioms, the standard Courant
algebroid on $TM\oplus T^*M$, $H$-twisted Dorfman brackets with the
Jacobi defect $\iota_W\iota_V\iota_U\,dH$, the Roytenberg-to-Courant
reductions, Poisson-generalized pairs and $R$-flux, the Bourbaki
pre-calculus (B), general $\Psi$-twists that transport all algebroid
axioms, exceptional rotations, frame evaluation, and the exact locality
projector.

**Using packages together.** The packages share the central objects
and can be combined in one computation; several joint results are
tested (for example a Dorfman bracket twisted by a bivector becomes the
Nambu double plus a correction $R'$ that vanishes exactly under the
declared Poisson condition). Each package also loads on its own.

## The user's own structure

Users can write their own bundle, bracket and axioms and ask for a
proof. Two routes exist today:

1. **Opaque bracket and declarations.** Use the core declarations and
   levels, or write axioms as rewrite rules (`Definition` subclasses
   with `role = "assumption"`); the result then lists them by name. For
   example, with right Leibniz and antisymmetry declared, the left
   Leibniz rule closes in four steps; if either declaration is
   withdrawn, it does not close and the residual shows what is
   missing.
2. **A bracket given by components, and an axiom suite**
   (`jacopy.research`). Typed generalized sections
   (`SectionType`, `GeneralizedSection`), block-operator automorphisms
   $\Psi$ (`BlockMatrix`, with derived inverses), automatic engine
   assembly from the expressions to be checked (`assemble_engine`,
   `assembly_report`), structure providers that carry their own
   declarations, and `AxiomSuite`, which checks right Leibniz,
   symmetric part, anchor morphism, metric invariance and
   Leibniz–Jacobi and reports `CLOSED` or `RESIDUAL` for each
   component. `transport(Ψ)` moves a whole structure along $\Psi$
   (TW (7.3)).

Extension points are described in [Architecture](architecture.md); the
four example notebooks in `examples/` walk through these workflows.

## Output

Every proof can be printed as a step tree, as LaTeX (`to_latex`,
`chain_to_latex`) or as a standalone LaTeX document with an APA 7
bibliography (`theorem_to_latex_document`), and notebooks render
theorem cards. The literature source of each rule is printed with every
step it produces.

## Large computations

The engine also closes computations that would take hours by hand. Two
recorded runs: DD (D.19) for the Nambu double with $p=3$ closes in 913
steps (about 6 seconds), and metric invariance for the exceptional
bracket rotated by $\Psi_\Pi$ closes in 10,184 steps (about 21 minutes),
with intermediate expressions of up to 77,498 nodes.

What JacoPy cannot do yet is collected in [Limitations](limitations.md).
