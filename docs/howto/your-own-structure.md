# Your own structure: the research interface

This page answers the question "how do I work with a structure that is not ready-made in the
library?". You may have a bracket and want to know which axioms it satisfies, or want an
identity proved from exactly the axioms you choose. The research interface
`jacopy.research` provides five tools for this: typed sections (`SectionType`), block
matrices (`BlockMatrix`), axiom checking (`AlgebroidData` and `AxiomSuite`), automatic engine
assembly (`assemble_engine`), and registration of your own structure kinds
(`StructureKind`). You can also write your own rewrite rules (`Definition`).

## Setup

```python
import jacopy
reg = jacopy.PropertyRegistry()
f, g, h = jacopy.functions("f g h", registry=reg)
X, Y, Z = jacopy.vector_fields("X Y Z")
alpha, beta, gamma = jacopy.forms("alpha beta gamma", degree=1)

from jacopy.research import (
    SectionType, GeneralizedSection, Slot, BlockMatrix, Map, Operator, Identity, ZeroOperator,
    as_operator, Bracket, AlgebroidData, AxiomSuite, assemble_engine, assembly_report, Scan,
    StructureKind, register_structure_kind, register_family, register_family_rule,
    antisymmetrize_indices, antisymmetrize, permutation_sign, swap_indices, rename_indices,
    WedgeGradedOrderDefinition, WedgeScalarFactorDefinition,
)
from jacopy.research.providers import is_provider, structure_rules, declared_axioms
from jacopy.research.block_matrix import ScaledOperator
from jacopy.research.structure_kinds import unregister
from jacopy.central.algebroid import algebroid, algebroid_engine, DECLARATIONS, LEVELS, jacobiator
from jacopy.central.algebroid.context import AlgebroidBracket
from jacopy.proof.result import prove
from jacopy.core.expr import Integer, Product, Sum, Neg
from jacopy.algebra.derivation import Act
```

## How the objects are set up

```python
# (1) An abstract algebroid: only the axioms you choose hold
E = algebroid("E", declare=("right-leibniz",))      # bracket [., .]_E and anchor rho
u, v, w = E.sections("u v w")

# (2) Typed generalized sections of TM + T*M
T = SectionType.generalized_tangent()                # TM + Lambda^1 T*M
e1, e2, e3 = T.section(X, alpha), T.section(Y, beta), T.section(Z, gamma)

# (3) The block matrix Psi = (1 theta-sharp; 0 1) for a bivector theta (Poisson package)
from jacopy.packages.poisson import nambu_structure
theta = nambu_structure("θ", p=1)
Psi = BlockMatrix(T, [[1, Map(theta.sharp_vf, "θ♯")], [0, 1]], name="Ψ")

# (4) All the data of a bracket: bracket, anchor, pairing, D and the R-valued Lie action
from jacopy.packages.drinfeld import dorfman_double, canonical_pairing
from jacopy.central.tangent.exterior import d
std = AlgebroidData(
    bracket=Bracket.from_components(T, dorfman_double, name="Dorfman"),
    anchor=lambda e: e[0],                                   # rho(U + omega) = U
    pairing=lambda a, b: (canonical_pairing(*a, *b),),       # <e1, e2>, as a tuple of components
    D=lambda p: T.section(Integer(0), d(p)),                 # D<., .> = 0 + d<., .>
    lie_R=lambda e, q: (Act(e[0], q),),                      # L^R_e g = rho(e)(g)
    name="Dorfman",
)
suite = AxiomSuite(std, registry=reg, probe=h, structures=(theta,))

# (5) Two operators used below
S_op = Map(theta.sharp_vf, "θ♯")
Lx = Map(lambda x: jacopy.lie_derivative(X)(x), "L_X")
```

- `declare=` takes a **subset** of the atomic axioms (`DECLARATIONS`) or of the ready-made
  levels (`LEVELS`, for example `"leibniz"` = right Leibniz + Jacobi). An axiom that is not
  declared is never used.
- A `GeneralizedSection` is not an expression but a tuple of components: `tuple(e)` gives
  the components and `e[0]` is the vector part. `jacopy.to_latex` is applied component by
  component.
