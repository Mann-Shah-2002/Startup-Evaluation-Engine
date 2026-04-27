from fpdf import FPDF
from config import CATEGORIES

def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        '–': '-', '—': '-',
        '“': '"', '”': '"',
        '‘': "'", '’': "'",
        '…': '...',
        '\u2028': '\n', '\u2029': '\n',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Replace any remaining unsupported characters with '?'
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(result: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    
    # Fonts
    pdf.set_font("helvetica", style="B", size=18)
    
    # Title
    pdf.cell(0, 10, sanitize_text("Future Unicorn Evaluator Report"), ln=True, align="C")
    pdf.ln(5)
    
    # Startup Info Header
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text(f"Startup: {result.get('startup_name', 'Unknown')}"), ln=True)
    
    pdf.set_font("helvetica", size=11)
    info_line = []
    if result.get("sector"): info_line.append(f"Sector: {result['sector']}")
    if result.get("stage"): info_line.append(f"Stage: {result['stage']}")
    if result.get("geography"): info_line.append(f"Geo: {result['geography']}")
    
    if info_line:
        pdf.cell(0, 6, sanitize_text(" | ".join(info_line)), ln=True)
    pdf.ln(5)
    
    # Score and Tier
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text(f"Final Score: {result.get('final_score', 0)} / 100"), ln=True)
    pdf.cell(0, 8, sanitize_text(f"Tier: {result.get('tier', 'Unknown')}"), ln=True)
    
    if result.get("kill_filter_triggered"):
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, sanitize_text(f"KILL FILTER TRIGGERED: {result.get('kill_filter_reason', '')}"), ln=True)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Categories Breakdown
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text("Category Breakdown"), ln=True)
    pdf.set_font("helvetica", size=10)
    
    cats = result.get("categories", {})
    for cat_key, cat_config in CATEGORIES.items():
        if cat_key in cats:
            c = cats[cat_key]
            pdf.set_font("helvetica", style="B", size=11)
            pdf.cell(0, 8, sanitize_text(f"{c.get('display_name', cat_key)} - Score: {c.get('score', 0)} (Weight: {c.get('weight', 0)})"), ln=True)
            pdf.set_font("helvetica", size=10)
            pdf.multi_cell(0, 6, sanitize_text(f"Rationale: {c.get('rationale', '')}"))
            pdf.ln(3)

    pdf.add_page()
    
    # Red Flags
    red_flags = result.get("red_flags", [])
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text("Red Flags"), ln=True)
    pdf.set_font("helvetica", size=10)
    if red_flags:
        for flag in red_flags:
            pdf.multi_cell(0, 6, sanitize_text(f"- [{flag.get('severity', '').upper()}] {flag.get('flag', '')}: {flag.get('description', '')}"))
            pdf.ln(2)
    else:
        pdf.cell(0, 6, sanitize_text("No red flags detected."), ln=True)
    pdf.ln(5)
    
    # Deterministic Findings
    det = result.get("deterministic_findings", [])
    flagged = [f for f in det if f.get("status") in ("fail", "flag")]
    if flagged:
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 8, sanitize_text("Deterministic Check Flags:"), ln=True)
        pdf.set_font("helvetica", size=10)
        for f in flagged:
            pdf.multi_cell(0, 6, sanitize_text(f"- {f.get('check', '')}: {f.get('reason', '')}"))
        pdf.ln(5)
        
    # Gap Analysis
    gaps = result.get("gap_list", [])
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text("Gap Analysis"), ln=True)
    pdf.set_font("helvetica", size=10)
    if gaps:
        for gap in gaps:
            pdf.multi_cell(0, 6, sanitize_text(f"- {gap.get('category', '')} ({gap.get('current_score', 0)} -> {gap.get('target', 0)}): potential uplift +{gap.get('potential_uplift', 0)}"))
            pdf.ln(2)
    else:
        pdf.cell(0, 6, sanitize_text("No gaps found."), ln=True)
    pdf.ln(5)
    
    # Founder Feedback
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 8, sanitize_text("Draft Founder Feedback"), ln=True)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(0, 6, sanitize_text(str(result.get("founder_feedback_draft", "No feedback generated."))))
    
    # Return as bytes
    return bytes(pdf.output(dest='S'))
