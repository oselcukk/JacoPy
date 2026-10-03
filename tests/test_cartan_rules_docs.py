"""``jacopy.central.tangent.cartan_rules`` docstrings match the
reviewed roles (display-polish 2026-10-02): the four rules have role
``definition`` in ``rule_roles_inventory.json``; three of them are
theorem-TAGGED (they carry a sub-proof builder). The docstrings called
them "THEOREM-classified". Roles are unchanged."""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_cartan_rules_docstrings_match_reviewed_roles():
    from jacopy.central.tangent import cartan_rules

    inventory = json.loads((ROOT / "tests" / "rule_roles_inventory.json").read_text())
    names = ("MagicFormulaDefinition", "LieIotaCommutatorDefinition", "DSquaredZeroDefinition", "DWedgeLeibnizDefinition")
    assert "THEOREM-classified" not in (cartan_rules.__doc__ or "")
    for n in names:
        cls = getattr(cartan_rules, n)
        assert inventory[f"jacopy.central.tangent.cartan_rules.{n}"] == "definition" == cls.role
        assert "THEOREM-classified" not in (cls.__doc__ or "")
        rule = cls()  # every constructor argument is optional
        # the docstring's "theorem-tagged" claim: a sub-proof builder
        assert rule.is_theorem == (n != "DWedgeLeibnizDefinition")
    assert "role ``definition``" in cartan_rules.__doc__ or "ROLE ``definition``" in cartan_rules.__doc__
