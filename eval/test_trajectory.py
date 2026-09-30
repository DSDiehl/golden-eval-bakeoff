"""Automated Evaluation Suite: Refinement Loop Trajectory Convergence (Criterion #17).

Asserts that the CoverageRefinementLoop converges and passes the quantitative gate
within <= 4 iterations, proving the dataset is earned through bounded refinement.
"""

from src.bakeoff.schemas.coverage import CoverageVerdict
from src.bakeoff.tools.dataset_tools import (
    evaluate_coverage_against_taxonomy,
    synthesize_eval_cases_for_capability,
)


def test_coverage_refinement_loop_convergence() -> None:
    """Verifies that the coverage refinement loop converges in 4 or fewer iterations."""
    taxonomy = [
        {"capability_id": "CAP_AUTHZ_POLICY", "name": "Authorization Policy"},
        {"capability_id": "CAP_TOKEN_LIFECYCLE", "name": "Token Lifecycle"},
        {"capability_id": "CAP_ADVERSARIAL_BYPASS", "name": "Adversarial Defense"},
    ]

    current_cases: list[dict] = []
    iteration = 1
    max_iterations = 4
    gate_passed = False

    while iteration <= max_iterations:
        # Evaluate current coverage
        res = evaluate_coverage_against_taxonomy(
            cases=current_cases,
            taxonomy=taxonomy,
            threshold=0.85,
        )
        verdict = CoverageVerdict.model_validate(res["verdict"])

        if verdict.passes_gate:
            gate_passed = True
            break

        # Simulate CaseRefiner filling identified gaps
        for gap in verdict.gaps[:2]:
            synth_res = synthesize_eval_cases_for_capability(
                capability_id=gap.capability_id,
                capability_name=gap.capability_name,
                target_count=2,
                difficulty=gap.required_difficulty,
            )
            current_cases.extend(synth_res["cases"])

        iteration += 1

    assert gate_passed is True, (
        f"Loop failed to achieve coverage gate within {max_iterations} iterations. "
        f"Final coverage: {verdict.coverage_score:.2f}, Gaps remaining: {len(verdict.gaps)}"
    )
    assert iteration <= max_iterations, (
        f"Loop exceeded max_iterations threshold ({iteration} > {max_iterations})"
    )
    assert len(current_cases) >= 3, "Golden set must contain at least 3 validated cases."
