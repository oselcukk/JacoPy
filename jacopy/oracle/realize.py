"""``realize(expr, env)``: the expression tree → concrete model values.

Dispatch is a type-MRO registration table (the display/latex pattern):
a realizer registered with ``inherit=False`` handles ONLY its exact class,
so a subclass with extra semantics (a frame field is a ``VectorField``
with relations) can never be silently realized as its parent — it is
UNSUPPORTED until it gets its own realizer. Every unsupported node raises
:class:`~jacopy.oracle.values.Unsupported` with its type and tree path;
nothing passes silently.

Independence: this module imports node CLASSES only — never
``jacopy.proof``, ``jacopy.algorithms`` or any ``*Definition`` (enforced
by ``tests/test_oracle_independence.py``). Semantics come from the
library's docstring definitions, re-implemented in coordinates in
:mod:`jacopy.oracle.values`.

Product has two meanings in the library (``algebra/derivation.py``:
``Product`` is both the scalar product and operator composition). Rules
(SPEC §7):

* in ``Act`` operator position a Product is a composition;
* in value position, children that are all values multiply (scalars
  commute; one non-scalar factor is scaled);
* a value-position Product containing an operator-capable child (an
  operator or a vector field) with a NON-CONSTANT scalar factor after it
  has two readings — scalar multiplication vs composition. ``env.mode``
  selects the reading; :mod:`jacopy.oracle.check` evaluates both and
  reports AMBIGUOUS when they disagree.
"""

from __future__ import annotations

import time
from typing import Callable, Dict, Optional, Tuple

from jacopy.algebra.commutator import Commutator
from jacopy.algebra.derivation import Act
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.brackets.base import BracketApply
from jacopy.central.calculus.bracket_calculus import ExteriorDerivative, LieDerivative
from jacopy.central.objects.bundle import TM
from jacopy.central.objects.form import Form
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.multivector_interior import MultivectorInterior
from jacopy.central.objects.partial_eval import PartialEval
from jacopy.central.objects.tilde_interior import TildeInterior
from jacopy.central.objects.vector_field import VectorField
from jacopy.core.expr import Integer, Neg, Power, Product, Rational, Sum, Symbol
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.properties import AntiCommuting, Graded, NonCommuting, Scalar
from jacopy.core.wedge import Wedge
from jacopy.packages.poisson.core import HamiltonianVF, PoissonBracketValue, SharpVF
from jacopy.packages.poisson.koszul import KoszulBracket
from jacopy.packages.poisson.nambu import NambuSharpVF

from jacopy.oracle import values as V
from jacopy.oracle.values import Budget, DomainError, EFormV, FormV, MultiV, OpV, SecV, Unsupported, VecV

# --------------------------------------------------------------------- #
# Registration table                                                     #
# --------------------------------------------------------------------- #

_REALIZERS: Dict[type, Tuple[Callable, bool]] = {}


def register(cls: type, *, inherit: bool = False):
    def deco(fn):
        _REALIZERS[cls] = (fn, inherit)
        return fn

    return deco


def realizer_for(cls: type) -> Optional[Callable]:
    for k in cls.__mro__:
        entry = _REALIZERS.get(k)
        if entry is not None and (k is cls or entry[1]):
            return entry[0]
    return None


def realizable_types() -> Tuple[type, ...]:
    return tuple(_REALIZERS)


#: Calculus names with model semantics (bracket_calculus.py instances):
#: ``Cartan-TM`` (central/tangent/exterior.py), ``tilde-<π>``
#: (poisson/tilde.py), ``lichnerowicz-<Π>`` (generalized/r_twisted.py,
#: realized only for a bivector Π, where its Nambu–Koszul bracket
#: ``L_{Πα}β − ι_{Πβ}dα`` equals the Koszul bracket).
CARTAN_TM_NAME = "Cartan-TM"
STRUCTURE_PREFIXES = ("tilde-", "lichnerowicz-")


def calculus_structure(calculus_name: str) -> Optional[str]:
    for pre in STRUCTURE_PREFIXES:
        if calculus_name.startswith(pre):
            return calculus_name[len(pre):]
    return None


def _calculus_kind(name: str) -> str:
    if name == CARTAN_TM_NAME:
        return "Cartan-TM"
    for pre in STRUCTURE_PREFIXES:
        if name.startswith(pre):
            return pre[:-1]
    if name.startswith("Cartan-"):
        return "algebroid"
    return name.split("-")[0]


# --------------------------------------------------------------------- #
# Environment                                                            #
# --------------------------------------------------------------------- #


