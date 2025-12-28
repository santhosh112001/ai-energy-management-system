import streamlit as st
import pandas as pd

from data_loader import load_data
from kpi_engine import calculate_kpis
from ai_engine import generate_ai_insights
from report_generator import generate_pdf


# ---------- SESSION STATE ----------
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None


# ---------- UI ----------
st.set_page_config(layout="wide")
st.title("AI-Enabled Industrial Energy Management System")

uploaded_file = st.file_uploader(
    "Upload Energy Data (CSV or Excel)",
    type=["csv", "xlsx"]
)

api_key = st.text_input(
    "Enter Gemini API Key",
    type="password"
)


# ---------- DATA ----------
if uploaded_file:
    df = load_data(uploaded_file)
    df = calculate_kpis(df)

    st.subheader("Processed Equipment Data")
    st.dataframe(df)

    monthly_summary = df.groupby("Equipment").agg({
        "Actual_kWh": "sum",
        "Cost_Loss_Rs": "sum",
        "KPI_Score": "mean"
    }).reset_index()

    st.subheader("📊 Monthly Equipment KPI Summary")
    st.dataframe(monthly_summary)

    st.bar_chart(
        monthly_summary.set_index("Equipment")["KPI_Score"]
    )

    # ---------- AI REPORT ----------
    if api_key:
        if st.button("🧠 Generate AI Engineering Report"):
            st.session_state.ai_report = generate_ai_insights(
                monthly_summary, api_key
            )
            st.session_state.pdf_ready = False
            st.session_state.pdf_path = None
            st.success("AI report generated successfully")

    if st.session_state.ai_report:
        st.subheader("🧠 AI Engineering Report")
        st.write(st.session_state.ai_report)

        # ---------- PDF ----------
        if st.button("📄 Generate Monthly PDF Report"):
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
                "⬇️ Download PDF Report",
                pdf_file,
                file_name="Monthly_Energy_Report.pdf",
                mime="application/pdf"
            )
