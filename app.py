import streamlit as st

# === TAX CONFIG (2024 Pub 15‑T Percentage Method) ===
TAX_CONFIG = {
    "standard_deduction": {"single": 14600, "married": 29200, "head": 21900},
    "dependent_credit": 2000,
    "brackets": {
        "single": [
            {"min": 0,      "rate": 0.10, "base":      0},
            {"min": 11600,  "rate": 0.12, "base":   1160},
            {"min": 47150,  "rate": 0.22, "base":   5146},
            {"min": 95375,  "rate": 0.24, "base":  16290},
            {"min": 182100, "rate": 0.32, "base":  37104},
            {"min": 231250, "rate": 0.35, "base":  52832},
            {"min": 578125, "rate": 0.37, "base": 174238},
        ],
        "married": [
            {"min": 0,      "rate": 0.10, "base":    0},
            {"min": 23200,  "rate": 0.12, "base":  2320},
            {"min": 94300,  "rate": 0.22, "base": 10294},
            {"min": 190750, "rate": 0.24, "base": 32580},
            {"min": 364200, "rate": 0.32, "base": 74208},
            {"min": 462500, "rate": 0.35, "base":105664},
            {"min": 693750, "rate": 0.37, "base":186601},
        ],
        "head": [
            {"min": 0,      "rate": 0.10, "base":    0},
            {"min": 17400,  "rate": 0.12, "base":  1740},
            {"min": 64700,  "rate": 0.22, "base":  7198},
            {"min": 95350,  "rate": 0.24, "base": 14678},
            {"min": 182100, "rate": 0.32, "base": 35498},
            {"min": 231250, "rate": 0.35, "base": 51226},
            {"min": 578100, "rate": 0.37, "base":172623},
        ],
    }
}

FREQ_MAP = {"weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12}


# === UTILS ===
def find_bracket(filing_status, taxable):
    """Return the marginal bracket (base, rate, min) for given taxable income."""
    for b in reversed(TAX_CONFIG["brackets"][filing_status]):
        if taxable >= b["min"]:
            return b
    return TAX_CONFIG["brackets"][filing_status][0]


def compute_percent_method(taxable):
    """Compute annual federal tax via percentage method given taxable income and filing_status."""
    bracket = find_bracket(filing_status, taxable)
    return bracket["base"] + (taxable - bracket["min"]) * bracket["rate"]


# === UI LAYOUT ===
st.set_page_config(page_title="Mike's Calculator 💸", page_icon="💸", layout="wide")
st.title("Withholding Tool — 2024 Earnings")
st.write("Built with Python • IRS Pub 15‑T Percentage Method")

with st.sidebar:
    st.header("Inputs")
    # Mode
    mode = st.radio("Calculation mode", ["Single Paycheck", "Full Year"])
    annual = (mode == "Full Year")

    # Income type
    if annual:
        income_type = st.radio("Income type", ["Salary", "Hourly"])
    else:
        income_type = "Salary"  # unneeded but defined

    # Gross pay
    if annual:
        if income_type == "Salary":
            gross_annual = st.number_input(
                "Annual salary ($)",
                min_value=0.0,
                value=50000.0,
                help="Total gross pay for the year."
            )
        else:
            hourly_rate = st.number_input(
                "Hourly rate ($)",
                min_value=0.0,
                value=20.0,
                help="Before-tax hourly rate."
            )
            hours_per_week = st.number_input(
                "Hours per week",
                min_value=0.0,
                value=40.0,
                help="Average hours worked each week."
            )
            gross_annual = hourly_rate * hours_per_week * 52
    else:
        gross_pay = st.number_input(
            "Gross pay this period ($)",
            min_value=0.0,
            value=1000.0,
            help="Gross pay for this check."
        )

    # W‑4 fields
    st.subheader("W‑4 / Deductions")
    step_2_checked = st.checkbox(
        "Step 2: Multiple jobs?",
        help="If checked, increases withholding (not yet implemented)."
    )
    dependents_amount = st.number_input(
        "Dependent claims (Step 3)",
        min_value=0.0,
        value=0.0,
        help="$2,000 tax credit per dependent."
    )
    other_income = st.number_input(
        "Other income (Step 4a)",
        min_value=0.0,
        value=0.0,
        help="Annual other income added to wages."
    )
    deductions = st.number_input(
        "Deductions (Step 4b)",
        min_value=0.0,
        value=0.0,
        help="Annual deductions reducing taxable income."
    )
    extra_withholding = st.number_input(
        "Extra withholding (Step 4c) per check",
        min_value=0.0,
        value=0.0,
        help="Additional tax per paycheck."
    )

    # Filing & frequency
    st.subheader("Filing & Frequency")
    filing_status = st.selectbox("Filing status", list(TAX_CONFIG["brackets"].keys()))
    pay_freq = st.selectbox("Pay frequency", list(FREQ_MAP.keys()))
    periods = FREQ_MAP[pay_freq]


# === CALCULATE & SHOW RESULTS ===
if st.button("Calculate"):
    # Validate
    if not annual and gross_pay == 0:
        st.error("Enter some gross pay for this period.")
        st.stop()

    # Compute taxable income
    if annual:
        # full year
        adj_income = gross_annual + other_income - TAX_CONFIG["standard_deduction"][filing_status] - deductions
        taxable = max(adj_income, 0)
        fed_annual = compute_percent_method(taxable)
        # dependent credit
        fed_annual = max(fed_annual - dependents_amount * TAX_CONFIG["dependent_credit"], 0)
        # extra withholding annualized
        fed_annual += extra_withholding * periods
        # FICA
        ss_annual = min(gross_annual, 168600) * 0.062
        medicare_annual = gross_annual * 0.0145
        total_tax = fed_annual + ss_annual + medicare_annual
        net_annual = gross_annual - total_tax

        st.subheader("Annual Estimate")
        st.write(f"Federal Tax:        ${fed_annual:,.2f}")
        st.write(f"Social Security:    ${ss_annual:,.2f}")
        st.write(f"Medicare:           ${medicare_annual:,.2f}")
        st.write(f"=== Net Pay:        ${net_annual:,.2f}")

    else:
        # single paycheck
        per_sd = TAX_CONFIG["standard_deduction"][filing_status] / periods
        per_other = other_income / periods
        per_ded = deductions / periods
        per_credit = dependents_amount * TAX_CONFIG["dependent_credit"] / periods

        taxable = gross_pay + per_other - per_sd - per_ded
        taxable = max(taxable, 0)
        fed = compute_percent_method(taxable)
        fed = max(fed - per_credit, 0)
        fed += extra_withholding

        ss = min(gross_pay * periods, 168600) * 0.062 / periods
        medicare = gross_pay * 0.0145

        total_tax = fed + ss + medicare
        net = gross_pay - total_tax

        st.subheader("Single‑Paycheck Estimate")
        st.write(f"Federal Tax:        ${fed:,.2f}")
        st.write(f"Social Security:    ${ss:,.2f}")
        st.write(f"Medicare:           ${medicare:,.2f}")
        st.write(f"=== Net Pay:        ${net:,.2f}")
