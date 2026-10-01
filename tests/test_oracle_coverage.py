"""Every ``Expr`` subclass of the library either has an oracle realizer
or is on the explicit UNSUPPORTED allowlist (SPEC §1) — a NEW node type
fails here until it is classified, so nothing passes silently. The
allowlist is the F2–F5 backlog (SPEC §1/§5)."""

import importlib
import pkgutil

import pytest

pytest.importorskip("sympy")

import jacopy
from jacopy.core.expr import Expr
from jacopy.oracle.realize import realizer_for

UNSUPPORTED_ALLOWLIST = {
    # abstract / generic bases and pattern atoms (always UNSUPPORTED)
    "jacopy.algebra.derivation.Derivation",
    "jacopy.core.expr.Atom",
    "jacopy.core.wildcards.SeqWildcard",
    "jacopy.core.wildcards.Wildcard",
    "jacopy.packages.generalized.bourbaki_precalculus._SlotAtom",
    "jacopy.proof.verifier._PropertyMarker",
    # F2: the binder token of α-normalized keys (never in a closed equation)
    "jacopy.core.indexed_sum._BoundSumToken",
    # F3: Poisson / tilde remainder
    "jacopy.packages.poisson.symplectic.SymplecticHamiltonianVF",
    "jacopy.packages.poisson.tilde.TildeAnholonomyCoefficient",
    # F4: metric-affine, tensors, musical maps
    "jacopy.central.objects.connection.CovariantOp",
    "jacopy.central.objects.endomorphism.EndoForm",
    "jacopy.central.objects.endomorphism.EndoVF",
    "jacopy.central.objects.metric.InverseMetric",
    "jacopy.central.objects.metric.Metric",
    "jacopy.central.objects.musical.Flat",
    "jacopy.central.objects.musical.Sharp",
    "jacopy.central.objects.tensor.Tensor",
    "jacopy.core.hodge.HodgeStar",
    "jacopy.core.symmetrize.Antisymmetrization",
    "jacopy.core.symmetrize.Symmetrization",
    "jacopy.core.tensor_product.TensorProduct",
    "jacopy.packages.metric_affine.frame_components.ConnectionCoefficient",
    "jacopy.packages.metric_affine.frame_components.ConnectionForm",
    "jacopy.packages.metric_affine.metric.InverseMetricComponent",
    "jacopy.packages.metric_affine.metric.MetricValue",
    "jacopy.packages.metric_affine.metric.NonMetricity",
    "jacopy.packages.metric_affine.torsion_curvature.Curvature",
    "jacopy.packages.metric_affine.torsion_curvature.Torsion",
    # F5: generalized / Courant / Drinfeld
    "jacopy.packages.generalized.bourbaki_exact.ChiSec",
    "jacopy.packages.generalized.bourbaki_exact.PhiSec",
    "jacopy.packages.generalized.bourbaki_precalculus.BD",
    "jacopy.packages.generalized.bourbaki_precalculus.BIota",
    "jacopy.packages.generalized.bourbaki_precalculus.BLieR",
    "jacopy.packages.generalized.bourbaki_precalculus.BLieZ",
    "jacopy.packages.generalized.bourbaki_precalculus.BSymbol",
    "jacopy.packages.generalized.bourbaki_structure.BDop",
    "jacopy.packages.generalized.bourbaki_structure.BLieRE",
    "jacopy.packages.generalized.bourbaki_structure.BMetric",
    "jacopy.packages.generalized.bourbaki_structure.BSymbolL",
    "jacopy.packages.generalized.courant_axioms.CourantD",
    "jacopy.packages.generalized.general_twist.PsiInvSec",
    "jacopy.packages.generalized.general_twist.PsiSec",
}


def _all_expr_classes():
    for m in pkgutil.walk_packages(jacopy.__path__, "jacopy."):
        importlib.import_module(m.name)
    out, stack = set(), [Expr]
    while stack:
        c = stack.pop()
        for s in c.__subclasses__():
            if s.__module__.startswith("jacopy.") and s not in out:
                out.add(s)
                stack.append(s)
    return out


def test_every_node_is_realized_or_allowlisted():
    classes = _all_expr_classes()
    names = {f"{c.__module__}.{c.__qualname__}" for c in classes}
    missing = sorted(f"{c.__module__}.{c.__qualname__}" for c in classes
                     if realizer_for(c) is None and f"{c.__module__}.{c.__qualname__}" not in UNSUPPORTED_ALLOWLIST)
    assert not missing, f"unclassified node types (add a realizer or allowlist them): {missing}"
    stale = sorted(UNSUPPORTED_ALLOWLIST - names)
    assert not stale, f"allowlist entries without a class: {stale}"
    realized_and_listed = sorted(n for c in classes for n in [f"{c.__module__}.{c.__qualname__}"]
                                 if n in UNSUPPORTED_ALLOWLIST and realizer_for(c) is not None)
    assert not realized_and_listed, realized_and_listed
