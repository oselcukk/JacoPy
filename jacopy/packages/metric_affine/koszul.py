"""Compatibility path: this module moved to :mod:`jacopy.packages.metric_affine.metric_koszul`.

It is the Koszul-formula family of the metric-affine package (Levi-Civita); not the Poisson Koszul bracket. The file was renamed so that no two modules of the
package share a basename; this old path
stays importable and IS the moved module — ``import jacopy.packages.metric_affine.koszul`` returns
the very module object :mod:`jacopy.packages.metric_affine.metric_koszul`, so every name (private ones
included) keeps resolving to the same object, with no warning.
"""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("jacopy.packages.metric_affine.metric_koszul")
