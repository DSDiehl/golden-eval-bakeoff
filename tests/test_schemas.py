"""Unit tests for Pydantic domain, run, and evaluation schemas (Criterion #3)."""

import pytest
from pydantic import ValidationError
from src.bakeoff.schemas.coverage import CoverageVerdict
from src.bakeoff.schemas.eval_case import CapabilityTaxonomy, EvalCase
from src.bakeoff.schemas.judgment import DimensionScore, Judgment, TCOProjection
from src.bakeoff.schemas.run_result import ModelResponse, RunResult


def test_capability_taxonomy_valid() -> None:
    cap = CapabilityTaxonomy(
        capability_id="CAP_TEST",
        name="Test Capability",
        description="Detailed description of test capability.",
        priority="critical",
    )
    assert cap.capability_id == "CAP_TEST"
    assert cap.priority == "critical"


def test_eval_case_validation_rejects_invalid_difficulty() -> None:
    with pytest.raises(ValidationError):
        EvalCase(
            case_id="CASE_001",
            capability="CAP_TEST",
            prompt="Test prompt",
            expected_behavior="Expected output",
            difficulty="impossible",  # Invalid choice  # type: ignore
        )


def test_coverage_verdict_schema_bounds() -> None:
    with pytest.raises(ValidationError):
        CoverageVerdict(
            coverage_score=1.5,  # Exceeds max 1.0
            passes_gate=False,
            reasoning="Too high",
        )


def test_dimension_score_requires_cited_evidence() -> None:
    dim = DimensionScore(
        dimension="accuracy",
        score=5,
        reasoning="Good answer",
        cited_evidence="Quoted verbatim evidence here",
    )
    assert dim.cited_evidence != ""
    assert dim.score == 5


def test_tco_projection_serialization() -> None:
    proj = TCOProjection(
        candidate_model="gemini-2.5-flash",
        cost_per_1k_interactions_usd=0.045,
        projected_monthly_cost_usd=225.0,
        stated_monthly_volume=5_000_000,
        avg_input_tokens=450.0,
        avg_output_tokens=120.0,
        input_rate_per_1m=0.075,
        output_rate_per_1m=0.30,
    )
    dumped = proj.model_dump()
    assert dumped["projected_monthly_cost_usd"] == 225.0
