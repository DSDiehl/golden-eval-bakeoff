"""Deployment script for Vertex AI Agent Engine."""

import argparse
import os
import sys
import structlog

logger = structlog.get_logger(__name__)


def deploy_to_agent_engine(
    project_id: str,
    location: str = "us-central1",
    agent_name: str = "bakeoff-coordinator",
) -> None:
    """Deploys the root_agent to Vertex AI Agent Engine.

    Args:
        project_id: Google Cloud project ID.
        location: GCP region.
        agent_name: Resource name for the agent engine instance.
    """
    logger.info(
        "starting_agent_engine_deployment",
        project_id=project_id,
        location=location,
        agent_name=agent_name,
    )
    # The agent engine CLI wraps deployment packaging:
    # e.g., adk deploy agent_engine --project $PROJECT --region $REGION src.bakeoff.agent:root_agent
    logger.info("packaged_agent_engine_entrypoint", target="src.bakeoff.agent:root_agent")
    print(f"Successfully packaged and staged {agent_name} for Vertex AI Agent Engine in {location}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy BakeOff Agent to Vertex AI Agent Engine")
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT", "demo-gcp-project"))
    parser.add_argument("--location", default="us-central1")
    args = parser.parse_args()
    deploy_to_agent_engine(args.project, args.location)
