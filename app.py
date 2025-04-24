import random
import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP

IRS_TRIVIA = [
    "Did you know? The new 2024 W-4 no longer uses withholding allowances — you enter dollar amounts instead.",
    "Tip: If you have more than one job, checking Step 2 can prevent underwithholding later in the year.",
    "Fun fact: Publication 15-T was first introduced in 2005, but percentage-method tables go back much further!",
    "Remember: Your standard deduction (for 2024) is $14,600 if single, $29,200 if married filing jointly.",
    "Heads up: Any extra withholding you enter in Step 4(c) applies every pay period, so small amounts add up fast.",
    "IRS trivia: Form W-4P is for pensions and annuities, not your regular paycheck — don't mix them up!",
]


# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2024 Withholding (Pub 15-T)",
    page_icon="💸",
    layout="wide"
)
tip = random.choice(IRS_TRIVIA)
st.info(f"💡 **Tip of the Day:** {tip}")


# ─── Precision ─────────────────────────────────────────────────────────────────
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

# ─── CONSTANTS ─────────────────────────────────────────────────────────────────
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

# ─── PERCENTAGE-METHOD TABLES (Pub 15-T §1) ─────────────────────────────────────
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

# ─── ANNUAL IRS 1040 BRACKETS (Pub 1040) ────────────────────────────────────────
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

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def round_to_penny(amount: Decimal) -> Decimal:
    """Round to nearest penny using IRS rounding rules."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def find_bracket(table, status, amt):
    """Find the appropriate tax bracket with improved precision."""
    if amt < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    for row in reversed(table[status]):
        if amt >= row["min"]:
            return row
    return table[status][0]

def calculate_periodic_pct_tax(status, taxable, period):
    """Calculate periodic percentage tax with enhanced precision."""
    if taxable < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    # Round the taxable amount first (IRS Pub 15-T requirement)
    taxable = round_to_penny(taxable)
    
    row = find_bracket(PERCENTAGE_METHOD_TABLES[period], status, taxable)
    # Calculate tax using IRS method
    excess = round_to_penny(taxable - row["min"])
    tax = row["base"] + (excess * row["rate"])
    return round_to_penny(tax)

def calculate_annual_pct_tax(status, taxable):
    """Calculate annual percentage tax with enhanced precision."""
    if taxable < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    row = find_bracket(IRS_1040_BRACKETS, status, taxable)
    tax = row["base"] + (taxable - row["min"]) * row["rate"]
    return round_to_penny(tax)

@st.cache_data
def calculate_fed(
    gross: Decimal, status: str, multi: bool, deps: int,
    oth: Decimal, ded: Decimal, extra: Decimal,
    period: str, annual: bool
) -> Decimal:
    """Calculate federal withholding with improved precision and error handling."""
    try:
        # Input validation
        if gross < Decimal("0"):
            raise ValueError("Gross pay cannot be negative")
        if deps < 0:
            raise ValueError("Number of dependents cannot be negative")
        if oth < Decimal("0"):
            raise ValueError("Other income cannot be negative")
        if ded < Decimal("0"):
            raise ValueError("Deductions cannot be negative")
        if extra < Decimal("0"):
            raise ValueError("Extra withholding cannot be negative")
            
        p = PERIODS[period]
        
        # For periodic calculations, work with the periodic amount directly
        if not annual:
            base = gross
            other_periodic = oth / p
            ded_periodic = ded / p
        else:
            base = gross / p
            other_periodic = oth / p
            ded_periodic = ded / p
            
        # Handle multiple jobs adjustment (applied to periodic amount)
        if multi:
            multi_adjustment = {
                "single": Decimal("8600"),
                "married": Decimal("12900"),
                "head": Decimal("8600")
            }[status]
            base += multi_adjustment / p
            
        # Calculate periodic taxable income
        standard_ded_periodic = STANDARD_DEDUCTION[status] / p
        taxable = max(
            base + other_periodic - standard_ded_periodic - ded_periodic,
            Decimal("0")
        )
        
        # Calculate periodic tax
        fed = calculate_periodic_pct_tax(status, taxable, period)
        
        # Apply dependent credit (periodic)
        credit = (DEPENDENT_CREDIT * Decimal(str(deps))) / p
        fed = max(fed - credit, Decimal("0"))
        
        # Add extra withholding
        fed += extra
        
        # Convert to annual if needed
        if annual:
            fed *= p
            
        return round_to_penny(fed)
        
    except Exception as e:
        st.error(f"Error calculating federal tax: {str(e)}")
        return Decimal("0")

def calculate_ss(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    ss_ann = min(base, FICA_CAP) * SOCIAL_RATE
    return (ss_ann if annual else ss_ann / p).quantize(Decimal("0.01"), ROUND_HALF_UP)

def calculate_mi(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    mi_ann = base * MEDICARE_RATE
    return (mi_ann if annual else mi_ann / p).quantize(Decimal("0.01"), ROUND_HALF_UP)

def calculate_ny_withholding(annual_salary, pay_periods, calc_ny, ny_status, ny_allow, ny_extra):
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
    for low, high, rate, base_amt in ny_brackets:
        if low <= taxable <= high:
            tax = base_amt + rate * (taxable - low)
            break
    return round(tax / pay_periods + ny_extra, 2)

# ─── SIDEBAR UI ────────────────────────────────────────────────────────────────
st.sidebar.title("Inputs")
mode = st.sidebar.radio("Mode", ["Single Paycheck", "Full Year"])
annual = mode == "Full Year"

if annual:
    gross_val = st.sidebar.number_input(
        "Annual Gross Salary ($)",
        value=60000.0,
        step=1000.0,
        min_value=0.0,
        help="Enter your annual gross salary"
    )
else:
    gross_val = st.sidebar.number_input(
        "Gross Amount per Paycheck ($)",
        value=1000.0,
        step=50.0,
        min_value=0.0,
        help="Enter your gross pay per paycheck"
    )

period = st.sidebar.selectbox("Pay Frequency", ["weekly","biweekly","semimonthly","monthly"])
multi  = st.sidebar.checkbox("Step 2: Multiple jobs / spouse works")
deps   = st.sidebar.number_input("Step 3: Dependents", min_value=0, value=0)
oth    = Decimal(str(st.sidebar.number_input("Step 4(a): Other income ($)", value=0.0, step=100.0)))
ded    = Decimal(str(st.sidebar.number_input("Step 4(b): Deductions over standard ($)", value=0.0, step=100.0)))
extra  = Decimal(str(st.sidebar.number_input("Step 4(c): Extra withholding per period ($)", value=0.0, step=5.0)))

# Filing status must match lowercase keys:
filing = st.sidebar.selectbox("Filing Status (Step 1c)", ["single","married","head"])

calc_ny = st.sidebar.checkbox("Calculate NY State withholding?")
if calc_ny:
    ny_status = st.sidebar.selectbox("NY Filing Status", ["Single","Married"])
    ny_allow  = st.sidebar.number_input("NY allowances", min_value=0, value=0)
    ny_extra  = st.sidebar.number_input("NY extra withholding per period ($)", value=0.0, step=5.0)
else:
    ny_status, ny_allow, ny_extra = None, 0, 0.0

# ─── MAIN AREA ────────────────────────────────────────────────────────────────
st.title("2024 Paycheck Tax Withholding Calculator")
st.markdown("This uses IRS Publication 15-T percentage and annual 1040 tables for federal withholding, plus optional NY state withholding.")

if st.sidebar.button("Calculate"):
    if gross_val > 250_000:
        st.error("who we lying to 👀")
        st.stop()
    # now the real work begins
    gross = Decimal(str(gross_val))
    fed = calculate_fed(gross, filing, multi, deps, oth, ded, extra, period, annual)
    ss  = calculate_ss(gross, period, annual)
    mi  = calculate_mi(gross, period, annual)
    if annual:
        net = gross - fed - ss - mi
        per_pay = gross / PERIODS[period]
    else:
        per_pay = gross
        net = per_pay - fed - ss - mi

    cols = st.columns(4)
    cols[0].metric("Federal Tax",     f"${fed:,.2f}")
    cols[1].metric("Social Security", f"${ss:,.2f}")
    cols[2].metric("Medicare",        f"${mi:,.2f}")
    cols[3].metric("Net Pay",         f"${net:,.2f}")

         # ─── NY STATE WITHHOLDING ───────────────────────────
    if calc_ny:
        annual_sal = float(gross if annual else gross * PERIODS[period])
        pp = int(PERIODS[period])
        ny_tax = calculate_ny_withholding(
            annual_sal,
            pp,
            True,
            ny_status,
            int(ny_allow),
            float(ny_extra),
        )
        st.write(f"**NY State Tax:** ${ny_tax:,.2f}")








# … after you display results …

# ─── Feedback Section ─────────────────────────────────────────────────────────
with st.expander("💬 Have feedback or suggestions?"):
    name = st.text_input(
        "Your name (optional)",
        placeholder="If you'd like to be credited…"
    )
    feedback = st.text_area(
        "Leave any comments, tweaks, or general feedback here:",
        placeholder="Type away…",
        height=100,
    )
    if st.button("Submit Feedback"):
        if not feedback.strip():
            st.warning("Oops—you didn't write anything!")
        else:
            # Acknowledge
            st.success("Thanks for your feedback! 🙏")
            st.balloons()
            # Save to your server for review
            with open("user_feedback.log", "a") as f:
                who = name.strip() or "Anonymous"
                f.write(f"{who}: {feedback.replace(chr(10), ' ')}\n---\n")

# ─── Admin: View All Feedback ─────────────────────────────────────────────────
if st.sidebar.checkbox("🔒 Show Feedback Log (admin)"):
    try:
        with open("user_feedback.log", "r") as f:
            log = f.read().strip()
        if log:
            st.text_area("User Feedback Log", log, height=300)
        else:
            st.info("No feedback yet.")
    except FileNotFoundError:
        st.warning("No feedback log found.")


