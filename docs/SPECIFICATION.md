# Future Unicorn Evaluator — Technical Specification v1.0

## Project Context

**Client:** Growth91 (Growth Sense Group), India-based startup investment platform.

**Problem:** Growth91 has 200+ startups in their pipeline that need curation/QC evaluation before being listed for ~2,000 investors. Manual evaluation is slow and inconsistent across evaluators.

**Solution:** A web-based evaluation tool that applies a locked, deterministic rubric to startup pitch decks and produces structured scoring with tier assignment.

**Deadline:** 1.5 days for v1.

## What You're Building

A Streamlit web application that:

1. Accepts a startup pitch deck (PDF) upload
2. Optionally accepts metadata (sector, stage, geography)
3. Extracts structured data from the deck via Anthropic Claude API
4. Applies a 6-category scoring rubric (deterministic + LLM-evaluated)
5. Produces a final score (0-100), tier assignment, and category breakdown
6. Displays results via a dashboard with a circular score gauge
7. Saves evaluations to a shared Google Sheet
8. Is password-protected and deployed to Streamlit Community Cloud

## Architecture

```
[Streamlit UI - app.py]
        ↓
[Auth check - streamlit_authenticator]
        ↓
[PDF Upload]
        ↓
[evaluator.py - main orchestrator]
        ↓
   ┌────────────────┬─────────────────┐
   ↓                ↓                 ↓
[extractor.py]  [deterministic   [llm_evaluator.py]
                 _checks.py]     (calls Anthropic API)
   ↓                ↓                 ↓
   └────────────────┴─────────────────┘
        ↓
[aggregator.py - weighted sum + kill filter + tier]
        ↓
[output.py - format results, push to Google Sheet]
        ↓
[Dashboard renders results]
```

## File Structure

```
future_unicorn_evaluator/
├── app.py                     # Streamlit UI
├── evaluator.py               # Main orchestrator
├── extractor.py               # Deck → structured JSON
├── deterministic_checks.py    # Math reconciliation
├── llm_evaluator.py           # 6 category scoring via Claude
├── aggregator.py              # Score computation + tier
├── output.py                  # Google Sheet integration
├── config.py                  # Weights, thresholds, constants
├── prompts/
│   ├── extraction.txt
│   ├── founder_stage.txt
│   ├── internal_consistency.txt
│   ├── claim_testability.txt
│   ├── sector_coherence.txt
│   ├── stage_coherence.txt
│   └── problem_market_fit.txt
├── tests/
│   └── test_talenode.py
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.template
└── README.md
```

## The Locked Rubric

This rubric is FINAL. Do not modify weights, thresholds, or scoring logic.

### Scoring Scale

Every category scores on a discrete 3-point scale:

- **0** = Weak / unverified / inconsistent → normalized to 0
- **1** = Partial / unclear / mixed → normalized to 50
- **2** = Strong / verifiable / aligned → normalized to 100

### The 6 Categories with Weights

| # | Category | Weight |
|---|---|---|
| 1 | Founder–Stage Translation | 20 |
| 2 | Internal Consistency | 20 |
| 3 | Claim Testability | 20 |
| 4 | Sector Coherence | 15 |
| 5 | Stage Coherence | 15 |
| 6 | Problem × Market Fit | 10 |
| | **Total** | **100** |

### Score Computation

```
For each category:
    contribution = weight × (normalized_score / 100)

final_score = sum of all 6 contributions
```

### Kill Filter (Hard Rejection)

If `Internal Consistency == 0` OR `Claim Testability == 0`:
- Tier is forced to "Reject" regardless of weighted score
- This must be a hard override in the aggregator

### Tier Mapping

| Score Range | Tier | Color (hex) |
|---|---|---|
| 75–100 | High Priority | #639922 (green) |
| 60–74 | Consider | #BA7517 (amber) |
| 40–59 | Watchlist | #D85A30 (orange) |
| 0–39 | Reject | #A32D2D (red) |
| Kill filter triggered | Reject (override) | #A32D2D |

### Rubric Anchors