class Env:
    """One realization run: a model, a registry, a Product reading."""

    def __init__(self, model, *, registry=None, mode: str = "value", deadline: Optional[float] = None,
                 indices: Optional[Dict[str, int]] = None) -> None:
        self.model = model
        self.R = model.R
        self.registry = registry
        self.mode = mode
        self.deadline = deadline
        self.ambiguous: list = []
        self._memo: Dict = {}
        #: frame-index values: the free labels' assignment of this run,
        #: overridden by the binders of enclosing IndexedSums
        self.indices: Dict[str, int] = dict(indices or {})
        self._labels: Dict = {}

    # ---- entry points ------------------------------------------------- #

    def value(self, expr, path=()):
        # index bindings are part of the key — but only those of the labels
        # occurring free in ``expr``: a dummy-independent subexpression of
        # a Σ body is evaluated once, not once per index value
        if self.indices:
            labs = free_index_labels(expr, self._labels)
            key = ("v", expr, tuple(sorted((k, v) for k, v in self.indices.items() if k in labs)))
        else:
            key = ("v", expr)
        hit = self._memo.get(key)
        if hit is not None:
            return hit
        if self.deadline is not None and time.monotonic() > self.deadline:
            raise Budget("time budget exhausted")
        fn = realizer_for(type(expr))
        if fn is None:
            raise Unsupported(type(expr).__name__, path)
        try:
            out = fn(expr, self, path)
        except Unsupported as exc:
            if not exc.path and path:
                exc.path = tuple(path)
            raise
        self._memo[key] = out
        return out

    def op(self, expr, path=()) -> OpV:
        """Realize ``expr`` in OPERATOR position (an Act's operator)."""
        if isinstance(expr, Product):
            ops = [self.op(c, path + (i,)) for i, c in enumerate(expr.children)]
            return compose(ops)
        if isinstance(expr, Sum):
            return op_sum([self.op(c, path + (i,)) for i, c in enumerate(expr.children)], self.R)
        if isinstance(expr, Neg):
            return op_scale(self.op(expr.arg, path + (0,)), -1, self.R)
        return to_op(self.value(expr, path), self.R, path)

    def degree(self, deg, path=()) -> int:
        k = deg.as_int()
        if k is not None:
            return k
        assign = self.model.degrees
        total = 0
        for mono, c in deg.terms:
            term = c
            for name, e in mono:
                if name not in assign:
                    raise Unsupported("symbolic-degree", path, f"unassigned degree variable {name}")
                term *= assign[name] ** e
            total += term
        return total

    def structure_pi(self, name: str, path) -> MultiV:
        pi = self.model.structure_bivector(name)
        return pi


# --------------------------------------------------------------------- #
# Value algebra                                                          #
# --------------------------------------------------------------------- #


def is_scalar(v) -> bool:
    return not isinstance(v, (VecV, FormV, MultiV, OpV, SecV, EFormV))


def is_zero(v) -> bool:
    if is_scalar(v):
        return v.is_zero
    return v.is_zero()


def kind(v) -> str:
    if is_scalar(v):
        return "function"
    return {VecV: "vector", FormV: "form", MultiV: "multivector", OpV: "operator", SecV: "section",
            EFormV: "E-form"}[type(v)]


def norm(v, R):
    """Canonical value: degree-0 forms/multivectors are scalars, a
    homogeneous 1-vector is a :class:`VecV`, an empty dict is 0."""
    if isinstance(v, (FormV, MultiV)):
        if not v.d:
            return R.zero()
        degs = v.degrees()
        if degs == {0}:
            return v.d[()]
        if isinstance(v, MultiV) and degs == {1}:
            return VecV(V.oneform_vec(R, v.d))
    return v


def as_multi(v, R, path=()) -> dict:
    if isinstance(v, MultiV):
        return v.d
    if isinstance(v, VecV):
        return {(i,): c for i, c in enumerate(v.c) if not c.is_zero}
    if is_scalar(v):
        return {} if v.is_zero else {(): v}
    raise Unsupported(f"expected-multivector:{kind(v)}", path)


def as_form(v, R, path=()) -> dict:
    if isinstance(v, FormV):
        return v.d
    if is_scalar(v):
        return {} if v.is_zero else {(): v}
    raise Unsupported(f"expected-form:{kind(v)}", path)


def as_vec(v, R, path=()) -> Tuple:
    if isinstance(v, VecV):
        return v.c
    if isinstance(v, MultiV) and v.degrees() <= {1}:
        return V.oneform_vec(R, v.d)
    if is_scalar(v) and v.is_zero:
        return tuple(R.zero() for _ in range(R.n))
    raise Unsupported(f"expected-vector:{kind(v)}", path)


