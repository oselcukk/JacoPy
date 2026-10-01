"""Model-oracle F2 control suite: algebroids, frames, indexed sums.

POSITIVE controls are textbook algebroid identities that must be AGREE
in the declared models (a failure means a realizer's convention does not
match the library's); NEGATIVE controls must be DISAGREE — among them
the audit's P0-4 (``d(m)(u,u) = 0`` at the leibniz / courant levels),
P0-5 (the L_E product rule without declared right Leibniz) and the M7-1
cubic / derivative coframe-recombination counter-examples; LEAK controls
must be ASSUMPTION_LEAK (a Jacobi-dependent equation whose record does
not show ``jacobi``)."""

from types import SimpleNamespace

import pytest

pytest.importorskip("sympy")

from jacopy.algebra.derivation import Act
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.central.algebroid.calculus import algebroid_calculus, d_E, evaluate, lie_E
from jacopy.central.algebroid.context import algebroid, locality_term
from jacopy.central.algebroid.operators import anchor_predator, derivator, jacobiator, section_map
from jacopy.central.objects import Bundle, forms, functions
from jacopy.central.objects.frame import Frame, FrameIndex, kronecker_delta
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.vector_field import vector_fields
from jacopy.central.tangent.anholonomy import AnholonomyCoefficient
from jacopy.central.tangent.exterior import d
from jacopy.core.expr import Integer, Neg, Product, Sum
from jacopy.core.indexed_sum import IndexedSum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.core.wedge import Wedge
from jacopy.oracle import check_equal
from jacopy.oracle.models.algebroid import ALGEBRAIC, FAMILIES, build_structure, family_rank

reg = PropertyRegistry()
f, g, h = functions("f g h", registry=reg)


def make(level, name="E"):
    E = algebroid(name, declare=(level,) if level else ())
    u, v, w = E.sections("u v w")
    al, = forms("alpha", degree=1, bundle=E.bundle)
    be, = forms("beta", degree=1, bundle=E.bundle)
    return E, u, v, w, al, be


def ok(lhs, rhs, E, **kw):
    kw.setdefault("registry", reg)
    return check_equal(lhs, rhs, owners=[E], **kw)


def palais(E, al, u, v):
    return Sum(Act(E.anchor(u), Pairing(al, v)), Neg(Act(E.anchor(v), Pairing(al, u))), Neg(Pairing(al, E.bracket(u, v))))


def cartan_rhs(E, u, al, v):
    return Sum(Pairing(Act(algebroid_calculus(E).d, Act(Interior(u), al)), v), Pairing(Act(Interior(u), d_E(E, al)), v))


# identities of EVERY anchored bundle with an ℝ-bilinear bracket
UNIVERSAL = {
    "⟨d_E f, u⟩ = ρ(u)f": lambda E, u, v, w, al, be: (Pairing(d_E(E, f), u), Act(E.anchor(u), f)),
    "⟨d_E f, u⟩ = ⟨Df, u⟩": lambda E, u, v, w, al, be: (Pairing(d_E(E, f), u), Pairing(E.D(f), u)),
    "ordered Palais d_E α(u,v)": lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, v), palais(E, al, u, v)),
    "Cartan magic on f": lambda E, u, v, w, al, be: (Act(lie_E(E, u), f), Sum(Act(algebroid_calculus(E).d, Act(Interior(u), f)), Act(Interior(u), d_E(E, f)))),
    "Cartan magic on α": lambda E, u, v, w, al, be: (Pairing(Act(lie_E(E, u), al), v), cartan_rhs(E, u, al, v)),
    "L_u v = [u,v]": lambda E, u, v, w, al, be: (Act(lie_E(E, u), v), E.bracket(u, v)),
    "L_u(f v) = [u, f v] (definition, no split)": lambda E, u, v, w, al, be: (Act(lie_E(E, u), Product(f, v)), E.bracket(u, Product(f, v))),
    "ρ C∞-linear": lambda E, u, v, w, al, be: (E.anchor(Product(f, u)), Product(f, E.anchor(u))),
    "Jacobiator definition": lambda E, u, v, w, al, be: (jacobiator(E, u, v, w), Sum(E.bracket(u, E.bracket(v, w)), Neg(E.bracket(E.bracket(u, v), w)), Neg(E.bracket(v, E.bracket(u, w))))),
    "anchor predator definition": lambda E, u, v, w, al, be: (anchor_predator(E, u, v), Sum(E.anchor(E.bracket(u, v)), Neg(LieBracketVF(E.anchor(u), E.anchor(v))))),
    "wedge determinant (α∧β)(u,v)": lambda E, u, v, w, al, be: (
        evaluate(Wedge(al, be), u, v), Sum(Product(Pairing(al, u), Pairing(be, v)), Neg(Product(Pairing(al, v), Pairing(be, u))))),
}

