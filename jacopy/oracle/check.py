"""``check_equal`` / ``check_chain``: evaluate both sides of a closed
equation in random concrete models and compare.

Model selection:

* D-models: ``R^n`` with ``n = max(3, D + 1)``, ``D`` an upper bound of
  the exterior / multivector degree of EVERY subnode (operator results
  and what an operator can lower included), capped at ``MAX_DIM = 6``
  (beyond: UNSUPPORTED(dimension) unless already refuted). Random sparse
  cubic polynomial data.
* A structure bivector (named by a ``tilde-π`` / ``lichnerowicz-π``
  calculus or a Poisson node) is POISSON when its structure declares
  ``poisson`` (or ``fundamental-identity``), GENERIC when the owners are
  known and do not declare it, and UNSUPPORTED(owners-unknown) when no
  owner information is available.
* ASSUMPTION_LEAK (the ``poisson`` declaration only): every declared
  Poisson π occurring in the equation (also as a plain PVector) whose
  declaration the proof record does not use must also hold in a
  verified non-Poisson counter-model; an unknown record or a failing
  counter-model sets ``leak_unchecked``.
* Symbolic degrees: the full product of ``0..k+2`` per variable (``k`` =
  degree-lowering operations on one side; both parities), budget
  ``MAX_ASSIGNMENTS``.
* Operators are compared on the test basis of every form / multivector
  degree ``0..n`` (domain rule in :func:`values_equal`).
* Determinism: model seed ``sha256(base_seed, goal, index)``;
  a DISAGREE is re-run automatically with a second base seed.
"""

from __future__ import annotations

import hashlib
import itertools
import time
from typing import Iterable, Optional, Tuple

from jacopy.central.calculus.bracket_calculus import ExteriorDerivative, LieDerivative
from jacopy.central.objects.form import Form
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.vector_field import VectorField
from jacopy.algebra.commutator import Commutator
from jacopy.algebra.derivation import Act
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.brackets.base import BracketApply
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.multivector_interior import MultivectorInterior
from jacopy.central.objects.partial_eval import PartialEval
from jacopy.central.objects.tilde_interior import TildeInterior
from jacopy.core.expr import Expr, Neg, Product, Sum, Symbol
from jacopy.core.wedge import Wedge
from jacopy.packages.poisson.core import HamiltonianVF, PoissonBracketValue, SharpVF
from jacopy.packages.poisson.koszul_forms import KoszulBracket
from jacopy.packages.poisson.nambu import NambuSharpVF

from jacopy.central.algebroid.context import CoboundaryForm
from jacopy.oracle import realize as RZ
from jacopy.oracle import select as SEL
from jacopy.oracle.models.algebroid import POOL, AlgebroidModel, build_structure
from jacopy.oracle.report import (
    AGREE,
    AMBIGUOUS,
    ASSUMPTION_LEAK,
    DISAGREE,
    UNSUPPORTED,
    ChainReport,
    OracleReport,
    Witness,
)
from jacopy.oracle.values import Budget, DomainError, OpV, Unsupported

POISSON_KEYS = ("poisson", "fundamental-identity")
SECOND_SEED_OFFSET = 1_000_003
MAX_NODES = 20_000
#: largest model dimension; an equation needing more is UNSUPPORTED(dimension)
MAX_DIM = 6
#: largest number of symbolic-degree assignments (full product)
MAX_ASSIGNMENTS = 64


# --------------------------------------------------------------------- #
# Tree scan                                                              #
# --------------------------------------------------------------------- #


def _subexprs(e):
    yield from e.children
    for s in getattr(e, "rewritable_slots", None) or ():
        if isinstance(s, Expr):
            yield s
    for attr in ("pi", "form", "vector", "multivector"):
        try:
            s = getattr(e, attr, None)
        except Exception:  # noqa: BLE001 — a property may refuse
            s = None
        if isinstance(s, Expr):
            yield s


_STRUCTURE_USERS = (NambuSharpVF, SharpVF, HamiltonianVF, PoissonBracketValue, KoszulBracket)


