# Running proofs

Expressions are inert until an engine works on them. This page shows how to choose an
engine, the three ways to ask for a proof, how to read the result, the ready-made theorem
builders for $TM$ and for algebroids, how to switch on optional rules, how to store and cite
theorems, and how to write a rule of your own.

## Setup

```python
import jacopy
from jacopy.core import Degree, Scalar, Closed
from jacopy.central.algebroid import algebroid, tangent_algebroid, section_map, locality_projector

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta = jacopy.forms("alpha beta", degree=1)
(omega,) = jacopy.forms("omega", degree=2)
pi = jacopy.bivector("pi")
(T,) = jacopy.tensors("T", upper=1, lower=2)
nabla = jacopy.connection()
e = jacopy.frame("e")
reg.declare(omega, Closed())

E = algebroid("E", declare=("leibniz",)); u, v, w = E.sections("u v w")
A = algebroid("A"); a1, a2, a3 = A.sections("u v w")
(muA,) = jacopy.forms("mu", degree=1, bundle=A.bundle)
K = algebroid("K", declare=("lie", "anchor-morphism")); k1, k2, k3 = K.sections("u v w")
(muK,) = jacopy.forms("mu", degree=1, bundle=K.bundle)
C = algebroid("C", declare=("courant",)); c1, c2, c3 = C.sections("u v w")
R = algebroid("R", declare=("local", "regular")); Pr = locality_projector(R)
Lp = algebroid("Lp", declare=("local", "anchor-morphism")); l1, l2 = Lp.sections("u v")
As = algebroid("As", declare=("antisymmetric",)); s1, s2, s3 = As.sections("u v w")
(muS,) = jacopy.forms("mu", degree=1, bundle=As.bundle)

from jacopy.central.tangent import tangent_engine, d, SN
from jacopy.central.algebroid import algebroid_engine
from jacopy.proof.result import prove as prove_result
from jacopy.proof import (SearchStrategy, PortfolioStrategy, ExpandAndSimplify,
    UnrollToFoundations, AgreementOnGenerators, prove_operator_equation, prove_equivalence,
    unroll_property, diagnose, ExplicitAssumption, default_engine)
from jacopy.proof.verifier import prove_jacobi as prove_bracket_jacobi
from jacopy.proof.theorems import check_citation
from jacopy.brackets.derived import derived_bracket
import jacopy.central.tangent as tg
from jacopy.central.tangent.lie_bracket import jacobi_combination_theorems
import jacopy.central.algebroid as ag
import jacopy.central.algebroid.defect_formulas as df
```

## Choosing the engine

An engine is the set of rules a proof may use. For $TM$ use `tangent_engine`; for an
algebroid use `algebroid_engine(E)`, which loads the definitions of $E$ together with its
declared axioms. `algebroid_engine(tangent_algebroid())` returns the tangent engine. Every
engine is given the same `registry=reg`.

```python
eng  = tangent_engine(registry=reg)                          # definitions on TM
engH = tangent_engine(registry=reg, holonomic_frames=(e,))   # + [e_a, e_b] = 0
engE = algebroid_engine(E, registry=reg)                     # definitions + axioms of E
engR = algebroid_engine(R, registry=reg, projectors=(Pr,))   # + projector rules
print(len(eng.definitions), len(engE.definitions), len(engR.definitions))
print(len(default_engine().definitions))                     # structural rule only
```

```text
25 28 30
1
```

## Three ways to prove an identity

| Way | Pattern | Returns | When |
|---|---|---|---|
| {py:func}`jacopy.show_equal` | `jacopy.show_equal(lhs, rhs, registry=reg, engine=eng)` | `ProofChain`; raises `ProofFailure` (with `.residual`) if it does not close | The default. Runs the definitions, the product rule and the simplifier together. |
| {py:func}`jacopy.prove` | `jacopy.prove(lhs, rhs, registry=reg, engine=eng, prefer="shortest")` | `ProofChain` | Without `prefer` it is the same as `show_equal`. With `prefer` (`"shortest"`, `"readable"`, `"elementary"`) it searches several proofs and keeps the best. |
| `jacopy.proof.result.prove` | `prove_result(eng, lhs, rhs, registry=reg)` | `ProofResult` with `status` (`CLOSED`, `RESIDUAL`, `BUDGET`, `INVALID`), `requires`, `residual` and `.summary()` | When you want to see the assumptions a proof closed under. It does not run the product-rule pass, so some identities that `show_equal` closes stay `RESIDUAL` (see the $d(fh)$ example below). If `rhs` is omitted it defaults to zero; pass `jacopy.Zero`, not the Python `0`. |

