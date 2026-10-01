"""
Exact defect formulas for the Cartan relations on an ALMOST-Lie
algebroid (Phase 6.G) — [2409.11973 App A, eqs (A.5)/(A.7)/(A.8)].

Phase 3.F proved the ⟺ statements (``d_E² = 0`` on functions ⟺
anchor morphism; on 1-forms the Lie theorem). Here the failures are
QUANTIFIED: each broken Cartan relation equals an exact combination
of the
predator ``𝒫_ρ(u,v) = [ρu, ρv]_Lie − ρ([u,v])`` and the Jacobiator
``𝒥(u,v,w)`` — the two diagnosis nodes of Phase 3 become the
CURVATURE of the calculus. On functions (A.7):

    ℒ_u ℒ_v f − ℒ_v ℒ_u f − ℒ_{[u,v]} f = 𝒫(u,v)(f),
    (d_E d_E f)(u,v)                    = 𝒫(u,v)(f),
    (ℒ_u d_E f)(v) − (d_E ℒ_u f)(v)    = 𝒫(u,v)(f);

on a 1-form μ (A.5), evaluated on ``w``:

    (ℒ_uℒ_vμ − ℒ_vℒ_uμ − ℒ_{[u,v]}μ)(w)
        = 𝒫(u,v)(ι_w μ) − μ(𝒥(u,v,w)),
    (d_E d_E μ)(u,v,w)
        = 𝒫(u,v)(ι_wμ) − 𝒫(u,w)(ι_vμ) + 𝒫(v,w)(ι_uμ)
          − μ(𝒥(u,v,w)),
    (ℒ_u d_E μ − d_E ℒ_u μ)(v,w)
        = 𝒫(u,v)(ι_wμ) − 𝒫(u,w)(ι_vμ) − μ(𝒥(u,v,w));

and the calculus conditions (A.8):

    (ℒ_u d_E ι_w η − d_E ι_{[u,w]} η − d_E ι_w ℒ_u η)(v)
        = 𝒫(u,v)(ι_w η),
    (ℒ_w d_E ι_v ω − d_E ι_w d_E ι_v ω)(u) = 𝒫(w,u)(ι_v ω).

**Scope (audit 0B00E1B-FULL M2-3).** The paper states them on an
almost-Lie algebroid (skew bracket + right Leibniz), where ``d_E`` is a
genuine exterior derivative. Read as identities of the ORDERED Palais
evaluation formulas (``d_E`` evaluated plain-multilinearly when the
bracket is not declared skew, M2-1), seven of the eight are
mathematically valid for every ℝ-bilinear bracket; the engine CLOSES
them on a bare algebroid (tested) — under extra declarations a
declared rule (e.g. ``J → 0``) may rewrite one side before the other is
recognized, so closure there is not claimed. The exception is
(A.5)-2, ``d_E² μ``: in general the bracket terms are

    μ([[u,v],w] − [[u,w],v] + [[v,w],u])
        = −μ(𝒥(u,v,w)) + μ(S(u,[v,w]) − S(v,[u,w])),
    S(a,b) := [a,b] + [b,a],

so the formula above NEEDS ``antisymmetric`` (S = 0);
:func:`prove_defect_d_squared_on_one_forms` fails honestly without it
and :func:`prove_defect_d_squared_on_one_forms_general` proves the
declaration-free version with the symmetric-part correction.

Corollaries: a declared ``anchor-morphism`` kills every ``𝒫`` and
``jacobi`` kills ``𝒥`` — recovering the 3.F closures.
"""

from __future__ import annotations

from typing import Optional

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Expr, Integer, Neg, Sum
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.objects.interior import Interior
from jacopy.central.algebroid.calculus import _engine, d_E, lie_E
from jacopy.central.algebroid.context import Algebroid
from jacopy.central.algebroid.operators import anchor_predator, jacobiator


def _P(alg: Algebroid, u: Expr, v: Expr, x: Expr) -> Expr:
    """Paper-convention predator action [eq (A.6)]:
    ``𝒫_ρ(u,v) = [ρu,ρv]_Lie − ρ([u,v])`` — the NEGATIVE of the v3
    :class:`Predator` node (``P_Φ = Φ[u,v] − [Φu,Φv]``)."""
    return Neg(Act(anchor_predator(alg, u, v), x))


def _iota(u: Expr, x: Expr) -> Expr:
    return Act(Interior(u), x)


def _prove(alg, node, registry, engine, max_steps):
    return ExpandAndSimplify().prove(
        node,
        Integer(0),
        registry=registry,
        engine=engine
        if engine is not None
        else _engine(alg, registry),
        max_steps=max_steps,
    )