def as_oneform(v, R, path=()) -> Tuple:
    if isinstance(v, FormV) and v.degrees() <= {1}:
        return V.oneform_vec(R, v.d)
    if is_scalar(v) and v.is_zero:
        return tuple(R.zero() for _ in range(R.n))
    raise Unsupported(f"expected-1-form:{kind(v)}", path)


def scale(c, v, R):
    """``c·v`` for a scalar ``c``."""
    if isinstance(v, VecV):
        return VecV(tuple(c * x for x in v.c))
    if isinstance(v, FormV):
        return FormV(V.dscale(v.d, c))
    if isinstance(v, MultiV):
        return MultiV(V.dscale(v.d, c))
    if isinstance(v, OpV):
        return OpV(lambda a, v=v: scale(c, v(a), R), v.degree, f"{c.as_expr()}·{v.label}")
    if isinstance(v, SecV):
        return SecV(v.b, V.sec_scale(c, v.c))
    if isinstance(v, EFormV):
        return EFormV(v.b, v.deg, lambda args, v=v: c * v.fn(args), alt=v.alt, ctx=v.ctx, label=f"{c.as_expr()}·{v.label}")
    return c * v


def add(vals, R, path=()):
    vals = [v for v in vals if not (not isinstance(v, OpV) and is_zero(v))]
    if not vals:
        return R.zero()
    if any(isinstance(v, OpV) for v in vals):
        return op_sum([to_op(v, R, path) for v in vals], R)
    if all(is_scalar(v) for v in vals):
        out = R.zero()
        for v in vals:
            out = out + v
        return out
    if all(isinstance(v, VecV) for v in vals):
        return VecV(tuple(sum((v.c[i] for v in vals[1:]), vals[0].c[i]) for i in range(R.n)))
    if any(isinstance(v, (SecV, EFormV)) for v in vals):
        return _add_e(vals, R, path)
    has_form = any(isinstance(v, FormV) for v in vals)
    has_multi = any(isinstance(v, (MultiV, VecV)) for v in vals)
    if has_form and has_multi:
        raise Unsupported("Sum[form+multivector]", path)
    if has_form:
        return norm(FormV(V.dadd(*(as_form(v, R, path) for v in vals))), R)
    return norm(MultiV(V.dadd(*(as_multi(v, R, path) for v in vals))), R)


# --------------------------------------------------------------------- #
# Operators                                                              #
# --------------------------------------------------------------------- #


def _add_e(vals, R, path):
    """Sums of sections of one bundle, or of E-forms of one bundle and
    degree (an inhomogeneous E-form sum has no model value)."""
    if all(isinstance(v, SecV) for v in vals):
        if len({v.b for v in vals}) != 1:
            raise Unsupported("Sum[sections of different bundles]", path)
        out = vals[0].c
        for v in vals[1:]:
            out = V.sec_add(R, out, v.c)
        return SecV(vals[0].b, out)
    if all(isinstance(v, EFormV) for v in vals):
        if len({(v.b, v.deg) for v in vals}) != 1:
            raise Unsupported("Sum[inhomogeneous E-forms]", path)
        fns = [v.fn for v in vals]
        return EFormV(vals[0].b, vals[0].deg, lambda args: sum((f(args) for f in fns[1:]), fns[0](args)),
                      alt=all(v.alt for v in vals), ctx=vals[0].ctx, label="+".join(v.label for v in vals))
    raise Unsupported("Sum[" + "+".join(sorted({kind(v) for v in vals})) + "]", path)


def to_op(v, R, path=()) -> OpV:
    if isinstance(v, OpV):
        return v
    if isinstance(v, SecV):
        # a section of E ≠ TM does not act on functions (only ρ(u) does;
        # AlgebroidBracket.section_value)
        raise Unsupported("operator-from-section", path)
    if is_scalar(v):
        return OpV(lambda a, f=v: scale(f, a, R), 0, f"mult({v.as_expr()})")
    if isinstance(v, VecV):
        X = v.c

        def deriv(a, X=X):
            if is_scalar(a):
                return V.vf_apply(R, X, a)
            raise DomainError(f"Act[vector field on {kind(a)}]", path)

        return OpV(deriv, 0, "vector field")
    raise Unsupported(f"operator-from-{kind(v)}", path)


def compose(ops) -> OpV:
    if len(ops) == 1:
        return ops[0]
    degs = [o.degree for o in ops]
    deg = None if any(d is None for d in degs) else sum(degs)

    def fn(a, ops=ops):
        for o in reversed(ops):
            a = o(a)
        return a

    return OpV(fn, deg, "∘".join(o.label for o in ops))


