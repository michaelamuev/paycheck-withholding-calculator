import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 28

# === CONSTANTS ===
STANDARD_DEDUCTION = {
    "single": Decimal("14600"),
    "married": Decimal("29200"),
    "head": Decimal("21900"),
}

DEPENDENT_CREDIT = Decimal("2000")
FICA_CAP        = Decimal("168600")
SOCIAL_RATE     = Decimal("0.062")
MEDICARE_RATE   = Decimal("0.0145")

PERIODS = {
    "weekly":      Decimal("52"),
    "biweekly":    Decimal("26"),
    "semimonthly": Decimal("24"),
    "monthly":     Decimal("12"),
}

# === IRS PERCENTAGE‐METHOD TABLES (from Pub 15-T §1) ===
from decimal import Decimal

PERCENTAGE_METHOD_TABLES = {
    "weekly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("76"),   "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("291"),  "base": Decimal("21.50"),  "rate": Decimal("0.12")},
            {"min": Decimal("933"),  "base": Decimal("104.26"), "rate": Decimal("0.22")},
            {"min": Decimal("1822"), "base": Decimal("326.26"), "rate": Decimal("0.24")},
            {"min": Decimal("3692"), "base": Decimal("788.50"), "rate": Decimal("0.32")},
            {"min": Decimal("4600"), "base": Decimal("1086.90"),"rate": Decimal("0.35")},
            {"min": Decimal("11950"),"base": Decimal("3700.27"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("230"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("711"),  "base": Decimal("48.10"),  "rate": Decimal("0.12")},
            {"min": Decimal("1691"), "base": Decimal("165.98"), "rate": Decimal("0.22")},
            {"min": Decimal("3185"), "base": Decimal("488.38"), "rate": Decimal("0.24")},
            {"min": Decimal("5159"), "base": Decimal("955.10"), "rate": Decimal("0.32")},
            {"min": Decimal("6479"), "base": Decimal("1356.54"),"rate": Decimal("0.35")},
            {"min": Decimal("16942"),"base": Decimal("4627.58"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("145"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("457"),  "base": Decimal("31.20"),  "rate": Decimal("0.12")},
            {"min": Decimal("1034"), "base": Decimal("102.54"), "rate": Decimal("0.22")},
            {"min": Decimal("1611"), "base": Decimal("228.58"), "rate": Decimal("0.24")},
            {"min": Decimal("3117"), "base": Decimal("604.90"), "rate": Decimal("0.32")},
            {"min": Decimal("3933"), "base": Decimal("865.62"), "rate": Decimal("0.35")},
            {"min": Decimal("10225"),"base": Decimal("2950.56"),"rate": Decimal("0.37")},
        ],
    },

    "biweekly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("153"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("583"),  "base": Decimal("43"),    "rate": Decimal("0.12")},
            {"min": Decimal("1866"), "base": Decimal("208.52"),"rate": Decimal("0.22")},
            {"min": Decimal("3644"), "base": Decimal("652.52"),"rate": Decimal("0.24")},
            {"min": Decimal("7385"), "base": Decimal("1577.00"),"rate": Decimal("0.32")},
            {"min": Decimal("9200"), "base": Decimal("2173.80"),"rate": Decimal("0.35")},
            {"min": Decimal("23900"),"base": Decimal("7400.70"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("460"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("1423"), "base": Decimal("96.10"), "rate": Decimal("0.12")},
            {"min": Decimal("3382"), "base": Decimal("331.96"),"rate": Decimal("0.22")},
            {"min": Decimal("6370"), "base": Decimal("976.76"),"rate": Decimal("0.24")},
            {"min": Decimal("10318"),"base": Decimal("1910.20"),"rate": Decimal("0.32")},
            {"min": Decimal("12958"),"base": Decimal("2714.14"),"rate": Decimal("0.35")},
            {"min": Decimal("33884"),"base": Decimal("9255.38"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("289"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("913"),  "base": Decimal("62.50"), "rate": Decimal("0.12")},
            {"min": Decimal("2067"), "base": Decimal("205.20"),"rate": Decimal("0.22")},
            {"min": Decimal("3222"), "base": Decimal("457.16"),"rate": Decimal("0.24")},
            {"min": Decimal("6234"), "base": Decimal("1209.40"),"rate": Decimal("0.32")},
            {"min": Decimal("7866"), "base": Decimal("1731.24"),"rate": Decimal("0.35")},
            {"min": Decimal("20450"),"base": Decimal("5901.12"),"rate": Decimal("0.37")},
        ],
    },

    "semimonthly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("166"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("632"),  "base": Decimal("46.60"), "rate": Decimal("0.12")},
            {"min": Decimal("2022"), "base": Decimal("224.72"),"rate": Decimal("0.22")},
            {"min": Decimal("3953"), "base": Decimal("703.20"),"rate": Decimal("0.24")},
            {"min": Decimal("8015"), "base": Decimal("1697.84"),"rate": Decimal("0.32")},
            {"min": Decimal("9983"), "base": Decimal("2338.72"),"rate": Decimal("0.35")},
            {"min": Decimal("25900"),"base": Decimal("7963.20"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("500"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1543"), "base": Decimal("104.20"), "rate": Decimal("0.12")},
            {"min": Decimal("3662"), "base": Decimal("359.28"), "rate": Decimal("0.22")},
            {"min": Decimal("6890"), "base": Decimal("1056.88"),"rate": Decimal("0.24")},
            {"min": Decimal("11100"),"base": Decimal("2066.40"),"rate": Decimal("0.32")},
            {"min": Decimal("13908"),"base": Decimal("2935.36"),"rate": Decimal("0.35")},
            {"min": Decimal("36358"),"base": Decimal("10005.84"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),    "rate": Decimal("0.10")},
            {"min": Decimal("314"),  "base": Decimal("0"),    "rate": Decimal("0.10")},
            {"min": Decimal("995"),  "base": Decimal("68.60"),"rate": Decimal("0.12")},
            {"min": Decimal("2248"), "base": Decimal("225.60"),"rate": Decimal("0.22")},
            {"min": Decimal("3500"), "base": Decimal("502.48"),"rate": Decimal("0.24")},
            {"min": Decimal("6781"), "base": Decimal("1329.20"),"rate": Decimal("0.32")},
            {"min": Decimal("8550"), "base": Decimal("1900.36"),"rate": Decimal("0.35")},
            {"min": Decimal("22215"),"base": Decimal("6472.84"),"rate": Decimal("0.37")},
        ],
    },

    "monthly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("333"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1250"), "base": Decimal("90.40"),  "rate": Decimal("0.12")},
            {"min": Decimal("4043"), "base": Decimal("450.48"), "rate": Decimal("0.22")},
            {"min": Decimal("7900"), "base": Decimal("1405.44"),"rate": Decimal("0.24")},
            {"min": Decimal("16031"),"base": Decimal("3395.68"),"rate": Decimal("0.32")},
            {"min": Decimal("19967"),"base": Decimal("4677.84"),"rate": Decimal("0.35")},
            {"min": Decimal("51800"),"base": Decimal("15921.84"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1000"), "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("3087"), "base": Decimal("208.40"), "rate": Decimal("0.12")},
            {"min": Decimal("7325"), "base": Decimal("718.56"), "rate": Decimal("0.22")},
            {"min": Decimal("13781"),"base": Decimal("2113.76"),"rate": Decimal("0.24")},
            {"min": Decimal("22200"),"base": Decimal("4132.80"),"rate": Decimal("0.32")},
            {"min": Decimal("27817"),"base": Decimal("5870.72"),"rate": Decimal("0.35")},
            {"min": Decimal("72717"),"base": Decimal("19650.72"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("628"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("2000"), "base": Decimal("138.20"), "rate": Decimal("0.12")},
            {"min": Decimal("4525"), "base": Decimal("451.40"), "rate": Decimal("0.22")},
            {"min": Decimal("7034"), "base": Decimal("1004.96"),"rate": Decimal("0.24")},
            {"min": Decimal("13562"),"base": Decimal("2658.40"),"rate": Decimal("0.32")},
            {"min": Decimal("17098"),"base": Decimal("3800.72"),"rate": Decimal("0.35")},
            {"min": Decimal("44433"),"base": Decimal("12945.68"),"rate": Decimal("0.37")},
        ],
    },
}


# IRS_1040 annual brackets (for Full Year mode)
IRS_1040_BRACKETS = {
    "single": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("11600"),  "base": Decimal("1160"),   "rate": Decimal("0.12")},
        {"min": Decimal("47150"),  "base": Decimal("5426"),   "rate": Decimal("0.22")},
        {"min": Decimal("100525"), "base": Decimal("17206"),  "rate": Decimal("0.24")},
        {"min": Decimal("191950"), "base": Decimal("39146"),  "rate": Decimal("0.32")},
        {"min": Decimal("243725"), "base": Decimal("55682"),  "rate": Decimal("0.35")},
        {"min": Decimal("609350"), "base": Decimal("183647"), "rate": Decimal("0.37")},
    ],
    "married": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("23200"),  "base": Decimal("2320"),   "rate": Decimal("0.12")},
        {"min": Decimal("94300"),  "base": Decimal("8620"),   "rate": Decimal("0.22")},
        {"min": Decimal("201050"), "base": Decimal("29366"),  "rate": Decimal("0.24")},
        {"min": Decimal("383900"), "base": Decimal("74766"),  "rate": Decimal("0.32")},
        {"min": Decimal("487450"), "base": Decimal("105654"), "rate": Decimal("0.35")},
        {"min": Decimal("731200"), "base": Decimal("196669"), "rate": Decimal("0.37")},
    ],
    "head": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("16550"),  "base": Decimal("1655"),   "rate": Decimal("0.12")},
        {"min": Decimal("63100"),  "base": Decimal("7206"),   "rate": Decimal("0.22")},
        {"min": Decimal("100500"), "base": Decimal("15498"),  "rate": Decimal("0.24")},
        {"min": Decimal("191950"), "base": Decimal("37236"),  "rate": Decimal("0.32")},
        {"min": Decimal("243700"), "base": Decimal("53772"),  "rate": Decimal("0.35")},
        {"min": Decimal("609350"), "base": Decimal("183074"), "rate": Decimal("0.37")},
    ],
}

