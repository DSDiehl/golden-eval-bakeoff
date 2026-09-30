"""Judgments, TCO projections, and final bake-off report schemas.

Enforces structured qualitative scoring from the QualityJudgeAgent and deterministic
projections from the TCOAnalystAgent.
"""

from typing import Literal
import pydantic
from .eval_case import EvalCase
from .run_result import TokenTelemetry

BaseModel = pydantic.BaseModel
Field = pydantic.Field
ConfigDict = pydantic.ConfigDict


class DimensionScore(BaseModel):
    """Evaluation score for a single rubric dimension."""

    model_config = ConfigDict(extra="forbid")

    dimension: str = Field(
        description="Rubric dimension name (e.g., accuracy, relevance, safety)."
    )
    score: int = Field(
        ge=1,
        le=5,
        description="Integer rating on a 1-5 scale anchored in the rubric constitution."
    )
    reasoning: str = Field(
        description="Detailed explanation justifying the score."
    )
    cited_evidence: str = Field(
        description="Mandatory direct quote or verifiable citation from the response text."
    )


class Judgment(BaseModel):
    """Comprehensive qualitative judgment emitted by QualityJudgeAgent for one case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(
        description="Identifier of the evaluated test case."
    )
    candidate_model: str = Field(
        description="Identifier of the candidate model evaluated."
    )
    scores: dict[str, DimensionScore] = Field(
        description="Mapping of dimension name to structured score object."
    )
    overall_score: float = Field(
        ge=1.0,
        le=5.0,
        description="Composite arithmetic mean across all evaluated dimensions."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Self-assessed confidence level of the judge (0.0 to 1.0)."
    )
    verdict: Literal["pass", "marginal", "fail"] = Field(
        description="Categorical judgment verdict."
    )
    cited_evidence: str = Field(
        description="Primary cited evidence anchoring the overall verdict."
    )


class DeterministicMetrics(BaseModel):
    """Deterministic, arithmetic scoring metrics."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(
        description="Identifier of the test case."
    )
    candidate_model: str = Field(
        description="Identifier of the candidate model."
    )
    exact_match: bool | None = Field(
        default=None,
        description="True if output matches expected canonical answer exactly, if applicable."
    )
    latency_ms: float = Field(
        description="End-to-end response latency in ms."
    )
    input_tokens: int = Field(
        description="Exact prompt tokens."
    )
    output_tokens: int = Field(
        description="Exact completion tokens."
    )
    total_tokens: int = Field(
        description="Total tokens consumed."
    )


class TCOProjection(BaseModel):
    """Model total cost of ownership (TCO) projected from empirical token telemetry."""

    model_config = ConfigDict(extra="forbid")

    candidate_model: str = Field(
        description="Candidate model identifier."
    )
    cost_per_1k_interactions_usd: float = Field(
        ge=0.0,
        description="Projected cost per 1,000 production interactions."
    )
    projected_monthly_cost_usd: float = Field(
        ge=0.0,
        description="Projected monthly total cost at the customer's stated monthly volume."
    )
    stated_monthly_volume: int = Field(
        ge=1,
        description="Customer stated monthly transaction volume."
    )
    avg_input_tokens: float = Field(
        description="Measured average input tokens per query."
    )
    avg_output_tokens: float = Field(
        description="Measured average output tokens per query."
    )
    input_rate_per_1m: float = Field(
        description="Published price per 1M input tokens."
    )
    output_rate_per_1m: float = Field(
        description="Published price per 1M output tokens."
    )


class ModelBakeOffSummary(BaseModel):
    """Aggregated bake-off standings for a candidate model."""

    model_config = ConfigDict(extra="forbid")

    candidate_model: str = Field(
        description="Model name."
    )
    rank: int = Field(
        description="Relative rank (1 = winner)."
    )
    overall_quality_score: float = Field(
        description="Average quality score across all evaluated cases (1.0 to 5.0)."
    )
    p50_latency_ms: float = Field(
        description="Median latency."
    )
    p95_latency_ms: float = Field(
        description="95th percentile latency."
    )
    projected_monthly_tco_usd: float = Field(
        description="Estimated monthly spend."
    )
    pass_rate: float = Field(
        description="Percentage of cases receiving a pass verdict."
    )


class BakeOffReport(BaseModel):
    """Complete, executive-ready bake-off comparison deliverable."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(
        description="Unique evaluation run identifier."
    )
    account_id: str = Field(
        description="Customer or account identifier (e.g., enterprise_isv, acme_corp)."
    )
    timestamp: str = Field(
        description="ISO 8601 timestamp of report generation."
    )
    domain_description: str = Field(
        description="Summary of the customer domain corpus evaluated."
    )
    golden_set_size: int = Field(
        description="Number of canonical test cases in the golden evaluation set."
    )
    candidates_evaluated: list[str] = Field(
        description="List of model identifiers evaluated."
    )
    standings: list[ModelBakeOffSummary] = Field(
        description="Ranked standings across quality, latency, and TCO."
    )
    tco_projections: list[TCOProjection] = Field(
        description="Detailed TCO breakdown per model."
    )
    telemetry_summary: list[TokenTelemetry] = Field(
        description="Detailed latency and token statistics."
    )
    recommended_model: str = Field(
        description="Definitive model recommendation based on quality and cost trade-offs."
    )
    recommendation_rationale: str = Field(
        description="Executive summary justifying the recommendation."
    )
    full_judgments: list[Judgment] = Field(
        default_factory=list,
        description="Comprehensive list of individual case judgments."
    )