- `AxiomSuite(..., probe=h)`: vector-valued identities are tested by evaluating them on the
  function `h`, and $k$-form-valued identities on $k$ fresh vector fields.
- `structures=(theta,)`: if $\theta^\sharp$ appears in an expression, its structure must be
  given explicitly; the engine does not guess the rules of a structure it has not been told
  about.

## Choosing axioms by subset

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| list of atomic axioms | `DECLARATIONS` | | tuple of names | The names accepted by `declare=` |
| ready-made levels | `LEVELS` | | dict, for example `'leibniz': ('right-leibniz', 'jacobi')` | A level expands into atomic axioms |
| algebroid with chosen axioms | `algebroid("E", declare=("right-leibniz",))` | name; tuple of axiom or level names | algebroid | `declare=()` means no axioms at all |
| adding a declaration | `E.with_declarations("jacobi")` | axiom names | a new algebroid | The original is unchanged |
| $[u,v]_E$ | `E.bracket(u, v)` | sections of E | $\left[u,\, v\right]_{E}$ | Opaque bracket |
| $\rho(u)$ | `E.anchor(u)` | section of E | $\rho\!\left(u\right)$ | |
| $J(u,v,w)$ | `jacobiator(E, u, v, w)` | algebroid; three sections | $J_{E}\!\left(u,\, v,\, w\right)$ | |

The same expression is the same node under every axiom set; the assumptions live in the
engine, not in the expression. The right Leibniz rule $[u,fv]_E=\rho(u)(f)\,v+f[u,v]_E$
closes exactly when an axiom set containing it is declared:

```python
def right_leibniz_goal(A):
    a, b = A.sections("u v")
    return (A.bracket(a, Product(f, b)),
            Sum(Product(Act(A.anchor(a), f), b), Product(f, A.bracket(a, b))))

for decl in [(), ("right-leibniz",), ("almost-leibniz",), ("local",)]:
    A = algebroid("E", declare=decl)
    lhs, rhs = right_leibniz_goal(A)
    res = prove(algebroid_engine(A, registry=reg), lhs, rhs, registry=reg)
    print(decl, res.status)

El = algebroid("E", declare=("leibniz",))
a1, a2, a3 = El.sections("u v w")
res = prove(algebroid_engine(El, registry=reg), jacobiator(El, a1, a2, a3), jacopy.Zero, registry=reg)
print(res.status, [a.name for a in res.declared])
```

```text
() RESIDUAL
('right-leibniz',) CLOSED
('almost-leibniz',) CLOSED
('local',) CLOSED
CLOSED ['Leibniz-Jacobi (E): J(u,v,w) = 0']
```

