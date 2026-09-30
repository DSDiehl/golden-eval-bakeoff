"""Root agent assembly implementing ADK Multi-Agent Orchestration Patterns (Criterion #9).

Orchestrates four distinct ADK primitives:
1. BakeOffCoordinator (LlmAgent) - Root planner and conductor.
2. DatasetPipeline (SequentialAgent) - Strictly ordered dataset extraction and refinement.
3. CoverageRefinementLoop (LoopAgent) - Bounded refinement loop terminating on quantitative gate.
4. BakeOffRunner & JudgePanel (ParallelAgent) - Concurrent fan-out over candidate models and judges.
"""

from typing import Any
from .callbacks.guardrails import TokenBudgetGuardrail
from .callbacks.hitl import HumanApprovalGate
from .config import DEFAULT_CANDIDATES, get_model_for_role
from .prompts.loader import load_prompt
from .sub_agents.candidate_runner import create_candidate_runner_agent
from .sub_agents.case_refiner import create_case_refiner_agent
from .sub_agents.case_synthesizer import create_case_synthesizer_agent
from .sub_agents.corpus_profiler import create_corpus_profiler_agent
from .sub_agents.coverage_critic import create_coverage_critic_agent
from .sub_agents.deterministic_scorer import create_deterministic_scorer_agent
from .sub_agents.quality_judge import create_quality_judge_agent
from .sub_agents.report_composer import create_report_composer_agent
from .sub_agents.tco_analyst import create_tco_analyst_agent
from .tools.dataset_tools import promote_to_canonical_golden_set

try:
    from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
except ImportError:
    # Stub classes for local/offline environments if google-adk is being installed
    class LlmAgent:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.name = kwargs.get("name", "agent")
            self.sub_agents = kwargs.get("sub_agents", [])

    class SequentialAgent(LlmAgent):  # type: ignore
        pass

    class LoopAgent(LlmAgent):  # type: ignore
        pass

    class ParallelAgent(LlmAgent):  # type: ignore
        pass


def build_dataset_pipeline(hitl_gate: HumanApprovalGate | None = None) -> SequentialAgent:
    """Builds the SequentialAgent for capability profiling, synthesis, and refinement.

    Criterion #9 (Sequential): Dataset construction is strictly ordered.
    Includes the CoverageRefinementLoop (LoopAgent with max_iterations=4) to ensure
    the dataset is earned through quantitative verification rather than merely generated.

    Args:
        hitl_gate: Optional HumanApprovalGate callback handler.

    Returns:
        Assembled SequentialAgent instance.
    """
    profiler = create_corpus_profiler_agent()
    synthesizer = create_case_synthesizer_agent()

    # LoopAgent for bounded iterative refinement (max 4 iterations)
    critic = create_coverage_critic_agent()
    refiner = create_case_refiner_agent()
    refinement_loop = LoopAgent(
        name="coverage_refinement_loop",
        sub_agents=[critic, refiner],
        max_iterations=4,
    )

    return SequentialAgent(
        name="dataset_pipeline",
        sub_agents=[profiler, synthesizer, refinement_loop],
    )


def build_bakeoff_runner(candidate_models: list[str] | None = None) -> ParallelAgent:
    """Builds the ParallelAgent for concurrent candidate model evaluation.

    Criterion #9 (Parallel): Candidate models are mutually independent;
    fan-out maximizes throughput and minimizes execution latency.

    Args:
        candidate_models: List of model identifiers to evaluate. Defaults to DEFAULT_CANDIDATES.

    Returns:
        Assembled ParallelAgent instance.
    """
    models = candidate_models or DEFAULT_CANDIDATES
    runners = [create_candidate_runner_agent(m) for m in models]
    return ParallelAgent(
        name="bakeoff_runner",
        sub_agents=runners,
    )


def build_judge_panel() -> ParallelAgent:
    """Builds the ParallelAgent for concurrent qualitative and deterministic scoring.

    Runs QualityJudgeAgent (LM-as-Judge with anti-bias constitution) in parallel with
    DeterministicScorer (exact match, tokens, latency arithmetic).

    Returns:
        Assembled ParallelAgent instance.
    """
    quality_judge = create_quality_judge_agent()
    deterministic_scorer = create_deterministic_scorer_agent()
    return ParallelAgent(
        name="judge_panel",
        sub_agents=[quality_judge, deterministic_scorer],
    )


def create_bakeoff_coordinator(
    candidate_models: list[str] | None = None,
    hitl_gate: HumanApprovalGate | None = None,
    token_guardrail: TokenBudgetGuardrail | None = None,
) -> LlmAgent:
    """Creates the root BakeOffCoordinator orchestrating the full multi-agent hierarchy.

    Criterion #9 (Coordinator): Top-level planner managing the sequence:
    DatasetPipeline -> HumanApprovalGate -> BakeOffRunner -> JudgePanel -> TCOAnalyst -> ReportComposer.

    Args:
        candidate_models: List of candidate models under test.
        hitl_gate: Optional Human-in-the-Loop gate.
        token_guardrail: Optional Token budget enforcer.

    Returns:
        Root LlmAgent instance.
    """
    gate = hitl_gate or HumanApprovalGate()
    guard = token_guardrail or TokenBudgetGuardrail()

    dataset_pipeline = build_dataset_pipeline(hitl_gate=gate)
    bakeoff_runner = build_bakeoff_runner(candidate_models=candidate_models)
    judge_panel = build_judge_panel()
    tco_analyst = create_tco_analyst_agent()
    report_composer = create_report_composer_agent()

    return LlmAgent(
        name="bakeoff_coordinator",
        model=get_model_for_role("coordinator"),
        instruction=load_prompt("coordinator"),
        tools=[promote_to_canonical_golden_set],
        sub_agents=[
            dataset_pipeline,
            bakeoff_runner,
            judge_panel,
            tco_analyst,
            report_composer,
        ],
        before_tool_callback=gate.before_tool_callback,
        before_model_callback=guard.before_model_callback,
    )


# Canonical ADK entrypoint for Vertex AI Agent Engine and adk CLI
root_agent = create_bakeoff_coordinator()
