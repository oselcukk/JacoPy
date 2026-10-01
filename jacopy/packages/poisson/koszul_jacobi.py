"""
The GENERAL Koszul Jacobi identity (5.E.2b closure, 2026-09-07) —
the oldest recorded deferral of the project:

    ⟨ [α,[β,γ]_π]_π + [β,[γ,α]_π]_π + [γ,[α,β]_π]_π , X ⟩ = 0

on GENERAL (non-exact) 1-forms, under the declared ``[π,π]_SN = 0``.

Mechanism (the 6.J programme completed): a GREEDY stall-time
difference-test over a rich instance-seed space, followed by an
exact ℚ-LINEAR phase (Gaussian elimination over the monomial
vectorization) for the multi-seed combinations greedy cannot reach.
Soundness: every seed is a proven/declared zero —

* ``S_br`` — pairing-Leibniz bridges
  ``⟨c,[a♯,b♯]⟩ = a♯(π(b,c)) − π(b, ℒ_{a♯}c)`` (mechanical);
* ``2NF`` — two-normal-form sharp/interior instances (the 6.B
  recipe: one node, full-engine leg vs sharp-only leg);
* ``pairD`` — the declared ``[π,π] = 0`` slices
  ``⟨c, D(a,b)⟩ = ½[π,π](a,b,c) = 0`` with X-, bracket- and
  d-pairing lifts (congruence);
* ``jac`` — cited vector-field Jacobi combinations;
* ``blift`` / ``symD`` — pairing-Leibniz and sharp-antisymmetry
  congruences —

so any rational linear combination is zero.

Evidence (audit 0B00E1B-FULL M3-3). The search only FINDS a
certificate ``Jac = Σ c_i S_i``; it is not the proof. Each seed is a
:class:`ZeroSeed` record — expression, origin, and its own ``S_i = 0``
theorem built by library producers (engine rewrites, normalization
passes, strategies), so its chain replays and its requirements (the
``[π,π] = 0`` declaration for the defect slices) are structural. The
returned chain (:func:`prove_koszul_zero_by_certificate`) cites the
reduction ``Jac = Σ c_i S_i`` — the coefficients are the claim of an
explicit step — and every seed's zero theorem; nothing in it is a
hand-built step. Honest-fail without the declaration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, List, Optional, Tuple

from jacopy.algebra.derivation import Act
from jacopy.core.expr import (
    Expr,
    Integer,
    Neg,
    Product,
    Rational,
    Sum,
)
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition, ExpansionEngine
from jacopy.proof.strategies import ProofFailure
from jacopy.proof.theorems import Theorem
from jacopy.central.objects.interior import Interior
from jacopy.central.tangent.exterior import CARTAN_TM, d
from jacopy.central.tangent.lie_bracket import (
    jacobi_combination_theorems,
    lie_bracket,
)
from jacopy.packages.poisson.core import (
    SharpEvaluationDefinition,
    SharpVF,
)
from jacopy.packages.poisson.koszul import (
    KoszulBracket,
    koszul_bracket,
)


def _node_size(x: Expr) -> int:
    if x.is_atom:
        n = 1
        slots = getattr(x, "rewritable_slots", None)
        if slots:
            for sl in slots:
                n += _node_size(sl)
        return n
    n = 1
    for c in x.children:
        n += _node_size(c)
    return n


def _rich_engine(P, registry, *, declare: bool):
    from jacopy.central.calculus import (
        ActExpansionDefinition,
        InteriorVectorLinearityDefinition,
        MultiEvalArgLinearityDefinition,
    )
    from jacopy.packages.drinfeld.twist import (
        MagicFormulaDefinition,
        PairingArgSplitDefinition,
    )
    from jacopy.packages.poisson.showcase import showcase_engine

    e = showcase_engine(
        P, registry=registry, declare_poisson=declare
    )
    e.register(MagicFormulaDefinition(registry))
    e.register(InteriorVectorLinearityDefinition(registry))
    e.register(ActExpansionDefinition(registry))
    e.register(MultiEvalArgLinearityDefinition(registry))
    e.register(PairingArgSplitDefinition())
    return e


def _normalize(engine, seed: Expr, registry) -> Expr:
    from jacopy.packages.poisson.tilde import _normalized_by

    return _normalized_by(engine, seed, registry)


def _to_vec(expr: Expr, acc=None, coeff=Fraction(1)):
    """Monomial vectorization with multilinearity bookkeeping."""
    if acc is None:
        acc = {}
    if expr == Integer(0):
        return acc
    if isinstance(expr, Sum):
        for c in expr.children:
            _to_vec(c, acc, coeff)
        return acc
    if isinstance(expr, Neg):
        return _to_vec(expr.arg, acc, -coeff)
    if isinstance(expr, Product) and expr.children:
        head = expr.children[0]
        num = None
        if isinstance(head, Integer):
            num = Fraction(int(head._repr_inner()))
        elif isinstance(head, Rational):
            num = Fraction(head._repr_inner())
        if num is not None:
            rest = expr.children[1:]
            core = (
                rest[0] if len(rest) == 1 else Product(*rest)
            )
            return _to_vec(core, acc, coeff * num)
        # Distribute a Sum/Neg factor (multilinearity of the
        # monomial reading) — collect passes fold common scalar
        # factors back into ``f·(a + b)``, which would otherwise
        # be one opaque monomial (2026-09-08, Bourbaki
        # left-Leibniz).
        for k, c in enumerate(expr.children):
            if isinstance(c, Sum):
                for t in c.children:
                    _to_vec(
                        Product(
                            *expr.children[:k],
                            t,
                            *expr.children[k + 1 :],
                        ),
                        acc,
                        coeff,
                    )
                return acc
            if isinstance(c, Neg):
                return _to_vec(
                    Product(
                        *expr.children[:k],
                        c.arg,
                        *expr.children[k + 1 :],
                    ),
                    acc,
                    -coeff,
                )
    if isinstance(expr, Pairing):
        if isinstance(expr.X, Sum):
            for t in expr.X.children:
                _to_vec(Pairing(expr.alpha, t), acc, coeff)
            return acc
        if isinstance(expr.X, Neg):
            return _to_vec(
                Pairing(expr.alpha, expr.X.arg), acc, -coeff
            )
        if isinstance(expr.alpha, Sum):
            for t in expr.alpha.children:
                _to_vec(Pairing(t, expr.X), acc, coeff)
            return acc
        if isinstance(expr.alpha, Neg):
            return _to_vec(
                Pairing(expr.alpha.arg, expr.X), acc, -coeff
            )
    if isinstance(expr, MultiEval):
        for k, sl in enumerate(expr.args):
            if isinstance(sl, (Sum, Neg)):
                if isinstance(sl, Neg):
                    new_args = (
                        expr.args[:k]
                        + (sl.arg,)
                        + expr.args[k + 1 :]
                    )
                    return _to_vec(
                        expr.with_args(*new_args), acc, -coeff
                    )
                for t in sl.children:
                    new_args = (
                        expr.args[:k]
                        + (t,)
                        + expr.args[k + 1 :]
                    )
                    _to_vec(
                        expr.with_args(*new_args), acc, coeff
                    )
                return acc
    if isinstance(expr, Act):
        if isinstance(expr.arg, Sum):
            for t in expr.arg.children:
                _to_vec(Act(expr.op, t), acc, coeff)
            return acc
        if isinstance(expr.arg, Neg):
            return _to_vec(
                Act(expr.op, expr.arg.arg), acc, -coeff
            )
    key = expr._repr_inner()
    acc[key] = acc.get(key, Fraction(0)) + coeff
    return acc


def _gauss_solve(rows, target, keys):
    m = len(rows)
    A = [
        [rows[i].get(k, Fraction(0)) for i in range(m)]
        + [target.get(k, Fraction(0))]
        for k in keys
    ]
    piv_cols = []
    r = 0
    for col in range(m):
        p = None
        for rr in range(r, len(A)):
            if A[rr][col] != 0:
                p = rr
                break
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][col]
        A[r] = [x / pv for x in A[r]]
        for rr in range(len(A)):
            if rr != r and A[rr][col] != 0:
                fac = A[rr][col]
                A[rr] = [
                    x - fac * y for x, y in zip(A[rr], A[r])
                ]
        piv_cols.append(col)
        r += 1
        if r == len(A):
            break
    for row in A:
        if all(x == 0 for x in row[:m]) and row[m] != 0:
            return None
    coeffs = [Fraction(0)] * m
    for ridx, col in enumerate(piv_cols):
        coeffs[col] = A[ridx][m]
    return coeffs


# --------------------------------------------------------------------- #
# Zero seeds: expression + origin + replayed zero theorem               #
# (audit 0B00E1B-FULL M3-3)                                              #
# --------------------------------------------------------------------- #


class _InstanceOf(Definition):
    """``rule`` restricted to ONE node: fires only on ``node`` (and only
    when ``rule`` itself matches it), rewriting as ``rule`` does.

    A seed's zero proof unfolds exactly the pairing its bridge is about
    (``⟨L_V c, W⟩`` in ``⟨c,[V,W]⟩ = V⟨c,W⟩ − ⟨L_V c, W⟩``); the full
    rule would also unfold every other ``⟨L_·(·), ·⟩`` around it. The
    restriction is a set of instances of ``rule`` — it keeps the rule's
    (effective) role, so an assumption never becomes a definition."""

    def __init__(self, rule: Definition, node: Expr) -> None:
        from jacopy.proof.expansion import effective_role

        self._rule = rule
        self._node = node
        self.anchor = type(node)
        self.role = effective_role(rule)
        self.owner = getattr(rule, "owner", None)
        self.name = f"{rule.name} — at {node._repr_inner()}"
        self.identity = ("InstanceOf", rule.key, node)

    def matches(self, expr: Expr) -> bool:
        return expr == self._node and self._rule.matches(expr)

    def rewrite(self, expr: Expr) -> Expr:
        return self._rule.rewrite(expr)


class _GenericFunction:
    """The generating set ``{f}`` of a GENERIC function (``generic-
    function`` generality): a vector field killing the generic ``f``
    kills every function, hence is zero.

    ``f`` is MINTED here, never taken from the caller: a fresh symbol
    (absent from ``avoid`` and unknown to the registry) declared
    ``Graded(0)`` only — not Scalar, not a constant — so agreement on it
    is agreement on an arbitrary function (a constant such as ``1``
    would make every vector field "vanish")."""

    def __init__(self, avoid: Expr, registry) -> None:
        from jacopy.core.expr import Symbol
        from jacopy.core.properties import Graded, Scalar

        text = avoid._repr_inner()
        k = 0
        while True:
            f = Symbol(f"𝔣{k}")
            if f._repr_inner() not in text and not any(registry.all_for(f)):
                break
            k += 1
        registry.declare(f, Graded(degree=0))
        props = list(registry.all_for(f))
        if registry.has(f, Scalar) or len(props) != 1:
            raise ProofFailure(
                f"generic function {f._repr_inner()} is not unconstrained "
                f"in this registry: {props}"
            )
        self.f = f
        self.generators = (f,)


#: Only the library's seed space mints :class:`ZeroSeed` records
#: (``_seed_records``); a certificate built from anything else is
#: refused by :func:`prove_koszul_zero_by_certificate`.
_SEED_TOKEN = object()


@dataclass(frozen=True, eq=False)
class ZeroSeed:
    """One zero instance of the search, carried as a record — not a
    bare expression (audit 0B00E1B-FULL M3-3):

    * ``expr`` — the instance ``S`` (the claim is ``S = 0``);
    * ``family`` / ``origin`` — which identity it instantiates, and why
      it vanishes;
    * ``normal_form`` — ``NF(S)`` under the search engine (the vector
      the greedy / ℚ-linear phases work with);
    * :attr:`theorem` — the ``S = 0`` record, built on first use by
      library producers (engine rewrites, normalization passes,
      strategies) so its chain replays; its :attr:`requires` carry
      every declared axiom the zero depends on (the ``[π,π] = 0``
      declaration for the defect slices) transitively.
    """

    family: str
    expr: Expr
    normal_form: Expr
    origin: str
    _prover: Callable[[], Theorem] = field(repr=False)
    _token: object = field(default=None, repr=False)
    _cache: dict = field(init=False, default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self._token is not _SEED_TOKEN:
            raise TypeError(
                "ZeroSeed records are minted by the library's seed space "
                "only (koszul_jacobi_certificate)"
            )

    @property
    def theorem(self) -> Theorem:
        if "t" not in self._cache:
            self._cache["t"] = self._prover()
        return self._cache["t"]

    @property
    def proof(self) -> ProofChain:
        return self.theorem.proof

    @property
    def requires(self):
        return self.theorem.requires


@dataclass(frozen=True)
class KoszulJacobiCertificate:
    """The witness of the search: ``target = Σ c_i S_i`` with every
    ``S_i = 0`` a :class:`ZeroSeed`. The coefficients ARE the
    certificate — :func:`prove_koszul_zero_by_certificate` checks it
    and turns it into a replayable chain."""

    terms: Tuple[Tuple[Fraction, ZeroSeed], ...]

    def combination(self) -> Expr:
        """``Σ c_i S_i`` with the seeds unnormalized (each ``S_i`` stays
        a subterm, so its zero theorem can be cited in place)."""
        if not self.terms:
            return Integer(0)
        return Sum(*(_times(c, s.expr) for c, s in self.terms))


def _times(c: Fraction, e: Expr) -> Expr:
    if c == 1:
        return e
    if c == -1:
        return Neg(e)
    n_, d_ = c.numerator, c.denominator
    base = e if n_ > 0 else Neg(e)
    ce = Integer(abs(n_)) if d_ == 1 else Rational(abs(n_), d_)
    return Product(ce, base)


def _theorem(name, lhs, rhs, engine, registry, *, max_steps=20000) -> Theorem:
    """``lhs = rhs`` by :class:`ExpandAndSimplify` over ``engine`` (a
    library producer: the chain is minted and replays in the
    ``lhs − rhs → 0`` form), with its requirements derived."""
    from jacopy.proof.strategies import ExpandAndSimplify

    chain = ExpandAndSimplify().prove(
        lhs, rhs, registry=registry, engine=engine, max_steps=max_steps
    )
    return Theorem(
        name=name,
        statement=f"{lhs._repr_inner()[:200]} = {rhs._repr_inner()[:200]}",
        lhs=lhs,
        rhs=rhs,
        proof=chain,
    ).with_structural_requires()


def _declared_rules(engine):
    """The engine's ``[π,π] = 0`` declaration rules (owned by the
    declared structure): citations of declared zeros check them."""
    from jacopy.packages.poisson.core import PoissonSNDeclaration

    return [r for r in engine.definitions if isinstance(r, PoissonSNDeclaration)]


def _cite_engine(theorems, declared, *, reverse=(), extra=()):
    """An engine citing ``theorems`` (indices in ``reverse`` read
    right-to-left), with ``extra`` rules, the declaration rules the
    citations require and slot-zero linearity."""
    from jacopy.central.calculus.bracket_calculus import SlotZeroDefinition
    from jacopy.proof.theorems import TheoremDefinition

    rules = [
        TheoremDefinition(t, reverse=(i in reverse))
        for i, t in enumerate(theorems)
    ]
    return ExpansionEngine(
        rules + list(extra) + list(declared) + [SlotZeroDefinition()]
    )


class _SeedProvers:
    """The zero theorems of the seed families, memoized per run.

    Every family vanishes by one named reason, proved mechanically:

    * ``Sbr`` — ``⟨c,[a♯,b♯]⟩ − a♯π(b,c) + π(b, L_{a♯}c)``: the
      sharp evaluation ``⟨θ, ♯b⟩ = π(b,θ)`` read backwards (a lemma by
      :class:`SharpEvaluationDefinition`) and the intrinsic ``L`` on
      1-forms, ``⟨L_V c, W⟩ = V⟨c,W⟩ − ⟨c,[V,W]⟩`` (definition);
    * ``pairD(θ)`` — ``⟨θ, D(a,b)⟩`` with ``D = [a♯,b♯] − ♯[a,b]_π``:
      the lemma ``⟨θ,D⟩ = Sbr(a,b,θ) + ½[π,π](a,b,θ)`` (sharp
      evaluation, pairing linearity, the general SN evaluation), then
      ``Sbr = 0`` and the DECLARED ``[π,π]_SN = 0``;
    * ``brD`` — ``⟨c,[X,D]⟩ = X⟨c,D⟩ − ⟨L_X c, D⟩`` (intrinsic ``L``),
      two ``pairD`` zeros; ``dpairD`` is ``pairD(d⟨c,X⟩)``;
    * ``2NF`` — two normal forms of one node (both normalization
      chains, read backwards);
    * ``jac`` — the vector-field Jacobi combination, zero by agreement
      on the generic function; ``pjac`` pairs it;
    * ``symD`` — ``π(a,b) + π(b,a) = 0`` inside a sharp slot
      (alternation);
    * ``Xblift`` — the intrinsic ``L`` on 1-forms;
    * ``X…`` — ``X(S) = 0`` from ``S = 0``.
    """

    def __init__(self, P, search_engine, registry) -> None:
        from jacopy.central.calculus.bracket_calculus import (
            IntrinsicLDefinition,
        )

        self._P = P
        self._engine = search_engine
        self._registry = registry
        self._memo: dict = {}
        self._il = IntrinsicLDefinition(CARTAN_TM, registry)
        self._declared = _declared_rules(search_engine)

    # -- helpers ------------------------------------------------------- #

    def _memoized(self, key, build):
        if key not in self._memo:
            self._memo[key] = build()
        return self._memo[key]

    def _cite(self, *theorems, reverse=(), extra=()):
        return _cite_engine(
            theorems, self._declared, reverse=reverse, extra=extra
        )

    def _sharp(self, a):
        return SharpVF(self._P.pi, a)

    def _pp(self, x, y):
        return MultiEval(
            self._P.pi, x, y, alternating=True, slot_kind="covector"
        )

    def _L(self, V, x):
        return Act(CARTAN_TM.lie(V), x)

    def defect(self, a, b):
        return Sum(
            lie_bracket(self._sharp(a), self._sharp(b)),
            Neg(self._sharp(koszul_bracket(self._P, a, b))),
        )

    def sbr(self, a, b, c):
        return Sum(
            Pairing(c, lie_bracket(self._sharp(a), self._sharp(b))),
            Neg(Act(self._sharp(a), self._pp(b, c))),
            self._pp(b, self._L(self._sharp(a), c)),
        )

    # -- families ------------------------------------------------------ #

    def zero_sbr(self, a, b, c) -> Theorem:
        def build():
            reg = self._registry
            V, W = self._sharp(a), self._sharp(b)
            pre = Sum(
                Pairing(c, lie_bracket(V, W)),
                Neg(Act(V, Pairing(c, W))),
                Pairing(self._L(V, c), W),
            )
            target = self.sbr(a, b, c)
            unfold = _theorem(
                "koszul seed Sbr: sharp evaluation",
                pre, target,
                ExpansionEngine([SharpEvaluationDefinition(self._P)]),
                reg,
            )
            return _theorem(
                f"koszul seed Sbr({a._repr_inner()},{b._repr_inner()},"
                f"{c._repr_inner()}) = 0",
                target, Integer(0),
                self._cite(
                    unfold,
                    reverse=(0,),
                    extra=[_InstanceOf(self._il, Pairing(self._L(V, c), W))],
                ),
                reg,
            )

        return self._memoized(("Sbr", a, b, c), build)

    def zero_pair_defect(self, theta, a, b) -> Theorem:
        def build():
            from jacopy.central.tangent.schouten import sn_bracket
            from jacopy.packages.poisson.showcase import (
                SharpPairingLinearityDefinition,
                SNBivectorGeneralEvalDefinition,
            )

            reg = self._registry
            P = self._P
            lhs = Pairing(theta, self.defect(a, b))
            sn = MultiEval(
                sn_bracket(P.pi, P.pi), a, b, theta,
                alternating=True, slot_kind="covector",
            )
            lemma = _theorem(
                "koszul seed pairD: ⟨θ,D(a,b)⟩ = Sbr(a,b,θ) + ½[π,π](a,b,θ)",
                lhs,
                Sum(self.sbr(a, b, theta), Product(Rational(1, 2), sn)),
                ExpansionEngine([
                    SNBivectorGeneralEvalDefinition(P),
                    SharpEvaluationDefinition(P),
                    SharpPairingLinearityDefinition(P, reg),
                ]),
                reg,
            )
            return _theorem(
                f"koszul seed pairD ⟨{theta._repr_inner()}, "
                f"D({a._repr_inner()},{b._repr_inner()})⟩ = 0",
                lhs, Integer(0),
                self._cite(lemma, self.zero_sbr(a, b, theta)),
                reg,
            )

        return self._memoized(("pairD", theta, a, b), build)

    def zero_bracket_defect(self, c, a, b, X) -> Theorem:
        def build():
            reg = self._registry
            Dv = self.defect(a, b)
            lhs = Pairing(c, lie_bracket(X, Dv))
            Lc = self._L(X, c)
            lemma = _theorem(
                "koszul seed brD: ⟨c,[X,D]⟩ = X⟨c,D⟩ − ⟨L_X c, D⟩",
                lhs,
                Sum(Act(X, Pairing(c, Dv)), Neg(Pairing(Lc, Dv))),
                ExpansionEngine([_InstanceOf(self._il, Pairing(Lc, Dv))]),
                reg,
            )
            return _theorem(
                f"koszul seed brD ⟨{c._repr_inner()}, [X, D]⟩ = 0",
                lhs, Integer(0),
                self._cite(
                    lemma,
                    self.zero_pair_defect(c, a, b),
                    self.zero_pair_defect(Lc, a, b),
                ),
                reg,
            )

        return self._memoized(("brD", c, a, b, X), build)

    def zero_two_nf(self, node, sharp_only) -> Tuple[Expr, Callable]:
        """``(n_sharp − n_full, prover)`` for one node: both normal
        forms are recorded once; the zero theorem is built by the
        (memoized) prover only for a 2NF seed a certificate uses. A
        normalization budget overrun is a :class:`ProofFailure`."""
        from jacopy.packages.poisson.tilde import _normal_form

        reg = self._registry
        try:
            # recorded ONCE: the search uses the normal forms, the
            # (lazy) prover the chains
            nf_full = _normal_form(self._engine, node, reg, record=True)
            nf_sharp = _normal_form(sharp_only, node, reg, record=True)
        except RuntimeError as exc:
            raise ProofFailure(f"koszul seed 2NF: {exc}")
        expr = Sum(nf_sharp.expr, Neg(nf_full.expr))

        def nf_theorem(nf, label):
            return Theorem(
                name=f"koszul seed 2NF: {label} normal form",
                statement=f"{node._repr_inner()[:200]} = {nf.expr._repr_inner()[:200]}",
                lhs=node, rhs=nf.expr, proof=ProofChain(nf.chain),
            ).with_structural_requires()

        def build():
            full = nf_theorem(nf_full, "full-engine")
            sharp = nf_theorem(nf_sharp, "sharp-only")
            return _theorem(
                "koszul seed 2NF = 0", expr, Integer(0),
                self._cite(sharp, full, reverse=(0, 1)), reg,
            )

        return expr, (lambda: self._memoized(("2NF", expr), build))

    def zero_vf_jacobi(self, J) -> Theorem:
        """``J = 0`` for a vector-field combination, by agreement on a
        FRESH generic function (:class:`_GenericFunction`)."""
        def build():
            from jacopy.central.tangent.engine import tangent_engine
            from jacopy.core.registry import PropertyRegistry
            from jacopy.proof.strategies import AgreementOnGenerators

            reg = self._registry
            if reg is None:
                reg = PropertyRegistry()
            # the generic function lives only inside this proof: its
            # declaration is rolled back (the caller's registry keeps
            # its fingerprint, also when the proof fails)
            with reg.scope():
                chain = AgreementOnGenerators(_GenericFunction(J, reg)).prove(
                    J, Integer(0), registry=reg,
                    engine=tangent_engine(registry=reg),
                )
                return Theorem(
                    name="koszul seed jac: vector-field Jacobi combination = 0",
                    statement=f"{J._repr_inner()[:200]} = 0",
                    lhs=J, rhs=Integer(0), proof=chain,
                ).with_structural_requires()

        return self._memoized(("jac", J), build)

    def zero_sym(self, expr) -> Theorem:
        def build():
            from jacopy.packages.generalized.dialect_bridge import (
                PoissonSharpSlotAlternatingNormalizeDefinition,
            )

            reg = self._registry
            eng = _rich_engine(self._P, reg, declare=False)
            eng.register(PoissonSharpSlotAlternatingNormalizeDefinition(reg))
            return _theorem(
                "koszul seed symD: π(a,b) + π(b,a) = 0 in a sharp slot",
                expr, Integer(0), eng, reg,
            )

        return self._memoized(("sym", expr), build)

    def zero_blift(self, expr, X, a, V) -> Theorem:
        return _theorem(
            "koszul seed Xblift: ⟨a,[X,V]⟩ − X⟨a,V⟩ + ⟨L_X a, V⟩ = 0",
            expr, Integer(0),
            ExpansionEngine([_InstanceOf(self._il, Pairing(self._L(X, a), V))]),
            self._registry,
        )

    def zero_act(self, X, inner: Theorem, label: str) -> Theorem:
        expr = Act(X, inner.lhs)
        return self._memoized(("X", X, inner.lhs), lambda: _theorem(
            f"koszul seed X{label}: X(S) = 0", expr, Integer(0),
            self._cite(inner), self._registry,
        ))

    def zero_pair(self, c, inner: Theorem, label: str) -> Theorem:
        expr = Pairing(c, inner.lhs)
        return self._memoized(("p", c, inner.lhs), lambda: _theorem(
            f"koszul seed p{label}: ⟨c, V⟩ = 0", expr, Integer(0),
            self._cite(inner), self._registry,
        ))


def _seed_records(
    P, engine, alpha, beta, gamma, X, f, registry
) -> Tuple[List[Tuple[int, ZeroSeed, Expr]], "_SeedProvers"]:
    """The seed space as :class:`ZeroSeed` records, and the search
    vectors ``(sign, seed, NF(sign·S))`` (both signs, deduplicated by
    normal form; zero normal forms are dropped)."""
    pv = _SeedProvers(P, engine, registry)
    sharp = pv._sharp
    trip = (alpha, beta, gamma)
    pairs = [(a, b) for a in trip for b in trip if a is not b]
    sharp_only = ExpansionEngine([SharpEvaluationDefinition(P)])
    raw: List[Tuple[str, Expr, str, Callable]] = []

    def add(family, expr, origin, prover):
        raw.append((family, expr, origin, prover))

    for a in trip:
        for b in trip:
            if a is b:
                continue
            for c in trip:
                sbr = pv.sbr(a, b, c)
                z = (lambda a=a, b=b, c=c: pv.zero_sbr(a, b, c))
                add("Sbr", sbr, "pairing-Leibniz bridge (intrinsic L, sharp evaluation)", z)
                add("XSbr", Act(X, sbr), "X applied to the Sbr bridge",
                    lambda z=z: pv.zero_act(X, z(), "Sbr"))
    for a in trip:
        for (b, c) in pairs:
            node = Pairing(Act(Interior(sharp(c)), d(a)), sharp(b))
            two_nf, z = pv.zero_two_nf(node, sharp_only)
            add("2NF", two_nf, "two normal forms of one node", z)
            add("X2NF", Act(X, two_nf), "X applied to a 2NF zero",
                lambda z=z: pv.zero_act(X, z(), "2NF"))
    for (a, b) in pairs:
        Dv = pv.defect(a, b)
        for cc in trip:
            origin = "anchor-defect slice ⟨θ,D(a,b)⟩ = ½[π,π](a,b,θ), declared [π,π] = 0"
            zp = (lambda cc=cc, a=a, b=b: pv.zero_pair_defect(cc, a, b))
            add("pairD", Pairing(cc, Dv), origin, zp)
            add("XpairD", Act(X, Pairing(cc, Dv)), origin + " (X-lift)",
                lambda zp=zp: pv.zero_act(X, zp(), "pairD"))
            add("brD", Pairing(cc, lie_bracket(X, Dv)), origin + " (bracket lift)",
                lambda cc=cc, a=a, b=b: pv.zero_bracket_defect(cc, a, b, X))
            th = d(Pairing(cc, X))
            add("dpairD", Pairing(th, Dv), origin + " (d-pairing lift)",
                lambda th=th, a=a, b=b: pv.zero_pair_defect(th, a, b))
    for a in trip:
        for b in trip:
            V = sharp(b)
            xb = Sum(
                Pairing(a, lie_bracket(X, V)),
                Neg(Act(X, Pairing(a, V))),
                Pairing(pv._L(X, a), V),
            )
            add("Xblift", xb, "pairing-Leibniz congruence (intrinsic L)",
                lambda xb=xb, a=a, V=V: pv.zero_blift(xb, X, a, V))
    for (a, b) in pairs:
        for t in jacobi_combination_theorems(
            X, sharp(a), sharp(b), f, registry=registry
        ):
            # only the normalized combination is taken from the
            # tangent record; its zero is re-proved here (agreement on
            # the generic function, a library strategy)
            J = t.lhs
            zj = (lambda J=J: pv.zero_vf_jacobi(J))
            add("jac", J, "vector-field Jacobi (agreement on the generic function)", zj)
            for cc in trip:
                add("pjac", Pairing(cc, J), "paired vector-field Jacobi",
                    lambda cc=cc, zj=zj: pv.zero_pair(cc, zj(), "jac"))
    for (a, b) in pairs:
        ssym = Sum(sharp(d(pv._pp(a, b))), sharp(d(pv._pp(b, a))))
        for cc in trip:
            e1 = Pairing(cc, lie_bracket(X, ssym))
            e2 = Pairing(cc, ssym)
            add("symD", e1, "alternation of π in a sharp slot", lambda e1=e1: pv.zero_sym(e1))
            add("symD2", e2, "alternation of π in a sharp slot", lambda e2=e2: pv.zero_sym(e2))
    out: List[Tuple[int, ZeroSeed, Expr]] = []
    seen = set()
    for family, expr, origin, prover in raw:
        nfs = {
            1: _normalize(engine, expr, registry),
            -1: _normalize(engine, Neg(expr), registry),
        }
        seed = None
        for sign, nf in nfs.items():
            if nf == Integer(0):
                continue
            k = nf._repr_inner()
            if k in seen:
                continue
            seen.add(k)
            if seed is None:
                seed = ZeroSeed(
                    family=family, expr=expr, normal_form=nfs[1],
                    origin=origin, _prover=prover, _token=_SEED_TOKEN,
                )
            out.append((sign, seed, nf))
    return out, pv


def _koszul_jacobiator(P, alpha, beta, gamma, X) -> Expr:
    pi = P.pi
    return Sum(*(
        Pairing(KoszulBracket(pi, a, KoszulBracket(pi, b, c)), X)
        for a, b, c in (
            (alpha, beta, gamma), (beta, gamma, alpha), (gamma, alpha, beta)
        )
    ))


def koszul_jacobi_certificate(
    P,
    alpha: Expr,
    beta: Expr,
    gamma: Expr,
    X: Expr,
    f: Expr,
    *,
    target: Optional[Expr] = None,
    registry: Optional[PropertyRegistry] = None,
    max_rounds: int = 40,
) -> KoszulJacobiCertificate:
    """SEARCH for a certificate ``target = Σ c_i S_i`` (default target:
    the paired Koszul Jacobiator) — greedy stall-difference over the
    seed space, then an exact ℚ-linear phase. The search only FINDS the
    coefficients; nothing it computes is evidence —
    :func:`prove_koszul_zero_by_certificate` checks them.
    :class:`ProofFailure` when no certificate is found."""
    if target is None:
        target = _koszul_jacobiator(P, alpha, beta, gamma, X)
    engine = _rich_engine(P, registry, declare=True)
    vectors, _ = _seed_records(
        P, engine, alpha, beta, gamma, X, f, registry
    )
    coeff: dict = {}

    def credit(seed, c):
        coeff[seed] = coeff.get(seed, Fraction(0)) + c

    residual = _normalize(engine, target, registry)
    for _ in range(max_rounds):
        if residual == Integer(0):
            break
        progressed = False
        for sign, seed, lhs in vectors:
            cand = _normalize(engine, Sum(residual, Neg(lhs)), registry)
            if _node_size(cand) < _node_size(residual):
                credit(seed, Fraction(sign))
                residual = cand
                progressed = True
                break
        if not progressed:
            break
    if residual != Integer(0):
        # ℚ-LINEAR phase.
        tvec = _to_vec(residual)
        rows = [_to_vec(lhs) for _, _, lhs in vectors]
        keys = sorted(set(tvec) | {k for row in rows for k in row})
        coeffs = _gauss_solve(rows, tvec, keys)
        if coeffs is None:
            raise ProofFailure(
                "Koszul certificate search: residual survives — "
                f"{residual._repr_inner()[:140]}"
            )
        for (sign, seed, _), c in zip(vectors, coeffs):
            if c != 0:
                credit(seed, c * sign)
    terms = tuple((c, s) for s, c in coeff.items() if c != 0)
    return KoszulJacobiCertificate(terms)


def _checked_zero(seed) -> Theorem:
    """The seed's zero theorem, checked: a library-minted record whose
    theorem proves EXACTLY ``seed.expr = 0`` with a replayed chain."""
    if type(seed) is not ZeroSeed or seed._token is not _SEED_TOKEN:
        raise ProofFailure("certificate term is not a library ZeroSeed record")
    t = seed.theorem
    if type(t) is not Theorem:
        raise ProofFailure(f"seed {seed.family}: its zero is not a Theorem record")
    if t.lhs != seed.expr or t.rhs != Integer(0):
        raise ProofFailure(
            f"seed {seed.family}: its theorem proves "
            f"{t.lhs._repr_inner()[:80]} = {t.rhs._repr_inner()[:40]}, not "
            f"{seed.expr._repr_inner()[:80]} = 0"
        )
    if not t.chain_replayed or t.legacy:
        raise ProofFailure(
            f"seed {seed.family}: its zero theorem is not a replayed record "
            f"({'; '.join(t.unreplayed_reasons() or t.unverified_reasons())[:160]})"
        )
    return t


def prove_koszul_zero_by_certificate(
    P,
    target: Expr,
    certificate: KoszulJacobiCertificate,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 20000,
) -> ProofChain:
    """``target = 0`` from a certificate, as a chain of LIBRARY steps:

    1. the reduction ``target = Σ c_i S_i`` — :class:`ExpandAndSimplify`
       over the search engine (the coefficients appear in the claim:
       the witness is an explicit step, not a comment), cited ONCE at
       the root (``target → Σ c_i S_i``; skipped when the combination
       is the target itself);
    2. ``Σ c_i S_i → Σ c_i·0 → 0`` — every seed's zero theorem cited
       by the engine, then simplification
       (:func:`~jacopy.proof.result.prove`).

    Every seed must be a library-minted :class:`ZeroSeed` whose theorem
    proves exactly ``S_i = 0`` with a replayed chain; the result's
    requirements carry each seed's (the declared ``[π,π] = 0`` for the
    defect slices). :class:`ProofFailure` otherwise, or when the
    certificate does not reduce ``target``."""
    from jacopy.oracle.hook import on_closed
    from jacopy.proof.registry_facts import registry_context
    from jacopy.proof.result import Goal, ProofResult, prove

    if type(certificate) is not KoszulJacobiCertificate:
        raise ProofFailure("not a KoszulJacobiCertificate")
    engine = _rich_engine(P, registry, declare=True)
    declared = _declared_rules(engine)
    zeros = []
    seen = set()
    for c, seed in certificate.terms:
        if not isinstance(c, Fraction) or c == 0:
            raise ProofFailure(f"certificate coefficient {c!r} is not a nonzero rational")
        if id(seed) not in seen:
            seen.add(id(seed))
            zeros.append(_checked_zero(seed))
    combination = certificate.combination()
    steps = []
    if combination != target:
        reduction = _theorem(
            "Koszul Jacobi reduction to the certificate",
            target, combination, engine, registry, max_steps=max_steps,
        )
        once = _cite_engine((reduction,), declared)
        with registry_context(registry):
            after, step = once.expand_once(target)
        if step is None or after != combination or step.before != target:
            raise ProofFailure(
                "Koszul certificate: the reduction is not citable at the root"
                + ("; " + "; ".join(once.assembly_report[:3]) if once.assembly_report else "")
            )
        steps.append(step)
    final = _cite_engine(zeros, declared)
    result = prove(
        final, combination, Integer(0), registry=registry, max_steps=max_steps
    )
    if not result.closed:
        raise ProofFailure(
            "Koszul certificate: the cited zeros leave "
            f"{getattr(result.residual, '_repr_inner', lambda: '?')()[:140]}"
            + ("; " + "; ".join(final.assembly_report[:3]) if final.assembly_report else "")
        )
    chain = ProofChain(steps + list(result.chain.steps))
    whole = ProofResult.from_chain(chain, Goal(target, Integer(0)))
    if not whole.closed:  # pragma: no cover - the two legs compose
        raise ProofFailure("Koszul certificate: the chain does not close")
    on_closed(target, Integer(0), registry=registry, source="prove_koszul_zero_by_certificate",
              engine=final, requires=whole.requires, chain=chain)
    return chain


def prove_general_koszul_jacobi(
    P,
    alpha: Expr,
    beta: Expr,
    gamma: Expr,
    X: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    declare_poisson: bool = True,
    max_rounds: int = 40,
) -> ProofChain:
    """THE 5.E.2b theorem: the Koszul bracket satisfies the Jacobi
    identity on GENERAL 1-forms, paired against the probe ``X``,
    under the declared ``[π,π]_SN = 0``.

    The certificate search (:func:`koszul_jacobi_certificate`) finds
    ``Jac = Σ c_i S_i`` over zero seeds; the returned chain
    (:func:`prove_koszul_zero_by_certificate`) runs ``Jac → 0``
    through cited, replayed records only — the reduction with its
    coefficients and every seed's zero theorem — so the result names
    the ``[π,π] = 0`` declaration among its requirements.

    Without the declaration the defect slices are not zero and no
    certificate exists; the search is not run (honest fail)."""
    jac = _koszul_jacobiator(P, alpha, beta, gamma, X)
    if not declare_poisson:
        engine = _rich_engine(P, registry, declare=False)
        residual = _normalize(engine, jac, registry)
        raise ProofFailure(
            "general Koszul Jacobi needs the declared [π,π] = 0; "
            f"residual: {residual._repr_inner()[:120]}"
        )
    cert = koszul_jacobi_certificate(
        P, alpha, beta, gamma, X, f, target=jac,
        registry=registry, max_rounds=max_rounds,
    )
    return prove_koszul_zero_by_certificate(
        P, jac, cert, registry=registry
    )