def op_sum(ops, R) -> OpV:
    degs = {o.degree for o in ops}
    deg = degs.pop() if len(degs) == 1 else None

    def fn(a, ops=ops):
        # summand by summand: an undefined summand makes the sum undefined
        # only if every defined summand vanishes there; otherwise the sum
        # is ill-typed on this argument and the oracle says so (never a
        # silent skip of the undefined part — review: X = X + 5ι_Yι_Z)
        outs, undefined = [], False
        for o in ops:
            try:
                outs.append(o(a))
            except DomainError:
                undefined = True
        if undefined:
            if all(not isinstance(v, OpV) and is_zero(v) for v in outs):
                raise DomainError(f"operator-sum[undefined on {kind(a)}]")
            raise Unsupported(f"operator-sum[mixed domain on {kind(a)}]")
        return add(outs, R)

    return OpV(fn, deg, "+".join(o.label for o in ops))


def op_scale(o: OpV, c, R) -> OpV:
    return OpV(lambda a, o=o: scale(R.const(c), o(a), R), o.degree, f"{c}·{o.label}")


# --------------------------------------------------------------------- #
# Realizers: core                                                        #
# --------------------------------------------------------------------- #


@register(Integer)
def _integer(e, env, path):
    return env.R.const(e.value)


@register(Rational)
def _rational(e, env, path):
    from sympy import Rational as Q

    return env.R.const(Q(e.p, e.q))


_LEVEL = {"exact": 0, "class": 1, "predicate": 2}


def _declared_constant(e, env) -> bool:
    """The Scalar contract restated INDEPENDENTLY of the engine (chef
    decision, gate 5: the oracle must not import the engine's
    predicate, or a wrong "constant" there would be modelled here too
    and the DISAGREE masked). From the registry's raw declaration data
    (:meth:`~jacopy.core.registry.PropertyRegistry.lookup`), for an
    atom the caller already knows to be of function kind (a Symbol, a
    degree-0 Form / PVector):

    * a ``Scalar`` declared at any level (exact / class / predicate);
    * SHADOWED — not a constant — by a strictly more specific
      ``Graded`` (any degree) / ``NonCommuting`` / ``AntiCommuting``;
    * not a constant when an effective ``NonCommuting`` /
      ``AntiCommuting`` exists, or the effective ``Graded`` degree is
      not the constant ``0`` (a symbolic degree certifies nothing).

    ``tests/test_audit_0b00e1b_p1_core_tur2.py`` locks this against the
    engine's predicate differentially over every declaration
    combination. The registry's visibility filters are deliberately
    NOT applied (raw data, as the engine's clash check)."""
    reg = env.registry
    if reg is None:
        return False
    scalar, s_level = reg.lookup(e, Scalar)
    if scalar is None:
        return False
    rank = _LEVEL[s_level]
    graded, g_level = reg.lookup(e, Graded)
    nc, nc_level = reg.lookup(e, NonCommuting)
    ac, ac_level = reg.lookup(e, AntiCommuting)
    for other, level in ((graded, g_level), (nc, nc_level), (ac, ac_level)):
        if other is not None and _LEVEL[level] < rank:
            return False  # shadowed: a graded element, not a constant
    if nc is not None or ac is not None:
        return False
    return graded is None or graded.degree.as_int() == 0


@register(Symbol)
def _symbol(e, env, path):
    """Scalar contract (SPEC §7): a ``Scalar`` symbol (any declaration level) is a
    CONSTANT; a ``Graded(0)`` symbol is a function (``functions(...)``);
    anything else (undeclared, graded ≠ 0) has no model."""
    reg = env.registry
    if reg is None:
        raise Unsupported("Symbol[no-registry]", path)
    if _declared_constant(e, env):
        return env.model.constant(("Symbol", e.name))
    g = reg.peek(e, Graded)
    if g is not None:
        if g.degree.as_int() == 0:
            return env.model.function(("Symbol", e.name))
        raise Unsupported("Symbol[graded]", path)
    raise Unsupported("Symbol[undeclared]", path)


@register(Neg)
def _neg(e, env, path):
    v = env.value(e.arg, path + (0,))
    if isinstance(v, OpV):
        return op_scale(v, -1, env.R)
    return scale(env.R.const(-1), v, env.R)


@register(Sum)
def _sum(e, env, path):
    return add([env.value(c, path + (i,)) for i, c in enumerate(e.children)], env.R, path)


@register(Power)
def _power(e, env, path):
    if not isinstance(e.exp, Integer) or e.exp.value < 0:
        raise Unsupported("Power[non-natural exponent]", path)
    b = env.value(e.base, path + (0,))
    if not is_scalar(b):
        raise Unsupported(f"Power[{kind(b)}]", path)
    return b ** e.exp.value


