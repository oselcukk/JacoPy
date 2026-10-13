"""Public surface of the library (DENETİM 0B00E1B-FULL T2-5/T2-6/T2-7/T2-9).

* every ``:mod:`` path a facade docstring points at imports and is not
  an empty placeholder (T2-5);
* package facades expose the user-path names and old deep import
  paths keep resolving to the SAME objects (T2-6);
* the top-level ``jacopy`` surface is explicit and every name is the
  expected object; no two ``__all__`` lists bind one name to two
  different objects beyond a documented allow-list (T2-7);
* packaging metadata: one version source, ``py.typed`` (T2-9).
"""

from __future__ import annotations

import importlib
import importlib.util
import pkgutil
import re

import pytest

import jacopy
import jacopy.packages

_MOD_REF = re.compile(r":mod:`~?(jacopy(?:\.\w+)+)`")


def _mod_refs(doc: str) -> list[str]:
    return sorted(set(_MOD_REF.findall(doc or "")))


# --------------------------------------------------------------- T2-5
class TestPackagesDocstringTargets:
    def test_every_referenced_module_exists_and_is_not_empty(self):
        refs = _mod_refs(jacopy.packages.__doc__)
        assert refs, "packages docstring lists no modules"
        for path in refs:
            mod = importlib.import_module(path)
            exported = getattr(mod, "__all__", None)
            assert exported, f"{path} is an empty placeholder"

    @pytest.mark.parametrize(
        "gone", ["jacopy.packages.algebroid_calculus", "jacopy.packages.research"]
    )
    def test_placeholders_removed(self, gone):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(gone)

    def test_item_13_and_15_have_real_homes(self):
        import jacopy.packages.drinfeld as dr
        import jacopy.research as rs

        assert "dorfman_double" in dr.__all__
        assert "AxiomSuite" in rs.__all__


# --------------------------------------------------------------- T2-6
_FACADES = (
    "jacopy.packages.drinfeld",
    "jacopy.packages.poisson",
    "jacopy.packages.generalized",
    "jacopy.packages.metric_affine",
)


@pytest.mark.parametrize("facade", _FACADES)
def test_facade_names_are_the_deep_objects(facade):
    """Every facade name is the very object of its defining module, so
    the old deep import paths and the facade agree (no wrappers)."""
    pkg = importlib.import_module(facade)
    assert len(pkg.__all__) == len(set(pkg.__all__))
    for name in pkg.__all__:
        obj = getattr(pkg, name)
        home = importlib.import_module(obj.__module__)
        assert getattr(home, name) is obj, (facade, name)
        assert obj.__module__.startswith(facade + "."), (facade, name)


# Facade names equal to a submodule name rebind the package attribute,
# so ``import pkg.sub as m`` returns the function, not the module. These
# predate the facade alignment; no new one may appear.
_SHADOWING_SUBMODULE = {
    "jacopy.packages.generalized": {"exceptional_double"},
    "jacopy.packages.metric_affine": {"metric", "e_connection"},
}


@pytest.mark.parametrize("facade", _FACADES)
def test_facade_names_do_not_shadow_submodules(facade):
    pkg = importlib.import_module(facade)
    subs = {m.name for m in pkgutil.iter_modules(pkg.__path__)}
    shadowing = set(pkg.__all__) & subs
    assert shadowing <= _SHADOWING_SUBMODULE.get(facade, set()), shadowing


def test_import_as_of_drinfeld_submodules_gives_modules():
    import types

    import jacopy.packages.drinfeld as dr

    for sub in pkgutil.iter_modules(dr.__path__):
        mod = importlib.import_module(f"{dr.__name__}.{sub.name}")
        assert isinstance(getattr(dr, sub.name), types.ModuleType), sub.name
        assert getattr(dr, sub.name) is mod


