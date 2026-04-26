# YOUR CHECKLIST — While the Engineer Builds

## Hour 0–2: Find and Hire the Engineer

### Where to find them
- **Internshala:** internshala.com (post a 1-day Python + Streamlit gig)
- **Wellfound (AngelList Talent):** wellfound.com (good for Indian freelancers)
- **Upwork:** upwork.com (vetted but more expensive)
- **Your network:** XLRI / Hansraj / Symbiosis alumni groups, ex-colleagues from Swiggy / AON / Gartner

### What to look for
- Python (intermediate or better)
- Streamlit experience (any — it's easy)
- REST API experience (calling external APIs)
- GitHub familiarity
- Available immediately for 1-day sprint

### What to ask in screening (5-min call)
1. "Have you built and deployed a Streamlit app before?" (Yes is mandatory)
2. "Do you know how to use the Anthropic or OpenAI API?" (Either is fine)
3. "Can you start in the next 2 hours and work for ~36 hours?" (Hard requirement)
4. "What do you charge for a one-day project?" (Should be ₹8,000-15,000)

If they hesitate on any of these, move to next candidate.

### Hand them
- The `future_unicorn_evaluator/` folder
- The Talenode pitch deck (for validation)
- This README at the top: `docs/ENGINEER_BRIEFING.md`

## Hour 0–2: Account Setup (Do in Parallel)

### 1. Anthropic API Account (15 min)
1. Go to **console.anthropic.com**
2. Sign up with email
3. Verify email
4. Click "Add billing" — add a credit card with ₹4,000-5,000 credit
5. Click "API Keys" → "Create Key"
6. Copy the key starting with `sk-ant-api03-` — save securely
7. Share with engineer (via secure channel — not WhatsApp)

### 2. GitHub Account (10 min)
1. Go to **github.com**
2. Sign up with email
3. Verify email
4. Once engineer is hired, you'll add them as a collaborator on the repo

### 3. Streamlit Cloud Account (5 min)
1. Go to **share.streamlit.io**
2. Click "Sign in with GitHub"
3. Authorize the connection

### 4. Google Sheet (10 min)
1. Go to **sheets.google.com**, create a new sheet
2. Name it "Future Unicorn Evaluations"
3. Copy the sheet ID from the URL (the long string between `/d/` and `/edit`)
4. Save this ID — engineer will need it

### 5. Google Cloud Project (15 min — engineer can also do this)
1. Go to **console.cloud.google.com**
2. Create a new project: "growth91-evaluator"
3. Enable APIs:
   - Search "Google Sheets API" → Enable
   - Search "Google Drive API" → Enable
4. The engineer will create a service account and download credentials.
5. When they have the service account email, share your Google Sheet with that email (with Edit access).

## Hour 2–24: Reference Startups for Calibration

While the engineer works, prepare 5 reference startups from your queue that you've already manually scored. The engineer needs these for calibration testing.

For each startup, provide:
- The pitch deck (PDF)
- Your manually-assigned score in each category (0/1/2)
- Your assigned tier
- Brief notes on why

The engineer will run these through the system and compare. Target: 80% category-level agreement.

If the system disagrees with your scoring, that's information — sometimes the system catches what you missed, sometimes prompts need tuning.

## Hour 24–36: Final Calibration

When the engineer hands back the deployed app:

1. **Log in** with the password they set
2. **Upload Talenode deck** — verify score 62.5 ± 5, tier "Consider"
3. **Upload your 5 reference startups** — compare to your manual scores
4. **Save to Google Sheet** — verify the row appears correctly
5. **Test edge cases:**
   - Upload a deck with no founders listed (should still extract gracefully)
   - Upload a very short deck (3-4 slides)
   - Upload a deck without financials

If something breaks, the engineer should still be available to patch.

## Hour 36+: Going Live

Once validated:
1. Update the Streamlit Cloud password to something only your team knows
2. Share the URL + password with your team
3. Start running on the 200+ backlog (one at a time, ~5 startups/hour)
4. Begin tracking which evaluations need human override (this is your data for v2)

## Budget

| Item | Cost |
|---|---|
| Engineer (1 day) | ₹8,000 - 15,000 |
| Anthropic API credit | ₹4,000 (covers 200+ evaluations) |
| Streamlit Cloud | Free |
| Google Sheets | Free |
| **Total** | **~₹12,000 - 19,000** |

## Risk Mitigation

**If the engineer flakes or can't deliver:**
- Hire a backup before midpoint (Hour 18). Don't wait until Hour 30 to discover trouble.
- The code in `future_unicorn_evaluator/` is complete — a second engineer can pick it up immediately.

**If the API calls fail:**
- Check Anthropic billing is active
- Check API key is valid
- Check the model name in `config.py` matches a current Anthropic model

**If Talenode test diverges by >10 points:**
- This means LLM scoring is misbehaving
- DO NOT change prompts — flag to client (you), iterate together
- Can also be a model version issue (check `LLM_MODEL` in config.py)

## Final Note

This system is designed to assist curation, not replace it. After you start running it on real intake:
- Track agreement rate with your manual scoring weekly
- Flag startups where the system was confidently wrong
- Use this data to refine prompts in v2

Good luck. You'll be processing 200+ startups in week 2 instead of week 12.
