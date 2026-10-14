"""
Non-metricity 1-forms ``Q_ab(∇, g)``
[ADM Eqs. (2.4), (2.5), (2.12), (2.13)].

Definition [ADM (2.12)]: on a frame ``(e_a)``,

    Q_ab(∇, g)(v) := Q(∇, g)(v, e_a, e_b),

i.e. the frame indices sit in the two METRIC slots and the 1-form
argument is the DIRECTION slot of ``Q(∇,g) = ∇g``
(``Q(X,Y,Z) = X(g(Y,Z)) − g(∇_X Y, Z) − g(Y, ∇_X Z)``). Hence the
components [ADM (2.13)] ``Q_ab(∇,g)_c = Q(∇,g)_cab`` and, with
[ADM (2.5)],

    Q_ab(e_c) = e_c(g_ab) − Σ_s Γ^s_ca g_sb − Σ_s Γ^s_cb g_as.

Mechanical theorems (all through the package engine, no hand step):

* :func:`prove_nonmetricity_form_symmetric` — ``Q_ab = Q_ba``
  evaluated on an ARBITRARY vector (metric symmetry; declaration-free);
* :func:`prove_nonmetricity_form_tensorial` — ``Q_ab(f·X) = f·Q_ab(X)``
  (declaration-free);
* :func:`prove_nonmetricity_form_components` — the frame component
  formula above (needs the frame-decomposition declaration
  ``∇_{e_c}e_a = Σ_s Γ^s_ca e_s``);
* :func:`prove_nonmetricity_form_cartan` — the form-language version
  ``Q_ab(e_c) = e_c(g_ab) − Σ_s ω^s_a(e_c) g_sb − Σ_s ω^s_b(e_c) g_as``
  (``Q_ab = dg_ab − ω_ba − ω_ab`` evaluated on the frame), connecting
  the non-metricity forms with the connection 1-forms ``ω^a_b``.

Scope: tangent bundle (``TM``) only; the algebroid analogue (an
E-non-metricity 1-form, ADM Def 3.14) is not built — the package's
E-non-metricity is an explicit expression
(:func:`~jacopy.packages.metric_affine.e_koszul.e_nonmetricity`),
not an atom.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from jacopy.algebra.derivation import Act
from jacopy.bibliography import cite
from jacopy.core.expr import Atom, Expr, Neg, Product, Sum
from jacopy.core.pairing import Pairing
from jacopy.core.registry import PropertyRegistry
from jacopy.core.symbolic_degree import Degree
from jacopy.proof.chain import ProofChain
from jacopy.proof.expansion import Definition
from jacopy.proof.strategies import ExpandAndSimplify
from jacopy.central.objects.connection import Connection
from jacopy.central.objects.frame import Frame, IndexLike, frame_index_str
from jacopy.packages.metric_affine.metric import (
    Metric,
    MetricValue,
    as_metric_context,
    nonmetricity,
)


class NonMetricityForm(Atom):
    """``Q_ab(∇, g)`` — the non-metricity 1-form on a frame (degree 1),
    defined by its evaluation ``Q_ab(v) := Q(∇,g)(v, e_a, e_b)``
    [ADM (2.12)]."""

    __slots__ = ("_connection_name", "_metric_name", "_frame_name", "_a", "_b")

    #: one slot — trivially alternating (``admits_alternation``)
    alternating_values = True

    def __init__(
        self,
        connection_name: str,
        metric_name: str,
        frame_name: str,
        a: str,
        b: str,
    ) -> None:
        self._connection_name = connection_name
        self._metric_name = metric_name
        self._frame_name = frame_name
        self._a = a
        self._b = b

    @property
    def connection_name(self) -> str:
        return self._connection_name

    @property
    def metric_name(self) -> str:
        return self._metric_name

    @property
    def frame_name(self) -> str:
        return self._frame_name

    @property
    def lower(self) -> Tuple[str, str]:
        return (self._a, self._b)

    @property
    def degree(self) -> Degree:
        return Degree.const(1)

    def _key(self) -> Any:
        return (
            self._connection_name,
            self._metric_name,
            self._frame_name,
            self._a,
            self._b,
        )

    def _repr_inner(self) -> str:
        return f"Q_{self._a}{self._b}"

    @property
    def index_names(self) -> Tuple[str, ...]:
        return (self._a, self._b)

    def substitute_atom(self, dummy: Expr, target: Expr) -> Expr:
        from jacopy.central.objects.frame import substituted_index_names

        if self == dummy:
            return target
        renamed = substituted_index_names(self.index_names, dummy, target)
        if renamed is None:
            return self
        return NonMetricityForm(
            self._connection_name,
            self._metric_name,
            self._frame_name,
            *renamed,
        )


def nonmetricity_form(
    conn: Connection, g: Metric, fr: Frame, a: IndexLike, b: IndexLike
) -> NonMetricityForm:
    """``Q_ab(∇, g)`` of the connection and metric on the frame."""
    if not isinstance(conn, Connection):
        raise TypeError("nonmetricity_form expects a Connection")
    if not isinstance(fr, Frame):
        raise TypeError("nonmetricity_form expects a Frame")
    g = as_metric_context(g)
    if not (conn.bundle.is_tangent and fr.bundle.is_tangent):
        raise ValueError(
            "nonmetricity_form is built on TM only (the E-non-metricity "
            "1-form is not an atom in this package)"
        )
    return NonMetricityForm(
        conn.name, g.name, fr.name, frame_index_str(a), frame_index_str(b)
    )


class NonMetricityFormEvaluationDefinition(Definition):
    """``⟨Q_ab, v⟩ → Q(∇,g)(v, e_a, e_b)`` — the defining evaluation
    of the non-metricity 1-form [ADM (2.12)] (per connection/metric/
    frame triple, so the rewrite can rebuild the frame legs)."""

    anchor = Pairing
    source = cite("DereliDogan2023", "Eq. (2.12)")

    def __init__(self, conn: Connection, g: Metric, fr: Frame) -> None:
        if not isinstance(conn, Connection):
            raise TypeError(
                "NonMetricityFormEvaluationDefinition expects a Connection"
            )
        if not isinstance(fr, Frame):
            raise TypeError(
                "NonMetricityFormEvaluationDefinition expects a Frame"
            )
        self._conn = conn
        self._g = as_metric_context(g)
        self._frame = fr
        self.name = (
            f"non-metricity form ({conn.name}, {self._g.name}, {fr.name}): "
            "⟨Q_ab, v⟩ = Q(v, e_a, e_b)"
        )

    def matches(self, expr: Expr) -> bool:
        return (
            isinstance(expr, Pairing)
            and isinstance(expr.alpha, NonMetricityForm)
            and expr.alpha.connection_name == self._conn.name
            and expr.alpha.metric_name == self._g.name
            and expr.alpha.frame_name == self._frame.name
        )

    def rewrite(self, expr: Expr) -> Expr:
        a, b = expr.alpha.lower
        return nonmetricity(
            self._conn,
            self._g,
            expr.X,
            self._frame.field(a),
            self._frame.field(b),
        )


def _engine(registry, conn, g, fr, *, decomposed: bool = False):
    from jacopy.packages.metric_affine.metric_affine_expansion import metric_affine_engine
    from jacopy.packages.metric_affine.frame_components import (
        ConnectionFormEvaluationDefinition,
    )

    engine = metric_affine_engine(
        registry=registry,
        decompositions=((conn, fr),) if decomposed else (),
    )
    engine.register(NonMetricityFormEvaluationDefinition(conn, g, fr))
    engine.register(ConnectionFormEvaluationDefinition(conn, fr))
    return engine


def prove_nonmetricity_form_symmetric(
    conn: Connection,
    g: Metric,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    X: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``Q_ab(X) = Q_ba(X)`` for an ARBITRARY vector ``X`` — the
    non-metricity forms are symmetric in the frame indices (``g`` is
    symmetric); declaration-free."""
    return ExpandAndSimplify().prove(
        Pairing(nonmetricity_form(conn, g, fr, a, b), X),
        Pairing(nonmetricity_form(conn, g, fr, b, a), X),
        registry=registry,
        engine=_engine(registry, conn, g, fr),
    )


