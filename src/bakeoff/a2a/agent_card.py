"""A2A Agent Card definition (Criterion #15 & Trust Boundary Architecture).

Publishes standard Agent2Agent (A2A) metadata and skill contracts served at
/.well-known/agent.json, allowing discovery and invocation across organizational boundaries.
"""

from typing import Any

BAKEOFF_RUNNER_AGENT_CARD: dict[str, Any] = {
    "$schema": "https://a2a-protocol.org/schemas/agent-card-v1.json",
    "name": "bakeoff-runner-agent",
    "version": "1.0.0",
    "description": (
        "Customer-side A2A runner executing model evaluations directly against private "
        "customer corpora within the customer's security boundary. Returns only sanitized "
        "scores, latency, and token telemetry across the boundary."
    ),
    "capabilities": {
        "streaming": True,
        "push_notifications": False,
        "distributed_tracing": "w3c_trace_context",
    },
    "skills": [
        {
            "id": "build_golden_set",
            "name": "Build Golden Dataset",
            "description": "Profiles customer corpus and synthesizes vetted evaluation cases.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "corpus_path": {"type": "string"},
                    "account_id": {"type": "string"},
                    "target_case_count": {"type": "integer", "default": 20},
                },
                "required": ["corpus_path", "account_id"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "golden_case_count": {"type": "integer"},
                    "coverage_score": {"type": "number"},
                },
            },
        },
        {
            "id": "execute_bakeoff",
            "name": "Execute Model Bake-Off",
            "description": "Runs canonical evaluation cases in parallel across candidate models.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "candidate_models": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["account_id", "candidate_models"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "cases_executed": {"type": "integer"},
                    "telemetry": {"type": "array"},
                },
            },
        },
        {
            "id": "score_results",
            "name": "Score Results & Project TCO",
            "description": "Executes dual-track evaluation and computes empirical TCO.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "run_id": {"type": "string"},
                    "stated_monthly_volume": {"type": "integer"},
                },
                "required": ["run_id", "stated_monthly_volume"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "report": {"type": "object"},
                },
            },
        },
    ],
}


def get_agent_card() -> dict[str, Any]:
    """Returns the compliant A2A Agent Card specification."""
    return BAKEOFF_RUNNER_AGENT_CARD