# Lie algebroid textbook identities
LIE = {
    "d_E² f = 0": lambda E, u, v, w, al, be: (evaluate(d_E(E, d_E(E, f)), u, v), Integer(0)),
    "d_E² α = 0": lambda E, u, v, w, al, be: (evaluate(d_E(E, d_E(E, al)), u, v, w), Integer(0)),
    "d_E∘d_E = 0 (operator, on α)": lambda E, u, v, w, al, be: (Act(Product(algebroid_calculus(E).d, algebroid_calculus(E).d), al), Integer(0)),
    "ρ homomorphism": lambda E, u, v, w, al, be: (E.anchor(E.bracket(u, v)), LieBracketVF(E.anchor(u), E.anchor(v))),
    "right Leibniz": lambda E, u, v, w, al, be: (E.bracket(u, Product(f, v)), Sum(Product(Act(E.anchor(u), f), v), Product(f, E.bracket(u, v)))),
    "left Leibniz (L = 0)": lambda E, u, v, w, al, be: (E.bracket(Product(f, u), v), Sum(Neg(Product(Act(E.anchor(v), f), u)), Product(f, E.bracket(u, v)))),
    "Jacobi J = 0": lambda E, u, v, w, al, be: (jacobiator(E, u, v, w), Integer(0)),
    "antisymmetry": lambda E, u, v, w, al, be: (E.bracket(u, v), Neg(E.bracket(v, u))),
    "d_E α alternating": lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, u), Integer(0)),
}

NEGATIVE = {
    # (level, builder)
    "P0-4 leibniz: d(α)(u,u) = 0": ("leibniz", lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, u), Integer(0))),
    "P0-4 courant: d(α)(u,u) = 0": ("courant", lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, u), Integer(0))),
    "P0-4 almost-courant: d(α)(u,u) = 0": ("almost-courant", lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, u), Integer(0))),
    "P0-5 undeclared: L_u(f u) = ρ(u)(f) u": ("", lambda E, u, v, w, al, be: (Act(lie_E(E, u), Product(f, u)), Product(Act(E.anchor(u), f), u))),
    "P0-5 undeclared: L_u(f v) product rule": ("", lambda E, u, v, w, al, be: (Act(lie_E(E, u), Product(f, v)), Sum(Product(Act(E.anchor(u), f), v), Product(f, Act(lie_E(E, u), v))))),
    "wrong right Leibniz (sign)": ("lie", lambda E, u, v, w, al, be: (E.bracket(u, Product(f, v)), Sum(Neg(Product(Act(E.anchor(u), f), v)), Product(f, E.bracket(u, v))))),
    "wrong right Leibniz (C∞-linear bracket)": ("lie", lambda E, u, v, w, al, be: (E.bracket(u, Product(f, v)), Product(f, E.bracket(u, v)))),
    "Cartan magic with minus": ("lie", lambda E, u, v, w, al, be: (Pairing(Act(lie_E(E, u), al), v), Sum(Pairing(Act(algebroid_calculus(E).d, Act(Interior(u), al)), v), Neg(Pairing(Act(Interior(u), d_E(E, al)), v))))),
    "Palais with swapped bracket": ("leibniz", lambda E, u, v, w, al, be: (evaluate(d_E(E, al), u, v), Sum(Act(E.anchor(u), Pairing(al, v)), Neg(Act(E.anchor(v), Pairing(al, u))), Neg(Pairing(al, E.bracket(v, u)))))),
    "d_E² f = 0 without anchor morphism": ("almost-leibniz", lambda E, u, v, w, al, be: (evaluate(d_E(E, d_E(E, f)), u, v), Integer(0))),
    "d_E² α = 0 at the leibniz level (needs antisymmetry)": ("leibniz", lambda E, u, v, w, al, be: (evaluate(d_E(E, d_E(E, al)), u, v, w), Integer(0))),
    "ρ homomorphism at almost-leibniz": ("almost-leibniz", lambda E, u, v, w, al, be: (E.anchor(E.bracket(u, v)), LieBracketVF(E.anchor(u), E.anchor(v)))),
    "Jacobi at pre-leibniz": ("pre-leibniz", lambda E, u, v, w, al, be: (jacobiator(E, u, v, w), Integer(0))),
    "L_{fu} = f L_u on α": ("lie", lambda E, u, v, w, al, be: (Pairing(Act(lie_E(E, Product(f, u)), al), v), Product(f, Pairing(Act(lie_E(E, u), al), v)))),
    "left Leibniz without L at leibniz": ("leibniz", lambda E, u, v, w, al, be: (E.bracket(Product(f, u), v), Sum(Neg(Product(Act(E.anchor(v), f), u)), Product(f, E.bracket(u, v))))),
}

