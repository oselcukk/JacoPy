"""Concrete values of the model oracle and the coordinate calculus on them.

Everything here is plain coordinate algebra on ``R^n`` with polynomial
coefficients (``sympy.Poly`` over ``QQ``); nothing in this module knows
about the expression tree or the proof engine.

Value kinds
-----------
* scalar        -- a ``Poly`` (functions and numbers alike);
* :class:`VecV` -- a vector field, ``n`` component polys;
* :class:`FormV` -- a differential form, sparse ``{sorted index tuple: poly}``
  (inhomogeneous forms are allowed; ``()`` is the 0-form part);
* :class:`MultiV` -- a multivector field, same sparse representation;
* :class:`OpV`  -- an operator: a callable on values with a degree.

Conventions (matched to the library's docstrings, see the comments at
each function):

* forms/multivectors are ``Σ_I c_I dx^{I_1}∧…∧dx^{I_p}`` over increasing
  ``I``; evaluation is the DETERMINANT convention without ``1/p!``
  (``core/wedge.py``: ``(α∧β)(U,V) = α(U)β(V) − α(V)β(U)``);
* ``ι_X`` inserts into the FIRST slot (``central/objects/interior.py``);
  ``ι̃_α`` likewise on multivectors (``tilde_interior.py``);
* ``d`` is the Palais/intrinsic ``d`` (``bracket_calculus.py``), which in
  the determinant convention is ``d(f dx^I) = df ∧ dx^I``;
* ``[X, Y] = X∘Y − Y∘X`` (``algebra/lie_bracket_vf.py``).
"""

from __future__ import annotations

from itertools import combinations, permutations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import sympy as sp


class Unsupported(Exception):
    """Raised when a node or a value combination has no model semantics.

    ``kind`` is the histogram key (usually a node type name), ``path`` the
    position in the expression tree; both end up in the oracle report.
    """

    def __init__(self, kind: str, path: Tuple = (), detail: str = "") -> None:
        super().__init__(f"{kind} at {path}: {detail}" if detail else f"{kind} at {path}")
        self.kind = kind
        self.path = tuple(path)
        self.detail = detail


class DomainError(Unsupported):
    """An operator applied to a value kind outside its MATHEMATICAL domain
    (``ι_X`` on a vector field, ``d`` on a multivector, a vector field on
    a form). Unlike a plain :class:`Unsupported` (a gap of the oracle),
    this is a fact about the operator: two operators whose domains differ
    on a test argument where one of them is nonzero are different."""


class Budget(Exception):
    """The per-check time or size budget ran out."""


# --------------------------------------------------------------------- #
# Ring of polynomial coefficients                                        #
# --------------------------------------------------------------------- #


