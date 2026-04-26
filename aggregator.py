"""
Aggregator: computes final score, applies kill filter, assigns tier.
This is the deterministic final step after LLM evaluation.
"""

from collections import Counter
from config import CATEGORIES, SCORE_NORMALIZATION, compute_tier


def majority_vote(votes: list) -> tuple:
    """
    Take majority vote from a list of scores (0/1/2).
    Returns (winning_score, confidence_level).
    Confidence: 'high' if all 3 agree, 'medium' if 2/3 agree, 'low' if all differ.
    """
    if not votes:
        return (0, "low")

    counter = Counter(votes)
    most_common = counter.most_common(1)[0]
    winning_score = most_common[0]
    winning_count = most_common[1]

    if winning_count == len(votes):
        confidence = "high"
    elif winning_count > len(votes) / 2:
        confidence = "medium"
    else:
        confidence = "low"

    return (winning_score, confidence)


def aggregate_scores(category_results: dict) -> dict:
    """
    Aggregate per-category votes into final score and tier.

    Input: {
        "founder_stage_translation": {"votes": [1, 1, 2], "rationale": "..."},
        "internal_consistency": {"votes": [1, 1, 1], "rationale": "..."},
        ...
    }

    Output: full evaluation result dict per the output schema.
    """
    result = {
        "final_score": 0.0,
        "categories": {},
        "kill_filter_triggered": False,
        "kill_filter_reason": None,
        "confidence": "high"
    }

    confidence_levels = []

    for cat_key, cat_config in CATEGORIES.items():
        votes = category_results.get(cat_key, {}).get("votes", [])
        rationale = category_results.get(cat_key, {}).get("rationale", "")

        score, confidence = majority_vote(votes)
        confidence_levels.append(confidence)

        normalized = SCORE_NORMALIZATION[score]
        contribution = cat_config["weight"] * (normalized / 100)

        result["categories"][cat_key] = {
            "display_name": cat_config["display_name"],
            "score": score,
            "normalized": normalized,
            "weight": cat_config["weight"],
            "contribution": contribution,
            "rationale": rationale,
            "votes": votes,
            "confidence": confidence
        }

        result["final_score"] += contribution

        # Kill filter check
        if cat_config.get("kill_filter") and score == 0:
            result["kill_filter_triggered"] = True
            if result["kill_filter_reason"] is None:
                result["kill_filter_reason"] = f"{cat_config['display_name']} = 0"
            else:
                result["kill_filter_reason"] += f", {cat_config['display_name']} = 0"

    # Round final score
    result["final_score"] = round(result["final_score"], 1)

    # Overall confidence: lowest of any category
    if "low" in confidence_levels:
        result["confidence"] = "low"
    elif "medium" in confidence_levels:
        result["confidence"] = "medium"
    else:
        result["confidence"] = "high"

    # Tier assignment
    tier_info = compute_tier(result["final_score"], result["kill_filter_triggered"])
    result["tier"] = tier_info["tier"]
    result["tier_color"] = tier_info["color"]
    result["kill_filter_override"] = tier_info["kill_filter_override"]

    return result
