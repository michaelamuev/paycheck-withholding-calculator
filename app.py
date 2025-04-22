import streamlit as st
import pandas as pd

# --- Page config ---
st.set_page_config(
    page_title="Mike's Paycheck Calculator 💸",
    page_icon="💸",
    layout="centered"
)

# --- Optional Logo ---
st.image("logo.png", width=80)

# --- Header ---
st.title("Mike's Paycheck Withholding Tool")
st.caption("Built with Python • Powered by IRS Pub 15-T")

# --- Load IRS Wage Bracket CSV ---
@st.cache_data
def load_wage_data():
    return pd.read_csv("def load_wage_data():
    return pd.read_csv("2024_federal_wage_bracket_master.csv")

wage_df = load_wage_data()

# --- Inputs ---
gross_pay = st.number_input("Gross Pay This Period ($)", min_value=0.0, value=1000.0)
pay_frequency = st.selectbox("Pay Frequency", ["weekly", "biweekly", "semimonthly", "monthly"])
filing_status = st.selectbox("Filing Status", ["single", "married", "head"])
step_2_checked = st.checkbox("Step 2 Checkbox (Multiple Jobs)?")
dependents_amount = st.number_input("Dependent Claim Amount (Step 3)", min_value=0.0, value=0.0)
other_income = st.number_input("Other Income (Step 4a)", min_value=0.0, value=0.0)
deductions = st.number_input("Deductions (Step 4b)", min_value=0.0, value=0.0)
extra_withholding = st.number_input("Additional Withholding (Step 4c)", min_value=0.0, value=0.0)

# --- Lookup IRS Withholding ---
def lookup_wage_bracket(filing_status, pay_frequency, gross_pay):
    matches = wage_df[
        (wage_df["filing_status"] == filing_status.lower()) &
        (wage_df["pay_frequency"] == pay_frequency.lower()) &
        (wage_df["min_wage"] <= gross_pay) &
        (wage_df["max_wage"] > gross_pay)
    ]
    if not matches.empty:
        return float(matches.iloc[0]["withholding"])
    return 0.0

# --- Calculation Logic ---
def calculate_paycheck():
    frequency_map = {"weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12}
    periods_per_year = frequency_map[pay_frequency]
    annual_gross = gross_pay * periods_per_year

    fed_withholding = lookup_wage_bracket(filing_status, pay_frequency, gross_pay)
    fed_withholding += extra_withholding

    social_security = min(annual_gross, 168600) * 0.062 / periods_per_year
    medicare = annual_gross * 0.0145 / periods_per_year

    total_tax = fed_withholding + social_security + medicare
    net_pay = gross_pay - total_tax

    return {
        "Federal Withholding": round(fed_withholding, 2),
        "Social Security": round(social_security, 2),
        "Medicare": round(medicare, 2),
        "Net Pay": round(net_pay, 2)
    }

# --- Output ---
if st.button("Calculate Take Home Pay"):
    results = calculate_paycheck()
    st.subheader("Paycheck Breakdown:")
    for k, v in results.items():
        st.write(f"{k}: ${v}")