## Typed sections and block matrices

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $TM\oplus T^*M$ | `SectionType.generalized_tangent()` | p (default 1) | `TM ⊕ Λ¹T*M` | `generalized_tangent(2)` gives `TM ⊕ Λ²T*M` |
| $TM\oplus\Lambda^2T^*M\oplus\Lambda^5T^*M$ | `SectionType.exceptional()` | | `TM ⊕ Λ²T*M ⊕ Λ⁵T*M` | |
| your own direct sum | `SectionType(Slot("vector"), Slot("form", 2))` | `Slot(kind, degree)` with kind `"vector"`, `"form"` or `"function"` | a section type | `Slot("form", 2)` is a $\Lambda^2T^*M$ slot |
| $X\oplus\alpha$ | `T.section(X, alpha)` | components | section $(X, \alpha)$ | Same as `GeneralizedSection(T, X, alpha)`; a component of the wrong kind raises `TypeError` |
| component kind check | `T.slots[1].accepts(alpha)` | expression | `"valid"`, `"invalid"` or `"unknown"` | `accepts(X)` gives `"invalid"`; an opaque expression gives `"unknown"` |
| $e_1+e_2$ | `e1 + e2` | sections | $(X + Y, \alpha + \beta)$ | slot by slot |
| $f\cdot e_1$ | `e1.scale(f)` | f: function | $(f \, X, f \, \alpha)$ | $C^\infty(M)$-module structure |
| $\Psi=\begin{pmatrix}1&\theta^\sharp\\0&1\end{pmatrix}$ | `BlockMatrix(T, [[1, Map(theta.sharp_vf, "θ♯")], [0, 1]], name="Ψ")` | type; rows of 0, 1, `Map` or `Operator` | block matrix | The entry `Psi[0, 1]` is `θ♯` |
| $(\Psi e)_i=\sum_j\Psi_{ij}e_j$ | `Psi(e1)` | section | $(X + \theta(\alpha), \alpha)$ | Same as `Psi.apply(e1)` |
| $\Psi^{-1}=\sum_k(-N)^k$ | `Psi.inverse()` | | `( 1 −θ♯ ; 0 1 )` | Derived only for unipotent matrices |
| is it unipotent? | `Psi.is_unipotent` | (a property) | `True` | |
| $\Psi\Psi^{-1}$, $\Psi^2$ | `Psi @ Psi.inverse()` | block matrices | the identity matrix | `Psi @ Psi` gives `( 1 (θ♯ + θ♯) ; 0 1 )`; `BlockMatrix.identity(T)` is the identity |
| operator $\Lambda^1\to TM$ | `Map(theta.sharp_vf, "θ♯")` | a function on expressions; a name | `Operator` | `as_operator(1)` is `Identity()` and `as_operator(0)` is `ZeroOperator()` |
| $\theta^\sharp\circ\mathcal L_X$ | `(S_op @ Lx)(beta)` | two operators | $\theta(\mathcal{L}_{X}(\beta))$ | |
| $S+S$, $-S$, $S-S$ | `(S_op + S_op)(beta)`, `(-S_op)(beta)`, `(S_op - S_op)(beta)` | operators | $\theta(\beta)+\theta(\beta)$, $-\theta(\beta)$, $0$ | |
| $f\cdot S$ | `ScaledOperator(f, S_op)(beta)` | function; operator | $f \, \theta(\beta)$ | `f * S_op` is not supported |

## Checking axioms with `AxiomSuite`

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| bracket from a component formula | `Bracket.from_components(T, dorfman_double, name="Dorfman")` | type; a function `fn(*e1, *e2) -> tuple` | `Bracket` | The library's component brackets have this form |
| $[e_1,e_2]_D$ | `std.bracket(e1, e2)` | two sections | $([X, Y],\ \mathcal{L}_{X}\beta - \mathcal{L}_{Y}\alpha + d\,\iota_{Y}\alpha)$ | Dorfman |
| $\rho(e_1)$ | `std.anchor(e1)` | section | $X$ | |
| $\langle e_1,e_2\rangle$ | `std.pairing(e1, e2)` | two sections | $(\iota_{X}\beta + \iota_{Y}\alpha)$ | a tuple of components |
| $[e_1,fe_2]=f[e_1,e_2]+(\rho(e_1)f)e_2$ | `suite.right_leibniz(e1, e2, f)` | two sections; function | report: both components `CLOSED` | |
| $[e_1,e_2]+[e_2,e_1]=D\langle e_1,e_2\rangle$ | `suite.symmetric_part(e1, e2)` | two sections | `CLOSED` | Needs `pairing` and `D` |
| $\rho[e_1,e_2]=[\rho e_1,\rho e_2]$ | `suite.anchor_morphism(e1, e2)` | two sections | `CLOSED` | A residual, if any, is the obstruction |
| $\mathcal L^R_{e_1}\langle e_2,e_3\rangle=\langle[e_1,e_2],e_3\rangle+\langle e_2,[e_1,e_3]\rangle$ | `suite.metric_invariance(e1, e2, e3)` | three sections | `CLOSED` | Needs `lie_R` |
| $[e_1,[e_2,e_3]]=[[e_1,e_2],e_3]+[e_2,[e_1,e_3]]$ | `suite.jacobi(e1, e2, e3)` | three sections; `max_steps`, `components` | `CLOSED` | Can be slow; select components with `components=(0, 1)` |
| all at once | `suite.run(e1, e2, f, e3=e3)` | two sections, a function, optionally a third section | `SuiteReport`; `.all_closed` | Without `e3`, metric invariance and Jacobi are skipped |
| $[e_1,e_2]_\Psi=\Psi^{-1}[\Psi e_1,\Psi e_2]$ | `std.bracket.twist(Psi)(e1, e2)` | block matrix | $([X + \theta(\alpha), Y + \theta(\beta)] - \theta(\dots),\ \dots)$ | Only the bracket is twisted |
| transport the whole structure | `twisted = std.transport(Psi)` | block matrix | `AlgebroidData` | $\rho'=\rho\circ\Psi$, $\langle\cdot,\cdot\rangle'=\langle\Psi\cdot,\Psi\cdot\rangle$, $D'=\Psi^{-1}D$ |

