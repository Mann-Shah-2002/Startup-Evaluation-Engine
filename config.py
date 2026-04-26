"""
Configuration for Future Unicorn Evaluator.
All weights, thresholds, and constants live here.
DO NOT modify the rubric values without explicit client approval.
"""

# ============================================================
# RUBRIC CONFIGURATION (LOCKED - DO NOT MODIFY)
# ============================================================

CATEGORIES = {
    "founder_stage_translation": {
        "display_name": "Founder–Stage Translation",
        "weight": 20,
        "core_question": "Can this team execute what they're attempting at this stage?"
    },
    "internal_consistency": {
        "display_name": "Internal Consistency",
        "weight": 20,
        "core_question": "Does the business make sense internally?",
        "kill_filter": True
    },
    "claim_testability": {
        "display_name": "Claim Testability",
        "weight": 20,
        "core_question": "Is this real or just a story?",
        "kill_filter": True
    },
    "sector_coherence": {
        "display_name": "Sector Coherence",
        "weight": 15,
        "core_question": "Do they understand how their market actually works?"
    },
    "stage_coherence": {
        "display_name": "Stage Coherence",
        "weight": 15,
        "core_question": "Is their actual state aligned with claimed stage?"
    },
    "problem_market_fit": {
        "display_name": "Problem × Market Fit",
        "weight": 10,
        "core_question": "Is the problem real and is there demonstrated pull?"
    }
}

# Score normalization
SCORE_NORMALIZATION = {0: 0, 1: 50, 2: 100}

# Tier thresholds
TIER_THRESHOLDS = [
    {"min": 75, "max": 100, "tier": "High Priority", "color": "#639922"},
    {"min": 60, "max": 74,  "tier": "Consider",      "color": "#BA7517"},
    {"min": 40, "max": 59,  "tier": "Watchlist",     "color": "#D85A30"},
    {"min": 0,  "max": 39,  "tier": "Reject",        "color": "#A32D2D"},
]

# Score color (for category bars)
SCORE_COLOR = {
    0: "#A32D2D",  # red
    1: "#BA7517",  # amber
    2: "#639922",  # green
}

# ============================================================
# LLM CONFIGURATION
# ============================================================

LLM_MODEL = "claude-haiku-4-5"
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS = 1024
LLM_VOTES_PER_CATEGORY = 3  # Majority voting

# ============================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================

SHEET_HEADER = [
    "Timestamp", "Startup Name", "Sector", "Stage", "Final Score", "Tier",
    "Kill Filter", "Confidence", "Founder", "Consistency", "Testability",
    "Sector Score", "Stage Score", "Problem-Fit", "Red Flags", "Evaluator", "Notes"
]

# ============================================================
# DEPLOYMENT CONFIGURATION
# ============================================================

APP_TITLE = "Growth91 Evaluation Engine"
APP_SUBTITLE = "Growth91 Internal Curation Tool"


def compute_tier(final_score: float, kill_filter_triggered: bool) -> dict:
    """Determine tier from score, with kill filter override."""
    if kill_filter_triggered:
        return {"tier": "Reject", "color": "#A32D2D", "kill_filter_override": True}

    for threshold in TIER_THRESHOLDS:
        if threshold["min"] <= final_score <= threshold["max"]:
            return {
                "tier": threshold["tier"],
                "color": threshold["color"],
                "kill_filter_override": False
            }

    return {"tier": "Reject", "color": "#A32D2D", "kill_filter_override": False}
