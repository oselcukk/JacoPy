"""Compatibility path: this module moved to :mod:`jacopy.packages.poisson.koszul_forms`.

It is the Koszul bracket of a Poisson bivector on 1-forms; not the metric Koszul formula. The file was renamed so that no two modules of the
package share a basename; this old path
stays importable and IS the moved module — ``import jacopy.packages.poisson.koszul`` returns
the very module object :mod:`jacopy.packages.poisson.koszul_forms`, so every name (private ones
included) keeps resolving to the same object, with no warning.
"""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("jacopy.packages.poisson.koszul_forms")
