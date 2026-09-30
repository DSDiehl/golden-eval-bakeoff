"""Evaluation case and capability taxonomy schemas for Golden Eval & Bake-Off Agent.

Provides strict Pydantic models for domain taxonomy definitions, identified capability
gaps, and synthesized evaluation test cases.
"""

from typing import Literal
import pydantic

BaseModel = pydantic.BaseModel
Field = pydantic.Field
ConfigDict = pydantic.ConfigDict


class CapabilityTaxonomy(BaseModel):
    """Domain capability category derived from customer corpus."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str = Field(
        description="Unique identifier for the capability (e.g., CAP_AUTHZ_POLICY)."
    )
    name: str = Field(
        description="Human-readable title of the capability."
    )
    description: str = Field(
        description="Detailed description of what the model is expected to handle under this capability."
    )
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="high",
        description="Business priority or frequency of the capability in production."
    )
    category: str = Field(
        default="core_capability",
        description="High-level category grouping (e.g., security, reasoning, retrieval)."
    )


class CapabilityGap(BaseModel):
    """Representation of an uncovered or under-tested capability gap."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str = Field(
        description="ID of the capability that lacks sufficient test coverage."
    )
    capability_name: str = Field(
        description="Human-readable name of the affected capability."
    )
    missing_aspect: str = Field(
        description="Specific scenario, edge case, or difficulty band missing from current coverage."
    )
    required_difficulty: Literal["basic", "intermediate", "adversarial"] = Field(
        description="Target difficulty level required to close the coverage gap."
    )
    rationale: str = Field(
        description="Justification explaining why this gap impacts model selection confidence."
    )


class EvalCase(BaseModel):
    """A canonical, structured evaluation case generated for model bake-off testing."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(
        description="Globally unique identifier for the evaluation case (e.g., CASE_SEC_001)."
    )
    capability: str = Field(
        description="Capability ID or name this test case evaluates."
    )
    prompt: str = Field(
        description="Exact prompt text submitted to the candidate models under test."
    )
    expected_behavior: str = Field(
        description="Descriptive benchmark criteria against which the response is qualitatively judged."
    )
    rubric_dimensions: list[str] = Field(
        default_factory=lambda: ["accuracy", "relevance", "instruction_following", "safety"],
        description="Quality dimensions to be graded by the judge panel."
    )
    difficulty: Literal["basic", "intermediate", "adversarial"] = Field(
        default="intermediate",
        description="Complexity level of the test case."
    )
    source: Literal["synthesized", "human_authored", "corpus_derived"] = Field(
        default="synthesized",
        description="Origin provenance of this evaluation case."
    )
    golden_standard: bool = Field(
        default=False,
        description="True if explicitly verified and signed off by a human CE."
    )
