"""A2A Server application deployed to Cloud Run inside the customer project."""

import json
from typing import Any
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from src.bakeoff.a2a.agent_card import get_agent_card
from src.bakeoff.observability.logging import configure_structured_logging, get_logger
from src.bakeoff.observability.redaction import redact_pii_dict
from src.bakeoff.observability.tracing import extract_w3c_trace_context, tracer
from src.bakeoff.tools.model_invoke_tools import execute_case_against_candidate_model

configure_structured_logging()
logger = get_logger("a2a_server")


async def well_known_agent_card(request: Request) -> JSONResponse:
    """Serves the standard A2A Agent Card for agent discovery."""
    return JSONResponse(get_agent_card())


async def execute_bakeoff_handler(request: Request) -> JSONResponse:
    """Executes evaluation cases locally within customer project boundary.

    Sanitizes all return data before returning across the A2A network interface.
    """
    extract_w3c_trace_context(dict(request.headers))

    with tracer.start_as_current_span("a2a_execute_bakeoff") as span:
        try:
            body = await request.json()
        except Exception:
            body = {}

        account_id = body.get("account_id", "unknown")
        candidate_models = body.get("candidate_models", ["gemini-3.8-flash"])
        span.set_attribute("bakeoff.account_id", account_id)

        logger.info("a2a_bakeoff_request_received", account_id=account_id, models=candidate_models)

        # Run simulated evaluation on customer-side corpus
        telemetry = []
        for model in candidate_models:
            res = execute_case_against_candidate_model(
                case_id="CASE_A2A_CUSTOMER_001",
                prompt=f"Execute customer-private policy validation for {account_id}.",
                candidate_model=model,
                mock_mode=True,
            )
            telemetry.append(res)

        result_payload = {
            "status": "success",
            "account_id": account_id,
            "cases_executed": len(telemetry),
            "telemetry": telemetry,
        }

        # Enforce Cloud DLP / Regex PII scrubbing before response egresses
        safe_payload = redact_pii_dict(result_payload)
        return JSONResponse(safe_payload)


async def health_check(request: Request) -> JSONResponse:
    """Liveness probe for Cloud Run."""
    return JSONResponse({"status": "healthy", "service": "bakeoff-runner-a2a"})


routes = [
    Route("/.well-known/agent.json", well_known_agent_card, methods=["GET"]),
    Route("/a2a/execute_bakeoff", execute_bakeoff_handler, methods=["POST"]),
    Route("/health", health_check, methods=["GET"]),
    Route("/", well_known_agent_card, methods=["GET"]),
]

app = Starlette(debug=False, routes=routes)
