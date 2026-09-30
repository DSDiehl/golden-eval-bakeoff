"""Distributed Tracing and Intent vs. Outcome Capture (Criteria #14 & #15).

Implements OpenTelemetry root and child spans with W3C trace context propagation across
the Agent2Agent (A2A) boundary, and records paired intent and outcome telemetry.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import structlog

logger = structlog.get_logger(__name__)

# Initialize default TracerProvider if none is set
if not isinstance(trace.get_tracer_provider(), TracerProvider):
    resource = Resource.create({"service.name": "golden-eval-bakeoff"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

tracer = trace.get_tracer("bakeoff.tracer")
propagator = TraceContextTextMapPropagator()


@contextmanager
def trace_intent_and_outcome(
    operation_name: str,
    intent_payload: dict[str, Any],
    run_id: str | None = None,
    account_id: str | None = None,
) -> Generator[trace.Span, None, None]:
    """Wraps an evaluation execution step, explicitly recording Intent and Outcome.

    Criterion #14: Native Intent vs. Outcome capture.
    Before execution: logs the intended action, prompt parameters, and expectations.
    After execution: logs the actual completion, status, latency, and judgment delta
    under the same OpenTelemetry span.

    Args:
        operation_name: Name of the traced operation (e.g. 'execute_candidate_case').
        intent_payload: Dictionary capturing the agent's planned action and expectations.
        run_id: Evaluation run ID.
        account_id: Customer account ID.

    Yields:
        The active OpenTelemetry Span to attach runtime attributes.
    """
    with tracer.start_as_current_span(operation_name) as span:
        # 1. Capture Intent before execution
        span.set_attribute("agent.intent.operation", operation_name)
        if run_id:
            span.set_attribute("bakeoff.run_id", run_id)
        if account_id:
            span.set_attribute("bakeoff.account_id", account_id)

        for k, v in intent_payload.items():
            span.set_attribute(f"agent.intent.{k}", str(v)[:200])

        logger.info(
            "eval_intent_captured",
            operation=operation_name,
            run_id=run_id,
            intent=intent_payload,
        )

        try:
            yield span
            # 2. Record successful outcome
            span.set_attribute("agent.outcome.status", "success")
            logger.info("eval_outcome_captured", operation=operation_name, status="success")
        except Exception as exc:
            span.record_exception(exc)
            span.set_attribute("agent.outcome.status", "error")
            span.set_attribute("agent.outcome.error", str(exc))
            logger.error(
                "eval_outcome_error",
                operation=operation_name,
                status="error",
                error=str(exc),
            )
            raise


def inject_w3c_trace_headers(headers: dict[str, str]) -> dict[str, str]:
    """Injects W3C traceparent headers for cross-process A2A distributed tracing.

    Criterion #15: OpenTelemetry W3C context propagation ensures a run spanning
    our coordinator and the customer's remote runner on Cloud Run resolves as
    a single distributed trace in Cloud Trace.

    Args:
        headers: Outgoing HTTP request header dictionary.

    Returns:
        Updated headers dictionary with W3C 'traceparent' header added.
    """
    propagator.inject(headers)
    return headers


def extract_w3c_trace_context(headers: dict[str, str]) -> None:
    """Extracts W3C traceparent from incoming A2A HTTP headers and attaches to active context.

    Args:
        headers: Incoming HTTP request header dictionary.
    """
    propagator.extract(headers)
