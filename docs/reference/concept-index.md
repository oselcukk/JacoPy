# Concept index

For the question "where is the thing I am looking for?": 81 concepts, in alphabetical order. Each concept has a one-line mathematical definition and the full paths of the files in which it occurs; the folder names link to the corresponding section of [mathematical content table](math-content-table.md). A detailed explanation of the concepts and the reading notes (two notions of degree, Koszul sign, conventions) can be found in the introduction of that page. Like the table, this index describes the repository at commit `9a11e9b` (file list unchanged since `8b46a5d`).

## A

### almost-Lie algebroid

Antisymmetric bracket satisfying the Leibniz rule $[u,fv]=f[u,v]+\rho(u)(f)\,v$ and the anchor morphism property $\rho[u,v]=[\rho u,\rho v]$; the Jacobi identity is not required. (4 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/defect_formulas.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### anchor ρ

$\rho:E\to TM$, $C^\infty$-linear; $u(f):=\rho(u)f$. (31 files)

- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/derived.py`
- {ref}`central (root) <mct-jacopy-central-root>`: `jacopy/central/__init__.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/vector_field.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/__init__.py`, `jacopy/central/calculus/bracket_calculus.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/__init__.py`, `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/defect_formulas.py`, `jacopy/central/algebroid/locality.py`, `jacopy/central/algebroid/operators.py`, `jacopy/central/algebroid/rules.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`, `jacopy/packages/metric_affine/e_connection.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/showcase.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/bracket_morphism.py`, `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/metric_invariance.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_exact.py`, `jacopy/packages/generalized/bourbaki_structure.py`, `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/frame_evaluation.py`, `jacopy/packages/generalized/general_twist.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/standard_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`, `jacopy/oracle/realize_e.py`

### anholonomy γ

In a frame, $[e_a,e_b]=\gamma^c_{ab}e_c$, i.e. $\gamma^c_{ab}=\langle e^c,[e_a,e_b]\rangle$. (1 file)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/anholonomy.py`

### (anti)symmetrization

$T_{(a_1\dots a_k)}=\tfrac1{k!}\sum_\sigma T_{a_{\sigma(1)}\dots a_{\sigma(k)}}$; $T_{[a_1\dots a_k]}$ is the same sum weighted by $\operatorname{sgn}\sigma$ (JacoPy normalizes by $1/k!$). (3 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/symmetrize.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/symmetrize_rules.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/antisymmetrize.py`

### assumption/declaration

An explicitly declared axiom/property (`*Declaration`; e.g. $[\pi,\pi]_{SN}=0$, $d\omega=0$); never assumed silently. (24 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/properties.py`, `jacopy/core/registry.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/algebroid_expansion.py`, `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/declarations.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/metric.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/koszul_jacobi.py`, `jacopy/packages/poisson/nambu.py`, `jacopy/packages/poisson/symplectic.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`, `jacopy/packages/drinfeld/tilde_calculus.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/_cited_rule.py`, `jacopy/packages/generalized/bourbaki_structure.py`, `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/r_twisted.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/providers.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/expansion.py`, `jacopy/proof/ownership.py`, `jacopy/proof/registry_facts.py`, `jacopy/proof/result.py`, `jacopy/proof/theorems.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/select.py`

## B

### bialgebroid

A pair $(A,Z)$, an algebroid and its partner, satisfying the calculus compatibility conditions; the input of the double. (3 files)

- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/calculus_conditions.py`, `jacopy/packages/drinfeld/poisson_bialgebroid.py`, `jacopy/packages/drinfeld/tilde_calculus.py`

### Bianchi identity

Form with torsion: (I) $\mathfrak S\,R(X,Y)Z=\mathfrak S[(\nabla_XT)(Y,Z)+T(T(X,Y),Z)]$, (II) $\mathfrak S[(\nabla_XR)(Y,Z)+R(T(X,Y),Z)]=0$; $\mathfrak S$ is the cyclic sum. (2 files)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/bianchi.py`, `jacopy/packages/metric_affine/e_bianchi.py`

### Bourbaki algebroid

Courant-type (pre-)metric algebroid whose metric takes values in a bundle $\mathcal R$ (B, 2022); Bourbaki pre-calculus and Ševera-type classification. (5 files)

- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_exact.py`, `jacopy/packages/generalized/bourbaki_precalculus.py`, `jacopy/packages/generalized/bourbaki_severa.py`, `jacopy/packages/generalized/bourbaki_structure.py`, `jacopy/packages/generalized/general_twist.py`

### bundle endomorphism

$C^\infty$-linear $\Phi:E\to E$ (e.g. twist $\Psi$, $m$, $m^{-1}$). (1 file)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/endomorphism.py`

## C

### Cartan relations

$\mathcal L_X=d\iota_X+\iota_Xd$, $[\mathcal L_X,\iota_Y]=\iota_{[X,Y]}$, $[\mathcal L_X,\mathcal L_Y]=\mathcal L_{[X,Y]}$, $[\mathcal L_X,d]=0$ (in JacoPy, theorems derived from the definitions). (13 files)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/__init__.py`, `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/cartan_rules.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/defect_formulas.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/tilde.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`, `jacopy/packages/drinfeld/calculus_conditions.py`, `jacopy/packages/drinfeld/poisson_bialgebroid.py`, `jacopy/packages/drinfeld/tilde_calculus.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_exact.py`, `jacopy/packages/generalized/bourbaki_precalculus.py`

### Cartan structure equations

In a frame, $T^a=de^a+\omega^a{}_b\wedge e^b$, $R^a{}_b=d\omega^a{}_b+\omega^a{}_c\wedge\omega^c{}_b$ (connection 1-forms $\omega^a{}_b$). (4 files)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/anholonomy.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/e_cartan.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`

### citation/bibliography

APA 7 citations of the papers that rules and theorems rely on (`cite`, locator). (8 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/__init__.py`, `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/declarations.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/step.py`
- {ref}`display <mct-jacopy-display>`: `jacopy/display/ascii.py`, `jacopy/display/latex.py`, `jacopy/display/terminal.py`
- {ref}`root files <mct-jacopy-root-files>`: `jacopy/bibliography.py`

### coboundary D

$D=\rho^*\circ d$: $\langle Df,u\rangle=\rho(u)f$. (2 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/rules.py`

### connection

Affine connection $\nabla$ ($C^\infty$-linear in the direction, Leibniz in the argument); E-connection $\nabla_u(fv)=\rho(u)(f)v+f\nabla_uv$. (16 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/connection.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/definitions.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/component_workflow.py`, `jacopy/packages/metric_affine/decomposition.py`, `jacopy/packages/metric_affine/e_bianchi.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/metric_affine_expansion.py`, `jacopy/packages/metric_affine/metric_koszul.py`, `jacopy/packages/metric_affine/modified.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`, `jacopy/packages/metric_affine/rules.py`, `jacopy/packages/metric_affine/torsion_curvature.py`

### cotangent algebroid

The Lie algebroid $(T^*M,\pi^\sharp,[\cdot,\cdot]_\pi)$. (3 files)

- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/showcase.py`, `jacopy/packages/poisson/tilde.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

### Courant algebroid

$(E,\rho,[\cdot,\cdot],\langle\cdot,\cdot\rangle)$: Leibniz–Jacobi, anchor morphism, invariance of the metric, and symmetric part given by $\mathcal D\langle u,v\rangle$ (LWX [C1]–[C5], Dorfman form [C'1]–[C'5]). (14 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/exact_locality_projector.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/r_twisted.py`, `jacopy/packages/generalized/roytenberg_courant.py`, `jacopy/packages/generalized/standard_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### Courant bracket

Antisymmetric bracket on $TM\oplus T^*M$: $[\![X+\xi,Y+\eta]\!]=[X,Y]+\mathcal L_X\eta-\mathcal L_Y\xi-\tfrac12d(\iota_X\eta-\iota_Y\xi)$. (5 files)

- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/standard_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### covariant derivative ∇

$\nabla_XT$; extended to tensors by the Leibniz rule; preserves the type. (7 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/connection.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/tensor_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/definitions.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/bianchi.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/rules.py`, `jacopy/packages/metric_affine/torsion_curvature.py`

### curvature

$R(X,Y)Z=\nabla_X\nabla_YZ-\nabla_Y\nabla_XZ-\nabla_{[X,Y]}Z$ (on E the projected $^{L}\hat R$). (8 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/defect_formulas.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/bianchi.py`, `jacopy/packages/metric_affine/e_bianchi.py`, `jacopy/packages/metric_affine/e_cartan.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/modified.py`, `jacopy/packages/metric_affine/torsion_curvature.py`

## D

### Derivator

$D_\Phi(u,v)=\Phi[u,v]-[\Phi u,v]-[u,\Phi v]$: the failure of $\Phi$ to be a derivation of the bracket. (1 file)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/operators.py`

### derived bracket

$\{a,b\}_Q=[[a,Q],b]$; for odd $Q$ on a graded Lie algebra, $[Q,Q]=0$ implies the Leibniz (Loday) form of the Jacobi identity. (4 files)

- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/derived.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/strategies.py`, `jacopy/proof/verifier.py`

### differential form

$p$-form $\omega\in\Gamma(\Lambda^pE^*)$: alternating, $C^\infty$-multilinear $\omega(Y_1,\dots,Y_p)$. (16 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/hodge.py`, `jacopy/core/multi_eval.py`, `jacopy/core/pairing.py`, `jacopy/core/properties.py`, `jacopy/core/wedge.py`
- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/grading.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/normalize_alternating.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/form.py`, `jacopy/central/objects/interior.py`, `jacopy/central/objects/partial_eval.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_forms.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exact_locality_projector.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

### Dorfman bracket

$[X+\xi,Y+\eta]=[X,Y]+\mathcal L_X\eta-\iota_Yd\xi$ (not antisymmetric; Leibniz type). (13 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/declarations.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/nambu.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/examples.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/frame_evaluation.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/roytenberg_courant.py`, `jacopy/packages/generalized/standard_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### Drinfeld double

Double bracket on $E=A\oplus Z$ built from bialgebroid data; the standard double is the Dorfman bracket. (8 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/endomorphism.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`, `jacopy/packages/drinfeld/bracket_morphism.py`, `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/metric_invariance.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exceptional_double.py`, `jacopy/packages/generalized/roytenberg_courant.py`

### d²=0

$d\circ d=0$; in JacoPy, a theorem derived from the Palais definition ($p=0,1$ in central, $p=1..5$ proved in tests; no symbolic $p$). (8 files)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/exterior.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/defect_formulas.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/tilde.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/diagnostic_rules.py`

## E

### exceptional geometry (E6)

Exceptional Courant bracket on $TM\oplus\Lambda^2T^*M\oplus\Lambda^5T^*M$, its double and the twist $\Psi_\Pi$. (6 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/multivector_interior.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/examples.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exceptional_double.py`, `jacopy/packages/generalized/exceptional_rotation.py`, `jacopy/packages/generalized/frame_evaluation.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/sections.py`

### expression tree

Tree form of a symbolic expression: nodes for sum, non-commutative product, $\wedge$, $\otimes$, $\star$, $\Sigma$ … (1 file)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/expr.py`

### exterior derivative d

$d:\Omega^p\to\Omega^{p+1}$, degree $+1$; defined by the Palais formula. (19 files)

- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/grading.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/__init__.py`, `jacopy/central/calculus/bracket_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/__init__.py`, `jacopy/central/tangent/anholonomy.py`, `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/exterior.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/defect_formulas.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`, `jacopy/packages/metric_affine/e_cartan.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_forms.py`, `jacopy/packages/poisson/symplectic.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/calculus_conditions.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_precalculus.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/diagnostic_rules.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize_e.py`, `jacopy/oracle/values.py`

## F

### frame/coframe

Local frame $(e_a)$ and coframe $(e^a)$, $\langle e^a,e_b\rangle=\delta^a_b$. (20 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/indexed_sum.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/frame.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/indexed_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/anholonomy.py`, `jacopy/central/tangent/definitions.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/component_workflow.py`, `jacopy/packages/metric_affine/decomposition.py`, `jacopy/packages/metric_affine/e_cartan.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/modified.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/tilde.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exact_locality_projector.py`, `jacopy/packages/generalized/frame_evaluation.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/antisymmetrize.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`, `jacopy/oracle/realize_e.py`

### function (C^∞)

Smooth functions $C^\infty(M)$, degree 0 (distinct from the ℝ-constant `Scalar`). (3 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/function.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/scalars.py`

## G

### generalized geometry

Courant/Dorfman structures on $TM\oplus T^*M$ and its generalizations. (4 files)

- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/examples.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/standard_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/sections.py`

### graded algebra

$\mathbb Z$-graded elements/operators: $|ab|=|a|+|b|$, $[A,B]=AB-(-1)^{|A||B|}BA$. (15 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/properties.py`, `jacopy/core/symbolic_degree.py`, `jacopy/core/wedge.py`
- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/commutator.py`, `jacopy/algebra/derivation.py`, `jacopy/algebra/grading.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/sort_product.py`
- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/base.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/function.py`, `jacopy/central/objects/interior.py`, `jacopy/central/objects/kind.py`, `jacopy/central/objects/multivector.py`, `jacopy/central/objects/vector_field.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/schouten.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/recognizers.py`

## H

### H-flux

Dorfman/Courant bracket twisted by a 3-form $H$ (term $H(X,Y,\cdot)$); Courant axioms $\iff dH=0$. (7 files)

- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/examples.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_severa.py`, `jacopy/packages/generalized/roytenberg_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### Hamiltonian vector field

$X_f=\pi^\sharp(df)$, $X_f(g)=\{f,g\}$; in the symplectic case $\iota_{X_f}\omega=df$. (4 files)

- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/showcase.py`, `jacopy/packages/poisson/symplectic.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize.py`

### Hodge ⋆

$\star:\Lambda^p\to\Lambda^{n-p}$ with respect to the metric, $\alpha\wedge\star\beta=g(\alpha,\beta)\,\mathrm{vol}_g$ (in JacoPy, only a structural node). (3 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/hodge.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/metric.py`

## I

### indexed sum

Sum over a bound index $\sum_a\mathrm{body}(a)$; the dummy index may be renamed. (2 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/indexed_sum.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/indexed_rules.py`

### interior product ι

$\iota_X\omega=\omega(X,\cdot,\dots)$ ($X$ in the first slot), degree $-1$; also $\tilde\iota_\alpha$, $\iota_P$. (19 files)

- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/grading.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/interior.py`, `jacopy/central/objects/multivector_interior.py`, `jacopy/central/objects/partial_eval.py`, `jacopy/central/objects/tilde_interior.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/interior_rules.py`, `jacopy/central/calculus/partial_eval_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/cartan_rules.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/symplectic.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/calculus_conditions.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_precalculus.py`, `jacopy/packages/generalized/exceptional_rotation.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/diagnostic_rules.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize_e.py`, `jacopy/oracle/values.py`

## J

### Jacobi identity

$[a,[b,c]]=[[a,b],c]+(-1)^{|a||b|}[b,[a,c]]$ (Leibniz form); for an antisymmetric bracket, the cyclic sum $=0$. (28 files)

- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/base.py`, `jacopy/brackets/derived.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/anholonomy.py`, `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/lie_bracket.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/bianchi.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_jacobi.py`, `jacopy/packages/poisson/nambu.py`, `jacopy/packages/poisson/showcase.py`, `jacopy/packages/poisson/tilde.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`, `jacopy/packages/drinfeld/calculus_conditions.py`, `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/examples.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/tilde_calculus.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/dialect_bridge.py`, `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/r_twisted.py`, `jacopy/packages/generalized/standard_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/strategies.py`, `jacopy/proof/verifier.py`

### Jacobiator

$J(u,v,w)=[u,[v,w]]-[[u,v],w]-[v,[u,w]]$: the defect of the Jacobi identity. (7 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/defect_formulas.py`, `jacopy/central/algebroid/operators.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`, `jacopy/packages/metric_affine/e_bianchi.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/general_twist.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize_e.py`

## K

### Koszul bracket

On 1-forms, $[\alpha,\beta]_\pi=\mathcal L_{\pi^\sharp\alpha}\beta-\mathcal L_{\pi^\sharp\beta}\alpha-d\,\pi(\alpha,\beta)$. (13 files)

- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/derived.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_forms.py`, `jacopy/packages/poisson/koszul_jacobi.py`, `jacopy/packages/poisson/nambu.py`, `jacopy/packages/poisson/showcase.py`, `jacopy/packages/poisson/tilde.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/poisson_bialgebroid.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/dialect_bridge.py`, `jacopy/packages/generalized/frame_evaluation.py`, `jacopy/packages/generalized/poisson_generalized.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/nambu_kind.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize.py`, `jacopy/oracle/values.py`

### Koszul formula

$2g(\nabla_XY,Z)=Xg(Y,Z)+Yg(X,Z)-Zg(X,Y)+g([X,Y],Z)-g([X,Z],Y)-g([Y,Z],X)$ (Levi-Civita). (2 files)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/metric_koszul.py`

### Koszul sign

The sign $(-1)^{|a||b|}$ produced when two graded elements are interchanged. (14 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/properties.py`, `jacopy/core/symbolic_degree.py`, `jacopy/core/wedge.py`
- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/commutator.py`, `jacopy/algebra/derivation.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/normalize_alternating.py`, `jacopy/algorithms/product_rule.py`, `jacopy/algorithms/simplify.py`, `jacopy/algorithms/sort_product.py`
- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/base.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/interior.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/schouten.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/engine_assembly.py`

### Kronecker delta

$\delta^a_b$; $\langle e^a,e_b\rangle=\delta^a_b$ and the contraction $\sum_b\delta^a_b\,t_b=t_a$. (1 file)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/frame.py`

## L

### LaTeX/display

Text/LaTeX rendering of expressions and proofs; notation conventions ($\iota_X$, $\mathcal L_X$, $\nabla$, $\langle\alpha,X\rangle$ …). (5 files)

- {ref}`display <mct-jacopy-display>`: `jacopy/display/__init__.py`, `jacopy/display/ascii.py`, `jacopy/display/jupyter.py`, `jacopy/display/latex.py`, `jacopy/display/terminal.py`

### Leibniz rule

For a graded derivation, $D(ab)=D(a)b+(-1)^{|D||a|}aD(b)$; for a bracket, $[u,fv]=f[u,v]+\rho(u)(f)\,v$. (30 files)

- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/commutator.py`, `jacopy/algebra/derivation.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/product_rule.py`
- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/base.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/connection.py`, `jacopy/central/objects/vector_field.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/definitions.py`, `jacopy/central/tangent/lie_bracket.py`, `jacopy/central/tangent/schouten.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/rules.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/rules.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/nambu.py`, `jacopy/packages/poisson/showcase.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`, `jacopy/packages/drinfeld/double.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_severa.py`, `jacopy/packages/generalized/bourbaki_structure.py`, `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/general_twist.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/recognizers.py`, `jacopy/proof/strategies.py`

### Levi-Civita

The unique torsion-free, metric-compatible connection ($T=0$, $\nabla g=0$). (2 files)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/metric_koszul.py`

### Lie algebroid

$(E,\rho,[\cdot,\cdot])$: an antisymmetric bracket satisfying Jacobi and $[u,fv]=f[u,v]+\rho(u)(f)v$. (7 files)

- {ref}`central (root) <mct-jacopy-central-root>`: `jacopy/central/__init__.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/__init__.py`, `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/context.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/showcase.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`

### Lie bracket

For vector fields, $[X,Y](f)=X(Y(f))-Y(X(f))$. (13 files)

- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/lie_bracket_vf.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/__init__.py`, `jacopy/central/tangent/anholonomy.py`, `jacopy/central/tangent/exterior.py`, `jacopy/central/tangent/lie_bracket.py`, `jacopy/central/tangent/schouten.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/operators.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/bianchi.py`, `jacopy/packages/metric_affine/decomposition.py`, `jacopy/packages/metric_affine/torsion_curvature.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/bracket_morphism.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

### Lie derivative L

$\mathcal L_Xf=X(f)$, $\mathcal L_XY=[X,Y]$, evaluation formula on tensors; on forms $\mathcal L_X=d\iota_X+\iota_Xd$ is a theorem. (20 files)

- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/lie_bracket_vf.py`
- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/derived.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/__init__.py`, `jacopy/central/calculus/bracket_calculus.py`, `jacopy/central/calculus/tensor_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/__init__.py`, `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/schouten.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/defect_formulas.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_forms.py`, `jacopy/packages/poisson/symplectic.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/calculus_conditions.py`, `jacopy/packages/drinfeld/metric_invariance.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_precalculus.py`, `jacopy/packages/generalized/exceptional_rotation.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize_e.py`, `jacopy/oracle/values.py`

### linearity

$\mathbb R$- or $C^\infty$-linearity: $T(fa+b)=fT(a)+T(b)$. (24 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/expr.py`, `jacopy/core/multi_eval.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/distribute.py`, `jacopy/algorithms/factor_terms.py`, `jacopy/algorithms/product_rule.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/endomorphism.py`, `jacopy/central/objects/multivector_interior.py`, `jacopy/central/objects/musical.py`, `jacopy/central/objects/tensor.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`, `jacopy/central/calculus/indexed_rules.py`, `jacopy/central/calculus/interior_rules.py`, `jacopy/central/calculus/partial_eval_rules.py`, `jacopy/central/calculus/slot_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/lie_bracket.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/locality.py`, `jacopy/central/algebroid/operators.py`, `jacopy/central/algebroid/rules.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/decomposition.py`, `jacopy/packages/metric_affine/rules.py`, `jacopy/packages/metric_affine/torsion_curvature.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exact_locality_projector.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/expansion.py`

### locality operator L

The $C^\infty$-trilinear $L(\omega,u,v)\in\Gamma(E)$ in $[fu,v]=f[u,v]-\rho(v)(f)u+L(Df,u,v)$ [MC Def 3.5]. (11 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/rules.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/modified.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/abstract_double.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_structure.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`, `jacopy/oracle/realize_e.py`

### locality projector 𝒫

On a regular anchored bundle, the $C^\infty$-linear $\mathcal P:\Gamma(E)\to\Gamma(E)$ with $\mathcal P L(Df,u,v)=L(Df,u,v)$, $\rho(\mathcal P L)=0$ [MC Def 3.10]; an object distinct from $L$. (8 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/algebroid_expansion.py`, `jacopy/central/algebroid/locality.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/derived.py`, `jacopy/packages/metric_affine/e_bianchi.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/modified.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exact_locality_projector.py`

## M

### metric

Symmetric non-degenerate $g$ (or an $E$-metric $\langle\cdot,\cdot\rangle$), inverse $g^{-1}$. (19 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/hodge.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/metric.py`, `jacopy/central/objects/musical.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/context.py`, `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/rules.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/component_workflow.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/metric_koszul.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_structure.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/algebroid.py`, `jacopy/oracle/realize_e.py`

### model oracle

Independent checker that tests an equality numerically on random concrete coordinate models (not a proof; an attempt at refutation). (11 files)

- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/__init__.py`, `jacopy/oracle/check.py`, `jacopy/oracle/hook.py`, `jacopy/oracle/models/__init__.py`, `jacopy/oracle/models/algebroid.py`, `jacopy/oracle/models/tangent.py`, `jacopy/oracle/realize.py`, `jacopy/oracle/realize_e.py`, `jacopy/oracle/report.py`, `jacopy/oracle/select.py`, `jacopy/oracle/values.py`

### multivector

$p$-vector $P\in\Gamma(\Lambda^pE)$, alternating evaluation on covectors $P(\alpha_1,\dots,\alpha_p)$. (14 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/multi_eval.py`
- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/grading.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/multivector.py`, `jacopy/central/objects/multivector_interior.py`, `jacopy/central/objects/tilde_interior.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/schouten.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/nambu.py`, `jacopy/packages/poisson/tilde.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/examples.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exceptional_double.py`, `jacopy/packages/generalized/frame_evaluation.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

### musical isomorphism ♯/♭

$g^\flat(X)=g(X,\cdot)$, $\pi^\sharp(\alpha)=\pi(\alpha,\cdot)$: vector ↔ 1-form. (3 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/musical.py`, `jacopy/central/objects/partial_eval.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/partial_eval_rules.py`

## N

### Nambu–Poisson

$(p+1)$-vector $\Pi$, $\{f_0,\dots,f_p\}=\Pi(df_0,\dots,df_p)$, fundamental identity; higher Koszul bracket on $p$-forms. (12 files)

- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/nambu.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/bracket_morphism.py`, `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/metric_invariance.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/tilde_calculus.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/dialect_bridge.py`, `jacopy/packages/generalized/exceptional_double.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/nambu_kind.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize.py`, `jacopy/oracle/values.py`

### non-metricity

$Q=\nabla g$, $Q(X,Y,Z)=(\nabla_Xg)(Y,Z)$. (5 files)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/metric_koszul.py`, `jacopy/packages/metric_affine/nonmetricity_forms.py`

### normal form/simplification

Reduction of an expression to a chosen representative of its equivalence class (distribution, like terms, Koszul ordering). (17 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/equality.py`, `jacopy/core/expr.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/canonicalize.py`, `jacopy/algorithms/collect_terms.py`, `jacopy/algorithms/distribute.py`, `jacopy/algorithms/factor_terms.py`, `jacopy/algorithms/flatten.py`, `jacopy/algorithms/normalize_alternating.py`, `jacopy/algorithms/rewrite.py`, `jacopy/algorithms/simplify.py`, `jacopy/algorithms/sort_product.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/scalars.py`, `jacopy/central/calculus/slot_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/lie_bracket.py`, `jacopy/central/tangent/tangent_expansion.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/component_workflow.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/normalize.py`

## P

### pairing

$\langle\alpha,X\rangle=\alpha(X)\in C^\infty(M)$; bilinear, degree 0. (23 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/pairing.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/factor_terms.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/form.py`, `jacopy/central/objects/frame.py`, `jacopy/central/objects/multivector.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`, `jacopy/central/calculus/interior_rules.py`, `jacopy/central/calculus/slot_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/definitions.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/rules.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/examples.py`, `jacopy/packages/drinfeld/metric_invariance.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_exact.py`, `jacopy/packages/generalized/bourbaki_precalculus.py`, `jacopy/packages/generalized/courant_axioms.py`, `jacopy/packages/generalized/dorfman_axioms.py`, `jacopy/packages/generalized/frame_evaluation.py`, `jacopy/packages/generalized/general_twist.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/standard_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`

### Palais formula

$(d\omega)(X_0,\dots,X_p)=\sum_i(-1)^iX_i\,\omega(\dots\hat X_i\dots)+\sum_{i<j}(-1)^{i+j}\omega([X_i,X_j],\dots\hat X_i\dots\hat X_j\dots)$ (no prefactor). (2 files)

- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/exterior.py`

### partial evaluation

Fixing the first $j$ slots of a multilinear map, $T(a_1,\dots,a_j,\cdot,\dots)$ (index lowering/raising). (2 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/partial_eval.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/partial_eval_rules.py`

### Poisson bracket

$\{f,g\}=\pi(df,dg)$; antisymmetric, Leibniz; Jacobi identity under the declaration $[\pi,\pi]_{SN}=0$. (4 files)

- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/koszul_forms.py`, `jacopy/packages/poisson/symplectic.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/realize.py`

### Poisson structure

Bivector $\pi$ with $[\pi,\pi]_{SN}=0$; $\pi^\sharp:T^*M\to TM$. (14 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/properties.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/multivector.py`, `jacopy/central/objects/musical.py`, `jacopy/central/objects/tilde_interior.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/component_workflow.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/poisson_bialgebroid.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/dialect_bridge.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/r_twisted.py`, `jacopy/packages/generalized/roytenberg_courant.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/tangent.py`, `jacopy/oracle/values.py`

### Predator

$P_\Phi(u,v)=\Phi[u,v]_E-[\Phi u,\Phi v]$: the failure to be a bracket morphism; $P_\rho\equiv0\iff$ anchor morphism (sign note in the appendix). (3 files)

- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/defect_formulas.py`, `jacopy/central/algebroid/operators.py`, `jacopy/central/algebroid/theorems.py`

### proof chain

Step-by-step record of an equality (before → after, rule used, assumption relied on). (13 files)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/theorems.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/koszul_jacobi.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/_cited_rule.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/chain.py`, `jacopy/proof/diagnostics.py`, `jacopy/proof/replay.py`, `jacopy/proof/result.py`, `jacopy/proof/search.py`, `jacopy/proof/step.py`, `jacopy/proof/strategies.py`, `jacopy/proof/theorems.py`, `jacopy/proof/verifier.py`

## R

### research interface

The layer in which the user builds and tests their own structure (sections $U\oplus\omega_2\oplus\omega_5$, block matrix $\Psi$, axiom set). (9 files)

- {ref}`research <mct-jacopy-research>`: `jacopy/research/__init__.py`, `jacopy/research/antisymmetrize.py`, `jacopy/research/axiom_suite.py`, `jacopy/research/block_matrix.py`, `jacopy/research/engine_assembly.py`, `jacopy/research/nambu_kind.py`, `jacopy/research/providers.py`, `jacopy/research/sections.py`, `jacopy/research/structure_kinds.py`

### rewrite rule

Left-hand side → right-hand side rewrite rule (`*Definition`, `*Declaration`). (29 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/equality.py`, `jacopy/core/wildcards.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/rewrite.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/endomorphism.py`, `jacopy/central/objects/multivector_interior.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`, `jacopy/central/calculus/indexed_rules.py`, `jacopy/central/calculus/interior_rules.py`, `jacopy/central/calculus/partial_eval_rules.py`, `jacopy/central/calculus/slot_rules.py`, `jacopy/central/calculus/symmetrize_rules.py`, `jacopy/central/calculus/tensor_calculus.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/definitions.py`, `jacopy/central/tangent/lie_bracket.py`, `jacopy/central/tangent/schouten.py`, `jacopy/central/tangent/tangent_expansion.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/algebroid_expansion.py`, `jacopy/central/algebroid/declarations.py`, `jacopy/central/algebroid/locality.py`, `jacopy/central/algebroid/operators.py`, `jacopy/central/algebroid/rules.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/decomposition.py`, `jacopy/packages/metric_affine/metric_affine_expansion.py`, `jacopy/packages/metric_affine/rules.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/_cited_rule.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/engine_assembly.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/expansion.py`, `jacopy/proof/search.py`

### Ricci/Einstein

$\mathrm{Ric}(Y,Z)=\operatorname{tr}(X\mapsto R(X,Y)Z)$, scalar $g^{ab}\mathrm{Ric}_{ab}$, $G_{ab}=\mathrm{Ric}_{ab}-\tfrac12 g_{ab}\,g^{cd}\mathrm{Ric}_{cd}$. (1 file)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/frame_components.py`

## S

### scalar multiplication

Multiplication $c\cdot x$ by an ℝ-constant or a function; ℝ-constants produce no Koszul sign. (5 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/expr.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/product_rule.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/tensor.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/lie_bracket.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/sections.py`

### Schouten–Nijenhuis bracket

$[\cdot,\cdot]_{SN}$: the graded bracket extending $[X,Y]$ to multivectors, $|[P,Q]_{SN}|=p+q-1$. (11 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/properties.py`
- {ref}`brackets <mct-jacopy-brackets>`: `jacopy/brackets/base.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/__init__.py`, `jacopy/central/tangent/schouten.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/core.py`, `jacopy/packages/poisson/koszul_jacobi.py`, `jacopy/packages/poisson/showcase.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/roytenberg.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/r_twisted.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/models/tangent.py`, `jacopy/oracle/values.py`

### symplectic form

Closed non-degenerate 2-form $\omega$; $\pi=\omega^{-1}$. (1 file)

- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/symplectic.py`

## T

### tensor

$(q,r)$-tensor, product $\otimes$; $C^\infty$-multilinear. (14 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/multi_eval.py`, `jacopy/core/symmetrize.py`, `jacopy/core/tensor_product.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/connection.py`, `jacopy/central/objects/metric.py`, `jacopy/central/objects/partial_eval.py`, `jacopy/central/objects/tensor.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/partial_eval_rules.py`, `jacopy/central/calculus/symmetrize_rules.py`, `jacopy/central/calculus/tensor_calculus.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/modified.py`, `jacopy/packages/metric_affine/torsion_curvature.py`

### theorem builder

A `prove_*` function: proves an identity on generic objects and returns the proof chain. (11 files)

- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/anholonomy.py`, `jacopy/central/tangent/cartan.py`, `jacopy/central/tangent/definitions.py`, `jacopy/central/tangent/exterior.py`, `jacopy/central/tangent/lie_bracket.py`, `jacopy/central/tangent/schouten.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/calculus.py`, `jacopy/central/algebroid/defect_formulas.py`, `jacopy/central/algebroid/theorems.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/_cited_rule.py`
- {ref}`proof <mct-jacopy-proof>`: `jacopy/proof/theorems.py`

### tilde calculus

Calculus of the cotangent algebroid $(\tilde d,\tilde{\mathcal L},\tilde\iota)$, $\tilde{\mathcal L}_\alpha=\tilde d\tilde\iota_\alpha+\tilde\iota_\alpha\tilde d$. (13 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/tilde_interior.py`
- {ref}`packages/poisson <mct-jacopy-packages-poisson>`: `jacopy/packages/poisson/tilde.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/bracket_morphism.py`, `jacopy/packages/drinfeld/double.py`, `jacopy/packages/drinfeld/metric_invariance.py`, `jacopy/packages/drinfeld/poisson_bialgebroid.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/tilde_calculus.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/exceptional_double.py`, `jacopy/packages/generalized/poisson_generalized.py`, `jacopy/packages/generalized/r_twisted.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/nambu_kind.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

### torsion

$T(X,Y)=\nabla_XY-\nabla_YX-[X,Y]$ (on E the locality-corrected $^{L}T$). (11 files)

- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/admissible.py`, `jacopy/packages/metric_affine/bianchi.py`, `jacopy/packages/metric_affine/e_bianchi.py`, `jacopy/packages/metric_affine/e_cartan.py`, `jacopy/packages/metric_affine/e_connection.py`, `jacopy/packages/metric_affine/e_koszul.py`, `jacopy/packages/metric_affine/frame_components.py`, `jacopy/packages/metric_affine/metric.py`, `jacopy/packages/metric_affine/metric_koszul.py`, `jacopy/packages/metric_affine/modified.py`, `jacopy/packages/metric_affine/torsion_curvature.py`

### twist (Ψ, B, Π, R)

Transport by a bundle automorphism $[u,v]_\Psi=\Psi^{-1}[\Psi u,\Psi v]$; $\Psi_B$, $\Psi_\Pi$, R-twist $R'(\omega,\eta)=[\Pi\omega,\Pi\eta]-\Pi[\omega,\eta]$. (13 files)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/endomorphism.py`
- {ref}`packages/drinfeld <mct-jacopy-packages-drinfeld>`: `jacopy/packages/drinfeld/examples.py`, `jacopy/packages/drinfeld/roytenberg.py`, `jacopy/packages/drinfeld/twist.py`
- {ref}`packages/generalized <mct-jacopy-packages-generalized>`: `jacopy/packages/generalized/bourbaki_severa.py`, `jacopy/packages/generalized/exceptional_double.py`, `jacopy/packages/generalized/exceptional_rotation.py`, `jacopy/packages/generalized/general_twist.py`, `jacopy/packages/generalized/r_twisted.py`, `jacopy/packages/generalized/roytenberg_courant.py`, `jacopy/packages/generalized/twisted_courant.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/axiom_suite.py`, `jacopy/research/block_matrix.py`

### type system

Determination of the kind and degree of an expression (`kind_of`: function, section, form, multivector …). (1 file)

- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/kind.py`

## V

### vector bundle

The vector bundle $E\to M$ on which the objects live (default $TM$), sections $\Gamma(E)$. (8 files)

- {ref}`central (root) <mct-jacopy-central-root>`: `jacopy/central/__init__.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/bundle.py`, `jacopy/central/objects/form.py`, `jacopy/central/objects/vector_field.py`
- {ref}`central/algebroid <mct-jacopy-central-algebroid>`: `jacopy/central/algebroid/context.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/e_connection.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/block_matrix.py`, `jacopy/research/sections.py`

### vector field

$X\in\mathfrak X(M)=\Gamma(TM)$ (or $\Gamma(E)$), acting on functions as a derivation, $X(f)$. (7 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/pairing.py`
- {ref}`algebra <mct-jacopy-algebra>`: `jacopy/algebra/lie_bracket_vf.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/vector_field.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/lie_bracket.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/torsion_curvature.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

## W

### wedge product

$\alpha\wedge\beta=(-1)^{|\alpha||\beta|}\beta\wedge\alpha$; determinant convention $(\alpha\wedge\beta)(X,Y)=\alpha(X)\beta(Y)-\alpha(Y)\beta(X)$. (16 files)

- {ref}`core <mct-jacopy-core>`: `jacopy/core/wedge.py`
- {ref}`algorithms <mct-jacopy-algorithms>`: `jacopy/algorithms/distribute.py`, `jacopy/algorithms/normalize_alternating.py`, `jacopy/algorithms/product_rule.py`
- {ref}`central/objects <mct-jacopy-central-objects>`: `jacopy/central/objects/__init__.py`, `jacopy/central/objects/form.py`, `jacopy/central/objects/multivector_interior.py`
- {ref}`central/calculus <mct-jacopy-central-calculus>`: `jacopy/central/calculus/bracket_calculus.py`, `jacopy/central/calculus/indexed_rules.py`, `jacopy/central/calculus/slot_rules.py`
- {ref}`central/tangent <mct-jacopy-central-tangent>`: `jacopy/central/tangent/cartan_rules.py`, `jacopy/central/tangent/schouten.py`
- {ref}`packages/metric_affine <mct-jacopy-packages-metric-affine>`: `jacopy/packages/metric_affine/e_cartan.py`, `jacopy/packages/metric_affine/frame_components.py`
- {ref}`research <mct-jacopy-research>`: `jacopy/research/engine_assembly.py`
- {ref}`oracle <mct-jacopy-oracle>`: `jacopy/oracle/values.py`

