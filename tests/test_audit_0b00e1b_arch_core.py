"""Audit 0B00E1B-FULL architecture lane (arch-core): behaviour-preserving
moves, pinned by identity.

T2-1 — the structure-free Cartan / slot-hygiene rules live in the
central layer (``jacopy.central.tangent.cartan_rules``,
``jacopy.central.calculus.slot_rules``); the package modules they were
first written in re-export the SAME class objects, so no import path
breaks and no engine changes.
"""

from __future__ import annotations

import importlib

import pytest

# (new central module, old package module, class name)
MOVED = [
    ("jacopy.central.tangent.cartan_rules", "jacopy.packages.drinfeld.twist", "MagicFormulaDefinition"),
    ("jacopy.central.tangent.cartan_rules", "jacopy.packages.drinfeld.tilde_calculus", "LieIotaCommutatorDefinition"),
    ("jacopy.central.tangent.cartan_rules", "jacopy.packages.poisson.nambu", "DSquaredZeroDefinition"),
    ("jacopy.central.tangent.cartan_rules", "jacopy.packages.poisson.nambu", "DWedgeLeibnizDefinition"),
    ("jacopy.central.calculus.slot_rules", "jacopy.packages.drinfeld.twist", "PairingArgSplitDefinition"),
    ("jacopy.central.calculus.slot_rules", "jacopy.packages.drinfeld.twist", "FormProductToWedgeDefinition"),
    ("jacopy.central.calculus.slot_rules", "jacopy.packages.drinfeld.twist", "WedgeSumScalarDefinition"),
    ("jacopy.central.calculus.slot_rules", "jacopy.packages.poisson.nambu", "WedgeZeroNegDefinition"),
    ("jacopy.central.calculus.slot_rules", "jacopy.packages.poisson.nambu", "TrivialZeroSumDefinition"),
]


@pytest.mark.parametrize("new, old, name", MOVED)
def test_t2_1_old_and_new_paths_are_the_same_class(new, old, name):
    new_cls = getattr(importlib.import_module(new), name)
    old_cls = getattr(importlib.import_module(old), name)
    assert new_cls is old_cls
    assert new_cls.__module__ == new
    assert name in importlib.import_module(new).__all__


