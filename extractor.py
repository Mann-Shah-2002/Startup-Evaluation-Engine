"""
Extractor: Convert pitch deck PDF into structured JSON for evaluation.
Uses Claude's document understanding via the messages API.
"""

import base64
import json
import re
from pathlib import Path
from anthropic import Anthropic
from config import LLM_MODEL


EXTRACTION_PROMPT = """You are a careful analyst extracting structured data from a startup pitch deck.

Extract the following fields. If a field is not present in the deck, use null. Do not invent or infer information beyond what's clearly stated.

Return a JSON object with this exact structure:

{
  "startup_name": "string or null",
  "tagline": "string or null",
  "sector": "string or null",
  "stage": "Idea | MVP | Pilot | Early Revenue | Growth | Scale | null",
  "geography": ["list of geographies mentioned"],

  "founders": [
    {
      "name": "string",
      "role": "string",
      "experience_years": "number or null",
      "prior_companies": ["list"],
      "prior_outcomes": "string describing exits/scale achieved or null",
      "education": "string or null",
      "domain_match": "boolean - does background fit the startup's sector?"
    }
  ],
  "team_size": "number or null - includes non-founders",
  "key_hires_planned": ["list of role gaps mentioned"],

  "problem_statement": "string - what problem are they solving",
  "problem_quantified": "boolean - is the problem quantified with specific numbers?",
  "problem_evidence": "string - evidence cited for the problem (sources, stats)",

  "solution": "string - what the product does",
  "product_maturity": "Idea | MVP | Pilot | Live | Scaled",

  "customers": {
    "total_count": "number or null",
    "named_customers": ["list of named logos"],
    "paying_count": "number or null",
    "pilot_count": "number or null",
    "case_studies": [
      {
        "customer_name": "string",
        "outcome_claim": "string",
        "outcome_metrics": "string with specific numbers"
      }
    ]
  },

  "revenue": {
    "current_arr": "number in USD or null",
    "current_mrr": "number in USD or null",
    "growth_rate": "string or null",
    "retention_data": "string or null - NRR, churn, cohort retention if mentioned",
    "monetization_model": "string"
  },

  "market": {
    "tam": "string or null",
    "sam": "string or null",
    "som": "string or null",
    "icp": "string - who is the ideal customer?",
    "named_competitors": ["list"],
    "differentiation": "string"
  },

  "fundraise": {
    "amount_seeking": "number in USD or null",
    "valuation_pre": "number in USD or null",
    "previously_raised": "number in USD or null",
    "use_of_proceeds": "string",
    "target_milestone": "string - what they aim to achieve with this raise",
    "target_arr_mentioned": "number in USD or null",
    "target_timeline_months": "number or null"
  },

  "claims_with_evidence": ["list of specific quantified outcome claims with attribution"],
  "claims_without_evidence": ["list of claims made without supporting evidence"],

  "red_flags_observed": ["list of any concerning patterns"],
  "missing_critical_info": ["list of fields that should be in deck but aren't"]
}

Be thorough but conservative. Mark fields null when uncertain rather than guessing.
Return ONLY the JSON object, no other text."""


def extract_from_pdf(pdf_bytes: bytes, api_key: str) -> dict:
    """
    Extract structured data from a pitch deck PDF using Claude's vision.
    Returns the parsed JSON dict.
    """
    client = Anthropic(api_key=api_key)
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=4096,
        temperature=0,
        system=EXTRACTION_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64
                    }
                },
                {
                    "type": "text",
                    "text": "Extract the structured data from this pitch deck. Return only the JSON object."
                }
            ]
        }]
    )

    response_text = response.content[0].text

    # Try to parse the response as JSON
    try:
        # Look for JSON in the response (may be wrapped in markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback: return as raw text
        return {"_raw_extraction": response_text, "_parse_error": True}
