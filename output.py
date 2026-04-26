"""
Output: Push evaluation results to a Google Sheet.
Uses gspread with a service account.
"""

from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from config import SHEET_HEADER


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_sheet(sheet_id: str, service_account_info: dict):
    """Get gspread Worksheet for the configured sheet."""
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)
    sheet = spreadsheet.sheet1

    # Ensure header row exists
    try:
        existing_headers = sheet.row_values(1)
        if not existing_headers or existing_headers != SHEET_HEADER:
            sheet.update(range_name="A1", values=[SHEET_HEADER])
    except Exception:
        sheet.update(range_name="A1", values=[SHEET_HEADER])

    return sheet


def append_evaluation(result: dict, sheet_id: str, service_account_info: dict, evaluator_name: str = "system"):
    """Append a single evaluation result to the Google Sheet."""
    sheet = get_sheet(sheet_id, service_account_info)

    cats = result.get("categories", {})
    red_flags = result.get("red_flags", [])

    row = [
        datetime.utcnow().isoformat(),
        result.get("startup_name", ""),
        result.get("sector", "") or "",
        result.get("stage", "") or "",
        result.get("final_score", 0),
        result.get("tier", ""),
        "Yes" if result.get("kill_filter_triggered") else "No",
        result.get("confidence", ""),
        cats.get("founder_stage_translation", {}).get("score", ""),
        cats.get("internal_consistency", {}).get("score", ""),
        cats.get("claim_testability", {}).get("score", ""),
        cats.get("sector_coherence", {}).get("score", ""),
        cats.get("stage_coherence", {}).get("score", ""),
        cats.get("problem_market_fit", {}).get("score", ""),
        ", ".join([f["flag"] for f in red_flags]),
        evaluator_name,
        ""  # Notes - left blank for human to fill
    ]

    sheet.append_row(row)
    return True
