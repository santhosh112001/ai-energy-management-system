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
# ADVANCED AESTHETIC STYLING (SAFE FOR STREAMLIT CLOUD)
# --------------------------------------------------
st.markdown("""
<style>
/* Background */
body {
    background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

/* Header */
.main-title {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sub-title {
    color: #6b7280;
    font-size: 16px;
    margin-bottom: 20px;
}

/* Glass cards */
.glass-card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.05);
    transition: all 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 30px 60px rgba(0,0,0,0.08);
}

/* KPI text */
.kpi-title {
    font-size: 14px;
    color: #6b7280;
}
.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
}

/* Section title */
.section-title {
    font-size: 24px;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 8px;
    color: #111827;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #c7d2fe, transparent);
    margin: 25px 0;
}

/* Sidebar polish */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1f2937);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Fade-in animation */
.fade-in {
    animation: fadeIn 0.8s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(8px);}
    to {opacity: 1; transform: translateY(0);}
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
st.markdown("<div class='main-title fade-in'>⚡ AI Energy Management Dashboard</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title fade-in'>Enterprise-grade energy analytics • Cost optimization • AI-driven insights</div>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("📂 Data Control")
    uploaded_file = st.file_uploader(
        "Upload Energy Data",
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
    # KPI GLASS CARDS
    # --------------------------------------------------
    total_loss = monthly_summary["Cost_Loss_Rs"].sum()
    avg_kpi = monthly_summary["KPI_Score"].mean()
    worst_eq = monthly_summary.sort_values("KPI_Score").iloc[0]["Equipment"]

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class='glass-card fade-in'>
        <div class='kpi-title'>Monthly Energy Loss</div>
        <div class='kpi-value'>₹ {total_loss:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class='glass-card fade-in'>
        <div class='kpi-title'>Average KPI Score</div>
        <div class='kpi-value'>{avg_kpi:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class='glass-card fade-in'>
        <div class='kpi-title'>Worst Performing Asset</div>
        <div class='kpi-value'>{worst_eq}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------
    # KPI TABLE
    # --------------------------------------------------
    st.markdown("<div class='section-title'>📋 Equipment KPI Scorecard</div>", unsafe_allow_html=True)

    def highlight(val):
        if val < 70:
            return "background-color:#fee2e2"
        elif val < 85:
            return "background-color:#fef3c7"
        return "background-color:#dcfce7"

    styled_df = monthly_summary.style.applymap(
        highlight, subset=["KPI_Score"]
    )

    st.dataframe(styled_df, use_container_width=True)

    # --------------------------------------------------
    # CHARTS
    # --------------------------------------------------
    st.markdown("<div class='section-title'>📊 Performance Analytics</div>", unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        st.bar_chart(
            monthly_summary.set_index("Equipment")["KPI_Score"],
            height=340
        )

    with colB:
        st.bar_chart(
            monthly_summary.set_index("Equipment")["Cost_Loss_Rs"],
            height=340
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------
    # AI INSIGHTS
    # --------------------------------------------------
    if api_key:
        if st.button("🧠 Generate AI Insights"):
            st.session_state.ai_report = generate_ai_insights(
                monthly_summary, api_key
            )
            st.session_state.pdf_ready = False
            st.session_state.pdf_path = None
            st.success("AI insights generated")

    if st.session_state.ai_report:
        with st.expander("🧠 AI Engineering Insights", expanded=True):
            st.write(st.session_state.ai_report)

        st.markdown("<div class='section-title'>📄 Executive Report</div>", unsafe_allow_html=True)

        if st.button("Generate Monthly PDF"):
            pdf_path = "reports/generated_reports/Monthly_Energy_Report.pdf"
            generate_pdf(
                st.session_state.ai_report,
                monthly_summary,
                pdf_path
            )
            st.session_state.pdf_ready = True
            st.session_state.pdf_path = pdf_path
            st.success("PDF generated successfully")

    if st.session_state.pdf_ready and st.session_state.pdf_path:
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            st.download_button(
                "⬇ Download PDF",
                pdf_file,
                file_name="Monthly_Energy_Report.pdf",
                mime="application/pdf"
            )

else:
    st.info("⬅ Upload energy data to begin analysis")