def scan(*exprs):
    """``(structure bivector names, higher Nambu names, degree variables,
    atom names, number of degree-lowering operations, node count)``. A
    bivector is a STRUCTURE bivector when a tilde/Lichnerowicz calculus or
    a Poisson node (sharp, Hamiltonian, bracket) refers to it."""
    names, nambu, dvars, atoms = set(), set(), set(), set()
    lowering, count = 0, 0
    seen = set()
    stack = list(exprs)
    while stack:
        e = stack.pop()
        count += 1
        if count > MAX_NODES:
            break
        key = id(e)
        if key in seen:
            continue
        seen.add(key)
        if isinstance(e, (ExteriorDerivative, LieDerivative)):
            n = RZ.calculus_structure(e.calculus_name)
            if n is not None:
                names.add(n)
        if isinstance(e, _STRUCTURE_USERS):
            pi = getattr(e, "pi", None)
            if isinstance(pi, PVector):
                k = pi.degree.as_int()
                (names if k == 2 else nambu).add(pi._repr_inner())
        if isinstance(e, (Form, PVector, VectorField, Symbol)):
            atoms.add(e._repr_inner())
        if isinstance(e, (Form, PVector)) and e.degree.as_int() is None:
            dvars |= set(e.degree.variables())
        stack.extend(_subexprs(e))
    lowering = max(_lowering(x) for x in exprs)
    return names, nambu, dvars, atoms, lowering, count


def _lowering(expr) -> int:
    """Number of degree-lowering operations in ONE side (ι, ι̃ count 1,
    ι_P counts deg P, a partial evaluation its fixed slots)."""
    total, visits, stack = 0, 0, [expr]
    while stack and visits < MAX_NODES:  # shared subtrees count each time
        e = stack.pop()
        visits += 1
        if isinstance(e, (Interior, TildeInterior)):
            total += 1
        elif isinstance(e, MultivectorInterior):
            total += max(1, max_exterior_degree((e.multivector,), {}))
        elif isinstance(e, PartialEval):
            total += len(e.fixed)
        stack.extend(_subexprs(e))
    return total


#: Owner classes whose declared axioms the random models understand. Any other
#: owner whose names occur in the equation constrains the atoms in ways
#: the random model does not reproduce (e.g. a symplectic ω with π = ω⁻¹)
#: → UNSUPPORTED instead of a false DISAGREE.
_MODELED_OWNERS = ("PoissonStructure", "NambuPoissonStructure", "Algebroid")


def _owner_obstruction(owners, atoms, nambu):
    """The UNSUPPORTED kind forced by the owners, or ``None``."""
    if owners is None:
        return "NambuPoisson[owners unknown]" if nambu else None
    if isinstance(owners, dict):
        owners = list(owners.values())
    for o in owners:
        cls = type(o).__name__
        ids = set()
        for attr in ("pi", "omega"):
            a = getattr(o, attr, None)
            if a is not None and hasattr(a, "_repr_inner"):
                ids.add(a._repr_inner())
        nm = getattr(o, "name", None)
        if isinstance(nm, str):
            ids.add(nm)
        if not (ids & atoms):
            continue
        if cls not in _MODELED_OWNERS:
            return f"owner[{cls}]"
        if cls == "NambuPoissonStructure":
            deg = o.pi.degree.as_int()
            if deg != 2 and "fundamental-identity" in (getattr(o, "declarations", None) or ()):
                return "NambuPoisson[fundamental-identity]"
    return None


def _structure_info(owners):
    """``{bivector name: declares Poisson?}`` from owner structures."""
    if owners is None:
        return None
    if isinstance(owners, dict):
        owners = list(owners.values())
    out = {}
    for o in owners:
        pi = getattr(o, "pi", None)
        if pi is None or not hasattr(pi, "_repr_inner"):
            continue
        deg = getattr(pi, "degree", None)
        if deg is None or deg.as_int() != 2:
            continue
        decl = getattr(o, "declarations", None) or ()
        name = pi._repr_inner()
        out[name] = out.get(name, False) or any(k in decl for k in POISSON_KEYS)
    return out


