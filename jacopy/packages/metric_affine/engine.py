"""Compatibility path: this module moved to :mod:`jacopy.packages.metric_affine.metric_affine_expansion`.

It is the metric-affine package engine (``metric_affine_engine``). The file was renamed so that no two modules of the
package share a basename (audit 0B00E1B-FULL T2 names); this old path
stays importable and IS the moved module — ``import jacopy.packages.metric_affine.engine`` returns
the very module object :mod:`jacopy.packages.metric_affine.metric_affine_expansion`, so every name (private ones
included) keeps resolving to the same object, with no warning.
"""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("jacopy.packages.metric_affine.metric_affine_expansion")
