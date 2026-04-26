# ENGINEER BRIEFING — Future Unicorn Evaluator

## Project at a Glance

- **Client:** Growth91 (Indian startup investment platform)
- **Deadline:** 1.5 days (~36 hours from briefing)
- **Stack:** Python + Streamlit + Anthropic Claude API + Google Sheets
- **Deployment:** Streamlit Community Cloud (free)
- **Budget:** ₹8,000–15,000 for one day of work

## What's in This Package

This zip contains **all the code and specifications you need**. Your job is mostly setup, deployment, calibration. Not greenfield development.

```
future_unicorn_evaluator/
├── docs/SPECIFICATION.md      # Read this first - full technical spec
├── README.md                   # Setup and deployment instructions
├── app.py                      # Streamlit UI - DO NOT modify
├── evaluator.py                # Main pipeline - DO NOT modify
├── extractor.py                # PDF parsing - DO NOT modify
├── llm_evaluator.py            # Claude API calls - DO NOT modify
├── deterministic_checks.py     # Math checks - DO NOT modify
├── aggregator.py               # Scoring logic - DO NOT modify
├── output.py                   # Google Sheets - DO NOT modify
├── config.py                   # Weights/thresholds - DO NOT modify
├── prompts/                    # LLM prompts - DO NOT modify in v1
├── tests/test_talenode.py      # Validation test
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.template
└── .gitignore
```

**Important:** Do not modify the rubric, weights, thresholds, or prompts without explicit client approval. The rubric was carefully designed and locked. Your job is to deploy this code, not rewrite it.

## Your Task in 36 Hours

### Hour 0–4: Setup
1. Verify you have Python 3.10+ and Git installed
2. Get repo access from the client
3. Set up local dev environment, get the app running with a test secrets file
4. Make sure `streamlit run app.py` opens the login page locally

### Hour 4–8: Get API access working
1. Client gives you access to their Anthropic console (or you spin up a test account)
2. Get a small test API key working
3. Run a test evaluation on Talenode deck (client will provide)
4. Verify it produces a score in the right range

### Hour 8–16: Deploy to Streamlit Cloud
1. Create GitHub repo (private), push code
2. Sign in to share.streamlit.io
3. Connect repo, deploy
4. Configure secrets via Streamlit UI
5. Confirm live app works

### Hour 16–24: Google Sheets integration
1. Set up Google Cloud project
2. Enable Sheets API + Drive API
3. Create service account, download JSON key
4. Create the Google Sheet, share with service account
5. Add credentials to Streamlit secrets
6. Test "Save to Sheet" button in deployed app

### Hour 24–36: Calibration & polish
1. Run on 5 reference startups client provides
2. Compare to client's manual scores
3. Document any divergences (do NOT change prompts unless client approves)
4. Fix any UI bugs you spot
5. Hand back to client with deployment URL + admin access

## Critical Constraints

1. **Do not modify the rubric.** Weights, thresholds, scoring logic, kill filter, tier mapping — all locked. If you think something's wrong, flag it, don't fix it.

2. **Do not modify the prompts.** The LLM prompts in `prompts/` are calibrated. If results diverge from expected on Talenode, that's a deployment or model version issue, not a prompt issue.

3. **Use majority voting.** Each category gets 3 LLM calls, take majority. This is implemented; don't shortcut it.

4. **Keep it simple.** This is v1 with a hard deadline. Don't add features. Don't refactor. Don't add unit tests beyond Talenode. Ship what's spec'd.

5. **Confidentiality.** Pitch decks may be marked confidential. Don't share, screenshot, or store them outside the deployed app.

## Validation Criteria (Must Pass Before Handoff)

- [ ] App deployed at a public Streamlit Cloud URL
- [ ] Password protection working
- [ ] Talenode test passes: score 62.5 ± 5, tier "Consider"
- [ ] Google Sheet integration: clicking "Save to Sheet" appends a row
- [ ] No runtime errors when uploading a 5-page or 20-page deck
- [ ] Score gauge renders correctly with smooth animation
- [ ] Category breakdown shows 6 rows with progress bars
- [ ] All 4 result tabs (Rationale, Gap analysis, Red flags, Founder feedback) populate

## What Success Looks Like

End of Hour 36: Client has a working URL, can log in with a password, upload a PDF, get an evaluation in 60-90 seconds, see the dashboard, save to Google Sheet, and download a JSON report. The Talenode validation passes.

Anything beyond that is v2.

## Communication

- Direct any clarification questions to the client immediately — don't guess
- If something doesn't work after 30 minutes of debugging, flag it and ask for help
- Track time spent so you can invoice cleanly

## Payment

Discuss with client. Suggested structure:
- 50% on local app working
- 50% on validated deployment with Sheet integration

Good luck.
