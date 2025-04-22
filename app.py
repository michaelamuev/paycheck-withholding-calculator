import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Mike's Calculator 💸",
    page_icon="💸",
    layout="centered"
)

# --- Header ---
st.title("Withholding Tool")
st.caption("Built with Python • Powered by IRS Percentage Method")

# --- Calculation Mode ---
mode = st.radio("Select calculation mode:", ["Estimate for single paycheck", "Estimate for full year"])
annual_calc = (mode == "Estimate for full year")

# --- Income Type (always asked, even if not used for single‑paycheck) ---
income_type = st.radio("Select income type:", ["Salary", "Hourly"])

# --- Gross Pay Inputs ---
if annual_calc:
    if income_type == "Salary":
        gross_annual = st.number_input("Enter annual salary ($)", min_value=0.0, value=0.0)
    else:
        hourly_rate = st.number_input("Enter hourly rate ($)", min_value=0.0, value=20.0)
        hours_per_week = st.number_input("Enter average weekly hours", min_value=0.0, value=40.0)
        gross_annual = hourly_rate * hours_per_week * 52.0
else:
    gross_pay = st.number_input("Enter gross pay this period ($)", min_value=0.0, value=0.0)

# --- Step 2 Checkbox (unused in notebook logic, but included for parity) ---
step_2_checked = st.checkbox("Is Step 2 checkbox selected?")

# --- Other Inputs ---
dependents_amount = st.number_input("Dependent claims amount (Step 3) ($)", min_value=0.0, value=0.0)
other_income      = st.number_input("Other income (Step 4a) ($)",   min_value=0.0, value=0.0)
deductions        = st.number_input("Deductions (Step 4b) ($)",     min_value=0.0, value=0.0)
extra_withholding = st.number_input("Additional withholding (Step 4c) ($)", min_value=0.0, value=0.0)

# --- Filing Status & Pay Frequency ---
filing_status = st.radio("Select filing status:", ["single", "married", "head"])
pay_frequency = st.radio("Select pay frequency:", ["weekly", "biweekly", "semimonthly", "monthly"])
periods_per_year_map = {"weekly":52, "biweekly":26, "semimonthly":24, "monthly":12}
periods_per_year = periods_per_year_map[pay_frequency]

# --- IRS Percentage Method Constants (from your notebook) ---
standard_deduction = {"single":14600, "married":29200, "head":21900}
tax_brackets = {
    "single": [(0, 0.10,   0), (11600, 0.12, 1160), (47150, 0.22, 5146)],
    "married":[(0, 0.10,   0), (23200, 0.12, 2320), (94300, 0.22,10294)],
    "head":   [(0, 0.10,   0), (17400, 0.12, 1740), (64700, 0.22, 7198)],
}

# --- Calculate & Display ---
if st.button("Calculate"):
    # align with your notebook logic
    if annual_calc:
        adj_income = gross_annual \
                     - other_income \
                     - standard_deduction[filing_status] \
                     - deductions
        adj_income = max(adj_income, 0)
        # find top bracket
        bracket = next(b for b in reversed(tax_brackets[filing_status]) if adj_income >= b[0])
        annual_fed_tax = bracket[2] + (adj_income - bracket[0]) * bracket[1]
        annual_fed_tax += extra_withholding * periods_per_year

        social_security = min(gross_annual, 168600) * 0.062
        medicare        = gross_annual * 0.0145

        total_tax  = annual_fed_tax + social_security + medicare
        net_annual = gross_annual - total_tax

        st.subheader("--- Annual Estimate ---")
        st.write(f"Annual Federal Withholding: ${annual_fed_tax:,.2f}")
        st.write(f"Annual Social Security:     ${social_security:,.2f}")
        st.write(f"Annual Medicare:           ${medicare:,.2f}")
        st.write(f"Estimated Net Pay:         ${net_annual:,.2f}")

    else:
        # single‑paycheck path
        gross_annual = gross_pay * periods_per_year
        adj_income = gross_annual \
                     - other_income \
                     - standard_deduction[filing_status] \
                     - deductions
        adj_income = max(adj_income, 0)
        bracket = next(b for b in reversed(tax_brackets[filing_status]) if adj_income >= b[0])
        annual_fed_tax = bracket[2] + (adj_income - bracket[0]) * bracket[1]
        annual_fed_tax += extra_withholding * periods_per_year

        per_period_fed_tax = annual_fed_tax / periods_per_year
        social_security    = min(gross_annual, 168600) * 0.062 / periods_per_year
        medicare           = gross_annual * 0.0145 / periods_per_year

        total_tax = per_period_fed_tax + social_security + medicare
        net_pay   = gross_pay - total_tax

        st.subheader("--- Paycheck Estimate ---")
        st.write(f"Federal Withholding: ${per_period_fed_tax:,.2f}")
        st.write(f"Social Security:     ${social_security:,.2f}")
        st.write(f"Medicare:            ${medicare:,.2f}")
        st.write(f"Net Pay:             ${net_pay:,.2f}")
