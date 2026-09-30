"""CaseSynthesizerAgent implementation."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..tools.dataset_tools import synthesize_eval_cases_for_capability

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_case_synthesizer_agent() -> LlmAgent:
    """Creates the CaseSynthesizerAgent instance routed to Gemini Flash for high-volume generation."""
    return LlmAgent(
        name="case_synthesizer",
        model=get_model_for_role("case_synthesizer"),
        instruction=load_prompt("case_synthesizer"),
        tools=[synthesize_eval_cases_for_capability],
    )
