"""F2 realizers: algebroid nodes, the algebroid Cartan calculus, frames
and indexed sums. Registered into :mod:`jacopy.oracle.realize`'s table.

Conventions (each matched to the library, cited at the realizer):

* sections of ``E ≠ TM`` are :class:`~jacopy.oracle.values.SecV`
  (``r`` components in the model's constant frame of ``E``); E-forms
  are LAZY ordered multilinear maps :class:`~jacopy.oracle.values.EFormV`;
* ``d_E`` is the ORDERED Palais formula of ``bracket_calculus.py``
  (``dω(X_0…X_p) = Σ_i (−1)^i ρ(X_i)ω(…X̂_i…) + Σ_{i<j} (−1)^{i+j}
  ω([X_i,X_j], …X̂_i…X̂_j…)``) for every bracket, skew or not; it is
  alternating only when the model's bracket is verified skew;
* ``L^E_u`` is the definition ``L_u f = ρ(u)f``, ``L_u v = [u, v]_E``
  (on ``f·v`` too: the calculus' ``right_leibniz`` flag is False, so a
  product split is never assumed), ``(L_u ω)(Y…) = ρ(u)ω(Y…) −
  Σ_i ω(…[u,Y_i]…)``;
* ``ι_u`` inserts into the FIRST slot (``central/objects/interior.py``).
"""

from __future__ import annotations

from jacopy.central.algebroid.context import (
    AlgebroidBracket,
    AnchoredVF,
    CoboundaryForm,
    EMetric,
    LocalityOperator,
    MetricSharp,
)
from jacopy.central.algebroid.operators import Derivator, Jacobiator, MappedSection, Predator
from jacopy.central.objects.frame import CoframeField, FrameField, FrameIndex, KroneckerDelta
from jacopy.central.tangent.anholonomy import AnholonomyCoefficient
from jacopy.core.indexed_sum import IndexedSum

import time

from jacopy.oracle import values as V
from jacopy.oracle.realize import (
    DomainError,
    OpV,
    Unsupported,
    add,
    as_form,
    as_vec,
    is_scalar,
    is_zero,
    kind,
    norm,
    register,
)
from jacopy.oracle.values import EFormV, FormV, SecV, VecV

# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def as_sec(v, bundle, path=()):
    """The components of a section of ``bundle`` (0 → zero section)."""
    if isinstance(v, SecV):
        if v.b != bundle:
            raise Unsupported("section[bundle mismatch]", path, f"{v.b!r} ≠ {bundle!r}")
        return v.c
    if is_scalar(v) and v.is_zero:
        return None  # caller treats as the zero section
    raise Unsupported(f"expected-section:{kind(v)}", path)


def _sec(v, env, bundle, path):
    c = as_sec(v, bundle, path)
    if c is None:
        r = env.model.rank(bundle, path)
        return tuple(env.R.zero() for _ in range(r))
    return c


def _structure(env, name, path):
    st = env.model.structure(name, path)
    return st, env.model.bundle_of(name)


def _basis(R, r, a):
    return tuple(R.one() if i == a else R.zero() for i in range(r))


def _oneform_comps(om: EFormV, R, r):
    """Components ``ω(e_a)`` of an E-1-form on the constant frame (a
    C∞-linear slot, as for every E-1-form the engine pairs)."""
    return tuple(om([_basis(R, r, a)]) for a in range(r))


def _index(env, label, path):
    if label not in env.indices:
        raise Unsupported("FrameIndex[unassigned]", path, label)
    return env.indices[label]


# --------------------------------------------------------------------- #
# Atoms: sections and E-forms                                            #
# --------------------------------------------------------------------- #


def _section_atom(e, env, path):
    return env.model.section(e.bundle, ("VectorField", e.name))


def _eform_atom(e, env, p, path):
    if p == 0:
        return env.model.eform(e.bundle, ("Form", e.name), 0)
    if p > env.model.rank(e.bundle, path):
        return env.R.zero()
    return env.model.eform(e.bundle, ("Form", e.name), p)


# --------------------------------------------------------------------- #
# Anchor, bracket and the defect operators (context.py, operators.py)    #
# --------------------------------------------------------------------- #


