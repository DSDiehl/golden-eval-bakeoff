"""Deterministic scorer agent wrapping exact arithmetic calculations."""

from typing import Any
from ..schemas.judgment import DeterministicMetrics
from ..tools.scoring_tools import compute_deterministic_metrics

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_deterministic_scorer_agent() -> LlmAgent:
    """Creates the DeterministicScorer agent running arithmetic evaluation."""
    instruction = (
        "You are the DeterministicScorer. Evaluate exact match criteria, calculate total tokens, "
        "and record latency using compute_deterministic_metrics. Do not use subjective grading."
    )
    return LlmAgent(
        name="deterministic_scorer",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[compute_deterministic_metrics],
        output_schema=DeterministicMetrics,
    )
