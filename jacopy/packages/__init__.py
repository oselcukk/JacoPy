"""Packages (PDF item 7): geometry built on top of the central code.

Each sub-package has a facade (``from jacopy.packages.<name> import …``)
whose ``__all__`` lists its supported entry points: object/bracket
constructors, ``prove_*`` theorem functions and the package's own
rewrite rules. Deeper module paths keep working but are not part of
the facade.

* :mod:`~jacopy.packages.metric_affine` — metric-affine geometry
  (torsion, curvature, non-metricity, Ricci, Einstein, Bianchi,
  Cartan structure, Koszul, Schouten; E-connections and admissible
  connections on an algebroid) — item 11.
* :mod:`~jacopy.packages.poisson` — symplectic, Poisson,
  Nambu-Poisson; Koszul bracket, tilde-calculus — item 12.
* :mod:`~jacopy.packages.drinfeld` — calculus on algebroids &
  Drinfel'd doubles: tilde-calculus on A and Z, twist procedures
  (π/B/H/R/M-twists), the general Roytenberg bracket and the
  exceptional/BN examples — item 13.
* :mod:`~jacopy.packages.generalized` — generalized geometry: Courant
  algebroid, Dorfman/Courant bracket, H-twist — item 14.

Item 15 (research interface: pick a bracket/object, define new
objects, prove properties) lives one layer up, in
:mod:`jacopy.research`, because it combines several packages.
"""
