"""Calculus on algebroids & Drinfel'd doubles (PDF item 13; Phase 6).

Primary sources (bibliography keys in :mod:`jacopy.bibliography`):

* **DD** = arXiv:2312.06584, Çatal-Özer, Doğan & Yetişmişoğlu (2024)
  (``CatalOzerDoganYetismisoglu2024``) — untwisted bialgebroids, the
  dual-calculus double, App D Nambu-Poisson claims;
* **TW** = arXiv:2409.11973, Çatal-Özer, Doğan & Yetişmişoğlu (2025)
  (``CatalOzerDoganYetismisoglu2025``) — twists, the general
  Roytenberg bracket, §8 examples.

The two papers number their equations independently (e.g. DD (4.19)
is the double's metric, TW (4.19) the bracket-morphism condition), so
every equation label in this package carries its paper prefix:
``[DD (4.17)]``, ``[TW (5.2)]``."""

from jacopy.packages.drinfeld.double import (
    canonical_pairing,
    dorfman_double,
    poisson_double,
    prove_dorfman_jacobi_form,
    prove_dorfman_right_leibniz_form,
    prove_dorfman_symmetric_part,
)
from jacopy.packages.drinfeld.poisson_bialgebroid import (
    kappa_cartan,
    kappa_tilde,
    lie_tilde_vf,
    prove_compat_condition_one,
    prove_compat_condition_three_p1,
    prove_compat_condition_two,
)
from jacopy.packages.drinfeld.calculus_conditions import (
    kappa,
    prove_calculus_condition_one,
    prove_calculus_condition_three,
    prove_calculus_condition_two,
    prove_kappa_bracket,
    prove_kappa_kappa,
)

__all__ = [
    "canonical_pairing",
    "dorfman_double",
    "poisson_double",
    "prove_dorfman_jacobi_form",
    "prove_dorfman_right_leibniz_form",
    "prove_dorfman_symmetric_part",
    "kappa_cartan",
    "kappa_tilde",
    "lie_tilde_vf",
    "prove_compat_condition_one",
    "prove_compat_condition_three_p1",
    "prove_compat_condition_two",
    "kappa",
    "prove_calculus_condition_one",
    "prove_calculus_condition_two",
    "prove_calculus_condition_three",
    "prove_kappa_bracket",
    "prove_kappa_kappa",
]