LEVELS = ("", "almost-leibniz", "local", "pre-leibniz", "leibniz", "lie", "almost-courant", "courant")


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("name", sorted(UNIVERSAL))
def test_universal_identities_agree(level, name):
    E, u, v, w, al, be = make(level)
    rep = ok(*UNIVERSAL[name](E, u, v, w, al, be), E)
    assert rep.verdict == "AGREE", str(rep)


@pytest.mark.parametrize("name", sorted(LIE))
def test_lie_algebroid_textbook_identities_agree(name):
    E, u, v, w, al, be = make("lie")
    rep = ok(*LIE[name](E, u, v, w, al, be), E)
    assert rep.verdict == "AGREE", str(rep)
    assert all(w_.equal for w_ in rep.witnesses)


@pytest.mark.parametrize("name", sorted(NEGATIVE))
def test_negative_controls_disagree(name):
    level, build = NEGATIVE[name]
    E, u, v, w, al, be = make(level)
    rep = ok(*build(E, u, v, w, al, be), E)
    assert rep.verdict == "DISAGREE", str(rep)
    assert rep.reproduced is True


def test_leibniz_level_uses_a_non_skew_model():
    # a falsifier for the leibniz level must not only try skew (Lie) models
    E, u, v, w, al, be = make("leibniz")
    rep = ok(evaluate(d_E(E, al), u, v), palais(E, al, u, v), E)
    assert rep.verdict == "AGREE"
    # the cover needs a non-skew Courant model and a left-Leibniz breaker
    assert any("dorfman" in m for m in rep.models) and any("rho0" in m for m in rep.models), rep.models


def test_locality_operator_left_leibniz():
    # [fu, v] = −ρ(v)(f)u + f[u,v] + L(Df,u,v) under left Leibniz (Dorfman: L ≠ 0)
    E, u, v, w, al, be = make("courant")
    lhs = E.bracket(Product(f, u), v)
    rhs = Sum(Neg(Product(Act(E.anchor(v), f), u)), Product(f, E.bracket(u, v)), locality_term(E, f, u, v))
    assert ok(lhs, rhs, E).verdict == "AGREE"
    bad = Sum(Neg(Product(Act(E.anchor(v), f), u)), Product(f, E.bracket(u, v)), Neg(locality_term(E, f, u, v)))
    assert ok(lhs, bad, E).verdict == "DISAGREE"


