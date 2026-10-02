"""Name clashes resolved without behaviour change (audit 0B00E1B-FULL
T2 names / K3).

* module files that shared a basename were renamed; the old module
  path stays importable and IS the moved module (same object, private
  names included, no warning);
* names that two different objects carried across subpackage
  ``__all__`` lists got an unambiguous name; the old name stays an
  attribute of its old module and package (same object).
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import warnings

import pytest

# old module path -> new module path
MODULE_RENAMES = {
    "jacopy.packages.metric_affine.koszul": "jacopy.packages.metric_affine.metric_koszul",
    "jacopy.packages.poisson.koszul": "jacopy.packages.poisson.koszul_forms",
    "jacopy.central.tangent.engine": "jacopy.central.tangent.tangent_expansion",
    "jacopy.central.algebroid.engine": "jacopy.central.algebroid.algebroid_expansion",
    "jacopy.packages.metric_affine.engine": "jacopy.packages.metric_affine.metric_affine_expansion",
}

# (package, old name, new name, defining module)
NAME_RENAMES = [
    ("jacopy.research", "Zero", "ZeroOperator", "jacopy.research.block_matrix"),
    ("jacopy.research", "antisymmetrize", "antisymmetrize_indices", "jacopy.research.antisymmetrize"),
    ("jacopy.algorithms", "normalize", "rewrite_to_fixpoint", "jacopy.algorithms.rewrite"),
    ("jacopy.core", "Provenance", "PropertyProvenance", "jacopy.core.properties"),
    ("jacopy.central.tangent", "prove_jacobi", "prove_lie_jacobi", "jacopy.central.tangent.lie_bracket"),
    ("jacopy.central.algebroid", "prove_cartan_magic_on_functions",
     "prove_algebroid_cartan_magic_on_functions", "jacopy.central.algebroid.calculus"),
    ("jacopy.central.algebroid", "prove_cartan_magic_on_one_forms",
     "prove_algebroid_cartan_magic_on_one_forms", "jacopy.central.algebroid.calculus"),
    ("jacopy.central.algebroid", "prove_d_squared_zero_on_functions",
     "prove_algebroid_d_squared_zero_on_functions", "jacopy.central.algebroid.calculus"),
    ("jacopy.central.algebroid", "prove_d_squared_zero_on_one_forms",
     "prove_algebroid_d_squared_zero_on_one_forms", "jacopy.central.algebroid.calculus"),
]


@pytest.mark.parametrize("old,new", sorted(MODULE_RENAMES.items()))
def test_old_module_path_is_the_new_module(old, new):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        old_mod = importlib.import_module(old)
        new_mod = importlib.import_module(new)
    assert old_mod is new_mod
    assert new_mod.__name__ == new
    # every name, private ones included, resolves to the same object
    for name, obj in vars(new_mod).items():
        if not name.startswith("__"):
            assert getattr(old_mod, name) is obj


def test_old_module_path_private_names():
    from jacopy.packages.metric_affine.koszul import _koszul_rhs
    from jacopy.packages.metric_affine.metric_koszul import _koszul_rhs as new
    from jacopy.packages.poisson.koszul import KoszulBracket, _engine
    from jacopy.packages.poisson.koszul_forms import KoszulBracket as KB2, _engine as e2

    assert _koszul_rhs is new and KoszulBracket is KB2 and _engine is e2
    assert KoszulBracket.__module__ == "jacopy.packages.poisson.koszul_forms"


def test_no_two_modules_share_a_basename_among_the_renamed():
    import pathlib

    import jacopy

    root = pathlib.Path(jacopy.__file__).parent
    shims = {root.joinpath(*o.split(".")[1:]).with_suffix(".py") for o in MODULE_RENAMES}
    stems = {}
    for p in root.rglob("*.py"):
        if p.name == "__init__.py" or p in shims:
            continue
        stems.setdefault(p.stem, []).append(p)
    for stem in ("koszul", "engine", "metric_koszul", "koszul_forms", "tangent_expansion",
                 "algebroid_expansion", "metric_affine_expansion"):
        assert len(stems.get(stem, [])) <= 1, (stem, stems.get(stem))


@pytest.mark.parametrize("pkg,old,new,home", NAME_RENAMES)
def test_renamed_name_old_and_new_are_one_object(pkg, old, new, home):
    p = importlib.import_module(pkg)
    h = importlib.import_module(home)
    assert getattr(p, new) is getattr(p, old) is getattr(h, old) is getattr(h, new)
    assert new in p.__all__ and old not in p.__all__


def test_old_import_statements_still_work():
    from jacopy.algorithms import normalize, rewrite_to_fixpoint
    from jacopy.central.algebroid import prove_cartan_magic_on_functions as a1
    from jacopy.central.algebroid import prove_algebroid_cartan_magic_on_functions as a2
    from jacopy.central.tangent import prove_jacobi, prove_lie_jacobi
    from jacopy.core import PropertyProvenance, Provenance
    from jacopy.research import Zero, ZeroOperator, antisymmetrize, antisymmetrize_indices

    assert normalize is rewrite_to_fixpoint and a1 is a2
    assert prove_jacobi is prove_lie_jacobi and Provenance is PropertyProvenance
    assert Zero is ZeroOperator and antisymmetrize is antisymmetrize_indices


def test_the_other_objects_keep_the_bare_names():
    import jacopy
    from jacopy.central.tangent.cartan import prove_cartan_magic_on_functions as tm
    from jacopy.core.expr import Zero
    from jacopy.core.symmetrize import antisymmetrize
    from jacopy.proof import Provenance, normalize, prove_jacobi

    import jacopy.central.objects as objects
    import jacopy.central.tangent as tangent

    assert jacopy.Zero is Zero and jacopy.normalize is normalize
    assert objects.antisymmetrize is antisymmetrize
    assert tangent.prove_cartan_magic_on_functions is tm
    assert Provenance.__module__ == "jacopy.proof.result"
    assert prove_jacobi.__module__ == "jacopy.proof.verifier"


def _fresh(code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-W", "error", "-c", code], capture_output=True, text=True
    )


@pytest.mark.parametrize("path", sorted(set(MODULE_RENAMES) | set(MODULE_RENAMES.values())))
def test_each_renamed_module_imports_alone_in_a_clean_process(path):
    r = _fresh(f"import {path}")
    assert r.returncode == 0, r.stderr[-2000:]


@pytest.mark.parametrize("old,new", sorted(MODULE_RENAMES.items()))
def test_old_path_first_then_new_in_a_clean_process(old, new):
    r = _fresh(
        "import importlib, sys\n"
        f"a = importlib.import_module({old!r})\n"
        f"b = importlib.import_module({new!r})\n"
        f"assert a is b and sys.modules[{old!r}] is b\n"
    )
    assert r.returncode == 0, r.stderr[-2000:]


# ------------------------------------------------------------ T2-4 / K3-4
# (defining module, private name, public name) — same object
PUBLIC_ALIASES = [
    ("jacopy.packages.poisson.tilde", "_normalized_by", "normalized_by"),
    ("jacopy.packages.drinfeld.tilde_calculus", "_tilde_engine", "nambu_tilde_engine"),
    ("jacopy.central.objects.frame", "_index_str", "frame_index_str"),
    ("jacopy.packages.drinfeld.double", "_ev", "evaluate_on_slots"),
    ("jacopy.packages.drinfeld.double", "_double_engine", "double_engine"),
    ("jacopy.packages.poisson.showcase", "_is_exact", "is_exact_form"),
    ("jacopy.packages.drinfeld.twist", "_twist_engine", "twist_engine"),
    ("jacopy.packages.generalized.exceptional_rotation", "_engine", "exceptional_rotation_engine"),
    ("jacopy.algorithms.normalize_alternating", "_sort_key", "structural_sort_key"),
    ("jacopy.proof.search", "_node_count", "node_count"),
]


@pytest.mark.parametrize("home,private,public", PUBLIC_ALIASES)
def test_public_alias_is_the_private_object(home, private, public):
    mod = importlib.import_module(home)
    assert getattr(mod, public) is getattr(mod, private)


def test_notebook_engine_names_are_on_the_facades():
    import jacopy.packages.drinfeld as dr
    import jacopy.packages.generalized as ge
    from jacopy.packages.drinfeld.twist import _twist_engine
    from jacopy.packages.generalized.exceptional_rotation import _engine

    assert dr.twist_engine is _twist_engine and "twist_engine" in dr.__all__
    assert ge.exceptional_rotation_engine is _engine
    assert "exceptional_rotation_engine" in ge.__all__


def _jacopy_sources():
    import pathlib

    import jacopy

    root = pathlib.Path(jacopy.__file__).parent
    for p in root.rglob("*.py"):
        rel = p.relative_to(root.parent).with_suffix("")
        mod = ".".join(rel.parts)
        yield (mod[: -len(".__init__")] if mod.endswith(".__init__") else mod), p.read_text(encoding="utf-8")


def test_publicized_helpers_are_not_imported_privately_across_modules():
    import ast

    wanted = {(home, private) for home, private, _ in PUBLIC_ALIASES}
    offenders = []
    for mod, src in _jacopy_sources():
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                for a in node.names:
                    if (node.module, a.name) in wanted and node.module != mod:
                        offenders.append((mod, node.module, a.name))
    assert not offenders, offenders


def test_notebooks_import_no_private_jacopy_names():
    import ast
    import json
    import pathlib

    import jacopy

    examples = pathlib.Path(jacopy.__file__).resolve().parents[1] / "examples"
    if not examples.is_dir():
        pytest.skip("installed package: no examples/ next to it")
    offenders = []
    for nb in sorted(examples.rglob("*.ipynb")):
        for i, cell in enumerate(json.loads(nb.read_text(encoding="utf-8"))["cells"]):
            if cell["cell_type"] != "code":
                continue
            for node in ast.walk(ast.parse("".join(cell["source"]))):
                if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("jacopy"):
                    offenders += [(nb.name, i, a.name) for a in node.names if a.name.startswith("_")]
    assert not offenders, offenders


def test_notebook_replacements_agree_with_the_old_helpers():
    import jacopy
    from jacopy.central.objects import forms, functions, vector_fields
    from jacopy.central.tangent.cartan import L
    from jacopy.core.registry import PropertyRegistry
    from jacopy.packages.drinfeld.double import _ev
    from jacopy.packages.drinfeld.twist import _twist_engine
    from jacopy.packages.poisson.nambu import nambu_structure
    from jacopy.packages.poisson.tilde import _normalized_by

    reg = PropertyRegistry()
    (f,) = functions("f", registry=reg)
    X, Y, Z, W, Q = vector_fields("X Y Z W Q")
    (om,) = forms("ω", degree=1)
    N = nambu_structure("Π", p=1)
    eng = _twist_engine(N, reg)
    e = L(X, om)
    old = _normalized_by(eng, e, reg)
    nf = jacopy.normalize(eng, e, reg)
    assert nf.stopped_by != "steps" and nf.expr == old
    for slots in ((Y, Z), (X, Y, Z, W, Q)):
        assert _ev(om, slots) == jacopy.multi_eval(om, *slots)