def test_drinfeld_facade_covers_item_13():
    import jacopy.packages.drinfeld as dr
    from jacopy.packages.drinfeld import double, examples, roytenberg, twist

    wanted = {
        "r_twist": twist.r_twist,
        "pi_twist": twist.pi_twist,
        "b_twist": twist.b_twist,
        "m_twist": twist.m_twist,
        "twisted_dorfman": twist.twisted_dorfman,
        "twisted_dorfman_h": twist.twisted_dorfman_h,  # the H-twist
        "dorfman_double_h": twist.dorfman_double_h,
        "roytenberg_bracket": roytenberg.roytenberg_bracket,
        "exceptional_courant_bracket": examples.exceptional_courant_bracket,
        "nambu_double": double.nambu_double,
    }
    for name, obj in wanted.items():
        assert name in dr.__all__ and getattr(dr, name) is obj


# Names the example notebooks reach by deep (public) import; each must
# now also be on its package facade.
_NOTEBOOK_DEEP_NAMES = {
    "jacopy.packages.drinfeld": [
        "dorfman_double", "canonical_pairing", "nambu_double", "r_twist",
        "twisted_dorfman", "prove_pi_twist_form_is_nambu",
        "prove_pi_twist_vec_is_nambu_plus_r", "prove_twisted_lie_tilde",
        "prove_twisted_kappa_tilde", "prove_twisted_z_bracket_is_koszul",
        "prove_tilde_calculus_condition_one", "prove_tilde_calculus_condition_two",
        "prove_tilde_calculus_condition_three", "prove_jacobi_compat_d8",
        "prove_jacobi_compat_d9", "prove_jacobi_compat_d10", "prove_jacobi_compat_d11",
        "prove_jacobi_compat_d12", "prove_jacobi_compat_d13",
        "prove_z_metric_invariance", "prove_a_mixing_condition",
        "prove_a_invariance_of_gz", "prove_dual_mixing_condition",
        "prove_double_metric_invariance", "prove_total_anchor_is_bracket_morphism",
        "prove_phi_z_is_morphism", "prove_morphism_compat_condition",
        "prove_morphism_compat_condition_dual",
        "prove_nambu_double_symmetric_part_vec", "prove_nambu_double_symmetric_part_form",
        "prove_nambu_double_right_leibniz_vec", "prove_nambu_double_right_leibniz_form",
        "exceptional_courant_bracket", "exceptional_pairing_two",
        "exceptional_pairing_five", "prove_exceptional_symmetric_part",
        "prove_exceptional_right_leibniz", "boxtimes", "prove_exceptional_twist_linear",
        "prove_exceptional_twist_inverse", "prove_exceptional_jacobi_five",
        "prove_top_slot_jacobi", "prove_calculus_condition_one",
        "prove_calculus_condition_two", "prove_calculus_condition_three",
        "prove_kappa_kappa", "prove_kappa_bracket", "twist_engine",
    ],
    "jacopy.packages.poisson": ["nambu_structure", "NambuSharpLinearityDefinition"],
    "jacopy.packages.generalized": [
        "prove_koszul_dialects_agree", "prove_theta_form_jacobi_by_citation",
        "rotated_exceptional_bracket", "prove_rotated_form_decomposition",
        "prove_rotated_vector_decomposition", "prove_boxtimes_components_are_413",
        "exceptional_double", "exceptional_r_twist", "exceptional_r_twist_components",
        "prove_rotated_is_exceptional_double_plus_r",
        "prove_exceptional_r_twist_bidegree_split",
        "prove_r22_reduces_to_lifted_cross_term",
        "prove_r25_is_lie_tilde_equivariance_defect",
        "prove_exceptional_r_twist_symmetric_part", "exceptional_rotation_engine",
    ],
}


@pytest.mark.parametrize("facade", sorted(_NOTEBOOK_DEEP_NAMES))
def test_notebook_deep_imports_are_on_the_facade(facade):
    pkg = importlib.import_module(facade)
    missing = [n for n in _NOTEBOOK_DEEP_NAMES[facade] if n not in pkg.__all__]
    assert not missing, missing