def poisson_requires(requires=None, chain=None):
    """Bivector names whose Poisson declaration the proof USED, or
    ``None`` when the record cannot tell (legacy / textual entries)."""

    def owner_name(o):
        pi = getattr(o, "pi", None)
        decl = getattr(o, "declarations", None) or ()
        if pi is not None and hasattr(pi, "_repr_inner") and any(k in decl for k in POISSON_KEYS):
            return pi._repr_inner()
        return None

    if requires is not None:
        used = set()
        for a in requires:
            k = getattr(a, "kind", None)
            if k in ("legacy", "textual"):
                return None
            if k == "declared":
                n = owner_name(getattr(a, "owner", None))
                if n:
                    used.add(n)
        return used
    if chain is None:
        return None
    used = set()

    def visit(steps):
        for s in steps:
            role = getattr(s, "role", None)
            tag = getattr(s, "provenance_tag", None)
            if role == "assumption":
                if getattr(s, "key", None) is None:
                    return False
                n = owner_name(getattr(s, "owner", None))
                if n:
                    used.add(n)
            elif role == "unverified-citation":
                return False
            elif tag == "theorem":
                cited = getattr(s, "cites", None)
                if cited is not None:
                    if getattr(cited, "legacy", True):
                        return False
                    for a in getattr(cited, "requires", ()):
                        if getattr(a, "kind", None) in ("legacy", "textual"):
                            return False
                        if getattr(a, "kind", None) == "declared":
                            n = owner_name(getattr(a, "owner", None))
                            if n:
                                used.add(n)
                elif getattr(s, "key", None) is None and not getattr(s, "children", ()):
                    return False
            elif tag == "axiom" and role != "definition":
                return False
            if visit(getattr(s, "children", ())) is False:
                return False
        return True

    ok = visit(getattr(chain, "steps", chain))
    return used if ok else None


def _poisson_bivector_owner(o) -> bool:
    pi = getattr(o, "pi", None)
    deg = getattr(pi, "degree", None)
    decl = getattr(o, "declarations", None) or ()
    return (type(o).__name__ in ("PoissonStructure", "NambuPoissonStructure") and deg is not None
            and deg.as_int() == 2 and any(k in decl for k in POISSON_KEYS))


def unmodeled_assumption(requires=None, chain=None):
    """The first DECLARED assumption the proof used that the models do
    not satisfy (anything but a Poisson bivector's declaration), as an
    UNSUPPORTED kind — a D-model must satisfy every used axiom, else a
    DISAGREE would be the model's fault. ``None`` when all are modeled."""

    def judge(owner, rule):
        if owner is not None and _poisson_bivector_owner(owner):
            return None
        if owner is not None and SEL.is_algebroid(owner):
            # the hierarchy axioms are modeled (select.py); any other
            # algebroid-owned assumption (package rules citing
            # bourbaki/courant theorems, projectors) is not
            ax = SEL.axiom_of_rule(rule or "")
            return None if ax is not None else f"assumption[Algebroid:{(rule or '?').split(' (')[0][:40]}]"
        return f"assumption[{type(owner).__name__ if owner is not None else 'unowned'}]"

    if requires is not None:
        for a in requires:
            if getattr(a, "kind", None) == "declared":
                k = judge(getattr(a, "owner", None), getattr(a, "name", ""))
                if k:
                    return k
        return None
    if chain is None:
        return None
    stack = list(getattr(chain, "steps", chain))
    while stack:
        s = stack.pop()
        if getattr(s, "role", None) == "assumption":
            k = judge(getattr(s, "owner", None), getattr(s, "rule", ""))
            if k:
                return k
        cited = getattr(s, "cites", None)
        for a in getattr(cited, "requires", ()) if cited is not None else ():
            if getattr(a, "kind", None) == "declared":
                k = judge(getattr(a, "owner", None), getattr(a, "name", ""))
                if k:
                    return k
        stack.extend(getattr(s, "children", ()))
    return None


# --------------------------------------------------------------------- #
# Comparison                                                             #
# --------------------------------------------------------------------- #


