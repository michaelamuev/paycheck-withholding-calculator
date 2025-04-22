import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Set Decimal precision
getcontext().prec = 28

# === CONSTANTS ===
STANDARD_DEDUCTION = {
    "single": Decimal('14600'),
    "married": Decimal('29200'),
    "head": Decimal('21900'),
}
DEPENDENT_CREDIT = Decimal('2000')

# FICA caps & rates
FICA_CAP = Decimal('168600')
SOCIAL_RATE = Decimal('0.062')
MEDICARE_RATE = Decimal('0.0145')

# Multiple jobs adjustment (Step 2)
MULTI_JOB_ADJUST = {
    "single": Decimal('8600'),
    "married": Decimal('12900'),
    "head": Decimal('8600'),
}

# Percentage-method brackets
BRACKETS = {
    "single": [
        {"min": Decimal('0'),      "base": Decimal('0'),      "rate": Decimal('0.10')},
        {"min": Decimal('16300'),  "base": Decimal('1630'),   "rate": Decimal('0.12')},
        {"min": Decimal('39500'),  "base": Decimal('4320'),   "rate": Decimal('0.22')},
        {"min": Decimal('110600'), "base": Decimal('10696'),  "rate": Decimal('0.24')},
        {"min": Decimal('217350'), "base": Decimal('34337'),  "rate": Decimal('0.32')},
        {"min": Decimal('400200'), "base": Decimal('78221'),  "rate": Decimal('0.35')},
        {"min": Decimal('503750'), "base": Decimal('111357'), "rate": Decimal('0.37')},
    ],
    "married": [
        {"min": Decimal('0'),      "base": Decimal('0'),      "rate": Decimal('0.10')},
        {"min": Decimal('26200'),  "base": Decimal('2620'),   "rate": Decimal('0.12')},
        {"min": Decimal('61750'),  "base": Decimal('8110'),   "rate": Decimal('0.22')},
        {"min": Decimal('115125'), "base": Decimal('25326'),  "rate": Decimal('0.24')},
        {"min": Decimal('206550'), "base": Decimal('62244'),  "rate": Decimal('0.32')},
        {"min": Decimal('258325'), "base": Decimal('105664'), "rate": Decimal('0.35')},
        {"min": Decimal('380200'), "base": Decimal('155682'), "rate": Decimal('0.37')},
    ],
    "head": [
        {"min": Decimal('0'),      "base": Decimal('0'),      "rate": Decimal('0.10')},
        {"min": Decimal('19225'),  "base": Decimal('1922.5'), "rate": Decimal('0.12')},
        {"min": Decimal('42500'),  "base": Decimal('5197.5'), "rate": Decimal('0.22')},
        {"min": Decimal('61200'),  "base": Decimal('11017.5'),"rate": Decimal('0.24')},
        {"min": Decimal('106925'), "base": Decimal('25501.5'),"rate": Decimal('0.32')},
        {"min": Decimal('132800'), "base": Decimal('46266.5'),"rate": Decimal('0.35')},
        {"min": Decimal('315625'), "base": Decimal('93157.5'),"rate": Decimal('0.37')},
    ],
}

# Periods per year
PERIODS = {
    "weekly": Decimal('52'),
    "biweekly": Decimal('26'),
    "semimonthly": Decimal('24'),
    "monthly": Decimal('12'),
}

# UTILS
def find_bracket(status: str, taxable: Decimal) -> dict:
    for b in reversed(BRACKETS[status]):
        if taxable >= b["min"]:
            return b
    return BRACKETS[status][0]


def annual_pct_tax(status: str, taxable: Decimal) -> Decimal:
    br = find_bracket(status, taxable)
    return br["base"] + (taxable - br["min"]) * br["rate"]

@st.cache_data
def calculate_taxes(
    gross: Decimal,
    status: str,
    multiple_jobs: bool,
    dependents: int,
    other_inc: Decimal,
    deducts: Decimal,
    extra_wh: Decimal,
    periods: Decimal,
    annual: bool,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    base = gross if annual else gross * periods
    taxable = base + other_inc - STANDARD_DEDUCTION[status] - deducts
    if not multiple_jobs:
        taxable -= MULTI_JOB_ADJUST[status]
    taxable = max(taxable, Decimal('0'))

    fed_annual = annual_pct_tax(status, taxable)
    fed_annual = max(fed_annual - DEPENDENT_CREDIT * dependents, Decimal('0'))
    fed_annual += extra_wh * periods

    fed = fed_annual if annual else fed_annual / periods

    ss_annual = min(base, FICA_CAP) * SOCIAL_RATE
    mi_annual = base * MEDICARE_RATE
    ss = ss_annual if annual else ss_annual / periods
    mi = mi_annual if annual else mi_annual / periods

    net = gross - fed - ss - mi

    def quantize(val: Decimal) -> Decimal:
        return val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return quantize(fed), quantize(ss), quantize(mi), quantize(net)

# STREAMLIT UI
st.set_page_config(page_title="Precision Withholding", page_icon="💸", layout="wide")
st.title("Precision Withholding Calculator (2024 Pub 15‑T)")

with st.sidebar:
    mode = st.radio("Mode", ["Single Paycheck", "Full Year"])
    status = st.selectbox("Filing Status", ["single", "married", "head"])
    annual = (mode == "Full Year")

    gross_val = st.number_input("Gross Amount ($)", value=1000.0 if not annual else 50000.0)
    gross = Decimal(str(gross_val))
    freq = st.selectbox("Frequency", list(PERIODS.keys()))
    periods = PERIODS[freq]

    st.markdown("---")
    multiple_jobs = st.checkbox("Multiple jobs? (Step 2)")
    dependents = st.number_input("Dependents (Step 3)", min_value=0, value=0)
    other_income = Decimal(str(st.number_input("Other income (annual)", value=0.0)))
    deductions = Decimal(str(st.number_input("Deductions (annual)", value=0.0)))
    extra_withholding = Decimal(str(st.number_input("Extra withholding per period", value=0.0)))

if st.button("Calculate"):
    fed, ss, mi, net = calculate_taxes(
        gross, status, multiple_jobs, dependents,
        other_income, deductions, extra_withholding,
        periods, annual
    )

    cols = st.columns(4)
    cols[0].metric("Federal Tax", f"${fed}")
    cols[1].metric("Social Security", f"${ss}")
    cols[2].metric("Medicare", f"${mi}")
    cols[3].metric("Net Pay", f"${net}")

    eff = (fed / gross) * (Decimal('1') if annual else periods)
    st.caption(f"Effective Federal Rate: {eff.quantize(Decimal('0.0001')):.2%}")
