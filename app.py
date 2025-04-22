import streamlit as st

# ─── App Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mike's Calculator 💸",
    page_icon="💸",
    layout="wide",
)
st.title("Mike’s Federal Withholding Calculator")
st.caption("Per‑Period Pub 15‑T Tables & Annual Percentage Method (2024)")

# ─── Embed Pub 15‑T Table 2 (per‑period) ────────────────────────────────────────
# Weekly brackets from IRS Pub 15‑T Table 2(a) for “Automated Payroll Systems”
_weekly = {
    "single": [
        (0,    88,   0.10,   0.00),
        (88,   443,  0.12,   8.80),
        (443,  1538, 0.22,  51.80),
        (1538, float("inf"), 0.24, 359.60),
    ],
    "married": [
        (0,    176,  0.10,    0.00),
        (176,  886,  0.12,   17.60),
        (886,  3076, 0.22,  103.52),
        (3076, float("inf"), 0.24, 716.08),
    ],
    "head": [
        (0,    129,  0.10,    0.00),
        (129,  598,  0.12,   12.90),
        (598,  1538, 0.22,   72.06),
        (1538, float("inf"), 0.24, 359.60),
    ],
}

# Build biweekly/semimonthly/monthly by scaling weekly thresholds
periodic_brackets = {
    "weekly":  _weekly,
    "biweekly": {
        status: [
            (low*2, high*2 if high!=float("inf") else float("inf"), rate, base*2)
            for (low, high, rate, base) in _weekly[status]
        ]
        for status in _weekly
    },
    "semimonthly": {
        status: [
            (low*(26/24), high*(26/24) if high!=float("inf") else float("inf"), rate, base*(26/24))
            for (low, high, rate, base) in _weekly[status]
        ]
        for status in _weekly
    },
    "monthly": {
        status: [
            (low*(52/12), high*(52/12) if high!=float("inf") else float("inf"), rate, base*(52/12))
            for (low, high, rate, base) in _weekly[status]
        ]
        for status in _weekly
    }
}

def lookup_periodic_withholding(status, freq, wages):
    """Returns federal withholding for one paycheck via Pub 15‑T Table 2."""
    for low, high, rate, base in periodic_brackets[freq][status]:
        if low < wages <= high:
            return round(base + (wages - low)*rate, 2)
    return 0.0

# ─── Annual Percentage‑Method Tables & Constants ─────────────────────────────
PCT_TABLES = {
    "single": [
        (0,       0.10,      0),
        (11600,   0.12,   1160),
        (47150,   0.22,   5146),
        (95375,   0.24,  16290),
        (182100,  0.32,  37104),
        (231250,  0.35,  52832),
        (578125,  0.37, 174238),
    ],
    "married":[
        (0,       0.10,      0),
        (23200,   0.12,   2320),
        (94300,   0.22,  10294),
        (190750,  0.24,  32580),
        (364200,  0.32,  74208),
        (462500,  0.35, 105664),
        (693750,  0.37, 186601),
    ],
    "head":   [
        (0,       0.10,      0),
        (17400,   0.12,   1740),
        (64700,   0.22,   7198),
        (95350,   0.24,  14678),
        (182100,  0.32,  35498),
        (231250,  0.35,  51226),
        (578100,  0.37, 172623),
    ],
}
STD_DEDUCTION    = {"single":14600, "married":29200, "head":21900}
DEPENDENT_CREDIT = 2000

def annual_pct_tax(status, taxable):
    """Compute annual federal tax via IRS Percentage Method (Table 1)."""
    for mn, rate, base in reversed(PCT_TABLES[status]):
        if taxable >= mn:
            return round(base + (taxable - mn)*rate, 2)
    return 0.0

# ─── Sidebar Inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Inputs")
    mode        = st.radio("Mode", ["Single Paycheck","Full Year"])
    is_annual   = (mode == "Full Year")
    if is_annual:
        inc_type = st.radio("Income Type", ["Salary","Hourly"])

    if is_annual:
        if inc_type=="Salary":
            gross_annual = st.number_input("Annual salary ($)", 0.0, 1e7, 50000.0)
        else:
            hr_rate  = st.number_input("Hourly rate ($)", 0.0, 1e4, 20.0)
            hrs_week = st.number_input("Hours per week", 0.0, 168.0, 40.0)
            gross_annual = hr_rate * hrs_week * 52.0
    else:
        gross_pay = st.number_input("Gross pay this period ($)", 0.0, 1e6, 1000.0)

    step2        = st.checkbox("Step 2: Multiple jobs?")  # implement later
    dependents   = st.number_input("Dependents (Step 3)", 0.0, 50.0, 0.0)
    other_inc    = st.number_input("Other income (4a)", 0.0, 1e6, 0.0)
    deducs       = st.number_input("Deductions (4b)",   0.0, 1e6, 0.0)
    extra_wd     = st.number_input("Extra withholding per check (4c)", 0.0, 1e5, 0.0)

    st.markdown("---")
    filing_status = st.selectbox("Filing status", list(PCT_TABLES.keys()))
    pay_freq      = st.selectbox("Pay frequency", list(periodic_brackets.keys()))
    periods       = {"weekly":52,"biweekly":26,"semimonthly":24,"monthly":12}[pay_freq]

# ─── Compute & Display Results ─────────────────────────────────────────────────
if st.button("Calculate"):
    # validate
    if not is_annual and gross_pay<=0:
        st.error("Enter a positive gross pay for this period.")
        st.stop()

    if is_annual:
        # Annual path
        adj    = gross_annual + other_inc - STD_DEDUCTION[filing_status] - deducs
        taxable= max(adj,0)
        fed_ann = annual_pct_tax(filing_status, taxable)
        fed_ann = max(fed_ann - dependents*DEPENDENT_CREDIT, 0)
        fed_ann += extra_wd * periods

        ss_ann = min(gross_annual,168600)*0.062
        med_ann= gross_annual *0.0145
        total  = fed_ann + ss_ann + med_ann
        net    = gross_annual - total

        st.subheader("Annual Estimate")
        st.write(f"Federal Withholding: ${fed_ann:,.2f}")
        st.write(f"Social Security:     ${ss_ann:,.2f}")
        st.write(f"Medicare:            ${med_ann:,.2f}")
        st.write(f"Net Pay:             ${net:,.2f}")

    else:
        # Single‑paycheck path
        # Prorate dependents & other annual items to per pay period
        dep_per = dependents*DEPENDENT_CREDIT/periods
        other_per= other_inc/periods
        ded_per  = deducs/periods

        taxable_pp = gross_pay + other_per - ded_per
        taxable_pp = max(taxable_pp,0)
        fed_pp     = lookup_periodic_withholding(filing_status,pay_freq,taxable_pp)
        fed_pp     = max(fed_pp - dep_per,0)
        fed_pp    += extra_wd

        ss_pp  = min(gross_pay*periods,168600)*0.062/periods
        med_pp = gross_pay*0.0145

        total_pp= fed_pp + ss_pp + med_pp
        net_pp  = gross_pay - total_pp

        st.subheader("Single‑Paycheck Estimate")
        st.write(f"Federal Withholding: ${fed_pp:,.2f}")
        st.write(f"Social Security:     ${ss_pp:,.2f}")
        st.write(f"Medicare:            ${med_pp:,.2f}")
        st.write(f"Net Pay:             ${net_pp:,.2f}")
