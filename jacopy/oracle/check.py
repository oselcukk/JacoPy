"""``check_equal`` / ``check_chain``: evaluate both sides of a closed
equation in random concrete models and compare.

Model selection (F1):

* D-models: ``R^n`` (``n = 3``, or 4 when a degree-3 object occurs) with
  random polynomial data; a structure bivector (named by a ``tilde-π`` /
  ``lichnerowicz-π`` calculus) is POISSON when its structure declares
  ``poisson`` (or ``fundamental-identity``) — or when no owner
  information is available — and GENERIC when the owners are known and
  do not declare it.
* ASSUMPTION_LEAK (F1: the ``poisson`` declaration only): when a
  structure is declared Poisson but the proof's requirement record does
  not use it, the equation must also hold in a verified non-Poisson
  counter-model.
* Symbolic degrees: each degree variable is assigned ``{0, 1, 2}``
  (both parities; SPEC §7) and every assignment is checked.
* Determinism: model seed ``sha256(base_seed, goal, index)`` (SPEC §4);
  a DISAGREE is re-run automatically with a second base seed.
"""

from __future__ import annotations

import hashlib
import itertools
import time
from typing import Iterable, Optional

from jacopy.central.calculus.bracket_calculus import ExteriorDerivative, LieDerivative
from jacopy.central.objects.form import Form
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.vector_field import VectorField
from jacopy.core.expr import Expr, Symbol
from jacopy.packages.poisson.core import HamiltonianVF, PoissonBracketValue, SharpVF
from jacopy.packages.poisson.koszul import KoszulBracket
from jacopy.packages.poisson.nambu import NambuSharpVF

from jacopy.oracle import realize as RZ
from jacopy.oracle.models.tangent import TangentModel
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
from jacopy.oracle.values import Budget, OpV, Unsupported