def _show(v) -> str:
    if RZ.is_scalar(v):
        return str(v.as_expr())
    return repr(v)


def _apply(op, t):
    """``op(t)``, or ``DOMAIN`` when ``t`` lies outside the operator's
    mathematical domain. Oracle gaps (plain Unsupported) propagate."""
    try:
        return op(t)
    except DomainError:
        return DOMAIN


DOMAIN = object()


def values_equal(a, b, model, path=()) -> bool:
    """Equality of two realized values.

    Operators are compared on the FULL standard test basis (a function, a
    1-form, a 2-form, a vector field, a bivector). Domain rule (the
    mathematically honest one): two operators are equal only if they
    agree on every test argument. If one is defined on an argument and
    the other is not, they are DIFFERENT operators unless the defined one
    gives 0 there (a zero result is compatible with "not acting", e.g.
    ``d∘d = 0`` on a vector field). A test argument outside BOTH domains
    is skipped; no common argument at all is UNSUPPORTED. A gap of the
    oracle (not a domain fact) propagates as UNSUPPORTED."""
    R = model.R
    if isinstance(a, OpV) or isinstance(b, OpV):
        A, B = RZ.to_op(a, R, path), RZ.to_op(b, R, path)
        compared = 0
        for t in model.test_arguments():
            x, y = _apply(A, t), _apply(B, t)
            if x is DOMAIN and y is DOMAIN:
                continue
            if x is DOMAIN or y is DOMAIN:
                other = y if x is DOMAIN else x
                if isinstance(other, OpV) or not RZ.is_zero(other):
                    return False
                continue
            compared += 1
            if not values_equal(x, y, model, path):
                return False
        if not compared:
            raise Unsupported("operator-comparison[no common domain]", path)
        return True
    if RZ.is_zero(a) or RZ.is_zero(b):
        return RZ.is_zero(a) and RZ.is_zero(b)
    diff = RZ.add([a, RZ.scale(R.const(-1), b, R)], R, path)
    return RZ.is_zero(diff)


# --------------------------------------------------------------------- #
# Model dimension                                                        #
# --------------------------------------------------------------------- #

_VECTORISH = (VectorField, LieBracketVF, NambuSharpVF, SharpVF, HamiltonianVF)


def _deg_value(deg, assign):
    k = deg.as_int()
    if k is not None:
        return k
    total = 0
    for mono, c in deg.terms:
        term = c
        for name, e in mono:
            if name not in assign:
                return None
            term *= assign[name] ** e
        total += term
    return total


def _op_raise(op) -> int:
    """Upper bound of the degree an operator can ADD."""
    if isinstance(op, ExteriorDerivative):
        return 1
    if isinstance(op, Product):
        return sum(_op_raise(c) for c in op.children)
    if isinstance(op, (Sum,)):
        return max((_op_raise(c) for c in op.children), default=0)
    if isinstance(op, Neg):
        return _op_raise(op.arg)
    if isinstance(op, Commutator):
        return _op_raise(op.a) + _op_raise(op.b)
    return 0


def _op_lower(e, ub) -> int:
    """Upper bound of the degree an operator expression can LOWER."""
    if isinstance(e, (Interior, TildeInterior)):
        return 1
    if isinstance(e, MultivectorInterior):
        return ub(e.multivector)
    if isinstance(e, Product):
        return sum(_op_lower(c, ub) for c in e.children)
    if isinstance(e, Sum):
        return max((_op_lower(c, ub) for c in e.children), default=0)
    if isinstance(e, Neg):
        return _op_lower(e.arg, ub)
    if isinstance(e, Commutator):
        return _op_lower(e.a, ub) + _op_lower(e.b, ub)
    return 0


def _tm_object(e) -> bool:
    b = getattr(e, "bundle", None)
    return b is None or (getattr(b, "is_tangent", False) and b.dim is None)


