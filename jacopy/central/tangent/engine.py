"""Compatibility path: this module moved to :mod:`jacopy.central.tangent.tangent_expansion`.

It is the TM expansion engine (``tangent_engine``). The file was renamed so that no two modules of the
package share a basename; this old path
stays importable and IS the moved module — ``import jacopy.central.tangent.engine`` returns
the very module object :mod:`jacopy.central.tangent.tangent_expansion`, so every name (private ones
included) keeps resolving to the same object, with no warning.
"""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module("jacopy.central.tangent.tangent_expansion")
