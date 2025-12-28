import streamlit as st
import pandas as pd
from data_loader import load_data
from kpi_engine import calculate_kpis
from ai_engine import generate_ai_insights
from report_generator import generate_pdf

st.set_page_config(layout="wide")
st.title("AI-Enabled Industrial Energy Management System")

uploaded_file = st.file_uploader(
    "Upload Energy Data (CSV or Excel)",
    type=["csv", "xlsx"]
)

api_key = st.text_input("Enter Gemini API Key", type="password")

if uploaded_file:
    df = load_data(uploaded_file)
    df = calculate_kpis(df)

    st.subheader("Processed Data")
    st.dataframe(df)

    monthly_summary = df.groupby("Equipment").agg({
        "Actual_kWh": "sum",
        "Cost_Loss_Rs": "sum",
        "KPI_Score": "mean"
    }).reset_index()

    st.subheader("Monthly KPI Summary")
    st.dataframe(monthly_summary)

    st.bar_chart(
        monthly_summary.set_index("Equipment")["KPI_Score"]
    )

    if api_key and st.button("Generate AI Engineering Report"):
        ai_report = generate_ai_insights(monthly_summary, api_key)
        st.subheader("AI Engineering Report")
        st.write(ai_report)

        if st.button("Export PDF Report"):
            file_path = "reports/generated_reports/Monthly_Energy_Report.pdf"
            generate_pdf(ai_report, file_path)
            st.success(f"Report saved: {file_path}")