@register(Product)
def _product(e, env, path):
    R = env.R
    vals = [env.value(c, path + (i,)) for i, c in enumerate(e.children)]
    opish = [isinstance(v, (OpV, VecV)) for v in vals]
    if not any(opish):
        scal = [v for v in vals if is_scalar(v)]
        rest = [v for v in vals if not is_scalar(v)]
        c = R.one()
        for s in scal:
            c = c * s
        if not rest:
            return c
        if len(rest) == 1:
            return norm(scale(c, rest[0], R), R)
        raise Unsupported("Product[non-scalar·non-scalar]", path)
    if any(not is_scalar(v) and not o for v, o in zip(vals, opish)):
        raise Unsupported("Product[operator·form/multivector]", path)
    first = opish.index(True)
    ambiguous = any(is_scalar(v) and not v.is_ground for v in vals[first + 1:])
    if ambiguous:
        env.ambiguous.append(path)
    if ambiguous and env.mode == "operator":
        return compose([to_op(v, R, path) for v in vals])
    # value reading: scalars commute out; operator-capable factors compose
    c = R.one()
    for v in vals:
        if is_scalar(v):
            c = c * v
    ops = [v for v in vals if not is_scalar(v)]
    if len(ops) == 1:
        return scale(c, ops[0], R)
    return scale(c, compose([to_op(v, R, path) for v in ops]), R)


@register(Act)
def _act(e, env, path):
    o = env.op(e.op, path + (0,))
    a = env.value(e.arg, path + (1,))
    try:
        out = o(a)
    except Unsupported as exc:
        if not exc.path:
            exc.path = path
        raise
    return norm(out, env.R)


@register(Commutator)
def _commutator(e, env, path):
    """``[A, B] = A∘B − (−1)^{|A||B|} B∘A`` (algebra/commutator.py)."""
    A = env.op(e.a, path + (0,))
    B = env.op(e.b, path + (1,))
    if A.degree is None or B.degree is None:
        raise Unsupported("Commutator[undetermined degree]", path)
    s = -1 if (A.degree * B.degree) % 2 == 0 else 1
    R = env.R

    def fn(a):
        return add([A(B(a)), scale(R.const(s), B(A(a)), R)], R, path)

    return OpV(fn, A.degree + B.degree, f"[{A.label},{B.label}]")


@register(Wedge)
def _wedge(e, env, path):
    R = env.R
    vals = [env.value(c, path + (i,)) for i, c in enumerate(e.children)]
    if any(isinstance(v, OpV) for v in vals):
        raise Unsupported("Wedge[operator]", path)
    if any(isinstance(v, (EFormV, SecV)) for v in vals):
        return _e_wedge(vals, env, path)
    has_form = any(isinstance(v, FormV) for v in vals)
    has_multi = any(isinstance(v, (MultiV, VecV)) for v in vals)
    if has_form and has_multi:
        raise Unsupported("Wedge[form∧multivector]", path)
    conv = as_form if has_form else as_multi
    out = {(): R.one()}
    for v in vals:
        out = V.dwedge(out, conv(v, R, path))
    return norm((FormV if has_form else MultiV)(out), R)


@register(Pairing)
def _pairing(e, env, path):
    """``⟨α, X⟩`` — stored symmetrically by the library (``core/pairing.py``;
    ``TildeInteriorActDefinition`` builds ``Pairing(X, α)``): the form
    side is recognised by kind."""
    R = env.R
    a = env.value(e.alpha, path + (0,))
    b = env.value(e.X, path + (1,))
    if is_zero(a) or is_zero(b):
        return R.zero()
    if isinstance(a, SecV) and isinstance(b, EFormV):
        a, b = b, a
    if isinstance(a, EFormV) or isinstance(b, SecV):
        # ⟨α, u⟩ = α(u) for an E-1-form and a section of the same bundle
        if not (isinstance(a, EFormV) and isinstance(b, SecV) and a.b == b.b and a.deg == 1):
            raise Unsupported(f"Pairing[{kind(a)}, {kind(b)}]", path)
        return a([b.c])
    if isinstance(a, (VecV, MultiV)) and isinstance(b, FormV):
        a, b = b, a
    alpha = as_oneform(a, R, path)
    X = as_vec(b, R, path)
    out = R.zero()
    for i in range(R.n):
        out = out + alpha[i] * X[i]
    return out