**`show_equal`: a chain if it closes, `ProofFailure` if it does not.** A residual is the
difference that could not be expanded further; it is not a refutation.

```python
chain = jacopy.show_equal(jacopy.lie_derivative(X)(f*h), X(f)*h + f*X(h),
                          registry=reg, engine=eng)
print("closed:", len(chain.steps), "steps")
try:
    jacopy.show_equal(jacopy.lie_derivative(X)(f*Y), f*jacopy.lie_bracket(X, Y),
                      registry=reg, engine=eng)
except jacopy.ProofFailure as fail:
    print("residual:", fail.residual)
```

```text
closed: 3 steps
residual: (X(f) * Y)
```

**`prove_result`: status and assumptions.**

```python
res = prove_result(eng, jacopy.lie_derivative(X)(Y), jacopy.lie_bracket(X, Y), registry=reg)
print(res.status, res.closed, "|", res.goal)
print(res.summary())
res2 = prove_result(eng, jacopy.multi_eval(d(d(f)), X, Y), registry=reg)   # rhs defaults to 0
print(res2.status)
res3 = prove_result(eng, d(f*h), f*d(h) + h*d(f), registry=reg)
print(res3.status, "| residual:", res3.residual)
print([str(a) for a in res3.requires][:2])
```

```text
CLOSED True | L_X(Y) = [X,Y]_VF
CLOSED: L_X(Y) = [X,Y]_VF  — assumption-free
  generality: generic-function
  via definition: intrinsic L (Cartan-TM): L_X f = ρ(X)(f), L_X Y = [X,Y], (L_X ω)(Y…) = ρ(X)(ω(Y…)) − Σ ω(…,[X,Y_i],…)
  budget: 1/1024 steps; jacopy 0.1.0a1
CLOSED
RESIDUAL | residual: ((-(d(f) * h)) + (-(d(h) * f)) + d((f * h)))
['registry: registry declaration: Graded(degree=0) on f', 'registry: registry declaration: Graded(degree=0) on h']
```

**`jacopy.prove` and proof strategies.**

```python
lhs, rhs = jacopy.lie_bracket(X, Y)(f), -jacopy.lie_bracket(Y, X)(f)
ch = jacopy.prove(lhs, rhs, registry=reg, engine=eng)                      # = show_equal
ch2 = jacopy.prove(lhs, rhs, registry=reg, engine=eng, prefer="shortest")   # graph search
print(len(ch.steps), len(ch2.steps))
pf = PortfolioStrategy([SearchStrategy(prefer="readable", max_states=200), ExpandAndSimplify()])
print(len(pf.prove(lhs, rhs, registry=reg, engine=eng).steps))
deep = UnrollToFoundations(ExpandAndSimplify()).prove(lhs, rhs, registry=reg, engine=eng)
print(len(deep.steps))
```

```text
5 3
4
5
```

**Normal form, operator identities, diagnosing a residual.**
{py:func}`jacopy.normalize` brings an expression to normal form; `prove_operator_equation`
proves an operator identity by agreement on a set of generators; `diagnose` explains why a
residual stalled.

```python
nf = jacopy.normalize(eng, jacopy.lie_derivative(X)(f*h), reg)
print(nf.expr, nf.converged)

class Functions:                     # generator set for AgreementOnGenerators
    generators = (f,)

ch = prove_operator_equation(jacopy.lie_derivative(X), X, Functions(), registry=reg, engine=eng)
print("L_X = X on functions:", len(ch.steps), "step(s)")
dd = jacopy.exterior_d()             # the operator (d(...) is a shortcut function)
report = diagnose(jacopy.Act(dd, jacopy.Act(dd, f)), registry=reg)
print(report.hints[0].category)
```

