from fpdf import FPDF


def sanitize_text(text):
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "•": "-",
        "₹": "Rs.",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", "ignore").decode("latin-1")


def extract_section(text, start_tag, end_tag=None):
    if start_tag not in text:
        return ""

    start = text.index(start_tag) + len(start_tag)
    if end_tag and end_tag in text:
        end = text.index(end_tag)
        return text[start:end].strip()
    return text[start:].strip()


def generate_pdf(ai_text, summary_df, filename):
    pdf = FPDF()
    pdf.add_page()

    # ---------- HEADER ----------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI-Enabled Energy Management Report", ln=True)

    pdf.set_font("Arial", size=9)
    pdf.cell(0, 6, "Prepared by: AI Energy Management System", ln=True)
    pdf.ln(6)

    safe_text = sanitize_text(ai_text)

    exec_summary = extract_section(safe_text, "[EXEC_SUMMARY]", "[KEY_FINDINGS]")
    key_findings = extract_section(safe_text, "[KEY_FINDINGS]", "[ROOT_CAUSES]")
    root_causes = extract_section(safe_text, "[ROOT_CAUSES]", "[CORRECTIVE_ACTIONS]")
    actions = extract_section(safe_text, "[CORRECTIVE_ACTIONS]", "[COST_SAVINGS]")
    savings = extract_section(safe_text, "[COST_SAVINGS]")

    def write_section(title, content):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Arial", size=9)
        pdf.multi_cell(0, 6, content)
        pdf.ln(3)

    write_section("1. Executive Summary", exec_summary)
    write_section("2. Key Findings", key_findings)
    write_section("3. Probable Root Causes", root_causes)
    write_section("4. Recommended Corrective Actions", actions)
    write_section("5. Estimated Cost Savings", savings)

    # ---------- KPI SUMMARY ----------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "6. Monthly KPI Summary", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", size=9)
    for _, row in summary_df.iterrows():
        line = (
            f"{row['Equipment']} | "
            f"KPI Score: {row['KPI_Score']:.1f} | "
            f"Cost Loss (Rs): {row['Cost_Loss_Rs']:.0f}"
        )
        pdf.multi_cell(0, 6, sanitize_text(line))

    pdf.output(filename)
