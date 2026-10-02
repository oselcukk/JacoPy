"""The oracle must stay independent of the engine it checks (SPEC §1):
no import of ``jacopy.proof`` / ``jacopy.algorithms``, no ``*Definition``
/ ``*Declaration`` rule, and from the rest of jacopy only expression-node
CLASSES (plus a few inert markers). Enforced by an AST scan of every
module of ``jacopy/oracle``."""

import ast
import importlib
from pathlib import Path

import jacopy
from jacopy.core.expr import Expr

ORACLE = Path(jacopy.__file__).parent / "oracle"
FORBIDDEN_PREFIXES = ("jacopy.proof", "jacopy.algorithms")
#: non-node names the oracle may import from jacopy: the tangent bundle
#: marker (bundle check) and the registry property classes (scalar
#: contract) — data markers, no rewriting logic.
ALLOWED_NON_NODES = {
    ("jacopy.central.objects.bundle", "TM"),
    ("jacopy.core.properties", "Scalar"),
    ("jacopy.core.properties", "Graded"),
    ("jacopy.core.properties", "NonCommuting"),
    ("jacopy.core.properties", "AntiCommuting"),
}


def _imports():
    for path in sorted(ORACLE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    yield path, a.name, None
            elif isinstance(node, ast.ImportFrom) and node.module:
                for a in node.names:
                    yield path, node.module, a.name


def test_oracle_modules_exist():
    names = {p.name for p in ORACLE.rglob("*.py")}
    assert {"values.py", "realize.py", "check.py", "report.py", "hook.py", "tangent.py"} <= names


def test_no_engine_imports():
    bad = [(p.name, m, n) for p, m, n in _imports() if m.startswith(FORBIDDEN_PREFIXES)]
    assert not bad, bad


def test_no_rule_imports():
    bad = [(p.name, m, n) for p, m, n in _imports()
           if n and (n.endswith("Definition") or n.endswith("Declaration"))]
    assert not bad, bad


def test_only_node_classes_from_jacopy():
    bad = []
    for p, mod, name in _imports():
        if not mod.startswith("jacopy.") or mod.startswith("jacopy.oracle"):
            continue
        if name is None:
            bad.append((p.name, mod, "module import"))
            continue
        if (mod, name) in ALLOWED_NON_NODES:
            continue
        obj = getattr(importlib.import_module(mod), name)
        if not (isinstance(obj, type) and issubclass(obj, Expr)):
            bad.append((p.name, mod, name))
    assert not bad, bad
