"""
Deterministic Checks: Math reconciliation and red flag detection.
These checks complement the LLM evaluation by catching things math can decide.
"""


def check_fundraise_to_milestone(extracted_data: dict) -> dict:
    """
    Check if the fundraise amount is reasonable for the stated target milestone.
    Returns finding dict.
    """
    fundraise = extracted_data.get("fundraise", {})
    amount = fundraise.get("amount_seeking")
    target_arr = fundraise.get("target_arr_mentioned")
    timeline = fundraise.get("target_timeline_months")

    if not amount or not target_arr or not timeline:
        return {
            "check": "fundraise_to_milestone",
            "status": "skipped",
            "reason": "Insufficient data"
        }

    # Heuristic: monthly burn should not exceed (raise / timeline * 1.5)
    # And ARR target growth should be reasonable
    monthly_runway = amount / timeline
    arr_jump_required = target_arr  # assuming starting from 0 or near-0

    # Rough check: SaaS typically needs ~1-2x of target ARR in capital to reach it
    capital_efficiency_ratio = target_arr / amount if amount > 0 else 0

    if capital_efficiency_ratio > 2.5:
        return {
            "check": "fundraise_to_milestone",
            "status": "fail",
            "reason": f"Raise of ${amount:,} appears underpowered for ${target_arr:,} ARR target. Capital efficiency required: {capital_efficiency_ratio:.1f}x (typical SaaS: 1-2x)",
            "severity": "medium"
        }

    return {
        "check": "fundraise_to_milestone",
        "status": "pass",
        "reason": f"Capital efficiency: {capital_efficiency_ratio:.1f}x is within reasonable range"
    }


def check_customer_count_revenue(extracted_data: dict) -> dict:
    """Check if claimed revenue matches customer count and pricing."""
    customers = extracted_data.get("customers", {})
    revenue = extracted_data.get("revenue", {})

    paying = customers.get("paying_count")
    arr = revenue.get("current_arr")

    if not paying or not arr:
        return {"check": "customer_revenue_match", "status": "skipped", "reason": "Insufficient data"}

    if paying > 0:
        implied_acv = arr / paying
        if implied_acv < 100 or implied_acv > 1_000_000:
            return {
                "check": "customer_revenue_match",
                "status": "flag",
                "reason": f"Implied ACV of ${implied_acv:,.0f} seems unusual for {paying} customers and ${arr:,} ARR",
                "severity": "low"
            }

    return {"check": "customer_revenue_match", "status": "pass"}


def check_team_size_vs_stage(extracted_data: dict) -> dict:
    """Check if team size matches claimed stage."""
    team_size = extracted_data.get("team_size")
    stage = extracted_data.get("stage")

    if not team_size or not stage:
        return {"check": "team_size_stage", "status": "skipped"}

    expected = {
        "Idea": (1, 3),
        "MVP": (2, 8),
        "Pilot": (3, 12),
        "Early Revenue": (5, 25),
        "Growth": (15, 100),
        "Scale": (50, 500)
    }

    if stage in expected:
        low, high = expected[stage]
        if team_size < low:
            return {
                "check": "team_size_stage",
                "status": "flag",
                "reason": f"Team of {team_size} seems small for {stage} stage (typical: {low}-{high})",
                "severity": "low"
            }
        if team_size > high:
            return {
                "check": "team_size_stage",
                "status": "flag",
                "reason": f"Team of {team_size} seems large for {stage} stage (typical: {low}-{high})",
                "severity": "low"
            }

    return {"check": "team_size_stage", "status": "pass"}


def check_red_flags(extracted_data: dict) -> list:
    """Detect known red flag patterns."""
    flags = []

    # Check for "no competition" claim
    competitors = extracted_data.get("market", {}).get("named_competitors", [])
    if not competitors or len(competitors) == 0:
        differentiation = (extracted_data.get("market", {}).get("differentiation") or "").lower()
        if any(phrase in differentiation for phrase in ["no competition", "no competitors", "first mover", "no one else"]):
            flags.append({
                "flag": "no_competition_claim",
                "severity": "high",
                "description": "Claims no competition - usually indicates poor market understanding"
            })

    # Check for missing financials when claiming revenue
    arr = extracted_data.get("revenue", {}).get("current_arr")
    if arr and arr > 100_000:
        if not extracted_data.get("revenue", {}).get("retention_data"):
            flags.append({
                "flag": "no_retention_data",
                "severity": "medium",
                "description": f"Claims ${arr:,} ARR but no retention/churn data provided"
            })

    # Check for unrealistic projections
    target_arr = extracted_data.get("fundraise", {}).get("target_arr_mentioned")
    current_arr = extracted_data.get("revenue", {}).get("current_arr") or 0
    timeline = extracted_data.get("fundraise", {}).get("target_timeline_months")

    if target_arr and timeline and current_arr is not None:
        if current_arr == 0 and target_arr > 1_000_000 and timeline <= 18:
            flags.append({
                "flag": "aggressive_projection",
                "severity": "medium",
                "description": f"Targeting ${target_arr:,} ARR in {timeline} months from zero"
            })

    # Check for unverified customer logos in case studies vs named customers
    case_studies = extracted_data.get("customers", {}).get("case_studies", [])
    named = extracted_data.get("customers", {}).get("named_customers", [])
    if case_studies and not named:
        flags.append({
            "flag": "case_studies_without_logos",
            "severity": "low",
            "description": "Case studies described but no customer logos shown"
        })

    return flags


def run_all_checks(extracted_data: dict) -> dict:
    """Run all deterministic checks. Returns findings + red flags."""
    findings = [
        check_fundraise_to_milestone(extracted_data),
        check_customer_count_revenue(extracted_data),
        check_team_size_vs_stage(extracted_data),
    ]

    red_flags = check_red_flags(extracted_data)

    return {
        "findings": findings,
        "red_flags": red_flags
    }
