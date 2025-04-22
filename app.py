import streamlit as st

# === CONSTANTS FROM 2024 PUB 15-T ===
STANDARD_DEDUCTION = {
    "single": 14600,
    "married": 29200,
    "head": 21900,
}
DEPENDENT_CREDIT = 2000

# FICA caps & rates
FICA_CAP      = 168600
SOCIAL_RATE   = 0.062
MEDICARE_RATE = 0.0145

# Multiple jobs adjustment (Step 2)
MULTI_JOB_ADJUST = {
    "single": 8600,
    "married": 12900,
    "head": 8600,
}

# Annual percentage-method brackets (Standard tables)
BRACKETS = {
    "single": [
        {"min": 0,     "base":    0,     "rate": 0.10},
        {"min": 16300, "base": 1630,     "rate": 0.12},
        {"min": 39500, "base": 4320,     "rate": 0.22},
        {"min": 110600,"base":10696,     "rate": 0.24},
        {"min": 217350,"base":34337,     "rate": 0.32},
        {"min": 400200,"base":78221,     "rate": 0.35},
        {"min": 503750,"base":111357,    "rate": 0.37},
    ],
    "married": [
        {"min": 0,     "base":    0,     "rate": 0.10},
        {"min": 26200, "base": 2620,     "rate": 0.12},
        {"min": 61750, "base": 8110,     "rate": 0.22},
        {"min": 115125,"base":25326,     "rate": 0.24},
        {"min": 206550,"base":62244,     "rate": 0.32},
        {"min": 258325,"base":105664,    "rate": 0.35},
        {"min": 380200,"base":155682,    "rate": 0.37},
    ],
    "head": [
        {"min": 0,     "base":    0,     "rate": 0.10},
        {"min": 19225, "base": 1922.5,   "rate": 0.12},
        {"min": 42500, "base": 5197.5,   "rate": 0.22},
        {"min": 61200, "base":11017.5,   "rate": 0.24},
        {"min": 106925,"base":25501.5,   "rate": 0.32},
        {"min": 132800,"base":46266.5,   "rate": 0.35},
        {"min": 315625,"base":93157.5,   "rate": 0.37},
    ],
}

# Pay-frequency → periods per year
PERIODS = {
    "weekly":      52,
    "biweekly":    26,
    "semimonthly": 24,
    "monthly":     12,
}

# UTILS
def find_bracket(status, taxable):
    """Return the correct marginal bracket for a given annual taxable income."""
    for b in reversed(BRACKETS[status]):
        if taxable >= b["min"]:
            return b
    return BRACKETS[status][0]

def annual_pct_tax(status, taxable):
    """Annual federal tax via percentage method."""
    br = find_bracket(status, taxable)
    return br["base"] + (taxable - br["min"]) * br["rate"]

# STREAMLIT UI
st.set_page_config(
    page_title="Accurate Federal Withholding Calculator",
    page_icon="💸",
    layout="wide",
)
st.title("Accurate Federal Withholding Calculator (2024 Pub 15-T)")
st.caption("Using Percentage Method Tables for Automated Payroll)

with st.sidebar:
    st.header("Inputs")
    mode = st.radio("Mode", ["Single Paycheck", "Full Year"])
    annual = (mode == "Full Year")
    if annual:
        gross_annual = st.number_input("Gross annual amount ($)", 0.0, 1_000_000.0, 50000.0)
    else:
        gross_pay = st.number_input("Gross pay this period ($)", 0.0, 100000.0, 1000.0)

    st.markdown("### W-4 Information")
    multiple_jobs = st.checkbox("Multiple jobs? (Step 2 checkbox)")
    dependents   = st.number_input("Dependents (Step 3)", 0, 20, 0)
    other_inc    = st.number_input("Other income (annual, Step 4a)", 0.0, 100000.0, 0.0)
    deducts      = st.number_input("Deductions (annual, Step 4b)", 0.0, 100000.0, 0.0)
    extra_wh     = st.number_input("Extra withholding per period (Step 4c)", 0.0, 10000.0, 0.0)

    st.markdown("### Filing & Frequency")
    status = st.selectbox("Filing status", ["single", "married", "head"])
    freq   = st.selectbox("Pay frequency", list(PERIODS.keys()))
    periods = PERIODS[freq]

if st.button("Calculate"):
    if annual:
        # Adjusted annual taxable
        adj_taxable = gross_annual + other_inc - STANDARD_DEDUCTION[status] - deducts
        if not multiple_jobs:
            adj_taxable -= MULTI_JOB_ADJUST[status]
        adj_taxable = max(adj_taxable, 0.0)

        # Federal annual
        fed_ann = annual_pct_tax(status, adj_taxable)
        fed_ann = max(fed_ann - dependents * DEPENDENT_CREDIT, 0.0)
        fed_ann += extra_wh * periods

        # FICA/Medicare
        ss = min(gross_annual, FICA_CAP) * SOCIAL_RATE
        mi = gross_annual * MEDICARE_RATE
        total_tax = fed_ann + ss + mi
        net = gross_annual - total_tax

        st.subheader("Annual Estimate")
        st.write(f"Federal Tax:       ${fed_ann:,.2f}")
        st.write(f"Social Security:   ${ss:,.2f}")
        st.write(f"Medicare:          ${mi:,.2f}")
        st.write(f"Net Take-Home:     ${net:,.2f}")

    else:
        # Equivalent annual
        annual_equiv = gross_pay * periods + other_inc - STANDARD_DEDUCTION[status] - deducts
        if not multiple_jobs:
            annual_equiv -= MULTI_JOB_ADJUST[status]
        annual_equiv = max(annual_equiv, 0.0)

        fed_ann = annual_pct_tax(status, annual_equiv)
        fed_ann = max(fed_ann - dependents * DEPENDENT_CREDIT, 0.0)
        fed_ann += extra_wh * periods
        fed_per = fed_ann / periods

        ss = min(gross_pay * periods, FICA_CAP) * SOCIAL_RATE / periods
        mi = gross_pay * MEDICARE_RATE
        total = fed_per + ss + mi
        net_pay = gross_pay - total

        st.subheader("Single-Paycheck Estimate")
        st.write(f"Federal Tax:       ${fed_per:,.2f}")
        st.write(f"Social Security:   ${ss:,.2f}")
        st.write(f"Medicare:          ${mi:,.2f}")
        st.write(f"Net Pay:           ${net_pay:,.2f}")