# ------------------------------------------------------------------- #
# (A.7) — functions                                                    #
# ------------------------------------------------------------------- #


def prove_defect_lie_lie_on_functions(
    alg: Algebroid,
    u: Expr,
    v: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 4096,
) -> ProofChain:
    """(A.7)-1: the ``[ℒ,ℒ]`` commutator defect on functions IS the
    predator."""
    node = Sum(
        Act(lie_E(alg, u), Act(lie_E(alg, v), f)),
        Neg(Act(lie_E(alg, v), Act(lie_E(alg, u), f))),
        Neg(Act(lie_E(alg, alg.bracket(u, v)), f)),
        Neg(_P(alg, u, v, f)),
    )
    return _prove(alg, node, registry, engine, max_steps)


def prove_defect_d_squared_on_functions(
    alg: Algebroid,
    u: Expr,
    v: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 4096,
) -> ProofChain:
    """(A.7)-2: ``(d_E d_E f)(u,v) = 𝒫(u,v)(f)`` — the quantitative
    version of the 3.F ``d² = 0 ⟺ morphism`` theorem."""
    node = Sum(
        MultiEval(
            d_E(alg, d_E(alg, f)),
            u,
            v,
            slot_kind="vector",
        ),
        Neg(_P(alg, u, v, f)),
    )
    return _prove(alg, node, registry, engine, max_steps)


def prove_defect_lie_d_on_functions(
    alg: Algebroid,
    u: Expr,
    v: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 4096,
) -> ProofChain:
    """(A.7)-3: ``(ℒ_u d_E f)(v) − (d_E ℒ_u f)(v) = 𝒫(u,v)(f)``."""
    node = Sum(
        Pairing(Act(lie_E(alg, u), d_E(alg, f)), v),
        Neg(Pairing(d_E(alg, Act(lie_E(alg, u), f)), v)),
        Neg(_P(alg, u, v, f)),
    )
    return _prove(alg, node, registry, engine, max_steps)


# ------------------------------------------------------------------- #
# (A.5) — 1-forms                                                      #
# ------------------------------------------------------------------- #


def prove_defect_lie_lie_on_one_forms(
    alg: Algebroid,
    mu: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.5)-1: on a 1-form, the ``[ℒ,ℒ]`` defect gains the
    Jacobiator: ``𝒫(u,v)(ι_wμ) − μ(𝒥(u,v,w))``."""
    node = Sum(
        Pairing(
            Act(lie_E(alg, u), Act(lie_E(alg, v), mu)), w
        ),
        Neg(
            Pairing(
                Act(lie_E(alg, v), Act(lie_E(alg, u), mu)), w
            )
        ),
        Neg(
            Pairing(
                Act(lie_E(alg, alg.bracket(u, v)), mu), w
            )
        ),
        Neg(_P(alg, u, v, _iota(w, mu))),
        Pairing(mu, jacobiator(alg, u, v, w)),
    )
    return _prove(alg, node, registry, engine, max_steps)


def prove_defect_d_squared_on_one_forms(
    alg: Algebroid,
    mu: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.5)-2: ``(d_E d_E μ)(u,v,w)`` equals the alternating
    predator sum minus ``μ(𝒥(u,v,w))``.

    VALID ONLY FOR A SKEW BRACKET (declare ``antisymmetric``; the
    paper's almost-Lie setting): otherwise the symmetric-part terms of
    :func:`prove_defect_d_squared_on_one_forms_general` survive and
    this raises :class:`ProofFailure` (M2-3)."""
    node = Sum(
        MultiEval(
            d_E(alg, d_E(alg, mu)),
            u,
            v,
            w,
            slot_kind="vector",
        ),
        Neg(_P(alg, u, v, _iota(w, mu))),
        _P(alg, u, w, _iota(v, mu)),
        Neg(_P(alg, v, w, _iota(u, mu))),
        Pairing(mu, jacobiator(alg, u, v, w)),
    )
    return _prove(alg, node, registry, engine, max_steps)


def _S(alg: Algebroid, a: Expr, b: Expr) -> Expr:
    """Symmetric part ``S(a,b) = [a,b] + [b,a]`` (0 on a skew bracket)."""
    return Sum(alg.bracket(a, b), alg.bracket(b, a))


