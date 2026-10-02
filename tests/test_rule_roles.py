"""The semantic ROLE inventory of every rule class (audit dc44f79 F3):
each ``Definition`` subclass of the package is listed in
``rule_roles_inventory.json`` with its reviewed role — ``definition``
(a definitional unfolding or structural law: assumes nothing),
``assumption`` (a declared / opt-in hypothesis: enters a result's
requirements) or ``theorem``. A new rule class without an entry, or a
class whose role drifted from the reviewed one, fails here — a
hypothesis cannot silently become a definition."""

from __future__ import annotations

import importlib
import json
import pathlib
import pkgutil

import pytest

import jacopy
from jacopy.proof.expansion import Definition

INVENTORY = pathlib.Path(__file__).with_name("rule_roles_inventory.json")


def _classes():
    for m in pkgutil.walk_packages(jacopy.__path__, "jacopy."):
        importlib.import_module(m.name)
    seen, out = set(), {}

    def walk(c):
        for s in c.__subclasses__():
            if s in seen:
                continue
            seen.add(s)
            if s.__module__.startswith("jacopy."):
                out[f"{s.__module__}.{s.__name__}"] = s
            walk(s)

    walk(Definition)
    return out


def test_every_rule_class_has_a_reviewed_role():
    pytest.importorskip("sympy")  # walks every module, jacopy.oracle included (sympy extra)
    inventory = json.loads(INVENTORY.read_text())
    classes = _classes()
    missing = sorted(set(classes) - set(inventory))
    assert not missing, f"review the role of the new rule class(es) and add them to the inventory: {missing}"
    stale = sorted(set(inventory) - set(classes))
    assert not stale, f"remove from the inventory: {stale}"
    drift = {n: (inventory[n], c.role) for n, c in classes.items() if c.role != inventory[n]}
    assert not drift, f"role drifted from the reviewed inventory: {drift}"
    assert set(inventory.values()) <= {"definition", "assumption", "theorem"}


def test_declaration_classes_are_assumptions():
    pytest.importorskip("sympy")  # walks every module, jacopy.oracle included (sympy extra)
    # the naming convention is not the trust boundary, but every class
    # named *Declaration must at least be an assumption
    for name, c in _classes().items():
        if name.endswith("Declaration"):
            assert c.role == "assumption", name


# --- audit 0B00E1B-FULL M1-4 --------------------------------------- #
#: A rule that presents itself as a CITED RESULT (class name says
#: "Theorem", docstring says "THEOREM-classified" / "citing the
#: proven") is not a definitional unfolding.
import re as _re

_CITATION_MARK = _re.compile(r"THEOREM-classified|citing the proven", _re.I)


def _own_builder(c):
    return c.theorem_proof_builder is not Definition.theorem_proof_builder


def test_theorem_like_rules_are_not_bare_definitions():
    pytest.importorskip("sympy")  # walks every module, jacopy.oracle included (sympy extra)
    # "Theorem" in the name / a citation docstring + role "definition"
    # + no proof builder = the rule rewrites by a theorem while the
    # engine records an assumption-free definitional step (M1-4)
    offenders = []
    for name, c in _classes().items():
        doc = " ".join((c.__doc__ or "").split())[:300]
        claims = "Theorem" in c.__name__ or _CITATION_MARK.search(doc)
        if claims and c.role == "definition" and not _own_builder(c):
            offenders.append(name)
    assert not offenders, f"theorem-like rule(s) with role 'definition' and no proof builder: {offenders}"


def test_theorem_role_rules_have_a_proof_builder():
    pytest.importorskip("sympy")  # walks every module, jacopy.oracle included (sympy extra)
    # role "theorem" without a builder is tagged "axiom" by the engine
    # and lands as a LEGACY requirement — the citation never flows
    for name, c in _classes().items():
        if c.role == "theorem":
            assert _own_builder(c), name
