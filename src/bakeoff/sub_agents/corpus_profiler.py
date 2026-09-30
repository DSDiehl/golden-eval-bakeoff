"""CorpusProfilerAgent implementation."""

from typing import Any
from ..config import get_model_for_role
from ..prompts.loader import load_prompt
from ..tools.corpus_tools import extract_corpus_capabilities, read_customer_corpus_sample

try:
    from google.adk.agents import LlmAgent
except ImportError:
    # Lightweight stub for local offline testing if google-adk is being installed
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")
            self.model = kwargs.get("model")
            self.instruction = kwargs.get("instruction")
            self.tools = kwargs.get("tools", [])


def create_corpus_profiler_agent() -> LlmAgent:
    """Creates the CorpusProfilerAgent instance with strategic model routing."""
    return LlmAgent(
        name="corpus_profiler",
        model=get_model_for_role("corpus_profiler"),
        instruction=load_prompt("corpus_profiler"),
        tools=[read_customer_corpus_sample, extract_corpus_capabilities],
    )
