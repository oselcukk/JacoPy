"""Oracle verdicts and reports (no sympy, no engine imports)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional, Tuple

AGREE = "AGREE"
DISAGREE = "DISAGREE"
UNSUPPORTED = "UNSUPPORTED"
AMBIGUOUS = "AMBIGUOUS"
ASSUMPTION_LEAK = "ASSUMPTION_LEAK"
VERDICTS = (AGREE, DISAGREE, UNSUPPORTED, AMBIGUOUS, ASSUMPTION_LEAK)

#: Verdicts that refute a closure (strict mode raises on them).
REFUTING = (DISAGREE, ASSUMPTION_LEAK)


def _short(text: str, limit: int = 400) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


@dataclass
class Witness:
    """One model in which the two sides were compared."""

    model: str
    mode: str
    lhs_value: str
    rhs_value: str
    equal: bool


@dataclass
class OracleReport:
    """The oracle's verdict on one equation ``lhs = rhs``.

    AGREE means "not refuted in N models" — the oracle is a falsifier,
    never a proof (SPEC §7)."""

    verdict: str
    lhs: str = ""
    rhs: str = ""
    seed: int = 0
    samples: int = 0
    models: List[str] = field(default_factory=list)
    degree_assignments: List[str] = field(default_factory=list)
    unsupported_type: Optional[str] = None
    unsupported_path: Optional[Tuple] = None
    detail: str = ""
    witnesses: List[Witness] = field(default_factory=list)
    reproduced: Optional[bool] = None
    leak_structure: Optional[str] = None
    #: the ASSUMPTION_LEAK counter-model could not be evaluated (AGREE is
    #: then NOT a leak-free certificate; strict mode reports it)
    leak_unchecked: Optional[str] = None
    source: str = ""
    nodeid: str = ""
    elapsed: float = 0.0

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"unknown verdict {self.verdict!r}")
        self.lhs = _short(self.lhs)
        self.rhs = _short(self.rhs)

    @property
    def refutes(self) -> bool:
        return self.verdict in REFUTING

    def summary(self) -> str:
        """One LaTeX-safe line for ProofResult displays (plain text)."""
        if self.verdict == AGREE:
            if self.detail.startswith("trivial"):
                return f"oracle: AGREE ({self.detail})"
            extra = f"; {', '.join(self.degree_assignments)} checked" if self.degree_assignments else ""
            leak = f"; assumption-leak check NOT done ({self.leak_unchecked})" if self.leak_unchecked else ""
            return f"oracle: AGREE ({self.samples} model(s), seed {self.seed}{extra}{leak})"
        if self.verdict == UNSUPPORTED:
            return f"oracle: UNSUPPORTED ({self.unsupported_type} at {self.unsupported_path})"
        return f"oracle: {self.verdict} ({self.detail})"

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["unsupported_path"] is not None:
            d["unsupported_path"] = [str(x) for x in d["unsupported_path"]]
        return d

    def __str__(self) -> str:
        lines = [self.summary(), f"  equation: {self.lhs} = {self.rhs}"]
        for w in self.witnesses:
            if not w.equal:
                lines.append(f"  model {w.model} [{w.mode}]: lhs={_short(w.lhs_value, 200)} rhs={_short(w.rhs_value, 200)}")
        return "\n".join(lines)


@dataclass
class ChainReport:
    """Step-by-step check of a proof chain (K4-2): the first refuted
    step names the rule that broke the equation."""

    steps: List[OracleReport]
    first_bad_index: Optional[int] = None
    first_bad_rule: Optional[str] = None

    @property
    def verdict(self) -> str:
        if self.first_bad_index is not None:
            return DISAGREE
        if any(r.verdict == UNSUPPORTED for r in self.steps):
            return UNSUPPORTED
        if any(r.verdict == AMBIGUOUS for r in self.steps):
            return AMBIGUOUS
        return AGREE