```text
((X(f) * h) + (X(h) * f)) True
L_X = X on functions: 1 step(s)
stalled-d-squared
```

**Bracket Jacobi, equivalence, provenance of a declaration, explicit assumptions.**
`ExplicitAssumption(expr, target)` adds a single rewrite $\text{expr}\to\text{target}$ to an
engine; it is recorded as an assumption.

```python
db = derived_bracket(SN, pi)
print(db.jacobi_obstruction())                                  # [pi, pi]_SN
print(prove_equivalence(db, db, alpha, beta, registry=reg).steps == [] or "ok")
print(unroll_property(reg.get(omega, Closed)).steps[0].rule)
engX = tangent_engine(registry=reg)
engX.register(ExplicitAssumption(jacopy.lie_bracket(X, Y), jacopy.Zero))   # only [X, Y] = 0
print(len(jacopy.show_equal(jacopy.lie_bracket(X, Y)(f), jacopy.Zero,
                            registry=reg, engine=engX).steps))
```

```text
[·,·]_SN(pi, pi)
ok
axiom
3
```

## Reading the result

- `ProofResult.status` takes four values:
  - `CLOSED`: the proof closed, under the assumptions listed in `requires`.
  - `RESIDUAL`: both sides were brought to normal form and a difference remained. This is
    **not** a refutation, only a difference that could not be expanded further.
  - `BUDGET`: the step limit was reached.
  - `INVALID`: the types or degrees of the two sides do not match.
- `res.requires` lists everything the proof relies on: declared axioms, declarations read
  from the registry and cited theorems. `res.summary()` prints them in readable form.
- `ProofChain.steps` is the list of steps. Each `ProofStep` carries `rule`, `role` and
  `provenance_tag` (definition, axiom, theorem, assumption), `before` and `after`.
  `chain.initial` and `chain.final` are the two ends of the chain.

```python
chain = tg.prove_cartan_magic_on_functions(X, f, registry=reg)
step = chain.steps[0]
print(step.provenance_tag, "|", step.role, "|", step.before, "->", step.after)
print(chain.initial, "=>", chain.final)
print(len(chain.steps), "steps")
```

```text
axiom | definition | L_X(f) -> X(f)
L_X(f) => 0
6 steps
```

{py:func}`jacopy.print_chain` prints the whole chain as a tree, one node per step, with the
rule that justifies it.

## Ready-made theorem builders: $TM$

These functions prove a theorem for the objects you pass and return the chain. They are
called as `tg.<name>` after `import jacopy.central.tangent as tg`, except
`jacobi_combination_theorems`, which is imported from `jacopy.central.tangent.lie_bracket`.
Argument orders and return types differ between builders; check the "Arguments" and
"Returns" columns.

