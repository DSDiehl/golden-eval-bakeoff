"""QualityJudgeAgent implementation with anti-bias constitution and strict Judgment output schema."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..schemas.judgment import Judgment
from ..tools.scoring_tools import score_response_against_rubric

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_quality_judge_agent() -> LlmAgent:
    """Creates the QualityJudgeAgent instance with Pro model and strict Judgment output schema."""
    return LlmAgent(
        name="quality_judge",
        model=get_model_for_role("quality_judge"),
        instruction=load_prompt("quality_judge"),
        tools=[score_response_against_rubric],
        output_schema=Judgment,
    )