@register(AnchoredVF)
def _anchored(e, env, path):
    """``ρ(u) = u^a ρ_a`` — a vector field on M."""
    st, b = _structure(env, e.algebroid_name, path)
    u = _sec(env.value(e.section, path + ("section",)), env, b, path)
    return VecV(st.anchor(u))


@register(AlgebroidBracket)
def _algebroid_bracket(e, env, path):
    """``[u, v]_E`` — the model's ℝ-bilinear bracket (a section)."""
    st, b = _structure(env, e.algebroid_name, path)
    u = _sec(env.value(e.u, path + ("u",)), env, b, path)
    v = _sec(env.value(e.v, path + ("v",)), env, b, path)
    return SecV(b, st.bracket(u, v))


@register(Jacobiator)
def _jacobiator(e, env, path):
    """``J(u,v,w) = [u,[v,w]] − [[u,v],w] − [v,[u,w]]`` (operators.py,
    Leibniz form); on the tangent algebroid with the Lie bracket."""
    R = env.R
    vals = [env.value(s, path + (i,)) for i, s in enumerate(e.sections)]
    if e.tangent:
        u, v, w = (as_vec(x, R, path) for x in vals)
        br = lambda a, b: V.vf_bracket(R, a, b)  # noqa: E731
        out = [x - y - z for x, y, z in zip(br(u, br(v, w)), br(br(u, v), w), br(v, br(u, w)))]
        return VecV(out)
    st, b = _structure(env, e.algebroid_name, path)
    u, v, w = (_sec(x, env, b, path) for x in vals)
    br = st.bracket
    out = [x - y - z for x, y, z in zip(br(u, br(v, w)), br(br(u, v), w), br(v, br(u, w)))]
    return SecV(b, out)


def _matvec(M, u, R):
    return tuple(sum((M[i][j] * u[j] for j in range(len(u))), R.zero()) for i in range(len(M)))


@register(MappedSection)
def _mapped_section(e, env, path):
    """``Φ(u)`` for a random C∞-linear ``Φ`` (a polynomial matrix):
    ``E → TM`` when ``tangent`` (a vector field), otherwise ``E → E`` —
    the node does not record a non-tangent target bundle, and the
    derivator (its only producer) needs ``Φ: E → E``."""
    R = env.R
    s = env.value(e.section, path + ("section",))
    if isinstance(s, VecV):
        b, u = None, s.c
    elif isinstance(s, SecV):
        b, u = s.b, s.c
    elif is_scalar(s) and s.is_zero:
        return R.zero()
    else:
        raise Unsupported(f"MappedSection[{kind(s)}]", path)
    M = env.model.section_map(e.map_name, b, e.tangent)
    out = _matvec(M, u, R)
    if e.tangent:
        return VecV(out)
    return VecV(out) if b is None else SecV(b, out)


def _phi(env, map_name, b, tangent, u):
    M = env.model.section_map(map_name, b, tangent)
    return _matvec(M, u, env.R)


@register(Derivator)
def _derivator(e, env, path):
    """``D_Φ(u,v) = Φ[u,v] − [Φu, v] − [u, Φv]`` for ``Φ: E → E``."""
    R = env.R
    vals = [env.value(s, path + (i,)) for i, s in enumerate(e.sections)]
    if e.tangent:
        u, v = (as_vec(x, R, path) for x in vals)
        br = lambda a, b: V.vf_bracket(R, a, b)  # noqa: E731
        ph = lambda a: _phi(env, e.map_name, None, True, a)  # noqa: E731
        out = [x - y - z for x, y, z in zip(ph(br(u, v)), br(ph(u), v), br(u, ph(v)))]
        return VecV(out)
    st, b = _structure(env, e.algebroid_name, path)
    u, v = (_sec(x, env, b, path) for x in vals)
    ph = lambda a: _phi(env, e.map_name, b, False, a)  # noqa: E731
    br = st.bracket
    out = [x - y - z for x, y, z in zip(ph(br(u, v)), br(ph(u), v), br(u, ph(v)))]
    return SecV(b, out)