Each row of a report is a `CheckResult` with the fields `axiom`, `component`, `status`,
`seconds`, `steps`, `residual` and `note`:

```python
rep = suite.run(e1, e2, f)
twisted = std.transport(Psi)          # Psi applied to the whole structure
print(rep.all_closed)
print([(r.axiom, r.component, r.status) for r in rep.results])
rep_t = AxiomSuite(twisted, registry=reg, probe=h, structures=(theta,)).run(e1, e2, f)
print(rep_t.all_closed, len(rep_t.results))
```

```text
True
[('right-Leibniz', 'TM', 'CLOSED'), ('right-Leibniz', 'Λ¹T*M', 'CLOSED'), ('symmetric part', 'TM', 'CLOSED'), ('symmetric part', 'Λ¹T*M', 'CLOSED'), ('anchor morphism', 'ρ on probe', 'CLOSED')]
True 5
```

The transported Dorfman structure passes the same checks without any assumption on
$\theta$.

## `assemble_engine`: building the engine from the expression

`assemble_engine` looks at the node families that occur in the expressions and adds the
rules they need; `assembly_report` explains what was added and why.

```python
tw = twisted.bracket(e1, e2)
eng = assemble_engine(*tw, registry=reg, structures=(theta,))
expr = jacopy.wedge(Product(f, alpha), beta)
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| node families in an expression | `Scan(tw)` | expressions | `Scan(families=[...], sharps=['θ'])` | |
| engine with the required rules | `assemble_engine(*tw, registry=reg, structures=(theta,))` | expressions; registry; structures; `extra=(rule, ...)` | `ExpansionEngine` | `ValueError` if $\theta^\sharp$ occurs and `structures` is not given |
| explanation | `assembly_report(eng)` | engine | list of lines | Which rule was added and why |
| normal form | `jacopy.normalize(eng, tw[1], reg).expr` | engine, expression, registry | $d\,\theta(\alpha,\beta) + d\langle \beta, X \rangle + \iota_{X}d\beta - \iota_{Y}d\alpha + \iota_{\theta(\alpha)}d\beta - \iota_{\theta(\beta)}d\alpha$ | |
| declaring the Poisson condition | `assemble_engine(tw[0], registry=reg, structures=(theta.with_declarations("fundamental-identity"),))` | | engine | The report states that the fundamental identity is declared |
| $(f\alpha)\wedge\beta=f(\alpha\wedge\beta)$ | `jacopy.normalize(assemble_engine(expr, registry=reg), expr, reg).expr` | | $\left(\alpha \wedge \beta\right) \, f$ | Rule: wedge scalar pull-out |
| $\beta\wedge\alpha=-\alpha\wedge\beta$ | `jacopy.normalize(assemble_engine(jacopy.wedge(beta, alpha), registry=reg), jacopy.wedge(beta, alpha), reg).expr` | | $-\alpha \wedge \beta$ | Only in concrete degrees |
| adding your own rule | `assemble_engine(expr, registry=reg, extra=(WedgeScalarFactorDefinition(reg),))` | `extra`: rule instances | engine | `extra` rules are not deduplicated |

```python
for line in assembly_report(eng):
    print(line)
