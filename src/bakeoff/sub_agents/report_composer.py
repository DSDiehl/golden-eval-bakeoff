"""ReportComposerAgent implementation."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..schemas.judgment import BakeOffReport

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_report_composer_agent() -> LlmAgent:
    """Creates the ReportComposerAgent routed to Gemini Pro for executive synthesis."""
    return LlmAgent(
        name="report_composer",
        model=get_model_for_role("report_composer"),
        instruction=load_prompt("report_composer"),
        tools=[],
        output_schema=BakeOffReport,
    )
