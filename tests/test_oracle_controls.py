"""Model-oracle control suite (SPEC §7: the oracle must not have its own
bugs). POSITIVE controls are textbook identities that must be AGREE —
a failure here means a realizer's convention does not match the
library's; NEGATIVE controls are known-false equations (including the
audit's P0-1 / P0-2 shapes) that must be DISAGREE."""

from types import SimpleNamespace

import pytest

pytest.importorskip("sympy")

from jacopy.algebra.commutator import Commutator
from jacopy.algebra.derivation import Act
from jacopy.algebra.lie_bracket_vf import LieBracketVF
from jacopy.brackets.base import BracketApply
from jacopy.central.objects import forms, functions, vector_fields
from jacopy.central.objects.interior import Interior
from jacopy.central.objects.multivector import PVector
from jacopy.central.objects.multivector_interior import MultivectorInterior
from jacopy.central.objects.tilde_interior import TildeInterior
from jacopy.central.tangent.exterior import CARTAN_TM, d
from jacopy.central.tangent.schouten import SN
from jacopy.core.expr import Integer, Neg, Product, Sum, Symbol
from jacopy.core.multi_eval import MultiEval
from jacopy.core.pairing import Pairing
from jacopy.core.properties import Scalar
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.core.wedge import Wedge
from jacopy.oracle import check_equal
from jacopy.packages.poisson.core import HamiltonianVF, PoissonBracketValue, poisson_structure
from jacopy.packages.poisson.nambu import NambuSharpVF
from jacopy.packages.poisson.tilde import d_tilde, lie_tilde

reg = PropertyRegistry()
X, Y, Z = vector_fields("X Y Z")
f, g, h, a, b = functions("f g h a b", registry=reg)
al, be = forms("alpha beta", degree=1)
om, = forms("omega", degree=2)
th, = forms("theta", degree=3)
c = Symbol("c")
reg.declare(c, Scalar())

P = poisson_structure("π", declare=("poisson",))
P0 = poisson_structure("π")  # same bivector, NOT declared Poisson
PI = P.pi


def L(V, x):
    return Act(CARTAN_TM.lie(V), x)


def i(V, x):
    return Act(Interior(V), x)


def ok(lhs, rhs, **kw):
    kw.setdefault("registry", reg)
    return check_equal(lhs, rhs, **kw)