```

```text
scanned 2 expression(s): Scan(families=['act', 'exterior_derivative', 'interior', 'lie_bracket', 'lie_derivative', 'nambu_sharp'], sharps=['θ'])
base: tilde-calculus engine hosted by θ (Cartan calculus + Koszul/tilde rules) — no fundamental-identity declaration
+ zero product: 0·x = 0 (slot-reachable)  [always: zero products inside operator slots]
+ sharp-slot alternating normalization: θ♯(slot) with the slot's MultiEvals in canonical order  [sharp slots present (alternation must reach inside them)]
```

## Writing your own rules and axioms

Scenario: a bare bundle $A$ with a bracket and an anchor and **no axioms at all**. You write
two axioms yourself (right Leibniz and antisymmetry), choose which of them are declared
through a structure class of your own, and ask for the left Leibniz rule

$$[f\,u, v] = f\,[u, v] - \rho(v)(f)\,u .$$

A `Definition` has two methods: `matches(e)` (does the rule apply to this node?) and
`rewrite(e)` (what replaces it?). `role = "assumption"` marks the rule as an assumption, and
`anchor` names the node class the rule looks at.

```python
from jacopy.central.calculus.scalars import is_scalar_function

A = algebroid("A")                      # bare bundle: bracket and anchor, no axioms
p, q = A.sections("u v")

def split_scalar(x):                    # x = g*b  ->  (g, b)
    if isinstance(x, Product) and len(x.children) == 2 and is_scalar_function(x.children[0], reg):
        return x.children
    return None

class RightLeibniz(jacopy.Definition):
    name = "right Leibniz: [a, g·b] = ρ(a)(g)·b + g·[a, b]"
    role = "assumption"
    anchor = AlgebroidBracket
    def matches(self, e):
        return isinstance(e, AlgebroidBracket) and split_scalar(e.v) is not None
    def rewrite(self, e):
        g_, b = split_scalar(e.v)
        return Sum(Product(Act(A.anchor(e.u), g_), b), Product(g_, A.bracket(e.u, b)))

class Antisymmetry(jacopy.Definition):
    name = "antisymmetry: [a, b] = −[b, a]"
    role = "assumption"
    anchor = AlgebroidBracket
    @staticmethod
    def order(x):                       # a fixed order: products to the right
        return (isinstance(x, Product), x._repr_inner())
    def matches(self, e):
        return isinstance(e, AlgebroidBracket) and self.order(e.u) > self.order(e.v)
    def rewrite(self, e):
        return Neg(A.bracket(e.v, e.u))

class MyStructure:                      # records which axioms are declared
    AXIOMS = {"right-leibniz": RightLeibniz, "antisymmetry": Antisymmetry}
    def __init__(self, declared=()):
        self.name = "L"
        self.declarations = frozenset(declared)
    def declares(self, k):
        return k in self.declarations
    def with_declarations(self, *k):
        return MyStructure(self.declarations | set(k))
    def engine_rules(self, registry=None, *, phase=None):
        rules = []
        for k in sorted(self.declarations):
            r = self.AXIOMS[k]()
            r.owner = self              # the structure owns its axiom
            rules.append(r)
        return rules
    def __eq__(self, o):
        return isinstance(o, MyStructure) and o.declarations == self.declarations
    def __hash__(self):
        return hash(("MyStructure", self.declarations))
    def __repr__(self):
        return f"MyStructure({sorted(self.declarations)})"

lhs = A.bracket(Product(f, p), q)                                              # [f u, v]
rhs = Sum(Product(f, A.bracket(p, q)), Neg(Product(Act(A.anchor(q), f), p)))  # f[u,v] - rho(v)(f) u

def prove_with(declared, lhs=lhs, rhs=rhs):
    S = MyStructure(declared)
    engine = algebroid_engine(A, registry=reg)   # definitional rules only
    for rule in S.engine_rules(reg):
        engine.register(rule)                    # plus the declared axioms
    return S, engine, prove(engine, lhs, rhs, registry=reg)

for declared in [(), ("right-leibniz",), ("antisymmetry",), ("right-leibniz", "antisymmetry")]:
    res = prove_with(declared)[2]
    print(declared, res.status, len(res.chain.steps) if res.chain else 0)

