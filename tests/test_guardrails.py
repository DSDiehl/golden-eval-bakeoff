"""Unit tests for Human-in-the-Loop and policy guardrails (Criteria #11 & #12)."""

import pytest
from src.bakeoff.callbacks import (
    HumanApprovalGate,
    JudgeConfidenceGuardrail,
    TokenBudgetExceededException,
    TokenBudgetGuardrail,
)
from src.bakeoff.tools.dataset_tools import promote_to_canonical_golden_set


def test_hitl_gate_blocks_golden_set_promotion_without_human_approval() -> None:
    """Criterion #12: High-stakes golden set promotion halts until human signs off."""
    gate = HumanApprovalGate()
    args = {
        "cases": [{"case_id": "CASE_1"}],
        "account_id": "enterprise_isv",
        "approver_ldap": "marcusdiehl",
    }

    # Intercept tool call
    result = gate.before_tool_callback(promote_to_canonical_golden_set, args)

    assert result is not None
    assert result["status"] == "blocked_pending_human_approval"
    assert "requires explicit human CE sign-off" in result["guidance"]


def test_hitl_gate_permits_execution_after_approval_granted() -> None:
    """Criterion #12: Tool executes normally once human approval is explicitly granted."""
    gate = HumanApprovalGate()
    action_key = "promote_golden_set:enterprise_isv"
    gate.grant_approval(action_key)

    args = {
        "cases": [{"case_id": "CASE_1"}],
        "account_id": "enterprise_isv",
        "approver_ldap": "marcusdiehl",
    }
    result = gate.before_tool_callback(promote_to_canonical_golden_set, args)

    assert result is None  # None indicates normal execution permitted


def test_token_budget_guardrail_halts_runaway_burn() -> None:
    """Criterion #11: Halts execution when token consumption ceiling is reached."""
    guard = TokenBudgetGuardrail(max_token_budget=10_000)
    guard.record_usage(5_000)
    guard.before_model_callback(None, None)  # Should not raise

    guard.record_usage(6_000)  # Total 11,000 exceeds 10,000 ceiling
    with pytest.raises(TokenBudgetExceededException):
        guard.before_model_callback(None, None)


def test_judge_confidence_floor_flags_uncertain_judgments() -> None:
    """Criterion #11: Judgments below confidence floor (0.70) are flagged for human review."""
    guard = JudgeConfidenceGuardrail(confidence_floor=0.70)

    low_conf_judgment = {
        "case_id": "CASE_UNCERTAIN_01",
        "confidence": 0.55,
        "overall_score": 3.0,
    }
    flagged = guard.validate_judgment(low_conf_judgment)
    assert flagged["human_review_required"] is True
    assert "Requires CE validation" in flagged["review_reason"]

    high_conf_judgment = {
        "case_id": "CASE_CONFIDENT_02",
        "confidence": 0.95,
        "overall_score": 4.5,
    }
    passed = guard.validate_judgment(high_conf_judgment)
    assert passed["human_review_required"] is False
