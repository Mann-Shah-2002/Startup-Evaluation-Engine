"""
LLM Evaluator: Calls Anthropic Claude API to score each rubric category.
Uses majority voting (3 calls per category) for reliability.
"""

import json
import re
from pathlib import Path
from anthropic import Anthropic
from config import CATEGORIES, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_VOTES_PER_CATEGORY

PROMPT_DIR = Path(__file__).parent / "prompts"


def load_prompt(category_key: str) -> str:
    """Load the prompt template for a given category."""
    prompt_file = PROMPT_DIR / f"{category_key}.txt"
    return prompt_file.read_text()


def extract_score_from_response(response_text: str) -> tuple:
    """
    Parse the LLM's response to extract score and rationale.
    Expected format: JSON object with 'score' (0/1/2) and 'rationale' (string).
    """
    try:
        # Find JSON in response
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            score = int(data.get("score", -1))
            rationale = data.get("rationale", "")
            if score in [0, 1, 2]:
                return (score, rationale)
    except (json.JSONDecodeError, ValueError, AttributeError):
        pass

    # Fallback: regex score extraction
    score_match = re.search(r'"?score"?\s*:?\s*([012])', response_text)
    if score_match:
        return (int(score_match.group(1)), response_text[:500])

    return (None, response_text[:500])


def score_category_once(client: Anthropic, category_key: str, extracted_data: dict) -> tuple:
    """Run one LLM call to score one category. Returns (score, rationale)."""
    prompt = load_prompt(category_key)

    user_message = f"""Here is the extracted data from the startup's pitch deck:

{json.dumps(extracted_data, indent=2)}

Apply the rubric above and return a JSON object with:
- "score": 0, 1, or 2
- "rationale": 2-3 sentence justification citing specific evidence from the data

Return ONLY the JSON object, no other text."""

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        system=prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    response_text = response.content[0].text
    return extract_score_from_response(response_text)


def evaluate_all_categories(extracted_data: dict, api_key: str) -> dict:
    """
    Score all 6 categories using LLM with majority voting.

    Returns: {
        "founder_stage_translation": {"votes": [1, 1, 2], "rationale": "..."},
        ...
    }
    """
    client = Anthropic(api_key=api_key)
    results = {}

    for category_key in CATEGORIES.keys():
        votes = []
        rationales = []

        for _ in range(LLM_VOTES_PER_CATEGORY):
            try:
                score, rationale = score_category_once(client, category_key, extracted_data)
                if score is not None:
                    votes.append(score)
                    rationales.append(rationale)
            except Exception as e:
                rationales.append(f"Error: {str(e)}")

        # Use the rationale from the most common vote
        from collections import Counter
        if votes:
            most_common_score = Counter(votes).most_common(1)[0][0]
            for v, r in zip(votes, rationales):
                if v == most_common_score:
                    final_rationale = r
                    break
            else:
                final_rationale = rationales[0] if rationales else ""
        else:
            final_rationale = "Failed to score - all attempts failed"

        results[category_key] = {
            "votes": votes,
            "rationale": final_rationale
        }

    return results
