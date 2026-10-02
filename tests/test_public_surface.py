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
