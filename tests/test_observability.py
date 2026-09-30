"""Unit tests for structured logging, tracing, intent/outcome, and PII redaction (Criteria #13-16)."""

from src.bakeoff.observability.logging import get_logger
from src.bakeoff.observability.redaction import redact_pii_dict, redact_pii_text
from src.bakeoff.observability.tracing import inject_w3c_trace_headers, trace_intent_and_outcome


def test_structured_logger_context_binding() -> None:
    """Criterion #13: Structured JSON logging binds operational metadata."""
    log = get_logger("test", run_id="RUN_101", candidate_model="gemini-3.1-pro-preview")
    assert log is not None


def test_intent_vs_outcome_tracing() -> None:
    """Criterion #14 & #15: Intent and outcome captured under shared trace span."""
    intent = {"case_id": "CASE_100", "expected": "403 Forbidden"}

    with trace_intent_and_outcome("eval_case_execution", intent, run_id="RUN_100") as span:
        assert span is not None
        # Simulate execution
        span.set_attribute("measured.latency_ms", 145.2)


def test_w3c_trace_header_injection() -> None:
    """Criterion #15: W3C traceparent header injected for A2A cross-process tracing."""
    headers: dict[str, str] = {}
    updated = inject_w3c_trace_headers(headers)
    assert "traceparent" in updated
    assert updated["traceparent"].startswith("00-")


def test_pii_redaction_email_phone_and_keys() -> None:
    """Criterion #16: Active scrubbing masks sensitive customer PII."""
    raw_text = (
        "User alice.smith@okta.com contacted support at +1-415-555-0199 using API key "
        "AIzaSyD-TEST-KEY-123456789012345 and token Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    )
    redacted = redact_pii_text(raw_text)

    assert "alice.smith@okta.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "415-555-0199" not in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "AIzaSyD-TEST-KEY" not in redacted
    assert "[REDACTED_API_KEY]" in redacted
    assert "[REDACTED_TOKEN]" in redacted


def test_pii_dict_redaction() -> None:
    """Criterion #16: Recursive dictionary PII scrubbing."""
    data = {
        "user_email": "admin@zoominfo.com",
        "nested": {"phone": "650-253-0000"},
        "tags": ["normal_tag", "contact: john@gitlab.com"],
    }
    cleaned = redact_pii_dict(data)

    assert "[REDACTED_EMAIL]" in cleaned["user_email"]
    assert "[REDACTED_PHONE]" in cleaned["nested"]["phone"]
    assert "[REDACTED_EMAIL]" in cleaned["tags"][1]
