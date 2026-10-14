"""
The ABSTRACT main theorem of the double — the statement
"property subset + compatibility ⟹ the double satisfies
the same subset", realized as a FINITE DECLARATION SWEEP on the
abstract-algebroid layer (the engine proves instances, not
schemas; the sweep over declared subsets is the mechanical face of
the schema).

Construction: for an abstract algebroid ``A`` (a declaration
context) with its OWN Cartan calculus ``(d_E, ℒ^E, ι)``,
the abstract STANDARD double on ``A ⊕ Λᵖ A*`` is

    [u+α, v+β] := [u,v]_A ⊕ ( ℒ^E_u β − ℒ^E_v α + d_E ι_v α ).

Sweep results (each an ⟹ with an honest-fail partner):

* **right-Leibniz**: the double is right-Leibniz with anchor
  ``ρ(u+α) = u``  ⟺  ``A`` declares ``right-leibniz`` +
  ``left-leibniz`` + ``local`` — TW's "local almost-Leibniz"
  (TW §3, after TW (3.17)) hypothesis rediscovered mechanically,
  term by term: right-Leibniz alone leaves the left-Leibniz defect;
  adding left-Leibniz leaves EXACTLY ``⟨α, L(df,v,w)⟩`` — the
  locality operator — as the one-term residual, so ``local`` (L = 0) is forced.
* **symmetric part**: form component ``= d_E⟨e₁,e₂⟩₊`` needs NO
  declaration (the abstract Cartan magic theorem); the vector component
  ``[u,v]+[v,u] = 0`` is exactly the ``antisymmetric`` declaration.
* **Leibniz-Jacobi (form)**: closes under ``jacobi`` +
  ``anchor-morphism`` (+ right-leibniz), with bracket-level Jacobi
  entering as cited :func:`jacobi_combination_theorem` instances —
  and honest-fails when ``jacobi`` is withheld.

Scope: this is ONLY the tilde-free
(standard) double — the Z-side bracket and the tilde calculus are zero,
so the compatibility conditions of the paper's main theorem
[DD §4, (4.36)-(4.40)] never enter. The general statement "calculus +
dual calculus + compatibility ⟹ double" is NOT swept here. For the
concrete instantiations with a non-trivial tilde side: the Poisson /
Nambu double's symmetric part, right-Leibniz and (FI) anchor morphism
are proved in :mod:`double` / :mod:`bracket_morphism`; its
Leibniz-Jacobi is proved only for the FORM component and only via
the Π-twist (:func:`~jacopy.packages.drinfeld.twist.
prove_nambu_double_jacobi_via_twist`, FI declared, p = 1 in the SLOW
suite) — the vector component is open.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from jacopy.algebra.derivation import Act
from jacopy.core.expr import Expr, Integer, Neg, Product, Sum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.proof.chain import ProofChain
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.proof.theorems import Theorem, TheoremDefinition
from jacopy.central.objects.interior import Interior
from jacopy.central.algebroid.calculus import (
    _engine,
    d_E,
    jacobi_combination_theorem,
    lie_E,
)
from jacopy.central.algebroid.context import Algebroid


def _iota(u: Expr, x: Expr) -> Expr:
    return Act(Interior(u), x)


def _double_engine(alg: Algebroid, registry):
    """The abstract calculus engine LAYERED with the declaration
    engine — the calculus rules alone never see the declared axioms
    (anchor-morphism, Leibniz, locality), which is exactly what the
    sweep is about."""
    from jacopy.central.algebroid.algebroid_expansion import algebroid_engine

    eng = _engine(alg, registry)
    for d in algebroid_engine(alg, registry=registry).definitions:
        eng.register(d)
    return eng


def abstract_double(
    alg: Algebroid, u: Expr, alpha: Expr, v: Expr, beta: Expr
) -> Tuple[Expr, Expr]:
    """The abstract standard double bracket on ``A ⊕ Λᵖ A*`` as a
    ``(section, form)`` pair."""
    return (
        alg.bracket(u, v),
        Sum(
            Act(lie_E(alg, u), beta),
            Neg(Act(lie_E(alg, v), alpha)),
            d_E(alg, _iota(v, alpha)),
        ),
    )


def abstract_pairing(
    u: Expr, alpha: Expr, v: Expr, beta: Expr
) -> Expr:
    """``⟨e₁,e₂⟩₊ = ι_u β + ι_v α``."""
    return Sum(_iota(u, beta), _iota(v, alpha))


def prove_abstract_double_right_leibniz(
    alg: Algebroid,
    u: Expr,
    alpha: Expr,
    v: Expr,
    beta: Expr,
    f: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 30000,
) -> Tuple[ProofChain, ProofChain]:
    """The double's right-Leibniz law with anchor ``ρ(u+α) = u``,
    as an EXACT DEFECT FORMULA: under the "local"
    level (right- + left-Leibniz) the form-component defect is
    precisely the LOCALITY term,

        form([e₁, f·e₂]) − f·form([e₁,e₂]) − (ρ(e₁)f)·β
            ⟨·, w⟩ = ⟨α, L(df, v, w)⟩,

    (surfaced mechanically: the bare run leaves the left-Leibniz
    defect; the local run leaves exactly this one term). The vector
    component is plain right-Leibniz. Corollary: the double is
    right-Leibniz ⟺ the locality operator vanishes — an instance-form
    reading of TW (3.17) (the locality operator ``L_E``, defined in the
    paper through the LEFT-Leibniz defect) and its decomposition TW (5.8).
    The right-Leibniz ⟺ locality equivalence is this module's own
    derivation, not a statement printed in TW."""
    vec_l, form_l = abstract_double(
        alg, u, alpha, Product(f, v), Product(f, beta)
    )
    vec_b, form_b = abstract_double(alg, u, alpha, v, beta)
    anchor_f = Act(alg.anchor(u), f)
    eng = _double_engine(alg, registry)
    c_vec = ExpandAndSimplify().prove(
        Act(
            Sum(
                vec_l,
                Neg(
                    Sum(
                        Product(f, vec_b),
                        Product(anchor_f, v),
                    )
                ),
            ),
            f,
        ),
        Integer(0),
        registry=registry,
        engine=eng,
        max_steps=max_steps,
    )
    from jacopy.central.algebroid.context import locality_term

    c_form = ExpandAndSimplify().prove(
        Pairing(
            Sum(
                form_l,
                Neg(
                    Sum(
                        Product(f, form_b),
                        Product(anchor_f, beta),
                    )
                ),
            ),
            w,
        ),
        Pairing(alpha, Act(locality_term(alg, f, v, w), f))
        if False
        else Pairing(
            alpha, locality_term(alg, f, v, w)
        ),
        registry=registry,
        engine=eng,
        max_steps=max_steps,
    )
    return c_vec, c_form


def prove_abstract_double_symmetric_part(
    alg: Algebroid,
    u: Expr,
    alpha: Expr,
    v: Expr,
    beta: Expr,
    f: Expr,
    w: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 30000,
) -> Tuple[ProofChain, ProofChain]:
    """Symmetric part ``= (0, d_E⟨e₁,e₂⟩₊)``: the form component is
    DECLARATION-FREE (the abstract Cartan magic theorem); the vector component is
    exactly the ``antisymmetric`` declaration (honest-fail
    without)."""
    v12, f12 = abstract_double(alg, u, alpha, v, beta)
    v21, f21 = abstract_double(alg, v, beta, u, alpha)
    eng = _double_engine(alg, registry)
    c_vec = ExpandAndSimplify().prove(
        Act(Sum(v12, v21), f),
        Integer(0),
        registry=registry,
        engine=eng,
        max_steps=max_steps,
    )
    c_form = ExpandAndSimplify().prove(
        Pairing(
            Sum(
                f12,
                f21,
                Neg(
                    d_E(
                        alg,
                        abstract_pairing(u, alpha, v, beta),
                    )
                ),
            ),
            w,
        ),
        Integer(0),
        registry=registry,
        engine=eng,
        max_steps=max_steps,
    )
    return c_vec, c_form


def prove_abstract_double_jacobi_form(
    alg: Algebroid,
    u: Expr,
    alpha: Expr,
    v: Expr,
    beta: Expr,
    w: Expr,
    gamma: Expr,
    probe: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
    max_steps: int = 60000,
) -> Tuple[ProofChain, List[Theorem]]:
    """Form component of the double's Leibniz-Jacobi — the abstract
    form of the double theorem: closes under ``jacobi`` + ``anchor-morphism`` (+
    ``right-leibniz``), with the bracket-level Jacobi entering as
    cited :func:`jacobi_combination_theorem` instances. Honest-fail
    when ``jacobi`` is withheld. Evaluated against the probe section
    ``probe``."""

    def nest(u1, a1, u2, a2, u3, a3):
        iv, if_ = abstract_double(alg, u2, a2, u3, a3)
        return abstract_double(alg, u1, a1, iv, if_)[1]

    v12, f12 = abstract_double(alg, u, alpha, v, beta)
    lhs = Sum(
        nest(u, alpha, v, beta, w, gamma),
        Neg(abstract_double(alg, v12, f12, w, gamma)[1]),
        Neg(nest(v, beta, u, alpha, w, gamma)),
    )
    eng = _double_engine(alg, registry)
    used: List[Theorem] = []
    if alg.declares("jacobi"):
        from itertools import combinations

        from jacopy.packages.poisson.tilde import (
            normalized_by,
        )

        # Stage 1: normalize ALL ± lhs's in the citing engine BEFORE
        # registering any (registering the + variant
        # first makes the − seed normalize to 0 and get skipped,
        # while the slot residual carries exactly the − shape).
        staged = []
        for trip in combinations((u, v, w, probe), 3):
            thm = jacobi_combination_theorem(
                alg, *trip, registry=registry
            )
            for sgn, tag in (
                ((lambda x: x), ""),
                (Neg, "_neg"),
            ):
                lhs_nf = normalized_by(
                    eng, sgn(thm.lhs), registry
                )
                if lhs_nf == Integer(0):
                    continue
                staged.append((thm, tag, lhs_nf))
        # Stage 2: register.
        for thm, tag, lhs_nf in staged:
            variant = Theorem(
                name=thm.name + tag,
                statement=thm.statement,
                lhs=lhs_nf,
                rhs=Integer(0),
                proof=thm.proof,
                generality="instance",
                source=thm.source,  # copied from the cited record
            ).with_structural_requires()
            eng.register(TheoremDefinition(variant, allow_legacy=True))  # instance record: explicit
            used.append(variant)
    chain = ExpandAndSimplify().prove(
        Pairing(lhs, probe),
        Integer(0),
        registry=registry,
        engine=eng,
        max_steps=max_steps,
    )
    return chain, used
