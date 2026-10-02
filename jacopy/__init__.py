"""jacopy — graded algebra & bracket calculus with step-by-step proofs.

Layers (each builds on the ones above it; the remaining upward edges
are deferred imports):

* **Foundation** — ``core`` (expression tree, properties, matching),
  ``algebra`` (``Act``, ``Derivation``, grading), ``algorithms``
  (simplify / product rule / normal forms), ``brackets`` (the
  ``GradedBracket`` base), ``proof`` (proof chains, strategies,
  ``ProofResult``, theorems), ``display`` (text / LaTeX / HTML).
* **central** — objects and calculus valid on ``TM`` and on any
  algebroid ``E``: functions, vector fields, forms, tensors, metric,
  connection, frames; Lie/Schouten brackets, ``d``, ``ι``, ``ℒ``.
* **packages** — geometry built on the central code:
  ``metric_affine``, ``poisson``, ``drinfeld`` (algebroid calculus,
  Drinfel'd doubles, twists), ``generalized`` (Courant algebroids).
* **research** — :mod:`jacopy.research`: pick a bracket and objects,
  assemble an engine, check the bracket axioms.

Support levels
--------------
1. **Stable — this module.** The names in ``jacopy.__all__``: the core
   expression classes, the object factories, the tangent-bundle
   operators, the proof entry points (``show_equal``, ``prove``,
   ``ProofChain``, ``ProofResult``, ``Theorem`` …) and the display
   helpers. Each is the very object its subpackage exports, re-exported
   unchanged.
2. **Stable extension protocols.** Subclass :class:`Expr` / :class:`Atom`
   for a new expression node and :class:`Definition` for a new rewrite
   rule; register its rendering with :func:`jacopy.display.register`.
3. **Public, still evolving.** The subpackage facades —
   :mod:`jacopy.research` (the research front door),
   ``from jacopy.packages.<name> import …``, :mod:`jacopy.central.objects`,
   :mod:`jacopy.central.tangent`, :mod:`jacopy.proof`,
   :mod:`jacopy.display` — i.e. each package's ``__all__``. Names may
   still move between layers; the facade keeps importing them.
4. **Internal.** Any other module path and every ``_``-prefixed name;
   these may change without notice.

Same name, different object: here ``Zero`` is the expression
:data:`~jacopy.core.expr.Zero` (the block-matrix zero operator is
``jacopy.research.ZeroOperator``), ``metric``/``Metric`` the central
metric atom (not the :mod:`jacopy.packages.metric_affine` metric
context), ``normalize`` :func:`jacopy.proof.normalize` (the
rule-list fixed point is ``jacopy.algorithms.rewrite_to_fixpoint``),
``cite`` :func:`jacopy.proof.theorems.cite`, which cites proven
theorems into an engine (the literature-reference builder is the
different :func:`jacopy.bibliography.cite`), and ``prove``
:func:`jacopy.proof.search.prove`, which returns a :class:`ProofChain`
or raises :class:`ProofFailure` (the driver that returns a
:class:`ProofResult` with its requirements is the different
:func:`jacopy.proof.result.prove`, called as ``prove(engine, lhs, rhs)``).
``Provenance``, ``antisymmetrize`` and ``prove_jacobi`` are deliberately
not exported here; each subpackage ``__all__`` now carries an
unambiguous name for the second object (``PropertyProvenance``,
``antisymmetrize_indices``, ``prove_lie_jacobi``) while the old names
stay importable from their old paths.

The core expression classes load eagerly; every other name loads on
first access, so ``import jacopy.core`` (or ``jacopy.oracle``) stays as
light as before.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from jacopy.core.expr import (
    Atom,
    Expr,
    Integer,
    Neg,
    NegOne,
    One,
    Power,
    Product,
    Rational,
    Sum,
    Symbol,
    Zero,
)

# The single version source: pyproject.toml reads this literal
# ([tool.setuptools.dynamic] version = {attr = "jacopy.__version__"}).
__version__ = "0.0.1"

_CORE = "jacopy.core"
_ALGEBRA = "jacopy.algebra"
_OBJECTS = "jacopy.central.objects"
_TANGENT = "jacopy.central.tangent"
_PROOF = "jacopy.proof"
_DISPLAY = "jacopy.display"

# name -> the subpackage facade it is re-exported from (lazily).
_LAZY: dict[str, str] = {
    # core: registry and the n-ary expression nodes
    "PropertyRegistry": _CORE,
    "default_registry": _CORE,
    "Wedge": _CORE,
    "MultiEval": _CORE,
    # algebra: operator application
    "Act": _ALGEBRA,
    "Derivation": _ALGEBRA,
    # central object factories
    "Bundle": _OBJECTS,
    "TM": _OBJECTS,
    "tangent_bundle": _OBJECTS,
    "functions": _OBJECTS,
    "vector_fields": _OBJECTS,
    "forms": _OBJECTS,
    "p_vectors": _OBJECTS,
    "bivector": _OBJECTS,
    "tensors": _OBJECTS,
    "metric": _OBJECTS,
    "Metric": _OBJECTS,
    "hodge": _OBJECTS,
    "connection": _OBJECTS,
    "covariant_derivative": _OBJECTS,
    "frame": _OBJECTS,
    "coframe": _OBJECTS,
    "pairing": _OBJECTS,
    "Pairing": _OBJECTS,
    "wedge": _OBJECTS,
    "multi_eval": _OBJECTS,
    "interior": _OBJECTS,
    # tangent-bundle operators (``d``/``L`` shorthands: jacopy.central.tangent)
    "lie_bracket": _TANGENT,
    "lie_derivative": _TANGENT,
    "exterior_d": _TANGENT,
    "sn_bracket": _TANGENT,
    # proof entry points
    "show_equal": _PROOF,
    "prove": _PROOF,
    "ProofChain": _PROOF,
    "ProofStep": _PROOF,
    "ProofFailure": _PROOF,
    "ProofResult": _PROOF,
    "Goal": _PROOF,
    "Assumption": _PROOF,
    "Theorem": _PROOF,
    "TheoremBook": _PROOF,
    "cite": _PROOF,
    "normalize": _PROOF,
    "NormalForm": _PROOF,
    "Definition": _PROOF,
    "ExpansionEngine": _PROOF,
    # display
    "display_expr": _DISPLAY,
    "display_chain": _DISPLAY,
    "display_theorem": _DISPLAY,
    "print_expr": _DISPLAY,
    "print_chain": _DISPLAY,
    "to_latex": _DISPLAY,
    "to_ascii": _DISPLAY,
    "theorem_to_latex_document": _DISPLAY,
}

__all__ = [
    # core expression classes (extension protocol: Expr / Atom)
    "Expr",
    "Atom",
    "Symbol",
    "Integer",
    "Rational",
    "Sum",
    "Product",
    "Power",
    "Neg",
    "Zero",
    "One",
    "NegOne",
    *_LAZY,
]


def __getattr__(name: str) -> Any:
    home = _LAZY.get(name)
    if home is None:
        raise AttributeError(f"module 'jacopy' has no attribute {name!r}")
    value = getattr(importlib.import_module(home), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


if TYPE_CHECKING:  # static view of the lazy names (py.typed consumers)
    from jacopy.algebra import Act, Derivation
    from jacopy.central.objects import (
        TM,
        Bundle,
        Metric,
        Pairing,
        bivector,
        coframe,
        connection,
        covariant_derivative,
        forms,
        frame,
        functions,
        hodge,
        interior,
        metric,
        multi_eval,
        p_vectors,
        pairing,
        tangent_bundle,
        tensors,
        vector_fields,
        wedge,
    )
    from jacopy.central.tangent import (
        exterior_d,
        lie_bracket,
        lie_derivative,
        sn_bracket,
    )
    from jacopy.core import MultiEval, PropertyRegistry, Wedge, default_registry
    from jacopy.display import (
        display_chain,
        display_expr,
        display_theorem,
        print_chain,
        print_expr,
        theorem_to_latex_document,
        to_ascii,
        to_latex,
    )
    from jacopy.proof import (
        Assumption,
        Definition,
        ExpansionEngine,
        Goal,
        NormalForm,
        ProofChain,
        ProofFailure,
        ProofResult,
        ProofStep,
        Theorem,
        TheoremBook,
        cite,
        normalize,
        prove,
        show_equal,
    )
