"""Integration tests for Multi-Agent Orchestration Patterns and Model Routing (Criteria #9 & #10)."""

from src.bakeoff.agent import (
    build_bakeoff_runner,
    build_dataset_pipeline,
    build_judge_panel,
    create_bakeoff_coordinator,
    root_agent,
)
from src.bakeoff.config import MODEL_ROUTING


def test_strategic_model_routing_differentiated() -> None:
    """Criterion #10: CI asserts that model routing is strategically differentiated.

    A regression where 'everything is Pro' or 'everything is Flash' must fail the build.
    """
    pro_roles = ["corpus_profiler", "coverage_critic", "quality_judge", "report_composer"]
    flash_roles = ["case_synthesizer", "case_refiner", "tco_analyst"]

    for role in pro_roles:
        model = MODEL_ROUTING[role]
        assert "pro" in model.lower(), f"Expected Pro model for reasoning role '{role}', got '{model}'"

    for role in flash_roles:
        model = MODEL_ROUTING[role]
        assert "flash" in model.lower(), f"Expected Flash model for volume role '{role}', got '{model}'"


def test_multi_agent_hierarchy_assembly() -> None:
    """Criterion #9: Verifies assembly of Coordinator, Sequential, Loop, and Parallel agents."""
    coordinator = create_bakeoff_coordinator()
    assert coordinator.name == "bakeoff_coordinator"
    assert len(coordinator.sub_agents) == 5

    # Check Sequential Dataset Pipeline
    pipeline = build_dataset_pipeline()
    assert pipeline.name == "dataset_pipeline"
    assert len(pipeline.sub_agents) == 3

    # Check Parallel BakeOff Runner
    runner = build_bakeoff_runner(["gemini-3.8-flash", "claude-sonnet-5"])
    assert runner.name == "bakeoff_runner"
    assert len(runner.sub_agents) == 2

    # Check Parallel Judge Panel
    judges = build_judge_panel()
    assert judges.name == "judge_panel"
    assert len(judges.sub_agents) == 2


def test_root_agent_entrypoint_defined() -> None:
    """Verifies that canonical root_agent object is exposed for ADK Agent Engine."""
    assert root_agent is not None
    assert root_agent.name == "bakeoff_coordinator"
