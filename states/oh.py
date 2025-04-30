from decimal import Decimal
from typing import Dict, Any
import streamlit as st

from .base import StateTaxCalculator, StateTaxResult

class OHTaxCalculator(StateTaxCalculator):
    # Constants for 2024
    STANDARD_DEDUCTION = {
        "Single": Decimal("0"),        # OH doesn't have standard deduction
        "Married": Decimal("0"),
        "Head": Decimal("0"),
        "Separate": Decimal("0"),
        "Widow": Decimal("0")
    }
    
    # 2024 tax brackets (HB 33 eliminated taxes on income under $26,050)
    TAX_BRACKETS = {
        "Single": [
            {"min": Decimal("26050"), "max": Decimal("46100"), "rate": Decimal("0.0275"), "base": Decimal("0")},
            {"min": Decimal("46100"), "max": Decimal("92150"), "rate": Decimal("0.0324"), "base": Decimal("551.38")},
            {"min": Decimal("92150"), "max": Decimal("115300"), "rate": Decimal("0.0373"), "base": Decimal("2045.21")},
            {"min": Decimal("115300"), "max": None, "rate": Decimal("0.0399"), "base": Decimal("2907.88")}
        ]
    }
    
    def __init__(self):
        super().__init__()
        # Ohio uses same brackets for all filing statuses
        self.TAX_BRACKETS["Married"] = self.TAX_BRACKETS["Single"]
        self.TAX_BRACKETS["Head"] = self.TAX_BRACKETS["Single"]
        self.TAX_BRACKETS["Separate"] = self.TAX_BRACKETS["Single"]
        self.TAX_BRACKETS["Widow"] = self.TAX_BRACKETS["Single"]

    @property
    def state_code(self) -> str:
        return "OH"
        
    @property
    def state_name(self) -> str:
        return "Ohio"
        
    @property
    def has_local_tax(self) -> bool:
        return True
        
    @property
    def available_filing_statuses(self) -> list[str]:
        return ["Single", "Married", "Head", "Separate", "Widow"]
        
    def get_local_jurisdictions(self) -> list[str]:
        return ["School District"]
        
    def calculate(
        self,
        income: Decimal,
        filing_status: str,
        pay_period: str,
        is_annual: bool = False,
        **kwargs
    ) -> StateTaxResult:
        """Calculate OH state taxes."""
        # Extract kwargs
        extra_withholding = kwargs.get("extra_withholding", Decimal("0"))
        school_district_rate = kwargs.get("school_district_rate", self.SCHOOL_DISTRICT_RATES["default"])
        has_school_district_tax = kwargs.get("has_school_district_tax", False)
        part_year_resident = kwargs.get("part_year_resident", False)
        
        # Income is already annualized by app.py
        annual_income = income
        
        # Ohio has a special exemption credit
        exemptions = st.number_input("Number of exemptions (including yourself)", min_value=1, value=1, step=1)
        exemption_amount = Decimal("2400")  # 2024 exemption amount
        exemption_credit = exemptions * exemption_amount * Decimal("0.02")
        
        # Calculate tax
        if annual_income <= Decimal("26050"):
            tax = Decimal("0")
        else:
            tax = self._calculate_tax_from_brackets(annual_income, filing_status)
        
        # Apply exemption credit
        final_tax = max(Decimal("0"), tax - exemption_credit)
        
        # Calculate school district tax if applicable
        local_taxes = {}
        if has_school_district_tax:
            local_taxes["school_district"] = annual_income * school_district_rate
            
        # Part-year adjustment
        if part_year_resident:
            final_tax *= Decimal("0.5")
            local_taxes = {k: v * Decimal("0.5") for k, v in local_taxes.items()}
            
        # Add extra withholding
        final_tax += extra_withholding
        
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
            local_taxes = {k: v / period_count for k, v in local_taxes.items()}
            
        # Calculate effective rate (using annual amounts)
        total_tax = final_tax + sum(local_taxes.values())
        effective_rate = total_tax / annual_income if annual_income > 0 else Decimal("0")
        
        render = {
            "State Tax": f"${final_tax:,.2f}",
            "Taxable Income": f"${annual_income:,.2f}",
            "Exemption Credit": f"${exemption_credit:,.2f}"
        }
        
        return StateTaxResult(
            state_tax=final_tax,
            local_taxes=local_taxes,
            credits={},
            deductions={},
            effective_rate=effective_rate,
            marginal_rate=self._calculate_marginal_rate(annual_income, filing_status),
            warnings=["Part-year resident calculations are estimates"] if part_year_resident else None,
            errors=None,
            render=render
        )
        
    def get_ui_components(self) -> Dict[str, Any]:
        """Define OH-specific UI components for Streamlit."""
        def render(container):
            container.subheader("OH State Tax Options")
            
            # Basic Info
            filing_status = container.selectbox(
                "OH Filing Status",
                self.available_filing_statuses,
                help="Select your OH state filing status"
            )
            
            # Residency
            container.subheader("Residency Status")
            residency = container.radio(
                "Select your residency status:",
                ["Full-Year", "Part-Year"],
                help="Part-year residents are taxed only on income earned while resident in OH"
            )
            
            # School District Tax
            container.subheader("School District Tax")
            has_school_district_tax = container.checkbox(
                "Subject to School District Tax",
                help="Check if you live in a school district that levies an income tax"
            )
            
            school_district_rate = None
            if has_school_district_tax:
                school_district_rate = container.number_input(
                    "School District Tax Rate (%)",
                    min_value=0.0,
                    max_value=3.0,
                    value=1.0,
                    step=0.1,
                    help="Enter your school district tax rate as a percentage"
                )
            
            # Return all inputs as a dict
            return {
                "filing_status": filing_status,
                "part_year_resident": residency == "Part-Year",
                "has_school_district_tax": has_school_district_tax,
                "school_district_rate": Decimal(str(school_district_rate / 100)) if school_district_rate is not None else None
            }
            
        return {"render": render} 
