# Metric-affine geometry

The package `jacopy.packages.metric_affine` covers metric-affine geometry on the tangent
bundle (connections, torsion $T$, curvature $R$, non-metricity $Q$, the Levi-Civita and
Koszul formulas, the Bianchi identities and frame components: Cartan structure equations,
Ricci, Einstein) and on algebroids ($E$-connections, the locality-corrected torsion
${}^{L}T$, the projected curvature ${}^{L}\hat R$, admissible connections, the derived
algebroid $E^\nabla$ and the $E$-Koszul, $E$-Bianchi and $E$-Cartan equations).

The package is imported as `MA`; on this page the name `g` is the **metric**, so the
functions are called `f` and `h`.

## Setup

```python
import jacopy
import jacopy.packages.metric_affine as MA
from jacopy.central.objects import Bundle
from jacopy.central.objects.frame import Frame
from jacopy.central.algebroid import algebroid, locality_projector

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, = jacopy.forms("alpha", degree=1)

# on TM
nabla = jacopy.connection()          # nabla (a second connection: jacopy.connection("D"))
D     = jacopy.connection("D")
g     = MA.metric("g")               # the package's metric context; g(X, Y) is a MetricValue
fr    = jacopy.frame("e")            # frame e_a = fr.field("a"), coframe e^a = fr.dual().field("a")
(W,)  = jacopy.vector_fields("W")

eng     = MA.metric_affine_engine(registry=reg)                    # definitional rules
eng_lc  = MA.metric_affine_engine(registry=reg,
                                  compatible=[(nabla, g)],         # declaration: nabla g = 0
                                  torsion_free=[nabla])            # declaration: T(nabla) = 0
eng_dec = MA.metric_affine_engine(registry=reg,
                                  decompositions=[(nabla, fr)])    # declaration: frame completeness

# on an algebroid E
E = algebroid("E", Bundle("E"), declare=("local", "regular"))
u, v, w = E.sections("u v w")
nE  = MA.e_connection(E)             # E-connection (for E = TM the ordinary connection)
frE = Frame("e", bundle=E.bundle)    # frame on E
P   = locality_projector(E)          # locality projector
engE = MA.e_connection_engine(E, registry=reg, projectors=(P,))
Dn = MA.derived_algebroid(E)                     # derived algebroid E^nabla
Dh = MA.derived_algebroid(E, projected=True)     # projected version
```

- `MA.metric("g")` and the top-level {py:func}`jacopy.metric` are different objects: the
  first is the package's metric context (symmetry, bilinearity and the $Q$ rules are
  attached to it), the second is the core metric symbol.
  `MA.as_metric_context(jacopy.metric("g"))` converts the second into the first.
- An engine expands an expression: `eng.expand(e)[0]` applies the definitions in one pass;
  `jacopy.normalize(eng, e, reg).expr` simplifies to normal form.
- Some $E$-theorems need further algebroid declarations:
  `declare=("local", "regular", "anchor-morphism")` (derived calculus, $\hat d^2$) or
  `declare=("local", "pre-leibniz", "regular")` (the last slot of the curvature).

### Declarations

No axiom is assumed silently. A declaration is made through an argument of the engine
builder or by registering the declaration object with the engine (`engine.register(...)`).

| Declaration | Axiom | How it is declared |
|---|---|---|
| metric compatibility (`MetricCompatibilityDefinition`) | $\nabla g=0$, i.e. $X\,g(Y,Z)=g(\nabla_XY,Z)+g(Y,\nabla_XZ)$ | `metric_affine_engine(compatible=[(nabla, g)])` |
| torsion-freeness (`TorsionFreeDefinition`) | $T(\nabla)=0$, i.e. $[X,Y]=\nabla_XY-\nabla_YX$ | `metric_affine_engine(torsion_free=[nabla])` |
| frame completeness | $\nabla_{e_b}e_c=\sum_s\Gamma^s_{bc}e_s$, $[e_a,e_b]=\sum_s\gamma^s_{ab}e_s$ | `metric_affine_engine(decompositions=[(nabla, fr)])` |
| `AdmissibilityDeclaration` | $[u,v]+[v,u]=\sum_sL(e^s,\nabla_{e_s}u,v)+\sum_sL(e^s,\nabla_{e_s}v,u)$ | `engE.register(MA.AdmissibilityDeclaration(E, nE, frE))` |
| `ModifiedTorsionFreeDeclaration` | ${}^{L}T(\nabla)=0$, solved for the bracket: $[u,v]_E=\nabla_uv-\nabla_vu+\sum_sL(e^s,\nabla_{e_s}u,v)$ | `engE.register(MA.ModifiedTorsionFreeDeclaration(E, nE, frE))` |
| `EKoszulDeclaration` | $\nabla$ is E-Koszul: every $g(\nabla_uv,w)$ wrapped in the metric is solved by the modified Koszul formula | `engE.register(MA.EKoszulDeclaration(E, nE, frE))` |

With `eng_lc` (torsion-free and metric-compatible declared) torsion and non-metricity
normalize to zero:

```python
print(jacopy.normalize(eng_lc, MA.torsion(nabla, X, Y), reg).expr)
print(jacopy.normalize(eng_lc, MA.nonmetricity(nabla, g, X, Y, Z), reg).expr)
```

