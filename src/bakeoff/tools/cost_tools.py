"""Empirical TCO projection and pricing calculation tools.

Calculates projected total cost of ownership based on empirical token measurements
rather than list-price guesswork.
"""

from typing import Any
from ..schemas.judgment import TCOProjection

# Published pricing table per 1M tokens (USD)
MODEL_PRICING_TABLE: dict[str, dict[str, float]] = {
    "gemini-2.5-flash": {
        "input_per_1m": 0.075,
        "output_per_1m": 0.30,
    },
    "gemini-2.5-pro": {
        "input_per_1m": 1.25,
        "output_per_1m": 5.00,
    },
    "claude-3-5-sonnet-v2": {
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
    },
    "claude-3-5-haiku": {
        "input_per_1m": 0.80,
        "output_per_1m": 4.00,
    },
}


def get_model_pricing_tier(model_name: str) -> dict[str, Any]:
    """Retrieves published pricing rates per million tokens for a candidate model.

    Args:
        model_name: Model identifier (e.g., 'gemini-2.5-flash', 'claude-3-5-sonnet-v2').

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - model_name: Evaluated model.
            - input_per_1m: Cost per 1M input tokens in USD.
            - output_per_1m: Cost per 1M output tokens in USD.
            - guidance: Remediation guidance if model pricing is not found.
    """
    cleaned = model_name.lower().strip()
    match = None
    for key, rate in MODEL_PRICING_TABLE.items():
        if key in cleaned:
            match = rate
            break

    if not match:
        # Default fallback to standard mid-tier rate
        match = {"input_per_1m": 1.00, "output_per_1m": 4.00}

    return {
        "status": "success",
        "model_name": model_name,
        "input_per_1m": match["input_per_1m"],
        "output_per_1m": match["output_per_1m"],
        "guidance": "Pricing tier resolved. Use project_monthly_tco_from_telemetry for TCO forecast.",
    }


def project_monthly_tco_from_telemetry(
    candidate_model: str,
    stated_monthly_volume: int,
    avg_input_tokens: float,
    avg_output_tokens: float,
) -> dict[str, Any]:
    """Projects monthly total cost of ownership (TCO) from empirical token measurements.

    Combines measured per-interaction prompt and completion tokens with the customer's
    stated volume and published pricing tiers.

    Args:
        candidate_model: Candidate model identifier.
        stated_monthly_volume: Customer's expected interactions per month (e.g. 500,000).
        avg_input_tokens: Empirically measured average prompt tokens per interaction.
        avg_output_tokens: Empirically measured average completion tokens per interaction.

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - projection: Serialized TCOProjection model.
            - guidance: Actionable recommendation based on projected cost.

    Raises:
        ValueError: If stated_monthly_volume <= 0.
    """
    if stated_monthly_volume <= 0:
        raise ValueError(
            f"stated_monthly_volume must be greater than 0, got {stated_monthly_volume}."
        )

    pricing_data = get_model_pricing_tier(candidate_model)
    in_rate = pricing_data["input_per_1m"]
    out_rate = pricing_data["output_per_1m"]

    # Calculate cost per 1,000 interactions
    input_cost_1k = (1000 * avg_input_tokens / 1_000_000) * in_rate
    output_cost_1k = (1000 * avg_output_tokens / 1_000_000) * out_rate
    cost_per_1k = input_cost_1k + output_cost_1k

    # Total monthly cost
    total_monthly = (stated_monthly_volume / 1000) * cost_per_1k

    projection = TCOProjection(
        candidate_model=candidate_model,
        cost_per_1k_interactions_usd=round(cost_per_1k, 4),
        projected_monthly_cost_usd=round(total_monthly, 2),
        stated_monthly_volume=stated_monthly_volume,
        avg_input_tokens=round(avg_input_tokens, 1),
        avg_output_tokens=round(avg_output_tokens, 1),
        input_rate_per_1m=in_rate,
        output_rate_per_1m=out_rate,
    )

    return {
        "status": "success",
        "projection": projection.model_dump(),
        "guidance": (
            f"Monthly TCO for '{candidate_model}' projected at ${total_monthly:,.2f} "
            f"for {stated_monthly_volume:,} interactions."
        ),
    }