def test_courant_metric_axioms():
    E, u, v, w, al, be = make("courant")
    sym = Sum(E.bracket(u, v), E.bracket(v, u))
    assert ok(sym, E.sharp(E.D(E.metric(u, v))), E).verdict == "AGREE"
    mi = (Act(E.anchor(u), E.metric(v, w)), Sum(E.metric(E.bracket(u, v), w), E.metric(v, E.bracket(u, w))))
    assert ok(*mi, E).verdict == "AGREE"
    assert ok(sym, Integer(0), E).verdict == "DISAGREE"


def test_derivator_definition():
    E, u, v, w, al, be = make("lie")
    Phi = section_map("Φ", E.bundle, E.bundle)
    lhs = derivator(E, Phi, u, v)
    rhs = Sum(Phi(E.bracket(u, v)), Neg(E.bracket(Phi(u), v)), Neg(E.bracket(u, Phi(v))))
    assert ok(lhs, rhs, E).verdict == "AGREE"
    assert ok(lhs, Integer(0), E).verdict == "DISAGREE"


# ---- ASSUMPTION_LEAK ------------------------------------------------- #


def _declared(E, *rules):
    return tuple(SimpleNamespace(kind="declared", owner=E, name=f"{r} ({E.name}): …") for r in rules)


def test_jacobi_leak_is_reported():
    E, u, v, w, al, be = make("lie")
    goal = (jacobiator(E, u, v, w), Integer(0))
    # the record shows right-Leibniz and antisymmetry, NOT Jacobi
    rep = ok(*goal, E, requires=_declared(E, "right-Leibniz", "antisymmetry"))
    assert rep.verdict == "ASSUMPTION_LEAK", str(rep)
    assert "jacobi" in rep.leak_structure
    # the record shows Jacobi → no leak
    rep = ok(*goal, E, requires=_declared(E, "right-Leibniz", "antisymmetry", "Leibniz-Jacobi"))
    assert rep.verdict == "AGREE" and not rep.leak_unchecked, str(rep)
    # d_E² α = 0 needs Jacobi (and antisymmetry): a record without it leaks
    rep = ok(evaluate(d_E(E, d_E(E, al)), u, v, w), Integer(0), E, requires=_declared(E, "anchor morphism", "antisymmetry"))
    assert rep.verdict == "ASSUMPTION_LEAK", str(rep)


def test_no_leak_for_definitional_identities():
    E, u, v, w, al, be = make("lie")
    rep = ok(Pairing(Act(lie_E(E, u), al), v), cartan_rhs(E, u, al, v), E, requires=())
    assert rep.verdict == "AGREE" and not rep.leak_unchecked, str(rep)
    # anchor morphism derived from right-Leibniz + Jacobi: not a leak
    rep = ok(E.anchor(E.bracket(u, v)), LieBracketVF(E.anchor(u), E.anchor(v)), E,
             requires=_declared(E, "right-Leibniz", "Leibniz-Jacobi"))
    assert rep.verdict == "AGREE", str(rep)
    # unknown record → AGREE with the leak check marked as not done
    rep = ok(jacobiator(E, u, v, w), Integer(0), E, requires=(SimpleNamespace(kind="legacy", owner=None),))
    assert rep.verdict == "AGREE" and rep.leak_unchecked, str(rep)


def test_unmodeled_declarations_are_unsupported():
    E = algebroid("E", declare=("courant", "exact"))
    u, v = E.sections("u v")
    rep = ok(E.bracket(u, v), Neg(Neg(E.bracket(u, v))), E)
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "algebroid-model[exact]", str(rep)
    # unused (known record) → modeled without it, noted as unchecked
    rep = ok(E.bracket(u, v), Neg(Neg(E.bracket(u, v))), E, requires=())
    assert rep.verdict == "AGREE" and "exact" in (rep.leak_unchecked or ""), str(rep)


def test_unknown_algebroid_owner_is_unsupported():
    E, u, v, w, al, be = make("lie")
    rep = check_equal(E.bracket(u, v), Neg(E.bracket(v, u)), registry=reg)
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "owners-unknown"
    rep = check_equal(E.bracket(u, v), Neg(E.bracket(v, u)), registry=reg, owners=[])
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "algebroid[unknown structure]"


