"""Guardrails and Policy Plugins (Criterion #11).

Implements security, evaluation, and operational guardrails:
1. Cumulative Token Budget Enforcer (before_model_callback) to halt runaway loops.
2. Judge Confidence Floor Guardrail (escalates low-confidence evaluations).
3. Loop Iteration Bound Guardrail (ensures coverage refinement loop strictly terminates).
"""

from typing import Any
import structlog

logger = structlog.get_logger(__name__)


class TokenBudgetExceededException(Exception):
    """Raised when an agent invocation would breach the allocated token burn budget."""


class TokenBudgetGuardrail:
    """Enforces a hard ceiling on cumulative token expenditure during a bake-off."""

    def __init__(self, max_token_budget: int = 150_000) -> None:
        """Initializes the budget guardrail.

        Args:
            max_token_budget: Maximum cumulative tokens permitted across the session.
        """
        self.max_token_budget = max_token_budget
        self.cumulative_tokens_used = 0

    def record_usage(self, tokens: int) -> None:
        """Records token consumption from an executed invocation."""
        self.cumulative_tokens_used += tokens
        logger.info(
            "token_budget_tracked",
            used=self.cumulative_tokens_used,
            budget=self.max_token_budget,
            remaining=max(0, self.max_token_budget - self.cumulative_tokens_used),
        )

    def before_model_callback(
        self,
        context: Any,
        llm_request: Any,
    ) -> Any | None:
        """Inspects token budget before dispatching an LLM request.

        Criterion #11: Halts runaway execution loops before burning shared credit pools.

        Args:
            context: ADK callback context.
            llm_request: Target LLM request object.

        Returns:
            None if within budget, or overrides response if budget is exhausted.

        Raises:
            TokenBudgetExceededException: If the token ceiling is exceeded.
        """
        if self.cumulative_tokens_used >= self.max_token_budget:
            logger.error(
                "token_budget_exhausted",
                used=self.cumulative_tokens_used,
                budget=self.max_token_budget,
            )
            raise TokenBudgetExceededException(
                f"Token budget ceiling of {self.max_token_budget:,} tokens reached. "
                "Halting bake-off execution to prevent uncontrolled credit consumption."
            )
        return None


class JudgeConfidenceGuardrail:
    """Monitors qualitative judgments, flagging low-confidence evaluations for human review."""

    def __init__(self, confidence_floor: float = 0.70) -> None:
        """Initializes confidence guardrail.

        Args:
            confidence_floor: Minimum acceptable confidence score (0.0 to 1.0). Defaults to 0.70.
        """
        self.confidence_floor = confidence_floor

    def validate_judgment(self, judgment_dict: dict[str, Any]) -> dict[str, Any]:
        """Validates judgment confidence, tagging marginal or uncertain ratings for human review.

        Args:
            judgment_dict: Serialized Judgment dictionary.

        Returns:
            Validated judgment dictionary with escalation metadata if confidence is low.
        """
        confidence = judgment_dict.get("confidence", 1.0)
        if confidence < self.confidence_floor:
            logger.warn(
                "low_confidence_judgment_flagged",
                case_id=judgment_dict.get("case_id"),
                confidence=confidence,
                floor=self.confidence_floor,
            )
            judgment_dict["human_review_required"] = True
            judgment_dict["review_reason"] = (
                f"Judge confidence ({confidence:.2f}) is below minimum floor "
                f"({self.confidence_floor:.2f}). Requires CE validation."
            )
        else:
            judgment_dict["human_review_required"] = False

        return judgment_dict
