"""
The built-in Nambu-Poisson structure kind for
:func:`~jacopy.research.engine_assembly.assemble_engine` (audit
0B00E1B-FULL T2-3).

Everything ``assemble_engine`` used to hard-code about Nambu-Poisson
structures, now registered through the generic protocol of
:mod:`jacopy.research.structure_kinds`:

* the node family ``"nambu_sharp"`` (:class:`NambuSharpVF`, owned by
  its ``Π``; an operator with additive direction slots);
* the sharp-slot family rules (wedges inside sharp slots; alternation
  inside sharp slots);
* the kind itself: keyed by ``Π``, hosting the tilde-calculus engine
  (Cartan calculus + Koszul/tilde rules) and reporting the
  fundamental-identity declaration.

Behaviour, rule order and report lines are those of the pre-registry
``assemble_engine``.
"""

from __future__ import annotations

# imported at load time, as the pre-registry assemble_engine did on
# every call (module import side effects unchanged)
from jacopy.packages.drinfeld.roytenberg import SharpSlotWedgeNormalizeDefinition
from jacopy.packages.drinfeld.tilde_calculus import nambu_tilde_engine
from jacopy.packages.poisson.nambu import NambuPoissonStructure, NambuSharpVF
from jacopy.research.structure_kinds import (
    StructureKind,
    register_family,
    register_family_rule,
    register_structure_kind,
)


class NambuPoissonKind(StructureKind):
    """Nambu-Poisson structures (``p = 1``: Poisson) as assembled-engine
    hosts and members."""

    name = "nambu-poisson"
    host_includes_rules = True   # the tilde engine registers Π's own rules

    def accepts(self, structure) -> bool:
        return isinstance(structure, NambuPoissonStructure)

    def key(self, structure):
        return structure.pi

    def host_engine(self, structure, registry):
        return nambu_tilde_engine(structure, registry)

    def host_report(self, structure) -> str:
        return (
            f"base: tilde-calculus engine hosted by {structure.name} "
            f"(Cartan calculus + Koszul/tilde rules)"
            + (
                " — WITH the DECLARED fundamental identity (Poisson condition)"
                if structure.declares("fundamental-identity")
                else " — no fundamental-identity declaration"
            )
        )

    def member_report(self, structure) -> str:
        return (
            f"structure {structure.name}: "
            + ("WITH the DECLARED fundamental identity" if structure.declares("fundamental-identity") else "no fundamental-identity declaration")
        )


KIND = NambuPoissonKind()


def _sharp_slot_alternation(registry):
    # evaluations θ(·,·) are BORN inside sharp slots during expansion
    # (not visible in the scanned input), so the slot-reachable
    # alternation rule rides with every sharp
    from jacopy.packages.generalized.r_twisted import (
        SharpSlotAlternatingNormalizeDefinition,
    )

    return SharpSlotAlternatingNormalizeDefinition(registry)


def register() -> None:
    """Register the Nambu-Poisson family, family rules and kind (the
    ``order`` values place the rules exactly where the pre-registry
    ``assemble_engine`` added them — see ``engine_assembly``)."""
    register_family(NambuSharpVF, "nambu_sharp", owner_key=lambda n: n.pi, additive_slots=True)
    register_family_rule(
        {"wedge", "nambu_sharp"},
        SharpSlotWedgeNormalizeDefinition,
        "wedges inside sharp slots",
        order=35,
    )
    register_family_rule(
        "nambu_sharp",
        _sharp_slot_alternation,
        "sharp slots present (alternation must reach inside them)",
        order=40,
    )
    register_structure_kind(KIND)


__all__ = ["KIND", "NambuPoissonKind", "register"]