@register(Predator)
def _predator(e, env, path):
    """``P_Φ(u,v) = Φ[u,v]_E − [Φu, Φv]_Lie`` for ``Φ: E → TM``; the
    anchor's own name means ``Φ = ρ`` (operators.py
    PredatorExpansionDefinition). An uncertified ``Φ`` (``tangent``
    False) has no vector-field images: UNSUPPORTED."""
    R = env.R
    if not e.tangent:
        raise Unsupported("Predator[uncertified target]", path)
    st, b = _structure(env, e.algebroid_name, path)
    u, v = (_sec(env.value(s, path + (i,)), env, b, path) for i, s in enumerate(e.sections))
    if e.map_name == env.model.anchors.get(e.algebroid_name):
        ph = st.anchor
    else:
        ph = lambda a: _phi(env, e.map_name, b, True, a)  # noqa: E731
    out = [x - y for x, y in zip(ph(st.bracket(u, v)), V.vf_bracket(R, ph(u), ph(v)))]
    return VecV(out)


@register(CoboundaryForm)
def _coboundary(e, env, path):
    """``Df`` with ``⟨Df, u⟩ = ρ(u)(f)`` [MC Def 3.5]."""
    st, b = _structure(env, e.algebroid_name, path)
    f = env.value(e.function, path + ("f",))
    if not is_scalar(f):
        raise Unsupported("CoboundaryForm[non-function]", path)
    if f.is_zero:
        return f
    return EFormV(b, 1, lambda args: st.act(args[0], f), alt=True, ctx=env.model, label="Df")


@register(LocalityOperator)
def _locality(e, env, path):
    """``L(ω, u, v)``: the model's C∞-trilinear locality tensor (present
    only in families where left Leibniz holds; its defining identity
    ``[fu,v] = −ρ(v)(f)u + f[u,v] + L(Df,u,v)`` is self-checked)."""
    st, b = _structure(env, e.algebroid_name, path)
    om = env.value(e.form, path + ("form",))
    u = _sec(env.value(e.rewritable_slots[1], path + ("u",)), env, b, path)
    v = _sec(env.value(e.rewritable_slots[2], path + ("v",)), env, b, path)
    if is_scalar(om) and om.is_zero:
        return env.R.zero()
    if not (isinstance(om, EFormV) and om.b == b and om.deg == 1):
        raise Unsupported(f"LocalityOperator[form slot {kind(om)}]", path)
    return SecV(b, st.locality(_oneform_comps(om, env.R, st.r), u, v))


@register(EMetric)
def _emetric(e, env, path):
    """``g(u, v)`` — the model's fibre metric (symmetric, non-degenerate)."""
    st, b = _structure(env, e.algebroid_name, path)
    u = _sec(env.value(e.u, path + ("u",)), env, b, path)
    v = _sec(env.value(e.v, path + ("v",)), env, b, path)
    return st.metric(u, v)


@register(MetricSharp)
def _metric_sharp(e, env, path):
    """``g⁻¹(ω)``: ``g(g⁻¹(ω), w) = ⟨ω, w⟩``."""
    st, b = _structure(env, e.algebroid_name, path)
    om = env.value(e.form, path + ("form",))
    if is_scalar(om) and om.is_zero:
        return env.R.zero()
    if not (isinstance(om, EFormV) and om.b == b and om.deg == 1):
        raise Unsupported(f"MetricSharp[{kind(om)}]", path)
    return SecV(b, st.sharp(_oneform_comps(om, env.R, st.r)))


# --------------------------------------------------------------------- #
# The algebroid Cartan calculus (bracket_calculus.py, Cartan-<E>)        #
# --------------------------------------------------------------------- #


def _tick(deadline):
    """Lazy E-form evaluation runs outside ``Env.value``: honour the
    check's time budget here too."""
    if deadline is not None and time.monotonic() > deadline:
        raise V.Budget("time budget exhausted (E-form evaluation)")


