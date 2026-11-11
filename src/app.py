import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
import numpy as np
from src.engine import CompensationEngine

st.set_page_config(page_title="Compensation Equity & Disparity Engine", layout="wide")

st.title("⚖️ Compensation Equity & Disparity Analysis Engine")
st.markdown("Auditing enterprise pay parity against role, level, location, performance, and tenure.")

@st.cache_data
def get_data():
    engine = CompensationEngine()
    df = engine.run_normalization_and_enrichment()
    exceptions = engine.detect_exceptions(df)
    proposals = engine.generate_remediation_proposals(df)
    return engine, df, exceptions, proposals

engine, df, exceptions, proposals = get_data()

# KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Workforce", f"{len(df):,}")
col2.metric("Median Compa-Ratio", f"{df['compa_ratio'].median():.2f}")
col3.metric("Policy Violations / Exceptions", len(exceptions))
col4.metric("Recommended Adjustments", len(proposals))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Disparity Modeling", "🚨 Policy Exceptions", "🛠️ Remediation Proposals", "📁 Dataset Explorer"])

with tab1:
    st.subheader("Multivariate Ordinary Least Squares (OLS) Regression")
    st.caption("log(Salary) ~ Role + Level + Location + Tenure + Rating + Gender + Ethnicity")
    model = engine.analyze_equity_regression(df)
    
    coef_df = pd.DataFrame({
        "Feature": model.params.index,
        "Coefficient": model.params.values,
        "Std Error": model.bse.values,
        "P-Value": model.pvalues.values
    }).reset_index(drop=True)
    
    st.dataframe(coef_df, use_container_width=True)

with tab2:
    st.subheader("Detected Policy Breaches & Integrity Exceptions")
    st.caption("Expired bands, unapproved manual overrides, and unscaled part-time compensation.")
    st.dataframe(exceptions, use_container_width=True)

with tab3:
    st.subheader("Actionable Remediation Proposals")
    st.caption("Auditable proposals elevating eligible underpaid employees to band standard (0.90 compa-ratio).")
    st.dataframe(proposals, use_container_width=True)

with tab4:
    st.subheader("Normalized Employee Salary Ledger")
    selected_role = st.selectbox("Filter by Role:", options=["ALL"] + list(df["role_id"].unique()))
    filtered_df = df if selected_role == "ALL" else df[df["role_id"] == selected_role]
    st.dataframe(filtered_df[[
        "emp_id", "gender", "ethnicity", "role_id", "level_id", "location_id",
        "fte", "base_salary_local", "currency", "compa_ratio", "range_penetration"
    ]], use_container_width=True)