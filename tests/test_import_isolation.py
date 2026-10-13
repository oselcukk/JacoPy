"""Every jacopy (sub)package imports on its own in a fresh interpreter
(independent audit of commit 0b00e1b,
items T2-6/T2-7): widening the ``__init__`` facades must
not create an import-order dependency or a cycle that only a warm
``sys.modules`` hides."""

from __future__ import annotations

import importlib.util
import os
import pkgutil
import subprocess
import sys
from pathlib import Path

import pytest

import jacopy

_ROOT = Path(jacopy.__file__).resolve().parents[1]
_PACKAGES = sorted(
    ["jacopy"]
    + [m.name for m in pkgutil.walk_packages(jacopy.__path__, "jacopy.") if m.ispkg]
)


# subpackage prefix -> the optional dependency (extra) it needs
_OPTIONAL = {"jacopy.oracle": "sympy"}


@pytest.mark.parametrize("package", _PACKAGES)
def test_package_imports_in_a_clean_process(package):
    for prefix, dist in _OPTIONAL.items():
        if package.startswith(prefix) and importlib.util.find_spec(dist) is None:
            pytest.skip(f"{package} needs the optional {dist!r}")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(_ROOT), env.get("PYTHONPATH", "")) if p
    )
    code = (
        f"import importlib; m = importlib.import_module({package!r}); "
        "[getattr(m, n) for n in getattr(m, '__all__', ())]"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]


def test_top_level_surface_is_lazy():
    """``import jacopy`` (and so ``import jacopy.oracle``) must not pull
    the proof layer in: the oracle's independence and the import cost of
    ``jacopy.core`` are unchanged by the wider top-level surface."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(_ROOT), env.get("PYTHONPATH", "")) if p
    )
    code = (
        "import sys, jacopy.oracle; "
        "bad = sorted(m for m in sys.modules if m.startswith(('jacopy.proof', "
        "'jacopy.central', 'jacopy.packages', 'jacopy.research', 'jacopy.display'))); "
        "assert not bad, bad; "
        "import jacopy; jacopy.show_equal; "
        "assert 'jacopy.proof' in sys.modules"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=str(_ROOT), env=env,
        capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
