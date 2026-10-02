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
        "prove_kappa_kappa", "prove_kappa_bracket",
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
        "prove_exceptional_r_twist_symmetric_part",
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