See individual prompt files in `prompts/` directory for full rubric anchors per category. Each prompt file contains:
- Core question for the category
- Rubric anchors for 0/1/2 scores
- Dispute rules for borderline cases
- Sub-signals where applicable (Sector Coherence, Stage Coherence)

## Validation Test Case

The system has been calibrated against Talenode Analytics, an HR data quality SaaS startup. Expected output when running on Talenode's deck:

```
Final Score: 62.5
Tier: Consider

Category Breakdown:
- Founder–Stage Translation: 1 (contributes 10.0)
- Internal Consistency: 1 (contributes 10.0)
- Claim Testability: 1 (contributes 10.0)
- Sector Coherence: 2 (contributes 15.0)
- Stage Coherence: 1 (contributes 7.5)
- Problem × Market Fit: 2 (contributes 10.0)

Kill Filter: Not triggered
```

If your implementation produces this score (±5 points) on the Talenode deck, the system is working correctly. Larger divergence means a prompt or aggregation bug.

## LLM Configuration

**Provider:** Anthropic
**Model:** `claude-sonnet-4-5` (the latest Sonnet at deploy time; check anthropic.com/api for current model name)
**Temperature:** 0 (deterministic)
**Max tokens:** 1024 per category evaluation
**System prompt:** Loaded from prompt file per category

**Reliability strategy:** Run each category evaluation 3 times, take the majority vote on the score. If all 3 disagree (rare), flag confidence as "low" and route to human review.

## Output Schema

Each evaluation produces a JSON object with this structure:

```json
{
  "startup_name": "Talenode Analytics",
  "evaluation_id": "uuid-string",
  "evaluated_at": "2025-XX-XX timestamp",
  "final_score": 62.5,
  "tier": "Consider",
  "kill_filter_triggered": false,
  "kill_filter_reason": null,
  "confidence": "high",
  "categories": {
    "founder_stage_translation": {
      "score": 1,
      "normalized": 50,
      "weight": 20,
      "contribution": 10.0,
      "rationale": "...",
      "votes": [1, 1, 2]
    },
    "internal_consistency": { ... },
    "claim_testability": { ... },
    "sector_coherence": { ... },
    "stage_coherence": { ... },
    "problem_market_fit": { ... }
  },
  "extracted_data": { ... },
  "deterministic_findings": [ ... ],
  "red_flags": [ ... ],
  "gap_list": [ ... ],
  "founder_feedback_draft": "..."
}
```

## UI Requirements

### Login Page
- Single password field
- Authenticate against `st.secrets["app_password"]`
- Failed login shows error, no rate limiting needed for v1

### Main Page
- Logo / title at top
- File uploader for PDF
- Optional metadata fields (sector dropdown, stage dropdown, geography text)
- "Run Evaluation" button

### Results Page
The visual design must match this specification:

**Top section: Score gauge + summary**
- Circular gauge on left (200px diameter), score number in center
- Arc fills from 0° (top) clockwise based on score percentage
- Arc color matches tier:
  - 75-100: green (#639922)
  - 60-74: amber (#BA7517)
  - 40-59: orange (#D85A30)
  - 0-39: red (#A32D2D)
- Tier badge below gauge in matching color
- To the right: startup name, sector tag, three metric cards (kill filter status, confidence, red flag count)

**Middle section: Category breakdown**
- 6 rows, one per category
- Each row: category name | progress bar | "X / Y" (contribution / max) | raw score (0/1/2)
- Progress bar fills proportional to normalized score
- Bar color matches the score: 0 = red, 1 = amber, 2 = green

**Bottom section: Action buttons**
- "View rationale" — expands to show full per-category rationale
- "Gap analysis" — shows what would move the score up
- "Founder feedback" — shows draft email for outreach
- "Save to Sheet" — pushes to Google Sheet
- "Download report" — generates PDF or markdown report

### Visual Design Rules
- Use Streamlit's native components where possible
- For the score gauge, use a custom HTML component (st.components.v1.html)
- Sans-serif throughout
- No gradients, drop shadows, or decorative effects
- Match Anthropic-style minimalism — flat surfaces, 0.5px borders, generous whitespace
- Score gauge should animate (arc fills smoothly on load) — optional but adds polish

## Google Sheet Integration

Use `gspread` library. Credentials via service account JSON stored in Streamlit secrets.

**Sheet structure:**
| Column | Description |
|---|---|
| Timestamp | When evaluated |
| Startup Name | From extraction |
| Sector | User input or extracted |
| Stage | User input or extracted |
| Final Score | 0-100 |
| Tier | Reject/Watchlist/Consider/High Priority |
| Kill Filter | Yes/No |
| Confidence | High/Medium/Low |
| Founder | Score 0-2 |
| Consistency | Score 0-2 |
| Testability | Score 0-2 |
| Sector | Score 0-2 |
| Stage | Score 0-2 |
| Problem-Fit | Score 0-2 |
| Red Flags | Comma-separated list |
| Evaluator | Streamlit username (or "system" for v1) |
| Notes | Free text, post-evaluation human notes |

## Deployment

### Local Development

```bash
git clone <repo>
cd future_unicorn_evaluator
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml with API keys
streamlit run app.py
```

### Production Deployment to Streamlit Cloud

1. Push repo to GitHub (private repo recommended)
2. Sign in to share.streamlit.io with GitHub
3. Click "New app", select repo and branch
4. Add secrets via Streamlit Cloud UI:
   - `ANTHROPIC_API_KEY`
   - `APP_PASSWORD`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (paste full JSON as string)
5. Deploy

App will be live at `https://<app-name>.streamlit.app`

### Password Protection

Use a simple password gate in `app.py`:

```python
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    password = st.text_input("Enter password", type="password")
    if password == st.secrets["APP_PASSWORD"]:
        st.session_state.authenticated = True
        st.rerun()
    elif password:
        st.error("Incorrect password")
    return False

if not check_password():
    st.stop()
```

## Cost Expectations

**Per evaluation:**
- ~6 categories × 3 LLM calls = 18 calls
- ~2K input tokens, ~500 output tokens per call
- Approximate cost: ₹15-25 per startup
- 200 startups full backlog: ₹3,000-5,000 total

**Streamlit Cloud:** Free tier sufficient for this use case
**Google Sheets API:** Free
**GitHub:** Free for private repos

## Calibration Plan

After deployment, before going live:

1. Run on Talenode deck. Expected: 62.5 / Consider (±5 acceptable)
2. Run on 4 reference startups (client will provide). Compare to manual scores.
3. Target: 80% category-level agreement with manual scoring
4. If divergence is high, adjust prompts (especially the dispute rules section)
5. Document any prompt changes in CHANGELOG.md

## Out of Scope for v1

These are NOT required:
- Batch processing (single-startup mode only)
- Pipeline grid view (multiple startups at once)
- Distribution analytics
- Founder LinkedIn integration
- User management beyond single shared password
- Audit log or evaluation history (Google Sheet serves this purpose)

These can be added in v2 after v1 is in production.

## Critical Implementation Notes

1. **PDF parsing is fragile.** Pitch decks are often image-heavy. Use `pdfplumber` for text extraction. If a deck is mostly images, send the PDF directly to Claude's vision capability via the document parameter rather than parsing text.

2. **Majority voting for LLM scores.** This is not optional. Single LLM calls have ~10-15% variance on rubric scoring. Three calls + majority vote drops variance to <3%.

3. **Confidence scoring matters.** When the 3 LLM votes disagree (e.g., scores of 0, 1, 2), set confidence to "low" and surface this in the UI. The user should know when the system is uncertain.

4. **The kill filter is a hard override.** If Internal Consistency or Claim Testability comes back as 0, the tier MUST be Reject regardless of the weighted total. This logic should be in `aggregator.py` and clearly documented.

5. **Don't over-engineer.** This is a v1 with a 1.5-day deadline. Skip unit tests beyond the Talenode validation case. Skip logging frameworks. Skip async. Get it working, ship it, iterate.

## Contact

For specification clarifications during build, contact: [client to fill in]
For LLM prompt issues during calibration, work with the client to iterate.

---

End of Specification.