def max_exterior_degree(exprs, assign, tm_only: bool = False) -> int:
    """Upper bound of the exterior / multivector degree of EVERY subnode
    (operator results included: ``d`` raises by one). The model dimension
    must exceed it, else a nonzero object of that degree vanishes
    identically and wrong identities pass. ``tm_only``: E-forms (bundle
    ≠ TM) and algebroid ``d_E`` count 0 — the bound for ``n = dim M``
    (the rank ``r`` of ``E`` takes the full bound)."""
    memo = {}

    def ub(e):
        key = id(e)
        if key in memo:
            return memo[key]
        if tm_only and isinstance(e, Form) and not _tm_object(e):
            v = 0
        elif isinstance(e, (Form, PVector)):
            v = _deg_value(e.degree, assign) or 0
        elif isinstance(e, _VECTORISH) or isinstance(e, (KoszulBracket, CoboundaryForm)):
            v = 1
        elif isinstance(e, Wedge):
            v = sum(ub(c) for c in e.children)
        elif isinstance(e, Product):
            vec = [ub(c) for c in e.children if isinstance(c, _VECTORISH)]
            rest = [ub(c) for c in e.children if not isinstance(c, _VECTORISH)]
            v = max(sum(rest), max(vec, default=0))
        elif isinstance(e, Sum):
            v = max((ub(c) for c in e.children), default=0)
        elif isinstance(e, Neg):
            v = ub(e.arg)
        elif isinstance(e, Act):
            raise_ = _op_raise(e.op)
            if tm_only and isinstance(e.op, ExteriorDerivative) and RZ.algebroid_of_calculus(e.op.calculus_name):
                raise_ = 0
            v = ub(e.arg) + raise_
        elif isinstance(e, PartialEval):
            v = e.n_open
        elif isinstance(e, BracketApply):
            v = ub(e.a) + ub(e.b)
        else:
            v = 0
        # an OPERATOR subnode needs test arguments of the degree it can
        # lower: ι_{X∧Y∧Z} is only visible on 3-forms, ι_π∘ι_π on 4-forms
        v = max(v, _op_lower(e, ub))
        memo[key] = v
        return v

    best, seen, stack = 0, set(), list(exprs)
    while stack:
        e = stack.pop()
        if id(e) in seen:
            continue
        seen.add(id(e))
        best = max(best, ub(e))
        stack.extend(_subexprs(e))
    return best


def _model_seed(base_seed: int, goal: str, index: int) -> int:
    h = hashlib.sha256(f"{base_seed}|{goal}|{index}".encode()).hexdigest()
    return int(h[:16], 16)


def _evaluate(lhs, rhs, model, registry, mode, deadline, indices=None):
    env = RZ.Env(model, registry=registry, mode=mode, deadline=deadline, indices=indices)
    lv = env.value(lhs, ("lhs",))
    rv = env.value(rhs, ("rhs",))
    eq = values_equal(lv, rv, model)
    return eq, lv, rv, bool(env.ambiguous)


def degree_range(lowering: int) -> Tuple[int, ...]:
    """Values of a symbolic degree: ``0..k+2`` for ``k`` degree-lowering
    operations in the equation (so a form survives k contractions with
    both parities left over)."""
    return tuple(range(lowering + 3))


def _degree_assignments(dvars, lowering: int = 0):
    """The FULL product ``degree_range^m`` (every variable takes every
    value and both parities, jointly); beyond :data:`MAX_ASSIGNMENTS` the
    check is UNSUPPORTED(budget) — never a silent narrowing."""
    if not dvars:
        return [{}]
    names = sorted(dvars)
    combos = list(itertools.product(degree_range(lowering), repeat=len(names)))
    if len(combos) > MAX_ASSIGNMENTS:
        raise Unsupported("budget[degree-assignments]", (), f"{len(combos)} > {MAX_ASSIGNMENTS}")
    return [dict(zip(names, c)) for c in combos]