# === HELPERS ===

def find_bracket(tables, status, amount):
    rows = tables[status]
    for b in reversed(rows):
        if amount >= b["min"]:
            return b
    return rows[0]

def calculate_periodic_pct_tax(status, taxable, period):
    table = PERCENTAGE_METHOD_TABLES[period][status]
    br = find_bracket(table, status, taxable)
    return br["base"] + (taxable - br["min"]) * br["rate"]

def calculate_annual_pct_tax(status, taxable):
    br = find_bracket(IRS_1040_BRACKETS[status], status, taxable)
    return br["base"] + (taxable - br["min"]) * br["rate"]

@st.cache_data
def calculate_fed(
    gross: Decimal, status: str, multiple_jobs: bool, dependents: int,
    other_inc: Decimal, deducts: Decimal, extra_wh: Decimal,
    period: str, annual: bool
) -> Decimal:

    periods = PERIODS[period]
    base = gross if annual else gross * periods
    if multiple_jobs:
        # Add the statutory multiple-job adjustment
        adjust = {"single":Decimal("8600"), "married":Decimal("12900"), "head":Decimal("8600")}
        base += adjust[status]

    taxable = base + other_inc - STANDARD_DEDUCTION[status] - deducts
    taxable = max(taxable, Decimal("0"))

    if annual:
        fed_ann = calculate_annual_pct_tax(status, taxable)
    else:
        # convert to per-period taxable
        fed_ann = calculate_periodic_pct_tax(status, taxable/periods, period) * periods

    # subtract dependent credit
    dep_cr = DEPENDENT_CREDIT * dependents
    dep_cr = dep_cr if annual else dep_cr/periods
    fed_ann = max(fed_ann - dep_cr, Decimal("0"))

    fed_ann += extra_wh * (1 if annual else periods)
    fed = fed_ann if annual else fed_ann/periods

    return fed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calculate_ss(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    ss_ann = min(base, FICA_CAP) * SOCIAL_RATE
    return (ss_ann if annual else ss_ann/p).quantize(Decimal("0.01"), ROUND_HALF_UP)

def calculate_mi(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    mi_ann = base * MEDICARE_RATE
    return (mi_ann if annual else mi_ann/p).quantize(Decimal("0.01"), ROUND_HALF_UP)

def calculate_ny_withholding(
    annual_salary: float,
    pay_periods: int,
    calc_ny: bool,
    ny_status: str,
    ny_allow: int,
    ny_extra: float
) -> float:
    if not calc_ny:
        return 0.0
    taxable = max(annual_salary - ny_allow * 1000.0, 0.0)
    if ny_status == "Single":
        ny_brackets = [
            (0,8500,0.04,0),(8500,11700,0.045,340),(11700,13900,0.0525,484),
            (13900,21400,0.0585,600),(21400,80650,0.0625,1042),(80650,215400,0.0685,4842),
            (215400,1077550,0.0965,14220),(1077550,5000000,0.103,78990),(5000000,float('inf'),0.109,360491)
        ]
    else:
        ny_brackets = [
            (0,17150,0.04,0),(17150,23600,0.045,686),(23600,27900,0.0525,899),
            (27900,43000,0.0585,1116),(43000,161300,0.0625,2004),(161300,323200,0.0685,9051),
            (323200,2155350,0.0965,20797),(2155350,5000000,0.103,183010),(5000000,float('inf'),0.109,447441)
        ]
    tax = 0.0
    for low,high,rate,base_amt in ny_brackets:
        if low <= taxable <= high:
            tax = base_amt + rate * (taxable - low)
            break
    per_pay = tax / pay_periods + ny_extra
    return round(per_pay,2)

# === STREAMLIT UI ===
st.set_page_config(page_title="Paycheck Calculator", layout="wide")
st.sidebar.title("Inputs")

mode = st.sidebar.radio("Mode", ["Single Paycheck", "Full Year"])
annual = (mode=="Full Year")

if annual:
    gross_val = st.sidebar.number_input("Annual Gross Salary ($)", 60000.0, step=1000.0)
else:
    gross_val = st.sidebar.number_input("Gross Amount per Paycheck ($)", 1000.0, step=50.0)

period = st.sidebar.selectbox("Pay Frequency", ["weekly","biweekly","semimonthly","monthly"])
w4_type = st.sidebar.radio("Form W-4 Version", ["2020 or Later","2019 or Earlier"])
filing = st.sidebar.selectbox("Filing Status", ["single","married","head"])
step2  = st.sidebar.checkbox("Step 2: Multiple jobs / spouse works")
dependents = st.sidebar.number_input("Step 3: Dependents", min_value=0)
other_inc   = Decimal(str(st.sidebar.number_input("Step 4(a): Other income ($)", 0.0, step=100.0)))
deducts     = Decimal(str(st.sidebar.number_input("Step 4(b): Deductions over standard ($)", 0.0, step=100.0)))
extra_wh    = Decimal(str(st.sidebar.number_input("Step 4(c): Extra withholding/period ($)", 0.0, step=5.0)))

calc_ny  = st.sidebar.checkbox("Calculate NY State withholding?")
if calc_ny:
    ny_status = st.sidebar.selectbox("NY Filing Status", ["Single","Married"])
    ny_allow  = st.sidebar.number_input("NY allowances", min_value=0)
    ny_extra  = st.sidebar.number_input("NY extra withholding/period ($)", 0.0, step=5.0)
else:
    ny_status, ny_allow, ny_extra = None, 0, 0.0

if st.sidebar.button("Calculate"):
    gross = Decimal(str(gross_val))
    fed = calculate_fed(gross, filing, step2, dependents, other_inc, deducts, extra_wh, period, annual)
    ss  = calculate_ss(gross, period, annual)
    mi  = calculate_mi(gross, period, annual)
    net = (gross if not annual else gross/PERIODS[period]) - fed - ss - mi if not annual else gross - fed - ss - mi

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Federal Tax",      f"${fed:,.2f}")
    c2.metric("Social Security",  f"${ss:,.2f}")
    c3.metric("Medicare",         f"${mi:,.2f}")
    c4.metric("Net Pay",          f"${net:,.2f}")

    eff = (fed / (gross if not annual else gross/PERIODS[period]))
    st.caption(f"Effective Federal Rate: {eff:.2%}")

    if calc_ny:
        annual_sal = float(gross if annual else gross*PERIODS[period])
        pp = int(PERIODS[period])
        ny_tax = calculate_ny_withholding(annual_sal, pp, True, ny_status, int(ny_allow), float(ny_extra))
        st.write(f"**NY State Tax:** ${ny_tax:,.2f}")
