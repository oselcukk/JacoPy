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