def _make_model(n, seed, s, *, families, assign, label, plan, fams, need):
    """A model of ``R^n`` with the algebroid structures ``fams``
    (``{name: (family, r)}``, structures drawn from the seed pool and
    self-checked) and the plan's other bundles."""
    structures, bundles, anchors = {}, {}, {}
    if plan is not None:
        for name, (fam, r) in fams.items():
            info = plan.algebroids[name]
            structures[name] = build_structure(fam, n, r, seed % POOL)
            bundles[info["bundle"]] = (r, name)
            anchors[name] = info["anchor"]
        for b, name in plan.bundles.items():
            if b not in bundles:
                bundles[b] = (getattr(b, "dim", None) or max(3, need), None)
    return AlgebroidModel(n, seed, bivectors=families, degrees=assign, label=label, sample=s,
                          structures=structures, bundles=bundles, anchors=anchors)


def _index_dims(plan, model):
    dims = {}
    for lab, b in (plan.free_labels if plan is not None else {}).items():
        if b is None or (getattr(b, "is_tangent", False) and b.dim is None):
            dims[lab] = model.n
        else:
            dims[lab] = model.rank(b)
    return dims


def _run(lhs, rhs, *, registry, families, samples, base_seed, dvars, lowering, deadline, goal, label="",
         plan=None, override=None):
    """Evaluate in every (degree assignment × model spec × free-index
    assignment). Returns ``(witnesses, models, value_reading_holds,
    operator_reading_holds)``; raises Unsupported/Budget. Where a model
    has no Product ambiguity the operator reading IS the value reading.
    With algebroids, the number of models is at least the size of the
    family cover (select.py)."""
    witnesses, models, skipped = [], [], []
    v_all = o_all = True
    idx = 0
    for assign in _degree_assignments(dvars, lowering):
        need = max_exterior_degree((lhs, rhs), assign) + 1
        if need > MAX_DIM:
            # not evaluated: a refutation elsewhere still stands, but an
            # AGREE over the remaining assignments would be a silent
            # narrowing → the caller turns it into UNSUPPORTED(dimension)
            skipped.append((assign, need))
            continue
        n = max(3, need)
        if plan is not None:
            # E-degrees bound the rank r (select.py), not n = dim M
            n = max(3, max_exterior_degree((lhs, rhs), assign, tm_only=True) + 1)
        if plan is not None and plan.algebroids:
            specs = plan.model_specs(n, need, samples, override)
        else:
            specs = [(n, {})] * samples
        for s, (nm, fams) in enumerate(specs):
            seed = _model_seed(base_seed, goal, idx)
            idx += 1
            model = _make_model(nm, seed, s, families=families, assign=assign, label=label, plan=plan,
                                fams=fams, need=need)
            dims = _index_dims(plan, model)
            for ia in SEL.index_assignments(plan.free_labels if plan is not None else {}, dims, seed):
                eq, lv, rv, amb = _evaluate(lhs, rhs, model, registry, "value", deadline, ia)
                desc = model.describe() + (f" indices {ia}" if ia else "")
                models.append(desc)
                witnesses.append(Witness(desc, "value", _show(lv), _show(rv), eq))
                eq_op = eq
                if amb:  # same model (its atom cache), the other Product reading
                    eq_op, lv2, rv2, _ = _evaluate(lhs, rhs, model, registry, "operator", deadline, ia)
                    witnesses.append(Witness(desc, "operator", _show(lv2), _show(rv2), eq_op))
                v_all = v_all and eq
                o_all = o_all and eq_op
                if not v_all and not o_all:
                    return witnesses, models, False, False  # refuted: stop early
    if skipped and (v_all or o_all):
        raise Unsupported("dimension", (), f"{len(skipped)} assignment(s) need up to R^{max(k for _, k in skipped)} > R^{MAX_DIM}")
    return witnesses, models, v_all, o_all


