# Roadmap

This page describes where JacoPy is heading. Everything here is a
**plan or an idea**, not a commitment or a release schedule. What is
missing today is listed in [Limitations](limitations.md).

## Two kinds of users

1. A user **who writes code** uses JacoPy as a Python library, in
   notebooks or scripts, much as one uses SageMath today.
2. A user **who does not write code** enters definitions, identities and
   theorems through a **web interface**, in the spirit of mathdf,
   Symbolab or WolframAlpha, and JacoPy shows the proof step by step,
   with its assumptions and with LaTeX and APA output. A natural shape
   is a page per area (for example a generalized-geometry page with
   Dorfman and Courant blocks and "prove" buttons).

**Already in place:** the proof engine, step-by-step recording,
assumption tracking, LaTeX output with an APA bibliography, HTML theorem
cards in notebooks, and the model oracle.

**Three missing layers**, in order:

| Layer | What it will do | Today |
|---|---|---|
| Input parser | Convert text or LaTeX written by the user (for example `\mathcal{L}_X \omega = \iota_X d\omega + d\iota_X\omega`) into a JacoPy term. | missing |
| Front door (`GeometryContext`) | A single context object: declare a structure, add a rule, prove, record as a theorem, cite. In mathematical terms, a worksheet that begins "in this section let $E$ be a Courant algebroid". | planned |
| Server | Pass a request from the web page to the front door and send back the result (steps, assumptions, LaTeX). | missing |

The server is the machinery behind a "prove" button; it can be built
on top of the front door without touching the proof engine.

### The front door

Today the research interface works, but a user has to import from
several modules and pass infrastructure such as the registry or the
probe function by hand. The planned `GeometryContext` (with
`.declare(structure)`, `.add_rule`, `.prove(lhs, rhs)`,
`.check(AlgebroidData)` and `.cite`) would offer the cycle "add an
assumption, prove, record as a theorem, cite in another question" on a
single surface. Related planned pieces are a full instance assumption
(`assume_zero`), a common metric protocol, a hierarchy of error classes
and a user guide. The prerequisites (result objects, theorem
requirements, structure providers, normal forms) are complete.

## Idea: rejection diagnostics

When a proof does not close, the library shows the residual, which is
already useful. The idea is to let the engine also record **why** it
skipped a step (no alternation certificate was found, a constancy
record was missing, a theorem fell outside its citation scope) and to
show a hint next to the residual, such as "no alternation certificate
for this head, rule not applied". This would show users where the
engine got stuck, and would catch the library's own completeness gaps
early.

## Idea: the oracle as a user feature

Today the model oracle is a checking tool for developers. Opened to
users, it could serve four purposes, each labeled "an example is not a
proof":

1. **A concrete example next to a proof:** for a closed identity, a
   witness such as "with these $X$, $Y$, $\omega$ on $\mathbb{R}^3$ both
   sides equal 1874".
2. **A counterexample for a claim that does not close:** "at this point
   the left-hand side is 1972 and the right-hand side 946", matching
   the residual shown by the engine.
3. **Testing a conjecture before proving it** on a few random models.
4. **Teaching examples:** concrete coordinate versions of textbook
   identities.

## Plan: proofs in symbolic degree

Today the Cartan relations and $d^2=0$ are proved separately for each
concrete degree; on $TM$ there is one proof for each of $p=1,\dots,5$.
The reason is the way the engine works: a $p$-form is evaluated on $p$
vector fields and $d$ is expanded by the Palais formula

$$d\omega(X_0,\dots,X_p)=\sum_i(-1)^iX_i\big(\omega(\dots\hat X_i\dots)\big)+\sum_{i<j}(-1)^{i+j}\omega([X_i,X_j],\dots),$$

and expanding these sums requires a concrete $p$. On paper the general
proof is done by induction or by index computation; neither is yet
available in the engine. Two routes are planned, possibly together:

1. **Symbolically indexed sums:** simplify objects such as
   $\sum_{i=0}^{p}$ and $\sum_{i<j}$ without expanding them, by sign and
   index-shift rules. The code already has the beginnings of this
   (`IndexedSum`, and symbolic degrees through `Degree`); the missing
   parts are the rules that apply the Palais formula, reindex and track
   signs on these objects.
2. **An induction scheme:** recognizing "a proof for $p$ gives a proof
   for $p+1$" as a proof form in the engine, with today's concrete
   proofs as base cases.

The gain: the Cartan calculus and $d^2=0$, and their algebroid
versions, become single theorems valid in all degrees, and the "higher
$p$" claims in the packages can move from docstrings to proofs.

## Mathematical roadmap

The open mathematical items are listed in
{ref}`Limitations <limitations-open-items>`. The
most prominent are: splitting the general $\Psi$-twist into calculus
terms and transport without declarations; the vector component of the
Nambu double's Jacobi identity and $p\ge2$; the Koszul–Brylinski
bracket of mixed degrees; the general Bourbaki decomposition; and the
exceptional Drinfel'd conditions, once the reference for the
exceptional bracket is identified.

Further geometries (the whole of exceptional generalized geometry,
conformal and projective geometry, supergravity, T- and U-duality,
spinors, AKSZ constructions, …) fit the existing package structure: a
new geometry is added under `jacopy/packages/` with its own rules, and
a new structure kind can be registered without changing library files
(see {ref}`Architecture <architecture-extension-points>`).
