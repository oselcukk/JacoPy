"""The tangent model: ``M = R^n`` with random polynomial data.

Every atom of the expression tree gets a deterministic random value that
depends only on ``(model seed, atom key)`` — never on traversal order —
so a check is reproducible from its seed alone (SPEC §4).

Poisson data (F1 core): a bivector named by a tilde / Lichnerowicz
calculus (or declared ``poisson`` by its structure) is drawn from a
Poisson family; the counter-model draws a generic quadratic bivector and
verifies ``[π, π]_SN ≠ 0`` numerically. Both families are self-checked
with the oracle's own Schouten bracket (``values.schouten``).
"""

from __future__ import annotations

import hashlib
import random
from itertools import combinations, combinations_with_replacement
from typing import Dict, Optional, Tuple

import sympy as sp

from jacopy.oracle.values import FormV, MultiV, Ring, VecV, schouten


class OracleSelfCheckError(AssertionError):
    """A generated model does not satisfy what it claims (oracle bug)."""


def _subseed(seed: int, key) -> int:
    h = hashlib.sha256(f"{seed}|{key!r}".encode()).hexdigest()
    return int(h[:16], 16)


#: Polynomial degrees of the random data: functions AND vector / form /
#: multivector coefficients are cubic, so third-derivative errors (Jacobi
#: type identities, ∂³ terms) are not killed by the data.
FUNCTION_DEGREE = 3
COEFF_DEGREE = 3


