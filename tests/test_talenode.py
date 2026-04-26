"""
Test: Validation against Talenode Analytics deck.
Expected output: Final score 62.5 ± 5, Tier "Consider".

Run after deployment to verify the system is calibrated correctly.

Usage:
    python tests/test_talenode.py path/to/talenode_deck.pdf YOUR_API_KEY
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluator import evaluate_startup


def test_talenode(pdf_path: str, api_key: str):
    """Validate against Talenode expected output."""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print("Running evaluation on Talenode deck...")
    result = evaluate_startup(pdf_bytes=pdf_bytes, api_key=api_key)

    print("\n" + "="*60)
    print(f"Startup: {result['startup_name']}")
    print(f"Final Score: {result['final_score']}")
    print(f"Tier: {result['tier']}")
    print(f"Kill Filter: {'Triggered' if result['kill_filter_triggered'] else 'Not triggered'}")
    print(f"Confidence: {result['confidence']}")
    print("\nCategory Breakdown:")
    print("-"*60)
    for cat_key, cat in result['categories'].items():
        print(f"  {cat['display_name']:35} score={cat['score']} contribution={cat['contribution']}")

    print("\n" + "="*60)
    print("VALIDATION:")
    expected_score = 62.5
    score_diff = abs(result['final_score'] - expected_score)
    if score_diff <= 5:
        print(f"  PASS: Score {result['final_score']} is within ±5 of expected {expected_score}")
    else:
        print(f"  FAIL: Score {result['final_score']} diverges from expected {expected_score} by {score_diff} points")
        print("  Action: Review prompts and rubric implementation")

    if result['tier'] == 'Consider':
        print(f"  PASS: Tier 'Consider' matches expected")
    else:
        print(f"  CHECK: Tier '{result['tier']}' differs from expected 'Consider'")
        print("  Action: Verify scoring logic in aggregator.py")

    if not result['kill_filter_triggered']:
        print(f"  PASS: Kill filter not triggered (expected)")
    else:
        print(f"  FAIL: Kill filter triggered unexpectedly")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_talenode.py <pdf_path> <api_key>")
        sys.exit(1)

    test_talenode(sys.argv[1], sys.argv[2])
