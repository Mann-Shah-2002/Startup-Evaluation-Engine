# Future Unicorn Evaluator

Internal curation tool for Growth91. Evaluates startup pitch decks against the locked Future Unicorn rubric and assigns a tier (High Priority / Consider / Watchlist / Reject).

## Quick Start (Local)

```bash
# Clone repo
git clone <repo-url>
cd future_unicorn_evaluator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up secrets
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with real values

# Run
streamlit run app.py
```

App will open at http://localhost:8501

## Deployment to Streamlit Cloud

### Step 1: GitHub
1. Create a private GitHub repo
2. Push this code to it
3. Make sure `.streamlit/secrets.toml` is in `.gitignore` (it should be — never commit real secrets)

### Step 2: Anthropic API Key
1. Sign up at console.anthropic.com
2. Add billing (~$50 USD is plenty for first 200 startups)
3. Create an API key, save it as `ANTHROPIC_API_KEY`

### Step 3: Google Sheet
1. Create a new Google Sheet, copy its ID from the URL (the long string between /d/ and /edit)
2. Go to console.cloud.google.com
3. Create a new project
4. Enable "Google Sheets API" and "Google Drive API"
5. Create a Service Account, download the JSON key
6. Open your Google Sheet, share it with the service account email (with edit access)

### Step 4: Streamlit Cloud
1. Sign up at share.streamlit.io with GitHub
2. Click "New app"
3. Select your repo, branch (main), and app file (app.py)
4. Click "Advanced settings" → "Secrets"
5. Paste in (with real values):

```toml
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
APP_PASSWORD = "your-secure-password"
GOOGLE_SHEET_ID = "..."
GOOGLE_SERVICE_ACCOUNT_JSON = '''
{
  "type": "service_account",
  ...
}
'''
```

6. Deploy. App will be live at `https://<your-app-name>.streamlit.app`

## Validation

After deployment, run the Talenode validation test to confirm the system is calibrated:

```bash
python tests/test_talenode.py path/to/talenode_deck.pdf YOUR_API_KEY
```

Expected output: Final Score 62.5 ± 5, Tier "Consider", kill filter not triggered.

If results diverge significantly, review the prompts in `prompts/` directory.

## Architecture

See `docs/SPECIFICATION.md` for full technical spec.

## File Structure

- `app.py` — Streamlit UI
- `evaluator.py` — Main orchestrator
- `extractor.py` — PDF → structured JSON
- `deterministic_checks.py` — Math reconciliation, red flag detection
- `llm_evaluator.py` — Claude API calls with majority voting
- `aggregator.py` — Score computation, tier assignment
- `output.py` — Google Sheets integration
- `config.py` — Weights, thresholds (LOCKED — do not modify)
- `prompts/` — LLM prompts per category

## Costs

- Per evaluation: ~₹15-25 in Anthropic API costs
- 200 startup backlog: ~₹3,000-5,000
- Streamlit Cloud: free
- Google Sheets: free

## v1 Limitations (planned for v2)

- Single startup at a time (no batch)
- No pipeline grid view
- No analytics dashboard
- No founder LinkedIn integration
- Single shared password (no per-user auth)

## Support

Issues during build: contact [client name]
Calibration adjustments: iterate on prompts in `prompts/` directory, then re-run Talenode test
