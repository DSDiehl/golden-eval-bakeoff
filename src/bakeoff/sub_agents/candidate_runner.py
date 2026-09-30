"""CandidateRunnerAgent implementation for parallel model execution."""

from typing import Any
from ..tools.model_invoke_tools import execute_case_against_candidate_model

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_candidate_runner_agent(candidate_model: str) -> LlmAgent:
    """Creates a CandidateRunnerAgent dedicated to a specific candidate model.

    Args:
        candidate_model: Model under test (e.g. 'gemini-3.8-flash', 'claude-sonnet-5').

    Returns:
        Configured LlmAgent instance.
    """
    clean_name = candidate_model.replace("-", "_").replace(".", "_")
    instruction = (
        f"You are the CandidateRunner for candidate model '{candidate_model}'. "
        "Your duty is to execute each test case prompt using execute_case_against_candidate_model "
        "and record raw text completions, execution latency, and exact token counts."
    )
    return LlmAgent(
        name=f"runner_{clean_name}",
        model="gemini-3.8-flash",
        instruction=instruction,
        tools=[execute_case_against_candidate_model],
    )