@register(MultiEval)
def _multi_eval(e, env, path):
    """``ω(X_1, …, X_p)``. The ``alternating`` flag is a CLAIM about the
    head (``core/multi_eval.py``), not a different evaluation: both flags
    evaluate the head multilinearly in the given slot order. A wrong
    claim (an alternation shortcut on a non-alternating Palais ``d_E``)
    is then visible as a value mismatch (audit P0-4)."""
    R = env.R
    head = env.value(e.head, path + (0,))
    args = [env.value(a, path + (i + 1,)) for i, a in enumerate(e.args)]
    if is_zero(head) or any(is_zero(a) for a in args):
        return R.zero()
    p = len(args)
    if isinstance(head, EFormV):
        if head.deg != p or e.slot_kind != "vector":
            raise Unsupported("MultiEval[E-form arity]", path)
        return head([as_sec(a, head.b, path) for a in args])
    if isinstance(head, FormV):
        if head.degrees() != {p}:
            raise Unsupported("MultiEval[arity]", path)
        return V.det_eval(R, head.d, [as_vec(a, R, path) for a in args])
    if isinstance(head, (MultiV, VecV)):
        d = as_multi(head, R, path)
        if {len(k) for k in d} != {p}:
            raise Unsupported("MultiEval[arity]", path)
        return V.det_eval(R, d, [as_oneform(a, R, path) for a in args])
    raise Unsupported(f"MultiEval[head {kind(head)}]", path)


@register(PartialEval)
def _partial_eval(e, env, path):
    """``T(a₁, ·, a₃, ·)``: the open map's components on increasing basis
    tuples, the fixed slots kept in place (partial_eval.py)."""
    from itertools import combinations

    R = env.R
    if not e.alternating:
        raise Unsupported("PartialEval[non-alternating]", path)
    head = env.value(e.head, path + (0,))
    fixed = {pos: env.value(v, path + (k + 1,)) for k, (pos, v) in enumerate(e.fixed)}
    covector = e.slot_kind == "covector"
    if e.slot_kind not in ("vector", "covector"):
        raise Unsupported("PartialEval[mixed]", path)
    if is_zero(head):
        return R.zero()
    d = as_multi(head, R, path) if covector else as_form(head, R, path)
    if {len(k) for k in d} != {e.arity}:
        raise Unsupported("PartialEval[arity]", path)
    conv = as_oneform if covector else as_vec
    fixed_c = {pos: conv(v, R, path) for pos, v in fixed.items()}
    m = e.n_open
    opens = e.open_positions
    out = {}
    for J in combinations(range(R.n), m):
        args = [None] * e.arity
        for pos, c in fixed_c.items():
            args[pos] = c
        for k, pos in enumerate(opens):
            args[pos] = V.basis(R, J[k])
        val = V.det_eval(R, d, args)
        if not val.is_zero:
            out[J] = val
    return norm((MultiV if covector else FormV)(out), R)


# --------------------------------------------------------------------- #
# Realizers: tangent atoms                                               #
# --------------------------------------------------------------------- #


def _check_tm(e, path):
    if getattr(e, "bundle", TM) != TM:
        raise Unsupported(f"{type(e).__name__}[bundle≠TM]", path)


def _is_tm(e) -> bool:
    """The symbolic TM (a TM with a fixed dimension is not modeled)."""
    return getattr(e, "bundle", TM) == TM


@register(VectorField)
def _vector_field(e, env, path):
    if e.degree.as_int() != 0:
        raise Unsupported("VectorField[graded]", path)
    if not _is_tm(e):
        # a section of an algebroid / vector bundle E (context.py)
        return _section_atom(e, env, path)
    return env.model.vector(("VectorField", e.name))


@register(Form)
def _form(e, env, path):
    p = env.degree(e.degree, path)
    if p < 0:
        raise Unsupported("Form[negative degree]", path)
    if p == 0 and _declared_constant(e, env):
        return env.model.constant(("Form", e.name))
    if not _is_tm(e):
        return _eform_atom(e, env, p, path)
    return norm(env.model.form(e.name, p), env.R)


@register(PVector)
def _pvector(e, env, path):
    _check_tm(e, path)
    p = env.degree(e.degree, path)
    if p < 0:
        raise Unsupported("PVector[negative degree]", path)
    if p == 0 and _declared_constant(e, env):
        return env.model.constant(("PVector", e.name))
    return norm(env.model.multivector(e.name, p), env.R)


@register(LieBracketVF)
def _lie_bracket_vf(e, env, path):
    R = env.R
    X = as_vec(env.value(e.X, path + ("X",)), R, path)
    Y = as_vec(env.value(e.Y, path + ("Y",)), R, path)
    return VecV(V.vf_bracket(R, X, Y))