class TangentModel:
    """``R^n`` with lazily drawn atom values.

    ``bivectors`` maps a structure bivector's name to its family:
    ``"poisson"`` (a Poisson bivector), ``"counter"`` (a generic,
    verified non-Poisson bivector) or ``"generic"`` (an unconstrained
    random bivector, treated like any other ``PVector``).
    """

    def __init__(self, n: int, seed: int, *, bivectors: Optional[Dict[str, str]] = None,
                 degrees: Optional[Dict[str, int]] = None, label: str = "", sample: int = 0) -> None:
        self.n = n
        #: sample 0 of every check draws NON-DEGENERATE Poisson bivectors
        #: (∂π ≠ 0 and ∂²π ≠ 0); later samples may draw any family
        self.sample = sample
        self.seed = seed
        self.R = Ring(n)
        self.bivectors = dict(bivectors or {})
        self.degrees = dict(degrees or {})
        self.label = label
        self._cache: Dict = {}
        self.families: Dict[str, str] = {}

    # ---- description -------------------------------------------------- #

    def describe(self) -> str:
        bits = [f"R^{self.n}", f"seed={self.seed}"]
        if self.families:
            bits.append(", ".join(f"{k}:{v}" for k, v in sorted(self.families.items())))
        if self.degrees:
            bits.append(", ".join(f"{k}={v}" for k, v in sorted(self.degrees.items())))
        if self.label:
            bits.append(self.label)
        return " ".join(bits)

    # ---- random building blocks -------------------------------------- #

    def _rng(self, key) -> random.Random:
        return random.Random(_subseed(self.seed, key))

    def _poly(self, rng: random.Random, degree: int, *, nonzero: bool = True,
              variables: Optional[Tuple[int, ...]] = None):
        """A SPARSE random polynomial: 3–5 monomials of degree ≤ ``degree``
        with small nonzero integer coefficients, one of them of full
        degree (so ``degree``-th derivatives do not vanish). Sparse keeps
        R^5/R^6 models affordable; genericity comes from the random
        support and coefficients."""
        R = self.R
        vs = tuple(range(R.n)) if variables is None else variables
        top = [m for m in combinations_with_replacement(vs, degree)]
        lower = [m for d in range(degree) for m in combinations_with_replacement(vs, d)]
        monos = [rng.choice(top)] + rng.sample(lower, min(len(lower), rng.randint(2, 4)))
        expr = sp.Integer(0)
        for mono in monos:
            term = sp.Integer(rng.choice([-3, -2, -1, 1, 2, 3]))
            for i in mono:
                term = term * R.coords[i]
            expr = expr + term
        return R.poly(expr)

    def _poly_min(self, rng: random.Random, degree: int, mindeg: int, variables: Tuple[int, ...]):
        """A random polynomial with at least one monomial of degree ≥ ``mindeg``."""
        R = self.R
        base = self._poly(rng, degree, variables=variables)
        if base.total_degree() >= mindeg:
            return base
        mono = sp.Integer(rng.choice([1, 2, -1, 3]))
        for _ in range(rng.randint(mindeg, degree)):
            mono = mono * R.coords[rng.choice(variables)]
        return base + R.poly(mono)

    def _sparse(self, rng: random.Random, p: int, degree: int) -> Dict:
        out = {}
        for I in combinations(range(self.n), p):
            if p == 0 or rng.random() < 0.8:
                c = self._poly(rng, degree, nonzero=False)
                if not c.is_zero:
                    out[I] = c
        if not out and p <= self.n:
            I = tuple(range(p))
            out[I] = self._poly(rng, degree)
        return out

    # ---- atom values ------------------------------------------------- #

    def function(self, key):
        k = ("function", key)
        if k not in self._cache:
            self._cache[k] = self._poly(self._rng(k), FUNCTION_DEGREE)
        return self._cache[k]

    def constant(self, key):
        k = ("constant", key)
        if k not in self._cache:
            rng = self._rng(k)
            self._cache[k] = self.R.const(sp.Rational(rng.choice([-5, -3, -2, 2, 3, 5, 7]), rng.choice([1, 1, 2, 3])))
        return self._cache[k]

    def vector(self, key) -> VecV:
        k = ("vector", key)
        if k not in self._cache:
            rng = self._rng(k)
            self._cache[k] = VecV(tuple(self._poly(rng, COEFF_DEGREE, nonzero=False) for _ in range(self.n)))
        return self._cache[k]

    def form(self, key, p: int) -> FormV:
        k = ("form", key, p)
        if k not in self._cache:
            self._cache[k] = FormV(self._sparse(self._rng(k), p, COEFF_DEGREE) if p <= self.n else {})
        return self._cache[k]

    def multivector(self, key, p: int) -> MultiV:
        """A ``p``-vector atom; a structure bivector follows its family."""
        if p == 2 and key in self.bivectors:
            return self.structure_bivector(key)
        k = ("multi", key, p)
        if k not in self._cache:
            self._cache[k] = MultiV(self._sparse(self._rng(k), p, COEFF_DEGREE) if p <= self.n else {})
        return self._cache[k]

    # ---- Poisson families --------------------------------------------- #

    def structure_bivector(self, name: str) -> MultiV:
        family = self.bivectors.get(name, "generic")
        k = ("bivector", name, family)
        if k in self._cache:
            return self._cache[k]
        rng = self._rng(k)
        R = self.R
        if family == "poisson":
            d, label = self._poisson(rng)
            if schouten(R, d, d):
                raise OracleSelfCheckError(f"{label} bivector is not Poisson: [π,π]_SN ≠ 0")
        elif family == "counter":
            d, label = self._counter(rng)
        else:
            d, label = self._sparse(rng, 2, COEFF_DEGREE), "generic"
        self.families[name] = label
        self._cache[k] = MultiV(d)
        return self._cache[k]

    def _poisson(self, rng: random.Random):
        """Poisson families. Sample 0 always draws a NON-DEGENERATE one
        (coefficients of total degree ≥ 2, so ∂π ≠ 0 and ∂²π ≠ 0)."""
        R, n = self.R, self.n
        x = R.coords
        strong = self.sample == 0
        if n == 2:
            # every bivector on R^2 is Poisson; f cubic
            return {(0, 1): self._poly_min(rng, 3, 3 if strong else 0, (0, 1))}, "f∂0∧∂1 (f cubic)"
        families = ["lie-poisson×casimir"] + (["blocks"] if n >= 4 else [])
        if not strong:
            families += ["constant", "lie-poisson"]
        choice = rng.choice(families)
        if choice == "constant":
            d = {}
            for I in combinations(range(n), 2):
                c = rng.choice([-2, -1, 0, 1, 2, 3])
                if c:
                    d[I] = R.const(c)
            if not d:
                d[(0, 1)] = R.one()
            return d, "constant"
        if choice in ("lie-poisson", "lie-poisson×casimir"):
            # so(3)* Lie–Poisson on (x0, x1, x2) times a function of the
            # Casimir C = |x|²: (a + b·C + c·C²)·π_LP is still Poisson.
            a = rng.choice([1, 2, -1])
            b = rng.choice([1, -1, 2]) if choice.endswith("casimir") else 0
            c = rng.choice([0, 1]) if choice.endswith("casimir") else 0
            C = x[0] ** 2 + x[1] ** 2 + x[2] ** 2
            cas = R.poly(a + b * C + c * C ** 2)
            d = {(0, 1): cas * R.var(2), (0, 2): -(cas * R.var(1)), (1, 2): cas * R.var(0)}
            return d, "lie-poisson so(3)" + ("×casimir" if b else "")
        # n >= 4: a product of two planar Poisson structures, cubic factors
        f = self._poly_min(rng, 3, 2, (0, 1))
        g = self._poly_min(rng, 3, 2, (2, 3))
        return {(0, 1): f, (2, 3): g}, "planar blocks"

    def _counter(self, rng: random.Random):
        if self.n < 3:
            raise OracleSelfCheckError("a non-Poisson bivector needs n ≥ 3")
        for _ in range(20):
            d = self._sparse(rng, 2, COEFF_DEGREE)
            if schouten(self.R, d, d):
                return d, "non-Poisson (verified [π,π]≠0)"
        raise OracleSelfCheckError("could not draw a non-Poisson bivector")

    # ---- test arguments for operator comparison ---------------------- #

    def test_arguments(self):
        """The standard test basis for operator equality: a function and,
        in EVERY degree 1..n, a random form and a random multivector
        (degree 1 multivector = vector field). Operators that differ
        only in high degree (ι_{X∧Y∧Z}, ι_π∘ι_π) are thus separated."""
        out = [self.function(("test", "f"))]
        for p in range(1, self.n + 1):
            out.append(self.form(("test", "form"), p))
        out.append(self.vector(("test", "X")))
        for p in range(2, self.n + 1):
            out.append(self.multivector(("test", "P"), p))
        return out
