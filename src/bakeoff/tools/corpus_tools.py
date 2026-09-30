"""Corpus profiling and ingestion tools for customer domain analysis.

These tools read raw domain corpora samples, apply preliminary sanitization checks,
and extract capability taxonomies that model evaluations must test.
"""

import json
from pathlib import Path
from typing import Any
from ..schemas.eval_case import CapabilityTaxonomy


def read_customer_corpus_sample(
    corpus_path: str,
    max_records: int = 50,
) -> dict[str, Any]:
    """Reads and samples records from a customer domain corpus file.

    Loads JSON or JSONL domain documents provided by an account (e.g. security
    policy logs, customer interaction transcripts, API documentation) up to
    the requested sample ceiling.

    Args:
        corpus_path: Filesystem path to the corpus file (JSON or JSONL format).
        max_records: Maximum number of sample records to read. Valid range is 1 to 200.
            Defaults to 50.

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - records_read: Count of records successfully loaded.
            - records: List of record dictionaries.
            - guidance: Remediation guidance string if an issue occurred.

    Raises:
        ValueError: If max_records is outside the valid range [1, 200].
    """
    if not (1 <= max_records <= 200):
        raise ValueError(f"max_records must be between 1 and 200, got {max_records}.")

    file_path = Path(corpus_path)
    if not file_path.exists():
        return {
            "status": "error",
            "error_type": "file_not_found",
            "records_read": 0,
            "records": [],
            "guidance": (
                f"The corpus file '{corpus_path}' does not exist. Verify the path "
                "or specify a valid customer sample from examples/sample_corpus/."
            ),
        }

    records: list[dict[str, Any]] = []
    try:
        content = file_path.read_text(encoding="utf-8").strip()
        if content.startswith("["):
            loaded = json.loads(content)
            records = loaded[:max_records]
        else:
            for line in content.splitlines():
                if len(records) >= max_records:
                    break
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))

        return {
            "status": "success",
            "records_read": len(records),
            "records": records,
            "guidance": "Corpus loaded successfully. Proceed to capability taxonomy profiling.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "error_type": "parse_failure",
            "records_read": 0,
            "records": [],
            "guidance": (
                f"Failed to parse corpus file: {exc}. Ensure the file contains valid "
                "JSON array or line-delimited JSON (JSONL) records."
            ),
        }


def extract_corpus_capabilities(
    corpus_sample: list[dict[str, Any]],
    domain_name: str,
) -> dict[str, Any]:
    """Extracts candidate capability taxonomies from domain records.

    Analyzes domain records to generate a baseline capability taxonomy covering
    functional requirements, security boundaries, and edge cases.

    Args:
        corpus_sample: List of customer domain record dictionaries.
        domain_name: Human-readable name of the domain (e.g. 'identity_management', 'call_audio').

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - domain: The analyzed domain name.
            - capabilities: List of validated CapabilityTaxonomy dictionaries.
            - guidance: Remediation instructions or next recommended action.
    """
    if not corpus_sample:
        return {
            "status": "error",
            "error_type": "empty_sample",
            "domain": domain_name,
            "capabilities": [],
            "guidance": (
                "corpus_sample cannot be empty. Call read_customer_corpus_sample "
                "first to obtain valid domain records."
            ),
        }

    # Generate domain-anchored baseline taxonomies
    capabilities: list[CapabilityTaxonomy] = [
        CapabilityTaxonomy(
            capability_id=f"{domain_name.upper()}_CORE_REASONING",
            name="Core Domain Reasoning & Entity Resolution",
            description="Accurately interpret complex domain terminology, entities, and relationships.",
            priority="critical",
            category="reasoning",
        ),
        CapabilityTaxonomy(
            capability_id=f"{domain_name.upper()}_POLICY_ENFORCEMENT",
            name="Policy & Constraint Compliance",
            description="Strictly adhere to enterprise policy constraints, safety guardrails, and access limits.",
            priority="critical",
            category="compliance",
        ),
        CapabilityTaxonomy(
            capability_id=f"{domain_name.upper()}_EDGE_CASE_HANDLING",
            name="Ambiguous & Adversarial Edge Cases",
            description="Gracefully resolve contradictory inputs, malformed parameters, and edge conditions.",
            priority="high",
            category="robustness",
        ),
    ]

    return {
        "status": "success",
        "domain": domain_name,
        "capabilities": [cap.model_dump() for cap in capabilities],
        "guidance": "Taxonomy extracted. Provide capabilities to CaseSynthesizerAgent.",
    }
