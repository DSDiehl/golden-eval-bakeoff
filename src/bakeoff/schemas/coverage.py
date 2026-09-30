"""Coverage verdict and refinement schemas for Golden Eval & Bake-Off Agent.

Provides strict schemas to quantify capability coverage and control termination of
the iterative refinement loop.
"""

import pydantic
from .eval_case import CapabilityGap

BaseModel = pydantic.BaseModel
Field = pydantic.Field
ConfigDict = pydantic.ConfigDict


class CoverageVerdict(BaseModel):
    """Quantitative evaluation of dataset coverage against domain capability taxonomy."""

    model_config = ConfigDict(extra="forbid")

    coverage_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Calculated coverage ratio across all required capabilities (0.0 to 1.0)."
    )
    gaps: list[CapabilityGap] = Field(
        default_factory=list,
        description="List of specific capability deficiencies requiring additional cases."
    )
    passes_gate: bool = Field(
        description="True if coverage score exceeds the threshold and all critical gaps are closed."
    )
    reasoning: str = Field(
        description="Detailed justification from the CoverageCriticAgent explaining the verdict."
    )
    iteration_count: int = Field(
        default=1,
        description="Current loop iteration count."
    )


class RefinementIteration(BaseModel):
    """Snapshot record of one pass through the coverage refinement loop."""

    model_config = ConfigDict(extra="forbid")

    iteration: int = Field(
        description="1-indexed iteration number."
    )
    cases_before: int = Field(
        description="Dataset size before this refinement iteration."
    )
    cases_added: int = Field(
        description="Number of targeted cases synthesized during this iteration."
    )
    coverage_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Coverage score achieved at the conclusion of this iteration."
    )
    gate_achieved: bool = Field(
        description="Whether the quantitative gate was passed."
    )