def check_equal(lhs, rhs, *, registry=None, owners=None, samples: int = 2, seed: int = 0,
                requires=None, chain=None, timeout: float = 20.0, second_seed: bool = True,
                source: str = "", nodeid: str = "") -> OracleReport:
    """Compare ``lhs`` and ``rhs`` in random concrete models.

    ``owners``: the structures in scope (an engine's ``owners`` dict or an
    iterable) — they decide which declared axioms the D-models satisfy.
    ``requires`` / ``chain``: the proof's requirement record, used for the
    ASSUMPTION_LEAK check (skipped when it is unknown).
    """
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < 1:
        raise ValueError(f"samples must be a positive int, got {samples!r}")
    t0 = time.monotonic()
    deadline = t0 + timeout
    goal = f"{lhs._repr_inner()} = {rhs._repr_inner()}"
    base = dict(lhs=lhs._repr_inner(), rhs=rhs._repr_inner(), seed=seed, source=source, nodeid=nodeid)
    if lhs == rhs:
        return OracleReport(AGREE, detail="trivial (syntactically identical)", elapsed=time.monotonic() - t0, **base)
    names, nambu, dvars, atoms, lowering, count = scan(lhs, rhs)
    if count > MAX_NODES:
        return OracleReport(UNSUPPORTED, unsupported_type="budget[size]", unsupported_path=(),
                            detail=f"> {MAX_NODES} nodes", elapsed=time.monotonic() - t0, **base)
    obstruction = _owner_obstruction(owners, atoms, nambu) or unmodeled_assumption(requires, chain)
    if obstruction is not None:
        return OracleReport(UNSUPPORTED, unsupported_type=obstruction, unsupported_path=(),
                            detail="a declared structure axiom has no F1 model", elapsed=time.monotonic() - t0, **base)
    info = _structure_info(owners)
    if info is None and names:
        # unknown owners: whether a structure bivector is Poisson is not
        # known — no charitable guess (owners-unknown)
        return OracleReport(UNSUPPORTED, unsupported_type="owners-unknown", unsupported_path=(),
                            detail=f"structure bivector(s) {sorted(names)} without owner information",
                            elapsed=time.monotonic() - t0, **base)
    try:
        need0 = max(max_exterior_degree((lhs, rhs), a) + 1 for a in _degree_assignments(dvars, lowering))
        plan = SEL.plan_algebroids(lhs, rhs, owners, requires, chain, min(need0, MAX_DIM))
    except Unsupported as exc:
        return OracleReport(UNSUPPORTED, unsupported_type=exc.kind, unsupported_path=exc.path, detail=exc.detail,
                            elapsed=time.monotonic() - t0, **base)
    if not plan.active:
        plan = None
    declared = {n for n, ok in (info or {}).items() if ok}
    families = {}
    for n in names | declared:
        families[n] = "poisson" if n in declared else "generic"
    assign_txt = []
    if dvars:
        rng = degree_range(lowering)
        k = len(rng) ** len(dvars)
        assign_txt = [f"{v}∈{{{rng[0]}..{rng[-1]}}}" for v in sorted(dvars)] + [f"full product, {k} assignment(s)"]
    run = dict(registry=registry, families=families, samples=samples, dvars=dvars, lowering=lowering, goal=goal,
               plan=plan)
    try:
        witnesses, models, v_all, o_all = _run(lhs, rhs, base_seed=seed, deadline=deadline, **run)
    except Unsupported as exc:
        return OracleReport(UNSUPPORTED, unsupported_type=exc.kind, unsupported_path=exc.path, detail=exc.detail,
                            elapsed=time.monotonic() - t0, **base)
    except Budget:
        return OracleReport(UNSUPPORTED, unsupported_type="budget[time]", unsupported_path=(),
                            detail=f"> {timeout}s", elapsed=time.monotonic() - t0, **base)
    common = dict(samples=len(models), models=models, degree_assignments=assign_txt, witnesses=witnesses)
    if not v_all and not o_all:
        # every reading refuted in some model
        reproduced = None
        if second_seed:
            try:
                _, _, v2, o2 = _run(lhs, rhs, base_seed=seed + SECOND_SEED_OFFSET,
                                    deadline=time.monotonic() + timeout, **run)
                reproduced = not v2 and not o2
            except (Unsupported, Budget):
                reproduced = None
        bad = next(w for w in witnesses if not w.equal)
        return OracleReport(DISAGREE, detail=f"sides differ in {bad.model} [{bad.mode}]", reproduced=reproduced,
                            elapsed=time.monotonic() - t0, **common, **base)
    if v_all != o_all:
        survivor = "multiplication" if v_all else "composition"
        return OracleReport(AMBIGUOUS, detail=f"only the {survivor} reading of a Product survives every model",
                            elapsed=time.monotonic() - t0, **common, **base)
    # ASSUMPTION_LEAK: declared-but-unused Poisson structures
    unchecked = list(plan.notes) if plan is not None else []
    if plan is not None and plan.algebroids:
        counters, alg_unchecked = SEL.leak_counter_plans(plan, min(need0, MAX_DIM))
        unchecked.extend(alg_unchecked)
        for name, fam, hit in counters:
            try:
                w3, m3, v3, o3 = _run(lhs, rhs, base_seed=seed + 7, deadline=deadline,
                                      label=f"counter-model {name}:{fam[0]}",
                                      **dict(run, samples=1, override={name: [fam]}))
            except Budget:
                return _leak_budget(base, t0, timeout, f"{name} ({fam[0]})", common)
            except Unsupported as exc:
                unchecked.append(f"{name} ({fam[0]}): counter-model {type(exc).__name__} {getattr(exc, 'kind', '')}".strip())
                continue
            if not (v3 and o3):
                return OracleReport(ASSUMPTION_LEAK, leak_structure=f"{name}: {', '.join(hit)}",
                                    detail=(f"holds only under the axiom(s) {hit} of {name}, which the proof "
                                            f"record does not use (counter-model {fam[0]})"),
                                    elapsed=time.monotonic() - t0, samples=len(models) + len(m3),
                                    models=models + m3, degree_assignments=assign_txt,
                                    witnesses=witnesses + w3, **base)
    present = declared & (names | atoms)  # also a plain PVector π ([π,π]_SN, π(df,dg))
    used = poisson_requires(requires, chain)
    if used is None and present:
        unchecked.append(f"{', '.join(sorted(present))}: proof record unknown")
    if used is not None:
        for n in sorted(present):
            if n in used:
                continue
            fam = dict(families)
            fam[n] = "counter"
            try:
                w3, m3, v3, o3 = _run(lhs, rhs, base_seed=seed + 7, deadline=deadline,
                                      label="counter-model", **dict(run, families=fam, samples=1))
            except Budget:
                return _leak_budget(base, t0, timeout, n, common)
            except Unsupported as exc:
                unchecked.append(f"{n}: counter-model {type(exc).__name__} {getattr(exc, 'kind', '')}".strip())
                continue
            if not (v3 and o3):
                return OracleReport(ASSUMPTION_LEAK, leak_structure=n,
                                    detail=f"holds only under the Poisson condition on {n}, which the proof record does not use",
                                    elapsed=time.monotonic() - t0, samples=len(models) + len(m3),
                                    models=models + m3, degree_assignments=assign_txt,
                                    witnesses=witnesses + w3, **base)
    return OracleReport(AGREE, elapsed=time.monotonic() - t0, leak_unchecked="; ".join(unchecked) or None,
                        **common, **base)


def _leak_budget(base, t0, timeout, what, common):
    """The ASSUMPTION_LEAK counter-models share the check's deadline; when
    it runs out the D-models agreed but the leak check is incomplete —
    reported as UNSUPPORTED(budget[leak-check]), never a plain AGREE."""
    return OracleReport(UNSUPPORTED, unsupported_type="budget[leak-check]", unsupported_path=(),
                        detail=(f"sides agree in {common['samples']} D-model(s), but the assumption-leak "
                                f"counter-model for {what} exceeded the {timeout}s budget"),
                        elapsed=time.monotonic() - t0, **base)


def check_chain(chain, **kw) -> ChainReport:
    """Check every step ``before = after`` of a proof chain; the first
    refuted step names the rule that broke the equation."""
    reports, first, rule = [], None, None
    for i, s in enumerate(getattr(chain, "steps", chain)):
        r = check_equal(s.before, s.after, **kw)
        reports.append(r)
        if first is None and r.refutes:
            first, rule = i, getattr(s, "rule", None)
    return ChainReport(reports, first, rule)
