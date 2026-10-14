# Choosing a proof strategy

A proof strategy decides the order in which the rules of an engine are applied. The default
strategy follows one fixed order and returns the first proof it finds. A search strategy
explores several orders and returns the best proof under a criterion you choose. This page
shows how to ask for a shorter, a more readable or a more elementary proof, how to bound the
search, and what each of the strategy classes in `jacopy.proof` is for. The choice of
strategy never changes what counts as a proof; see
[Proof search and soundness](../explanation/trust-model.md#proof-search-and-soundness).

## Setup

The example identity combines two facts about a 1-form $\alpha$: the commutator
$\mathcal L_X\iota_Y\alpha-\iota_Y\mathcal L_X\alpha=\iota_{[X,Y]}\alpha$ and the intrinsic
formula $(d\alpha)(X,Y)=X\alpha(Y)-Y\alpha(X)-\alpha([X,Y])$. The commutator is also
available as a proved theorem, which is cited into the engine, so a proof may either use the
theorem as one step or derive the same result from the definitions.

```python
import jacopy
import jacopy.central.tangent as tg
from jacopy.central.tangent import tangent_engine, d
from jacopy.proof import (SearchStrategy, PortfolioStrategy, ExpandAndSimplify,
    UnrollToFoundations, AgreementOnGenerators, DerivedBracketStrategy, Strategy)
from jacopy.proof.search import node_count

reg = jacopy.PropertyRegistry()
f, h = jacopy.functions("f h", registry=reg)
X, Y = jacopy.vector_fields("X Y")
(alpha,) = jacopy.forms("alpha", degree=1)
L, I, B = jacopy.lie_derivative, jacopy.interior, jacopy.lie_bracket

book = jacopy.TheoremBook()
tg.register_cartan_theorems(book, alpha, X, Y, f, registry=reg)
eng = jacopy.cite(tangent_engine(registry=reg), book, *book.names())

comm = L(X)(I(Y)(alpha)) - I(Y)(L(X)(alpha))
lhs = comm + jacopy.multi_eval(d(alpha), X, Y)
rhs = I(B(X, Y))(alpha) + X(alpha(Y)) - Y(alpha(X)) - alpha(B(X, Y))
```

## Asking for a particular kind of proof

`jacopy.prove(lhs, rhs, registry=..., engine=..., prefer=...)` takes one of three values for
`prefer`. Each names a scorer; lower scores are better.

| `prefer` | Chooses the proof with | Tie-break |
|---|---|---|
| `"shortest"` | the fewest steps | first found |
| `"readable"` | the smallest peak intermediate expression (the largest number of expression nodes in any `before` or `after` of the chain) | fewer steps |
| `"elementary"` | the fewest steps that cite a theorem (`provenance_tag == "theorem"`) | fewer steps |

Without `prefer` (the default, `prefer=None`), `jacopy.prove` is the same as
{py:func}`jacopy.show_equal`: the deterministic `ExpandAndSimplify` strategy, which applies
rules in a fixed order and does not search. The script below proves the same identity four
ways and prints, for each proof, the number of steps, the peak expression size and the
number of theorem citations.

```python
def profile(chain):
    peak = max(max(node_count(s.before), node_count(s.after)) for s in chain.steps)
    cited = sum(1 for s in chain.steps if s.provenance_tag == "theorem")
    return len(chain.steps), peak, cited

print("default   ", profile(jacopy.prove(lhs, rhs, registry=reg, engine=eng)))
for p in ("shortest", "readable", "elementary"):
    chain = jacopy.prove(lhs, rhs, registry=reg, engine=eng, prefer=p)
    print(f"{p:<10}", profile(chain))
```

```text
default    (7, 54, 0)
shortest   (3, 49, 1)
readable   (4, 39, 1)
elementary (7, 54, 0)
```

The shortest proof cites the commutator theorem and needs three steps. The readable proof
is one step longer, but its largest intermediate expression is smaller. The elementary proof
avoids the theorem and derives everything from the definitions; here it has the same profile as the
default proof. On identities with only one reasonable proof all three choices return the
same chain.

The rules of the shortest proof:

```python
chain = jacopy.prove(lhs, rhs, registry=reg, engine=eng, prefer="shortest")
for s in chain.steps:
    print(s.provenance_tag, "|", s.rule[:60])
```

```text
axiom | intrinsic d (Cartan-TM): Palais formula dω(X_0,…,X_p) = Σ(−1
theorem | theorem L_iota_commutator ⇒: [L_X, ι_Y] ω = ι_{[X,Y]} ω  (1-
None | simplify
```

## Bounding the search

`prefer` switches to `SearchStrategy`. Any further keyword argument of
`jacopy.prove` is passed to it; you can also construct the strategy yourself.

| Keyword | Default | Meaning |
|---|---|---|
| `prefer` | `"shortest"` (on `SearchStrategy`) | the scorer, as above |
| `max_depth` | `12` | the largest number of moves in a proof |
| `max_states` | `5000` | the number of distinct expressions explored before the search gives up the exhaustive phase |
| `beam_width` | `32` | the number of candidates kept per level by the fallback search |
| `max_solutions` | `16` | the search stops after this many proofs and returns the best of them |

The search works on the expression $\text{lhs}-\text{rhs}$ and looks for a sequence of moves
that reaches $0$. A move is one rule applied at one position, one product-rule pass or one
simplification pass. Expressions reached along different routes are merged, so the search
counts distinct expressions, not routes. The first phase is a breadth-first search that
collects proofs up to `max_depth` and returns the best under the scorer. If it explores more
than `max_states` expressions without finding a proof, a beam search takes over: at each
level it keeps the `beam_width` smallest expressions and returns the first proof it reaches.
A beam proof is not compared with other proofs, so `prefer` has no effect on it.

After a run, `strategy.last_stats` records what happened:

```python
s = SearchStrategy(prefer="shortest")
s.prove(lhs, rhs, registry=reg, engine=eng)
st = s.last_stats
print(st["engine"], st["states_explored"], st["solutions_found"], st["chosen_length"])
print(st["solution_lengths"])
print(len(s.last_solutions), "proofs found")
```

```text
bfs 294 16 3
[3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6, 6, 6, 7, 8]
16 proofs found
```

The search explored 294 distinct expressions and stopped at the default `max_solutions=16`;
the lengths of the proofs it found range from 3 to 8, and the best one under `"shortest"` has
3 steps. `last_stats["engine"]` is `"bfs"` or `"beam"`, and `last_solutions` holds the step
lists of all proofs found.

A small state budget sends the search to the beam fallback, which still finds a proof here:

```python
s = SearchStrategy(prefer="shortest", max_states=50)
chain = s.prove(lhs, rhs, registry=reg, engine=eng)
print(len(chain.steps), s.last_stats["engine"], s.last_stats["budget_exhausted"])
```

```text
3 beam True
```

When no proof is found, `prove` raises {py:class}`jacopy.ProofFailure`. The message states the
depth and the state budget, and whether the beam fallback was tried. Unlike the default
strategy, the search does not attach a residual (`residual` is `None`).

```python
for opts in ({"max_depth": 2}, {"max_depth": 1, "max_states": 5}):
    try:
        SearchStrategy(**opts).prove(lhs, rhs, registry=reg, engine=eng)
    except jacopy.ProofFailure as fail:
        print(str(fail).split(" within ")[1], "| residual:", fail.residual)
```

```text
depth 2 / 5000 states | residual: None
depth 1 / 5 states (beam fallback also failed) | residual: None
```

`max_solutions=1` returns the first proof the breadth-first search finds, which is also a
shortest one. An unknown `prefer` value raises `ValueError`:

```python
s = SearchStrategy(max_solutions=1)
print(len(s.prove(lhs, rhs, registry=reg, engine=eng).steps), s.last_stats["solutions_found"])
try:
    jacopy.prove(lhs, rhs, registry=reg, engine=eng, prefer="fastest")
except ValueError as err:
    print(err)
```

```text
3 1
prefer must be one of ('shortest', 'readable', 'elementary'), got 'fastest'
```

Without `prefer`, `jacopy.prove` does not search and ignores the search keywords: the call
below runs the default strategy.

```python
print(len(jacopy.prove(lhs, rhs, registry=reg, engine=eng, max_states=1).steps))
```

```text
7
```

The search explores many expressions, so it is slower than the default strategy. Use it when
the default proof is long or hard to read, not as the first attempt on every identity.

## The strategy classes

Every strategy has the method
`prove(lhs, rhs, *, registry=None, engine=None) -> ProofChain` and raises `ProofFailure` when
it cannot close. A strategy object can be passed to {py:func}`jacopy.show_equal` with
`strategy=`.

| Class | What it does | Use it when |
|---|---|---|
| `ExpandAndSimplify()` | Applies rules in a fixed order (leftmost-innermost, first match), alternating with the product rule and the simplifier, until $\text{lhs}-\text{rhs}$ is $0$ or stops changing. The default. | Almost always: it is fast and deterministic. |
| `SearchStrategy(prefer=..., ...)` | Graph search over rule orders, as above. | The default proof is long, or you want a short, readable or theorem-free proof. |
| `PortfolioStrategy([s1, s2, ...])` | Tries the strategies in order and returns the first proof. If all fail, raises one `ProofFailure` that lists every failure. | You want a fast attempt first and a slower one as fallback. |
| `UnrollToFoundations(inner)` | Runs `inner` with the engine switched to `"foundational"` mode, in which every theorem step carries the theorem's own proof as sub-steps. | You want a self-contained transcript that bottoms out at definitions and axioms. |
| `AgreementOnGenerators(algebra, sub_strategy=None)` | Proves an equality of two derivations of the same degree by proving that they agree on each generator in `algebra.generators`. | Operator identities. `jacopy.proof.prove_operator_equation` wraps it. |
| `DerivedBracketStrategy()` | Proves the Jacobi identity of a derived bracket $[[a,Q],b]$ by reducing it to $[Q,Q]=0$, after checking the hypotheses of the derived bracket theorem. Its method is `prove_jacobi(bracket, a, b, c, registry=...)`. | Brackets built with `jacopy.brackets.derived.derived_bracket`. `jacopy.proof.prove_jacobi` calls it. |
| `Strategy` | The abstract base class. | Writing a strategy of your own. |

**`ExpandAndSimplify` and its step budget.** `ExpandAndSimplify().prove` takes
`max_steps=1024`, the number of rule applications allowed per expansion pass. When it runs
out the strategy raises `RuntimeError`, not `ProofFailure`, because an exhausted budget says
nothing about the identity. `show_equal` and `jacopy.prove` do not take `max_steps`; construct
the strategy to change it.

```python
try:
    ExpandAndSimplify().prove(lhs, rhs, registry=reg, engine=eng, max_steps=2)
except RuntimeError as err:
    print(err)
print(len(jacopy.show_equal(lhs, rhs, registry=reg, engine=eng,
                            strategy=SearchStrategy(prefer="readable")).steps))
```

```text
ExpansionEngine did not converge within 2 steps; expansion pass of round 1.1 used all 2 steps
4
```

**`PortfolioStrategy`.** Here a search limited to depth 1 fails and the default strategy
closes. With two failing members the error names both.

```python
pf = PortfolioStrategy([SearchStrategy(max_depth=1), ExpandAndSimplify()])
print(len(pf.prove(comm, I(B(X, Y))(alpha), registry=reg, engine=eng).steps))
try:
    PortfolioStrategy([SearchStrategy(max_depth=1), SearchStrategy(max_depth=1,
                       prefer="readable")]).prove(comm, I(B(X, Y))(alpha),
                                                   registry=reg, engine=eng)
except jacopy.ProofFailure as fail:
    print(str(fail).splitlines()[0])
    print(len(str(fail).splitlines()) - 1, "member failures listed")
```

```text
6
all portfolio strategies failed:
2 member failures listed
```

**`UnrollToFoundations`.** The shortest proof of the commutator cites the theorem in one
step. In foundational mode the same step carries the theorem's proof, so the transcript
contains every step down to the definitions. The function below counts all steps, nested
ones included.

```python
def all_steps(steps):
    return sum(1 + all_steps(s.children) for s in steps)

short = SearchStrategy().prove(comm, I(B(X, Y))(alpha), registry=reg, engine=eng)
deep = UnrollToFoundations(SearchStrategy()).prove(comm, I(B(X, Y))(alpha),
                                                   registry=reg, engine=eng)
print(len(short.steps), all_steps(short.steps), "|", len(deep.steps), all_steps(deep.steps))
print(eng.mode)          # the engine you pass is not changed
```

```text
2 3 | 2 9
efficient
```

**`AgreementOnGenerators`.** The algebra argument is any object with a `generators`
attribute. Here $\mathcal L_X$ and $X$ are compared on functions, with the generator $f$.

```python
class Functions:
    generators = (f,)

ag = AgreementOnGenerators(Functions(), sub_strategy=SearchStrategy())
chain = ag.prove(L(X), X, registry=reg, engine=tangent_engine(registry=reg))
print(len(chain.steps), "|", chain.steps[0].rule[:60])
```

```text
1 | AgreementOnGenerators
```

**`DerivedBracketStrategy`.** The strategy first checks the hypotheses of the derived
bracket theorem for the given triple and refuses to conclude when one of them cannot be
verified. For the derived bracket of an undeclared bivector $\pi$ with the
Schouten–Nijenhuis bracket, the bracket is not known to be skew on functions, so the
strategy raises `ProofFailure` instead of citing the theorem.

```python
from jacopy.brackets.derived import derived_bracket
from jacopy.central.tangent import SN

pi = jacopy.bivector("pi")
(k,) = jacopy.functions("k", registry=reg)
db = derived_bracket(SN, pi)
print(db.jacobi_obstruction())
try:
    DerivedBracketStrategy().prove_jacobi(db, f, h, k, registry=reg)
except jacopy.ProofFailure as fail:
    print(str(fail).split(" — ")[0])
```

```text
[·,·]_SN(pi, pi)
DerivedBracketStrategy: the derived bracket is not certified skew on this triple
```

**A strategy of your own.** Subclass `Strategy` and implement `prove`. The example below
tries the default strategy and, if it fails, a search; this is what `PortfolioStrategy` does
in general. A custom strategy can only order and combine the rules of the engine, so it
cannot produce a step that the engine would not allow.

```python
class DefaultThenSearch(Strategy):
    name = "DefaultThenSearch"
    def prove(self, lhs, rhs, *, registry=None, engine=None):
        try:
            return ExpandAndSimplify().prove(lhs, rhs, registry=registry, engine=engine)
        except jacopy.ProofFailure:
            return SearchStrategy().prove(lhs, rhs, registry=registry, engine=engine)

print(len(jacopy.show_equal(lhs, rhs, registry=reg, engine=eng,
                            strategy=DefaultThenSearch()).steps))
```

```text
7
```

## See also

- [Running proofs](running-proofs.md) for engines, `show_equal` and `ProofResult`.
- [Common parameters and settings](../reference/parameters.md) for every keyword on one
  page.
- [Trust model](../explanation/trust-model.md) for what a proof chain certifies.
