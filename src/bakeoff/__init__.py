"""Golden Eval & Model Bake-Off Agent package."""

from .agent import (
    build_bakeoff_runner,
    build_dataset_pipeline,
    build_judge_panel,
    create_bakeoff_coordinator,
    root_agent,
)
from .config import DEFAULT_CANDIDATES, MODEL_ROUTING, get_model_for_role, resolve_secret

__all__ = [
    "root_agent",
    "create_bakeoff_coordinator",
    "build_dataset_pipeline",
    "build_bakeoff_runner",
    "build_judge_panel",
    "MODEL_ROUTING",
    "DEFAULT_CANDIDATES",
    "get_model_for_role",
    "resolve_secret",
]
