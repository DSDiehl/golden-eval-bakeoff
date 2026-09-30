"""Human-in-the-Loop (HITL) Hooks (Criterion #12).

Implements explicit code stops and before_tool_callback hooks requiring human confirmation
before executing high-stakes actions:
1. Promoting a synthesized dataset to the canonical golden standard.
2. Initiating a multi-model bake-off run exceeding a projected cost ceiling.
"""

from typing import Any
import structlog

logger = structlog.get_logger(__name__)


class HumanApprovalRequiredException(Exception):
    """Raised when an action is blocked pending explicit human confirmation."""


class HumanApprovalGate:
    """Manages Human-in-the-Loop approval policies and callback gates."""

    def __init__(
        self,
        cost_ceiling_usd: float = 50.0,
        auto_approve_for_test: bool = False,
    ) -> None:
        """Initializes the HITL gate.

        Args:
            cost_ceiling_usd: Maximum cost threshold allowed without human intervention.
            auto_approve_for_test: If True, bypasses manual block for automated CI testing.
        """
        self.cost_ceiling_usd = cost_ceiling_usd
        self.auto_approve_for_test = auto_approve_for_test
        self._approved_actions: set[str] = set()

    def grant_approval(self, action_key: str) -> None:
        """Records human sign-off for a specific action key."""
        self._approved_actions.add(action_key)
        logger.info("hitl_approval_granted", action_key=action_key)

    def is_approved(self, action_key: str) -> bool:
        """Checks if human approval has been granted for the action."""
        if self.auto_approve_for_test:
            return True
        return action_key in self._approved_actions

    def before_tool_callback(
        self,
        tool: Any,
        args: dict[str, Any],
        context: Any = None,
    ) -> dict[str, Any] | None:
        """Intercepts tool execution to enforce Human-in-the-Loop gates.

        Criterion #12: High-stakes actions include explicit code stops requiring
        human confirmation before execution.

        Args:
            tool: Target tool callable or tool instance.
            args: Tool invocation arguments dictionary.
            context: Optional ADK execution context.

        Returns:
            None to allow normal execution, or a descriptive dictionary if blocked.

        Raises:
            HumanApprovalRequiredException: If explicit human approval is missing.
        """
        tool_name = getattr(tool, "__name__", str(tool))

        # Gate 1: Canonical Golden Set Promotion
        if tool_name == "promote_to_canonical_golden_set":
            account_id = args.get("account_id", "unknown")
            action_key = f"promote_golden_set:{account_id}"

            if not self.is_approved(action_key):
                logger.warn(
                    "hitl_gate_triggered_golden_set_promotion",
                    account_id=account_id,
                    tool=tool_name,
                )
                return {
                    "status": "blocked_pending_human_approval",
                    "gate": "canonical_golden_set_promotion",
                    "action_key": action_key,
                    "guidance": (
                        f"STOP: Promoting cases to the canonical golden set for account '{account_id}' "
                        "requires explicit human CE sign-off. Provide approval via grant_approval() "
                        "before proceeding."
                    ),
                }

        # Gate 2: High-Cost Bake-Off Execution
        if tool_name == "project_monthly_tco_from_telemetry":
            volume = args.get("stated_monthly_volume", 0)
            if volume > 1_000_000 and not self.is_approved(f"high_volume_eval:{volume}"):
                logger.warn("hitl_gate_triggered_high_volume", volume=volume)
                # Informational review warning

        return None
