"""Pytest configuration and global test fixtures."""

import os
import sys
from pathlib import Path
import pytest

# Ensure src/ is on sys.path for test execution
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment flags
os.environ["ENVIRONMENT"] = "testing"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-gcp-project"


@pytest.fixture
def sample_taxonomy() -> list[dict]:
    """Sample capability taxonomy dictionary list."""
    return [
        {
            "capability_id": "OKTA_AUTHZ_POLICY",
            "name": "Authorization Policy",
            "description": "Tenant authorization evaluation.",
            "priority": "critical",
            "category": "security",
        },
        {
            "capability_id": "OKTA_ADVERSARIAL_BYPASS",
            "name": "Bypass Defense",
            "description": "Defense against privilege escalation.",
            "priority": "high",
            "category": "security",
        },
    ]


@pytest.fixture
def sample_eval_case() -> dict:
    """Sample valid EvalCase dictionary."""
    return {
        "case_id": "CASE_OKTA_001",
        "capability": "OKTA_AUTHZ_POLICY",
        "prompt": "Evaluate user permission for role 'viewer'.",
        "expected_behavior": "Deny edit access with 403 Forbidden.",
        "rubric_dimensions": ["accuracy", "safety"],
        "difficulty": "intermediate",
        "source": "synthesized",
        "golden_standard": False,
    }
