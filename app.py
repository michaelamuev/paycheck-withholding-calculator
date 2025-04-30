import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Required for Streamlit
from decimal import Decimal, getcontext, ROUND_HALF_UP
import numpy as np
import pandas as pd

# Import visualization functions directly from the file
try:
    from tax_visualizations import (
        create_tax_breakdown_pie,
        create_tax_comparison_bar,
        create_annual_projection,
        create_ny_tax_breakdown,
        create_total_tax_pie
    )
except ImportError:
    # If import fails, use the functions directly from the current file
    def create_tax_breakdown_pie(fed: Decimal, ss: Decimal, mi: Decimal, net: Decimal):
        """Create a pie chart showing tax breakdown."""
        plt.figure(figsize=(10, 8))
        values = [float(net), float(fed), float(ss), float(mi)]
        labels = ['Take Home Pay', 'Federal Tax', 'Social Security', 'Medicare']
        colors = ['#66bb6a', '#ef5350', '#42a5f5', '#ffee58']
        
        plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Your Paycheck Breakdown')
        return plt

    def create_tax_comparison_bar(fed: Decimal, ss: Decimal, mi: Decimal):
        """Create a bar chart comparing tax components."""
        plt.figure(figsize=(10, 6))
        taxes = ['Federal Tax', 'Social Security', 'Medicare']
        amounts = [float(fed), float(ss), float(mi)]
        colors = ['#ef5350', '#42a5f5', '#ffee58']
        
        plt.bar(taxes, amounts, color=colors)
        plt.title('Tax Components Comparison')
        plt.ylabel('Amount ($)')
        
        for i, v in enumerate(amounts):
            plt.text(i, v, f'${v:,.2f}', ha='center', va='bottom')
        
        return plt

    def create_annual_projection(amount: Decimal, period: str):
        """Create a line chart showing annual projection."""
        periods_map = {
            'weekly': 52,
            'biweekly': 26,
            'semimonthly': 24,
            'monthly': 12
        }
        
        periods = list(range(1, periods_map[period] + 1))
        amounts = [float(amount) * i for i in periods]
        
        plt.figure(figsize=(12, 6))
        plt.plot(periods, amounts, marker='o')
        plt.title(f'Annual Projection (Based on {period.title()} Pay)')
        plt.xlabel('Pay Period')
        plt.ylabel('Cumulative Amount ($)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        return plt

    def create_ny_tax_breakdown(state_tax: Decimal, nyc_tax: Decimal, yonkers_tax: Decimal):
        """Create a bar chart for NY tax components."""
        plt.figure(figsize=(10, 6))
        taxes = ['State Tax', 'NYC Tax', 'Yonkers Tax']
        amounts = [float(state_tax), float(nyc_tax), float(yonkers_tax)]
        colors = ['#66bb6a', '#42a5f5', '#ffee58']
        
        plt.bar(taxes, amounts, color=colors)
        plt.title('New York Tax Components')
        plt.ylabel('Amount ($)')
        
        for i, v in enumerate(amounts):
            plt.text(i, v, f'${v:,.2f}', ha='center', va='bottom')
        
        return plt

    def create_total_tax_pie(fed: Decimal, ss: Decimal, mi: Decimal, state_tax: Decimal, 
                            nyc_tax: Decimal, yonkers_tax: Decimal, net: Decimal):
        """Create a pie chart showing all tax components including NY taxes."""
        plt.figure(figsize=(10, 8))
        values = [float(net), float(fed), float(ss), float(mi), 
                  float(state_tax), float(nyc_tax), float(yonkers_tax)]
        labels = ['Take Home Pay', 'Federal Tax', 'Social Security', 'Medicare', 
                  'NY State Tax', 'NYC Tax', 'Yonkers Tax']
        colors = ['#66bb6a', '#ef5350', '#42a5f5', '#ffee58', '#4caf50', '#2196f3', '#ff9800']
        
        plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Complete Tax Breakdown (Federal & State)')
        return plt

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
FICA_CAP        = Decimal("168600")
SOCIAL_RATE     = Decimal("0.062")
MEDICARE_RATE   = Decimal("0.0145")
PERIODS = {
    "weekly":      Decimal("52"),
    "biweekly":    Decimal("26"),
    "semimonthly": Decimal("24"),
    "monthly":     Decimal("12"),
}

# Multiple Jobs Tax Brackets (annual ranges)
MULTIPLE_JOBS_RANGES = {
    "single": [
        {"range": (0, 14200), "adjustment": Decimal("0")},
        {"range": (14200, 34000), "adjustment": Decimal("1020")},
        {"range": (34000, 100000), "adjustment": Decimal("2040")},
        {"range": (100000, 200000), "adjustment": Decimal("3060")},
        {"range": (200000, float('inf')), "adjustment": Decimal("4080")}
    ],
    "married": [
        {"range": (0, 17000), "adjustment": Decimal("0")},
        {"range": (17000, 45000), "adjustment": Decimal("2040")},
        {"range": (45000, 120000), "adjustment": Decimal("4080")},
        {"range": (120000, 240000), "adjustment": Decimal("6120")},
        {"range": (240000, float('inf')), "adjustment": Decimal("8160")}
    ],
    "head": [
        {"range": (0, 14200), "adjustment": Decimal("0")},
        {"range": (14200, 34000), "adjustment": Decimal("1020")},
        {"range": (34000, 100000), "adjustment": Decimal("2040")},
        {"range": (100000, 200000), "adjustment": Decimal("3060")},
        {"range": (200000, float('inf')), "adjustment": Decimal("4080")}
    ]
}

def get_multiple_jobs_adjustment(annual_income: Decimal, filing_status: str) -> Decimal:
    """Calculate the multiple jobs adjustment based on IRS tables."""
    for bracket in MULTIPLE_JOBS_RANGES[filing_status]:
        if bracket["range"][0] <= float(annual_income) < bracket["range"][1]:
            return bracket["adjustment"]
    return Decimal("0")

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
    gross: Decimal, status: str, multi: bool, dep_credit: Decimal,
    oth: Decimal, ded: Decimal, extra: Decimal,
    period: str, annual: bool, other_job_amount: Decimal = Decimal("0")
) -> Decimal:
    """Calculate federal withholding with improved multiple jobs handling."""
    try:
        # Input validation
        if gross < Decimal("0"):
            raise ValueError("Gross pay cannot be negative")
        if dep_credit < Decimal("0"):
            raise ValueError("Dependent credits cannot be negative")
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
            annual_gross = gross * p
        else:
            base = gross / p
            other_periodic = oth / p
            ded_periodic = ded / p
            annual_gross = gross
            
        # Enhanced multiple jobs adjustment
        if multi:
            # Calculate adjustment based on annual income
            if other_job_amount > Decimal("0"):
                # For two jobs, use the higher paying job's adjustment
                higher_income = max(annual_gross, other_job_amount)
                adjustment = get_multiple_jobs_adjustment(higher_income, status)
            else:
                # For three or more jobs, use this job's adjustment
                adjustment = get_multiple_jobs_adjustment(annual_gross, status)
            
            # Apply adjustment to periodic amount
            base += adjustment / p
            
        # Calculate periodic taxable income
        standard_ded_periodic = STANDARD_DEDUCTION[status] / p
        taxable = max(
            base + other_periodic - standard_ded_periodic - ded_periodic,
            Decimal("0")
        )
        
        # Calculate periodic tax
        fed = calculate_periodic_pct_tax(status, taxable, period)
        
        # Apply dependent credit (periodic)
        credit_periodic = dep_credit / p
        fed = max(fed - credit_periodic, Decimal("0"))
        
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

