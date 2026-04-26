"""
Future Unicorn Evaluator - Streamlit App
Growth91 Internal Curation Tool
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from evaluator import evaluate_startup
from output import append_evaluation
from config import APP_TITLE, APP_SUBTITLE, CATEGORIES, SCORE_COLOR

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🦄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# AUTH
# ============================================================

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    password = st.text_input("Enter password", type="password")
    if st.button("Sign in"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    return False


if not check_password():
    st.stop()


# ============================================================
# UI HELPERS
# ============================================================

def render_score_gauge(score: float, tier: str, tier_color: str):
    """Render a circular score gauge using HTML/SVG."""
    circumference = 2 * 3.14159 * 86  # r = 86
    offset = circumference - (score / 100) * circumference

    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 20px 0;">
        <div style="position: relative; width: 200px; height: 200px;">
            <svg viewBox="0 0 200 200" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                <circle cx="100" cy="100" r="86" fill="none" stroke="#e6e6e6" stroke-width="12"/>
                <circle id="score-arc" cx="100" cy="100" r="86" fill="none"
                        stroke="{tier_color}" stroke-width="12" stroke-linecap="round"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{circumference}"
                        style="transition: stroke-dashoffset 1.2s ease-out;"/>
            </svg>
            <div style="position: absolute; inset: 0; display: flex; flex-direction: column;
                        align-items: center; justify-content: center;">
                <div style="font-size: 42px; font-weight: 500; line-height: 1;
                            font-family: -apple-system, BlinkMacSystemFont, sans-serif;">{score}</div>
                <div style="font-size: 13px; color: #666; margin-top: 4px;
                            font-family: -apple-system, BlinkMacSystemFont, sans-serif;">out of 100</div>
            </div>
        </div>
        <div style="background: {tier_color}22; color: {tier_color}; font-size: 14px;
                    font-weight: 500; padding: 6px 16px; border-radius: 8px;
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif;">{tier}</div>
    </div>
    <script>
        setTimeout(function() {{
            var arc = document.getElementById('score-arc');
            if (arc) arc.style.strokeDashoffset = '{offset}';
        }}, 100);
    </script>
    """
    components.html(html, height=270)


def render_category_bar(name: str, score: int, contribution: float, weight: int):
    """Render a single category as a row with progress bar."""
    color = SCORE_COLOR[score]
    pct = (score / 2) * 100

    html = f"""
    <div style="display: grid; grid-template-columns: 200px 1fr 80px 50px;
                align-items: center; gap: 12px; padding: 8px 0;
                font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 14px;">
        <div>{name}</div>
        <div style="height: 8px; background: #e6e6e6; border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: {pct}%; background: {color}; border-radius: 4px;"></div>
        </div>
        <div style="font-size: 12px; color: #666; text-align: right;">{contribution} / {weight}</div>
        <div style="font-size: 13px; font-weight: 500; text-align: center;">{score}</div>
    </div>
    """
    components.html(html, height=40)


# ============================================================
# MAIN UI
# ============================================================

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)
st.divider()

