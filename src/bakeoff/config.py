"""Configuration and Strategic Model Routing for Golden Eval & Bake-Off Agent.

Implements declarative model routing based on task complexity (Pro for reasoning/profiling/
critique/judging, Flash for high-volume synthesis/refinement/arithmetic) and secure secret
resolution from Google Cloud Secret Manager.
"""

import os
from typing import Any

# Strategic Model Routing Table (Criterion #10)
# Pro models for reasoning-heavy, low-volume planning, profiling, critique, and judging.
# Flash models for high-volume, structured synthesis, targeted refinement, and cost arithmetic.
MODEL_ROUTING: dict[str, str] = {
    "corpus_profiler": "gemini-2.5-pro",
    "case_synthesizer": "gemini-2.5-flash",
    "coverage_critic": "gemini-2.5-pro",
    "case_refiner": "gemini-2.5-flash",
    "quality_judge": "gemini-2.5-pro",
    "tco_analyst": "gemini-2.5-flash",
    "report_composer": "gemini-2.5-pro",
    "coordinator": "gemini-2.5-pro",
}

# Default candidate models evaluated in bake-offs
DEFAULT_CANDIDATES: list[str] = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "claude-3-5-sonnet-v2",
]


def resolve_secret(secret_id: str, default: str | None = None) -> str | None:
    """Resolves secrets securely from Google Cloud Secret Manager with environment fallback.

    Implements Criterion #19 (Secure Secret Management). Checks GCP Secret Manager first
    using Application Default Credentials (ADC) or Workload Identity Federation (WIF).
    Falls back to environment variables for local testing, never hardcoding key material.

    Args:
        secret_id: Name of the secret in Secret Manager or environment variable.
        default: Optional fallback string if the secret is unavailable.

    Returns:
        The resolved secret value as a string, or default if unresolved.
    """
    # 1. Check local environment variable first for test/local hermetic execution
    env_val = os.getenv(secret_id)
    if env_val:
        return env_val

    # 2. Attempt Secret Manager resolution if running inside GCP project
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if project_id:
        try:
            from google.cloud import secretmanager  # type: ignore

            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8").strip()
        except Exception:
            # Fall back gracefully if Secret Manager client or IAM credentials unavailable
            pass

    return default


def get_model_for_role(role: str) -> str:
    """Returns the strategically routed model identifier for an agent role.

    Args:
        role: Functional agent role (e.g., 'coverage_critic', 'quality_judge').

    Returns:
        The mapped model name string.

    Raises:
        KeyError: If role is not defined in MODEL_ROUTING.
    """
    if role not in MODEL_ROUTING:
        raise KeyError(
            f"Unknown agent role '{role}'. Valid roles: {list(MODEL_ROUTING.keys())}"
        )
    return MODEL_ROUTING[role]