def e_d(st, b, val, ctx, path=(), deadline=None):
    """Ordered Palais ``d_E`` (see module docstring)."""
    R = st.R
    if is_scalar(val):
        f = val
        if f.is_zero:
            return f
        return EFormV(b, 1, lambda args: st.act(args[0], f), alt=True, ctx=ctx, label="d_E f")
    if not (isinstance(val, EFormV) and val.b == b):
        raise DomainError(f"d_E[on {kind(val)}]", path)
    p = val.deg
    om = val.fn

    def fn(args):
        _tick(deadline)
        total = R.zero()
        for i in range(p + 1):
            rest = args[:i] + args[i + 1:]
            term = st.act(args[i], om(rest))
            total = total + term if i % 2 == 0 else total - term
        for i in range(p + 1):
            for j in range(i + 1, p + 1):
                br = st.bracket(args[i], args[j])
                rest = [a for k, a in enumerate(args) if k not in (i, j)]
                term = om([br] + rest)
                total = total + term if (i + j) % 2 == 0 else total - term
        return total

    # alternating only for an alternating ω and a (verified) skew bracket
    return EFormV(b, p + 1, fn, alt=val.alt and "antisymmetric" in st.satisfied, ctx=ctx, label=f"d_E({val.label})")


def _e_exterior_derivative(alg, env, path):
    st, b = _structure(env, alg, path)
    model = env.model

    def d(a):
        if isinstance(a, (SecV, VecV, FormV, OpV)) or (isinstance(a, EFormV) and a.b != b) or not (
                is_scalar(a) or isinstance(a, EFormV)):
            raise DomainError(f"d_E[on {kind(a)}]", path)
        return e_d(st, b, a, model, path, env.deadline)

    return OpV(d, 1, f"d_{alg}")


def e_lie(st, b, X, val, ctx, path=(), deadline=None):
    R = st.R
    if is_scalar(val):
        return st.act(X, val)
    if isinstance(val, SecV) and val.b == b:
        return SecV(b, st.bracket(X, val.c))
    if isinstance(val, EFormV) and val.b == b:
        om, p = val.fn, val.deg

        def fn(args):
            _tick(deadline)
            total = st.act(X, om(args))
            for i in range(p):
                rep = list(args)
                rep[i] = st.bracket(X, args[i])
                total = total - om(rep)
            return total

        return EFormV(b, p, fn, alt=val.alt, ctx=ctx, label=f"L_E({val.label})")
    raise DomainError(f"L_E[on {kind(val)}]", path)


def _e_lie_derivative(alg, e, env, path):
    st, b = _structure(env, alg, path)
    X = _sec(env.value(e.vector, path + ("X",)), env, b, path)
    model = env.model
    return OpV(lambda a: norm(e_lie(st, b, X, a, model, path, env.deadline), env.R), 0, f"L^{alg}")


def _e_interior(Xv: SecV, env, path):
    """``ι_u`` on E-forms: first-slot insertion; ``ι_u f = 0``."""
    R = env.R
    u = Xv.c

    def i(a):
        if is_scalar(a):
            return R.zero()
        if isinstance(a, EFormV) and a.b == Xv.b:
            if a.deg == 1:
                return a([u])
            om = a.fn
            return EFormV(a.b, a.deg - 1, lambda args: om([u] + list(args)), alt=a.alt, ctx=a.ctx,
                          label=f"ι({a.label})")
        raise DomainError(f"ι_u[on {kind(a)}]", path)

    return OpV(i, -1, "ι_u")


def _e_wedge(vals, env, path):
    """Wedge of E-forms (and scalars), determinant convention; defined
    only for ALTERNATING factors (core/wedge.py)."""
    R = env.R
    c = R.one()
    forms = []
    for v in vals:
        if is_scalar(v):
            c = c * v
        elif isinstance(v, EFormV):
            if not v.alt:
                raise Unsupported("Wedge[non-alternating E-form]", path)
            forms.append(v)
        else:
            raise Unsupported(f"Wedge[E-form∧{kind(v)}]", path)
    if len({f.b for f in forms}) > 1:
        raise Unsupported("Wedge[E-forms of different bundles]", path)
    if c.is_zero:
        return R.zero()
    fn, p = forms[0].fn, forms[0].deg
    for f in forms[1:]:
        fn, p = V.e_wedge(fn, p, f.fn, f.deg), p + f.deg
    out = EFormV(forms[0].b, p, fn, alt=True, ctx=env.model, label="∧".join(f.label for f in forms))
    return out if c == R.one() else EFormV(out.b, p, lambda args: c * fn(args), alt=True, ctx=env.model, label=out.label)