# Sidebar with logout
with st.sidebar:
    st.header("Session")
    if st.button("Sign out"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()
    st.caption("v1.0 — Growth91 internal use")


# Stage 1: Upload
if "evaluation_result" not in st.session_state:
    st.subheader("Evaluate a startup")

    uploaded_file = st.file_uploader(
        "Upload pitch deck (PDF)",
        type=["pdf"],
        help="Upload a startup pitch deck. The system will extract data and score against the Future Unicorn rubric."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        sector = st.text_input("Sector (optional)", placeholder="e.g. HR Tech")
    with col2:
        stage = st.selectbox(
            "Stage (optional)",
            ["", "Idea", "MVP", "Pilot", "Early Revenue", "Growth", "Scale"]
        )
    with col3:
        geography = st.text_input("Geography (optional)", placeholder="e.g. India")

    if uploaded_file is not None:
        if st.button("Run Evaluation", type="primary"):
            with st.spinner("Extracting data and running evaluation... This takes 60-90 seconds."):
                pdf_bytes = uploaded_file.read()
                metadata = {}
                if sector:
                    metadata["sector"] = sector
                if stage:
                    metadata["stage"] = stage
                if geography:
                    metadata["geography"] = geography

                try:
                    result = evaluate_startup(
                        pdf_bytes=pdf_bytes,
                        api_key=st.secrets["ANTHROPIC_API_KEY"],
                        metadata=metadata
                    )
                    st.session_state.evaluation_result = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Evaluation failed: {str(e)}")
                    st.exception(e)


# Stage 2: Display results
else:
    result = st.session_state.evaluation_result

    if st.button("← New evaluation"):
        del st.session_state.evaluation_result
        st.rerun()

    st.divider()

    # Header section
    col1, col2 = st.columns([1, 1.5])

    with col1:
        render_score_gauge(
            score=result["final_score"],
            tier=result["tier"],
            tier_color=result["tier_color"]
        )

    with col2:
        st.markdown(f"### {result['startup_name']}")
        if result.get("sector") or result.get("stage"):
            tags = []
            if result.get("sector"):
                tags.append(result["sector"])
            if result.get("stage"):
                tags.append(result["stage"])
            st.caption(" · ".join(tags))

        m1, m2, m3 = st.columns(3)
        with m1:
            kf_status = "Triggered" if result["kill_filter_triggered"] else "Not triggered"
            st.metric("Kill filter", kf_status)
        with m2:
            st.metric("Confidence", result["confidence"].title())
        with m3:
            st.metric("Red flags", len(result.get("red_flags", [])))

    if result["kill_filter_triggered"]:
        st.error(f"⚠️ Kill filter triggered: {result['kill_filter_reason']}")

    st.divider()

    # Category breakdown
    st.subheader("Category breakdown")
    for cat_key, cat_config in CATEGORIES.items():
        cat_data = result["categories"][cat_key]
        render_category_bar(
            name=cat_data["display_name"],
            score=cat_data["score"],
            contribution=cat_data["contribution"],
            weight=cat_data["weight"]
        )

    st.divider()

    # Tabs for details
    tab1, tab2, tab3, tab4 = st.tabs(["Rationale", "Gap analysis", "Red flags", "Founder feedback"])

    with tab1:
        for cat_key, cat_config in CATEGORIES.items():
            cat_data = result["categories"][cat_key]
            with st.expander(f"{cat_data['display_name']} — Score {cat_data['score']}"):
                st.write(cat_data["rationale"])
                st.caption(f"Votes: {cat_data['votes']} · Confidence: {cat_data['confidence']}")

    with tab2:
        if result.get("gap_list"):
            st.write("Categories where score improvement would help most (sorted by potential uplift):")
            for gap in result["gap_list"]:
                st.write(f"- **{gap['category']}** ({gap['current_score']} → {gap['target']}): up to +{gap['potential_uplift']:.1f} points")
        else:
            st.success("All categories scored at maximum.")

    with tab3:
        red_flags = result.get("red_flags", [])
        if red_flags:
            for flag in red_flags:
                severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(flag["severity"], "⚪")
                st.write(f"{severity_color} **{flag['flag']}** ({flag['severity']}): {flag['description']}")
        else:
            st.success("No red flags detected.")

        det_findings = result.get("deterministic_findings", [])
        flagged = [f for f in det_findings if f.get("status") in ("fail", "flag")]
        if flagged:
            st.divider()
            st.write("Deterministic check findings:")
            for f in flagged:
                st.write(f"- **{f['check']}**: {f.get('reason', '')}")

    with tab4:
        st.text_area(
            "Draft message to founder",
            value=result.get("founder_feedback_draft", ""),
            height=200
        )

    st.divider()

    # Save to Sheet
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("💾 Save to Google Sheet", type="primary"):
            try:
                service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
                sheet_id = st.secrets["GOOGLE_SHEET_ID"]
                append_evaluation(result, sheet_id, service_account_info)
                st.success("Saved to Google Sheet")
            except Exception as e:
                st.error(f"Failed to save: {str(e)}")

    with col_b:
        st.download_button(
            "📥 Download JSON report",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"{result['startup_name'].replace(' ', '_')}_evaluation.json",
            mime="application/json"
        )
