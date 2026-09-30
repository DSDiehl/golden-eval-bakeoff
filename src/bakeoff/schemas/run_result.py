"""Model execution response and empirical token telemetry schemas.

Captures raw completions, latency percentiles, token usage, and execution status
for each candidate model under test.
"""

from typing import Literal
import pydantic

BaseModel = pydantic.BaseModel
Field = pydantic.Field
ConfigDict = pydantic.ConfigDict


class ModelResponse(BaseModel):
    """Execution output from a single candidate model invocation."""

    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(
        description="Generated completion text from the candidate model."
    )
    latency_ms: float = Field(
        ge=0.0,
        description="End-to-end request duration measured in milliseconds."
    )
    input_tokens: int = Field(
        ge=0,
        description="Exact prompt token count measured via model telemetry."
    )
    output_tokens: int = Field(
        ge=0,
        description="Exact completion token count measured via model telemetry."
    )
    status: Literal["success", "rate_limited", "context_overflow", "error"] = Field(
        default="success",
        description="Execution status of the invocation."
    )
    error_message: str | None = Field(
        default=None,
        description="Descriptive error detail or guided recovery text if status is not success."
    )


class TokenTelemetry(BaseModel):
    """Aggregated empirical telemetry across a suite of runs for one candidate model."""

    model_config = ConfigDict(extra="forbid")

    candidate_model: str = Field(
        description="Identifier of the model (e.g., gemini-3.8-flash, claude-sonnet-5)."
    )
    sample_size: int = Field(
        ge=1,
        description="Number of evaluation cases executed."
    )
    p50_latency_ms: float = Field(
        ge=0.0,
        description="Median request latency in milliseconds."
    )
    p95_latency_ms: float = Field(
        ge=0.0,
        description="95th percentile request latency in milliseconds."
    )
    avg_input_tokens: float = Field(
        ge=0.0,
        description="Average input tokens per case."
    )
    avg_output_tokens: float = Field(
        ge=0.0,
        description="Average output tokens per case."
    )
    total_tokens: int = Field(
        ge=0,
        description="Total tokens consumed across all cases."
    )
    measured_error_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction of requests that failed or encountered rate limiting."
    )


class RunResult(BaseModel):
    """Coupled execution outcome binding a test case to a candidate model's response."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(
        description="Identifier of the test case executed."
    )
    candidate_model: str = Field(
        description="Identifier of the candidate model evaluated."
    )
    response: ModelResponse = Field(
        description="Measured response and performance telemetry."
    )
