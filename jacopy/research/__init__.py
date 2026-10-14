"""
The research interface: the layer on which a
user writes *their own* question. Five components, each born from a piece
that ``examples/bracket_twist_walkthrough.ipynb`` had to do by hand:

* :mod:`sections` — typed generalized sections ``U ⊕ ω₂ ⊕ ω₅``;
* :mod:`block_matrix` — block-operator matrices with derived action,
  product and (unipotent) inverse;
* :mod:`engine_assembly` — build the rewrite engine from the
  expressions to be checked, with a self-explaining report;
* :mod:`axiom_suite` — the generic Courant-type condition runner and
  the Ψ-transport of a whole structure;
* :mod:`antisymmetrize` — index antisymmetrisation for frame formulas.

:mod:`structure_kinds` is the registry ``assemble_engine`` reads: a new
structure type (and its node families / family rules) is registered
there, without editing the library.
"""

from jacopy.research.antisymmetrize import (
    antisymmetrize,  # old name of antisymmetrize_indices (kept, not in __all__)
    antisymmetrize_indices,
    permutation_sign,
    rename_indices,
    swap_indices,
)
from jacopy.research.axiom_suite import (
    AlgebroidData,
    AxiomSuite,
    Bracket,
    CheckResult,
    SuiteReport,
)
from jacopy.research.block_matrix import (
    BlockMatrix,
    Identity,
    Map,
    Operator,
    Zero,  # old name of ZeroOperator (kept importable, not in __all__)
    ZeroOperator,
    as_operator,
)
from jacopy.research.engine_assembly import (
    Scan,
    WedgeGradedOrderDefinition,
    WedgeScalarFactorDefinition,
    assemble_engine,
    assembly_report,
)
from jacopy.research.sections import (
    GeneralizedSection,
    SectionType,
    Slot,
)
from jacopy.research.structure_kinds import (
    StructureKind,
    register_family,
    register_family_rule,
    register_structure_kind,
)

__all__ = [
    "AlgebroidData",
    "AxiomSuite",
    "BlockMatrix",
    "Bracket",
    "CheckResult",
    "GeneralizedSection",
    "Identity",
    "Map",
    "Operator",
    "Scan",
    "SectionType",
    "Slot",
    "StructureKind",
    "SuiteReport",
    "WedgeGradedOrderDefinition",
    "WedgeScalarFactorDefinition",
    "ZeroOperator",
    "antisymmetrize_indices",
    "as_operator",
    "assemble_engine",
    "assembly_report",
    "permutation_sign",
    "register_family",
    "register_family_rule",
    "register_structure_kind",
    "rename_indices",
    "swap_indices",
]