```text
0
0
```

## Metric and connection

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $g(X,Y)$ | `g(X, Y)` | X, Y: vector field | `MetricValue` (scalar) $g(X, Y)$ | The engine puts it into symmetric order: `g(Y, X)` → $g(X, Y)$ (`MetricValueSymmetryDefinition`) |
| $g(fX,Y)=f\,g(X,Y)$ | `eng.expand(g(f*X, Y))[0]` | f: function | $f \, g(X, Y)$ | `MetricValueBilinearityDefinition` |
| $g^{ab}$ | `MA.inverse_metric_component(g, "b", "a")` | g: `Metric`; indices: str | `InverseMetricComponent` $g^{ab}$ | The index order is canonicalized (symmetry); by name: `MA.inverse_metric_component_named("g", "b", "a")` |
| converting to a metric context | `MA.as_metric_context(jacopy.metric("g"))` | the core $g$ atom | `Metric('g', bundle=TM)` | Bridge between the top-level `jacopy.metric` and the package `Metric` |
| $\nabla_XY$ | `nabla(X, Y)` or `jacopy.covariant_derivative(nabla, X, Y)` | nabla: connection; X, Y: vector field | $\nabla_{X}(Y)$ | Both notations give the same node |
| $\nabla_{fX+Y}Z=f\nabla_XZ+\nabla_YZ$ | `eng.expand(nabla(f*X + Y, Z))[0]` | | $f \, \nabla_{X}(Z) + \nabla_{Y}(Z)$ | `ConnectionDirectionLinearityDefinition` |
| $\nabla_X(fY)=X(f)Y+f\nabla_XY$ | `eng.expand(nabla(X, f*Y))[0]` | | $X(f) \, Y + f \, \nabla_{X}(Y)$ | `ConnectionArgumentLeibnizDefinition` |

## Torsion, curvature, non-metricity

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $T(X,Y)$ | `MA.torsion(nabla, X, Y)` | nabla: connection; X, Y: vector field | `Torsion` $T(X, Y)$ | Closed node; use the engine to expand it |
| $T(X,Y)=\nabla_XY-\nabla_YX-[X,Y]$ | `eng.expand(MA.torsion(nabla, X, Y))[0]` | | $\nabla_{X}(Y) - \nabla_{Y}(X) - [X, Y]$ | `TorsionExpansionDefinition` |
| $R(X,Y)Z$ | `MA.curvature(nabla, X, Y, Z)` | X, Y, Z: vector field | `Curvature` $R(X, Y)Z$ | |
| $R(X,Y)Z=\nabla_X\nabla_YZ-\nabla_Y\nabla_XZ-\nabla_{[X,Y]}Z$ | `eng.expand(MA.curvature(nabla, X, Y, Z))[0]` | | $\nabla_{X}(\nabla_{Y}(Z)) - \nabla_{Y}(\nabla_{X}(Z)) - \nabla_{[X, Y]}(Z)$ | `CurvatureExpansionDefinition` |
| $Q(X,Y,Z)$ | `MA.nonmetricity(nabla, g, X, Y, Z)` | g: `Metric` | `NonMetricity` $Q(X, Y, Z)$ | |
| $Q(X,Y,Z)=Xg(Y,Z)-g(\nabla_XY,Z)-g(Y,\nabla_XZ)$ | `eng.expand(MA.nonmetricity(nabla, g, X, Y, Z))[0]` | | $X(g(Y, Z)) - g(Z, \nabla_{X}(Y)) - g(Y, \nabla_{X}(Z))$ | `NonMetricityExpansionDefinition` |
| $(\nabla_XT)(Y,Z)$ | `MA.covariant_torsion_derivative(nabla, X, Y, Z)` | | $\nabla_{X}(T(Y, Z)) - T(\nabla_{X}(Y), Z) - T(Y, \nabla_{X}(Z))$ | Returns the explicit form |
| $(\nabla_XR)(Y,Z)W$ | `MA.covariant_curvature_derivative(nabla, X, Y, Z, W)` | W: vector field | $\nabla_{X}(R(Y, Z)W) - R(\nabla_{X}(Y), Z)W - \dots - R(Y, Z)\nabla_{X}(W)$ | |
| $\sum\pm\nabla_{[\cdot,[\cdot,\cdot]]}W=0$ (Jacobi in the direction slot) | `MA.covariant_jacobi_theorems(nabla, X, Y, Z, W, f, registry=reg)` | f: function | `(Theorem, Theorem)`; names `covariant_jacobi_∇_X_Y_Z_W`, `..._neg` | the instance theorems used by Bianchi II |

