import streamlit as st
import pandas as pd

from data_loader import load_data
from kpi_engine import calculate_kpis
from ai_engine import generate_ai_insights
from report_generator import generate_pdf

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Energy Management System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PREMIUM UI STYLING
# --------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #f9fafb;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.04);
}
.kpi-title {
    font-size: 14px;
    color: #6b7280;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
}
.sub-text {
    color: #6b7280;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<div class='section-title'>⚡ AI-Enabled Energy Management Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Industrial KPI monitoring • Cost loss analytics • AI insights</div>", unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# SIDEBAR (CONTROL PANEL)
# --------------------------------------------------
with st.sidebar:
    st.header("📂 Data Input")
    uploaded_file = st.file_uploader(
        "Upload Energy Data (CSV / Excel)",
        type=["csv", "xlsx"]
    )

    st.header("🔐 AI Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password"
    )

# --------------------------------------------------
# MAIN LOGIC
# --------------------------------------------------
if uploaded_file:
    df = load_data(uploaded_file)
    df = calculate_kpis(df)

    monthly_summary = df.groupby("Equipment").agg({
        "Actual_kWh": "sum",
        "Cost_Loss_Rs": "sum",
        "KPI_Score": "mean"
    }).reset_index()

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------
    total_loss = monthly_summary["Cost_Loss_Rs"].sum()
    avg_kpi = monthly_summary["KPI_Score"].mean()
    worst_eq = monthly_summary.sort_values("KPI_Score").iloc[0]["Equipment"]

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class='card'>
        <div class='kpi-title'>Monthly Energy Loss</div>
        <div class='kpi-value'>₹ {total_loss:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class='card'>
        <div class='kpi-title'>Average KPI Score</div>
        <div class='kpi-value'>{avg_kpi:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class='card'>
        <div class='kpi-title'>Worst Performing Equipment</div>
        <div class='kpi-value'>{worst_eq}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --------------------------------------------------
    # KPI TABLE WITH STATUS COLOR
    # --------------------------------------------------
    st.markdown("<div class='section-title'>📋 Equipment KPI Scorecard</div>", unsafe_allow_html=True)

    def highlight_kpi(val):
        if val < 70:
            return "background-color:#fee2e2"
        elif val < 85:
            return "background-color:#fef3c7"
        return "background-color:#dcfce7"

    styled_df = monthly_summary.style.applymap(
        highlight_kpi, subset=["KPI_Score"]
    )

    st.dataframe(styled_df, use_container_width=True)

    # --------------------------------------------------
    # CHARTS
    # --------------------------------------------------
    st.markdown("<div class='section-title'>📊 Performance Visuals</div>", unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        st.subheader("KPI Score by Equipment")
        st.bar_chart(
            monthly_summary.set_index("Equipment")["KPI_Score"],
            height=320
        )

    with colB:
        st.subheader("Energy Cost Loss Distribution")
        st.bar_chart(
            monthly_summary.set_index("Equipment")["Cost_Loss_Rs"],
            height=320
        )

    st.divider()

    # --------------------------------------------------
    # AI REPORT
    # --------------------------------------------------
    if api_key:
        if st.button("🧠 Generate AI Engineering Insights"):
            st.session_state.ai_report = generate_ai_insights(
                monthly_summary, api_key
            )
            st.session_state.pdf_ready = False
            st.session_state.pdf_path = None
            st.success("AI insights generated successfully")

    if st.session_state.ai_report:
        with st.expander("🧠 AI Engineering Insights", expanded=True):
            st.write(st.session_state.ai_report)

        # --------------------------------------------------
        # PDF EXPORT
        # --------------------------------------------------
        st.markdown("<div class='section-title'>📄 Management Report</div>", unsafe_allow_html=True)

        if st.button("Generate Monthly PDF Report"):
            pdf_path = "reports/generated_reports/Monthly_Energy_Report.pdf"
            generate_pdf(
                st.session_state.ai_report,
                monthly_summary,
                pdf_path
            )
            st.session_state.pdf_ready = True
            st.session_state.pdf_path = pdf_path
            st.success("PDF report generated successfully")

    if st.session_state.pdf_ready and st.session_state.pdf_path:
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            st.download_button(
                "⬇ Download PDF Report",
                pdf_file,
                file_name="Monthly_Energy_Report.pdf",
                mime="application/pdf"
            )

else:
    st.info("⬅ Upload energy data to begin analysis")