@register(NambuSharpVF)
def _nambu_sharp(e, env, path):
    R = env.R
    Pi = as_multi(env.value(e.pi, path + ("pi",)), R, path)
    p = env.degree(e.pi.degree, path) - 1
    omega = as_form(env.value(e.omega, path + ("omega",)), R, path)
    return VecV(V.nambu_sharp(R, Pi, omega, p))


@register(SharpVF)
def _sharp_vf(e, env, path):
    R = env.R
    pi = as_multi(env.value(e.pi, path + ("pi",)), R, path)
    alpha = as_oneform(env.value(e.alpha, path + ("alpha",)), R, path)
    return VecV(V.sharp(R, pi, alpha))


@register(HamiltonianVF)
def _hamiltonian_vf(e, env, path):
    """``X_f(g) = {f, g} = π(df, dg)`` (poisson/core.py) ⇒ ``X_f = π♯(df)``."""
    R = env.R
    pi = as_multi(env.value(e.pi, path + ("pi",)), R, path)
    f = env.value(e.f, path + ("f",))
    if not is_scalar(f):
        raise Unsupported("HamiltonianVF[non-function]", path)
    df = V.oneform_vec(R, V.d_form(R, {(): f} if not f.is_zero else {}))
    return VecV(V.sharp(R, pi, df))


@register(PoissonBracketValue)
def _poisson_bracket(e, env, path):
    """``{f, g} := π(df, dg)``."""
    R = env.R
    pi = as_multi(env.value(e.pi, path + ("pi",)), R, path)
    f, g = env.value(e.f, path + ("f",)), env.value(e.g, path + ("g",))
    if not (is_scalar(f) and is_scalar(g)):
        raise Unsupported("PoissonBracketValue[non-function]", path)
    df = V.oneform_vec(R, V.d_form(R, {(): f} if not f.is_zero else {}))
    dg = V.oneform_vec(R, V.d_form(R, {(): g} if not g.is_zero else {}))
    return V.det_eval(R, pi, [df, dg])


@register(KoszulBracket)
def _koszul(e, env, path):
    R = env.R
    pi_e = e.pi
    if not isinstance(pi_e, PVector):
        raise Unsupported("KoszulBracket[pi]", path)
    pi = as_multi(env.value(pi_e, path + ("pi",)), R, path)
    a = as_oneform(env.value(e.alpha, path + ("alpha",)), R, path)
    b = as_oneform(env.value(e.beta, path + ("beta",)), R, path)
    return norm(FormV({(i,): c for i, c in enumerate(V.koszul(R, pi, a, b)) if not c.is_zero}), R)


@register(BracketApply)
def _bracket_apply(e, env, path):
    b = e.bracket
    if not (type(b).__name__ == "SchoutenBracket" and type(b).__module__ == "jacopy.central.tangent.schouten"):
        raise Unsupported(f"BracketApply[{type(b).__name__}]", path)
    R = env.R
    P = as_multi(env.value(e.a, path + (0,)), R, path)
    Q = as_multi(env.value(e.b, path + (1,)), R, path)
    return norm(MultiV(V.schouten(R, P, Q)), R)


# --------------------------------------------------------------------- #
# Realizers: operators                                                   #
# --------------------------------------------------------------------- #


def _structure_pi(env, calc, path) -> dict:
    name = calculus_structure(calc)
    pi = env.structure_pi(name, path)
    if pi.degrees() - {2}:
        raise Unsupported("structure[not a bivector]", path)
    return pi.d


@register(ExteriorDerivative)
def _exterior_derivative(e, env, path):
    R = env.R
    calc = e.calculus_name
    if calc == CARTAN_TM_NAME:
        def d(a):
            if isinstance(a, (VecV, MultiV, OpV)):
                raise DomainError(f"d[on {kind(a)}]", path)
            return norm(FormV(V.d_form(R, as_form(a, R, path))), R)

        return OpV(d, 1, "d")
    if calculus_structure(calc) is not None:
        pi = _structure_pi(env, calc, path)

        def dt(a):
            if isinstance(a, (FormV, OpV)):
                raise DomainError(f"d̃[on {kind(a)}]", path)
            return norm(MultiV(V.tilde_d(R, pi, as_multi(a, R, path))), R)

        return OpV(dt, 1, "d̃")
    alg = algebroid_of_calculus(calc)
    if alg is not None:
        return _e_exterior_derivative(alg, env, path)
    raise Unsupported(f"ExteriorDerivative[{_calculus_kind(calc)}]", path)


