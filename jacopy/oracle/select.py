"""Model selection for algebroid equations (SPEC §2 ``select.py``).

* D-models: every algebroid of the equation gets a family satisfying its
  DECLARED axioms (``Algebroid.declarations``, levels already expanded by
  the library), chosen to VIOLATE as many other axioms as possible; when
  several families are needed to cover the violations (e.g. a skew Lie
  model and a non-skew Courant model for ``leibniz``) all are used.
* ASSUMPTION_LEAK: an axiom declared but not used by the proof record
  (and not :data:`DERIVABLE` from the used ones) is checked in a
  counter-model that satisfies only the closure of the used axioms and
  violates the unused one.
* Declarations without a model (``bourbaki-invariance``,
  ``courant-invariance``, ``exact``) make the check UNSUPPORTED when the
  proof uses them (or the record is unknown); unused, they are skipped
  and reported as unchecked.

The proof record names a declared axiom by its RULE name
(``central/algebroid/declarations.py``: ``"right-Leibniz (E): …"``);
:data:`RULE_PREFIXES` maps it back. An unrecognised declared rule of an
algebroid owner makes the usage of that algebroid unknown.

This module reads owners and records by duck typing (no engine import).
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, List, Optional, Tuple

from jacopy.central.algebroid.context import (
    AlgebroidBracket,
    AnchoredVF,
    CoboundaryForm,
    EMetric,
    LocalityOperator,
    MetricSharp,
)
from jacopy.central.algebroid.operators import Derivator, Jacobiator, Predator
from jacopy.central.calculus.bracket_calculus import ExteriorDerivative, LieDerivative
from jacopy.central.objects.form import Form
from jacopy.central.objects.frame import CoframeField, FrameField, KroneckerDelta
from jacopy.central.objects.vector_field import VectorField
from jacopy.central.tangent.anholonomy import AnholonomyCoefficient
from jacopy.core.expr import Expr
from jacopy.core.indexed_sum import IndexedSum

from jacopy.oracle.models.algebroid import AM, AS, FAMILIES, J, LL, MI, MODELED, REG, RL, SP, family_rank
from jacopy.oracle.values import Unsupported

#: rule-name prefix → declared axiom (declarations.py ``self.name``)
RULE_PREFIXES = (
    ("right-Leibniz", RL),
    ("left-Leibniz", LL),
    ("anchor morphism", AM),
    ("Leibniz-Jacobi", J),
    ("antisymmetry", AS),
    ("metric invariance", MI),
    ("symmetric part", SP),
)

#: (premises, conclusion): theorems of the library's hierarchy
#: (context.py LEVELS comments): leibniz ⇒ anchor-morphism (Phase 3.D);
#: metric invariance + symmetric part ⇒ right Leibniz [B 4.11, g
#: non-degenerate by definition]; antisymmetry (resp. symmetric part)
#: + right Leibniz ⇒ left Leibniz (L = 0, resp. L = g(u,v) g⁻¹Df).
DERIVABLE = (
    (frozenset({RL, J}), AM),
    (frozenset({SP, MI}), RL),
    (frozenset({AS, RL}), LL),
    (frozenset({SP, RL}), LL),
)

#: violation weights for the greedy family cover (structural axioms first)
WEIGHTS = {RL: 3, AS: 3, J: 3, AM: 3, LL: 2, SP: 1, MI: 1, REG: 1}

MAX_INDEX_ASSIGNMENTS = 12


def axiom_of_rule(name: str) -> Optional[str]:
    for pre, ax in RULE_PREFIXES:
        if name.startswith(pre):
            return ax
    return None


def closure(axioms) -> frozenset:
    out = set(axioms)
    changed = True
    while changed:
        changed = False
        for prem, concl in DERIVABLE:
            if prem <= out and concl not in out:
                out.add(concl)
                changed = True
    return frozenset(out)


def is_algebroid(o) -> bool:
    return type(o).__name__ == "Algebroid" and hasattr(o, "declarations") and hasattr(o, "bundle")


def algebroid_owners(owners) -> Optional[Dict[str, dict]]:
    """``{name: {bundle, anchor, declared, tangent}}`` (declarations of
    same-named owners united), ``None`` when the owners are unknown."""
    if owners is None:
        return None
    if isinstance(owners, dict):
        owners = list(owners.values())
    out: Dict[str, dict] = {}
    for o in owners:
        if not is_algebroid(o):
            continue
        info = out.setdefault(o.name, {"bundle": o.bundle, "anchor": getattr(o, "anchor_name", "ρ"),
                                       "declared": set(), "tangent": bool(getattr(o, "is_tangent", False))})
        if info["bundle"] != o.bundle:
            info["conflict"] = True
        info["declared"] |= set(o.declarations)
    return out


def algebroid_usage(requires=None, chain=None):
    """``{algebroid name: used axioms or None (unknown)}`` from the proof
    record; ``None`` overall when the record cannot tell (legacy /
    textual entries, unknown citations)."""
    used: Dict[str, Optional[set]] = {}

    def note(owner, rule):
        if not is_algebroid(owner):
            return
        ax = axiom_of_rule(rule or "")
        cur = used.setdefault(owner.name, set())
        if ax is None or cur is None:
            used[owner.name] = None
        else:
            cur.add(ax)

    if requires is not None:
        for a in requires:
            k = getattr(a, "kind", None)
            if k in ("legacy", "textual", "unreplayed"):
                return None
            if k == "declared":
                note(getattr(a, "owner", None), getattr(a, "name", ""))
        return used
    if chain is None:
        return None

    def visit(steps):
        for s in steps:
            role = getattr(s, "role", None)
            tag = getattr(s, "provenance_tag", None)
            if role == "assumption":
                if getattr(s, "key", None) is None:
                    return False
                note(getattr(s, "owner", None), getattr(s, "rule", ""))
            elif role == "unverified-citation":
                return False
            elif tag == "theorem":
                cited = getattr(s, "cites", None)
                if cited is not None:
                    if getattr(cited, "legacy", True):
                        return False
                    for a in getattr(cited, "requires", ()):
                        if getattr(a, "kind", None) in ("legacy", "textual", "unreplayed"):
                            return False
                        if getattr(a, "kind", None) == "declared":
                            note(getattr(a, "owner", None), getattr(a, "name", ""))
                elif getattr(s, "key", None) is None and not getattr(s, "children", ()):
                    return False
            elif tag == "axiom" and role != "definition":
                return False
            if visit(getattr(s, "children", ())) is False:
                return False
        return True

    return used if visit(getattr(chain, "steps", chain)) else None


# --------------------------------------------------------------------- #
# Equation scan                                                          #
# --------------------------------------------------------------------- #

_NAMED = (AlgebroidBracket, AnchoredVF, CoboundaryForm, EMetric, LocalityOperator, MetricSharp, Derivator,
          Predator, Jacobiator)
_INDEXED = (FrameField, CoframeField, KroneckerDelta, AnholonomyCoefficient)


def _children(e):
    yield from e.children
    for s in getattr(e, "rewritable_slots", None) or ():
        if isinstance(s, Expr):
            yield s
    for attr in ("pi", "form", "vector", "multivector", "section", "function"):
        try:
            s = getattr(e, attr, None)
        except Exception:  # noqa: BLE001
            s = None
        if isinstance(s, Expr):
            yield s


def scan_algebroid(*exprs, max_nodes: int = 20_000):
    """``(algebroid names, non-TM bundles, free index labels → bundle,
    needs)`` where ``needs[name]`` ⊆ {"metric", "locality"} lists what
    the equation's nodes require of the structure. Free labels are those
    not bound by an enclosing IndexedSum."""
    names, bundles = set(), set()
    needs: Dict[str, set] = {}
    free: Dict[str, object] = {}
    count = 0
    stack = [(e, frozenset()) for e in exprs]
    seen = set()
    while stack:
        e, bound = stack.pop()
        count += 1
        if count > max_nodes:
            break
        key = (id(e), bound)
        if key in seen:
            continue
        seen.add(key)
        if isinstance(e, _NAMED):
            if not (isinstance(e, (Jacobiator, Derivator)) and e.tangent):
                names.add(e.algebroid_name)
            if isinstance(e, (EMetric, MetricSharp)):
                needs.setdefault(e.algebroid_name, set()).add("metric")
            if isinstance(e, LocalityOperator):
                needs.setdefault(e.algebroid_name, set()).add("locality")
        if isinstance(e, (ExteriorDerivative, LieDerivative)):
            c = e.calculus_name
            if c != "Cartan-TM" and c.startswith("Cartan-"):
                names.add(c[len("Cartan-"):])
        if isinstance(e, (VectorField, Form)):
            b = getattr(e, "bundle", None)
            if b is not None and not (getattr(b, "is_tangent", False) and b.dim is None):
                bundles.add(b)
        if isinstance(e, CoboundaryForm):
            bundles.add(e.bundle)
        if isinstance(e, _INDEXED):
            b = getattr(e, "bundle", None) if isinstance(e, (FrameField, CoframeField)) else None
            for lab in e.index_names:
                if lab not in bound and free.get(lab) is None:
                    # a label seen on an E-frame ranges over rank(E)
                    free[lab] = b
        if isinstance(e, IndexedSum):
            nb = bound | {getattr(e.dummy, "name", None)}
            rb = getattr(e.range_, "bundle", None)
            if rb is not None and not (getattr(rb, "is_tangent", False) and rb.dim is None):
                bundles.add(rb)
            stack.append((e.body, nb))
            continue
        for c in _children(e):
            stack.append((c, bound))
    return names, bundles, free, needs


# --------------------------------------------------------------------- #
# Family choice                                                          #
# --------------------------------------------------------------------- #


def _violations(family: str) -> frozenset:
    claims = FAMILIES[family][0]
    return frozenset(a for a in MODELED if a not in claims)


def candidates(target, n: int, need: int, dim=None, metric: bool = False) -> List[Tuple[str, int, int]]:
    """``(family, n_family, r)`` satisfying ``target`` (sorted by name)."""
    out = []
    for fam, (claims, n_min, _rule, has_g) in sorted(FAMILIES.items()):
        if not set(target) <= claims:
            continue
        if metric and not has_g:
            continue
        nf = max(n, n_min)
        r = family_rank(fam, nf, need)
        if r is None or r < need:
            continue
        if dim is not None and r != dim:
            if FAMILIES[fam][2] == "free" and dim >= need:
                r = dim
            else:
                continue
        out.append((fam, nf, r))
    return out


def cover(cands, wanted) -> List[Tuple[str, int, int]]:
    """Greedy weighted cover of the axioms in ``wanted`` by family
    violations; ties → fewer extra satisfied axioms, then smaller n·r.
    Always at least one family when ``cands`` is non-empty."""
    left = set(wanted)
    chosen: List = []
    pool = list(cands)
    while pool:
        def score(c):
            v = _violations(c[0]) & left
            return (sum(WEIGHTS.get(a, 1) for a in v), -len(FAMILIES[c[0]][0]), -(c[1] * c[2]), c[0])

        best = max(pool, key=score)
        gain = _violations(best[0]) & left
        if chosen and not gain:
            break
        chosen.append(best)
        pool.remove(best)
        left -= gain
        if not left:
            break
    return chosen


class AlgebroidPlan:
    """What the models of one check must contain."""

    def __init__(self) -> None:
        self.algebroids: Dict[str, dict] = {}  # name → info + target + plans
        self.bundles: Dict = {}  # non-TM bundle → algebroid name or None
        self.free_labels: Dict[str, object] = {}
        self.notes: List[str] = []

    @property
    def active(self) -> bool:
        return bool(self.algebroids or self.bundles or self.free_labels)

    def model_specs(self, n: int, need: int, samples: int, override: Optional[Dict[str, Tuple]] = None):
        """One spec per model: ``(n_model, {alg: (family, r)})``."""
        per_alg = {}
        for name, info in sorted(self.algebroids.items()):
            if override is not None and name in override:
                per_alg[name] = override[name]
                continue
            per_alg[name] = info["order"]
        count = max([samples] + [len(info["cover"]) for info in self.algebroids.values()]) if per_alg else samples
        specs = []
        for i in range(count):
            fams = {name: lst[i % len(lst)] for name, lst in per_alg.items()}
            nm = max([n] + [f[1] for f in fams.values()])
            # a family's rank may depend on n (n+1, 2n): recompute at nm
            fixed = {}
            for name, (fam, _nf, r) in fams.items():
                rr = family_rank(fam, nm, need)
                if FAMILIES[fam][2] == "free":
                    rr = r
                fixed[name] = (fam, rr)
            specs.append((nm, fixed))
        return specs


def plan_algebroids(lhs, rhs, owners, requires, chain, need: int):
    """Build the :class:`AlgebroidPlan` or raise :class:`Unsupported`."""
    names, bundles, free, needs = scan_algebroid(lhs, rhs)
    plan = AlgebroidPlan()
    plan.free_labels = free
    if not names and not bundles:
        return plan
    infos = algebroid_owners(owners)
    if infos is None:
        raise Unsupported("owners-unknown", (), f"algebroid structure(s) {sorted(names) or sorted(map(repr, bundles))}")
    usage = algebroid_usage(requires, chain)
    # algebroids whose bundle carries sections of the equation
    for name, info in infos.items():
        if info["bundle"] in bundles and not info["tangent"]:
            names.add(name)
    by_bundle: Dict = {}
    for name in sorted(names):
        info = infos.get(name)
        if info is None:
            raise Unsupported("algebroid[unknown structure]", (), name)
        if info.get("conflict"):
            raise Unsupported("algebroid[same name, different bundles]", (), name)
        if info["tangent"]:
            continue
        b = info["bundle"]
        if b in by_bundle:
            raise Unsupported("algebroid[two structures on one bundle]", (), f"{by_bundle[b]}, {name}")
        by_bundle[b] = name
        declared = set(info["declared"])
        unmodeled = sorted(declared - set(MODELED))
        used = None if usage is None else usage.get(name, set())
        if unmodeled:
            if used is None or set(unmodeled) & (used or set()):
                raise Unsupported(f"algebroid-model[{','.join(unmodeled)}]", (), name)
            plan.notes.append(f"{name}: declared {unmodeled} not modeled (unused by the proof)")
        target = frozenset(declared & set(MODELED))
        dim = getattr(b, "dim", None)
        need_metric = "metric" in needs.get(name, ())
        # L(ω,u,v) has a model value only where left Leibniz holds
        req = target | ({LL} if "locality" in needs.get(name, ()) else set())
        cands = candidates(req, 3, need, dim, metric=need_metric)
        if not cands:
            extra = "+metric" if need_metric else ""
            raise Unsupported(f"algebroid-model[{','.join(sorted(req)) or 'none'}{extra}]", (), name)
        wanted = set(MODELED) - closure(target)
        chosen = cover(cands, wanted)
        # samples beyond the cover cycle through the other candidates
        order = chosen + [c for c in cands if c not in chosen]
        plan.algebroids[name] = dict(info, target=target, used=used, cover=chosen, order=order, bundle=b, dim=dim,
                                     metric=need_metric, extra=frozenset(req - target))
    for b in bundles:
        if b not in by_bundle:
            plan.bundles[b] = None
    for b, name in by_bundle.items():
        plan.bundles[b] = name
    return plan


def leak_counter_plans(plan: AlgebroidPlan, need: int):
    """``[(algebroid, family tuple, violated unused axioms)]`` counter-
    models, and the unused axioms no family can isolate (unchecked)."""
    out, unchecked = [], []
    for name, info in sorted(plan.algebroids.items()):
        used = info["used"]
        if used is None:
            if info["target"]:
                unchecked.append(f"{name}: proof record unknown")
            continue
        base = closure(used)
        unused = set(info["target"]) - base
        if not unused:
            continue
        cands = candidates(base | info["extra"], 3, need, info["dim"], metric=info["metric"])
        left = set(unused)
        for fam in cover(cands, unused):
            hit = _violations(fam[0]) & left
            if not hit:
                continue
            out.append((name, fam, sorted(hit)))
            left -= hit
        if left:
            unchecked.append(f"{name}: no counter-model violating {sorted(left)} under {sorted(base)}")
    return out, unchecked


# --------------------------------------------------------------------- #
# Free frame-index assignments                                           #
# --------------------------------------------------------------------- #


def index_assignments(free: Dict[str, object], dims: Dict[str, int], seed: int) -> List[Dict[str, int]]:
    """Values of the free index labels: every assignment when there are
    at most :data:`MAX_INDEX_ASSIGNMENTS`, else the all-equal one, an
    all-distinct one and random ones (distinct labels may name the same
    index — ``kronecker_delta`` keeps ``δ^a_b`` symbolic)."""
    labels = sorted(free)
    if not labels:
        return [{}]
    ranges = [range(dims[lab]) for lab in labels]
    total = 1
    for r in ranges:
        total *= len(r)
    if total <= MAX_INDEX_ASSIGNMENTS:
        return [dict(zip(labels, c)) for c in itertools.product(*ranges)]
    rng = random.Random(seed)
    out = [dict.fromkeys(labels, 0), {lab: i % dims[lab] for i, lab in enumerate(labels)}]
    while len(out) < MAX_INDEX_ASSIGNMENTS:
        out.append({lab: rng.randrange(dims[lab]) for lab in labels})
    return out