wrong = Product(f, A.bracket(p, q))              # the false identity [f u, v] = f [u, v]
res_wrong = prove_with(("right-leibniz", "antisymmetry"), lhs, wrong)[2]
print("false identity:", res_wrong.status, "| residual:", jacopy.to_ascii(res_wrong.residual))
```

```text
() RESIDUAL 1
('right-leibniz',) RESIDUAL 1
('antisymmetry',) RESIDUAL 2
('right-leibniz', 'antisymmetry') CLOSED 4
false identity: RESIDUAL | residual: -ρ(v)(f) * u
```

Of the four axiom sets, the identity closes only when both axioms are declared. With right
Leibniz alone the rule never fires, because $f$ sits in the first slot and the rule looks at
the second. The false identity does not close even with both axioms, and its residual is
exactly the missing term $-\rho(v)(f)\,u$.

## Registering your own structure kind

`MyStructure` implements the "provider" protocol: `name`, `declarations`, `declares`,
`with_declarations` and `engine_rules`. Once its kind is registered, `assemble_engine` sets
up the engine by itself.

```python
class MyKind(StructureKind):
    name = "my-structure"
    host_includes_rules = False
    def accepts(self, s):                    # which objects this kind handles
        return isinstance(s, MyStructure)
    def key(self, s):                        # the structure's key
        return s.name
    def host_engine(self, s, registry):      # base engine when s is the first structure
        return algebroid_engine(A, registry=registry)
    def host_report(self, s):                # what the report says about the base
        return f"base: algebroid engine of A, first structure {s.name} [{self.name}]"

kind = register_structure_kind(MyKind())
S_full = MyStructure(("right-leibniz", "antisymmetry"))
res = prove(assemble_engine(lhs, rhs, registry=reg, structures=(S_full,)), lhs, rhs, registry=reg)
print(res.status)
```

```text
CLOSED
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| does it follow the protocol? | `is_provider(MyStructure())` | object | `True` | `False` if a method is missing |
| the structure's rules | `structure_rules(S_full, reg)` | structure, registry | the rule objects | Only the declared ones |
| who assumes what? | `declared_axioms([S_full, theta])` | structures | `{'L': ['antisymmetry', 'right-leibniz'], 'θ': []}` | For reports |
| base engine | `MyKind().host_engine(S_full, reg)` | structure, registry | `ExpansionEngine` | If you change `host_engine`, change `host_report` too |

A rule can also be attached to a new **node family** instead of a structure:

```python
class ZeroBracketDefinition(jacopy.Definition):    # [a, 0] = 0
    name = "zero slot: [a, 0] = 0"
    anchor = AlgebroidBracket
    def matches(self, e):
        return isinstance(e, AlgebroidBracket) and e.v == Integer(0)
    def rewrite(self, e):
        return Integer(0)

fam = register_family(AlgebroidBracket, "user_bracket")
frule = register_family_rule("user_bracket", lambda r: ZeroBracketDefinition(),
                             "user brackets present", order=90)
zb = A.bracket(p, Integer(0))
print(Scan([zb]))
print(prove(assemble_engine(zb, registry=reg, structures=(S_full,)), zb, Integer(0), registry=reg).status)
```

```text
Scan(families=['user_bracket'], sharps=[])
CLOSED
```

Family rules belong to no structure, so supply axioms through a structure's `engine_rules`,
not as family rules; only then does the result show which axiom of which structure was
used. Registrations are global for the whole Python process; remove them with `unregister`
when you are done:

```python
for entry in (frule, fam, kind):
    unregister(entry)
```

## Index antisymmetrization

The component $\theta^{ab}$ is the evaluation of $\theta$ on two coframe fields:

```python
from jacopy.central.objects import frame
from jacopy.core.multi_eval import MultiEval
from jacopy.algorithms.simplify import simplify
co = frame().dual()
tab = MultiEval(theta.pi, co.field("a"), co.field("b"), alternating=True, slot_kind="covector")
tcd = MultiEval(theta.pi, co.field("c"), co.field("d"), alternating=True, slot_kind="covector")
T_ab = antisymmetrize_indices(tab, ("a", "b"))
```