def prove_defect_d_squared_on_one_forms_general(
    alg: Algebroid,
    mu: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.5)-2 for ANY ℝ-bilinear bracket (ordered Palais evaluation,
    no declarations):

        (d_E d_E μ)(u,v,w) = 𝒫(u,v)(ι_wμ) − 𝒫(u,w)(ι_vμ) + 𝒫(v,w)(ι_uμ)
                             − μ(𝒥(u,v,w))
                             + μ(S(u,[v,w]) − S(v,[u,w])).

    The first-order ``ρ(·)μ([·,·])`` terms cancel pairwise; the
    second-order anchor terms give the predators; the bracket terms are
    ``μ([[u,v],w] − [[u,w],v] + [[v,w],u])``, which is the Jacobiator
    plus the symmetric-part correction (M2-3).

    The identity uses NO axiom, so by default it is proved with the
    engine of the declaration-free copy of ``alg`` (same name, anchor
    and bundle): declared rules such as ``J → 0`` would otherwise fire
    on one side only. It then holds in every declared context.

    COUPLING (pinned by a test): this relies on
    ``IntrinsicDDefinition`` recognizing a ``d`` by its CALCULUS NAME
    only (``Cartan-<alg.name>``). The copy's ``d`` is structurally a
    different node whenever ``alg`` declares ``antisymmetric`` (the
    skew flag is part of its key), yet the copy's Palais rule must
    still unroll ``alg``'s ``d``; the copy's bracket/anchor nodes are
    identical by name. If ``d`` matching ever becomes key-based, pass
    an ``engine`` explicitly."""
    node = Sum(
        MultiEval(
            d_E(alg, d_E(alg, mu)),
            u,
            v,
            w,
            slot_kind="vector",
        ),
        Neg(_P(alg, u, v, _iota(w, mu))),
        _P(alg, u, w, _iota(v, mu)),
        Neg(_P(alg, v, w, _iota(u, mu))),
        Pairing(mu, jacobiator(alg, u, v, w)),
        Neg(Pairing(mu, _S(alg, u, alg.bracket(v, w)))),
        Pairing(mu, _S(alg, v, alg.bracket(u, w))),
    )
    if engine is None:
        from jacopy.central.algebroid.context import algebroid

        bare = algebroid(
            alg.name, alg.bundle, anchor_name=alg.anchor_name, declare=()
        )
        engine = _engine(bare, registry)
    return _prove(alg, node, registry, engine, max_steps)


def prove_defect_lie_d_on_one_forms(
    alg: Algebroid,
    mu: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.5)-3: ``(ℒ_u d_E μ − d_E ℒ_u μ)(v,w) = 𝒫(u,v)(ι_wμ) −
    𝒫(u,w)(ι_vμ) − μ(𝒥(u,v,w))``."""
    node = Sum(
        MultiEval(
            Act(lie_E(alg, u), d_E(alg, mu)),
            v,
            w,
            slot_kind="vector",
        ),
        Neg(
            MultiEval(
                d_E(alg, Act(lie_E(alg, u), mu)),
                v,
                w,
                slot_kind="vector",
            )
        ),
        Neg(_P(alg, u, v, _iota(w, mu))),
        _P(alg, u, w, _iota(v, mu)),
        Pairing(mu, jacobiator(alg, u, v, w)),
    )
    return _prove(alg, node, registry, engine, max_steps)


# ------------------------------------------------------------------- #
# (A.8) — calculus conditions                                          #
# ------------------------------------------------------------------- #


def prove_defect_calculus_condition_two(
    alg: Algebroid,
    eta: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.8)-1: ``(ℒ_u d_E ι_w η − d_E ι_{[u,w]} η −
    d_E ι_w ℒ_u η)(v) = 𝒫(u,v)(ι_w η)``."""
    node = Sum(
        Pairing(
            Act(lie_E(alg, u), d_E(alg, _iota(w, eta))), v
        ),
        Neg(
            Pairing(
                d_E(alg, _iota(alg.bracket(u, w), eta)), v
            )
        ),
        Neg(
            Pairing(
                d_E(
                    alg,
                    _iota(w, Act(lie_E(alg, u), eta)),
                ),
                v,
            )
        ),
        Neg(_P(alg, u, v, _iota(w, eta))),
    )
    return _prove(alg, node, registry, engine, max_steps)


def prove_defect_calculus_condition_three(
    alg: Algebroid,
    omega: Expr,
    u: Expr,
    v: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    engine=None,
    max_steps: int = 8192,
) -> ProofChain:
    """(A.8)-2: ``(ℒ_w d_E ι_v ω − d_E ι_w d_E ι_v ω)(u) =
    𝒫(w,u)(ι_v ω)``."""
    node = Sum(
        Pairing(
            Act(lie_E(alg, w), d_E(alg, _iota(v, omega))), u
        ),
        Neg(
            Pairing(
                d_E(
                    alg,
                    Pairing(d_E(alg, _iota(v, omega)), w),
                ),
                u,
            )
        ),
        Neg(_P(alg, w, u, _iota(v, omega))),
    )
    return _prove(alg, node, registry, engine, max_steps)