# NY State Tax Constants (2024 - Subject to update when NY releases final figures)
NY_STANDARD_DEDUCTION = {
    "Single": Decimal("8500"),  # Estimated 2024
    "Married": Decimal("17050"), # Estimated 2024
    "Head": Decimal("11800"),    # Estimated 2024
    "Separate": Decimal("8500"), # Estimated 2024
    "Widow": Decimal("17050")    # Estimated 2024
}

NY_TAX_BRACKETS = {
    "Single": [
        {"min": Decimal("0"), "max": Decimal("8500"), "rate": Decimal("0.04"), "base": Decimal("0")},
        {"min": Decimal("8500"), "max": Decimal("11700"), "rate": Decimal("0.045"), "base": Decimal("340")},
        {"min": Decimal("11700"), "max": Decimal("13900"), "rate": Decimal("0.0525"), "base": Decimal("484")},
        {"min": Decimal("13900"), "max": Decimal("21400"), "rate": Decimal("0.0585"), "base": Decimal("600")},
        {"min": Decimal("21400"), "max": Decimal("80650"), "rate": Decimal("0.0625"), "base": Decimal("1042")},
        {"min": Decimal("80650"), "max": Decimal("215400"), "rate": Decimal("0.0685"), "base": Decimal("4842")},
        {"min": Decimal("215400"), "max": Decimal("1077550"), "rate": Decimal("0.0965"), "base": Decimal("14220")},
        {"min": Decimal("1077550"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("78990")},
        {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("360491")}
    ],
    "Married": [
        {"min": Decimal("0"), "max": Decimal("17150"), "rate": Decimal("0.04"), "base": Decimal("0")},
        {"min": Decimal("17150"), "max": Decimal("23600"), "rate": Decimal("0.045"), "base": Decimal("686")},
        {"min": Decimal("23600"), "max": Decimal("27900"), "rate": Decimal("0.0525"), "base": Decimal("899")},
        {"min": Decimal("27900"), "max": Decimal("43000"), "rate": Decimal("0.0585"), "base": Decimal("1116")},
        {"min": Decimal("43000"), "max": Decimal("161300"), "rate": Decimal("0.0625"), "base": Decimal("2004")},
        {"min": Decimal("161300"), "max": Decimal("323200"), "rate": Decimal("0.0685"), "base": Decimal("9051")},
        {"min": Decimal("323200"), "max": Decimal("2155350"), "rate": Decimal("0.0965"), "base": Decimal("20797")},
        {"min": Decimal("2155350"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("183010")},
        {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("447441")}
    ],
    "Head": [  # Head of Household brackets
        {"min": Decimal("0"), "max": Decimal("12800"), "rate": Decimal("0.04"), "base": Decimal("0")},
        {"min": Decimal("12800"), "max": Decimal("17650"), "rate": Decimal("0.045"), "base": Decimal("512")},
        {"min": Decimal("17650"), "max": Decimal("20900"), "rate": Decimal("0.0525"), "base": Decimal("730")},
        {"min": Decimal("20900"), "max": Decimal("32200"), "rate": Decimal("0.0585"), "base": Decimal("901")},
        {"min": Decimal("32200"), "max": Decimal("107650"), "rate": Decimal("0.0625"), "base": Decimal("1568")},
        {"min": Decimal("107650"), "max": Decimal("269300"), "rate": Decimal("0.0685"), "base": Decimal("6253")},
        {"min": Decimal("269300"), "max": Decimal("1616450"), "rate": Decimal("0.0965"), "base": Decimal("17233")},
        {"min": Decimal("1616450"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("131000")},
        {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("404016")}
    ],
    "Separate": [  # Married Filing Separately (half of married brackets)
        {"min": Decimal("0"), "max": Decimal("8575"), "rate": Decimal("0.04"), "base": Decimal("0")},
        {"min": Decimal("8575"), "max": Decimal("11800"), "rate": Decimal("0.045"), "base": Decimal("343")},
        {"min": Decimal("11800"), "max": Decimal("13950"), "rate": Decimal("0.0525"), "base": Decimal("450")},
        {"min": Decimal("13950"), "max": Decimal("21500"), "rate": Decimal("0.0585"), "base": Decimal("558")},
        {"min": Decimal("21500"), "max": Decimal("80650"), "rate": Decimal("0.0625"), "base": Decimal("1002")},
        {"min": Decimal("80650"), "max": Decimal("161600"), "rate": Decimal("0.0685"), "base": Decimal("4526")},
        {"min": Decimal("161600"), "max": Decimal("1077675"), "rate": Decimal("0.0965"), "base": Decimal("10399")},
        {"min": Decimal("1077675"), "max": Decimal("2500000"), "rate": Decimal("0.103"), "base": Decimal("91505")},
        {"min": Decimal("2500000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("223721")}
    ]
}

# NYC Tax Rates (2024 estimated)
NYC_TAX_RATES = {
    "Single": Decimal("0.03078"),
    "Married": Decimal("0.03078"),
    "Head": Decimal("0.03078"),
    "Separate": Decimal("0.03078"),
    "Widow": Decimal("0.03078")
}

# Yonkers Tax Rate (2024)
YONKERS_TAX_RATE = Decimal("0.16675")  # 16.75% of NY state tax

# NY Tax Credits and Deductions
NY_DEPENDENT_CREDIT = Decimal("100")  # Per qualifying dependent
NY_EMPIRE_STATE_CHILD_CREDIT = Decimal("333")  # Per qualifying child
NY_HOUSEHOLD_CREDIT = {
    "Single": [
        (Decimal("5000"), Decimal("75")),
        (Decimal("6000"), Decimal("60")),
        (Decimal("7000"), Decimal("50")),
        (Decimal("20000"), Decimal("45")),
        (Decimal("25000"), Decimal("40")),
        (Decimal("28000"), Decimal("20")),
        (Decimal("32000"), Decimal("15")),
        (None, Decimal("0"))
    ],
    "Married": [
        (Decimal("5000"), Decimal("90")),
        (Decimal("6000"), Decimal("75")),
        (Decimal("7000"), Decimal("65")),
        (Decimal("20000"), Decimal("60")),
        (Decimal("22000"), Decimal("60")),
        (Decimal("25000"), Decimal("50")),
        (Decimal("28000"), Decimal("40")),
        (Decimal("32000"), Decimal("20")),
        (None, Decimal("0"))
    ]
}

NY_ITEMIZED_CATEGORIES = {
    "medical": "Medical and Dental Expenses",
    "taxes": "State and Local Taxes Paid",
    "interest": "Interest Paid",
    "charity": "Charitable Contributions",
    "casualty": "Casualty and Theft Losses",
    "job": "Job Expenses",
    "other": "Other Itemized Deductions"
}

def calculate_ny_household_credit(income: Decimal, status: str, dependents: int) -> Decimal:
    """Calculate NY Household Credit based on income and filing status."""
    if status not in NY_HOUSEHOLD_CREDIT:
        return Decimal("0")
        
    credit = Decimal("0")
    for threshold, amount in NY_HOUSEHOLD_CREDIT[status]:
        if threshold is None or income <= threshold:
            credit = amount
            break
            
    # Additional credit for dependents (married only)
    if status == "Married" and dependents > 0:
        credit += Decimal("15") * Decimal(str(min(dependents, 5)))
        
    return credit

def calculate_ny_withholding(
    annual_salary: Decimal,
    pay_periods: int,
    calc_ny: bool,
    ny_status: str,
    ny_allow: int,
    ny_extra: Decimal,
    is_nyc_resident: bool = False,
    is_yonkers_resident: bool = False,
    itemized_deductions: dict = None,
    num_dependents: int = 0,
    qualifying_children: int = 0,
    part_year_resident: bool = False,
    supplemental_wages: bool = False,
    supplemental_amount: Decimal = Decimal("0")
) -> tuple[Decimal, Decimal, Decimal]:
    """
    Calculate NY state, NYC, and Yonkers withholding with improved precision.
    Returns a tuple of (state_tax, nyc_tax, yonkers_tax) per pay period.
    """
    if not calc_ny:
        return Decimal("0"), Decimal("0"), Decimal("0")
        
    try:
        # Convert inputs to Decimal
        annual_salary = Decimal(str(annual_salary))
        ny_extra = Decimal(str(ny_extra))
        
        # Handle supplemental wages
        if supplemental_wages:
            supplemental_amount = Decimal(str(supplemental_amount))
            supplemental_tax = supplemental_amount * Decimal("0.0985")  # NY supplemental wage rate
            annual_salary += supplemental_amount
        else:
            supplemental_tax = Decimal("0")
        
        # Calculate itemized deductions
        total_itemized = Decimal("0")
        if itemized_deductions:
            for category, amount in itemized_deductions.items():
                if category in NY_ITEMIZED_CATEGORIES:
                    total_itemized += Decimal(str(amount))
        
        # Determine deduction (greater of standard or itemized)
        standard_deduction = NY_STANDARD_DEDUCTION[ny_status]
        deduction = max(standard_deduction, total_itemized)
        
        # Calculate NY taxable income
        allowance_amount = Decimal(str(ny_allow)) * Decimal("1000")
        taxable = max(annual_salary - allowance_amount - deduction, Decimal("0"))
        
        # Calculate base state tax
        brackets = NY_TAX_BRACKETS[ny_status]
        state_tax = Decimal("0")
        
        for bracket in brackets:
            if bracket["max"] is None or taxable <= bracket["max"]:
                excess = taxable - bracket["min"]
                state_tax = bracket["base"] + (excess * bracket["rate"])
                break
        
        # Calculate credits
        credits = Decimal("0")
        
        # Household credit
        household_credit = calculate_ny_household_credit(annual_salary, ny_status, num_dependents)
        credits += household_credit
        
        # Dependent credit
        if num_dependents > 0:
            credits += NY_DEPENDENT_CREDIT * Decimal(str(num_dependents))
        
        # Empire State Child Credit
        if qualifying_children > 0:
            credits += NY_EMPIRE_STATE_CHILD_CREDIT * Decimal(str(qualifying_children))
        
        # Apply credits
        state_tax = max(state_tax - credits, Decimal("0"))
        
        # Part-year resident adjustment
        if part_year_resident:
            # Assume 6 months for demonstration - this should be configurable
            state_tax = state_tax * Decimal("0.5")
        
        # Calculate NYC Tax if applicable
        nyc_tax = Decimal("0")
        if is_nyc_resident:
            nyc_tax = taxable * NYC_TAX_RATES[ny_status]
            if part_year_resident:
                nyc_tax *= Decimal("0.5")
            
        # Calculate Yonkers Tax if applicable
        yonkers_tax = Decimal("0")
        if is_yonkers_resident:
            yonkers_tax = state_tax * YONKERS_TAX_RATE
            if part_year_resident:
                yonkers_tax *= Decimal("0.5")
        
        # Add supplemental tax if applicable
        state_tax += supplemental_tax
        
        # Convert to per-period amounts
        periods = Decimal(str(pay_periods))
        state_tax = round_to_penny(state_tax / periods) + ny_extra
        nyc_tax = round_to_penny(nyc_tax / periods)
        yonkers_tax = round_to_penny(yonkers_tax / periods)
        
        return state_tax, nyc_tax, yonkers_tax
        
    except Exception as e:
        st.error(f"Error calculating NY taxes: {str(e)}")
        return Decimal("0"), Decimal("0"), Decimal("0")

# ─── SIDEBAR UI ────────────────────────────────────────────────────────────────
st.sidebar.title("Inputs")
mode = st.sidebar.radio("Mode", ["Single Paycheck", "Full Year"])
annual = mode == "Full Year"

if annual:
    gross_input = st.sidebar.text_input(
        "Annual Gross Salary ($)",
        value="60000.00",
        help="Enter your annual gross salary (numbers only)"
    )
else:
    gross_input = st.sidebar.text_input(
        "Gross Amount per Paycheck ($)",
        value="1000.00",
        help="Enter your gross pay per paycheck (numbers only)"
    )

# Convert input to float, with error handling
try:
    gross_val = float(gross_input.replace(',', '').strip())
    if gross_val < 0:
        st.sidebar.error("Gross amount cannot be negative")
        gross_val = 0
except ValueError:
    st.sidebar.error("Please enter a valid number")
    gross_val = 0

period = st.sidebar.selectbox("Pay Frequency", ["weekly","biweekly","semimonthly","monthly"])

# Enhanced Multiple Jobs Section
st.sidebar.subheader("Step 2: Multiple Jobs / Spouse Works")
multi = st.sidebar.checkbox("Check if any of these apply:")
if multi:
    st.sidebar.markdown("""
        📋 **Multiple Jobs Worksheet**
        - You have more than one job at the same time
        - You're married filing jointly and your spouse also works
    """)
    
    job_count = st.sidebar.radio(
        "Select your situation:",
        ["Two jobs total", "Three or more jobs total"]
    )
    
    if job_count == "Two jobs total":
        st.sidebar.markdown("For most accurate withholding with two jobs:")
        other_job_input = st.sidebar.text_input(
            "Annual salary of other job ($)",
            value="0.00",
            help="Enter the annual salary of the other job"
        )
        try:
            other_job_amount = Decimal(other_job_input.replace(',', '').strip())
            if other_job_amount < 0:
                st.sidebar.error("Salary cannot be negative")
                other_job_amount = Decimal("0")
        except:
            st.sidebar.error("Please enter a valid number")
            other_job_amount = Decimal("0")
            
    else:  # Three or more jobs
        st.sidebar.markdown("""
            For three or more jobs:
            - Higher withholding amounts will be applied
            - Consider using the IRS Tax Withholding Estimator for more accuracy
        """)

# New dependent credit section
st.sidebar.subheader("Step 3: Dependent Credits")
st.sidebar.markdown("""
    Enter total dependent credits:
    - $2,000 per qualifying child under 17
    - $1,500 per dependent 17 and older
""")
dep_credit_input = st.sidebar.text_input(
    "Total Dependent Credits ($)",
    value="0.00",
    help="Enter total dependent credits (sum of $2,000 per qualifying child under 17 and $1,500 per dependent 17 and older)"
)

# Convert dependent credit input to float
try:
    dep_credit = float(dep_credit_input.replace(',', '').strip())
    if dep_credit < 0:
        st.sidebar.error("Dependent credits cannot be negative")
        dep_credit = 0
except ValueError:
    st.sidebar.error("Please enter a valid number for dependent credits")
    dep_credit = 0

oth    = Decimal(str(st.sidebar.number_input("Step 4(a): Other income ($)", value=0.0, step=100.0)))
ded    = Decimal(str(st.sidebar.number_input("Step 4(b): Deductions over standard ($)", value=0.0, step=100.0)))
extra  = Decimal(str(st.sidebar.number_input("Step 4(c): Extra withholding per period ($)", value=0.0, step=5.0)))

# Filing status must match lowercase keys:
filing = st.sidebar.selectbox("Filing Status (Step 1c)", ["single","married","head"])

# NY State Tax Section
st.sidebar.markdown("---")
st.sidebar.subheader("New York State Tax")
calc_ny = st.sidebar.checkbox("Calculate NY State withholding?")

if calc_ny:
    # Add expandable information section
    with st.sidebar.expander("ℹ️ NY Tax Information", expanded=False):
        st.markdown("""
            **2024 NY Tax Updates:**
            - Standard deductions have been adjusted for inflation
            - Tax brackets are estimated based on previous years
            - Final 2024 rates pending NY state confirmation
            
            **Filing Status Notes:**
            - Single: Unmarried individuals
            - Married: Joint return with spouse
            - Head: Head of household with qualifying person
            - Separate: Married filing separately
            - Widow: Qualifying widow(er) with dependent child
            
            **Credits Available:**
            - Household Credit (based on income)
            - Dependent Credit ($100 per dependent)
            - Empire State Child Credit ($333 per child)
            
            **Local Tax Notes:**
            - NYC residents pay additional city tax
            - Yonkers residents pay 16.75% of state tax
            - Other localities may have additional requirements
        """)
    
    ny_status = st.sidebar.selectbox(
        "NY Filing Status",
        ["Single", "Married", "Head", "Separate", "Widow"],
        help="Select your NY state filing status"
    )
    
    # Add warning for married status mismatch
    if filing == "married" and ny_status not in ["Married", "Separate"]:
        st.sidebar.warning("⚠️ Your federal and NY filing statuses don't match. This may affect accuracy.")
    elif filing == "single" and ny_status != "Single":
        st.sidebar.warning("⚠️ Your federal and NY filing statuses don't match. This may affect accuracy.")
    elif filing == "head" and ny_status != "Head":
        st.sidebar.warning("⚠️ Your federal and NY filing statuses don't match. This may affect accuracy.")
    
    # Residency Status
    st.sidebar.subheader("Residency Status")
    residency = st.sidebar.radio(
        "Select your residency status:",
        ["Full-Year", "Part-Year"],
        help="Part-year residents are taxed only on income earned while resident in NY"
    )
    part_year_resident = residency == "Part-Year"
    
    if part_year_resident:
        months_resident = st.sidebar.slider(
            "Months as NY resident",
            min_value=1,
            max_value=11,
            value=6,
            help="Number of months you were a NY resident"
        )
    
    # Deductions Section
    st.sidebar.subheader("NY Deductions")
    deduction_type = st.sidebar.radio(
        "Choose deduction type:",
        ["Standard", "Itemized"],
        help=f"Standard deduction for {ny_status}: ${NY_STANDARD_DEDUCTION[ny_status]:,.2f}"
    )
    
    itemized_deductions = {}
    if deduction_type == "Itemized":
        st.sidebar.markdown("Enter your itemized deductions:")
        for key, label in NY_ITEMIZED_CATEGORIES.items():
            amount = st.sidebar.number_input(
                f"{label} ($)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                help=f"Enter total {label.lower()} for the year"
            )
            if amount > 0:
                itemized_deductions[key] = amount
    
    # Credits Section
    st.sidebar.subheader("NY Tax Credits")
    num_dependents = st.sidebar.number_input(
        "Number of Dependents",
        min_value=0,
        max_value=99,
        value=0,
        help="Enter number of qualifying dependents"
    )
    
    qualifying_children = st.sidebar.number_input(
        "Number of Qualifying Children",
        min_value=0,
        max_value=num_dependents,
        value=0,
        help="Children under 17 who qualify for Empire State Child Credit"
    )
    
    # Supplemental Wages Section
    st.sidebar.subheader("Supplemental Wages")
    has_supplemental = st.sidebar.checkbox(
        "Include supplemental wages?",
        help="Bonuses, commissions, overtime pay, etc."
    )
    
    supplemental_amount = Decimal("0")
    if has_supplemental:
        supp_input = st.sidebar.number_input(
            "Supplemental wage amount ($)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="Enter total supplemental wages for the period"
        )
        supplemental_amount = Decimal(str(supp_input))
    
    # Allowances and Extra Withholding
    st.sidebar.subheader("Withholding Adjustments")
    st.sidebar.warning("""
        ⚠️ **Important:** NY is transitioning away from allowances.
        This calculator will be updated when new guidance is available.
    """)
    
    ny_allow = st.sidebar.number_input(
        "NY allowances (temporary)",
        min_value=0,
        max_value=99,
        value=0,
        help="Number of allowances claimed on your NY tax form"
    )
    
    ny_extra = st.sidebar.number_input(
        "NY extra withholding per period ($)",
        min_value=0.0,
        max_value=10000.0,
        value=0.0,
        step=5.0,
        help="Additional amount to withhold each pay period"
    )
    
    # Local Tax Options
    st.sidebar.subheader("Local Tax Options")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        is_nyc_resident = st.checkbox(
            "NYC Resident",
            help="Check if you are a New York City resident"
        )
    
    with col2:
        is_yonkers_resident = st.checkbox(
            "Yonkers Resident",
            help="Check if you are a Yonkers resident"
        )
    
    if is_nyc_resident and is_yonkers_resident:
        st.sidebar.error("❗ You cannot be both a NYC and Yonkers resident.")
        is_yonkers_resident = False
    
    if is_nyc_resident:
        st.sidebar.info(f"""
            🏙️ **NYC Tax Rate:** {float(NYC_TAX_RATES[ny_status])*100:.3f}%
            Applied to your NY taxable income
        """)
    
    if is_yonkers_resident:
        st.sidebar.info(f"""
            🏘️ **Yonkers Tax Rate:** {float(YONKERS_TAX_RATE)*100:.3f}%
            Applied to your NY state tax amount
        """)
else:
    ny_status = None
    ny_allow = 0
    ny_extra = Decimal("0")
    is_nyc_resident = False
    is_yonkers_resident = False
    part_year_resident = False
    itemized_deductions = None
    num_dependents = 0
    qualifying_children = 0
    supplemental_amount = Decimal("0")

# ─── MAIN AREA ────────────────────────────────────────────────────────────────
st.title("2024 Paycheck Tax Withholding Calculator")
st.markdown("This uses IRS Publication 15-T percentage and annual 1040 tables for federal withholding, plus optional NY state withholding.")

st.warning("""
⚠️ **Disclaimer**: 
- This calculator provides estimates based on IRS Publication 15-T procedures
- Results are approximations and should not be used for official tax filing purposes
- For accurate tax advice, please consult a qualified tax professional
- Actual withholding may vary based on specific employer policies and circumstances
""")

if st.sidebar.button("Calculate"):
    if gross_val > 250_000:
        st.error("who we lying to 👀")
        st.stop()
    # now the real work begins
    gross = Decimal(str(gross_val))
    dep_credit_dec = Decimal(str(dep_credit))
    other_job = Decimal(str(other_job_amount)) if multi and job_count == "Two jobs total" else Decimal("0")
    fed = calculate_fed(gross, filing, multi, dep_credit_dec, oth, ded, extra, period, annual, other_job)
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

    # ─── Visualizations ────────────────────────────────────────────────────────────
    st.markdown("### 📊 Interactive Tax Visualizations")
    
    # Create tabs for different visualizations
    viz_tabs = st.tabs(["Breakdown", "Comparison", "Projection"])
    
    with viz_tabs[0]:
        st.pyplot(create_tax_breakdown_pie(fed, ss, mi, net))
        st.caption("💡 **Tip:** Hover over segments for details, click legend items to filter")
        
    with viz_tabs[1]:
        st.pyplot(create_tax_comparison_bar(fed, ss, mi))
        st.caption("💡 **Tip:** Hover over bars for exact values")
        
    with viz_tabs[2]:
        st.pyplot(create_annual_projection(net, period))
        st.caption("💡 **Tip:** Hover over points to see cumulative amounts")
        
        # Add some insights
        annual_net = net * PERIODS[period]
        st.markdown(f"""
            #### 💰 Annual Projections
            - Your projected annual net pay: **${annual_net:,.2f}**
            - Average monthly take-home: **${(annual_net/12):,.2f}**
            - Per pay period: **${net:,.2f}**
        """)

    # Continue with NY state calculations if enabled
    if calc_ny:
        annual_sal = Decimal(str(gross if annual else gross * PERIODS[period]))
        pp = int(PERIODS[period])
        state_tax, nyc_tax, yonkers_tax = calculate_ny_withholding(
            annual_sal,
            pp,
            True,
            ny_status,
            int(ny_allow),
            Decimal(str(ny_extra)),
            is_nyc_resident,
            is_yonkers_resident,
            itemized_deductions,
            num_dependents,
            qualifying_children,
            part_year_resident,
            has_supplemental,
            supplemental_amount
        )
        
        # Display NY Tax Information with visualizations
        st.markdown("### New York Tax Breakdown")
        
        ny_cols = st.columns(4)
        
        with ny_cols[0]:
            st.metric(
                "NY State Tax",
                f"${state_tax:,.2f}",
                help="New York State withholding tax per pay period"
            )
            
        with ny_cols[1]:
            if is_nyc_resident:
                st.metric(
                    "NYC Tax",
                    f"${nyc_tax:,.2f}",
                    help="New York City resident tax per pay period"
                )
            else:
                st.metric(
                    "NYC Tax",
                    "N/A",
                    help="NYC tax only applies to city residents"
                )
                
        with ny_cols[2]:
            if is_yonkers_resident:
                st.metric(
                    "Yonkers Tax",
                    f"${yonkers_tax:,.2f}",
                    help="Yonkers resident tax per pay period"
                )
            else:
                st.metric(
                    "Yonkers Tax",
                    "N/A",
                    help="Yonkers tax only applies to city residents"
                )
                
        with ny_cols[3]:
            total_ny = state_tax + nyc_tax + yonkers_tax
            st.metric(
                "Total NY Tax",
                f"${total_ny:,.2f}",
                help="Total New York taxes per pay period"
            )
            
            # NY Tax Visualizations
            ny_viz_tabs = st.tabs(["NY Breakdown", "Complete Picture"])
            
            with ny_viz_tabs[0]:
                if total_ny > 0:
                    st.pyplot(create_ny_tax_breakdown(state_tax, nyc_tax, yonkers_tax))
                    st.caption("💡 **Tip:** Hover over bars for exact values")
                else:
                    st.info("No New York taxes to display")
            
            with ny_viz_tabs[1]:
                st.pyplot(create_total_tax_pie(fed, ss, mi, state_tax, nyc_tax, yonkers_tax, net))
                st.caption("💡 **Tip:** Click legend items to filter, hover for details")
            
            # Show annual equivalent if in single paycheck mode
            if not annual:
                annual_state = state_tax * PERIODS[period]
                annual_nyc = nyc_tax * PERIODS[period]
                annual_yonkers = yonkers_tax * PERIODS[period]
                annual_total = total_ny * PERIODS[period]
                
                st.markdown("#### Annual Equivalent")
                st.markdown(f"""
                    - State Tax: ${annual_state:,.2f}
                    - NYC Tax: ${annual_nyc:,.2f}
                    - Yonkers Tax: ${annual_yonkers:,.2f}
                    - **Total NY Tax: ${annual_total:,.2f}**
                """)
                
            # Add explanatory notes
            with st.expander("ℹ️ About NY Tax Calculations"):
                st.markdown(f"""
                    **Calculation Details:**
                    - Filing Status: {ny_status}
                    - Standard Deduction: ${NY_STANDARD_DEDUCTION[ny_status]:,.2f}
                    - Allowances: {ny_allow} × $1,000 = ${ny_allow*1000:,.2f}
                    - Extra Withholding: ${ny_extra:,.2f} per period
                    
                    **Notes:**
                    - These calculations are estimates based on 2024 tax tables
                    - Actual withholding may vary based on your specific situation
                    - Consult a tax professional for personalized advice
                """)

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

# ─── Snake Game Section ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🐍 Take a Break: Play Snake!", expanded=False):
    st.markdown("""
        ### Snake Game
        Use arrow keys to control the snake:
        - ⬆️ Move Up
        - ⬇️ Move Down
        - ⬅️ Move Left
        - ➡️ Move Right
        
        Click 'Start New Game' to begin!
        
        *Note: If the game doesn't load properly, try refreshing the page.*
    """)
    try:
        from snake_game import snake_game
        snake_game()
    except Exception as e:
        st.error("Unable to load the snake game. Please refresh the page.")
        st.warning(f"Error details: {str(e)}")


