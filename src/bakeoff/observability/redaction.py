"""PII Redaction pipeline for customer corpus and log scrubbing (Criterion #16).

Implements sensitive data inspection and de-identification using Google Cloud Data
Loss Prevention (Cloud DLP) with a resilient rule-based engine fallback for hermetic testing.
"""

import os
import re
from typing import Any
import structlog

logger = structlog.get_logger(__name__)

# Patterns for sensitive entity matching (emails, phone numbers, API keys, bearer tokens)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?1[-. ]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b")
API_KEY_PATTERN = re.compile(r"\b(?:AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36})\b")
BEARER_TOKEN_PATTERN = re.compile(r"\bBearer\s+[a-zA-Z0-9_\-\.]{20,}\b", re.IGNORECASE)


def redact_pii_text(text: str, project_id: str | None = None) -> str:
    """Scans and de-identifies PII/credentials from text before logging, storage, or egress.

    Criterion #16: Active scrubbing mechanism ensuring customer evaluation data,
    transcripts, and credentials never leak across trust boundaries or into logs.

    Args:
        text: Raw text string to redact.
        project_id: Optional GCP Project ID to use Cloud DLP API if configured.

    Returns:
        De-identified string with sensitive tokens replaced by typed redaction placeholders.
    """
    if not text:
        return text

    # 1. Attempt Cloud DLP if running with active project credentials
    project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if project:
        try:
            from google.cloud import dlp_v2  # type: ignore

            client = dlp_v2.DlpServiceClient()
            parent = f"projects/{project}/locations/global"
            item = {"value": text}
            deidentify_config = {
                "info_type_transformations": {
                    "transformations": [
                        {
                            "primitive_transformation": {
                                "replace_with_info_type_config": {}
                            }
                        }
                    ]
                }
            }
            inspect_config = {
                "info_types": [
                    {"name": "EMAIL_ADDRESS"},
                    {"name": "PHONE_NUMBER"},
                    {"name": "AUTH_TOKEN"},
                    {"name": "API_KEY"},
                ]
            }
            response = client.deidentify_content(
                request={
                    "parent": parent,
                    "deidentify_config": deidentify_config,
                    "inspect_config": inspect_config,
                    "item": item,
                }
            )
            return response.item.value
        except Exception:
            # Fall back smoothly to high-performance regex engine if Cloud DLP unavailable
            pass

    # 2. Deterministic rule-based sanitizer fallback
    sanitized = text
    sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
    sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    sanitized = API_KEY_PATTERN.sub("[REDACTED_API_KEY]", sanitized)
    sanitized = BEARER_TOKEN_PATTERN.sub("Bearer [REDACTED_TOKEN]", sanitized)

    return sanitized


def redact_pii_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively redacts PII strings within a nested dictionary structure.

    Args:
        data: Arbitrary dictionary to sanitize.

    Returns:
        Sanitized copy of the dictionary with PII masked.
    """
    clean_dict: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            clean_dict[key] = redact_pii_text(value)
        elif isinstance(value, dict):
            clean_dict[key] = redact_pii_dict(value)
        elif isinstance(value, list):
            clean_dict[key] = [
                redact_pii_dict(v) if isinstance(v, dict)
                else (redact_pii_text(v) if isinstance(v, str) else v)
                for v in value
            ]
        else:
            clean_dict[key] = value
    return clean_dict