| Mathematics | In code | Arguments | Returns |
|---|---|---|---|
| $[X,Y]f=-[Y,X]f$ | `tg.prove_antisymmetry(X, Y, f, registry=reg)` | X, Y; f | `ProofChain` |
| $\sum_{\mathrm{cyc}}[X,[Y,Z]]f=0$ | `tg.prove_lie_jacobi(X, Y, Z, f, registry=reg)` | X, Y, Z; f | `ProofChain` |
| Jacobi combination $=0$ (section level, both signs) | `jacobi_combination_theorems(X, Y, Z, f, registry=reg)` | X, Y, Z; f | `(Theorem, Theorem)` |
| $[X,fY](h)=X(f)Y(h)+f[X,Y](h)$ | `tg.prove_leibniz_second_slot(X, f, Y, h, registry=reg)` | X, f, Y, h (mind the order) | `ProofChain` |
| $[X,Y+Z]=[X,Y]+[X,Z]$ | `tg.prove_additivity_second_slot(X, Y, Z, f, registry=reg)` | X, Y, Z; f | `ProofChain` |
| $[cX,Y]=c[X,Y]$ | `tg.prove_scalar_homogeneity(3, X, Y, f, registry=reg)` | c: integer; X, Y; f | `ProofChain` |
| $[fX,Y](h)=f[X,Y](h)-Y(f)X(h)$ | `tg.prove_first_slot_function_linearity(f, X, Y, h, registry=reg)` | f, X, Y, h | `ProofChain` |
| $\nabla_Xf=X(f)$ | `tg.prove_covariant_scalar_action(nabla, X, f, registry=reg)` | connection; X; f | `ProofChain` |
| $\nabla_X(fT)=X(f)T+f\nabla_XT$ | `tg.prove_covariant_leibniz(nabla, X, f, T, registry=reg)` | connection; X; f; T | `ProofChain` |
| $\langle e^a,e_b\rangle=\delta^a_b$ | `tg.prove_frame_duality(e, "a", "b", registry=reg)` | frame; upper, lower index | `ProofChain` |
| $\langle df,X\rangle=X(f)$ | `tg.prove_df_on_vector(X, f, registry=reg)` | X; f | `ProofChain` |
| $(d\alpha)(X,Y)=X\alpha(Y)-Y\alpha(X)-\alpha([X,Y])$ | `tg.prove_one_form_intrinsic(alpha, X, Y, registry=reg)` | 1-form; X, Y | `ProofChain` |
| $(d\,df)(X,Y)=0$ | `tg.prove_d_squared_zero_on_functions(f, X, Y, registry=reg)` | f; X, Y | `ProofChain` |
| $(d\,d\alpha)(X,Y,Z)=0$ | `tg.prove_d_squared_zero_on_one_forms(alpha, X, Y, Z, f, registry=reg)` | 1-form; X, Y, Z; f | `(ProofChain, [Theorem])` |
| $\mathcal L_Xf=\iota_Xdf+d\iota_Xf$ | `tg.prove_cartan_magic_on_functions(X, f, registry=reg)` | X; f | `ProofChain` |
| $\langle\mathcal L_X\alpha,Y\rangle=\langle\iota_Xd\alpha+d\iota_X\alpha,Y\rangle$ | `tg.prove_cartan_magic_on_one_forms(alpha, X, Y, registry=reg)` | 1-form; X, Y | `ProofChain` |
| $\mathcal L_X(df)=d(\mathcal L_Xf)$ | `tg.prove_L_commutes_with_d_on_functions(X, f, Y, registry=reg)` | X; f; Y | `ProofChain` |
| $(\mathcal L_Xd\alpha)(Y,Z)=(d\mathcal L_X\alpha)(Y,Z)$ | `tg.prove_L_commutes_with_d_on_one_forms(alpha, X, Y, Z, f, registry=reg)` | 1-form; X, Y, Z; f | `(ProofChain, [Theorem])` |
| $\mathcal L_X\iota_Y\alpha-\iota_Y\mathcal L_X\alpha=\iota_{[X,Y]}\alpha$ | `tg.prove_L_iota_commutator(alpha, X, Y, registry=reg)` | 1-form; X, Y | `ProofChain` |
| $[\mathcal L_X,\mathcal L_Y]f=\mathcal L_{[X,Y]}f$ | `tg.prove_L_L_commutator_on_functions(X, Y, f, registry=reg)` | X, Y; f | `ProofChain` |
| $[\mathcal L_X,\mathcal L_Y]\alpha=\mathcal L_{[X,Y]}\alpha$ | `tg.prove_L_L_commutator_on_one_forms(alpha, X, Y, Z, f, registry=reg)` | 1-form; X, Y, Z; f | `(ProofChain, [Theorem])` |
| $\iota_X\iota_Y\omega+\iota_Y\iota_X\omega=0$ | `tg.prove_iota_anticommute(omega, X, Y, registry=reg)` | 2-form; X, Y | `ProofChain` |
| $\mathcal L_Ud\iota_W\eta-d\iota_{[U,W]}\eta-d\iota_W\mathcal L_U\eta=0$ | `tg.prove_L_d_iota_commutation(alpha, X, Y, Z, f, registry=reg)` | $\eta$; U, W; Y; f | `(ProofChain, [Theorem])` |
| $\mathcal L_Wd\iota_V\omega-d\iota_Wd\iota_V\omega=0$ | `tg.prove_L_d_iota_exact(alpha, X, Y, Z, f, registry=reg)` | $\omega$: 1-form; V, W; Y; f | `(ProofChain, [Theorem])` |
| general proof with bracket identities | `tg.prove_with_bracket_identities(jacopy.multi_eval(d(d(alpha)), X, Y, Z), jacopy.Zero, f, registry=reg)` | lhs; rhs; f | `(ProofChain, [Theorem])` |
| $\gamma^c_{ab}=-\gamma^c_{ba}$ | `tg.prove_gamma_antisymmetry(e, "c", "a", "b", registry=reg)` | frame; c, a, b | `ProofChain` |
| $de^c(e_a,e_b)=-\gamma^c_{ab}$ | `tg.prove_coframe_differential(e, "c", "a", "b", registry=reg)` | frame; c, a, b | `ProofChain` |
| $\langle e^d,\sum_{\mathrm{cyc}}[e_a,[e_b,e_c]]\rangle=0$ | `tg.prove_frame_jacobi(e, "d", "a", "b", "c", f, registry=reg)` | frame; d, a, b, c; f | `(ProofChain, [Theorem])` |
| $\gamma=0$ in a holonomic frame | `tg.prove_holonomic_gamma_vanishes(e, "c", "a", "b", registry=reg)` | frame; c, a, b | `ProofChain` |
| $[X,Y]_{SN}=[X,Y]$ | `tg.prove_reduces_to_lie(X, Y, f, registry=reg)` | X, Y; f | `ProofChain` |
| $[X,f]_{SN}=X(f)$ | `tg.prove_sn_vector_function(X, f, registry=reg)` | X; f | `ProofChain` |
| $[X,Y\wedge Z]=[X,Y]\wedge Z+Y\wedge[X,Z]$ | `tg.prove_sn_wedge_leibniz(X, Y, Z, registry=reg)` | X, Y, Z | `ProofChain` |
| $[X\wedge Y,Z]_{SN}=-[Z,X\wedge Y]_{SN}$ | `tg.prove_sn_graded_antisymmetry(X, Y, Z, registry=reg)` | X, Y, Z | `ProofChain` |