POSITIVE = {
    "d² f = 0": (d(d(f)), Integer(0)),
    "d² α = 0": (d(d(al)), Integer(0)),
    "d² ω = 0": (d(d(om)), Integer(0)),
    "d² on a symbolic-degree form": (d(d(forms("sigma", degree=Degree.var("p"))[0])), Integer(0)),
    "Cartan magic on f": (L(X, f), i(X, d(f))),
    "Cartan magic on α": (L(X, al), Sum(d(i(X, al)), i(X, d(al)))),
    "Cartan magic on ω": (L(X, om), Sum(d(i(X, om)), i(X, d(om)))),
    "Cartan magic on θ": (L(X, th), Sum(d(i(X, th)), i(X, d(th)))),
    "Cartan magic as graded commutator [d, ι_X] = L_X": (Act(Commutator(CARTAN_TM.d, Interior(X)), om), L(X, om)),
    "[L_X, ι_Y] = ι_[X,Y] on ω": (Act(Commutator(CARTAN_TM.lie(X), Interior(Y)), om), i(LieBracketVF(X, Y), om)),
    "[L_X, L_Y] = L_[X,Y] on α": (Act(Commutator(CARTAN_TM.lie(X), CARTAN_TM.lie(Y)), al), L(LieBracketVF(X, Y), al)),
    "[L_X, d] = 0": (Act(Commutator(CARTAN_TM.lie(X), CARTAN_TM.d), al), Integer(0)),
    "ι_X ι_Y = −ι_Y ι_X": (i(X, i(Y, th)), Neg(i(Y, i(X, th)))),
    "Leibniz X(fg)": (Act(X, Product(f, g)), Sum(Product(Act(X, f), g), Product(f, Act(X, g)))),
    "Leibniz d(fα)": (d(Product(f, al)), Sum(Wedge(d(f), al), Product(f, d(al)))),
    "graded Leibniz d(α∧β)": (d(Wedge(al, be)), Sum(Wedge(d(al), be), Neg(Wedge(al, d(be))))),
    "graded Leibniz ι_X(α∧β)": (i(X, Wedge(al, be)), Sum(Product(Pairing(al, X), be), Neg(Product(Pairing(be, X), al)))),
    "wedge determinant (α∧β)(X,Y)": (MultiEval(Wedge(al, be), X, Y),
                                     Sum(Product(Pairing(al, X), Pairing(be, Y)), Neg(Product(Pairing(al, Y), Pairing(be, X))))),
    "Palais dα(X,Y)": (MultiEval(d(al), X, Y),
                       Sum(Act(X, Pairing(al, Y)), Neg(Act(Y, Pairing(al, X))), Neg(Pairing(al, LieBracketVF(X, Y))))),
    "ι_X ω = ω(X, ·)": (Pairing(i(X, om), Y), MultiEval(om, X, Y)),
    "vector-field bracket as commutator": (Commutator(X, Y), LieBracketVF(X, Y)),
    "Jacobi of vector fields": (Sum(LieBracketVF(X, LieBracketVF(Y, Z)), LieBracketVF(Y, LieBracketVF(Z, X)),
                                    LieBracketVF(Z, LieBracketVF(X, Y))), Integer(0)),
    "constant scalar commutes": (Act(X, Product(c, f)), Product(c, Act(X, f))),
    "ι_{X∧Y} = ι_Y ∘ ι_X": (Act(MultivectorInterior(Wedge(X, Y)), th), i(Y, i(X, th))),
    "Nambu sharp p=1: (π df)(g) = π(df, dg)": (Act(NambuSharpVF(PI, d(f)), g), MultiEval(PI, d(f), d(g), slot_kind="covector")),
    "Hamiltonian Leibniz X_h(ab)": (Act(HamiltonianVF(PI, h), Product(a, b)),
                                    Sum(Product(Act(HamiltonianVF(PI, h), a), b), Product(a, Act(HamiltonianVF(PI, h), b)))),
    "{f,g} = X_f(g)": (PoissonBracketValue(PI, f, g), Act(HamiltonianVF(PI, f), g)),
}

POISSON_POSITIVE = {
    "Schouten [π,π] = 0 (Poisson model)": (BracketApply(SN, PI, PI), Integer(0)),
    "Jacobi of the Poisson bracket": (Sum(PoissonBracketValue(PI, f, PoissonBracketValue(PI, g, h)),
                                          PoissonBracketValue(PI, g, PoissonBracketValue(PI, h, f)),
                                          PoissonBracketValue(PI, h, PoissonBracketValue(PI, f, g))), Integer(0)),
    "d̃² f = 0 (Poisson model)": (d_tilde(P, d_tilde(P, f)), Integer(0)),
    "d̃² X = 0 (Poisson model)": (d_tilde(P, d_tilde(P, X)), Integer(0)),
    "d̃(X∧Y) = d̃X∧Y − X∧d̃Y": (d_tilde(P, Wedge(X, Y)), Sum(Wedge(d_tilde(P, X), Y), Neg(Wedge(X, d_tilde(P, Y))))),
    "⟨d̃f, α⟩ = π(α, df)": (Pairing(al, d_tilde(P, f)), MultiEval(PI, al, d(f), slot_kind="covector")),
    "tilde Cartan on f": (Act(lie_tilde(P, al), f), Act(TildeInterior(al), d_tilde(P, f))),
    "tilde Cartan on X": (Act(lie_tilde(P, al), X), Sum(d_tilde(P, Act(TildeInterior(al), X)), Act(TildeInterior(al), d_tilde(P, X)))),
    "tilde Cartan on π-type bivector": (Act(lie_tilde(P, al), Wedge(X, Y)),
                                        Sum(d_tilde(P, Act(TildeInterior(al), Wedge(X, Y))), Act(TildeInterior(al), d_tilde(P, Wedge(X, Y))))),
}