## Frame components: $\Gamma$, connection forms, Ricci, Einstein

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\Gamma^a_{bc}=\langle e^a,\nabla_{e_b}e_c\rangle$ | `MA.connection_coefficient(nabla, fr, "a", "b", "c")` | fr: frame; indices: str | `ConnectionCoefficient` $\Gamma^{a}_{bc}$ | No index symmetry |
| $\langle e^a,\nabla_{e_b}e_c\rangle\to\Gamma^a_{bc}$ | `eng.expand(jacopy.pairing(fr.dual().field("a"), nabla(fr.field("b"), fr.field("c"))))[0]` | | $\Gamma^{a}_{bc}$ | `FrameConnectionCoefficientDefinition` |
| $\nabla_{e_b}e_c=\sum_s\Gamma^s_{bc}e_s$ | `eng_dec.expand(nabla(fr.field("b"), fr.field("c")))[0]` | | $\sum_{s \in e} \Gamma^{s}_{bc} \, e_{s}$ | Only with the `decompositions` declaration |
| $\omega^a{}_b$ | `MA.connection_form(nabla, fr, "a", "b")` | | `ConnectionForm` $\omega^{a}_{b}$ (1-form) | $\langle\omega^a{}_b,X\rangle\to\langle e^a,\nabla_Xe_b\rangle$: once `MA.ConnectionFormEvaluationDefinition(nabla, fr)` is added to the engine |
| component formula for $R^a{}_{bcd}$ | `MA.curvature_component_formula(nabla, fr, "a", "b", "c", "d")` | `bound="s"` (kw): summation index | $e_{c}(\Gamma^{a}_{db}) - e_{d}(\Gamma^{a}_{cb}) + \sum_s \Gamma^{a}_{cs}\Gamma^{s}_{db} - \sum_s \Gamma^{a}_{ds}\Gamma^{s}_{cb} - \sum_s \Gamma^{a}_{sb}\gamma^{s}_{cd}$ | Returns the expression directly |
| $Ric_{bd}=\sum_s\langle e^s,R(e_s,e_b)e_d\rangle$ | `MA.ricci_component(nabla, fr, "b", "d")` | | $\sum_{s \in e} \langle e^{s}, R(e_{s}, e_{b})e_{d} \rangle$ | |
| $R=\sum_{s,t}g^{st}Ric_{st}$ | `MA.ricci_scalar(nabla, fr, g)` | `bounds=("s","t","u")` (kw) | $\sum_s\sum_t g^{st}\,(\sum_u \langle e^{u}, R(e_{u}, e_{s})e_{t} \rangle)$ | |
| $G_{bd}=Ric_{bd}-\tfrac12R\,g_{bd}$ | `MA.einstein_component(nabla, fr, g, "b", "d")` | | $(\sum_s\langle e^{s}, R(e_{s}, e_{b})e_{d}\rangle) - \frac{1}{2}(\dots)\,g(e_{b}, e_{d})$ | Trace identities (dimension $n$) are out of scope |
| $Q_{ab}$, $Q_{ab}(v)=Q(v,e_a,e_b)$ | `MA.nonmetricity_form(nabla, g, fr, "a", "b")` | | `NonMetricityForm` $Q_{ab}$ | Evaluation: once `MA.NonMetricityFormEvaluationDefinition(nabla, g, fr)` is added to the engine, $\langle Q_{ab},X\rangle\to X(g(e_a,e_b))-g(e_b,\nabla_X e_a)-g(e_a,\nabla_X e_b)$ |
| component formula for $Q_{ab}(e_c)$ | `MA.nonmetricity_form_component_formula(nabla, g, fr, "a", "b", "c")` | | $e_{c}(g(e_{a}, e_{b})) - \sum_s \Gamma^{s}_{ca}\, g(e_{s}, e_{b}) - \sum_s \Gamma^{s}_{cb}\, g(e_{a}, e_{s})$ | |

## Computing with concrete components

You can supply concrete components ($\Gamma^a_{bc}$, $g_{ab}$, $\gamma^c_{ab}$,
$\theta^{ab}$) in a finite-dimensional frame and evaluate the package's symbolic component
expressions on them.

```python
data = MA.ComponentInput(fr, dim=2, connection=nabla, total=True, holonomic=True)
data.set_gamma("0", "0", "1", f)          # Gamma^0_01 = f; total=True: every other component is 0
data2 = MA.ComponentInput(fr, dim=2, connection=nabla, metric=g, total=True, holonomic=True)
data2.set_metric("0", "0", 1); data2.set_metric("1", "1", h)     # g_00 = 1, g_11 = h
print(jacopy.to_latex(data.evaluate(MA.curvature_component_formula(nabla, fr, "0", "1", "0", "1"), registry=reg)))
```

