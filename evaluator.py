"""
Main Evaluator: Orchestrates the full evaluation pipeline.
Takes a PDF and returns a complete evaluation result.
"""

import uuid
from datetime import datetime
from extractor import extract_from_pdf
from deterministic_checks import run_all_checks
from llm_evaluator import evaluate_all_categories
from aggregator import aggregate_scores


def evaluate_startup(
    pdf_bytes: bytes,
    api_key: str,
    metadata: dict = None
) -> dict:
    """
    Run full evaluation pipeline on a startup pitch deck.

    Args:
        pdf_bytes: Raw PDF file bytes
        api_key: Anthropic API key
        metadata: Optional dict with 'sector', 'stage', 'geography' overrides

    Returns:
        Complete evaluation result dict per output schema
    """
    metadata = metadata or {}
    evaluation_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()

    # Step 1: Extract structured data from PDF
    extracted = extract_from_pdf(pdf_bytes, api_key)

    # Apply metadata overrides
    if metadata.get("sector"):
        extracted["sector"] = metadata["sector"]
    if metadata.get("stage"):
        extracted["stage"] = metadata["stage"]
    if metadata.get("geography"):
        extracted["geography"] = [metadata["geography"]] if isinstance(metadata["geography"], str) else metadata["geography"]

    # Step 2: Run deterministic checks
    deterministic = run_all_checks(extracted)

    # Step 3: Run LLM evaluation across all 6 categories
    category_results = evaluate_all_categories(extracted, api_key)

    # Step 4: Aggregate into final score and tier
    aggregated = aggregate_scores(category_results)

    # Step 5: Generate gap list and feedback
    gap_list = generate_gap_list(aggregated)
    feedback_draft = generate_feedback_draft(extracted, aggregated)

    # Compose final result
    result = {
        "evaluation_id": evaluation_id,
        "evaluated_at": started_at,
        "startup_name": extracted.get("startup_name") or "Unknown",
        "sector": extracted.get("sector"),
        "stage": extracted.get("stage"),
        "final_score": aggregated["final_score"],
        "tier": aggregated["tier"],
        "tier_color": aggregated["tier_color"],
        "kill_filter_triggered": aggregated["kill_filter_triggered"],
        "kill_filter_reason": aggregated["kill_filter_reason"],
        "kill_filter_override": aggregated["kill_filter_override"],
        "confidence": aggregated["confidence"],
        "categories": aggregated["categories"],
        "extracted_data": extracted,
        "deterministic_findings": deterministic["findings"],
        "red_flags": deterministic["red_flags"],
        "gap_list": gap_list,
        "founder_feedback_draft": feedback_draft
    }

    return result


def generate_gap_list(aggregated: dict) -> list:
    """Identify what would move scores up. Useful for Watchlist/Consider tier."""
    gaps = []
    for cat_key, cat_data in aggregated["categories"].items():
        if cat_data["score"] < 2:
            target = "1 → 2" if cat_data["score"] == 1 else "0 → 1+"
            gaps.append({
                "category": cat_data["display_name"],
                "current_score": cat_data["score"],
                "target": target,
                "weight": cat_data["weight"],
                "potential_uplift": cat_data["weight"] * (50 if cat_data["score"] == 1 else 100) / 100
            })
    # Sort by potential uplift
    gaps.sort(key=lambda x: x["potential_uplift"], reverse=True)
    return gaps


def generate_feedback_draft(extracted: dict, aggregated: dict) -> str:
    """Generate a draft feedback message for the founder."""
    name = extracted.get("startup_name") or "the team"
    tier = aggregated["tier"]

    if tier == "High Priority":
        return (f"Hi {name} team,\n\nThank you for sharing your deck. Your evaluation has been "
                f"prioritized for fast-track review. We'll be in touch within 5 business days "
                f"to discuss next steps.\n\nBest,\nGrowth91 Team")

    if tier == "Consider":
        return (f"Hi {name} team,\n\nThank you for sharing your deck with Growth91. Your startup "
                f"has been queued for standard diligence. We'll review and get back to you within "
                f"10 business days.\n\nBest,\nGrowth91 Team")

    if tier == "Watchlist":
        gaps = aggregated.get("categories", {})
        weak_cats = [c["display_name"] for c in gaps.values() if c["score"] < 2]
        return (f"Hi {name} team,\n\nThank you for sharing your deck with Growth91. After careful "
                f"review, we're not able to move forward with listing at this time. "
                f"Areas where strengthening evidence would help: {', '.join(weak_cats[:3])}. "
                f"We're happy to re-review once you have updated traction or documentation - "
                f"feel free to reach out in 90 days.\n\nBest,\nGrowth91 Team")

    # Reject
    return (f"Hi {name} team,\n\nThank you for sharing your deck with Growth91. After review, "
            f"we don't think your startup is the right fit for our platform at this stage. "
            f"We wish you the best with your venture.\n\nBest,\nGrowth91 Team")
