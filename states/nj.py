from decimal import Decimal
from typing import Dict, Any
import streamlit as st

from .base import StateTaxCalculator, StateTaxResult

class NJTaxCalculator(StateTaxCalculator):
    # Constants for 2024
    STANDARD_DEDUCTION = {
        "Single": Decimal("0"),        # NJ doesn't have standard deduction
        "Married": Decimal("0"),
        "Head": Decimal("0"),
        "Separate": Decimal("0"),
        "Widow": Decimal("0")
    }
    
    # Updated 2024 tax brackets
    TAX_BRACKETS = {
        "Single": [
            {"min": Decimal("0"), "max": Decimal("20000"), "rate": Decimal("0.014"), "base": Decimal("0")},
            {"min": Decimal("20000"), "max": Decimal("35000"), "rate": Decimal("0.0175"), "base": Decimal("280")},
            {"min": Decimal("35000"), "max": Decimal("40000"), "rate": Decimal("0.035"), "base": Decimal("542.50")},
            {"min": Decimal("40000"), "max": Decimal("75000"), "rate": Decimal("0.0553"), "base": Decimal("717.50")},
            {"min": Decimal("75000"), "max": Decimal("500000"), "rate": Decimal("0.0637"), "base": Decimal("2651.00")},
            {"min": Decimal("500000"), "max": Decimal("1000000"), "rate": Decimal("0.0897"), "base": Decimal("29723.50")},
            {"min": Decimal("1000000"), "max": None, "rate": Decimal("0.1075"), "base": Decimal("74573.50")}
        ],
        "Married": [
            {"min": Decimal("0"), "max": Decimal("20000"), "rate": Decimal("0.014"), "base": Decimal("0")},
            {"min": Decimal("20000"), "max": Decimal("50000"), "rate": Decimal("0.0175"), "base": Decimal("280")},
            {"min": Decimal("50000"), "max": Decimal("70000"), "rate": Decimal("0.0245"), "base": Decimal("805")},
            {"min": Decimal("70000"), "max": Decimal("80000"), "rate": Decimal("0.035"), "base": Decimal("1295.50")},
            {"min": Decimal("80000"), "max": Decimal("150000"), "rate": Decimal("0.0553"), "base": Decimal("1645.00")},
            {"min": Decimal("150000"), "max": Decimal("500000"), "rate": Decimal("0.0637"), "base": Decimal("5512.50")},
            {"min": Decimal("500000"), "max": Decimal("1000000"), "rate": Decimal("0.0897"), "base": Decimal("27597.50")},
            {"min": Decimal("1000000"), "max": None, "rate": Decimal("0.1075"), "base": Decimal("72447.50")}
        ]
    }
    
    def __init__(self):
        super().__init__()
        self.TAX_BRACKETS["Head"] = self.TAX_BRACKETS["Single"]
        self.TAX_BRACKETS["Separate"] = self.TAX_BRACKETS["Single"]
        self.TAX_BRACKETS["Widow"] = self.TAX_BRACKETS["Married"]

    @property
    def state_code(self) -> str:
        return "NJ"
        
    @property
    def state_name(self) -> str:
        return "New Jersey"
        
    @property
    def has_local_tax(self) -> bool:
        return False
        
    @property
    def available_filing_statuses(self) -> list[str]:
        return ["Single", "Married", "Head", "Separate", "Widow"]
        
    def get_local_jurisdictions(self) -> list[str]:
        """Return list of local tax jurisdictions for NJ."""
        return []  # NJ has no local income taxes
        
    def calculate(
        self,
        income: Decimal,
        filing_status: str,
        pay_period: str,
        is_annual: bool = False,
        **kwargs
    ) -> StateTaxResult:
        """Calculate NJ state taxes."""
        # Extract kwargs
        extra_withholding = kwargs.get("extra_withholding", Decimal("0"))
        itemized_deductions = kwargs.get("itemized_deductions", {})
        part_year_resident = kwargs.get("part_year_resident", False)
        
        # Income is already annualized by app.py
        annual_income = income
        
        # NJ doesn't have standard deduction, but keeping structure for consistency
        deduction = Decimal("0")
        
        # Calculate taxable income
        taxable_income = max(annual_income - deduction, Decimal("0"))
        
        # Property Tax Deduction/Credit (if applicable)
        property_tax_paid = st.number_input("Property taxes paid (if any)", min_value=0.0, value=0.0, step=100.0)
        property_tax_paid = Decimal(str(property_tax_paid))
        
        if property_tax_paid > 0:
            # Maximum property tax deduction is $15,000
            property_tax_deduction = min(property_tax_paid, Decimal("15000"))
            taxable_income = max(Decimal("0"), taxable_income - property_tax_deduction)
        
        # Find tax bracket and calculate base tax
        brackets = self.TAX_BRACKETS[filing_status]
        state_tax = Decimal("0")
        marginal_rate = Decimal("0")
        
        for bracket in brackets:
            if bracket["max"] is None or taxable_income <= bracket["max"]:
                excess = taxable_income - bracket["min"]
                state_tax = bracket["base"] + (excess * bracket["rate"])
                marginal_rate = bracket["rate"]
                break
                
        # Part-year adjustment
        if part_year_resident:
            state_tax *= Decimal("0.5")
            
        # Add extra withholding
        state_tax += extra_withholding
        
        # Property Tax Credit
        property_tax_credit = Decimal("0")
        if income <= Decimal("100000"):
            property_tax_credit = min(property_tax_paid, Decimal("50"))
        
        final_tax = max(Decimal("0"), state_tax - property_tax_credit)
        
        # Convert to per-period if needed
        if not is_annual:
            periods = {
                "weekly": Decimal("52"),
                "biweekly": Decimal("26"),
                "semimonthly": Decimal("24"),
                "monthly": Decimal("12")
            }
            period_count = periods[pay_period]
            final_tax = final_tax / period_count
            
        # Calculate effective rate (using annual amounts)
        effective_rate = final_tax / annual_income if annual_income > 0 else Decimal("0")
        
        render = {
            "State Tax": f"${final_tax:,.2f}",
            "Taxable Income": f"${taxable_income:,.2f}",
        }
        
        if property_tax_paid > 0:
            render["Property Tax Deduction"] = f"${property_tax_deduction:,.2f}"
            render["Property Tax Credit"] = f"${property_tax_credit:,.2f}"
        
        return StateTaxResult(
            state_tax=final_tax,
            local_taxes={},
            credits={},
            deductions={},
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            warnings=["Part-year resident calculations are estimates"] if part_year_resident else None,
            errors=None
        )
        
    def get_ui_components(self) -> Dict[str, Any]:
        """Define NJ-specific UI components for Streamlit."""
        def render(container):
            container.subheader("NJ State Tax Options")
            
            # Basic Info
            filing_status = container.selectbox(
                "NJ Filing Status",
                self.available_filing_statuses,
                help="Select your NJ state filing status"
            )
            
            # Residency
            container.subheader("Residency Status")
            residency = container.radio(
                "Select your residency status:",
                ["Full-Year", "Part-Year"],
                help="Part-year residents are taxed only on income earned while resident in NJ"
            )
            
            # Return all inputs as a dict
            return {
                "filing_status": filing_status,
                "part_year_resident": residency == "Part-Year",
            }
            
        return {"render": render} 