| Math | In code | Arguments | Result | Note |
|---|---|---|---|---|
| $T^{[a_1\dots a_n]}=\frac1{n!}\sum_\sigma \operatorname{sgn}\sigma\,T^{a_{\sigma(1)}\dots}$ | `antisymmetrize_indices(Product(tab, tcd), ("a", "b", "c"))` | expression; index names | $\frac{1}{6}\big(\theta(e^{a},e^{b})\,\theta(e^{c},e^{d}) - \theta(e^{a},e^{c})\,\theta(e^{b},e^{d}) - \dots\big)$ | Six signed terms; $d$ stays free |
| unweighted $\sum_\sigma \operatorname{sgn}\sigma\,T^{\dots}$ | `antisymmetrize(tab, ("a", "b"), unit_weight=True)` | expression; names; `unit_weight` | $\theta(e^{a},e^{b}) - \theta(e^{b},e^{a})$ | `antisymmetrize` is another name for `antisymmetrize_indices` |
| $\operatorname{sgn}\sigma$ | `permutation_sign((1, 0, 2))` | tuple of positions | `-1` | `permutation_sign((1, 2, 0))` is `1` |
| $a\leftrightarrow b$ | `swap_indices(tab, "a", "b")` | expression; two names | $\theta\!\left(e^{b},\, e^{a}\right)$ | |
| simultaneous renaming | `rename_indices(tab, {"a": "c", "b": "d"})` | expression; dict | $\theta\!\left(e^{c},\, e^{d}\right)$ | Names do not clash |
| $T^{[ab]}+T^{[ba]}=0$ | `simplify(Sum(T_ab, swap_indices(T_ab, "a", "b")), reg)` | | $0$ | |

## Reading the results

`prove(engine, lhs, rhs, registry=reg)` returns a `ProofResult`. The examples use the closed
proof with both axioms (`res2`) and the residual with right Leibniz alone (`res1`).

```python
from jacopy.proof.diagnostics import diagnose
S2, eng2, res2 = prove_with(("right-leibniz", "antisymmetry"))
S1, eng1, res1 = prove_with(("right-leibniz",))
print(res2.status, res2.closed)
print([s.rule for s in res2.chain.steps])
print(sorted({a.kind for a in res2.requires}), len(res2.declared))
print(res1.residual is not None, res2.residual)
print(diagnose(res1.residual, registry=reg, engine=eng1).hints)
```

```text
CLOSED True
['antisymmetry: [a, b] = −[b, a]', 'right Leibniz: [a, g·b] = ρ(a)(g)·b + g·[a, b]', 'antisymmetry: [a, b] = −[b, a]', 'simplify']
['declared', 'registry', 'structure'] 2
True None
[]
```

| What is read | In code | Note |
|---|---|---|
| status | `res2.status` | `CLOSED`, `RESIDUAL`, `BUDGET` or `INVALID`. A residual term is not a refutation |
| proof steps | `[s.rule for s in res2.chain.steps]` | Each step carries the rule that justifies it |
| assumptions used | `res2.requires` | Records with `kind` and `name`; kinds include `declared`, `structure`, `registry` |
| only the declared axioms | `res2.declared` | |
| residual term | `res1.residual` | An expression for `RESIDUAL`, `None` for `CLOSED` |
| summary text | `res2.summary()` | Status, goal, assumption lines and the step budget |
| source of normalization | `res2.provenance` | |
| hints for a residual | `diagnose(res1.residual, registry=reg, engine=eng1).hints` | Each hint has `category`, `message` and `location` |

**Numerical check.** The [oracle](oracle.md) has no concrete model for axioms you wrote
yourself, so it does not decide here; it reports `UNSUPPORTED` instead of `AGREE`:

```python
from jacopy.oracle import check_equal
rep = check_equal(lhs, rhs, registry=reg, owners=(S2,), requires=res2.requires, chain=res2.chain)
print(rep.verdict, "|", rep.detail)
```

```text
UNSUPPORTED | a declared structure axiom has no F1 model
```

## Rules the engine applies automatically

`assemble_engine` adds these rules itself when it sees the relevant nodes; they appear in the
report lines. The research layer has no `prove_*` builders: it tests brackets
(`AxiomSuite`) or sets up an engine for the identity in question (`assemble_engine`).

| Rule | Mathematical counterpart |
|---|---|
| `ZeroProductDefinition` | $0\cdot x=0$, also inside operator slots (in every engine) |
| `WedgeGradedOrderDefinition` | canonical order via $\alpha\wedge\beta=(-1)^{\lvert\alpha\rvert\lvert\beta\rvert}\beta\wedge\alpha$; only in concrete degrees (when wedges are present) |
| `WedgeScalarFactorDefinition` | $(f\alpha)\wedge\beta=f\,(\alpha\wedge\beta)$ (when wedges are present) |