def test_old_deep_paths_still_import():
    from jacopy.packages.drinfeld.double import _ev  # noqa: F401  (notebook path)
    from jacopy.packages.drinfeld.twist import (  # noqa: F401
        FormProductToWedgeDefinition,
        WedgeSumScalarDefinition,
        _twist_engine,
    )
    from jacopy.packages.drinfeld.calculus_conditions import iota, lie  # noqa: F401
    from jacopy.packages.drinfeld.tilde_calculus import d_tilde, iota_tilde  # noqa: F401
    from jacopy.packages.poisson.tilde import _normalized_by  # noqa: F401
    from jacopy.packages.generalized.exceptional_rotation import _engine  # noqa: F401
    from jacopy.packages.metric_affine.metric import Metric, metric  # noqa: F401


# --------------------------------------------------------------- T2-7
_TOP_LEVEL = {
    "jacopy.core.expr": [
        "Expr", "Atom", "Symbol", "Integer", "Rational", "Sum", "Product",
        "Power", "Neg", "Zero", "One", "NegOne",
    ],
    "jacopy.core": ["PropertyRegistry", "default_registry", "Wedge", "MultiEval"],
    "jacopy.algebra": ["Act", "Derivation"],
    "jacopy.central.objects": [
        "Bundle", "TM", "tangent_bundle", "functions", "vector_fields", "forms",
        "p_vectors", "bivector", "tensors", "metric", "Metric", "hodge",
        "connection", "covariant_derivative", "frame", "coframe", "pairing",
        "Pairing", "wedge", "multi_eval", "interior",
    ],
    "jacopy.central.tangent": [
        "lie_bracket", "lie_derivative", "exterior_d", "sn_bracket",
    ],
    "jacopy.proof": [
        "show_equal", "prove", "ProofChain", "ProofStep", "ProofFailure",
        "ProofResult", "Goal", "Assumption", "Theorem", "TheoremBook", "cite",
        "normalize", "NormalForm", "Definition", "ExpansionEngine",
    ],
    "jacopy.display": [
        "display_expr", "display_chain", "display_theorem", "print_expr",
        "print_chain", "to_latex", "to_ascii", "theorem_to_latex_document",
    ],
}


class TestTopLevelSurface:
    def test_all_is_exactly_the_documented_surface(self):
        expected = [n for names in _TOP_LEVEL.values() for n in names]
        assert sorted(jacopy.__all__) == sorted(expected)
        assert len(jacopy.__all__) == len(set(jacopy.__all__))

    @pytest.mark.parametrize("home", sorted(_TOP_LEVEL))
    def test_every_name_is_its_home_object(self, home):
        mod = importlib.import_module(home)
        for name in _TOP_LEVEL[home]:
            assert getattr(jacopy, name) is getattr(mod, name), name

    def test_canonical_choice_for_shared_names(self):
        from jacopy.central.objects.metric import Metric, metric
        from jacopy.core.expr import Zero
        from jacopy.proof.normalize import normalize
        from jacopy.proof.result import ProofResult
        from jacopy.proof.search import prove
        from jacopy.proof.theorems import Theorem
        from jacopy.proof.verifier import show_equal

        assert jacopy.Zero is Zero
        assert jacopy.metric is metric and jacopy.Metric is Metric
        assert jacopy.normalize is normalize
        assert jacopy.show_equal is show_equal and jacopy.prove is prove
        assert jacopy.ProofResult is ProofResult and jacopy.Theorem is Theorem
        for ambiguous in ("Provenance", "antisymmetrize", "prove_jacobi"):
            assert ambiguous not in jacopy.__all__

    def test_star_import_and_dir(self):
        ns: dict = {}
        exec("from jacopy import *", ns)
        assert set(jacopy.__all__) <= set(ns)
        assert set(jacopy.__all__) <= set(dir(jacopy))
        with pytest.raises(AttributeError):
            jacopy.no_such_name  # noqa: B018

    def test_docstring_is_current(self):
        doc = jacopy.__doc__
        assert "under construction" not in doc
        assert "will arrive" not in doc
        for name in ("show_equal", "ProofResult", "Theorem", "jacopy.research"):
            assert name in doc