POISSON_KEYS = ("poisson", "fundamental-identity")
SECOND_SEED_OFFSET = 1_000_003
MAX_NODES = 20_000


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
    max concrete degree, atom names, node count)``. A bivector is a
    STRUCTURE bivector when a tilde/Lichnerowicz calculus or a Poisson
    node (sharp, Hamiltonian, bracket) refers to it."""
    names, nambu, dvars, atoms = set(), set(), set(), set()
    maxdeg, count = 0, 0
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
        if isinstance(e, (Form, PVector)):
            k = e.degree.as_int()
            if k is None:
                dvars |= set(e.degree.variables())
            else:
                maxdeg = max(maxdeg, k)
        stack.extend(_subexprs(e))
    return names, nambu, dvars, maxdeg, atoms, count


#: Owner classes whose declared axioms the F1 models understand. Any other
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
    """The first DECLARED assumption the proof used that the F1 models do
    not satisfy (anything but a Poisson bivector's declaration), as an
    UNSUPPORTED kind — a D-model must satisfy every used axiom, else a
    DISAGREE would be the model's fault. ``None`` when all are modeled."""

    def judge(owner, rule):
        if owner is not None and _poisson_bivector_owner(owner):
            return None
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


def values_equal(a, b, model, path=()) -> bool:
    R = model.R
    if isinstance(a, OpV) or isinstance(b, OpV):
        A, B = RZ.to_op(a, R, path), RZ.to_op(b, R, path)
        compared = 0
        for t in model.test_arguments():
            try:
                x, y = A(t), B(t)
            except Unsupported:
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
# check_equal                                                            #
# --------------------------------------------------------------------- #


def _model_seed(base_seed: int, goal: str, index: int) -> int:
    h = hashlib.sha256(f"{base_seed}|{goal}|{index}".encode()).hexdigest()
    return int(h[:16], 16)


def _evaluate(lhs, rhs, model, registry, mode, deadline):
    env = RZ.Env(model, registry=registry, mode=mode, deadline=deadline)
    lv = env.value(lhs, ("lhs",))
    rv = env.value(rhs, ("rhs",))
    eq = values_equal(lv, rv, model)
    return eq, lv, rv, bool(env.ambiguous)


def _degree_assignments(dvars):
    if not dvars:
        return [{}]
    names = sorted(dvars)
    combos = list(itertools.product((0, 1, 2), repeat=len(names)))
    if len(combos) > 9:
        combos = combos[:: max(1, len(combos) // 9)][:9]
    return [dict(zip(names, c)) for c in combos]


def _run(lhs, rhs, *, registry, families, samples, base_seed, dvars, maxdeg, deadline, goal, label=""):
    """Evaluate in every (degree assignment × sample). Returns
    ``(witnesses, ambiguous_split, models)``; raises Unsupported/Budget."""
    witnesses, models = [], []
    ambiguous_split = False
    assignments = _degree_assignments(dvars)
    idx = 0
    for assign in assignments:
        top = max([maxdeg] + list(assign.values()))
        n = min(4, max(3, top + 1))
        for s in range(samples):
            seed = _model_seed(base_seed, goal, idx)
            idx += 1
            model = TangentModel(n, seed, bivectors=families, degrees=assign, label=label)
            eq, lv, rv, amb = _evaluate(lhs, rhs, model, registry, "value", deadline)
            models.append(model.describe())
            witnesses.append(Witness(model.describe(), "value", _show(lv), _show(rv), eq))
            if amb:
                model2 = TangentModel(n, seed, bivectors=families, degrees=assign, label=label)
                eq2, lv2, rv2, _ = _evaluate(lhs, rhs, model2, registry, "operator", deadline)
                witnesses.append(Witness(model2.describe(), "operator", _show(lv2), _show(rv2), eq2))
                if eq2 != eq:
                    ambiguous_split = True
    return witnesses, ambiguous_split, models


def check_equal(lhs, rhs, *, registry=None, owners=None, samples: int = 2, seed: int = 0,
                requires=None, chain=None, timeout: float = 20.0, second_seed: bool = True,
                source: str = "", nodeid: str = "") -> OracleReport:
    """Compare ``lhs`` and ``rhs`` in random concrete models.

    ``owners``: the structures in scope (an engine's ``owners`` dict or an
    iterable) — they decide which declared axioms the D-models satisfy.
    ``requires`` / ``chain``: the proof's requirement record, used for the
    ASSUMPTION_LEAK check (skipped when it is unknown).
    """
    t0 = time.monotonic()
    deadline = t0 + timeout
    goal = f"{lhs._repr_inner()} = {rhs._repr_inner()}"
    base = dict(lhs=lhs._repr_inner(), rhs=rhs._repr_inner(), seed=seed, source=source, nodeid=nodeid)
    names, nambu, dvars, maxdeg, atoms, count = scan(lhs, rhs)
    if count > MAX_NODES:
        return OracleReport(UNSUPPORTED, unsupported_type="budget[size]", unsupported_path=(),
                            detail=f"> {MAX_NODES} nodes", elapsed=time.monotonic() - t0, **base)
    obstruction = _owner_obstruction(owners, atoms, nambu) or unmodeled_assumption(requires, chain)
    if obstruction is not None:
        return OracleReport(UNSUPPORTED, unsupported_type=obstruction, unsupported_path=(),
                            detail="a declared structure axiom has no F1 model", elapsed=time.monotonic() - t0, **base)
    info = _structure_info(owners)
    declared = {n for n, ok in (info or {}).items() if ok}
    families = {}
    for n in names | declared:
        families[n] = "poisson" if (n in declared or info is None) else "generic"
    assign_txt = []
    if dvars:
        assign_txt = [f"{v}∈{{0,1,2}}" for v in sorted(dvars)]
    try:
        witnesses, split, models = _run(lhs, rhs, registry=registry, families=families, samples=samples,
                                        base_seed=seed, dvars=dvars, maxdeg=maxdeg, deadline=deadline, goal=goal)
    except Unsupported as exc:
        return OracleReport(UNSUPPORTED, unsupported_type=exc.kind, unsupported_path=exc.path, detail=exc.detail,
                            elapsed=time.monotonic() - t0, **base)
    except Budget:
        return OracleReport(UNSUPPORTED, unsupported_type="budget[time]", unsupported_path=(),
                            detail=f"> {timeout}s", elapsed=time.monotonic() - t0, **base)
    common = dict(samples=len(models), models=models, degree_assignments=assign_txt, witnesses=witnesses)
    if split:
        return OracleReport(AMBIGUOUS, detail="Product readings (multiplication vs composition) disagree",
                            elapsed=time.monotonic() - t0, **common, **base)
    if any(not w.equal for w in witnesses):
        reproduced = None
        if second_seed:
            try:
                w2, _, _ = _run(lhs, rhs, registry=registry, families=families, samples=samples,
                                base_seed=seed + SECOND_SEED_OFFSET, dvars=dvars, maxdeg=maxdeg,
                                deadline=time.monotonic() + timeout, goal=goal)
                reproduced = any(not w.equal for w in w2)
            except (Unsupported, Budget):
                reproduced = None
        bad = next(w for w in witnesses if not w.equal)
        return OracleReport(DISAGREE, detail=f"sides differ in {bad.model}", reproduced=reproduced,
                            elapsed=time.monotonic() - t0, **common, **base)
    # ASSUMPTION_LEAK: declared-but-unused Poisson structures
    used = poisson_requires(requires, chain)
    if used is not None:
        for n in sorted(declared & names):
            if n in used:
                continue
            fam = dict(families)
            fam[n] = "counter"
            try:
                w3, _, m3 = _run(lhs, rhs, registry=registry, families=fam, samples=1, base_seed=seed + 7,
                                 dvars=dvars, maxdeg=maxdeg, deadline=time.monotonic() + timeout, goal=goal,
                                 label="counter-model")
            except (Unsupported, Budget):
                continue
            if any(not w.equal for w in w3):
                return OracleReport(ASSUMPTION_LEAK, leak_structure=n,
                                    detail=f"holds only under the Poisson condition on {n}, which the proof record does not use",
                                    elapsed=time.monotonic() - t0, samples=len(models) + len(m3),
                                    models=models + m3, degree_assignments=assign_txt,
                                    witnesses=witnesses + w3, **base)
    return OracleReport(AGREE, elapsed=time.monotonic() - t0, **common, **base)


def check_chain(chain, **kw) -> ChainReport:
    """Check every step ``before = after`` of a proof chain; the first
    refuted step names the rule that broke the equation (K4-2)."""
    reports, first, rule = [], None, None
    for i, s in enumerate(getattr(chain, "steps", chain)):
        r = check_equal(s.before, s.after, **kw)
        reports.append(r)
        if first is None and r.refutes:
            first, rule = i, getattr(s, "rule", None)
    return ChainReport(reports, first, rule)
