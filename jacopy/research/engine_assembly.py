"""
Engine auto-assembly (research interface, Phase 8 brick 3): look at the
expressions a user wants normalised, detect which node families occur
(Cartan operators, Nambu sharps of which structures, multivector
interiors, wedges, evaluations, …) and build the rewrite engine that
knows about exactly those — with a human-readable *assembly report*
saying what was detected and which rules were added, so the engine
explains itself.

Honest by construction: a sharp map of a structure the caller did not
hand over is an error (the engine cannot guess that structure's
rules), and the Poisson/fundamental-identity declaration is an explicit
``declare_fi=True`` — never inferred.

Also home of the two slot-reachable wedge rules first written by hand
in ``examples/bracket_twist_walkthrough.ipynb`` (now library rules):

* :class:`WedgeGradedOrderDefinition` — ``α ∧ β = (−1)^{|α||β|} β ∧ α``
  as a canonical ordering, ONLY when every factor has a concrete
  degree (so the sign is exact);
* :class:`WedgeScalarFactorDefinition` — ``(f·α) ∧ β → f·(α ∧ β)``.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set

from jacopy.core.expr import Expr, Neg, Product, Sum
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.proof.expansion import Definition, ExpansionEngine


def _wedge_degree(c: Expr, registry) -> Optional[int]:
    """The EXTERIOR-algebra degree of a wedge factor as a concrete
    int, or ``None`` when it is not certain — the concrete view of the
    single contract :func:`jacopy.algebra.grading.exterior_degree`
    (Faz 8 step 2a). Kept under its old name because the audit tests
    query it; it no longer computes anything itself. History: this
    helper used to grade on its own and the 2026-09-09/09-10/09-22
    audits each caught it sorting an odd factor (a vector field, a
    vector sum, a nested wedge) as even."""
    from jacopy.algebra.grading import concrete_exterior_degree

    return concrete_exterior_degree(c, registry)


class ZeroProductDefinition(Definition):
    """``0 · x → 0`` — slot-reachable: the simplifier does not enter
    operator argument slots, so ``Π(0·0)`` used to survive there
    (2026-09-09 audit, finding F3)."""

    name = "zero product: 0·x = 0 (slot-reachable)"
    anchor = Product

    def matches(self, expr: Expr) -> bool:
        from jacopy.core.expr import Integer

        return isinstance(expr, Product) and any(
            c == Integer(0) for c in expr.children
        )

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.core.expr import Integer

        return Integer(0)


# ------------------------------------------------------------------ #
# The two promoted wedge rules                                        #
# ------------------------------------------------------------------ #


class WedgeGradedOrderDefinition(Definition):
    """Canonical graded order of wedge factors (sound only with
    concrete degrees — the rule stays inert otherwise)."""

    name = "wedge graded commutativity: canonical order (concrete degrees)"
    anchor = Wedge

    def __init__(self, registry: Optional[PropertyRegistry] = None) -> None:
        self._r = registry

    def _sorted(self, e: Wedge):
        from jacopy.algorithms.normalize_alternating import _sort_key

        items = []
        for c in e.children:
            k = _wedge_degree(c, self._r)
            if k is None:
                return None
            items.append((c, k))
        # the SAME key as the simplifier's odd-degree sort
        # (normalize_alternating._sort_key): two canonical orders on
        # the same wedge would rewrite each other forever (2026-09-09
        # non-convergence catch on the exceptional 5-form Jacobi).
        target = sorted(items, key=lambda it: _sort_key(it[0]))
        if [c for c, _ in target] == list(e.children):
            return None
        cur, sign = items[:], 0
        for pos in range(len(target)):
            j = next(i for i in range(pos, len(cur)) if cur[i] == target[pos])
            while j > pos:
                # adjacent swap of degrees a, b costs (−1)^{ab}
                sign ^= (cur[j][1] * cur[j - 1][1]) & 1
                cur[j], cur[j - 1] = cur[j - 1], cur[j]
                j -= 1
        return sign, [c for c, _ in cur]

    def matches(self, expr: Expr) -> bool:
        return isinstance(expr, Wedge) and self._sorted(expr) is not None

    def rewrite(self, expr: Expr) -> Expr:
        sign, kids = self._sorted(expr)
        out = Wedge(*kids)
        return Neg(out) if sign else out


class WedgeScalarFactorDefinition(Definition):
    """``(f·α) ∧ β → f·(α ∧ β)`` — scalar factors of a wedge factor
    pull out in front (scalars are central)."""

    name = "wedge factor scalar pull-out: (f·α) ∧ β = f·(α ∧ β)"
    anchor = Wedge

    def __init__(self, registry: Optional[PropertyRegistry] = None) -> None:
        self._r = registry

    def _site(self, e: Wedge):
        from jacopy.central.calculus.scalars import is_scalar_function

        for i, c in enumerate(e.children):
            if isinstance(c, Product) and any(
                is_scalar_function(k, self._r) for k in c.children
            ):
                return i
        return None

    def matches(self, expr: Expr) -> bool:
        return isinstance(expr, Wedge) and self._site(expr) is not None

    def rewrite(self, expr: Expr) -> Expr:
        from jacopy.central.calculus.scalars import is_scalar_function

        i = self._site(expr)
        c = expr.children[i]
        scalars = [k for k in c.children if is_scalar_function(k, self._r)]
        rest = [k for k in c.children if not is_scalar_function(k, self._r)]
        kids = list(expr.children)
        kids[i] = rest[0] if len(rest) == 1 else Product(*rest)
        return Product(*scalars, Wedge(*kids))


# ------------------------------------------------------------------ #
# Scanning                                                            #
# ------------------------------------------------------------------ #


def _walk(expr: Expr, seen: Set[int], out: List[Expr]) -> None:
    if id(expr) in seen:
        return
    seen.add(id(expr))
    out.append(expr)
    for c in expr.children:
        _walk(c, seen, out)
    for s in getattr(expr, "rewritable_slots", ()) or ():
        if isinstance(s, Expr):
            _walk(s, seen, out)


class Scan:
    """What occurs in a set of expressions — the node families
    registered in :mod:`jacopy.research.structure_kinds` (central
    families and those of every registered structure kind)."""

    def __init__(self, exprs: Iterable[Expr]) -> None:
        from jacopy.central.objects.multivector_interior import (
            MultivectorInterior,
        )
        from jacopy.research.structure_kinds import (
            ensure_builtin_kinds,
            families,
        )

        ensure_builtin_kinds()
        nodes: List[Expr] = []
        seen: Set[int] = set()
        for e in exprs:
            _walk(e, seen, nodes)
        self.families: Set[str] = set()
        #: keys of the structures owning scanned nodes (e.g. the ``Π``
        #: of each Nambu sharp), in first-occurrence order
        self.structure_keys = []
        self.interior_multivectors = []
        table = families()
        for n in nodes:
            for fam in table:
                if isinstance(n, fam.cls):
                    self.families.add(fam.tag)
                    if fam.owner_key is not None:
                        k = fam.owner_key(n)
                        if k not in self.structure_keys:
                            self.structure_keys.append(k)
            if isinstance(n, MultivectorInterior):
                mv = n.multivector
                if mv not in self.interior_multivectors:
                    self.interior_multivectors.append(mv)

    @property
    def sharp_pis(self):
        """Legacy name of :attr:`structure_keys` (the Nambu sharps'
        multivectors were the only structure-owned nodes)."""
        return self.structure_keys

    def __repr__(self) -> str:
        return (
            f"Scan(families={sorted(self.families)}, "
            f"sharps={[_key_repr(p) for p in self.structure_keys]})"
        )


def _key_repr(key) -> str:
    inner = getattr(key, "_repr_inner", None)
    return inner() if callable(inner) else repr(key)


# ------------------------------------------------------------------ #
# Central families and family rules (registered lazily by             #
# structure_kinds.ensure_builtin_kinds)                               #
# ------------------------------------------------------------------ #


def _register_central_builtins() -> None:
    """The structure-free node families and family rules. ``order``
    reproduces the pre-registry ``assemble_engine`` sequence; the
    Nambu-Poisson kind slots its sharp-slot rules in at 35 and 40
    (:mod:`jacopy.research.nambu_kind`)."""
    from jacopy.algebra.derivation import Act
    from jacopy.algebra.lie_bracket_vf import LieBracketVF
    from jacopy.core.multi_eval import MultiEval
    from jacopy.central.calculus import (
        ActExpansionDefinition,
        MultiEvalArgLinearityDefinition,
        OperatorSlotAdditivityDefinition,
    )
    from jacopy.central.calculus.bracket_calculus import (
        ExteriorDerivative,
        LieDerivative,
    )
    from jacopy.central.calculus.slot_rules import (
        FormProductToWedgeDefinition,
        WedgeSumScalarDefinition,
    )
    from jacopy.central.objects.interior import Interior
    from jacopy.central.objects.multivector_interior import (
        MultivectorInterior,
        MultivectorInteriorDecomposableDefinition,
        MultivectorInteriorDecomposableFormDefinition,
        MultivectorInteriorLinearityDefinition,
    )
    from jacopy.central.tangent.lie_bracket import (
        LieBracketLeibnizDefinition,
    )
    from jacopy.research.structure_kinds import (
        additive_slot_tags,
        register_family,
        register_family_rule,
    )

    register_family(Act, "act")
    register_family(MultiEval, "multi_eval")
    register_family(Wedge, "wedge")
    register_family(IndexedSum, "indexed_sum")
    register_family(LieDerivative, "lie_derivative", additive_slots=True)
    register_family(ExteriorDerivative, "exterior_derivative")
    register_family(Interior, "interior", additive_slots=True)
    register_family(LieBracketVF, "lie_bracket")
    register_family(MultivectorInterior, "multivector_interior")

    rule = register_family_rule
    rule(lambda fam: True, lambda r: ZeroProductDefinition(), "always: zero products inside operator slots", order=10)
    mi = "multivector interiors present"
    rule("multivector_interior", MultivectorInteriorLinearityDefinition, mi, order=20)
    rule("multivector_interior", lambda r: MultivectorInteriorDecomposableDefinition(), mi, order=21)
    rule("multivector_interior", MultivectorInteriorDecomposableFormDefinition, mi, order=22)
    rule("wedge", WedgeSumScalarDefinition, "wedges present", order=30)
    rule("wedge", FormProductToWedgeDefinition, "wedges present", order=31)
    rule("wedge", WedgeGradedOrderDefinition, "wedges present", order=32)
    rule("wedge", WedgeScalarFactorDefinition, "wedges present", order=33)
    rule("act", ActExpansionDefinition, "operator actions present", order=50)
    rule("multi_eval", MultiEvalArgLinearityDefinition, "multi-slot evaluations present", order=60)
    rule(
        lambda fam: bool(fam & additive_slot_tags()),
        lambda r: OperatorSlotAdditivityDefinition(),
        "operators with additive direction slots",
        order=70,
    )
    rule("lie_bracket", LieBracketLeibnizDefinition, "Lie brackets of vector fields present", order=80)


# ------------------------------------------------------------------ #
# Assembly                                                            #
# ------------------------------------------------------------------ #


def _has(engine: ExpansionEngine, cls, key=None) -> bool:
    for d in engine.definitions:
        if type(d) is cls:
            if key is None:
                return True
            if getattr(d, "_N", None) is not None and getattr(d._N, "pi", None) == key:
                return True
    return False


def assemble_engine(
    *exprs: Expr,
    registry: Optional[PropertyRegistry] = None,
    structures: Sequence = (),
    declare_fi: bool = False,
    extra: Sequence[Definition] = (),
) -> ExpansionEngine:
    """Build an engine for ``exprs``; :func:`assembly_report` returns
    its one-line explanations of what was detected and added.

    ``structures`` are the structures whose nodes may occur, each
    handled by its registered kind
    (:mod:`jacopy.research.structure_kinds`; built in: Nambu-Poisson,
    :mod:`jacopy.research.nambu_kind`). The first one hosts the base
    engine (``kind.host_engine``), the others contribute their own
    rules (``engine_rules``); without structures the base is the
    tangent (Cartan) engine. The scanned node families decide the
    family rules. ``declare_fi=True`` DECLARES the fundamental identity
    of the first structure — an explicit assumption, recorded in the
    report."""
    from jacopy.central.tangent.engine import tangent_engine
    from jacopy.proof.ownership import check_owners
    from jacopy.research.structure_kinds import family_rules, structure_kind_of

    # two structures under one bivector name are ambiguous in the tree
    check_owners(structures)
    scan = Scan(exprs)
    report: List[str] = [f"scanned {len(exprs)} expression(s): {scan}"]
    kinds = [structure_kind_of(s) for s in structures]
    known = {k.key(s): s for k, s in zip(kinds, structures)}
    if len(known) != len(structures):
        raise ValueError("assemble_engine: two structures share one multivector — pass each structure once")
    unknown = [p for p in scan.structure_keys if p not in known]
    if unknown:
        raise ValueError(
            "sharp maps of undeclared structure(s) "
            f"{[_key_repr(p) for p in unknown]}: pass them via "
            "structures=(...) — the engine will not guess their rules"
        )

    structures = list(structures)
    if declare_fi and structures:
        # pre-4a spelling: the flag meant "the FIRST structure declares
        # the fundamental identity"; it is applied to that structure
        # only and reported — never distributed (Faz 8 step 4a)
        if not structures[0].declares("fundamental-identity"):
            structures[0] = structures[0].with_declarations("fundamental-identity")
        report.append(
            "declare_fi=True is the pre-4a spelling: applied to the first structure "
            f"{structures[0].name} only — declare on the structure instead"
        )
    if structures:
        host, host_kind = structures[0], kinds[0]
        eng = host_kind.host_engine(host, registry)
        report.append(host_kind.host_report(host))
        registered = {getattr(r, "key", None) for r in eng.definitions}
        first = 1 if host_kind.host_includes_rules else 0
        for s, kind in zip(structures[first:], kinds[first:]):
            # every structure contributes ITS OWN rule set — definitional
            # capabilities are symmetric, declared axioms are each
            # structure's own (N₁ with the FI, N₂ without)
            for rule in s.engine_rules(registry):
                if rule.key in registered:
                    continue
                eng.register(rule)
                registered.add(rule.key)
                report.append(f"+ {rule.name}  [rules of {s.name}]")
            report.append(kind.member_report(s))
    else:
        eng = tangent_engine(registry=registry)
        report.append("base: tangent (Cartan) engine")

    def add(rule: Definition, why: str) -> None:
        # deduplicated by the rule's structural KEY (identity or
        # class + name), not by class alone (Faz 8 step 4a / 1d)
        if any(getattr(r, "key", None) == rule.key for r in eng.definitions):
            return
        eng.register(rule)
        report.append(f"+ {rule.name}  [{why}]")

    fam = frozenset(scan.families)
    for entry in family_rules():
        if entry.when(fam):
            add(entry.build(registry), entry.why)
    for rule in extra:
        # caller-supplied rules are NEVER deduplicated: two instances
        # of one Definition class with different parameters are two
        # rules (2026-09-22 library audit — the class-keyed `add`
        # silently dropped the second); the display name is not an
        # identity
        eng.register(rule)
        report.append(f"+ {rule.name}  [requested by the caller]")
    eng.assembly_report = report
    return eng


#: Legacy name — the report now lives on the engine itself
#: (``ExpansionEngine.assembly_report``), so nothing is registered here
#: and no engine is kept alive by this module (2026-09-09 audit, F4).
_REPORTS: dict = {}


def assembly_report(engine: ExpansionEngine) -> List[str]:
    """The assembly report of an engine built by
    :func:`assemble_engine` (empty for other engines)."""
    return list(getattr(engine, "assembly_report", None) or [])
