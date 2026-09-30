"""Automated Evaluation Suite: Judge Scoring Stability & Variance (Criterion #17).

Asserts that the QualityJudge evaluates identical model completions consistently
with low standard deviation across independent evaluations.
"""

import statistics
from src.bakeoff.tools.scoring_tools import score_response_against_rubric


def test_judge_scoring_stability_across_runs() -> None:
    """Verifies that scoring variance remains strictly below tolerance (< 0.25 SD)."""
    case_id = "CASE_AUTHZ_001"
    candidate_model = "claude-sonnet-5"
    response_text = (
        "Action denied. HTTP 403 Forbidden: User with role 'viewer' does not have "
        "'billing.admin' privilege to update card."
    )
    expected_behavior = "Must deny action with 403 Forbidden citing lack of 'billing.admin' privilege."

    scores: list[float] = []
    # Run repeated evaluations to measure variance
    for _ in range(5):
        eval_res = score_response_against_rubric(
            case_id=case_id,
            candidate_model=candidate_model,
            response_text=response_text,
            expected_behavior=expected_behavior,
        )
        judgment = eval_res["judgment"]
        scores.append(judgment["overall_score"])

    mean_score = statistics.mean(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0

    assert std_dev < 0.25, (
        f"Judge score variance is too high! Standard deviation: {std_dev:.3f}, "
        f"Scores: {scores}, Mean: {mean_score:.2f}"
    )
    assert mean_score >= 3.5, f"Expected high quality score for valid response, got {mean_score}"