# ---- frames and indexed sums (M7-1) ----------------------------------- #


def _m7_1():
    A = algebroid("Acheck", Bundle("Acheck"), declare=("local", "regular"))
    z, = A.sections("z")
    fr = Frame("b", bundle=A.bundle)
    beta = fr.dual().field("j")
    dh = Act(A.anchor(fr.field("j")), h)
    p = Pairing(beta, z)
    q = Act(A.anchor(z), h)
    sigma = lambda body: IndexedSum(FrameIndex("j"), fr, Product(dh, body))  # noqa: E731
    return A, sigma, p, q, z


def test_m7_1_linear_control_agrees():
    A, sigma, p, q, z = _m7_1()
    assert ok(sigma(p), q, A).verdict == "AGREE"


def test_m7_1_cubic_counterexample_disagrees():
    A, sigma, p, q, z = _m7_1()
    rep = ok(sigma(Product(p, p, p)), Product(q, q, q), A)
    assert rep.verdict == "DISAGREE" and rep.reproduced is True, str(rep)


def test_m7_1_derivative_counterexample_disagrees():
    A, sigma, p, q, z = _m7_1()
    rep = ok(sigma(Act(A.anchor(z), p)), Act(A.anchor(z), q), A)
    assert rep.verdict == "DISAGREE" and rep.reproduced is True, str(rep)


def test_frame_duality_and_anholonomy():
    fr = Frame("e")
    cf = fr.dual()
    X, = vector_fields("X")
    al, = forms("alpha", degree=1)
    # ⟨e^a, e_b⟩ = δ^a_b over every index assignment (a = b included)
    assert check_equal(fr.pairing("a", "b"), kronecker_delta("a", "b"), registry=reg, owners=[], requires=()).verdict == "AGREE"
    assert check_equal(fr.pairing("a", "b"), Integer(0), registry=reg, owners=[], requires=()).verdict == "DISAGREE"
    # frame decomposition Σ_s ⟨α, e_s⟩⟨e^s, X⟩ = ⟨α, X⟩
    s = FrameIndex("s")
    dec = IndexedSum(s, fr, Product(Pairing(al, fr.field("s")), Pairing(cf.field("s"), X)))
    assert check_equal(dec, Pairing(al, X), registry=reg, owners=[], requires=()).verdict == "AGREE"
    # de^c(e_a, e_b) = −γ^c_ab (Palais, γ^c_ab = ⟨e^c, [e_a, e_b]⟩)
    lhs = evaluate(d(cf.field("c")), fr.field("a"), fr.field("b"))
    gam = AnholonomyCoefficient("e", "c", "a", "b")
    assert check_equal(lhs, Neg(gam), registry=reg, owners=[], requires=()).verdict == "AGREE"
    assert check_equal(lhs, gam, registry=reg, owners=[], requires=()).verdict == "DISAGREE"


# ---- model self-check ------------------------------------------------ #


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_family_structures_self_check(family):
    """Every family satisfies exactly its claimed axioms on random
    sections and verifiably violates every other algebraic axiom (the
    check runs inside build_structure; here also for every pool seed)."""
    claims = FAMILIES[family][0]
    n = max(3, FAMILIES[family][1])
    r = family_rank(family, n, 3)
    for pool in range(3):
        st = build_structure(family, n, r, pool)
        assert st.satisfied == claims
        assert st.violated >= {a for a in ALGEBRAIC if a not in claims}


def test_tm_frame_with_unknown_record_is_unsupported():
    # the ownerless holonomic-frame rule may have been used: no verdict
    fr = Frame("e")
    rep = check_equal(fr.pairing("a", "b"), kronecker_delta("a", "b"), registry=reg, owners=[])
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "frame[proof record unknown]", str(rep)


# ---- false-AGREE probes (review): never a plain AGREE ----------------- #


def _never_agree(rep):
    assert rep.verdict in ("DISAGREE", "UNSUPPORTED"), str(rep)
    return rep


