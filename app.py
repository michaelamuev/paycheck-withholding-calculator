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
if calc_mode == "Estimate for single paycheck":
    gross_pay = st.number_input("Gross Pay This Period ($)", min_value=0.0, value=0.0)
else:
    if income_type == "Salary":
        gross_pay = st.number_input("Annual Salary ($)", min_value=0.0, value=0.0)
    else:
        hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=20.0)
        weekly_hours = st.number_input("Average Hours Worked Per Week", min_value=0.0, value=40.0)
        weeks_per_year = st.number_input("Weeks Worked Per Year", min_value=0.0, value=0.0)
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
    brackets = {
        "single": [
            (0, 0.10, 0),
            (11000, 0.12, 1100),
            (44725, 0.22, 5147),
            (95375, 0.24, 16290),
            (182100, 0.32, 37104),
            (231250, 0.35, 52832),
            (578125, 0.37, 174238.25)
        ],
        "married": [
            (0, 0.10, 0),
            (22000, 0.12, 2200),
            (89450, 0.22, 10294),
            (190750, 0.24, 32580),
            (364200, 0.32, 74208),
            (462500, 0.35, 105664),
            (693750, 0.37, 186601.50)
        ],
        "head": [
            (0, 0.10, 0),
            (15700, 0.12, 1570),
            (59850, 0.22, 6868),
            (95350, 0.24, 14678),
            (182100, 0.32, 35498),
            (231250, 0.35, 51226),
            (578100, 0.37, 172623.50)
        ]
    }

    for i in range(len(brackets[filing_status]) - 1, -1, -1):
        min_wage, rate, base_tax = brackets[filing_status][i]
        if taxable_annual_wages > min_wage:
            return base_tax + (taxable_annual_wages - min_wage) * rate
    return 0.0








# --- Per-Pay-Period Percentage Method ---
def percentage_method_periodic(filing_status, gross_pay, pay_frequency):
    # 2024 IRS Weekly Percentage Brackets (simplified for now)
    periodic_brackets = {
        "weekly": {
            "single": [
                (88, 0.00, 0),  # No withholding under $88
                (89, 443, 0.10, 88),
                (444, 1538, 0.12, 443),
                (1539, 3596, 0.22, 1538),
                (3597, float('inf'), 0.24, 3596)
            ]
        }
        # Add biweekly/semimonthly/monthly if needed later
    }

    brackets = periodic_brackets[pay_frequency][filing_status]

    for b in brackets:
        if len(b) == 3 and gross_pay <= b[0]:  # Exempt range
            return 0.0
        elif len(b) == 4 and gross_pay > b[0] and gross_pay <= b[1]:
            return (gross_pay - b[3]) * b[2]

    return 0.0









# --- Calculation Logic ---
def calculate():
    try:
        periods_per_year = frequency_map[pay_frequency]

        if calc_mode == "Estimate for single paycheck":
            # No annualization here
            taxable_income = gross_pay + other_income - deductions - (dependents_amount * 2000 / periods_per_year)
            taxable_income = max(taxable_income, 0)
            fed_withholding = percentage_method_periodic(filing_status, taxable_income, pay_frequency)
            fed_withholding += extra_withholding

            # FICA for single paycheck
            social_security = min(gross_pay, 168600 / periods_per_year) * 0.062
            medicare = gross_pay * 0.0145

            total_tax = fed_withholding + social_security + medicare
            net_pay = gross_pay - total_tax

        else:
            # Annual mode
            annual_gross = gross_pay * periods_per_year if income_type == "Hourly" else gross_pay

            if step_2_checked:
                annual_gross += 8000

            taxable_income = annual_gross + other_income - deductions - (dependents_amount * 2000)
            taxable_income = max(taxable_income, 0)

            fed_annual = percentage_method(filing_status, taxable_income)
            fed_withholding = fed_annual / periods_per_year
            fed_withholding += extra_withholding * periods_per_year

            # FICA annualized
            social_security = min(annual_gross, 168600) * 0.062 / periods_per_year
            medicare = annual_gross * 0.0145 / periods_per_year

            total_tax = fed_withholding + social_security + medicare
            net_pay = annual_gross / periods_per_year - total_tax

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
