import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Mike's Calculator 💸",
    page_icon="💸",
    layout="centered"
)

# --- Header ---
st.title("Withholding Tool")
st.caption("Built with Python • Powered by IRS Percentage Method Tables")

# --- Input: Calculation Mode ---
calc_mode = st.radio("Select Calculation Mode:", ["Estimate for single paycheck", "Estimate for full year"])

if calc_mode == "Estimate for full year":
    income_type = st.radio("Select Income Type:", ["Salary", "Hourly"])

# --- Inputs ---
gross_pay = 0.0
if calc_mode == "Estimate for single paycheck":
    gross_pay = st.number_input("Gross Pay This Period ($)", min_value=0.0, value=0.0)
elif income_type == "Salary":
    gross_pay = st.number_input("Annual Salary ($)", min_value=0.0, value=0.0)
else:
    hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=20.0)
    weekly_hours = st.number_input("Average Hours Worked Per Week", min_value=0.0, value=40.0)
    weeks_per_year = st.number_input("Weeks Worked Per Year", min_value=0.0, value=52.0)
    gross_pay = hourly_rate * weekly_hours * weeks_per_year

pay_frequency = st.selectbox("Pay Frequency", ["weekly", "biweekly", "semimonthly", "monthly"])
filing_status = st.selectbox("Filing Status", ["single", "married", "head"])
step_2_checked = st.checkbox("Step 2 Checkbox (Multiple Jobs)?")
dependents_amount = st.number_input("Dependent Claim Amount (Step 3)", min_value=0.0, value=0.0)
other_income = st.number_input("Other Income (Step 4a)", min_value=0.0, value=0.0)
deductions = st.number_input("Deductions (Step 4b)", min_value=0.0, value=0.0)
extra_withholding = st.number_input("Additional Withholding (Step 4c)", min_value=0.0, value=0.0)

# --- Frequency Map ---
frequency_map = {"weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12}

# --- Per-Pay-Period Percentage Method ---
def percentage_method_periodic(filing_status, gross_pay, pay_frequency):
    # Update this dictionary with the correct brackets and rates from Publication 15-T
    periodic_brackets = {
        "weekly": {
            "single": [
                (0, 87, 0.00, 0),  # Exempt bracket
                (88, 443, 0.10, 87),
                (444, 1538, 0.12, 443),
                (1539, 3596, 0.22, 1538),
                (3597, float('inf'), 0.24, 3596)
            ]
        },
        # Add other frequencies and filing statuses here
    }

    brackets = periodic_brackets[pay_frequency][filing_status]

    for b in brackets:
        if gross_pay <= b[1]:
            return (gross_pay - b[3]) * b[2]

    return 0.0

# --- Calculation Logic ---
def calculate():
    try:
        if calc_mode == "Estimate for single paycheck":
            taxable_income = gross_pay + other_income - deductions - (dependents_amount * 2000 / frequency_map[pay_frequency])
        else:
            taxable_income = gross_pay + other_income - deductions - (dependents_amount * 2000)

        taxable_income = max(taxable_income, 0)
        fed_withholding = percentage_method_periodic(filing_status, taxable_income, pay_frequency) + extra_withholding
        social_security = min(taxable_income, 147000) * 0.062 / frequency_map[pay_frequency]
        medicare = taxable_income * 0.0145 / frequency_map[pay_frequency]

        total_tax = fed_withholding + social_security + medicare
        net_pay = gross_pay - total_tax

        return {
            "Federal Withholding": round(fed_withholding, 2),
            "Social Security": round(social_security, 2),
            "Medicare": round(medicare, 2),
            "Net Pay": round(net_pay, 2)
        }
    except Exception as e:
        return {"Error": str(e)}

# --- Output ---
if st.button("Calculate"):
    result = calculate()
    st.subheader("Result:")
    for k, v in result.items():
        st.write(f"{k}: ${v}")
