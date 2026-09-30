"""TCOAnalystAgent implementation."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..schemas.judgment import TCOProjection
from ..tools.cost_tools import get_model_pricing_tier, project_monthly_tco_from_telemetry

try:
    from google.adk.agents import LlmAgent
except ImportError:
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")


def create_tco_analyst_agent() -> LlmAgent:
    """Creates the TCOAnalystAgent routed to Gemini Flash for empirical cost projections."""
    return LlmAgent(
        name="tco_analyst",
        model=get_model_for_role("tco_analyst"),
        instruction=load_prompt("tco_analyst"),
        tools=[get_model_pricing_tier, project_monthly_tco_from_telemetry],
        output_schema=TCOProjection,
    )