NEGATIVE = {
    "P0-1: d̃(X∧Y) = d̃X∧Y + X∧d̃Y": (d_tilde(P, Wedge(X, Y)), Sum(Wedge(d_tilde(P, X), Y), Wedge(X, d_tilde(P, Y)))),
    "P0-2: X_h(ab) = a·X_h(b)": (Act(HamiltonianVF(PI, h), Product(a, b)), Product(a, Act(HamiltonianVF(PI, h), b))),
    "Cartan with minus": (L(X, al), Sum(d(i(X, al)), Neg(i(X, d(al))))),
    "Cartan with factor two": (L(X, al), Sum(Product(Integer(2), d(i(X, al))), i(X, d(al)))),
    "[d, ι_X] read as ungraded AB − BA": (Act(Sum(Product(CARTAN_TM.d, Interior(X)), Neg(Product(Interior(X), CARTAN_TM.d))), om), L(X, om)),
    "[L_X, ι_Y] = −ι_[X,Y]": (Act(Commutator(CARTAN_TM.lie(X), Interior(Y)), om), Neg(i(LieBracketVF(X, Y), om))),
    "d(α∧β) with +": (d(Wedge(al, be)), Sum(Wedge(d(al), be), Wedge(al, d(be)))),
    "ι_X(α∧β) with +": (i(X, Wedge(al, be)), Sum(Product(Pairing(al, X), be), Product(Pairing(be, X), al))),
    "wedge determinant with swapped sign": (MultiEval(Wedge(al, be), X, Y),
                                            Sum(Product(Pairing(al, Y), Pairing(be, X)), Neg(Product(Pairing(al, X), Pairing(be, Y))))),
    "X(Yf) = Y(Xf)": (Act(X, Act(Y, f)), Act(Y, Act(X, f))),
    "Leibniz missing a term": (Act(X, Product(f, g)), Product(Act(X, f), g)),
    "ι_{X∧Y} = ι_X ∘ ι_Y (wrong order)": (Act(MultivectorInterior(Wedge(X, Y)), th), i(X, i(Y, th))),
    "L_{fX} = f L_X": (L(Product(f, X), al), Product(f, L(X, al))),
}


@pytest.mark.parametrize("name", sorted(POSITIVE))
def test_positive_controls_agree(name):
    lhs, rhs = POSITIVE[name]
    rep = ok(lhs, rhs)
    assert rep.verdict == "AGREE", str(rep)


@pytest.mark.parametrize("name", sorted(POISSON_POSITIVE))
def test_poisson_positive_controls_agree(name):
    lhs, rhs = POISSON_POSITIVE[name]
    rep = ok(lhs, rhs, owners=[P])
    assert rep.verdict == "AGREE", str(rep)
    assert all(w.equal for w in rep.witnesses)


@pytest.mark.parametrize("name", sorted(NEGATIVE))
def test_negative_controls_disagree(name):
    lhs, rhs = NEGATIVE[name]
    rep = ok(lhs, rhs, owners=[P])
    assert rep.verdict == "DISAGREE", str(rep)
    assert rep.reproduced is True


def test_non_poisson_bivector_breaks_d_tilde_squared():
    # owners known, π NOT declared Poisson → generic bivector → d̃² ≠ 0
    rep = ok(d_tilde(P0, d_tilde(P0, f)), Integer(0), owners=[P0])
    assert rep.verdict == "DISAGREE", str(rep)
    rep = ok(BracketApply(SN, PI, PI), Integer(0), owners=[P0])
    assert rep.verdict == "DISAGREE", str(rep)


def test_assumption_leak_on_unused_poisson_declaration():
    goal = (d_tilde(P, d_tilde(P, f)), Integer(0))
    # the proof record claims no assumption → must hold without Poisson
    rep = ok(*goal, owners=[P], requires=())
    assert rep.verdict == "ASSUMPTION_LEAK" and rep.leak_structure == "π", str(rep)
    # the record uses the declaration → fine
    used = (SimpleNamespace(kind="declared", owner=P),)
    assert ok(*goal, owners=[P], requires=used).verdict == "AGREE"
    # an assumption-free identity stays AGREE in the counter-model too
    rep = ok(d_tilde(P, Wedge(X, Y)), Sum(Wedge(d_tilde(P, X), Y), Neg(Wedge(X, d_tilde(P, Y)))), owners=[P], requires=())
    assert rep.verdict == "AGREE", str(rep)
    # unknown record (legacy) → no leak judgement
    legacy = (SimpleNamespace(kind="legacy", owner=None),)
    assert ok(*goal, owners=[P], requires=legacy).verdict == "AGREE"


def test_product_readings_are_reported_ambiguous():
    # value reading: f·X both sides; operator reading: X∘f ≠ f∘X
    rep = ok(Product(X, f), Product(f, X))
    assert rep.verdict == "AMBIGUOUS", str(rep)
    # constants commute: no ambiguity
    assert ok(Product(X, c), Product(c, X)).verdict == "AGREE"