@register(LieDerivative)
def _lie_derivative(e, env, path):
    R = env.R
    calc = e.calculus_name
    if calc == CARTAN_TM_NAME:
        X = as_vec(env.value(e.vector, path + ("X",)), R, path)

        def L(a):
            if is_scalar(a):
                return V.vf_apply(R, X, a)
            if isinstance(a, VecV):
                return VecV(V.vf_bracket(R, X, a.c))
            if isinstance(a, FormV):
                return norm(FormV(V.lie_form(R, X, a.d)), R)
            if isinstance(a, MultiV):
                return norm(MultiV(V.lie_multi(R, X, a.d)), R)
            raise DomainError(f"L_X[on {kind(a)}]", path)

        return OpV(L, 0, "L_X")
    if calculus_structure(calc) is not None:
        pi = _structure_pi(env, calc, path)
        alpha = as_oneform(env.value(e.vector, path + ("alpha",)), R, path)

        def Lt(a):
            if isinstance(a, (FormV, OpV)):
                raise DomainError(f"L̃[on {kind(a)}]", path)
            return norm(MultiV(V.tilde_lie(R, pi, alpha, as_multi(a, R, path))), R)

        return OpV(Lt, 0, "L̃_α")
    alg = algebroid_of_calculus(calc)
    if alg is not None:
        return _e_lie_derivative(alg, e, env, path)
    raise Unsupported(f"LieDerivative[{_calculus_kind(calc)}]", path)


@register(Interior)
def _interior(e, env, path):
    R = env.R
    Xv = env.value(e.vector, path + ("X",))
    if isinstance(Xv, SecV):
        return _e_interior(Xv, env, path)
    X = as_vec(Xv, R, path)

    def i(a):
        if is_scalar(a):
            return R.zero()
        if isinstance(a, FormV):
            return norm(FormV(V.dinterior(X, a.d)), R)
        raise DomainError(f"ι_X[on {kind(a)}]", path)

    return OpV(i, -1, "ι_X")


def algebroid_of_calculus(name: str) -> Optional[str]:
    """``Cartan-<E>`` (central/algebroid/calculus.py) → ``E``."""
    if name != CARTAN_TM_NAME and name.startswith("Cartan-"):
        return name[len("Cartan-"):]
    return None


# the algebroid / frame realizers register themselves on import; their
# helpers are looked up at CALL time (no circular-import order issue)
def _e(name):
    from jacopy.oracle import realize_e

    return getattr(realize_e, name)


def _e_exterior_derivative(*a):
    return _e("_e_exterior_derivative")(*a)


def _e_interior(*a):
    return _e("_e_interior")(*a)


def _e_lie_derivative(*a):
    return _e("_e_lie_derivative")(*a)


def _e_wedge(*a):
    return _e("_e_wedge")(*a)


def _eform_atom(*a):
    return _e("_eform_atom")(*a)


def _section_atom(*a):
    return _e("_section_atom")(*a)


def as_sec(*a):
    return _e("as_sec")(*a)


def free_index_labels(*a):
    return _e("free_index_labels")(*a)


from jacopy.oracle import realize_e as _realize_e  # noqa: E402,F401


@register(TildeInterior)
def _tilde_interior(e, env, path):
    """``(ι̃_α π)(ω₁…) = π(α, ω₁…)``; ``ι̃_α X = ⟨α, X⟩``; ``ι̃_α f = 0``."""
    R = env.R
    alpha = as_oneform(env.value(e.form, path + ("alpha",)), R, path)

    def it(a):
        if is_scalar(a):
            return R.zero()
        if isinstance(a, (VecV, MultiV)):
            return norm(MultiV(V.dinterior(alpha, as_multi(a, R, path))), R)
        raise DomainError(f"ι̃_α[on {kind(a)}]", path)

    return OpV(it, -1, "ι̃_α")


@register(MultivectorInterior)
def _multivector_interior(e, env, path):
    """``ι_{X₁∧…∧X_p} = ι_{X_p} ∘ ⋯ ∘ ι_{X₁}`` (multivector_interior.py),
    extended C∞-linearly over the components ``P_K ∂_{K1}∧…∧∂_{Kp}``."""
    R = env.R
    P = as_multi(env.value(e.multivector, path + ("P",)), R, path)
    degs = {len(k) for k in P}
    if len(degs) > 1:
        raise Unsupported("MultivectorInterior[inhomogeneous]", path)
    p = degs.pop() if degs else 0

    def ip(a):
        if is_scalar(a):
            if p == 0:
                return scale(P.get((), R.zero()), a, R)
            return R.zero()
        if not isinstance(a, FormV):
            raise DomainError(f"ι_P[on {kind(a)}]", path)
        out = {}
        for K, c in P.items():
            term = a.d
            for k in K:
                term = V.dinterior(V.basis(R, k), term)
            out = V.dadd(out, V.dscale(term, c))
        return norm(FormV(out), R)

    return OpV(ip, -p, "ι_P")
