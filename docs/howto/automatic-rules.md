# Rules the engine applies automatically

The rules on this page are not written by the user. The engines, the simplifier and the
oracle apply them, and their names appear as step names in proof chains. Use this page to
find out what a rule named in a proof step does, and which optional rules can be added to
an engine.

"Always on" means that the rule is part of the ready-made engine named in parentheses.
"Optional" rules are added with `eng.register(...)`, as shown on the
[Running proofs](running-proofs.md) page. Rules that implement an algebroid axiom are
switched on only by the corresponding declaration (see [Algebroids](algebroids.md)).
Labels such as [B (4.4)] or [MC (3.10)] give the source of a definition; the abbreviations
are listed in the [bibliography](../reference/bibliography.md). The "File" column gives the
source file under `jacopy/`.

The rules specific to the geometry packages are listed on the package pages:
[Poisson](poisson.md), [Drinfel'd doubles](drinfeld.md),
[generalized geometry](generalized-geometry.md), [metric-affine](metric-affine.md) and
[your own structure](your-own-structure.md).

## Rewrite rules

| Name | Mathematics (what the engine does) | Where switched on | File |
|---|---|---|---|
| `MultivectorInteriorLinearityDefinition` | $\iota_{fP+Q}=f\iota_P+\iota_Q$ | optional: `eng.register(MultivectorInteriorLinearityDefinition(reg))` (`from jacopy.central.objects.multivector_interior import MultivectorInteriorLinearityDefinition`) | `central/objects/multivector_interior.py` |
| `MultivectorInteriorDecomposableDefinition` | $\iota_{X_1\wedge\dots\wedge X_p}\omega=\iota_{X_p}(\cdots\iota_{X_1}\omega)$ | optional: `eng.register(MultivectorInteriorDecomposableDefinition())` (`from jacopy.central.objects.multivector_interior import MultivectorInteriorDecomposableDefinition`) | `central/objects/multivector_interior.py` |
| `MultivectorInteriorDecomposableFormDefinition` | $\iota_P(\alpha_1\wedge\dots\wedge\alpha_q)=\sum_{\lvert I\rvert=p}\mathrm{sgn}(I,I^c)\,P(\alpha_I)\,\alpha_{I^c}$ ($q\ge p\ge2$; sign convention consistent with the previous rule) | optional: `eng.register(MultivectorInteriorDecomposableFormDefinition(reg))` (`from jacopy.central.objects.multivector_interior import MultivectorInteriorDecomposableFormDefinition`) | `central/objects/multivector_interior.py` |
| `MultivectorWedgeEvalDefinition` | $(X_1\wedge\dots\wedge X_p)(\alpha_1..\alpha_p)=\sum_\sigma\mathrm{sgn}\sigma\prod_i\langle\alpha_i,X_{\sigma(i)}\rangle$ | optional: `eng.register(MultivectorWedgeEvalDefinition())` (`from jacopy.central.objects.multivector_interior import MultivectorWedgeEvalDefinition`) | `central/objects/multivector_interior.py` |
| `EndoLinearityDefinition` | $m(X+Y)=mX+mY$, $m(fX)=f\,m(X)$ (tensoriality) | optional: `eng.register(EndoLinearityDefinition(reg))` (`from jacopy.central.objects.endomorphism import EndoLinearityDefinition`) | `central/objects/endomorphism.py` |
| `EndoInverseDefinition` | $m^{-1}(m(x))=x$, $m(m^{-1}(x))=x$ | optional: `eng.register(EndoInverseDefinition())` (`from jacopy.central.objects.endomorphism import EndoInverseDefinition`) | `central/objects/endomorphism.py` |
| `IntrinsicDDefinition` | expansion of $d$ by the Palais formula; $\langle d f,X\rangle=\rho(X)f$ | always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/bracket_calculus.py` |
| `IntrinsicLDefinition` | canonical definition of $\mathcal L_X$ (three cases) | always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/bracket_calculus.py` |
| `HeadSumDefinition`, `HeadScalarDefinition` | evaluation is additive and $C^\infty$-linear in the form slot: $\langle f\alpha,Y\rangle=f\langle\alpha,Y\rangle$ | `HeadSumDefinition`: always on (`tangent_engine` and `algebroid_engine`); `HeadScalarDefinition`: always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/bracket_calculus.py` |
| `SlotNegDefinition`, `SlotZeroDefinition`, `MultiEvalArgLinearityDefinition`, `PairingVectorScalarDefinition` | multilinearity of evaluation in the argument slots | `SlotNegDefinition`: always on (`tangent_engine` and `algebroid_engine`); `SlotZeroDefinition`: always on (`tangent_engine` and `algebroid_engine`); `MultiEvalArgLinearityDefinition`: optional: `eng.register(MultiEvalArgLinearityDefinition(reg))` (`from jacopy.central.calculus.bracket_calculus import MultiEvalArgLinearityDefinition`); `PairingVectorScalarDefinition`: always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/bracket_calculus.py` |
| `ActExpansionDefinition` | product rule ($\mathbb R$-linearity + graded Leibniz) | optional: `eng.register(ActExpansionDefinition(reg))` (`from jacopy.central.calculus.bracket_calculus import ActExpansionDefinition`) | `central/calculus/bracket_calculus.py` |
| `HeadFormProductLiftDefinition` | $\alpha\cdot\beta=\alpha\wedge\beta$ in the head of an evaluation | optional: `eng.register(HeadFormProductLiftDefinition(reg))` (`from jacopy.central.calculus.bracket_calculus import HeadFormProductLiftDefinition`) | `central/calculus/bracket_calculus.py` |
| `OperatorSlotAdditivityDefinition` | $\mathcal L_{X+Y}=\mathcal L_X+\mathcal L_Y$; **not** $C^\infty$-linearity, $\mathcal L_{fX}\ne f\mathcal L_X$ | optional: `eng.register(OperatorSlotAdditivityDefinition())` (`from jacopy.central.calculus.bracket_calculus import OperatorSlotAdditivityDefinition`) | `central/calculus/bracket_calculus.py` |
| `InteriorActDefinition` | $\iota_Xf=0$, for a 1-form $\iota_X\omega=\langle\omega,X\rangle$ | always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/interior_rules.py` |
| `InteriorEvalDefinition` | $(\iota_X\omega)(Y_1..Y_k)=\omega(X,Y_1..Y_k)$ | always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/interior_rules.py` |
| `InteriorVectorLinearityDefinition` | $\iota_{fX+Y}=f\iota_X+\iota_Y$ (tensorial in the vector slot) | optional: `eng.register(InteriorVectorLinearityDefinition(reg))` (`from jacopy.central.calculus.interior_rules import InteriorVectorLinearityDefinition`) | `central/calculus/interior_rules.py` |
| `SymAltEvalDefinition` | $\mathrm{Sym}$ and $\mathrm{Alt}$ expanded under evaluation | always on (`tangent_engine` and `algebroid_engine`) | `central/calculus/symmetrize_rules.py` |
| `IndexedSumLinearityDefinition` | $\sum_s(a+b)=\sum_sa+\sum_sb$; factors independent of the bound index are pulled out (the product is not commutative, the order is preserved) | optional: `eng.register(IndexedSumLinearityDefinition(reg))` (`from jacopy.central.calculus.indexed_rules import IndexedSumLinearityDefinition`) | `central/calculus/indexed_rules.py` |
| `IndexedSumEvalPushInDefinition` | $(\sum_s\omega_s)(X..)=\sum_s\omega_s(X..)$ | optional: `eng.register(IndexedSumEvalPushInDefinition())` (`from jacopy.central.calculus.indexed_rules import IndexedSumEvalPushInDefinition`) | `central/calculus/indexed_rules.py` |
| `WedgeEvalDefinition` | $(\alpha_1\wedge..\wedge\alpha_n)(X_1..X_n)=\sum_\sigma\mathrm{sgn}\sigma\prod_i\langle\alpha_i,X_{\sigma(i)}\rangle$ | optional: `eng.register(WedgeEvalDefinition(reg))` (`from jacopy.central.calculus.indexed_rules import WedgeEvalDefinition`) | `central/calculus/indexed_rules.py` |
| `KroneckerContractionDefinition` | $\sum_s\delta^s_c\,t(s)=t(c)$ | optional: `eng.register(KroneckerContractionDefinition())` (`from jacopy.central.calculus.indexed_rules import KroneckerContractionDefinition`) | `central/calculus/indexed_rules.py` |
| `PartialEvalCollapseDefinition` | $T(a,\cdot)(b)=T(a,b)$ | always on (`tangent_engine`) | `central/calculus/partial_eval_rules.py` |
| `PartialEvalLinearityDefinition` | multilinearity in the fixed slots | always on (`tangent_engine`) | `central/calculus/partial_eval_rules.py` |
| `AlternatingPartialEvalAsInteriorDefinition` | $\omega(X_1..X_j,\cdot..)=\iota_{X_j}\cdots\iota_{X_1}\omega$ (non-leading slots with the permutation sign) | always on (`tangent_engine`) | `central/calculus/partial_eval_rules.py` |
| `MusicalAsPartialEvalDefinition` | $g^\flat(X)=g(X,\cdot)$, $\pi^\sharp(\alpha)=\pi(\alpha,\cdot)$ | always on (`tangent_engine`) | `central/calculus/partial_eval_rules.py` |
| `TensorLieEvalDefinition` | $(\mathcal L_XT)(a_1..)=\rho(X)(T(a_1..))-\sum_iT(..,\mathcal L_Xa_i,..)$ | always on (`tangent_engine`) | `central/calculus/tensor_calculus.py` |
| `TensorCovariantEvalDefinition` | $(\nabla_XT)(a_1..)=X(T(a_1..))-\sum_iT(..,\nabla_Xa_i,..)$ | optional: `eng.register(TensorCovariantEvalDefinition(reg))` (`from jacopy.central.calculus.tensor_calculus import TensorCovariantEvalDefinition`) | `central/calculus/tensor_calculus.py` |
| `PairingArgSplitDefinition` | $\langle\alpha,X+Y\rangle=\langle\alpha,X\rangle+\langle\alpha,Y\rangle$ | optional: `eng.register(PairingArgSplitDefinition())` (`from jacopy.central.calculus.slot_rules import PairingArgSplitDefinition`) | `central/calculus/slot_rules.py` |
| `FormProductToWedgeDefinition` | $\alpha\cdot\beta=\alpha\wedge\beta$ | optional: `eng.register(FormProductToWedgeDefinition(reg))` (`from jacopy.central.calculus.slot_rules import FormProductToWedgeDefinition`) | `central/calculus/slot_rules.py` |
| `WedgeSumScalarDefinition` | distributivity of the wedge over sums; $\alpha\wedge f=f\alpha$ | optional: `eng.register(WedgeSumScalarDefinition(reg))` (`from jacopy.central.calculus.slot_rules import WedgeSumScalarDefinition`) | `central/calculus/slot_rules.py` |
| `WedgeZeroNegDefinition` | $0\wedge\alpha=0$, $(-\alpha)\wedge\beta=-(\alpha\wedge\beta)$ | optional: `eng.register(WedgeZeroNegDefinition())` (`from jacopy.central.calculus.slot_rules import WedgeZeroNegDefinition`) | `central/calculus/slot_rules.py` |
| `TrivialZeroSumDefinition` | $0+(-0)+\dots=0$ | optional: `eng.register(TrivialZeroSumDefinition())` (`from jacopy.central.calculus.slot_rules import TrivialZeroSumDefinition`) | `central/calculus/slot_rules.py` |
| `LieBracketActionDefinition` | $[X,Y](f)\to X(Y(f))-Y(X(f))$ | always on (`tangent_engine` and `algebroid_engine`) | `central/tangent/lie_bracket.py` |
| `ScalarActAsMultiplicationDefinition` | $(f\cdot V)(g)=f\,V(g)$ ($C^\infty$-module structure of vector fields) | always on (`tangent_engine` and `algebroid_engine`) | `central/tangent/lie_bracket.py` |
| `BracketOrientationDefinition` | $[B,A]\to-[A,B]$, $[A,A]\to0$ (canonical form based on the antisymmetry theorem) | always on (`tangent_engine`) | `central/tangent/lie_bracket.py` |
| `LieBracketLeibnizDefinition` | $[fX,Y]=f[X,Y]-Y(f)X$, $[X,fY]=f[X,Y]+X(f)Y$, additivity (a theorem; not registered in the TM engine, packages switch it on optionally) | optional: `eng.register(LieBracketLeibnizDefinition(reg))` (`from jacopy.central.tangent.lie_bracket import LieBracketLeibnizDefinition`) | `central/tangent/lie_bracket.py` |
| `CovariantScalarActionDefinition` | $\nabla_Xf=X(f)$ (only for a connection on $TM$) | always on (`tangent_engine`) | `central/tangent/definitions.py` |
| `FrameDualityDefinition` | $\langle e^a,e_b\rangle=\delta^a_b$ | always on (`tangent_engine`) | `central/tangent/definitions.py` |
| `MagicFormulaDefinition` | $\mathcal L_X\omega\to\iota_Xd\omega+d\iota_X\omega$ ($\deg\omega\ge1$; proved separately for each degree $p=1,\dots,5$ in the test suite; not proved for symbolic $p$) | optional: `eng.register(MagicFormulaDefinition(reg))` (`from jacopy.central.tangent.cartan_rules import MagicFormulaDefinition`) | `central/tangent/cartan_rules.py` |
| `LieIotaCommutatorDefinition` | $\iota_{[X,Y]}=\mathcal L_X\iota_Y-\iota_Y\mathcal L_X$ | optional: `eng.register(LieIotaCommutatorDefinition())` (`from jacopy.central.tangent.cartan_rules import LieIotaCommutatorDefinition`) | `central/tangent/cartan_rules.py` |
| `DSquaredZeroDefinition` | $d(dx)\to0$ (proved separately for each degree $p=1,\dots,5$ in the test suite; not proved for symbolic $p$) | optional: `eng.register(DSquaredZeroDefinition())` (`from jacopy.central.tangent.cartan_rules import DSquaredZeroDefinition`) | `central/tangent/cartan_rules.py` |
| `DWedgeLeibnizDefinition` | $d(\alpha_1\wedge..\wedge\alpha_n)=\sum_i(-1)^{\deg\alpha_1+..+\deg\alpha_{i-1}}\alpha_1\wedge..d\alpha_i..\wedge\alpha_n$ | optional: `eng.register(DWedgeLeibnizDefinition(reg))` (`from jacopy.central.tangent.cartan_rules import DWedgeLeibnizDefinition`) | `central/tangent/cartan_rules.py` |
| `FrameBracketCoefficientDefinition` | $\langle e^c,[e_a,e_b]\rangle\to\gamma^c_{ab}$ | always on (`tangent_engine`) | `central/tangent/anholonomy.py` |
| `SNExpansionDefinition` | definitional expansion of $[P,Q]_{SN}$ | always on (`tangent_engine`) | `central/tangent/schouten.py` |
| `SNOrientationDefinition` | $[a,b]\to-(-1)^{(p-1)(q-1)}[b,a]$ (graded antisymmetry; mechanically verified in degrees $(1,1),(2,1),(2,2),(3,2),(3,3)$) | always on (`tangent_engine`) | `central/tangent/schouten.py` |
| `LieOnMultivectorDefinition` | $\mathcal L_XP=[X,P]_{SN}$ for $\deg P\ge2$ | always on (`tangent_engine`) | `central/tangent/schouten.py` |
| `AnchorLinearityDefinition` | $\rho(fu+v)=f\rho(u)+\rho(v)$ | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `BracketBilinearityDefinition` | $[\cdot,\cdot]_E$ is $\mathbb R$-bilinear: sums and **numerical** coefficients are pulled out, $C^\infty$ coefficients are not | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `CoboundaryPairingDefinition` | $\langle Df,u\rangle=\rho(u)(f)$ | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `LocalityMultilinearityDefinition` | $L$ is $C^\infty$-multilinear in all three slots | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `MetricBilinearityDefinition`, `MetricSymmetryDefinition` | $g$ is $C^\infty$-bilinear, $g(v,u)=g(u,v)$ | `MetricBilinearityDefinition`: always on (`algebroid_engine`); `MetricSymmetryDefinition`: always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `MetricSharpEvaluationDefinition` | $g(g^{-1}\omega,w)=\langle\omega,w\rangle$ | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `MetricSharpLinearityDefinition` | $g^{-1}$ is $C^\infty$-linear | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `CoboundaryLinearityDefinition` | $D(f+g)=Df+Dg$, $D(c)=0$, $D(fg)=fDg+gDf$ (theorem-classified; its proof is pairing with a generic section, acyclic) | always on (`algebroid_engine`) | `central/algebroid/rules.py` |
| `RightLeibnizDeclaration` | $[u,fv]_E=\rho(u)(f)v+f[u,v]_E$ [B (4.4)/MC (3.10)] | switched on by `algebroid(..., declare=("right-leibniz",))` | `central/algebroid/declarations.py` |
| `LeftLeibnizDeclaration` | $[fu,v]_E=-\rho(v)(f)u+f[u,v]_E+L(Df,u,v)$ [MC (3.11)] | switched on by `algebroid(..., declare=("left-leibniz",))` | `central/algebroid/declarations.py` |
| `AnchorMorphismDeclaration` | $\rho([u,v]_E)=[\rho u,\rho v]_{\mathrm{Lie}}$ [B (4.5)/MC (3.19)] | switched on by `algebroid(..., declare=("anchor-morphism",))` | `central/algebroid/declarations.py` |
| `JacobiDeclaration` | $J^E(u,v,w)=0$ (Leibniz–Jacobi [B (4.6)], carried by the Jacobiator node) | switched on by `algebroid(..., declare=("jacobi",))` | `central/algebroid/declarations.py` |
| `AntisymmetryDeclaration` | $[v,u]_E=-[u,v]_E$, $[u,u]=0$ | switched on by `algebroid(..., declare=("antisymmetric",))` | `central/algebroid/declarations.py` |
| `MetricInvarianceDeclaration` | $\rho(u)g(v,w)=g([u,v],w)+g(v,[u,w])$ (C1, [B (4.10)]) | switched on by `algebroid(..., declare=("metric-invariance",))` | `central/algebroid/declarations.py` |
| `SymmetricPartDeclaration` | $[u,v]_E+[v,u]_E=g^{-1}Dg(u,v)$ (C2, [B Def 4.2-4.3]; applied only in the summing direction, to avoid loops) | switched on by `algebroid(..., declare=("symmetric-part",))` | `central/algebroid/declarations.py` |
| `declaration_rules` | ordered list of the declared rules | `algebroid_engine` builds this list itself from the declarations (not called by the user) | `central/algebroid/declarations.py` |
| `MappedSectionLinearityDefinition` | $\Phi(fu+v)=f\Phi(u)+\Phi(v)$ | always on (`algebroid_engine`) | `central/algebroid/operators.py` |
| `JacobiatorExpansionDefinition`, `DerivatorExpansionDefinition`, `PredatorExpansionDefinition` | $J(u,v,w)=[u,[v,w]]-[[u,v],w]-[v,[u,w]]$, $D_\Phi(u,v)=\Phi[u,v]-[\Phi u,v]-[u,\Phi v]$, $P_\psi(u,v)=\psi[u,v]_E-[\psi u,\psi v]$ | always on (`algebroid_engine`) | `central/algebroid/operators.py` |
| `LocalityProjectorAbsorptionDefinition` | $\mathcal P L(Df,u,v)=L(Df,u,v)$ ($\hat L\in[\tilde L]$) | switched on by `algebroid_engine(..., projectors=(P,))` | `central/algebroid/locality.py` |
| `LocalityProjectorKernelDefinition` | $\mathrm{im}\,\hat L\subset\ker\rho$ | switched on by `algebroid_engine(..., projectors=(P,))` | `central/algebroid/locality.py` |
| `LocalityProjectorIdempotenceDefinition` | $\mathcal P\mathcal P L=\mathcal P L$ | switched on by `algebroid_engine(..., projectors=(P,))` (if `admissible=True`) | `central/algebroid/locality.py` |
| `ScalarConstantContract` | $D(c)=0$ | structural in every engine (always) | `proof/expansion.py` |
| `ActOverSumOpDefinition` | $(A+B)x=Ax+Bx$ | always on (`tangent_engine` and `algebroid_engine`) | `proof/expansion.py` |

## Automatic algebraic passes (simplifier and product rule)

| Name | Mathematics / function | File |
|---|---|---|
| `swapped(i,j)` | transposition, sign $-1$ | `core/multi_eval.py` |
| `with_dummy` | renaming a dummy index ($\sum_a=\sum_b$) | `core/indexed_sum.py` |
| `substitute_dummy_with` | $\text{body}[d\mapsto t]$ (for the Kronecker contraction $\sum_b\delta_{ab}f(b)=f(a)$; the rule itself lives in the `central` layer) | `core/indexed_sum.py` |
| `flatten` | associative normal form for sums and products | `algorithms/flatten.py` |
| `distribute` | distribution of a product over a sum (two-sided) | `algorithms/distribute.py` |
| `canonicalize` | idempotent normal form | `algorithms/canonicalize.py` |
| `collect_terms` | in $\sum c_i t_i$, adding up the coefficients of the same $t$ | `algorithms/collect_terms.py` |
| `factor_common` | inverse of left distribution | `algorithms/factor_terms.py` |
| `collect_pairings` | $\sum s_i\langle\alpha,V_i\rangle\to\langle\alpha,\sum s_iV_i\rangle$, $\sum s_i\,\eta(Y,\dots,V_i)\to\eta(Y,\dots,\sum s_iV_i)$ (linearity in the last slot) | `algorithms/factor_terms.py` |
| `sort_product` | $(\text{sorted product},\ e)$, result $=(-1)^e\cdot$ sorted product | `algorithms/sort_product.py` |
| `apply_sign` | folds in $(-1)^e$ if the parity of $e$ is known | `algorithms/sort_product.py` |
| `normalize_alternating` | $\omega(Y_{\sigma(1)},\dots)=\operatorname{sgn}\sigma\cdot\omega(Y_1,\dots)$, $\omega(\dots,Y,\dots,Y,\dots)=0$ | `algorithms/normalize_alternating.py` |
| `product_rule` | Leibniz + linearity for all `Act` nodes | `algorithms/product_rule.py` |
| `Rule(lhs, rhs, guard)` | conditional rewrite rule | `algorithms/rewrite.py` |
| `apply_bottomup/topdown/once_at_root` | strategy | `algorithms/rewrite.py` |
| `normalize` / `rewrite_to_fixpoint` | fixed point (normal form) | `algorithms/rewrite.py` |
| `annihilates` | $D(c)=0$ (a derivation kills constants) | `central/calculus/scalars.py` |
| `PASSES` | the two normalization passes run by `show_equal`: `product_rule` and `simplify` | `proof/normalize.py` |
| `CommutatorRecognizer` | $[A,B]$ | `proof/recognizers.py` |
| `LeibnizRecognizer` | $D(a_1a_2\cdots)$ | `proof/recognizers.py` |
| `AntisymmetryRecognizer` | $[A,B]$ as an antisymmetry claim | `proof/recognizers.py` |

## Automatic checks (type, degree, provenance)

| Name | Mathematics / function | File |
|---|---|---|
| `as_degree` | converting an int to a Degree | `core/symbolic_degree.py` |
| `scalar_contract_clash` | contradictory declarations such as "Scalar + Graded(k≠0)" are rejected | `core/properties.py` |
| `structural_equal` | syntactic equality | `core/equality.py` |
| `alpha_equal` | equality up to renaming of bound variables / pattern variables | `core/equality.py` |
| `sum_bag_equal` | order-independent comparison of the terms of a $\sum$ | `core/equality.py` |
| `has_repeated_arg` | the condition $\omega(\dots,Y,\dots,Y,\dots)=0$ | `core/multi_eval.py` |
| `admits_alternation` | alternation is rejected by default; only explicitly certified heads (form/multivector classes) count as alternating | `core/multi_eval.py` |
| `validate_arity` | check that the number of slots = the degree of the head | `core/multi_eval.py` |
| `dummy_in` | whether a free index occurs (taking shadowing into account) | `core/indexed_sum.py` |
| `leibniz` / `section_value` | certificate of "is this operator a derivation, or a value" | `algebra/derivation.py` |
| `is_certified_derivation` | Leibniz may be applied if $D$ is a derivation or $[D_1,D_2]$ is the commutator of two derivations | `algebra/commutator.py` |
| `section_value` | if one of the operands is not a section of $TM$, it does not count as a derivation | `algebra/lie_bracket_vf.py` |
| `semantically_equal` | equality with respect to this normal form (without using Koszul information) | `algorithms/canonicalize.py` |
| `koszul_well_typed` | the Koszul mode only for a bivector $Q$ and 1-forms | `brackets/derived.py` |
| `section_value` | if $E\neq TM$, a section is a "value", not a derivation | `central/objects/vector_field.py` |
| `wedge_factor_degree` | exterior degree used in Leibniz signs | `central/objects/kind.py` |
| `is_section_valued` | test for "valued in a bundle other than $TM$" | `central/objects/kind.py` |
| `is_scalar_function` | test for $f\in C^\infty(M)$ | `central/calculus/scalars.py` |
| `is_real_constant` | test for $c\in\mathbb R$ | `central/calculus/scalars.py` |
| `effective_role` | a rule from outside the library always counts as an "assumption" | `proof/expansion.py` |
| `DerivedBracketStrategy.prove_jacobi` | derived bracket theorem (only for the given triple and verified hypotheses) | `proof/strategies.py` |
| `check_goal` | type/degree compatibility of the two sides | `proof/result.py` |
| `structural_requires` | hypothesis set of the proof | `proof/result.py` |
| `is_substructure` | $\text{decl}(A)\subseteq\text{decl}(B)$ ⇒ a theorem of $A$ holds in $B$ | `proof/ownership.py` |
| `OwnerScope.bind/check/transfer` | name ↔ structure binding | `proof/ownership.py` |
| `AmbiguousOwnerError` | error if two structures are bound to the same name | `proof/ownership.py` |
| `RegistryFact` | (expression, property, value) hypothesis | `proof/registry_facts.py` |
| `unmet` | hypotheses not satisfied in the context | `proof/registry_facts.py` |
| `registry_context` | registry context of the proof | `proof/registry_facts.py` |
| `chain_shape` | whether $E_0=\text{lhs}\to\dots\to E_n=\text{rhs}$ is connected | `proof/replay.py` |
| `accountable` | whether a step was produced by a library rule | `proof/replay.py` |
| `chain_verdict` | hard/soft defects | `proof/replay.py` |
| `stalled_d_squared` | $D^2=0$ ($D$ of odd degree) | `proof/diagnostic_rules.py` |
| `stalled_act_over_zero` | $D(0)=0$ | `proof/diagnostic_rules.py` |
| `unreduced_iota_on_df` | $\iota_V df=V(f)$ | `proof/diagnostic_rules.py` |
| `unclassified_factor` | factor whose degree has not been declared | `proof/diagnostic_rules.py` |
| `OracleDisagreement` | refutation in strict mode | `oracle/hook.py` |

## Formulas used by the oracle model

| Name | Mathematics / function | File |
|---|---|---|
| `Ring` | $\mathbb Q[x_0,\dots,x_{n-1}]$ | `oracle/values.py` |
| `VecV`, `FormV`, `MultiV`, `OpV` | values of vector fields, forms, multivectors, operators | `oracle/values.py` |
| `dwedge` | $dx^I\wedge dx^J=\operatorname{sgn}\,dx^{\text{sort}(IJ)}$ | `oracle/values.py` |
| `dinterior` | $\iota_v dx^I=\sum_k(-1)^k v_{I_k}dx^{I\setminus I_k}$ | `oracle/values.py` |
| `det_eval` | $\omega(X_1..X_p)=\sum_I\omega_I\det[X_j^{I_i}]$ | `oracle/values.py` |
| `d_form` | exterior derivative $d$ | `oracle/values.py` |
| `vf_bracket` | $[X,Y]^i=X(Y^i)-Y(X^i)$ | `oracle/values.py` |
| `lie_form`, `lie_multi` | $\mathcal L_X$ on forms/multivectors | `oracle/values.py` |
| `schouten` / `_sn` | recursive definition of $[P,Q]_{SN}$ (with signs shifted by $s=m-1$) | `oracle/values.py` |
| `sharp` | $\langle\beta,\pi^\sharp\alpha\rangle=\pi(\alpha,\beta)$ | `oracle/values.py` |
| `koszul` | $[\alpha,\beta]_\pi=\mathcal L_{\pi^\sharp\alpha}\beta-\mathcal L_{\pi^\sharp\beta}\alpha-d\,\pi(\alpha,\beta)$ | `oracle/values.py` |
| `tilde_d`, `tilde_lie` | the Palais $\tilde d$ and $\tilde{\mathcal L}$ of the algebroid $(T^*M,\pi^\sharp,[\,,]_\pi)$ | `oracle/values.py` |
| `nambu_sharp` | $(\Pi\omega)(f)=\Pi(\alpha_1,\dots,\alpha_p,df)$ | `oracle/values.py` |
| `e_wedge`, `shuffles` | $(\alpha\wedge\beta)=\sum_{(p,q)\text{-shuffle}}\operatorname{sgn}\sigma\,\alpha\,\beta$ | `oracle/values.py` |
| `SecV`, `EFormV` | sections of $E$ and ordered multilinear $E$-forms | `oracle/values.py` |
| `realize` / `Env.value` / `Env.op` | interpretation (semantic function) | `oracle/realize.py` |
| registered nodes | node classes the oracle can evaluate: `Act`, `Wedge`, `Pairing`, `MultiEval`, `Interior`, `LieDerivative`, `ExteriorDerivative`, `LieBracketVF`, `Commutator`, `BracketApply`, `SharpVF`, `KoszulBracket`, `HamiltonianVF`, `NambuSharpVF`, `PoissonBracketValue`, and others | `oracle/realize.py` |
| `compose`, `op_sum`, `op_scale` | operator algebra | `oracle/realize.py` |
| `e_d` | $d_E$ (Palais) | `oracle/realize_e.py` |
| `e_lie` | $\mathcal L^E_u$ | `oracle/realize_e.py` |
| `Jacobiator` | $J(u,v,w)=[u,[v,w]]-[[u,v],w]-[v,[u,w]]$ (Leibniz form) | `oracle/realize_e.py` |
| `Derivator` | $D_\Phi(u,v)=\Phi[u,v]-[\Phi u,v]-[u,\Phi v]$ | `oracle/realize_e.py` |
| `Predator` | $P_\Phi(u,v)=\Phi[u,v]_E-[\Phi u,\Phi v]_{\text{Lie}}$ | `oracle/realize_e.py` |
| anholonomy | $\gamma^c_{ab}=\langle e^c,[e_a,e_b]\rangle$ | `oracle/realize_e.py` |
| `LocalityOperator` | the $L$ in $[fu,v]=-\rho(v)(f)u+f[u,v]+L(Df,u,v)$ | `oracle/realize_e.py` |
| `TangentModel` | random functions, vector fields, forms and multivectors on $\mathbb R^n$ | `oracle/models/tangent.py` |
| `structure_bivector` | Poisson / counter-model / generic $\pi$ | `oracle/models/tangent.py` |
| `test_arguments` | test basis for operator identities (forms and multivectors of every degree) | `oracle/models/tangent.py` |
| `OracleSelfCheckError` | if the model does not satisfy its claim | `oracle/models/tangent.py` |
| `EStructure` | $(E,\rho,[\,,],g,L)$, with verified axioms | `oracle/models/algebroid.py` |
| `anchor` | $\rho(u)=u^a\rho_a$ | `oracle/models/algebroid.py` |
| `D` | $(Df)_a=\rho_a(f)$ | `oracle/models/algebroid.py` |
| `sharp` | $g^{-1}$ | `oracle/models/algebroid.py` |
| `build_structure` | structure from the family, $n$, $r$ | `oracle/models/algebroid.py` |
| `AlgebroidModel.frame` | unit upper-triangular polynomial frame (det = 1) | `oracle/models/algebroid.py` |
| `section_map` | $C^\infty$-linear $\Phi:E\to TM$ or $E\to E$ | `oracle/models/algebroid.py` |
| `plan_algebroids` | model plan | `oracle/select.py` |
| `cover` | greedy set cover for axiom violations | `oracle/select.py` |
| `closure` | derivable closure of the axioms used | `oracle/select.py` |
| `leak_counter_plans` | counter-model for an unused axiom | `oracle/select.py` |
| `index_assignments` | values of free indices (equal/not equal) | `oracle/select.py` |
| `max_exterior_degree` | $D$ | `oracle/check.py` |
| `degree_range` | samples of symbolic degrees | `oracle/check.py` |
| `values_equal` | operator equality (same value on every test argument) | `oracle/check.py` |