```text
-e_{1}\!\left(f\right)
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $R^0{}_{101}$ when $\Gamma^0_{01}=f$ | `data.evaluate(MA.curvature_component_formula(nabla, fr, "0", "1", "0", "1"), registry=reg)` | expression, registry | $-e_{1}(f)$ | |
| $Ric_{11}$ with the same data | `data.evaluate(MA.ricci_component(nabla, fr, "1", "1"), registry=reg, engine=eng_dec)` | `engine`: engine with frame completeness declared | $-e_{1}(f)$ | With the default engine the $R$ node stays unexpanded; the `decompositions` declaration is needed |
| $g_{11}$ | `data2.metric_component(("1", "1"))` | key: index pair | $h$ | |
| $g(e_1,e_1)$ | `data2.evaluate(g(fr.field("1"), fr.field("1")), registry=reg)` | | $h$ | |

Other inputs: `set_anholonomy(c, a, b, value)` ($\gamma^c_{ab}$; antisymmetry is
automatic) and `set_pi(a, b, value)` ($\theta^{ab}$). With `total=False` (the default),
components that are not given stay symbolic.

## $E$-connections, modified torsion and projected curvature

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $\nabla_uv$ | `nE(u, v)` | u, v: E-section | $\nabla_{u}(v)$ | |
| $\nabla_uf=\rho(u)(f)$ | `engE.expand(nE(u, f))[0]` | f: function | $\rho(u)(f)$ | `EConnectionScalarActionDefinition` |
| $T^{(0)}(u,v)=\nabla_uv-\nabla_vu-[u,v]_E$ | `engE.expand(MA.torsion(nE, u, v))[0]` | | $\nabla_{u}(v) - \nabla_{v}(u) - [u, v]_{E}$ | `torsion` is the same function; for an E-connection `ETorsionExpansionDefinition` expands it |
| $R^{(0)}(u,v)w$ | `engE.expand(MA.curvature(nE, u, v, w))[0]` | | $\nabla_{u}(\nabla_{v}(w)) - \nabla_{v}(\nabla_{u}(w)) - \nabla_{[u, v]_{E}}(w)$ | `ECurvatureExpansionDefinition` |
| $Q(u,v,w)$ (E) | `MA.e_nonmetricity(E, nE, u, v, w)` | E: algebroid | $\rho(u)(g_{E}(v, w)) - g_{E}(\nabla_{u}(v), w) - g_{E}(v, \nabla_{u}(w))$ | Returns the explicit expression |
| ${}^{L}T(u,v)$ | `MA.modified_torsion(E, nE, frE, u, v)` | frE: E-frame; `bound` (kw) | $T(u, v) + \sum_{s \in e} L(e^{s}, \nabla_{e_{s}}(u), v)$ | |
| ${}^{L}\hat R(u,v)w$ | `MA.projected_curvature(E, nE, frE, P, u, v, w)` | P: locality projector | $R(u, v)w + \sum_{s} \nabla_{P(L(e^{s}, \nabla_{e_{s}}(u), v))}(w)$ | |
| $[u,v]^\nabla$ | `MA.modified_bracket(E, nE, frE, u, v)` | | $[u, v]_{E} - \sum_{s} L(e^{s}, \nabla_{e_{s}}(u), v)$ | |
| $\hat b(u,v)$ | `MA.projected_modified_bracket(E, nE, frE, P, u, v)` | | $[u, v]_{E} - \sum_{s} P(L(e^{s}, \nabla_{e_{s}}(u), v))$ | |
| $(1-\mathcal P)\Lambda(u,v)$ | `MA.anomaly_direction(E, nE, frE, P, u, v)` | | $\sum_s L(\dots) - \sum_s P(L(\dots))$ | |
| $(\nabla_u{}^{L}T)(v,w)$ | `MA.covariant_modified_torsion_derivative(E, nE, frE, u, v, w)` | | $\nabla_{u}({}^{L}T(v,w)) - {}^{L}T(\nabla_{u}v, w) - {}^{L}T(v, \nabla_{u}w)$ (explicit) | |
| generalized Ricci anomaly | `MA.generalized_ricci_anomaly(E, nE, frE, P, u, v, w)` | | $\sum_{s} (\nabla_{L(\dots)}(w) - \nabla_{P(L(\dots))}(w))$ | |
| $K(\nabla,g,L)(u,v,w)$ | `MA.koszul_correction(E, nE, frE, u, v, w)` | | $-g_{E}(\sum_s L(e^{s}, \nabla_{e_{s}}(v), w), u) - g_{E}(\sum_s L(\dots u, w), v) + g_{E}(\sum_s L(\dots u, v), w)$ | |
| the two sides of (3.44) | `MA.fundamental_theorem_components(E, nE, MA.e_connection(E, "K∇"), frE, "b", "c", "d")` | kconn: E-Koszul reference connection | `(lhs, rhs)`: $g_{E}(\nabla_{e_{b}}(e_{c}), e_{d})$, $g_{E}(K\nabla_{e_{b}}(e_{c}), e_{d}) + \frac{1}{2}(\dots)$ | |

## The derived algebroid $E^\nabla$ and the $E$-Cartan equations

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $E^\nabla$ / $E^{\hat\nabla}$ | `Dn = MA.derived_algebroid(E)` / `Dh = MA.derived_algebroid(E, projected=True)` | base: algebroid | `Algebroid('E^∇', bundle=Bundle('E'))` | Has no declarations of its own |
| is it projected? | `MA.derived_is_projected(E, Dh)` | | `True` | |
| $d(\nabla)f$ | `MA.d_derived(Dn, f)` | Dn: derived algebroid | $d_E^{\nabla}(f)$ | Closed node; `derived_engine` expands it |
| $\mathcal L^\nabla_uf$ | `MA.lie_derived(Dn, u)(f)` | | $L^E{}^{\nabla}_{u}(f)$ | Returns an operator, which is then applied |
| derived engine | `MA.derived_engine(E, Dn, nE, frE, registry=reg)` | `projector` (kw) | `ExpansionEngine` | |
| E-Cartan engine | `MA.e_cartan_engine(E, Dn, nE, frE, registry=reg)` | `projector`, `decomposed` (kw) | `ExpansionEngine` | |
| E-Cartan I sides | `MA.e_cartan_first_sides(E, nE, frE, "a", "b", "c")` | | `(lhs, rhs, derived)`: $\langle e^{a}, T(e_{b}, e_{c}) + \sum_{s} L(e^{s}, \nabla_{e_{s}}(e_{b}), e_{c}) \rangle$, $(d_E^{\nabla}(e^{a}))(e_{b}, e_{c}) + (\sum_{s} \omega^{a}_{s} \wedge e^{s})(e_{b}, e_{c})$ | |
| E-Cartan II sides | `MA.e_cartan_second_sides(E, nE, frE, P, "a", "b", "c", "d")` | | `(lhs, rhs, derived)`: $\langle e^{a}, R(e_{c}, e_{d})e_{b} + \sum_{s} \nabla_{P(L(e^{s}, \nabla_{e_{s}}(e_{c}), e_{d}))}(e_{b}) \rangle$, $(d_E^{\hat{\nabla}}(\omega^{a}_{b}))(e_{c}, e_{d}) + (\sum_{s} \omega^{a}_{s} \wedge \omega^{s}_{b})(e_{c}, e_{d})$ | |

## Theorem builders

Every builder takes the keyword argument `registry=reg` (not shown in the table). All
builders except `prove_levi_civita_unique` return only proof chains. Call examples:

```python
chain = MA.prove_koszul_formula(nabla, g, X, Y, Z, registry=reg)              # ProofChain
first, second = MA.prove_torsion_tensorial(nabla, X, Y, f, registry=reg)     # two ProofChains
chain, used = MA.prove_bianchi_first(nabla, X, Y, Z, f, registry=reg)        # (ProofChain, [Theorem])
chain, thm = MA.prove_levi_civita_unique(nabla, D, g, X, Y, Z, registry=reg)  # (ProofChain, Theorem)
print(jacopy.to_ascii(thm.lhs), "=", jacopy.to_ascii(thm.rhs))
```

```text
∇_X(Y) = D_X(Y)
```

The builders on an algebroid use $E$ declared `("local", "regular")`, except
`prove_e_curvature_last_slot_conditional` and `prove_projected_curvature_last_slot`
(`("local", "pre-leibniz", "regular")`) and `prove_derived_magic_*`,
`prove_projected_d_squared_*`, `prove_e_koszul_unique_under_null_locality` and
`prove_projectors_agree_on_coboundary_values` (`("local", "regular", "anchor-morphism")`).
`prove_e_bianchi_first_identity(..., admissible=True)` registers the admissibility
declaration itself. The last column notes builders that rely on a declared axiom or cite a
proved theorem.

| Builder | Identity it proves | Arguments | Returns | Note |
|---|---|---|---|---|
| `MA.prove_nonmetricity_form_cartan` | $Q_{ab}=dg_{ab}-\omega_{ba}-\omega_{ab}\text{ (in a frame)}$ | `conn`: Connection, `g`: Metric, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` | a declared axiom |
| `MA.prove_nonmetricity_form_components` | $Q_{ab}(e_c)=e_c(g_{ab})-\textstyle\sum_s\Gamma^s_{ca}g_{sb}-\sum_s\Gamma^s_{cb}g_{as}$ | `conn`: Connection, `g`: Metric, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` | a declared axiom |
| `MA.prove_nonmetricity_form_symmetric` | $Q_{ab}(X)=Q_{ba}(X)$ | `conn`: Connection, `g`: Metric, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `X`: Expr | `ProofChain` |  |
| `MA.prove_nonmetricity_form_tensorial` | $Q_{ab}(fX)=f\,Q_{ab}(X)$ | `conn`: Connection, `g`: Metric, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `X`: Expr, `f`: Expr | `ProofChain` |  |
| `MA.prove_e_cartan_first` | $T^a(\nabla)=d(\nabla)e^a+\omega^a{}_b\wedge e^b$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` |  |
| `MA.prove_e_cartan_second` | $R^a{}_b(\nabla)=\hat d(\nabla)\omega^a{}_b+\omega^a{}_c\wedge\omega^c{}_b$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `d`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` | a declared axiom |
| `MA.prove_connection_difference_tensorial` | $\nabla-\nabla' \text{ is } C^\infty\text{-linear in both slots}$ | `conn1`: Connection, `conn2`: Connection, `X`: Expr, `Y`: Expr, `f`: Expr | `Tuple[ProofChain, ProofChain]` |  |
| `MA.prove_curvature_antisymmetry` | $R(X,Y)Z=-R(Y,X)Z$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `Z`: Expr | `ProofChain` | cites a theorem |
| `MA.prove_curvature_tensorial` | $R(fX,Y)Z=R(X,fY)Z=R(X,Y)(fZ)=f\,R(X,Y)Z$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `Z`: Expr, `f`: Expr | `Tuple[ProofChain, ProofChain, ProofChain]` | cites a theorem |
| `MA.prove_torsion_antisymmetry` | $T(X,Y)=-T(Y,X)$ | `conn`: Connection, `X`: Expr, `Y`: Expr | `ProofChain` | cites a theorem |
| `MA.prove_torsion_tensorial` | $T(fX,Y)=T(X,fY)=f\,T(X,Y)$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `f`: Expr | `Tuple[ProofChain, ProofChain]` | cites a theorem |
| `MA.prove_generalized_koszul` | $2g(\nabla_XY,Z)=\text{Koszul}+Q\text{-block}+T\text{-block}$ | `conn`: Connection, `g`: Metric, `X`: Expr, `Y`: Expr, `Z`: Expr | `ProofChain` |  |
| `MA.prove_koszul_formula` | $2g(\nabla_XY,Z)=Xg(Y,Z)+Yg(X,Z)-Zg(X,Y)+g([X,Y],Z)-g([X,Z],Y)-g([Y,Z],X)$ | `conn`: Connection, `g`: Metric, `X`: Expr, `Y`: Expr, `Z`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_levi_civita_unique` | $\nabla_XY=D_XY \;(\text{both with } Q=0,\,T=0)$ | `conn1`: Connection, `conn2`: Connection, `g`: Metric, `X`: Expr, `Y`: Expr, `Z`: Expr | `Tuple[ProofChain, Theorem]` | a declared axiom; returns a `Theorem` record |
| `MA.prove_bianchi_first` | $\mathfrak S\,R(X,Y)Z=\mathfrak S\,[T(T(X,Y),Z)+(\nabla_XT)(Y,Z)]$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `Z`: Expr, `f`: Expr | `Tuple[ProofChain, List[Theorem]]` | cites a theorem |
| `MA.prove_bianchi_second` | $\mathfrak S\,[(\nabla_XR)(Y,Z)W+R(T(X,Y),Z)W]=0$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `Z`: Expr, `W`: Expr, `f`: Expr | `Tuple[ProofChain, List[Theorem]]` | cites a theorem |
| `MA.prove_ricci_identity_on_functions` | $\nabla_X\nabla_Yf-\nabla_Y\nabla_Xf-\nabla_{[X,Y]}f=0$ | `conn`: Connection, `X`: Expr, `Y`: Expr, `f`: Expr | `ProofChain` |  |
| `MA.prove_cartan_first_evaluated` | $T^a(e_b,e_c)=de^a(e_b,e_c)+(\omega^a{}_s\wedge e^s)(e_b,e_c)$ | `conn`: Connection, `fr`: Frame, `upper`: IndexLike, `b`: IndexLike, `c`: IndexLike | `ProofChain` |  |
| `MA.prove_cartan_first_structure` | $T^a=de^a+\textstyle\sum_s\omega^a{}_s\wedge e^s \text{ (in a frame, indexed sum)}$ | `conn`: Connection, `fr`: Frame, `upper`: IndexLike, `b`: IndexLike, `c`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` |  |
| `MA.prove_cartan_second_structure` | $R^a{}_b=d\omega^a{}_b+\textstyle\sum_s\omega^a{}_s\wedge\omega^s{}_b \text{ (in a frame)}$ | `conn`: Connection, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `d`: IndexLike, `bound`: str (kw, ='s') | `ProofChain` | a declared axiom |
| `MA.prove_curvature_components` | $R^a{}_{bcd}=e_c(\Gamma^a_{db})-e_d(\Gamma^a_{cb})+\Sigma\Gamma\Gamma-\Sigma\Gamma\Gamma-\Sigma\Gamma\gamma$ | `conn`: Connection, `fr`: Frame, `a`: IndexLike, `b`: IndexLike, `c`: IndexLike, `d`: IndexLike | `ProofChain` | a declared axiom |
| `MA.prove_ricci_components` | $Ric_{bd}=\textstyle\sum_s R^s{}_{dsb}\text{ expanded in }\Gamma,\gamma$ | `conn`: Connection, `fr`: Frame, `b`: IndexLike, `d`: IndexLike | `ProofChain` | a declared axiom; cites a theorem |
| `MA.prove_ricci_scalar_components` | $R=\textstyle\sum_{s,t}g^{st}Ric_{st}\text{ expanded in }\Gamma$ | `conn`: Connection, `fr`: Frame, `g`: Metric | `ProofChain` | a declared axiom; cites a theorem |
| `MA.prove_e_connection_anchored_leibniz` | $\nabla_u(fv)=\rho(u)(f)\,v+f\nabla_uv$ | `alg`: Algebroid, `conn`: Connection, `u`: Expr, `v`: Expr, `f`: Expr | `ProofChain` |  |
| `MA.prove_e_curvature_last_slot_conditional` | $R^{(0)}(u,v)(fw)=f\,R^{(0)}(u,v)w$ | `alg`: Algebroid, `conn`: Connection, `u`: Expr, `v`: Expr, `w`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_e_torsion_second_slot_tensorial` | $T^{(0)}(u,fv)=f\,T^{(0)}(u,v)$ | `alg`: Algebroid, `conn`: Connection, `u`: Expr, `v`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_pseudo_torsion_first_slot_defect` | $T^{(0)}(fu,v)=f\,T^{(0)}(u,v)-L(Df,u,v)$ | `alg`: Algebroid, `conn`: Connection, `u`: Expr, `v`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_modified_torsion_tensorial` | ${}^{L}T(fu,v)={}^{L}T(u,fv)=f\,{}^{L}T(u,v)$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `f`: Expr | `Tuple[ProofChain, ProofChain]` | a declared axiom |
| `MA.prove_projected_curvature_first_slot` | ${}^{L}\hat R(fu,v)w=f\,{}^{L}\hat R(u,v)w$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `u`: Expr, `v`: Expr, `w`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_projected_curvature_last_slot` | ${}^{L}\hat R(u,v)(fw)=f\,{}^{L}\hat R(u,v)w$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `u`: Expr, `v`: Expr, `w`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_connection_form_on_frame` | $\omega^a{}_b(e_c)=\Gamma^a_{cb}$ | `conn`: Connection, `fr`: Frame, `upper`: IndexLike, `lower`: IndexLike, `at`: IndexLike | `ProofChain` |  |
| `MA.prove_torsion_components` | $\langle e^a,T(e_b,e_c)\rangle=\Gamma^a_{bc}-\Gamma^a_{cb}-\gamma^a_{bc}$ | `conn`: Connection, `fr`: Frame, `upper`: IndexLike, `b`: IndexLike, `c`: IndexLike | `ProofChain` |  |
| `MA.prove_admissible_implies_metric_compatible` | $\text{admissible}\Rightarrow Q=0\text{ (in frame directions)}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `direction`: str (kw, ='a') | `ProofChain` | a declared axiom |
| `MA.prove_courant_locality_generator` | $S(fu,v)=f\,S(u,v)+{}^{g}L(Df,u,v)$ | `alg`: Algebroid, `fr`: Frame, `u`: Expr, `v`: Expr, `f`: Expr | `ProofChain` | a declared axiom; cites a theorem |
| `MA.prove_metric_compatible_implies_admissible` | $Q=0\Rightarrow\text{admissible (almost-Courant)}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_modified_bracket_left_leibniz` | $[fu,v]^\nabla=f[u,v]^\nabla-\rho(v)(f)\,u$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `f`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_modified_torsion_symmetric_part_vanishes` | ${}^{L}T(u,v)+{}^{L}T(v,u)=0$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_torsion_free_implies_admissible` | ${}^{L}T=0\Rightarrow [u,v]+[v,u]=\textstyle\sum_sL(e^s,\nabla_{e_s}u,v)+\sum_sL(e^s,\nabla_{e_s}v,u)$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_derived_magic_on_forms` | $\mathcal L^\nabla_u\omega=(d(\nabla)\iota_u+\iota_ud(\nabla))\omega\text{ (on slots)}$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `omega`: Expr, `slots`: tuple[Expr], `projector`: LocalityProjector (kw, =None) | `ProofChain` |  |
| `MA.prove_derived_magic_on_functions` | $\mathcal L^\nabla_uf=(d(\nabla)\iota_u+\iota_ud(\nabla))f$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `f`: Expr, `projector`: LocalityProjector (kw, =None) | `ProofChain` |  |
| `MA.prove_projected_d_squared_associator` | $(\hat d^2\alpha)(u,v,w)=\langle\alpha,\hat b(\hat b(u,v),w)-\hat b(\hat b(u,w),v)+\hat b(\hat b(v,w),u)\rangle$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `alpha`: Expr, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_projected_d_squared_on_functions` | $(\hat d(\nabla)^2f)(u,v)=0$ | `base`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `f`: Expr, `u`: Expr, `v`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_e_bianchi_first_identity` | $\mathfrak S\,{}^{L}\hat R(u,v)w=\mathfrak S[(\nabla_u{}^{L}T)(v,w)+{}^{L}T({}^{L}T(u,v),w)]+\text{correction blocks}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `u`: Expr, `v`: Expr, `w`: Expr, `admissible`: bool (kw, =False) | `ProofChain` |  |
| `MA.prove_e_bianchi_second_identity` | $\mathfrak S[(\nabla_u{}^{L}\hat R)(v,w)x+{}^{L}\hat R({}^{L}T(u,v),w)x]=\text{correction blocks}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `u`: Expr, `v`: Expr, `w`: Expr, `x`: Expr | `ProofChain` |  |
| `MA.prove_e_generalized_koszul` | $2g(\nabla_uv,w)+K=\text{Koszul}+Q\text{-block}+{}^{L}T\text{-block}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` |  |
| `MA.prove_e_koszul_admissible_implies_compatible` | $\text{E-Koszul}+\text{admissible}\Rightarrow Q(u,v,w)=0$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_e_koszul_admissible_implies_torsion_free` | $\text{E-Koszul}+\text{admissible}\Rightarrow g({}^{L}T(u,v),w)=0$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_e_koszul_formula` | ${}^{L}T=0,\,Q=0\Rightarrow 2g(\nabla_uv,w)+K=\text{Koszul right-hand side}$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_e_koszul_unique_under_null_locality` | $L=0\Rightarrow g(\nabla^1_uv-\nabla^2_uv,w)=0$ | `alg`: Algebroid, `conn1`: Connection, `conn2`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_fundamental_theorem_components` | $\Gamma_{dbc}=\Gamma(K\nabla)_{dbc}+\tfrac12[-Q_{bcd}-Q_{cbd}+Q_{dbc}+{}^0T_{dbc}-{}^0T_{cbd}-{}^0T_{bcd}]$ | `alg`: Algebroid, `conn`: Connection, `kconn`: Connection, `fr`: Frame, `b`: IndexLike (='b'), `c`: IndexLike (='c'), `d`: IndexLike (='d') | `ProofChain` | a declared axiom |
| `MA.prove_koszul_reference_decomposition` | $g(\nabla_uv-\bar\nabla_uv,w)=Q\text{- and }{}^{L}T\text{-blocks}$ | `alg`: Algebroid, `conn`: Connection, `ref`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_metric_lie_derivative_identity` | $(\mathcal L^\nabla_vg)(u,w)=g(\nabla_uv,w)+g(u,\nabla_wv)$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` | a declared axiom |
| `MA.prove_projectors_agree_on_coboundary_values` | $\mathcal P_1(L(Df,u,v))-\mathcal P_2(L(Df,u,v))=0$ | `alg`: Algebroid, `fr`: Frame, `f`: Expr, `u`: Expr, `v`: Expr | `ProofChain` |  |
| `MA.prove_generalized_ricci_identity` | $\nabla^2_{u,v}w-\nabla^2_{v,u}w={}^{L}\hat R(u,v)w-\nabla_{{}^{L}T(u,v)}w+\textstyle\sum_s\nabla_{(1-\mathcal P)L(\dots)}w$ | `alg`: Algebroid, `conn`: Connection, `fr`: Frame, `projector`: LocalityProjector, `u`: Expr, `v`: Expr, `w`: Expr | `ProofChain` |  |

## Rules the engine applies automatically

These rules are applied by `metric_affine_engine`, `e_connection_engine` or the engine of
the corresponding builder. Those that depend on a declaration (metric compatibility,
torsion-freeness, frame completeness) are active only when the corresponding argument is
given. For rules defined outside the facade, the module is given in parentheses.

| Rule | Mathematical counterpart |
|---|---|
| `ConnectionDirectionLinearityDefinition` | $\nabla_{fX+Y}T=f\nabla_XT+\nabla_YT$ |
| `ConnectionArgumentLeibnizDefinition` (`rules.py`) | $\nabla_X(fT)=X(f)\,T+f\,\nabla_XT$ |
| `TorsionExpansionDefinition` | $T(X,Y)\to\nabla_XY-\nabla_YX-[X,Y]$ ($TM$) |
| `CurvatureExpansionDefinition` | $R(X,Y)Z\to\nabla_X\nabla_YZ-\nabla_Y\nabla_XZ-\nabla_{[X,Y]}Z$ |
| `MetricValueSymmetryDefinition` | $g(Y,X)\to g(X,Y)$ (canonical order) |
| `MetricValueBilinearityDefinition` | $C^\infty$-bilinearity of $g$ |
| `NonMetricityExpansionDefinition` | $Q(X,Y,Z)\to Xg(Y,Z)-g(\nabla_XY,Z)-g(Y,\nabla_XZ)$ |
| `MetricCompatibilityDefinition` | declaration $\nabla g=0$: $Xg(Y,Z)\to g(\nabla_XY,Z)+g(Y,\nabla_XZ)$ |
| `TorsionFreeDefinition` | declaration $T=0$: $[X,Y]\to\nabla_XY-\nabla_YX$ |
| `MetricInverseContractionDefinition` | $\sum_sg^{as}g(e_s,e_c)\to\delta^a_c$ |
| `FrameConnectionCoefficientDefinition` | $\langle e^a,\nabla_{e_b}e_c\rangle\to\Gamma^a_{bc}$ |
| `FramePairingSplitDefinition` | $\langle e^a,\sum_it_i\rangle\to\sum_i\langle e^a,t_i\rangle$ (guarded) |
| `ConnectionFormEvaluationDefinition` | $\langle\omega^a{}_b,X\rangle\to\langle e^a,\nabla_Xe_b\rangle$ |
| `NonMetricityFormEvaluationDefinition` | $\langle Q_{ab},v\rangle\to Q(v,e_a,e_b)$ |
| `ConnectionFrameDecompositionDefinition` (`decomposition.py`) | declaration: $\nabla_{e_b}e_c\to\sum_s\Gamma^s_{bc}e_s$ |
| `BracketFrameDecompositionDefinition` (`decomposition.py`) | declaration: $[e_a,e_b]\to\sum_s\gamma^s_{ab}e_s$ |
| `IndexedSumOperatorPushDefinition` (`decomposition.py`) | $D(\sum_st_s)\to\sum_sD(t_s)$ |
| `MetricIndexedSumPushDefinition` (`decomposition.py`) | $g(\sum_sV_s,W)\to\sum_sg(V_s,W)$ |
| `EConnectionScalarActionDefinition` | $\nabla_uf\to\rho(u)(f)$ |
| `ETorsionExpansionDefinition` | $T^{(0)}(u,v)\to\nabla_uv-\nabla_vu-[u,v]_E$ |
| `ECurvatureExpansionDefinition` | $R^{(0)}(u,v)w\to\nabla_u\nabla_vw-\nabla_v\nabla_uw-\nabla_{[u,v]_E}w$ |
| `CoframeRecombinationDefinition` | $\sum_s\rho(e_s)(f)\,E(e^s)\to E(Df)$ |
| `SubstituteComponentsDefinition` (`component_workflow.py`) | replaces the symbolic components $\Gamma,g,\gamma,\theta$ with the `ComponentInput` data |
| `ConcreteDeltaDefinition` (`component_workflow.py`) | $\delta^a_b=0$ for distinct concrete indices, $1$ for equal ones |
| `IndexedSumUnrollDefinition` (`component_workflow.py`) | unrolls $\sum_s$ over a finite frame ($s=0,\dots,\dim-1$) |
