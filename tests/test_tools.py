"""Unit tests for tool docstrings, descriptive naming, and guided error handling (Criteria #1, #2, #4)."""

import inspect
from src.bakeoff import tools


def test_comprehensive_tool_docstrings_present() -> None:
    """Criterion #1: Every tool includes human-readable description and parameters."""
    tool_funcs = [
        tools.read_customer_corpus_sample,
        tools.extract_corpus_capabilities,
        tools.synthesize_eval_cases_for_capability,
        tools.evaluate_coverage_against_taxonomy,
        tools.promote_to_canonical_golden_set,
        tools.execute_case_against_candidate_model,
        tools.compute_deterministic_metrics,
        tools.score_response_against_rubric,
        tools.get_model_pricing_tier,
        tools.project_monthly_tco_from_telemetry,
    ]

    for fn in tool_funcs:
        doc = inspect.getdoc(fn)
        assert doc is not None, f"Tool '{fn.__name__}' is missing docstring!"
        assert "Args:" in doc, f"Tool '{fn.__name__}' docstring is missing 'Args:' section."
        assert "Returns:" in doc, f"Tool '{fn.__name__}' docstring is missing 'Returns:' section."


def test_descriptive_tool_names() -> None:
    """Criterion #2: Tool names encode specific action and domain object."""
    tool_names = [
        "read_customer_corpus_sample",
        "extract_corpus_capabilities",
        "synthesize_eval_cases_for_capability",
        "evaluate_coverage_against_taxonomy",
        "promote_to_canonical_golden_set",
        "execute_case_against_candidate_model",
        "compute_deterministic_metrics",
        "score_response_against_rubric",
        "project_monthly_tco_from_telemetry",
    ]
    for name in tool_names:
        assert hasattr(tools, name), f"Expected descriptive tool '{name}' not found."


def test_guided_error_handling_rate_limit_429() -> None:
    """Criterion #4: Tool returns structured recovery guidance rather than crashing on 429."""
    result = tools.execute_case_against_candidate_model(
        case_id="CASE_RATE_LIMIT_TEST",
        prompt="[TRIGGER_429_RATE_LIMIT] Test scenario",
        candidate_model="gemini-2.5-pro",
    )
    assert result["status"] == "rate_limited"
    assert result["retry_after_s"] == 30
    assert "guidance" in result
    assert "Reduce batch concurrency" in result["guidance"]


def test_guided_error_handling_context_overflow() -> None:
    """Criterion #4: Tool returns recovery instructions on context window overflow."""
    result = tools.execute_case_against_candidate_model(
        case_id="CASE_OVERFLOW_TEST",
        prompt="[TRIGGER_CONTEXT_OVERFLOW] Big prompt",
        candidate_model="gemini-2.5-pro",
    )
    assert result["status"] == "context_overflow"
    assert "guidance" in result
    assert "compaction" in result["guidance"]


def test_guided_error_handling_missing_corpus_file() -> None:
    """Criterion #4: Missing file returns descriptive recovery instructions."""
    result = tools.read_customer_corpus_sample(
        corpus_path="/nonexistent/path/sample.json",
        max_records=10,
    )
    assert result["status"] == "error"
    assert result["error_type"] == "file_not_found"
    assert "guidance" in result