def test_unsupported_is_never_silent():
    from jacopy.central.objects.bundle import Bundle
    from jacopy.central.objects.vector_field import VectorField

    u = VectorField("u", bundle=Bundle("E"))
    rep = ok(Act(u, f), Integer(0))
    assert rep.verdict == "UNSUPPORTED"
    assert rep.unsupported_type == "VectorField[bundle≠TM]" and rep.unsupported_path == ("lhs", 0)
    q = Symbol("q")  # undeclared symbol: no model semantics
    rep = ok(Act(X, q), Integer(0))
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "Symbol[undeclared]"


def test_reports_are_deterministic():
    l, r = NEGATIVE["Cartan with minus"]
    a1, a2 = ok(l, r, seed=5), ok(l, r, seed=5)
    assert a1.models == a2.models and [w.lhs_value for w in a1.witnesses] == [w.lhs_value for w in a2.witnesses]
    assert ok(l, r, seed=6).models != a1.models


def test_poisson_models_self_check():
    from jacopy.oracle.models.tangent import TangentModel
    from jacopy.oracle.values import schouten

    for n in (2, 3, 4):
        for s in range(6):
            m = TangentModel(n, s, bivectors={"π": "poisson"})
            pi = m.structure_bivector("π")
            assert not schouten(m.R, pi.d, pi.d)
    for s in range(6):
        m = TangentModel(3, s, bivectors={"π": "counter"})
        pi = m.structure_bivector("π")
        assert schouten(m.R, pi.d, pi.d)


def test_chain_check_names_first_bad_rule():
    from jacopy.oracle import check_chain

    steps = [
        SimpleNamespace(before=L(X, al), after=Sum(d(i(X, al)), i(X, d(al))), rule="cartan"),
        SimpleNamespace(before=Sum(d(i(X, al)), i(X, d(al))), after=Sum(d(i(X, al)), Neg(i(X, d(al)))), rule="bad-sign"),
    ]
    rep = check_chain(SimpleNamespace(steps=steps), registry=reg)
    assert rep.first_bad_index == 1 and rep.first_bad_rule == "bad-sign"


def test_unmodeled_owner_axioms_are_unsupported_not_disagree():
    from jacopy.packages.poisson.nambu import nambu_structure
    from jacopy.packages.poisson.symplectic import symplectic_structure

    # ω symplectic with π = ω⁻¹ is a relation the random model lacks
    S = symplectic_structure("ϖ")
    rep = ok(Pairing(S.omega if hasattr(S, "omega") else om, X), Integer(0), owners=[S])
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "owner[SymplecticStructure]", str(rep)
    # a Nambu 3-vector with the fundamental identity declared has no F1 model
    N = nambu_structure("Λ", p=2, declare=("fundamental-identity",))
    w2 = Wedge(d(f), d(g))
    rep = ok(Act(NambuSharpVF(N.pi, w2), h), Integer(0), owners=[N])
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "NambuPoisson[fundamental-identity]"
    rep = ok(Act(NambuSharpVF(N.pi, w2), h), Integer(0))
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "NambuPoisson[owners unknown]"
    # without the declaration the generic model is the right one
    N0 = nambu_structure("Λ", p=2)
    assert ok(Act(NambuSharpVF(N0.pi, w2), h), Integer(0), owners=[N0]).verdict == "DISAGREE"


def test_used_unmodeled_assumption_is_unsupported():
    # a proof record that used an axiom the models do not satisfy
    other = SimpleNamespace(kind="declared", owner=SimpleNamespace(name="E"), name="E: Jacobi")
    l, r = NEGATIVE["Cartan with minus"]
    rep = ok(l, r, requires=(other,))
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type == "assumption[SimpleNamespace]"
    used = (SimpleNamespace(kind="declared", owner=P, name="Poisson"),)
    assert ok(l, r, owners=[P], requires=used).verdict == "DISAGREE"


# --------------------------------------------------------------------- #
# Review probes: equations the first version wrongly AGREEd on          #
# --------------------------------------------------------------------- #

sig, = forms("sigma_p", degree=Degree.var("p"))
tau, = forms("tau_q", degree=Degree.var("q"))
rho, = forms("rho_r", degree=Degree.var("r"))
a1, a2, a3, a4 = forms("a1 a2 a3 a4", degree=1)

