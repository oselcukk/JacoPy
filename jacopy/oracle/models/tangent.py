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


#: Polynomial degrees of the random data: scalar functions get cubic
#: polynomials (so third derivatives — Jacobi-type identities — are not
#: trivially killed); vector/form/multivector coefficients are quadratic.
FUNCTION_DEGREE = 3
COEFF_DEGREE = 2


class TangentModel:
    """``R^n`` with lazily drawn atom values.

    ``bivectors`` maps a structure bivector's name to its family:
    ``"poisson"`` (a Poisson bivector), ``"counter"`` (a generic,
    verified non-Poisson bivector) or ``"generic"`` (an unconstrained
    random bivector, treated like any other ``PVector``).
    """

    def __init__(self, n: int, seed: int, *, bivectors: Optional[Dict[str, str]] = None,
                 degrees: Optional[Dict[str, int]] = None, label: str = "") -> None:
        self.n = n
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
        R = self.R
        vs = tuple(range(R.n)) if variables is None else variables
        expr = sp.Integer(0)
        for deg in range(degree + 1):
            for mono in combinations_with_replacement(vs, deg):
                if rng.random() < 0.55:
                    c = rng.choice([-3, -2, -1, 1, 2, 3])
                    term = sp.Integer(c)
                    for i in mono:
                        term = term * R.coords[i]
                    expr = expr + term
        if nonzero and expr == 0:
            expr = sp.Integer(rng.choice([1, 2, -1]))
        return R.poly(expr)

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
        R, n = self.R, self.n
        x = R.coords
        if n == 2:
            return {(0, 1): self._poly(rng, COEFF_DEGREE)}, "f∂0∧∂1"
        choice = rng.choice(["constant", "lie-poisson", "blocks"] if n >= 4 else ["constant", "lie-poisson"])
        if choice == "constant":
            d = {}
            for I in combinations(range(n), 2):
                c = rng.choice([-2, -1, 0, 1, 2, 3])
                if c:
                    d[I] = R.const(c)
            if not d:
                d[(0, 1)] = R.one()
            return d, "constant"
        if choice == "lie-poisson":
            # so(3)* Lie–Poisson on (x0, x1, x2), scaled by a Casimir
            # function (a + b·|x|²) — still Poisson.
            a, b = rng.choice([1, 2, -1]), rng.choice([0, 1, -1])
            cas = R.poly(a + b * (x[0] ** 2 + x[1] ** 2 + x[2] ** 2))
            d = {(0, 1): cas * R.var(2), (0, 2): -(cas * R.var(1)), (1, 2): cas * R.var(0)}
            return d, "lie-poisson so(3)"
        # n >= 4: a product of two planar Poisson structures
        f = self._poly(rng, COEFF_DEGREE, variables=(0, 1))
        g = self._poly(rng, COEFF_DEGREE, variables=(2, 3))
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
        """Arguments on which two operator values are compared."""
        out = [self.function(("test", "f"))]
        for p in (1, 2):
            if p <= self.n:
                out.append(self.form(("test", "form"), p))
        out.append(self.vector(("test", "X")))
        if self.n >= 2:
            out.append(self.multivector(("test", "P"), 2))
        return out