def test_t2_1_central_modules_do_not_import_packages():
    # the point of the move: the central home needs no package
    import ast
    import pathlib

    import jacopy

    root = pathlib.Path(jacopy.__file__).parent
    for rel in ("central/tangent/cartan_rules.py", "central/calculus/slot_rules.py"):
        tree = ast.parse((root / rel).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(("jacopy.packages", "jacopy.research")), (rel, node.module)
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert not a.name.startswith(("jacopy.packages", "jacopy.research")), (rel, a.name)


def test_t2_1_engines_register_the_moved_classes_unchanged():
    # the package engines still register exactly these class objects
    from jacopy.central.calculus.slot_rules import (
        FormProductToWedgeDefinition,
        PairingArgSplitDefinition,
        TrivialZeroSumDefinition,
        WedgeSumScalarDefinition,
        WedgeZeroNegDefinition,
    )
    from jacopy.central.tangent.cartan_rules import (
        DSquaredZeroDefinition,
        DWedgeLeibnizDefinition,
        LieIotaCommutatorDefinition,
        MagicFormulaDefinition,
    )
    from jacopy.packages.drinfeld.tilde_calculus import _tilde_engine
    from jacopy.packages.poisson.nambu import nambu_structure

    eng = _tilde_engine(nambu_structure("θ", p=1), None)
    types = {type(r) for r in eng.definitions}
    for cls in (
        MagicFormulaDefinition, LieIotaCommutatorDefinition, DSquaredZeroDefinition,
        DWedgeLeibnizDefinition, PairingArgSplitDefinition, FormProductToWedgeDefinition,
        WedgeSumScalarDefinition, WedgeZeroNegDefinition, TrivialZeroSumDefinition,
    ):
        assert cls in types, cls.__name__


# ------------------------------------------------------------------ #
# T2-3 — assemble_engine knows only the registry protocol; a new
# structure type is registered from user code (here: this test), with
# no library edit.
# ------------------------------------------------------------------ #

from jacopy.core.expr import Integer, Symbol
from jacopy.proof.expansion import Definition


class Flux(Symbol):
    """A test-local node owned by the structure of the same name."""

    __slots__ = ()


class FluxVanishes(Definition):
    """The test structure's single rule: its flux node is zero."""

    name = "test flux vanishes: H = 0"
    anchor = Flux

    def matches(self, expr):
        return isinstance(expr, Flux)

    def rewrite(self, expr):
        return Integer(0)


class FluxMarker(Definition):
    """A family rule, added when a flux node is scanned (never fires)."""

    name = "test flux family rule"
    anchor = Flux

    def matches(self, expr):
        return False

    def rewrite(self, expr):  # pragma: no cover
        return expr


class FluxStructure:
    """A provider WITHOUT a ``pi`` field (the pre-registry engine read
    ``s.pi`` and raised AttributeError on such a structure)."""

    def __init__(self, name, declarations=()):
        self.name = name
        self.declarations = frozenset(declarations)

    def declares(self, key):
        return key in self.declarations

    def with_declarations(self, *keys):
        return FluxStructure(self.name, self.declarations | set(keys))

    def engine_rules(self, registry=None, *, phase=None):
        rule = FluxVanishes()
        rule.owner = self
        rule.identity = ("FluxVanishes", self.name)
        return [rule]


@pytest.fixture()
def flux_kind():
    from jacopy.research.structure_kinds import (
        StructureKind,
        register_family,
        register_family_rule,
        register_structure_kind,
        unregister,
    )

    class FluxKind(StructureKind):
        name = "test-flux"

        def accepts(self, s):
            return isinstance(s, FluxStructure)

        def key(self, s):
            return s.name

    kind = register_structure_kind(FluxKind())
    fam = register_family(Flux, "flux", owner_key=lambda n: n.name)
    rule = register_family_rule("flux", lambda registry: FluxMarker(), "flux nodes present", order=90)
    yield kind
    for entry in (rule, fam, kind):
        unregister(entry)


def test_t2_3_a_new_structure_kind_registers_without_library_edits(flux_kind):
    from jacopy.core.registry import PropertyRegistry
    from jacopy.proof.result import prove
    from jacopy.research import Scan, assemble_engine, assembly_report

    reg = PropertyRegistry()
    H = FluxStructure("H")
    assert not hasattr(H, "pi")
    scan = Scan([Flux("H")])
    assert "flux" in scan.families and scan.structure_keys == ["H"]
    eng = assemble_engine(Flux("H"), registry=reg, structures=(H,))
    rep = assembly_report(eng)
    assert any("test flux vanishes: H = 0" in line and "[rules of H]" in line for line in rep)
    assert any("test flux family rule" in line and "[flux nodes present]" in line for line in rep)
    assert any(line.startswith("base: tangent (Cartan) engine") for line in rep)
    assert eng.owners == {"H": H}
    res = prove(eng, Flux("H"), Integer(0), registry=reg)
    assert res.closed
    # a rule class defined outside the package is the caller's ASSUMPTION
    assert any(r.owner is H for r in res.requires)


def test_t2_3_nodes_of_an_undeclared_structure_are_refused(flux_kind):
    from jacopy.research import assemble_engine

    with pytest.raises(ValueError, match="undeclared structure"):
        assemble_engine(Flux("K"), structures=(FluxStructure("H"),))


def test_t2_3_a_structure_without_a_registered_kind_is_a_clear_error():
    from jacopy.research import assemble_engine

    with pytest.raises(TypeError, match="no structure kind is registered"):
        assemble_engine(structures=(FluxStructure("H"),))


def test_t2_3_nambu_is_one_registered_kind_and_the_family_order_is_fixed():
    from jacopy.packages.poisson.nambu import NambuSharpVF, nambu_structure
    from jacopy.research.nambu_kind import KIND
    from jacopy.research.structure_kinds import additive_slot_tags, families, family_rules, structure_kind_of

    assert structure_kind_of(nambu_structure("θ", p=1)) is KIND
    tags = [f.tag for f in families()]
    assert tags[-1] == "nambu_sharp" and any(f.cls is NambuSharpVF for f in families())
    assert {"lie_derivative", "interior", "nambu_sharp"} <= additive_slot_tags()
    whys = [r.why for r in family_rules()]
    # the pre-registry assemble_engine sequence
    assert whys.index("wedges present") < whys.index("wedges inside sharp slots") < whys.index(
        "sharp slots present (alternation must reach inside them)"
    ) < whys.index("operator actions present")
