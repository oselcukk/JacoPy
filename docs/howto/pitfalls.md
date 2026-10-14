# Pitfalls and API quirks

This page collects behaviors that commonly surprise new users. Each item describes the
current behavior of the library and how to work with it.

## Two functions called `prove`

{py:func}`jacopy.prove` takes `(lhs, rhs, ...)` and returns a `ProofChain`.
`jacopy.proof.result.prove` takes `(engine, lhs, rhs, ...)` and returns a `ProofResult`; it
does not run the product-rule pass. As a consequence, identities such as
$d(fh)=f\,dh+h\,df$, $\mathcal L_X(fh)=X(f)h+fX(h)$, $[X,fY]=X(f)Y+f[X,Y]$ and
$\nabla_X(fY)=X(f)Y+f\nabla_XY$ close with {py:func}`jacopy.show_equal` but are left
`RESIDUAL` by `jacopy.proof.result.prove`. See [Running proofs](running-proofs.md).

## The right-hand side zero must be an expression

`jacopy.proof.result.prove(eng, lhs, 0)` raises `TypeError` ("Goal sides must be Exprs").
Write `jacopy.Zero`, or omit the right-hand side, which defaults to zero.

## Some heads are not callable

`omega(X, Y)`, `alpha(X)` and `g(X, Y)` can be called directly, but `d(alpha)(X, Y)` and
`jacopy.wedge(alpha, beta)(X, Y)` raise `TypeError`. Evaluate such heads with
{py:func}`jacopy.multi_eval`: `jacopy.multi_eval(d(alpha), X, Y)`.

## What the tangent engine does not expand by default

- $(\alpha\wedge\beta)(X,Y)$ and $\iota_{X\wedge Y}\omega$ need optional rules
  (`WedgeEvalDefinition`, `MultivectorInteriorDecomposableDefinition`); see
  [Running proofs](running-proofs.md).
- A commutator node applied to a function, `jacopy.Act(commutator(L_X, L_Y), f)`, is left
  as it is. Write $\mathcal L_X\mathcal L_Yf-\mathcal L_Y\mathcal L_Xf$ explicitly (this is
  what `tg.prove_L_L_commutator_on_functions` does).
- Registry declarations other than `Scalar`, `Graded`, `AntiCommuting` and
  `GradedCommutative` are recorded but not used by the engines. Declaring `Closed` on
  $\omega$ does not reduce $d\omega$ to zero; to use such a fact in a proof, add it as an
  `ExplicitAssumption` or use the package structure that declares it (for example
  `symplectic_engine(..., declare_closed=True)` on the [Poisson](poisson.md) page).

## The general bracket Jacobi verifier

`jacopy.proof.verifier.prove_jacobi(SN, X, Y, Z, ...)` does not close the section-level
Schouten–Nijenhuis Jacobi identity for three vector fields: a residual of the form
`[(-[X,Z]),Y]` remains, because the sign inside the outer bracket is not pulled out. The
same call with a function in the first slot, `prove_jacobi(SN, f, X, Y, ...)`, closes. For
vector fields, use `tg.prove_lie_jacobi`.

## Sections are not checked against their algebroid

A theorem builder does not check that the sections it receives belong to the algebroid it
is given; sections of another algebroid are accepted. Always pass sections created with
`E.sections(...)` of the same `E`.

## Auxiliary function names inside builders

`ag.prove_locality_anchor_annihilation` declares an auxiliary function named `h`. If your
registry already contains a function `h`, the call raises "Graded already declared on h".
Pass your function explicitly: `ag.prove_locality_anchor_annihilation(Lp, l1, l2, f, h=h, registry=reg)`.

## Argument orders and return types vary

- `tg.prove_leibniz_second_slot(X, f, Y, h)` but `tg.prove_first_slot_function_linearity(f, X, Y, h)`.
- On $TM$, `tg.prove_cartan_magic_on_one_forms(alpha, X, Y)`; on an algebroid,
  `ag.prove_algebroid_cartan_magic_on_one_forms(A, u, mu, v)`.
- Builders return a `ProofChain`, `(ProofChain, [Theorem])`, `(ProofChain, Theorem)`,
  `(ProofChain, ProofChain)`, a `Theorem` or `(Theorem, Theorem)`; the tables in this guide
  state the return type of every builder.

## Constructors with several arguments

`derivator(alg, Phi, u, v)` and `predator(alg, psi, u, v)` need a
`section_map("Phi", source_bundle, target_bundle)` first; source and target are **bundles**
(`A.bundle`), not algebroids. `LocalityOperator("R", mu, u, v)` takes the algebroid's
**name** as a string. See [Algebroids](algebroids.md).

## Names

- `jacobi_combination_theorems` is imported from `jacopy.central.tangent.lie_bracket`; it is
  not exported by `jacopy.central.tangent`.
- `jacopy.central.tangent.prove_jacobi` (Lie bracket) and
  `jacopy.proof.verifier.prove_jacobi` (general bracket) are different functions.
- `d` from `jacopy.central.tangent` is a shortcut that builds $d\omega$; the operator is
  {py:func}`jacopy.exterior_d`.
- {py:func}`jacopy.cite` (theorem as an engine rule) and `jacopy.bibliography.cite`
  (literature citation) are different functions.

## LaTeX output

- `ginv.sharp()(alpha)` renders as `g^{-1}^{\sharp}`, a double superscript that LaTeX does
  not compile; edit the string if you need it in a document.
- The Schouten–Nijenhuis bracket renders as `[P,Q]_{[\cdot,\cdot]_{SN}}` and the derived
  bracket as `[\alpha,\beta]_{{\cdot,\cdot}_{\pi}}`.
- $\mathcal L^E_u$ renders as `L^E_{u}`, without `\mathcal`.
- The same $Df$ has two notations: `E.D(f)` renders as `d_{E}f` and `d_E(E, f)` as
  `d_E\!\left(f\right)`.

## Small differences

- `registry=` is required by {py:func}`jacopy.functions` but not by
  {py:func}`jacopy.vector_fields`, {py:func}`jacopy.forms` or {py:func}`jacopy.tensors`.
- `ExpansionEngine.expand` does not simplify; `0 + Y` stays as it is.
- `reg.declare` raises `ValueError` if the same property is declared twice on the same
  object.