class Ring:
    """``QQ[x_0, …, x_{n-1}]`` with the few operations the oracle needs."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.coords = sp.symbols(f"x0:{n}")
        self._zero = sp.Poly(0, *self.coords, domain="QQ")
        self._one = sp.Poly(1, *self.coords, domain="QQ")

    def zero(self) -> sp.Poly:
        return self._zero

    def one(self) -> sp.Poly:
        return self._one

    def const(self, c) -> sp.Poly:
        return sp.Poly(sp.Rational(c), *self.coords, domain="QQ")

    def poly(self, expr) -> sp.Poly:
        return sp.Poly(expr, *self.coords, domain="QQ")

    def var(self, i: int) -> sp.Poly:
        return sp.Poly(self.coords[i], *self.coords, domain="QQ")

    def diff(self, p: sp.Poly, i: int) -> sp.Poly:
        return p.diff(self.coords[i])

    def is_scalar(self, v) -> bool:
        return isinstance(v, sp.Poly)


# --------------------------------------------------------------------- #
# Value classes                                                          #
# --------------------------------------------------------------------- #


class VecV:
    __slots__ = ("c",)

    def __init__(self, c: Sequence[sp.Poly]) -> None:
        self.c = tuple(c)

    def is_zero(self) -> bool:
        return all(x.is_zero for x in self.c)

    def __repr__(self) -> str:
        return "Vec(" + ", ".join(str(x.as_expr()) for x in self.c) + ")"


class _Graded:
    __slots__ = ("d",)
    tag = "?"

    def __init__(self, d: Dict[Tuple[int, ...], sp.Poly]) -> None:
        self.d = {k: v for k, v in d.items() if not v.is_zero}

    def is_zero(self) -> bool:
        return not self.d

    def degrees(self) -> set:
        return {len(k) for k in self.d}

    def __repr__(self) -> str:
        if not self.d:
            return f"{self.tag}(0)"
        parts = []
        for k in sorted(self.d):
            parts.append(f"({self.d[k].as_expr()})·{self.tag.lower()}{''.join(map(str, k)) or '1'}")
        return f"{self.tag}(" + " + ".join(parts) + ")"


class FormV(_Graded):
    __slots__ = ()
    tag = "Form"


class MultiV(_Graded):
    __slots__ = ()
    tag = "Multi"


class OpV:
    """An operator value. ``fn(value) -> value`` raises :class:`Unsupported`
    outside its domain. ``degree`` is the operator degree (``None`` when
    inhomogeneous / unknown) used by graded commutators."""

    __slots__ = ("fn", "degree", "label")

    def __init__(self, fn: Callable, degree: Optional[int], label: str) -> None:
        self.fn = fn
        self.degree = degree
        self.label = label

    def __call__(self, v):
        return self.fn(v)

    def is_zero(self) -> bool:  # an operator is never structurally zero
        return False

    def __repr__(self) -> str:
        return f"Op({self.label})"


# --------------------------------------------------------------------- #
# Sparse exterior algebra (shared by forms and multivectors)             #
# --------------------------------------------------------------------- #


def perm_sign(indices: Sequence[int]) -> int:
    """Sign of the permutation sorting ``indices`` (0 on a repeat)."""
    if len(set(indices)) != len(indices):
        return 0
    s = 1
    seq = list(indices)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def dadd(*ds: Dict) -> Dict:
    out: Dict = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out[k] + v if k in out else v
    return {k: v for k, v in out.items() if not v.is_zero}


def dscale(d: Dict, c: sp.Poly) -> Dict:
    return {k: v * c for k, v in d.items() if not (v * c).is_zero}


def dneg(d: Dict) -> Dict:
    return {k: -v for k, v in d.items()}


def dwedge(a: Dict, b: Dict) -> Dict:
    """``(dx^I) ∧ (dx^J) = sign(IJ) dx^{sort(IJ)}`` (same for ∂'s)."""
    out: Dict = {}
    for I, x in a.items():
        for J, y in b.items():
            K = I + J
            s = perm_sign(K)
            if s == 0:
                continue
            key = tuple(sorted(K))
            term = x * y if s > 0 else -(x * y)
            out[key] = out[key] + term if key in out else term
    return {k: v for k, v in out.items() if not v.is_zero}


def dinterior(v: Sequence[sp.Poly], a: Dict) -> Dict:
    """Insert the 1-slot object with components ``v`` into the FIRST slot:
    ``ι_v dx^I = Σ_k (−1)^k v_{I_k} dx^{I∖I_k}`` — (ι_X ω)(X₁…) = ω(X, X₁…)
    in the determinant convention (``central/objects/interior.py``)."""
    out: Dict = {}
    for I, c in a.items():
        for k, i in enumerate(I):
            rest = I[:k] + I[k + 1:]
            term = v[i] * c
            if k % 2:
                term = -term
            out[rest] = out[rest] + term if rest in out else term
    return {k: x for k, x in out.items() if not x.is_zero}


def det_eval(R: Ring, a: Dict, args: Sequence[Sequence[sp.Poly]]) -> sp.Poly:
    """``a(args) = Σ_I a_I det[args_j(I_i)]`` over the degree-``len(args)``
    part of ``a`` (determinant convention, no ``1/p!``)."""
    p = len(args)
    total = R.zero()
    for I, c in a.items():
        if len(I) != p:
            continue
        det = R.zero()
        for perm in permutations(range(p)):
            term = R.one()
            for i in range(p):
                term = term * args[perm[i]][I[i]]
            s = perm_sign(perm)
            det = det + term if s > 0 else det - term
        total = total + c * det
    return total


def basis(R: Ring, i: int) -> Tuple[sp.Poly, ...]:
    return tuple(R.one() if j == i else R.zero() for j in range(R.n))


def components_of(R: Ring, fn: Callable[[Tuple[int, ...]], sp.Poly], degree: int) -> Dict:
    """Build a sparse alternating object of ``degree`` from its values on
    increasing basis index tuples."""
    out = {}
    for I in combinations(range(R.n), degree):
        v = fn(I)
        if not v.is_zero:
            out[I] = v
    return out


# --------------------------------------------------------------------- #
# Cartan calculus on TM                                                  #
# --------------------------------------------------------------------- #


def vf_apply(R: Ring, X: Sequence[sp.Poly], f: sp.Poly) -> sp.Poly:
    """``X(f) = X^i ∂_i f``."""
    out = R.zero()
    for i in range(R.n):
        if not X[i].is_zero:
            out = out + X[i] * R.diff(f, i)
    return out


def vf_bracket(R: Ring, X, Y) -> Tuple[sp.Poly, ...]:
    """``[X, Y]^i = X(Y^i) − Y(X^i)`` (``[X,Y] = X∘Y − Y∘X``)."""
    return tuple(vf_apply(R, X, Y[i]) - vf_apply(R, Y, X[i]) for i in range(R.n))


def d_form(R: Ring, a: Dict) -> Dict:
    """``d(c dx^I) = Σ_i ∂_i c dx^i ∧ dx^I`` (== the Palais d in the
    determinant convention)."""
    out: Dict = {}
    for I, c in a.items():
        for i in range(R.n):
            dc = R.diff(c, i)
            if dc.is_zero:
                continue
            out = dadd(out, dwedge({(i,): dc}, {I: R.one()}))
    return out


def lie_form(R: Ring, X, a: Dict) -> Dict:
    """Lie derivative from the library's DEFINING evaluation formula
    (``bracket_calculus.LieDerivative``):
    ``(L_X ω)(Y…) = X(ω(Y…)) − Σ_i ω(…, [X, Y_i], …)``; on constant basis
    vectors ``[X, e_j] = −∂_j X``. Deliberately NOT ``dι + ιd`` so that the
    Cartan magic formula is a genuine check."""
    out: Dict = {}
    for p in {len(I) for I in a}:
        part = {I: c for I, c in a.items() if len(I) == p}

        def comp(J, part=part):
            val = vf_apply(R, X, det_eval(R, part, [basis(R, j) for j in J]) if p else part.get((), R.zero()))
            for k in range(len(J)):
                dX = tuple(R.diff(X[m], J[k]) for m in range(R.n))
                args = [basis(R, j) for j in J]
                args[k] = dX
                val = val + det_eval(R, part, args)
            return val

        out = dadd(out, components_of(R, comp, p))
    return out


def lie_multi(R: Ring, X, P: Dict) -> Dict:
    """``(L_X P)(β…) = X(P(β…)) − Σ_i P(…, L_X β_i, …)`` with constant basis
    covectors, ``L_X dx^j = d(X^j)`` (tensor Lie derivative; independent of
    the Schouten bracket)."""
    out: Dict = {}
    for p in {len(I) for I in P}:
        part = {I: c for I, c in P.items() if len(I) == p}

        def comp(J, part=part):
            if p == 0:
                return vf_apply(R, X, part.get((), R.zero()))
            val = vf_apply(R, X, det_eval(R, part, [basis(R, j) for j in J]))
            for k in range(len(J)):
                dXj = tuple(R.diff(X[J[k]], m) for m in range(R.n))
                args = [basis(R, j) for j in J]
                args[k] = dXj
                val = val - det_eval(R, part, args)
            return val

        out = dadd(out, components_of(R, comp, p))
    return out


# --------------------------------------------------------------------- #
# Schouten–Nijenhuis bracket (library recursion, schouten.py)            #
# --------------------------------------------------------------------- #


def _factors(R: Ring, P: Dict):
    """Decompose into terms ``c ∧ ∂_{K1} ∧ … ∧ ∂_{Kp}``: lists of factors,
    a factor being ``('f', poly)`` or ``('v', i)``."""
    for K, c in P.items():
        yield [("f", c)] + [("v", k) for k in K]


def _fdict(R: Ring, fac) -> Dict:
    return {(): fac[1]} if fac[0] == "f" else {(fac[1],): R.one()}


def _wedge_list(R: Ring, facs) -> Dict:
    out = {(): R.one()}
    for f in facs:
        out = dwedge(out, _fdict(R, f))
    return out


def _m(facs) -> int:
    return sum(1 for f in facs if f[0] == "v")


def _sn(R: Ring, A, B) -> Dict:
    """``[A, B]_SN`` by the library's defining recursion (schouten.py):
    ``[X,Y]=[X,Y]_Lie, [f,g]=0, [X,f]=X(f), [f,X]=−X(f)``,
    ``[X∧Y, Z] = X∧[Y,Z] + (−1)^{s(Z)m(Y)} [X,Z]∧Y``,
    ``[Z, X∧Y] = [Z,X]∧Y + (−1)^{s(Z)m(X)} X∧[Z,Y]``, ``s = m − 1``."""
    if len(A) == 1 and len(B) == 1:
        a, b = A[0], B[0]
        if a[0] == "v" and b[0] == "v":
            return {}  # coordinate fields commute
        if a[0] == "v" and b[0] == "f":
            v = R.diff(b[1], a[1])
            return {(): v} if not v.is_zero else {}
        if a[0] == "f" and b[0] == "v":
            v = -R.diff(a[1], b[1])
            return {(): v} if not v.is_zero else {}
        return {}
    if len(A) > 1:
        X, Y, Z = A[:1], A[1:], B
        sZ = _m(Z) - 1
        sign = -1 if (sZ * _m(Y)) % 2 else 1
        t1 = dwedge(_wedge_list(R, X), _sn(R, Y, Z))
        t2 = dwedge(_sn(R, X, Z), _wedge_list(R, Y))
        return dadd(t1, t2 if sign > 0 else dneg(t2))
    Z, X, Y = A, B[:1], B[1:]
    sZ = _m(Z) - 1
    sign = -1 if (sZ * _m(X)) % 2 else 1
    t1 = dwedge(_sn(R, Z, X), _wedge_list(R, Y))
    t2 = dwedge(_wedge_list(R, X), _sn(R, Z, Y))
    return dadd(t1, t2 if sign > 0 else dneg(t2))


def schouten(R: Ring, P: Dict, Q: Dict) -> Dict:
    out: Dict = {}
    for A in _factors(R, P):
        for B in _factors(R, Q):
            out = dadd(out, _sn(R, A, B))
    return out


# --------------------------------------------------------------------- #
# Poisson / tilde calculus (packages/poisson)                            #
# --------------------------------------------------------------------- #


def sharp(R: Ring, pi: Dict, alpha: Sequence[sp.Poly]) -> Tuple[sp.Poly, ...]:
    """``⟨β, π♯α⟩ = π(α, β)`` (poisson/core.py), so ``(π♯α)^k = π(α, dx^k)``."""
    return tuple(det_eval(R, pi, [alpha, basis(R, k)]) for k in range(R.n))


def oneform_vec(R: Ring, a: Dict) -> Tuple[sp.Poly, ...]:
    return tuple(a.get((i,), R.zero()) for i in range(R.n))


def koszul(R: Ring, pi: Dict, alpha, beta) -> Tuple[sp.Poly, ...]:
    """``[α, β]_π = L_{π♯α}β − L_{π♯β}α − d(π(α, β))`` (poisson/koszul.py)."""
    A = {(i,): c for i, c in enumerate(alpha) if not c.is_zero}
    B = {(i,): c for i, c in enumerate(beta) if not c.is_zero}
    sa, sb = sharp(R, pi, alpha), sharp(R, pi, beta)
    pab = det_eval(R, pi, [alpha, beta])
    out = dadd(lie_form(R, sa, B), dneg(lie_form(R, sb, A)), dneg(d_form(R, {(): pab})))
    return oneform_vec(R, out)


def tilde_d(R: Ring, pi: Dict, V: Dict) -> Dict:
    """Palais formula of the cotangent algebroid ``(T*M, π♯, [·,·]_π)``
    (bracket_calculus.py instantiated by poisson/tilde.py), on basis
    covectors: ``d̃V(α_0…α_p) = Σ_i (−1)^i π♯α_i(V(…α̂_i…)) +
    Σ_{i<j} (−1)^{i+j} V([α_i, α_j]_π, …α̂_i…α̂_j…)``."""
    out: Dict = {}
    for p in {len(I) for I in V}:
        part = {I: c for I, c in V.items() if len(I) == p}

        def comp(I, part=part, p=p):
            cov = [basis(R, i) for i in I]
            val = R.zero()
            for i in range(len(I)):
                rest = [cov[k] for k in range(len(I)) if k != i]
                inner = det_eval(R, part, rest) if p else part.get((), R.zero())
                term = vf_apply(R, sharp(R, pi, cov[i]), inner)
                val = val + term if i % 2 == 0 else val - term
            for i in range(len(I)):
                for j in range(i + 1, len(I)):
                    br = koszul(R, pi, cov[i], cov[j])
                    rest = [cov[k] for k in range(len(I)) if k not in (i, j)]
                    term = det_eval(R, part, [br] + rest)
                    val = val + term if (i + j) % 2 == 0 else val - term
            return val

        out = dadd(out, components_of(R, comp, p + 1))
    return out


def tilde_lie(R: Ring, pi: Dict, alpha, V: Dict) -> Dict:
    """``(L̃_α V)(β…) = π♯α(V(β…)) − Σ_i V(…, [α, β_i]_π, …)`` — the generic
    intrinsic L of bracket_calculus.py in the tilde calculus."""
    sa = sharp(R, pi, alpha)
    out: Dict = {}
    for p in {len(I) for I in V}:
        part = {I: c for I, c in V.items() if len(I) == p}

        def comp(J, part=part, p=p):
            if p == 0:
                return vf_apply(R, sa, part.get((), R.zero()))
            cov = [basis(R, j) for j in J]
            val = vf_apply(R, sa, det_eval(R, part, cov))
            for k in range(len(J)):
                args = list(cov)
                args[k] = koszul(R, pi, alpha, cov[k])
                val = val - det_eval(R, part, args)
            return val

        out = dadd(out, components_of(R, comp, p))
    return out


def nambu_sharp(R: Ring, Pi: Dict, omega: Dict, p: int) -> Tuple[sp.Poly, ...]:
    """``(Πω)(f) = Π(α₁,…,α_p, df)`` for ``ω = α₁∧…∧α_p`` (nambu.py), extended
    linearly: ``(Πω)^k = Σ_I ω_I Π(dx^{I_1},…,dx^{I_p}, dx^k)``."""
    out = [R.zero()] * R.n
    for I, c in omega.items():
        if len(I) != p:
            raise Unsupported("NambuSharpVF", (), f"form of degree {len(I)} for p={p}")
        for k in range(R.n):
            v = det_eval(R, Pi, [basis(R, i) for i in I] + [basis(R, k)])
            if not v.is_zero:
                out[k] = out[k] + c * v
    return tuple(out)


# --------------------------------------------------------------------- #
# Algebroid values: sections of E and (ordered) E-forms                  #
# --------------------------------------------------------------------- #


class SecV:
    """A section of a bundle ``E ≠ TM``: ``r`` component polys in the
    model's constant frame of ``E = R^n × R^r``. ``b`` is the bundle key
    (sections of different bundles never mix)."""

    __slots__ = ("b", "c")

    def __init__(self, b, c: Sequence[sp.Poly]) -> None:
        self.b = b
        self.c = tuple(c)

    def is_zero(self) -> bool:
        return all(x.is_zero for x in self.c)

    def __repr__(self) -> str:
        return f"Sec[{self.b}](" + ", ".join(str(x.as_expr()) for x in self.c) + ")"


class EFormV:
    """An E-p-form (p ≥ 1) as an ORDERED ℝ-multilinear map on sections,
    evaluated LAZILY on concrete sections: ``fn(list of r-tuples) -> poly``.

    Laziness is the point: for a non-skew / non-right-Leibniz bracket the
    Palais expression ``d_E ω`` is neither alternating nor C∞-linear in
    its first slot (see bracket_calculus.py), so it is not a tensor
    and must be evaluated on the actual arguments, never on a basis.
    ``alt`` records whether the map is alternating (atoms; d_E of an
    alternating form for a verified-skew bracket). ``ctx`` (the model)
    supplies the random test sections used by :meth:`is_zero`."""

    __slots__ = ("b", "deg", "fn", "alt", "ctx", "label")

    def __init__(self, b, deg: int, fn: Callable, *, alt: bool, ctx, label: str = "") -> None:
        self.b = b
        self.deg = deg
        self.fn = _memo_fn(fn)
        self.alt = alt
        self.ctx = ctx
        self.label = label

    def __call__(self, args) -> sp.Poly:
        if len(args) != self.deg:
            raise Unsupported("E-form[arity]", (), f"{len(args)} arguments for degree {self.deg}")
        return self.fn(list(args))

    def is_zero(self) -> bool:
        """Zero on the model's random test tuples (exact polynomial
        arithmetic; a falsifier: nonzero is certain, zero is "not refuted")."""
        return all(self.fn(list(t)).is_zero for t in self.ctx.test_tuples(self.b, self.deg))

    def __repr__(self) -> str:
        vals = []
        for t in self.ctx.test_tuples(self.b, self.deg)[:1]:
            vals.append(str(self.fn(list(t)).as_expr()))
        return f"EForm[{self.b}, deg {self.deg}]({self.label}; on test sections: {', '.join(vals)})"


def _memo_fn(fn):
    """Cache an E-form's values per argument tuple: the same evaluation is
    requested repeatedly (zero tests, displays, nested Palais terms)."""
    if getattr(fn, "_oracle_memo", False):
        return fn
    cache: Dict = {}

    def wrapped(args):
        key = tuple(tuple(a) for a in args)
        hit = cache.get(key)
        if hit is None:
            hit = cache[key] = fn(args)
        return hit

    wrapped._oracle_memo = True
    return wrapped


def sec_add(R: Ring, a: Sequence[sp.Poly], b: Sequence[sp.Poly]) -> Tuple[sp.Poly, ...]:
    return tuple(x + y for x, y in zip(a, b))


def sec_scale(c: sp.Poly, a: Sequence[sp.Poly]) -> Tuple[sp.Poly, ...]:
    return tuple(c * x for x in a)


def alt_eval(R: Ring, comps: Dict, args) -> sp.Poly:
    """An alternating E-form given by its components on increasing frame
    index tuples, evaluated in the determinant convention (no 1/p!) —
    the E version of :func:`det_eval`."""
    return det_eval(R, comps, args)


def shuffles(p: int, q: int):
    """``(sign, first p positions, last q positions)`` of the
    (p, q)-shuffles of ``range(p + q)``."""
    for first in combinations(range(p + q), p):
        rest = tuple(i for i in range(p + q) if i not in first)
        yield perm_sign(first + rest), first, rest


def e_wedge(a_fn, p: int, b_fn, q: int):
    """``(α∧β)(X_1…X_{p+q}) = Σ_{(p,q)-shuffles σ} sgn σ α(X_σ…)β(X_σ…)`` —
    the determinant convention of ``core/wedge.py``
    (``(α∧β)(U,V) = α(U)β(V) − α(V)β(U)``) for alternating α, β."""

    def fn(args):
        out = None
        for s, first, rest in shuffles(p, q):
            term = a_fn([args[i] for i in first]) * b_fn([args[i] for i in rest])
            if s < 0:
                term = -term
            out = term if out is None else out + term
        return out

    return fn