# --------------------------------------------------------------------- #
# Frames, Kronecker delta, anholonomy, indexed sums (frame.py, F2)       #
# --------------------------------------------------------------------- #


def _frame_bundle(e):
    b = e.bundle
    return None if getattr(b, "is_tangent", False) and b.dim is None else b


@register(FrameField)
def _frame_field(e, env, path):
    """``e_a``: column ``a`` of a random unit upper-triangular frame of
    the bundle (det = 1); ``a`` is the run's value of the index label."""
    b = _frame_bundle(e)
    if b is not None and getattr(b, "is_tangent", False):
        raise Unsupported("FrameField[TM with fixed dim]", path)
    cols, _ = env.model.frame(e.base_name, b)
    k = _index(env, e.index, path)
    if k >= len(cols):
        raise Unsupported("FrameIndex[out of range]", path)
    return VecV(cols[k]) if b is None else SecV(b, cols[k])


@register(CoframeField)
def _coframe_field(e, env, path):
    """``e^a``: the dual coframe, ``⟨e^a, e_b⟩ = δ^a_b``."""
    b = _frame_bundle(e)
    if b is not None and getattr(b, "is_tangent", False):
        raise Unsupported("CoframeField[TM with fixed dim]", path)
    _, rows = env.model.frame(e.base_name, b)
    k = _index(env, e.index, path)
    if k >= len(rows):
        raise Unsupported("FrameIndex[out of range]", path)
    if b is None:
        return norm(FormV({(i,): c for i, c in enumerate(rows[k]) if not c.is_zero}), env.R)
    from jacopy.oracle.models.algebroid import alt_form

    return alt_form(env.model, b, {(i,): c for i, c in enumerate(rows[k]) if not c.is_zero}, 1, label=f"e^{e.index}")


@register(KroneckerDelta)
def _kronecker(e, env, path):
    """``δ^a_b`` (a constant): 1 when the two labels take the same value."""
    return env.R.one() if _index(env, e.upper, path) == _index(env, e.lower, path) else env.R.zero()


@register(AnholonomyCoefficient)
def _anholonomy(e, env, path):
    """``γ^c_ab := ⟨e^c, [e_a, e_b]⟩`` (anholonomy.py) for a TM frame."""
    R = env.R
    cols, rows = env.model.frame(e.frame_name, None)
    c = _index(env, e.upper, path)
    a, b = (_index(env, x, path) for x in e.lower)
    br = V.vf_bracket(R, cols[a], cols[b])
    return sum((rows[c][i] * br[i] for i in range(R.n)), R.zero())


@register(FrameIndex)
def _frame_index(e, env, path):
    raise Unsupported("FrameIndex[as a value]", path)


@register(IndexedSum)
def _indexed_sum(e, env, path):
    """``Σ_d body`` over the frame indices of the range's bundle: the
    concrete finite sum, with the dummy bound in the environment."""
    rng = e.range_
    bundle = getattr(rng, "bundle", None)
    if bundle is None:
        raise Unsupported("IndexedSum[range without bundle]", path)
    if getattr(bundle, "is_tangent", False):
        if bundle.dim is not None:
            raise Unsupported("IndexedSum[TM with fixed dim]", path)
        dim = env.R.n
    else:
        dim = env.model.rank(bundle, path)
    name = getattr(e.dummy, "name", None)
    if not isinstance(name, str):
        raise Unsupported("IndexedSum[dummy]", path)
    saved = env.indices.get(name)
    vals = []
    try:
        for k in range(dim):
            env.indices[name] = k
            vals.append(env.value(e.body, path + ("Σ", k)))
    finally:
        if saved is None:
            env.indices.pop(name, None)
        else:
            env.indices[name] = saved
    return add(vals, env.R, path)


# silence unused-import linters: kept for symmetry with realize.py helpers
_ = (as_form, is_zero)