# Names that two different objects carry across the subpackage __all__
# lists, each owned outside the facade lane; a NEW collision fails.
# The other nine (Provenance, Zero, antisymmetrize, normalize, the four
# central prove_cartan_magic_* / prove_d_squared_zero_* pairs and
# prove_jacobi) were resolved by unambiguous names in the second
# package's __all__ (audit 0B00E1B-FULL T2 names); the old names stay
# importable as attributes (tests/test_audit_0b00e1b_arch_names.py).
_KNOWN_COLLISIONS = {
    "Metric",  # central atom vs metric_affine context (until the metric adapter lands)
    "metric",
}


def test_no_new_same_name_different_object():
    owners: dict[str, dict[int, str]] = {}
    packages = ["jacopy"] + [
        m.name for m in pkgutil.walk_packages(jacopy.__path__, "jacopy.") if m.ispkg
    ]
    for pkg_name in packages:
        if pkg_name.startswith("jacopy.oracle") and importlib.util.find_spec(
            "sympy"
        ) is None:  # the oracle needs the optional sympy (extra "oracle")
            continue
        pkg = importlib.import_module(pkg_name)
        for name in getattr(pkg, "__all__", None) or ():
            owners.setdefault(name, {})[id(getattr(pkg, name))] = pkg_name
    clashes = {n for n, objs in owners.items() if len(objs) > 1}
    assert clashes <= _KNOWN_COLLISIONS, sorted(clashes - _KNOWN_COLLISIONS)


# --------------------------------------------------------------- T2-9
_REPO = __import__("pathlib").Path(jacopy.__file__).resolve().parents[1]


def test_py_typed_ships_with_the_package():
    marker = __import__("pathlib").Path(jacopy.__file__).with_name("py.typed")
    assert marker.is_file()


def test_version_has_one_source():
    from importlib import metadata

    assert isinstance(jacopy.__version__, str) and jacopy.__version__
    try:
        installed = metadata.version("jacopy")
    except metadata.PackageNotFoundError:  # pragma: no cover - source tree only
        return
    assert installed == jacopy.__version__


def _pyproject():
    tomllib = pytest.importorskip("tomllib")
    path = _REPO / "pyproject.toml"
    if not path.is_file():
        pytest.skip("installed package: no pyproject.toml next to it")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_pyproject_reads_the_version_from_the_package():
    project = _pyproject()
    assert "version" not in project["project"]
    assert "version" in project["project"]["dynamic"]
    assert project["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "jacopy.__version__"
    }
    assert "py.typed" in project["tool"]["setuptools"]["package-data"]["jacopy"]


# extra requirement -> the import name it must be used under in jacopy/
_IMPORT_NAME = {"sympy": "sympy", "rich": "rich", "pytest": None, "ipykernel": None}


def test_runtime_extras_are_imported_somewhere():
    """Every runtime extra (not the test/notebook tooling) names a
    package that jacopy/ actually imports."""
    extras = _pyproject()["project"]["optional-dependencies"]
    sources = "\n".join(
        p.read_text(encoding="utf-8") for p in (_REPO / "jacopy").rglob("*.py")
    )
    for extra, reqs in extras.items():
        for req in reqs:
            dist = re.split(r"[<>=!~\[; ]", req, maxsplit=1)[0]
            assert dist in _IMPORT_NAME, f"extra {extra!r}: unknown {dist!r}"
            mod = _IMPORT_NAME[dist]
            if mod is not None:
                assert re.search(rf"^\s*(import|from) {mod}\b", sources, re.M), (
                    extra,
                    dist,
                )
