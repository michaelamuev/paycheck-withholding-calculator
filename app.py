import streamlit as st

# === CONSTANTS FROM 2024 PUB 15‑T ===

# Standard deduction by status
STANDARD_DEDUCTION = {
    "single": 14_600,
    "married": 29_200,
    "head": 21_900,
}

# Child & dependent credit (Step 3)
DEPENDENT_CREDIT = 2_000

# FICA caps & rates
FICA_CAP      = 168_600
SOCIAL_RATE   = 0.062
MEDICARE_RATE = 0.0145

# Annual percentage‑method brackets (STANDARD tables)
# Each list comes from the 2024 Pub 15‑T sec. 1 STANDARD Withholding Rate Schedules
BRACKETS = {
    "single": [
        {"min":     0, "rate": 0.10, "base":      0},
        {"min":  16_300, "rate": 0.12, "base":   1_630},
        {"min":  39_500, "rate": 0.22, "base":   4_320},
        {"min": 110_600, "rate": 0.24, "base":  10_696},
        {"min": 217_350, "rate": 0.32, "base":  34_337},
        {"min": 400_200, "rate": 0.35, "base":  78_221},
        {"min": 503_750, "rate": 0.37, "base": 111_357},
    ],
    "married": [
        {"min":     0, "rate": 0.10, "base":      0},
        {"min":  26_200, "rate": 0.12, "base":   2_620},
        {"min":  61_750, "rate": 0.22, "base":   8_110},
        {"min": 115_125, "rate": 0.24, "base":  25_326},
        {"min": 206_550, "rate": 0.32, "base":  62_244},
        {"min": 258_325, "rate": 0.35, "base": 105_664},
        {"min": 380_200, "rate": 0.37, "base": 155_682},
    ],
    "head": [
        {"min":     0, "rate": 0.10, "base":      0},
        {"min":  19_225, "rate": 0.12, "base":   1_922.5},
        {"min":  42_500, "rate": 0.22, "base":   5_197.5},
        {"min":  61_200, "rate": 0.24, "base":  11_017.5},
        {"min": 106_925, "rate": 0.32, "base":  25_501.5},
        {"min": 132_800, "rate": 0.35, "base":  46_266.5},
        {"min": 315_625, "rate": 0.37, "base":  93_157.5},
    ],
}

# Pay‑frequency → periods per year
PERIODS = {
    "weekly":      52,
    "biweekly":    26,
    "semimonthly": 24,
    "monthly":     12,
}

# === UTILS ===

def find_bracket(status, taxable):
    """Return the correct marginal bracket dict for a given annual taxable income."""
    for b in reversed(BRACKETS[status]):
        if taxable >= b["min"]:
            return b
    return BRACKETS[status][0]

def annual_pct_tax(status, taxable):
    """Annual federal tax via percentage method."""
    br = find_bracket(status, taxable)
    return br["base"] + (taxable - br["min"]) * br["rate"]

# === STREAMLIT UI ===

st.set_page_config(
    page_title="Mike’s Pub 15‑T Withholding",
    page_icon="💸",
    layout="wide",
)
st.title("Mike’s Federal Withholding Calculator")
st.caption("Using 2024 Pub 15‑T Percentage Method Tables")

# Sidebar inputs
with st.sidebar:
    mode = st.radio("Mode", ["Single Paycheck", "Full Year"])
    annual = (mode == "Full Year")

    if annual:
        income_type = st.radio("Income type", ["Salary", "Hourly"])
        if income_type == "Salary":
            gross_annual = st.number_input("Annual salary ($)", 0.0, 1_000_000.0, 50_000.0)
        else:
            rate = st.number_input("Hourly rate ($)", 0.0, 1_000.0, 20.0)
            hrs  = st.number_input("Hours per week", 0.0, 168.0, 40.0)
            gross_annual = rate * hrs * 52
    else:
        gross_pay = st.number_input("Gross pay this period ($)", 0.0, 50_000.0, 1_000.0)

    st.markdown("### W‑4 / Deductions")
    multiple_jobs = st.checkbox("Step 2: Multiple jobs?")
    dependents   = st.number_input("Dependents (Step 3)", 0.0, 10.0, 0.0)
    other_inc    = st.number_input("Other income (Step 4a)", 0.0, 50_000.0, 0.0)
    deducts      = st.number_input("Deductions (Step 4b)", 0.0, 50_000.0, 0.0)
    extra_wh     = st.number_input("Extra withholding (Step 4c)", 0.0, 5_000.0, 0.0)

    st.markdown("### Filing & Frequency")
    status    = st.selectbox("Filing status", ["single", "married", "head"])
    freq      = st.selectbox("Pay frequency", list(PERIODS.keys()))
    periods   = PERIODS[freq]

if st.button("Calculate"):
    # --- Annual path ---
    if annual:
        # Adjusted annual taxable income
        taxable = gross_annual + other_inc \
                  - STANDARD_DEDUCTION[status] \
                  - deducts
        taxable = max(taxable, 0)

        # Base federal using annual percentage method
        fed_ann = annual_pct_tax(status, taxable)

        # Subtract Step 3 credits
        fed_ann = max(fed_ann - dependents * DEPENDENT_CREDIT, 0)

        # Add extra withholding annualized
        fed_ann += extra_wh * periods

        # FICA
        ss  = min(gross_annual, FICA_CAP) * SOCIAL_RATE
        mi  = gross_annual * MEDICARE_RATE
        total_tax = fed_ann + ss + mi
        net = gross_annual - total_tax

        st.subheader("Annual Estimate")
        st.write(f"Federal Tax:        ${fed_ann:,.2f}")
        st.write(f"Social Security:    ${ss:,.2f}")
        st.write(f"Medicare:           ${mi:,.2f}")
        st.write(f"=== Net Pay:        ${net:,.2f}")

    # --- Single‑paycheck path ---
    else:
        # Scale Step 4(a)/(4b) per period
        per_other = other_inc / periods
        per_ded   = deducts / periods
        per_sd    = STANDARD_DEDUCTION[status] / periods
        per_cred  = dependents * DEPENDENT_CREDIT / periods

        # Adjusted annual equivalent taxable
        annual_equiv = (gross_pay + per_other - per_sd - per_ded) * periods
        annual_equiv = max(annual_equiv, 0)

        # Compute annual federal, then divide
        fed_ann = annual_pct_tax(status, annual_equiv)
        fed_ann = max(fed_ann - dependents * DEPENDENT_CREDIT, 0)
        fed_ann += extra_wh * periods
        fed_per = fed_ann / periods

        # FICA per period
        ss  = min(gross_pay * periods, FICA_CAP) * SOCIAL_RATE / periods
        mi  = gross_pay * MEDICARE_RATE

        total = fed_per + ss + mi
        net_pay = gross_pay - total

        st.subheader("Single‑Paycheck Estimate")
        st.write(f"Federal Tax:        ${fed_per:,.2f}")
        st.write(f"Social Security:    ${ss:,.2f}")
        st.write(f"Medicare:           ${mi:,.2f}")
        st.write(f"=== Net Pay:        ${net_pay:,.2f}")