def prove_nonmetricity_form_tensorial(
    conn: Connection,
    g: Metric,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    X: Expr,
    f: Expr,
    *,
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``Q_ab(f·X) = f·Q_ab(X)`` — ``Q_ab`` is a genuine 1-form
    (``C^∞(M)``-linear in its argument); declaration-free."""
    q = nonmetricity_form(conn, g, fr, a, b)
    return ExpandAndSimplify().prove(
        Pairing(q, Product(f, X)),
        Product(f, Pairing(q, X)),
        registry=registry,
        engine=_engine(registry, conn, g, fr),
    )


def nonmetricity_form_component_formula(
    conn: Connection,
    g: Metric,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    *,
    bound: str = "s",
) -> Expr:
    """``e_c(g_ab) − Σ_s Γ^s_ca g_sb − Σ_s Γ^s_cb g_as`` [ADM (2.5),
    (2.13)]."""
    from jacopy.core.indexed_sum import IndexedSum
    from jacopy.central.objects.frame import FrameIndex
    from jacopy.packages.metric_affine.frame_components import (
        check_bound_index,
        connection_coefficient,
    )

    check_bound_index(bound, a, b, c)
    g = as_metric_context(g)
    ea, eb, ec, es = (fr.field(i) for i in (a, b, c, bound))
    dummy = FrameIndex(bound)
    return Sum(
        Act(ec, MetricValue(g.name, ea, eb)),
        Neg(
            IndexedSum(
                dummy,
                fr,
                Product(
                    connection_coefficient(conn, fr, bound, c, a),
                    MetricValue(g.name, es, eb),
                ),
            )
        ),
        Neg(
            IndexedSum(
                dummy,
                fr,
                Product(
                    connection_coefficient(conn, fr, bound, c, b),
                    MetricValue(g.name, ea, es),
                ),
            )
        ),
    )


def prove_nonmetricity_form_components(
    conn: Connection,
    g: Metric,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    *,
    bound: str = "s",
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``Q_ab(e_c) = e_c(g_ab) − Σ_s Γ^s_ca g_sb − Σ_s Γ^s_cb g_as``
    [ADM (2.5), (2.13)] — needs the frame-decomposition declaration
    for ``(∇, frame)``."""
    return ExpandAndSimplify().prove(
        Pairing(nonmetricity_form(conn, g, fr, a, b), fr.field(c)),
        nonmetricity_form_component_formula(
            conn, g, fr, a, b, c, bound=bound
        ),
        registry=registry,
        engine=_engine(registry, conn, g, fr, decomposed=True),
    )


def prove_nonmetricity_form_cartan(
    conn: Connection,
    g: Metric,
    fr: Frame,
    a: IndexLike,
    b: IndexLike,
    c: IndexLike,
    *,
    bound: str = "s",
    registry: Optional[PropertyRegistry] = None,
) -> ProofChain:
    """``Q_ab(e_c) = e_c(g_ab) − Σ_s ω^s_a(e_c) g_sb − Σ_s ω^s_b(e_c) g_as``
    — the non-metricity forms in terms of the connection 1-forms
    (``Q_ab = dg_ab − ω_ba − ω_ab`` with ``ω_ab := g_as ω^s_b``,
    evaluated on the frame). Needs the frame-decomposition
    declaration."""
    from jacopy.core.indexed_sum import IndexedSum
    from jacopy.central.objects.frame import FrameIndex
    from jacopy.packages.metric_affine.frame_components import (
        check_bound_index,
        connection_form,
    )

    check_bound_index(bound, a, b, c)
    gname = as_metric_context(g).name
    ea, eb, ec, es = (fr.field(i) for i in (a, b, c, bound))
    dummy = FrameIndex(bound)
    rhs = Sum(
        Act(ec, MetricValue(gname, ea, eb)),
        Neg(
            IndexedSum(
                dummy,
                fr,
                Product(
                    Pairing(connection_form(conn, fr, bound, a), ec),
                    MetricValue(gname, es, eb),
                ),
            )
        ),
        Neg(
            IndexedSum(
                dummy,
                fr,
                Product(
                    Pairing(connection_form(conn, fr, bound, b), ec),
                    MetricValue(gname, ea, es),
                ),
            )
        ),
    )
    return ExpandAndSimplify().prove(
        Pairing(nonmetricity_form(conn, g, fr, a, b), ec),
        rhs,
        registry=registry,
        engine=_engine(registry, conn, g, fr, decomposed=True),
    )