def test_metric_level_does_not_assume_anchor_morphism():
    E, u, v, w, al, be = make("metric")
    rep = _never_agree(ok(E.anchor(E.bracket(u, v)), LieBracketVF(E.anchor(u), E.anchor(v)), E))
    assert rep.verdict == "DISAGREE"


def test_almost_courant_does_not_assume_metric_invariance():
    E, u, v, w, al, be = make("almost-courant")
    mi = (Act(E.anchor(u), E.metric(v, w)), Sum(E.metric(E.bracket(u, v), w), E.metric(v, E.bracket(u, w))))
    assert _never_agree(ok(*mi, E)).verdict == "DISAGREE"


@pytest.mark.parametrize("level", ["pre-leibniz", "leibniz"])
def test_left_leibniz_consequence_is_not_assumed(level):
    # [fh·u, v] − f[hu, v] = h[fu, v] − hf[u, v] holds under left Leibniz only
    E, u, v, w, al, be = make(level)
    lhs = Sum(E.bracket(Product(f, h, u), v), Neg(Product(f, E.bracket(Product(h, u), v))))
    rhs = Sum(Product(h, E.bracket(Product(f, u), v)), Neg(Product(h, f, E.bracket(u, v))))
    assert _never_agree(ok(lhs, rhs, E)).verdict == "DISAGREE"
    # and it AGREEs where left Leibniz is declared
    E, u, v, w, al, be = make("local")
    lhs = Sum(E.bracket(Product(f, h, u), v), Neg(Product(f, E.bracket(Product(h, u), v))))
    rhs = Sum(Product(h, E.bracket(Product(f, u), v)), Neg(Product(h, f, E.bracket(u, v))))
    assert ok(lhs, rhs, E).verdict == "AGREE"


def test_free_indices_are_enumerated_exhaustively():
    from jacopy.core.expr import Integer as I

    fr = Frame("e")
    d1, d2, d3 = kronecker_delta("a", "b"), kronecker_delta("c", "d"), kronecker_delta("a", "c")
    lhs = Product(d1, d2, Sum(I(1), Neg(d3)), fr.pairing("a", "b"))
    rep = check_equal(lhs, I(0), registry=reg, owners=[], requires=(), seed=0)
    assert _never_agree(rep).verdict == "DISAGREE"
    # too many labels: UNSUPPORTED, never a sampled AGREE
    many = Product(*(kronecker_delta(x, y) for x, y in ("ab", "cd", "ef")))
    rep = check_equal(many, many if False else Product(kronecker_delta("b", "a"), kronecker_delta("c", "d"),
                                                       kronecker_delta("e", "f")), registry=reg, owners=[], requires=())
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "index-sampling", str(rep)


def test_metric_invariance_alone_derives_right_leibniz():
    E, u, v, w, al, be = make("metric")
    rl = (E.bracket(u, Product(f, v)), Sum(Product(Act(E.anchor(u), f), v), Product(f, E.bracket(u, v))))
    rep = ok(*rl, E, requires=_declared(E, "metric invariance"))
    assert rep.verdict == "AGREE", str(rep)


def test_lwx_courant_data():
    from jacopy.core.expr import Rational

    E = algebroid("C", declare=("anchor-morphism", "antisymmetric", "courant-invariance"))
    x, y, z = E.sections("x y z")
    half_D = lambda a, b: Product(Rational(1, 2), E.sharp(E.D(E.metric(a, b))))  # noqa: E731
    c5 = (Act(E.anchor(x), E.metric(y, z)),
          Sum(E.metric(Sum(E.bracket(x, y), half_D(x, y)), z), E.metric(y, Sum(E.bracket(x, z), half_D(x, z)))))
    rep = ok(*c5, E)
    assert rep.verdict == "AGREE" and any("lwx" in m for m in rep.models), str(rep)
    # metric invariance WITHOUT the D-terms is not an LWX axiom
    mi = (Act(E.anchor(x), E.metric(y, z)), Sum(E.metric(E.bracket(x, y), z), E.metric(y, E.bracket(x, z))))
    assert ok(*mi, E).verdict == "DISAGREE"
