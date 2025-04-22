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
    weeks_per_year = st.number_input("Weeks Worked Per Year", min_value=0.0, value=52.0)  # Presumed default full year
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

# --- IRS Percentage Method ---
def percentage_method(filing_status, taxable_annual_wages):
    # Brackets could be updated with the current year's IRS tax brackets
    brackets = {
        "single": [(0, 0.10, 0), (11000, 0.12, 1100), (44725, 0.22, 5147), (95375, 0.24, 16290),
                   (182100, 0.32, 37104), (231250, 0.35, 52832), (578125, 0.37, 174238.25)],
        "married": [(0, 0.10, 0), (22000, 0.12, 2200), (89450, 0.22, 10294), (190750, 0.24, 32580),
                    (364200, 0.32, 74208), (462500, 0.35, 105664), (693750, 0.37, 186601.50)],
        "head": [(0, 0.10, 0), (15700, 0.12, 1570), (59850, 0.22, 6868), (95350, 0.24, 14678),
                 (182100, 0.32, 35498), (231250, 0.35, 51226), (578100, 0.37, 172623.50)]
    }
    for min_wage, rate, base_tax in reversed(brackets[filing_status]):
        if taxable_annual_wages > min_wage:
            return base_tax + (taxable_annual_wages - min_wage) * rate
    return 0.0

# --- Calculation Logic ---
def calculate():
    try:
        periods_per_year = frequency_map[pay_frequency]
        annual_gross = gross_pay if calc_mode == "Estimate for full year" else gross_pay * periods_per_year

        if step_2_checked:
            annual_gross += 8000

        taxable_income = annual_gross + other_income - deductions - (dependents_amount * 2000)
        taxable_income = max(taxable_income, 0)

        fed_withholding = percentage_method(filing_status, taxable_income) / periods_per_year
        fed_withholding += extra_withholding

        social_security = min(annual_gross, 147000) * 0.062 / periods_per_year
        medicare = annual_gross * 0.0145 / periods_per_year

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