## Ready-made theorem builders: algebroids

These are called after `import jacopy.central.algebroid as ag` and
`import jacopy.central.algebroid.defect_formulas as df`. Most builders require a hypothesis,
given in parentheses in the "Arguments" column (for example "anchor-morphism must be
declared"). If the hypothesis is missing, the builder raises `ProofFailure` or `ValueError`
instead of assuming it. The `df.` builders compute the defects of the Cartan calculus on an
algebroid with no axioms, in terms of the Predator $\mathcal P$ and related tensors.

| Mathematics | In code | Arguments | Returns |
|---|---|---|---|
| $\langle d_Ef,u\rangle=\rho(u)f$ | `ag.prove_d_on_functions(A, a1, f, registry=reg)` | algebroid; u; f | `ProofChain` |
| $\langle d_Ef,u\rangle=\langle Df,u\rangle$ | `ag.prove_d_coincides_with_coboundary(A, a1, f, registry=reg)` | algebroid; u; f | `ProofChain` |
| $(d_E\mu)(u,v)$ by the Palais formula | `ag.prove_palais_on_one_forms(A, muA, a1, a2, registry=reg)` | algebroid; $\mu$; u, v | `ProofChain` |
| $\mathcal L^E_uf=\rho(u)f$, $\mathcal L^E_uv=[u,v]_E$ | `ag.prove_lie_core_cases(A, a1, a2, f, registry=reg)` | algebroid; u, v; f | `(ProofChain, ProofChain)` |
| $\mathcal L^E_uf=(d_E\iota_u+\iota_ud_E)f$ | `ag.prove_algebroid_cartan_magic_on_functions(A, a1, f, registry=reg)` | algebroid; u; f | `ProofChain` |
| Cartan formula on an $E$-1-form | `ag.prove_algebroid_cartan_magic_on_one_forms(A, a1, muA, a2, registry=reg)` | algebroid; u; $\mu$; v (mind the order) | `ProofChain` |
| $(d_Ed_Ef)(u,v)=0$ | `ag.prove_algebroid_d_squared_zero_on_functions(K, k1, k2, f, registry=reg)` | algebroid (anchor-morphism); u, v; f | `ProofChain` |
| $(d_Ed_E\mu)(u,v,w)=0$ | `ag.prove_algebroid_d_squared_zero_on_one_forms(K, muK, k1, k2, k3, registry=reg)` | algebroid (lie, anchor-morphism); $\mu$; u, v, w | `(ProofChain, [Theorem])` |
| instance theorem $J(u,v,w)=0$ | `ag.jacobi_combination_theorem(E, u, v, w, registry=reg)` | algebroid (jacobi); u, v, w | `Theorem` |
| $\rho([u,v])=[\rho u,\rho v]$ | `ag.prove_anchor_morphism(E, u, v, f, registry=reg)` | algebroid (leibniz); u, v; f | `(ProofChain, Theorem)` |
| $[u,fv]=\rho(u)(f)v+f[u,v]$ from the metric axioms | `ag.prove_right_leibniz_from_metric(C, c1, c2, f, registry=reg)` | algebroid (metric or courant); u, v; f | `(ProofChain, Theorem)` |
| $L(Df,u,v)=g(u,v)\,g^{-1}(Df)$ | `ag.prove_left_leibniz_from_metric(C, c1, c2, f, registry=reg)` | algebroid (metric or courant); u, v; f | `(ProofChain, Theorem)` |
| $\rho(L(Df,u,v))=0$ | `ag.prove_locality_anchor_annihilation(Lp, l1, l2, f, h=h, registry=reg)` | algebroid (local pre-Leibniz); u, v; f; `h=` auxiliary function | `(ProofChain, Theorem)` |
| $P_\rho(u,v)=0$ | `ag.prove_anchor_predator_vanishes(E, u, v, f, registry=reg)` | algebroid (leibniz); u, v; f | `ProofChain` |
| $[\mathcal L_u,\mathcal L_v]f-\mathcal L_{[u,v]}f=\mathcal P(u,v)f$ | `df.prove_defect_lie_lie_on_functions(A, a1, a2, f, registry=reg)` | algebroid; u, v; f | `ProofChain` |
| $(d_Ed_Ef)(u,v)=\mathcal P(u,v)f$ | `df.prove_defect_d_squared_on_functions(A, a1, a2, f, registry=reg)` | algebroid; u, v; f | `ProofChain` |
| $(\mathcal L_ud_Ef-d_E\mathcal L_uf)(v)=\mathcal P(u,v)f$ | `df.prove_defect_lie_d_on_functions(A, a1, a2, f, registry=reg)` | algebroid; u, v; f | `ProofChain` |
| defect of $[\mathcal L_u,\mathcal L_v]-\mathcal L_{[u,v]}$ on $\mu$ | `df.prove_defect_lie_lie_on_one_forms(A, muA, a1, a2, a3, registry=reg)` | algebroid; $\mu$; u, v, w | `ProofChain` |
| defect of $d_E^2\mu$ (antisymmetric bracket) | `df.prove_defect_d_squared_on_one_forms(As, muS, s1, s2, s3, registry=reg)` | algebroid (antisymmetric); $\mu$; u, v, w | `ProofChain` |
| defect of $d_E^2\mu$, general bracket | `df.prove_defect_d_squared_on_one_forms_general(A, muA, a1, a2, a3, registry=reg)` | algebroid; $\mu$; u, v, w | `ProofChain` |
| defect of $\mathcal L_ud_E-d_E\mathcal L_u$ on $\mu$ | `df.prove_defect_lie_d_on_one_forms(A, muA, a1, a2, a3, registry=reg)` | algebroid; $\mu$; u, v, w | `ProofChain` |
| defect of the second calculus condition | `df.prove_defect_calculus_condition_two(A, muA, a1, a2, a3, registry=reg)` | algebroid; $\eta$; u, v, w | `ProofChain` |
| defect of the third calculus condition | `df.prove_defect_calculus_condition_three(A, muA, a1, a2, a3, registry=reg)` | algebroid; $\omega$; u, v, w | `ProofChain` |

## Extending the engine: optional rules

Some definition rules are not switched on in the ready-made engines; the full list is on the
[Automatic rules](automatic-rules.md) page. Add them with `eng.register(Rule(...))`. For
example, $(\alpha\wedge\beta)(X,Y)$ and $\iota_{X\wedge Y}\omega$ do not expand in the
tangent engine unless these rules are added:

```python
from jacopy.central.calculus.indexed_rules import WedgeEvalDefinition
from jacopy.central.objects.multivector_interior import (MultivectorInterior,
    MultivectorInteriorDecomposableDefinition)
engW = tangent_engine(registry=reg)
engW.register(WedgeEvalDefinition(reg))
engW.register(MultivectorInteriorDecomposableDefinition())
print(len(jacopy.show_equal(jacopy.multi_eval(jacopy.wedge(alpha, beta), X, Y),
                            alpha(X)*beta(Y) - alpha(Y)*beta(X), registry=reg, engine=engW).steps))
print(len(jacopy.show_equal(MultivectorInterior(jacopy.wedge(X, Y))(omega), omega(X, Y),
                            registry=reg, engine=engW).steps))
```

```text
2
4
```

## Theorems, theorem books and `cite`

A {py:class}`jacopy.Theorem` is a proved identity stored with its chain and its assumptions.
A {py:class}`jacopy.TheoremBook` keeps theorems. {py:func}`jacopy.cite` adds a theorem to an
engine **as a rule**, so that it can be used as a single step in another proof; that step is
labelled `theorem`. A theorem can be cited only if its assumptions also hold in the citing
engine; `check_citation` checks this.

```python
book = jacopy.TheoremBook()
thm = jacopy.Theorem(
    name="lie_antisymmetry", statement="[X,Y](f) = -[Y,X](f)",
    lhs=jacopy.lie_bracket(X, Y)(f), rhs=-jacopy.lie_bracket(Y, X)(f),
    proof=tg.prove_antisymmetry(X, Y, f, registry=reg),
    generality="generic-function",
).with_structural_requires()
book.add(thm)
tg.register_cartan_theorems(book, alpha, X, Y, f, registry=reg)    # four ready-made theorems
tg.register_d_squared_zero(book, f, X, Y, registry=reg)
print(book.names())
print(check_citation(thm, eng, registry=reg).ok)
engC = jacopy.cite(jacopy.ExpansionEngine([]), book, "lie_antisymmetry")   # theorem -> rule
out, steps = engC.expand(jacopy.lie_bracket(X, Y)(f))
print(out, "|", steps[0].provenance_tag)
print(len(prove_bracket_jacobi(SN, f, X, Y, registry=reg, engine=eng).steps))   # graded Jacobi
```

```text
('lie_antisymmetry', 'cartan_magic_on_functions', 'cartan_magic_on_one_forms', 'L_iota_commutator', 'iota_anticommute', 'd_squared_zero_on_functions')
True
(-[Y,X]_VF(f)) | theorem
4
```

## Writing your own rule

Subclass {py:class}`jacopy.Definition` and implement `matches` and `rewrite`. Every rule that
comes from outside the library enters the proof record as an **assumption**. For a single
expression, the shorter route is `ExplicitAssumption(expression, target)` (shown above).

```python
class XXZero(jacopy.Definition):
    name = "example rule: [X, X] -> 0"
    def matches(self, expr):
        return expr == jacopy.lie_bracket(X, X)
    def rewrite(self, expr):
        return jacopy.Zero

engU = jacopy.ExpansionEngine([XXZero()])
out, steps = engU.expand(jacopy.lie_bracket(X, X) + Y)
print(out, "|", steps[0].role)
```

```text
(0 + Y) | assumption
```

`ExpansionEngine.expand` applies rules only; it does not simplify, so `0 + Y` is left as it
is. A larger example, with axioms owned by a structure of your own, is on the
[Your own structure](your-own-structure.md) page.