FALSE_AGREE_PROBES = {
    # 1) every degree variable must take every value (σ_p∧τ_q∧ρ_r swap)
    "σ_p∧τ_q∧ρ_r = σ_p∧ρ_r∧τ_q": (Wedge(sig, tau, rho), Wedge(sig, rho, tau)),
    # 2) the dimension must exceed every subnode's degree
    "four 1-forms wedge to 0": (Wedge(a1, a2, a3, a4), Integer(0)),
    "ω∧ω = 0": (Wedge(om, om), Integer(0)),
    "ω∧α∧β = −α∧ω∧β": (Wedge(om, al, be), Neg(Wedge(al, om, be))),
    "d(ω∧α∧β) = 0": (d(Wedge(om, al, be)), Integer(0)),
    # 3) operator domains: equal operators agree on the whole test basis
    "ι_X = ι̃_α": (Interior(X), TildeInterior(al)),
    "L_X = X": (CARTAN_TM.lie(X), X),
    # 6) both Product readings refuted → DISAGREE, not AMBIGUOUS
    "X·f = g·X": (Product(X, f), Product(g, X)),
}


@pytest.mark.parametrize("name", sorted(FALSE_AGREE_PROBES))
def test_review_false_agree_probes_disagree(name):
    lhs, rhs = FALSE_AGREE_PROBES[name]
    rep = ok(lhs, rhs)
    assert rep.verdict == "DISAGREE", str(rep)


def test_degree_assignments_cover_every_value_jointly():
    rep = ok(Wedge(sig, tau), Wedge(tau, sig))  # true only when p·q even
    assert rep.verdict == "DISAGREE"
    rep = ok(Wedge(sig, tau, rho), Wedge(sig, tau, rho))
    assert rep.verdict == "AGREE"
    rep = ok(d(Wedge(sig, tau)), Sum(Wedge(d(sig), tau), Wedge(sig, d(tau))))  # sign (−1)^p missing
    assert rep.verdict == "DISAGREE"
    assert "full product, 9 assignment(s)" in rep.degree_assignments


def test_too_many_degree_variables_is_budget_unsupported():
    vs = forms("v1 v2 v3 v4", degree=Degree.var("k"))  # one variable: fine
    assert ok(Wedge(*vs[:2]), Wedge(*vs[:2])).verdict == "AGREE"
    many = [forms(f"w{i}", degree=Degree.var(f"k{i}"))[0] for i in range(4)]
    rep = ok(d(d(Wedge(*many))), Integer(0))
    assert rep.verdict == "UNSUPPORTED" and rep.unsupported_type in ("budget[degree-assignments]", "dimension")


def test_model_dimension_follows_subnode_degrees():
    rep = ok(Wedge(om, om), Wedge(om, om))
    assert rep.verdict == "AGREE" and all(m.startswith("R^5") for m in rep.models)
    rep = ok(d(Wedge(om, al, be)), d(Wedge(om, al, be)) + Integer(0))
    assert all(m.startswith("R^6") for m in rep.models)


def test_samples_must_be_positive():
    l, r = NEGATIVE["Cartan with minus"]
    for bad in (0, -1):
        with pytest.raises(ValueError):
            check_equal(l, r, registry=reg, samples=bad)


def test_poisson_sample_zero_is_never_degenerate():
    from jacopy.oracle.models.tangent import TangentModel

    degenerate = 0
    for target in range(300):
        n = (2, 3, 4)[target % 3]
        m = TangentModel(n, 10_000 + target, bivectors={"π": "poisson"}, sample=0)
        pi = m.structure_bivector("π")
        if max(c.total_degree() for c in pi.d.values()) < 2:  # ∂π or ∂²π vanishes
            degenerate += 1
    assert degenerate == 0


def test_leak_check_failure_is_flagged_not_plain_agree(monkeypatch):
    from jacopy.oracle.models.tangent import TangentModel
    from jacopy.oracle.values import Unsupported

    def refuse(self, rng):
        raise Unsupported("counter-model-test")

    monkeypatch.setattr(TangentModel, "_counter", refuse)
    rep = ok(d_tilde(P, d_tilde(P, f)), Integer(0), owners=[P], requires=())
    assert rep.verdict == "AGREE" and rep.leak_unchecked and "NOT done" in rep.summary()
