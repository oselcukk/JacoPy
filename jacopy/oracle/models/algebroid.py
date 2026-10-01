"""Algebroid models (F2): ``E = R^n × R^r`` with a polynomial anchor and a
concrete ℝ-bilinear bracket, plus frames.

Every algebroid of an equation gets an :class:`EStructure` drawn from a
FAMILY (SPEC §2). The bracket of every family is an instance of

    [u,v]^c = u^a ρ_a(v^c) − λ v^b ρ_b(u^c) + C^c_ab(x) u^a v^b + S(u,v)

(``S`` collects the family's extra terms: the Dorfman ``d⟨·,·⟩``-type
terms, the second-derivative "breaker" terms), transported by a random
unipotent polynomial bundle automorphism ``A`` of ``E``
(``[u,v]' = A⁻¹[Au, Av]``, ``ρ' = ρA``, ``g' = Aᵀ g A``) so that anchor,
structure functions and metric are all non-constant.

Families and the axioms (``central/algebroid/context.py`` DECLARATIONS)
they satisfy — the claim is SELF-CHECKED numerically when the structure
is built: every claimed axiom has zero defect on random sections, every
other algebraic axiom has a NONZERO defect (so a counter-model really
violates its target); a mismatch raises :class:`OracleSelfCheckError`.

* ``lie-tm+R``        TM ⊕ R with ``b = dθ``           RL LL AM J AS regular
* ``lie-so3``         so(3) action algebroid on R^3     RL LL AM J AS
* ``almost-lie-tm+R`` TM ⊕ R with non-closed 2-form     RL LL AM AS regular
* ``pre-leibniz-tm+R`` TM ⊕ R, generic bilinear ``b``   RL LL AM regular
* ``courant-dorfman`` TM ⊕ T*M Dorfman, dH = 0          RL LL AM J SP MI regular
* ``pre-courant-dorfman`` Dorfman, dH ≠ 0 (n ≥ 4)       RL LL AM SP MI regular
* ``almost-leibniz``  generic ρ, C, λ ≠ 1               RL LL
* ``skew-almost``     generic skew (λ = 1, C skew)      RL LL AS
* ``right-leibniz-only`` + second-derivative breaker    RL
* ``skew-only``       skew-symmetrized breaker          AS
* ``bare``            breakers in both slots            (none)

(RL right-leibniz, LL left-leibniz, AM anchor-morphism, J jacobi, AS
antisymmetric, SP symmetric-part, MI metric-invariance.)

Left Leibniz is ``[fu,v] = −ρ(v)(f)u + f[u,v] + L(Df,u,v)`` with a
C∞-trilinear locality operator ``L``: a family satisfying it carries
``L`` as an explicit tensor (``locality``), and the self-check verifies
the identity with it; a family violating it is checked to have a
defect that is NOT C∞-linear in ``u``.

Structures depend only on ``(family, n, r, pool)`` with a small pool of
seeds, so their (expensive) self-check is cached per process; the atoms
(sections, forms, functions) still depend on the per-check model seed.
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import combinations
from typing import Dict, Optional, Tuple

import sympy as sp

from jacopy.oracle import values as V
from jacopy.oracle.models.tangent import OracleSelfCheckError, TangentModel, _subseed
from jacopy.oracle.values import EFormV, FormV, Ring, SecV, Unsupported, VecV

RL, LL, AM, J, AS, SP, MI, REG = (
    "right-leibniz", "left-leibniz", "anchor-morphism", "jacobi", "antisymmetric",
    "symmetric-part", "metric-invariance", "regular",
)
#: axioms checked numerically on every structure
ALGEBRAIC = (RL, LL, AM, J, AS, SP, MI)
#: declarations the models can satisfy (``regular`` by construction)
MODELED = ALGEBRAIC + (REG,)

#: number of distinct structure seeds per (family, n, r)
POOL = 3

#: family → (claimed axioms, n_min, rank rule, carries a metric)
FAMILIES: Dict[str, Tuple[frozenset, int, object, bool]] = {
    "lie-tm+R": (frozenset({RL, LL, AM, J, AS, REG}), 2, "n+1", False),
    "lie-so3": (frozenset({RL, LL, AM, J, AS}), 3, 3, False),
    "almost-lie-tm+R": (frozenset({RL, LL, AM, AS, REG}), 3, "n+1", False),
    "pre-leibniz-tm+R": (frozenset({RL, LL, AM, REG}), 2, "n+1", False),
    "courant-dorfman": (frozenset({RL, LL, AM, J, SP, MI, REG}), 3, "2n", True),
    "pre-courant-dorfman": (frozenset({RL, LL, AM, SP, MI, REG}), 4, "2n", True),
    "almost-leibniz": (frozenset({RL, LL}), 2, "free", False),
    "skew-almost": (frozenset({RL, LL, AS}), 2, "free", False),
    "right-leibniz-only": (frozenset({RL}), 2, "free", False),
    "skew-only": (frozenset({AS}), 2, "free", False),
    "bare": (frozenset(), 2, "free", False),
}


def family_rank(family: str, n: int, need: int) -> Optional[int]:
    """The rank ``r`` of ``family`` on ``R^n`` (``None``: not available)."""
    claims, n_min, rule, _ = FAMILIES[family]
    if n < n_min:
        return None
    if rule == "n+1":
        return n + 1
    if rule == "2n":
        return 2 * n
    if rule == "free":
        return max(3, need)
    return rule


# --------------------------------------------------------------------- #
# The structure                                                          #
# --------------------------------------------------------------------- #


class EStructure:
    """``(E = R^n × R^r, ρ, [·,·], g?, L?)`` with verified axioms."""

    def __init__(self, family: str, label: str, R: Ring, rho, br, *, G=None, Ginv=None, loc=None,
                 regular: bool = False) -> None:
        self.family = family
        self.label = label
        self.R = R
        self.n = R.n
        self.rho = tuple(tuple(c) for c in rho)  # r columns, each an n-tuple
        self.r = len(self.rho)
        self._br = br
        self.G = G
        self.Ginv = Ginv
        self._loc = loc
        self.regular = regular
        self.satisfied: frozenset = frozenset()
        self.violated: frozenset = frozenset()

    # ---- structure maps ------------------------------------------------ #

    def anchor(self, u) -> Tuple[sp.Poly, ...]:
        """``ρ(u) = u^a ρ_a`` (C∞-linear by definition)."""
        R = self.R
        out = [R.zero()] * self.n
        for a, ua in enumerate(u):
            if ua.is_zero:
                continue
            for i in range(self.n):
                if not self.rho[a][i].is_zero:
                    out[i] = out[i] + ua * self.rho[a][i]
        return tuple(out)

    def act(self, u, f) -> sp.Poly:
        return V.vf_apply(self.R, self.anchor(u), f)

    def bracket(self, u, v) -> Tuple[sp.Poly, ...]:
        return tuple(self._br(tuple(u), tuple(v)))

    def D(self, f) -> Tuple[sp.Poly, ...]:
        """Components of the coboundary ``Df``: ``(Df)_a = ρ_a(f)``."""
        return tuple(V.vf_apply(self.R, self.rho[a], f) for a in range(self.r))

    @property
    def has_metric(self) -> bool:
        return self.G is not None

    def metric(self, u, v) -> sp.Poly:
        if self.G is None:
            raise Unsupported("EMetric[no fibre metric in this model]")
        R = self.R
        out = R.zero()
        for a in range(self.r):
            if u[a].is_zero:
                continue
            for b in range(self.r):
                if not self.G[a][b].is_zero and not v[b].is_zero:
                    out = out + u[a] * self.G[a][b] * v[b]
        return out

    def sharp(self, om) -> Tuple[sp.Poly, ...]:
        """``g⁻¹(ω)``: the section ``w`` with ``g(w, ·) = ω``."""
        if self.Ginv is None:
            raise Unsupported("MetricSharp[no fibre metric in this model]")
        R = self.R
        return tuple(sum((self.Ginv[a][b] * om[b] for b in range(self.r)), R.zero()) for a in range(self.r))

    @property
    def has_locality(self) -> bool:
        return self._loc is not None

    def locality(self, om, u, v) -> Tuple[sp.Poly, ...]:
        if self._loc is None:
            raise Unsupported("LocalityOperator[left-leibniz fails in this model]")
        return tuple(self._loc(tuple(om), tuple(u), tuple(v)))


# --------------------------------------------------------------------- #
# Random building blocks                                                 #
# --------------------------------------------------------------------- #


def _poly(gen: TangentModel, rng, degree: int):
    return gen._poly(rng, degree)


def _sparse_poly(gen: TangentModel, rng, degree: int, p_zero: float = 0.4):
    if rng.random() < p_zero:
        return gen.R.zero()
    return gen._poly(rng, degree)


def _unipotent(gen: TangentModel, rng, r: int):
    """``A = I + N`` with ``N`` strictly upper triangular, ``N² = 0``
    (two entries of degree ≤ 2), so ``A⁻¹ = I − N`` exactly."""
    R = gen.R
    pairs = [(i, j) for i in range(r) for j in range(i + 1, r)]
    rng.shuffle(pairs)
    chosen = []
    for i, j in pairs:
        if all(j != i2 and i != j2 for i2, j2 in chosen):
            chosen.append((i, j))
        if len(chosen) == 2:
            break
    N = [[R.zero()] * r for _ in range(r)]
    for i, j in chosen:
        N[i][j] = gen._poly(rng, 1)
    A = [[(R.one() if i == j else R.zero()) + N[i][j] for j in range(r)] for i in range(r)]
    Ainv = [[(R.one() if i == j else R.zero()) - N[i][j] for j in range(r)] for i in range(r)]
    return A, Ainv


def _matvec(M, u, R):
    return tuple(sum((M[i][j] * u[j] for j in range(len(u)) if not M[i][j].is_zero and not u[j].is_zero), R.zero())
                 for i in range(len(M)))


def _transpose(M):
    return [list(row) for row in zip(*M)]


def _transport(base: EStructure, A, Ainv) -> EStructure:
    """The isomorphic structure ``u ↦ Au`` (see module docstring)."""
    R = base.R
    AinvT = _transpose(Ainv)

    def br(u, v):
        return _matvec(Ainv, base.bracket(_matvec(A, u, R), _matvec(A, v, R)), R)

    rho = []
    for a in range(base.r):
        col = tuple(A[b][a] for b in range(base.r))
        rho.append(base.anchor(col))
    G = Ginv = None
    if base.G is not None:
        AT = _transpose(A)
        G = [[sum((AT[i][k] * base.G[k][l] * A[l][j] for k in range(base.r) for l in range(base.r)), R.zero())
              for j in range(base.r)] for i in range(base.r)]
        Ginv = [[sum((Ainv[i][k] * base.Ginv[k][l] * AinvT[l][j] for k in range(base.r) for l in range(base.r)),
                     R.zero()) for j in range(base.r)] for i in range(base.r)]
    loc = None
    if base.has_locality:
        def loc(om, u, v):
            om0 = _matvec(AinvT, om, R)
            return _matvec(Ainv, base.locality(om0, _matvec(A, u, R), _matvec(A, v, R)), R)
    return EStructure(base.family, base.label + " transported", R, rho, br, G=G, Ginv=Ginv, loc=loc,
                      regular=base.regular)


# --------------------------------------------------------------------- #
# Base families                                                          #
# --------------------------------------------------------------------- #


def _tm_plus_r(gen, rng, family: str) -> EStructure:
    """``E = TM ⊕ R``, ``ρ(X, f) = X``,
    ``[(X,f),(Y,g)] = ([X,Y], X(g) − Y(f) + b(X,Y))``: Lie iff ``b`` is a
    closed 2-form, almost-Lie for a non-closed 2-form, a non-skew
    pre-Leibniz algebroid for a generic bilinear ``b``."""
    R, n = gen.R, gen.n
    if family == "lie-tm+R":
        theta = [gen._poly(rng, 3) for _ in range(n)]
        B = [[R.diff(theta[j], i) - R.diff(theta[i], j) for j in range(n)] for i in range(n)]
    elif family == "almost-lie-tm+R":
        B = [[R.zero()] * n for _ in range(n)]
        for i, j in combinations(range(n), 2):
            c = gen._poly(rng, 2)
            B[i][j], B[j][i] = c, -c
    else:
        B = [[gen._poly(rng, 2) for _ in range(n)] for _ in range(n)]

    def br(u, v):
        X, f, Y, g = u[:n], u[n], v[:n], v[n]
        s = V.vf_apply(R, X, g) - V.vf_apply(R, Y, f)
        for i in range(n):
            if X[i].is_zero:
                continue
            for j in range(n):
                if not B[i][j].is_zero and not Y[j].is_zero:
                    s = s + X[i] * B[i][j] * Y[j]
        return V.vf_bracket(R, X, Y) + (s,)

    rho = [V.basis(R, a) for a in range(n)] + [tuple(R.zero() for _ in range(n))]
    zero = tuple(R.zero() for _ in range(n + 1))
    return EStructure(family, family, R, rho, br, loc=lambda om, u, v: zero, regular=True)


def _so3(gen, rng, family: str) -> EStructure:
    """The action algebroid of so(3) rotating ``(x0, x1, x2)``:
    ``[u,v]^c = ρ(u)(v^c) − ρ(v)(u^c) + c^c_ab u^a v^b`` with
    ``[ρ_a, ρ_b] = c^c_ab ρ_c`` (anchor not of constant rank)."""
    R, n = gen.R, gen.n
    x = [R.var(i) for i in range(3)]
    eps = {(0, 1, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1, (0, 2, 1): -1, (2, 1, 0): -1, (1, 0, 2): -1}
    rho = []
    for a in range(3):
        comp = [R.zero()] * n
        for (i, j, k), s in eps.items():
            if i == a:
                comp[k] = comp[k] + (x[j] if s > 0 else -x[j])
        rho.append(tuple(comp))
    # structure constants from [ρ_a, ρ_b] = s ε_abc ρ_c
    br01 = V.vf_bracket(R, rho[0], rho[1])
    s = 1 if all((br01[i] - rho[2][i]).is_zero for i in range(n)) else -1
    C = {}
    for (a, b, c), e in eps.items():
        C[(c, a, b)] = s * e

    def br(u, v):
        out = []
        ru, rv = None, None
        for c in range(3):
            val = V.vf_apply(R, _anchor(rho, u, R), v[c]) - V.vf_apply(R, _anchor(rho, v, R), u[c])
            for (cc, a, b), k in C.items():
                if cc == c:
                    val = val + R.const(k) * u[a] * v[b]
            out.append(val)
        return tuple(out)

    zero = tuple(R.zero() for _ in range(3))
    return EStructure(family, family, R, rho, br, loc=lambda om, u, v: zero, regular=False)


def _anchor(rho, u, R):
    n = len(rho[0])
    out = [R.zero()] * n
    for a, ua in enumerate(u):
        if ua.is_zero:
            continue
        for i in range(n):
            if not rho[a][i].is_zero:
                out[i] = out[i] + ua * rho[a][i]
    return tuple(out)


def _dorfman(gen, rng, family: str) -> EStructure:
    """``E = TM ⊕ T*M``, ``ρ(X, ξ) = X``, ``g = ½(ξ(Y) + η(X))``, the
    H-twisted Dorfman bracket
    ``[X+ξ, Y+η] = [X,Y] + L_Xη − ι_Y dξ + ι_Y ι_X H``: a Courant
    algebroid for ``dH = 0``, pre-Courant otherwise. The locality tensor
    is ``L(ω,u,v) = g(u,v)·g⁻¹(ω)`` ([fu,v] − f[u,v] + ρ(v)(f)u =
    2g(u,v)(0, df) and g⁻¹(Df) = (0, 2df))."""
    R, n = gen.R, gen.n
    if family == "courant-dorfman":
        if n == 3:
            H = {(0, 1, 2): gen._poly(rng, 3)}
        else:
            beta = gen._sparse(rng, 2, 3)
            H = V.d_form(R, beta)
    else:
        for _ in range(20):
            H = gen._sparse(rng, 3, 2)
            if V.d_form(R, H):
                break
        else:
            raise OracleSelfCheckError("could not draw a non-closed 3-form")

    def br(u, v):
        X, xi, Y, eta = u[:n], u[n:], v[:n], v[n:]
        Xd = {(i,): c for i, c in enumerate(X) if not c.is_zero}
        xid = {(i,): c for i, c in enumerate(xi) if not c.is_zero}
        etad = {(i,): c for i, c in enumerate(eta) if not c.is_zero}
        cot = V.dadd(V.lie_form(R, X, etad), V.dneg(V.dinterior(Y, V.d_form(R, xid))),
                     V.dinterior(Y, V.dinterior(X, H)))
        del Xd
        return V.vf_bracket(R, X, Y) + V.oneform_vec(R, cot)

    r = 2 * n
    half, two = R.const(Fraction(1, 2)), R.const(2)
    G = [[R.zero()] * r for _ in range(r)]
    Ginv = [[R.zero()] * r for _ in range(r)]
    for i in range(n):
        G[i][n + i] = G[n + i][i] = half
        Ginv[i][n + i] = Ginv[n + i][i] = two
    rho = [V.basis(R, a) for a in range(n)] + [tuple(R.zero() for _ in range(n)) for _ in range(n)]
    st = EStructure(family, family, R, rho, br, G=G, Ginv=Ginv, regular=True)

    def loc(om, u, v):
        return V.sec_scale(st.metric(u, v), st.sharp(om))

    st._loc = loc
    return st


def _generic(gen, rng, family: str, r: int) -> EStructure:
    """Generic polynomial anchor and structure functions:
    ``[u,v]^c = u^aρ_a(v^c) − λ v^bρ_b(u^c) + C^c_ab u^a v^b (+ breakers)``.
    Right Leibniz holds for every λ, C; left Leibniz holds with
    ``L(ω,u,v) = (1−λ) ω(v) u``. The breaker
    ``B(u,v)^c = N^c_de v^e ρ_0(ρ_0(u^d))`` is not C∞-linear in ``u``
    (breaks left Leibniz); ``B(v,u)`` breaks right Leibniz."""
    R, n = gen.R, gen.n
    rho = []
    for a in range(r):
        # affine anchor (degree 1): non-constant, but keeps nested
        # brackets of the Palais d_E² affordable
        col = [_sparse_poly(gen, rng, 1, 0.3) for _ in range(n)]
        if all(c.is_zero for c in col) or all(c.is_ground for c in col):
            col[a % n] = col[a % n] + gen._poly(rng, 1)
        rho.append(tuple(col))
    skew = family in ("skew-almost", "skew-only")
    lam = R.const(1) if skew else R.const(rng.choice([2, -1, 3, Fraction(1, 2)]))
    C = {}
    for c in range(r):
        for a in range(r):
            for b in range(r):
                if skew and a >= b:
                    continue
                p = _sparse_poly(gen, rng, 1, 0.5)
                if not p.is_zero:
                    C[(c, a, b)] = p
                    if skew:
                        C[(c, b, a)] = -p

    def Nmat():
        N = {}
        for c in range(r):
            for d in range(r):
                for e in range(r):
                    if rng.random() < 0.35:
                        N[(c, d, e)] = R.const(rng.choice([-2, -1, 1, 2]))
        if not N:
            N[(0, 0, 0)] = R.one()
        return N

    breaker_left = family in ("right-leibniz-only", "skew-only", "bare")
    breaker_right = family == "bare"
    N1 = Nmat() if breaker_left else None
    N2 = Nmat() if breaker_right else None
    rho0 = rho[0]

    def B(N, u, v):
        out = [R.zero()] * r
        dd = [V.vf_apply(R, rho0, V.vf_apply(R, rho0, u[d])) for d in range(r)]
        for (c, d, e), k in N.items():
            if not dd[d].is_zero and not v[e].is_zero:
                out[c] = out[c] + k * v[e] * dd[d]
        return out

    def br(u, v):
        ru, rv = _anchor(rho, u, R), _anchor(rho, v, R)
        out = []
        for c in range(r):
            val = V.vf_apply(R, ru, v[c]) - lam * V.vf_apply(R, rv, u[c])
            out.append(val)
        for (c, a, b), p in C.items():
            if not u[a].is_zero and not v[b].is_zero:
                out[c] = out[c] + p * u[a] * v[b]
        if N1 is not None:
            b1 = B(N1, u, v)
            if skew:
                b2 = B(N1, v, u)
                out = [o + x - y for o, x, y in zip(out, b1, b2)]
            else:
                out = [o + x for o, x in zip(out, b1)]
        if N2 is not None:
            out = [o + x for o, x in zip(out, B(N2, v, u))]
        return tuple(out)

    loc = None
    if not breaker_left:
        one_minus = R.one() - lam

        def loc(om, u, v):
            s = sum((om[a] * v[a] for a in range(r)), R.zero())
            return V.sec_scale(one_minus * s, u)

    return EStructure(family, family + f" (λ={lam.as_expr()})", R, rho, br, loc=loc, regular=False)


# --------------------------------------------------------------------- #
# Self-check                                                             #
# --------------------------------------------------------------------- #


def _defects(st: EStructure, gen: TangentModel, rng) -> Dict[str, bool]:
    """``{axiom: holds on the random test data}`` for the algebraic axioms."""
    R, r = st.R, st.r

    def sec():
        return tuple(_sparse_poly(gen, rng, 2, 0.25) for _ in range(r))

    def zero(t):
        return all(x.is_zero for x in t)

    def sub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    u, v, w = sec(), sec(), sec()
    f, h = gen._poly(rng, 3), gen._poly(rng, 2)
    br = st.bracket
    out = {}
    out[RL] = zero(sub(br(u, V.sec_scale(f, v)),
                       V.sec_add(R, V.sec_scale(st.act(u, f), v), V.sec_scale(f, br(u, v)))))

    def delta(f, u, v):  # [fu,v] − f[u,v] + ρ(v)(f)u
        return V.sec_add(R, sub(br(V.sec_scale(f, u), v), V.sec_scale(f, br(u, v))), V.sec_scale(st.act(v, f), u))

    if st.has_locality:
        out[LL] = zero(sub(delta(f, u, v), st.locality(st.D(f), u, v)))
    else:
        # violated certainly iff the defect is not C∞-linear in u
        tensorial = zero(sub(delta(f, V.sec_scale(h, u), v), V.sec_scale(h, delta(f, u, v))))
        out[LL] = None if tensorial else False
    out[AM] = zero(sub(st.anchor(br(u, v)), V.vf_bracket(R, st.anchor(u), st.anchor(v))))
    out[J] = zero(sub(sub(br(u, br(v, w)), br(br(u, v), w)), br(v, br(u, w))))
    out[AS] = zero(V.sec_add(R, br(u, v), br(v, u)))
    if st.has_metric:
        sym = V.sec_add(R, br(u, v), br(v, u))
        out[SP] = zero(sub(sym, st.sharp(st.D(st.metric(u, v)))))
        mi = st.act(u, st.metric(v, w)) - st.metric(br(u, v), w) - st.metric(v, br(u, w))
        out[MI] = mi.is_zero
    else:
        out[SP] = out[MI] = False
    return out


_CACHE: Dict = {}


def build_structure(family: str, n: int, r: int, pool: int) -> EStructure:
    """The (cached, self-checked) structure of ``family`` on ``R^n`` with
    rank ``r``, from structure seed ``pool``."""
    key = (family, n, r, pool)
    hit = _CACHE.get(key)
    if hit is not None:
        return hit
    claims = FAMILIES[family][0]
    seed = _subseed(pool, ("algebroid-structure", family, n, r))
    gen = TangentModel(n, seed)
    rng = random.Random(seed)
    if family in ("lie-tm+R", "almost-lie-tm+R", "pre-leibniz-tm+R"):
        base = _tm_plus_r(gen, rng, family)
    elif family == "lie-so3":
        base = _so3(gen, rng, family)
    elif family in ("courant-dorfman", "pre-courant-dorfman"):
        base = _dorfman(gen, rng, family)
    else:
        base = _generic(gen, rng, family, r)
    if base.r != r:
        raise OracleSelfCheckError(f"{family}: rank {base.r} ≠ requested {r}")
    A, Ainv = _unipotent(gen, rng, r)
    st = _transport(base, A, Ainv)
    st.label = f"{family} (n={n}, r={r}, pool {pool})"
    # numerical self-check on two independent random data sets
    holds = {a: True for a in ALGEBRAIC}
    for k in range(2):
        d = _defects(st, gen, random.Random(_subseed(seed, ("selfcheck", k))))
        for a in ALGEBRAIC:
            if d[a] is None:
                holds[a] = None if holds[a] is not False else False
            elif not d[a]:
                holds[a] = False
    bad_claims = sorted(a for a in claims if a in ALGEBRAIC and holds[a] is not True)
    if bad_claims:
        raise OracleSelfCheckError(f"{family}: claimed axioms {bad_claims} fail on random sections")
    not_violated = sorted(a for a in ALGEBRAIC if a not in claims and holds[a] is not False)
    if not_violated:
        raise OracleSelfCheckError(f"{family}: axioms {not_violated} are not verifiably violated")
    st.satisfied = frozenset(claims)
    viol = set(a for a in ALGEBRAIC if a not in claims)
    if REG not in claims and _rank_varies(st):
        viol.add(REG)
    st.violated = frozenset(viol)
    _CACHE[key] = st
    return st


def _rank_varies(st: EStructure) -> bool:
    """The anchor's rank at the origin differs from its rank at a generic
    rational point (a certificate of NON-regularity)."""
    R = st.R
    pts = [{c: 0 for c in R.coords}, {c: sp.Rational(k + 2, k + 3) for k, c in enumerate(R.coords)}]
    ranks = []
    for p in pts:
        M = sp.Matrix([[st.rho[a][i].as_expr().subs(p) for a in range(st.r)] for i in range(st.n)])
        ranks.append(M.rank())
    return ranks[0] != ranks[1]


# --------------------------------------------------------------------- #
# The model                                                              #
# --------------------------------------------------------------------- #


class AlgebroidModel(TangentModel):
    """A :class:`TangentModel` plus algebroid structures, sections and
    E-forms of their bundles, bundle maps and frames.

    ``structures``: ``{algebroid name: EStructure}``; ``bundles``:
    ``{bundle: (rank, algebroid name or None)}``; ``anchors``:
    ``{algebroid name: anchor display name}``."""

    def __init__(self, n: int, seed: int, *, structures=None, bundles=None, anchors=None, **kw) -> None:
        super().__init__(n, seed, **kw)
        self.structures: Dict[str, EStructure] = dict(structures or {})
        self.bundles: Dict = dict(bundles or {})
        self.anchors: Dict[str, str] = dict(anchors or {})

    def describe(self) -> str:
        base = super().describe()
        if self.structures:
            base += " " + "; ".join(f"{k}: {st.label}" for k, st in sorted(self.structures.items()))
        return base

    # ---- structure lookup --------------------------------------------- #

    def structure(self, name: str, path=()) -> EStructure:
        st = self.structures.get(name)
        if st is None:
            raise Unsupported("algebroid[unknown structure]", path, name)
        return st

    def rank(self, bundle, path=()) -> int:
        entry = self.bundles.get(bundle)
        if entry is None:
            raise Unsupported("bundle[unmodeled]", path, repr(bundle))
        return entry[0]

    def bundle_structure(self, bundle) -> Optional[EStructure]:
        entry = self.bundles.get(bundle)
        if entry is None or entry[1] is None:
            return None
        return self.structures.get(entry[1])

    def bundle_of(self, name: str):
        for b, (r, alg) in self.bundles.items():
            if alg == name:
                return b
        raise Unsupported("algebroid[unknown bundle]", (), name)

    # ---- atoms -------------------------------------------------------- #

    def section(self, bundle, key) -> SecV:
        k = ("section", bundle, key)
        if k not in self._cache:
            rng = self._rng(k)
            r = self.rank(bundle)
            comps = [self._poly(rng, 3) if rng.random() < 0.85 else self.R.zero() for _ in range(r)]
            if all(c.is_zero for c in comps):
                comps[0] = self._poly(rng, 3)
            self._cache[k] = SecV(bundle, comps)
        return self._cache[k]

    def eform_components(self, bundle, key, p: int) -> Dict:
        k = ("eform", bundle, key, p)
        if k not in self._cache:
            rng = self._rng(k)
            r = self.rank(bundle)
            out = {}
            for I in combinations(range(r), p):
                if rng.random() < 0.8:
                    out[I] = self._poly(rng, 3)
            if not out and p <= r:
                out[tuple(range(p))] = self._poly(rng, 3)
            self._cache[k] = out
        return self._cache[k]

    def eform(self, bundle, key, p: int):
        comps = self.eform_components(bundle, key, p)
        if p == 0:
            return comps.get((), self.R.zero())
        return alt_form(self, bundle, comps, p, label=str(key))

    def section_map(self, name: str, bundle, tangent: bool):
        """A random C∞-linear map ``Φ``: ``E → TM`` (``n × r``) when
        ``tangent``, else ``E → E`` (``r × r``)."""
        k = ("section-map", name, bundle, tangent)
        if k not in self._cache:
            rng = self._rng(k)
            r = self.rank(bundle) if bundle is not None else self.n
            rows = self.n if tangent else r
            M = [[_sparse_poly(self, rng, 2, 0.3) for _ in range(r)] for _ in range(rows)]
            self._cache[k] = M
        return self._cache[k]

    def frame(self, name: str, bundle):
        """A random frame of ``bundle`` (TM: ``bundle is None``): a unit
        upper-triangular polynomial matrix (det = 1, polynomial inverse).
        Returns ``(columns e_a, coframe rows e^a)``."""
        k = ("frame", name, bundle)
        if k not in self._cache:
            rng = self._rng(k)
            d = self.n if bundle is None else self.rank(bundle)
            M = [[(self.R.one() if i == j else (self._poly(rng, 2) if j > i and rng.random() < 0.7 else self.R.zero()))
                  for j in range(d)] for i in range(d)]
            Minv = _unitri_inverse(M, self.R)
            cols = [tuple(M[i][a] for i in range(d)) for a in range(d)]
            rows = [tuple(Minv[a][i] for i in range(d)) for a in range(d)]
            self._cache[k] = (cols, rows)
        return self._cache[k]

    # ---- test data ---------------------------------------------------- #

    def test_sections(self, bundle, count: int):
        return [self.section(bundle, ("test", "section", i)) for i in range(count)]

    def test_tuples(self, bundle, deg: int):
        """Two tuples of generic test sections for comparing E-forms (one
        in order, one permuted, so a slot-order error is visible)."""
        k = ("test-tuples", bundle, deg)
        if k not in self._cache:
            secs = [s.c for s in self.test_sections(bundle, deg + 1)]
            t1 = tuple(secs[:deg])
            t2 = tuple(reversed(secs[1:deg + 1]))
            self._cache[k] = [t1, t2]
        return self._cache[k]

    def test_arguments(self):
        out = super().test_arguments()
        for b, (r, _alg) in sorted(self.bundles.items(), key=lambda kv: repr(kv[0])):
            out.append(self.section(b, ("test", "op-section")))
            for p in range(1, min(r, 3) + 1):
                out.append(self.eform(b, ("test", "op-eform"), p))
        return out


def _unitri_inverse(M, R):
    d = len(M)
    inv = [[R.one() if i == j else R.zero() for j in range(d)] for i in range(d)]
    # back substitution for an upper unitriangular matrix
    for col in range(d):
        for i in range(d - 1, -1, -1):
            s = R.one() if i == col else R.zero()
            for k in range(i + 1, d):
                if not M[i][k].is_zero:
                    s = s - M[i][k] * inv[k][col]
            inv[i][col] = s
    return inv


def alt_form(ctx, bundle, comps: Dict, p: int, *, label: str = "") -> EFormV:
    """An alternating E-form from its components (determinant convention)."""
    R = ctx.R
    return EFormV(bundle, p, lambda args, comps=comps: V.det_eval(R, comps, args), alt=True, ctx=ctx, label=label)
