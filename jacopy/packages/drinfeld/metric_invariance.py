"""
Metric-invariance compatibility conditions (Phase 6.I.1) — DD App D
[DD = arXiv:2312.06584] eqs DD (D.14)-(D.19) [the DD (4.44)-(4.50)
family in tilde instantiation]: the ``g_Z`` metric layer born in
6.D/6.F closes the metric-invariance axis of the bialgebroid programme.

* **DD (D.14)** — the Z-side invariance: the metric-invariance operator
  of ``Z = Λᵖ T*M`` is ``ℒ̃_ω = ℒ_{ρ_Z(ω)} = ℒ_{Πω}``,

      g_Z([ω,η]_Kos, μ) + g_Z(η, [ω,μ]_Kos) = ℒ_{Πω} g_Z(η,μ).

* **DD (D.16)** — the A-side mixing condition is the lie-iota Cartan
  relation: ``ℒ_U ι_V μ = ι_{[U,V]} μ + ι_V ℒ_U μ``.

* **DD (D.17)** — the A-invariance of ``g_Z`` carries exact ``𝒦̃``
  corrections:

      ℒ_U g_Z(η,μ) = g_Z(ℒ_Uη, μ) + g_Z(η, ℒ_Uμ)
                     + ι_{𝒦̃_η U} μ + ι_{𝒦̃_μ U} η.

* **DD (D.18)** — the dual mixing condition with the tilde Lie
  derivative:

      ℒ_{Πω} ι_W η = ι_W ℒ_{Πω} η + ι_{ℒ̃_ω W} η
                     − ι_{Π(ι_W dω)} η.

* **DD (D.19) / Claim 6** — the DOUBLE-level metric invariance: the
  operator is the Lie derivative along the TOTAL anchor,

      ℒ_{U₁+Πω₁} g_E(e₂, e₃) = g_E([e₁,e₂], e₃) + g_E(e₂, [e₁,e₃]),

  with ``g_E(e₂,e₃) = ι_{U₂}η₃ + ι_{U₃}η₂ + g_Z(η₂,η₃)`` (½ of the
  summed DD (6.20) components in the code's ``g_Z`` normalisation —
  see :func:`double_metric`) and ``[·,·]`` the Nambu double. The
  declared FI enters exactly where the paper's derivation invokes
  the bracket morphism (sharp-sharp brackets in the cross terms); the
  FISharpPairingSwap consequence handles the ``Π(d g_Z)`` faces.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.objects.interior import Interior
from jacopy.central.tangent.exterior import CARTAN_TM, d
from jacopy.packages.drinfeld.double import (
    _ev,
    lie_tilde_nambu,
    nambu_double,
)
from jacopy.packages.drinfeld.tilde_calculus import (
    _tilde_engine,
    g_z_pairing,
    kappa_tilde_nambu,
)
from jacopy.packages.poisson.nambu import nambu_koszul_bracket


def _L(X: Expr, x: Expr) -> Expr:
    return Act(CARTAN_TM.lie(X), x)


def _iota(X: Expr, x: Expr) -> Expr:
    return Act(Interior(X), x)


def _maybe_ev(node: Expr, slots) -> Expr:
    """At p = 1 the g_Z-level statements are SCALARS (0 slots):
    prove them raw; otherwise evaluate on the given slots."""
    return node if not slots else _ev(node, slots)


def _prove(N, node, registry, declare_fi, max_steps):
    return ExpandAndSimplify().prove(
        node,
        Integer(0),
        registry=registry,
        engine=_tilde_engine(N, registry, declare_fi=declare_fi),
        max_steps=max_steps,
    )


def prove_z_metric_invariance(
    N,
    omega: Expr,
    eta: Expr,
    mu: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    declare_fi: bool = True,
    max_steps: int = 60000,
) -> ProofChain:
    """DD (D.14): ``g_Z([ω,η]_Kos, μ) + g_Z(η, [ω,μ]_Kos) =
    ℒ_{Πω} g_Z(η,μ)`` — the Z-side metric-invariance operator is
    ``ℒ_{Πω}`` DD (D.15). Uses the declared FI where the paper invokes
    the bracket morphism. Evaluated on ``p−1`` slots (scalar at
    p = 1: pass ``slots=[]`` … handled by the ``_ev`` helper via a
    single probe)."""
    node = _maybe_ev(
        Sum(
            g_z_pairing(
                N, nambu_koszul_bracket(N, omega, eta), mu
            ),
            g_z_pairing(
                N, eta, nambu_koszul_bracket(N, omega, mu)
            ),
            Neg(
                _L(N.sharp_vf(omega), g_z_pairing(N, eta, mu))
            ),
        ),
        slots,
    )
    return _prove(N, node, registry, declare_fi, max_steps)


def prove_a_mixing_condition(
    N,
    U: Expr,
    V: Expr,
    mu: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 30000,
) -> ProofChain:
    """DD (D.16): ``ℒ_U ι_V μ = ι_{[U,V]} μ + ι_V ℒ_U μ`` — the A-side
    mixing condition IS the lie-iota Cartan relation.
    Declaration-free."""
    from jacopy.central.tangent.lie_bracket import lie_bracket

    node = _maybe_ev(
        Sum(
            _L(U, _iota(V, mu)),
            Neg(_iota(lie_bracket(U, V), mu)),
            Neg(_iota(V, _L(U, mu))),
        ),
        slots,
    )
    return _prove(N, node, registry, False, max_steps)


def prove_a_invariance_of_gz(
    N,
    U: Expr,
    eta: Expr,
    mu: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 60000,
) -> ProofChain:
    """DD (D.17): the A-invariance of ``g_Z`` with its exact ``𝒦̃``
    corrections,

        ℒ_U g_Z(η,μ) = g_Z(ℒ_Uη, μ) + g_Z(η, ℒ_Uμ)
                       + ι_{𝒦̃_η U} μ + ι_{𝒦̃_μ U} η.

    Declaration-free (the ``[U,Πη]`` legs decompose through the
    ``𝒦̃`` face without the morphism)."""
    node = _maybe_ev(
        Sum(
            _L(U, g_z_pairing(N, eta, mu)),
            Neg(g_z_pairing(N, _L(U, eta), mu)),
            Neg(g_z_pairing(N, eta, _L(U, mu))),
            Neg(_iota(kappa_tilde_nambu(N, eta, U), mu)),
            Neg(_iota(kappa_tilde_nambu(N, mu, U), eta)),
        ),
        slots,
    )
    return _prove(N, node, registry, False, max_steps)


def prove_dual_mixing_condition(
    N,
    omega: Expr,
    eta: Expr,
    W: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 60000,
) -> ProofChain:
    """DD (D.18): the dual mixing condition,

        ℒ_{Πω} ι_W η = ι_W ℒ_{Πω} η + ι_{ℒ̃_ω W} η
                       − ι_{Π(ι_W dω)} η.

    Declaration-free (lie-iota + the ℒ̃ definition).

    Citation caveat: the printed DD (D.18) mixes ``V`` and ``W`` (its
    left side contracts with ``ι_V``, its right side is
    ``2ℒ_{Πω} ι_W η``) and carries the paper's ``g_Z`` factor 2, so it
    does not match this identity term by term. Expanding ``ℒ̃_ω W``
    (DD (6.6)) the statement here is the standard Cartan identity
    ``ℒ_{Πω} ι_W η = ι_W ℒ_{Πω} η + ι_{[Πω,W]} η`` — the content the
    first dual condition of DD (4.50) needs."""
    node = _maybe_ev(
        Sum(
            _L(N.sharp_vf(omega), _iota(W, eta)),
            Neg(_iota(W, _L(N.sharp_vf(omega), eta))),
            Neg(_iota(lie_tilde_nambu(N, omega, W), eta)),
            _iota(N.sharp_vf(_iota(W, d(omega))), eta),
        ),
        slots,
    )
    return _prove(N, node, registry, False, max_steps)


def double_metric(
    N, U2: Expr, eta2: Expr, U3: Expr, eta3: Expr
) -> Expr:
    """``g_E(e₂, e₃) = ι_{U₂}η₃ + ι_{U₃}η₂ + g_Z(η₂, η₃)`` — the
    form-valued metric of the Nambu double. Source: DD (6.20),
    ``g_E = 0 ⊕ (ι̃_ωV + ι̃_ηU) ⊕ 2(ι_{Πω}η + ι_{Πη}ω) ⊕ (ι_Uη + ι_Vω)``
    (equivalently TW (5.22) with ``g_A = g_R = g_H = 0``; "(5.22)" is a
    TW label — DD has no equation (5.22)). The code keeps ONE form,
    not the four bundle components: since ``ι̃_ωV = ι_Vω`` the two pairing
    components coincide, and with the code's ``g_Z`` (½ of DD (6.17))
    this ``g_E`` is exactly ½ × (sum of the four DD (6.20)
    components). Invariance is homogeneous, so the factor is harmless."""
    return Sum(
        _iota(U2, eta3),
        _iota(U3, eta2),
        g_z_pairing(N, eta2, eta3),
    )


def prove_double_metric_invariance(
    N,
    U1: Expr,
    om1: Expr,
    U2: Expr,
    om2: Expr,
    U3: Expr,
    om3: Expr,
    slots,
    *,
    registry: Optional[PropertyRegistry] = None,
    declare_fi: bool = True,
    max_steps: int = 90000,
) -> ProofChain:
    """DD (D.19) / **Claim 6**: the metric-invariance operator of the
    double is the Lie derivative along the TOTAL anchor,

        ℒ_{U₁+Πω₁} g_E(e₂,e₃)
            = g_E([e₁,e₂], e₃) + g_E(e₂, [e₁,e₃]),

    with ``[·,·]`` the Nambu double. The declared FI enters through
    the sharp-sharp cross brackets (as in the paper's derivation)."""
    rho1 = Sum(U1, N.sharp_vf(om1))
    v12, f12 = nambu_double(N, U1, om1, U2, om2)
    v13, f13 = nambu_double(N, U1, om1, U3, om3)
    node = _maybe_ev(
        Sum(
            _L(rho1, double_metric(N, U2, om2, U3, om3)),
            Neg(double_metric(N, v12, f12, U3, om3)),
            Neg(double_metric(N, U2, om2, v13, f13)),
        ),
        slots,
    )
    return _prove(N, node, registry, declare_fi, max_steps)
