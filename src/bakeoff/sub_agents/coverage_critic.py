"""CoverageCriticAgent implementation."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..schemas.coverage import CoverageVerdict
from ..tools.dataset_tools import evaluate_coverage_against_taxonomy

try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import exit_loop
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")

    def exit_loop() -> dict[str, str]:  # type: ignore
        """Exit the current loop agent."""
        return {"status": "exit_loop"}


def create_coverage_critic_agent() -> LlmAgent:
    """Creates the CoverageCriticAgent routed to Gemini Pro for rigorous gap analysis."""
    return LlmAgent(
        name="coverage_critic",
        model=get_model_for_role("coverage_critic"),
        instruction=load_prompt("coverage_critic"),
        tools=[evaluate_coverage_against_taxonomy, exit_loop],
        output_schema=CoverageVerdict,
    )
