from decimal import Decimal
from typing import Dict, Any
import streamlit as st

from .base import StateTaxCalculator, StateTaxResult

class NYTaxCalculator(StateTaxCalculator):
    # Constants
    STANDARD_DEDUCTION = {
        "Single": Decimal("8500"),     # 2024 estimated
        "Married": Decimal("17050"),   # 2024 estimated
        "Head": Decimal("11800"),      # 2024 estimated
        "Separate": Decimal("8500"),   # 2024 estimated
        "Widow": Decimal("17050")      # 2024 estimated
    }
    
    TAX_BRACKETS = {
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
        "Head": [
            {"min": Decimal("0"), "max": Decimal("12800"), "rate": Decimal("0.04"), "base": Decimal("0")},
            {"min": Decimal("12800"), "max": Decimal("17650"), "rate": Decimal("0.045"), "base": Decimal("512")},
            {"min": Decimal("17650"), "max": Decimal("20900"), "rate": Decimal("0.0525"), "base": Decimal("730")},
            {"min": Decimal("20900"), "max": Decimal("32200"), "rate": Decimal("0.0585"), "base": Decimal("901")},
            {"min": Decimal("32200"), "max": Decimal("107650"), "rate": Decimal("0.0625"), "base": Decimal("1568")},
            {"min": Decimal("107650"), "max": Decimal("269300"), "rate": Decimal("0.0685"), "base": Decimal("6253")},
            {"min": Decimal("269300"), "max": Decimal("1616450"), "rate": Decimal("0.0965"), "base": Decimal("17892")},
            {"min": Decimal("1616450"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("147518")},
            {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("396776")}
        ],
        "Separate": [
            {"min": Decimal("0"), "max": Decimal("8500"), "rate": Decimal("0.04"), "base": Decimal("0")},
            {"min": Decimal("8500"), "max": Decimal("11700"), "rate": Decimal("0.045"), "base": Decimal("340")},
            {"min": Decimal("11700"), "max": Decimal("13900"), "rate": Decimal("0.0525"), "base": Decimal("484")},
            {"min": Decimal("13900"), "max": Decimal("21400"), "rate": Decimal("0.0585"), "base": Decimal("600")},
            {"min": Decimal("21400"), "max": Decimal("80650"), "rate": Decimal("0.0625"), "base": Decimal("1042")},
            {"min": Decimal("80650"), "max": Decimal("215400"), "rate": Decimal("0.0685"), "base": Decimal("4721")},
            {"min": Decimal("215400"), "max": Decimal("1077550"), "rate": Decimal("0.0965"), "base": Decimal("13467")},
            {"min": Decimal("1077550"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("96333")},
            {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("360491")}
        ],
        "Widow": [
            {"min": Decimal("0"), "max": Decimal("17150"), "rate": Decimal("0.04"), "base": Decimal("0")},
            {"min": Decimal("17150"), "max": Decimal("23600"), "rate": Decimal("0.045"), "base": Decimal("686")},
            {"min": Decimal("23600"), "max": Decimal("27900"), "rate": Decimal("0.0525"), "base": Decimal("899")},
            {"min": Decimal("27900"), "max": Decimal("43000"), "rate": Decimal("0.0585"), "base": Decimal("1116")},
            {"min": Decimal("43000"), "max": Decimal("161300"), "rate": Decimal("0.0625"), "base": Decimal("2004")},
            {"min": Decimal("161300"), "max": Decimal("323200"), "rate": Decimal("0.0685"), "base": Decimal("9051")},
            {"min": Decimal("323200"), "max": Decimal("2155350"), "rate": Decimal("0.0965"), "base": Decimal("20797")},
            {"min": Decimal("2155350"), "max": Decimal("5000000"), "rate": Decimal("0.103"), "base": Decimal("183010")},
            {"min": Decimal("5000000"), "max": None, "rate": Decimal("0.109"), "base": Decimal("447441")}
        ]
    }
    
    NYC_TAX_RATES = {
        "Single": Decimal("0.03078"),
        "Married": Decimal("0.03078"),
        "Head": Decimal("0.03078"),
        "Separate": Decimal("0.03078"),
        "Widow": Decimal("0.03078")
    }
    
    YONKERS_TAX_RATE = Decimal("0.16675")  # 16.75% of NY state tax
    
    @property
    def state_code(self) -> str:
        return "NY"
        
    @property
    def state_name(self) -> str:
        return "New York"
        
    @property
    def has_local_tax(self) -> bool:
        return True
        
    @property
    def available_filing_statuses(self) -> list[str]:
        return ["Single", "Married", "Head", "Separate", "Widow"]
        
    def get_local_jurisdictions(self) -> list[str]:
        return ["New York City", "Yonkers"]
        
    def calculate(
        self,
        income: Decimal,
        filing_status: str,
        pay_period: str,
        is_annual: bool = False,
        **kwargs
    ) -> StateTaxResult:
        """Calculate NY state taxes."""
        # Extract kwargs
        allowances = kwargs.get("allowances", 0)
        extra_withholding = kwargs.get("extra_withholding", Decimal("0"))
        is_nyc_resident = kwargs.get("is_nyc_resident", False)
        is_yonkers_resident = kwargs.get("is_yonkers_resident", False)
        itemized_deductions = kwargs.get("itemized_deductions", {})
        num_dependents = kwargs.get("num_dependents", 0)
        part_year_resident = kwargs.get("part_year_resident", False)
        
        # Income is already annualized by app.py
        annual_income = income
        
        # Calculate deductions
        standard_ded = self.STANDARD_DEDUCTION[filing_status]
        itemized_total = sum(Decimal(str(amt)) for amt in itemized_deductions.values())
        deduction = max(standard_ded, itemized_total)
        
        # Calculate allowance reduction
        allowance_amount = Decimal(str(allowances)) * Decimal("1000")
        
        # Calculate taxable income
        taxable_income = max(annual_income - allowance_amount - deduction, Decimal("0"))
        
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
                
        # Calculate local taxes
        local_taxes = {}
        if is_nyc_resident:
            local_taxes["nyc"] = taxable_income * self.NYC_TAX_RATES[filing_status]
            
        if is_yonkers_resident:
            local_taxes["yonkers"] = state_tax * self.YONKERS_TAX_RATE
            
        # Part-year adjustment
        if part_year_resident:
            state_tax *= Decimal("0.5")
            local_taxes = {k: v * Decimal("0.5") for k, v in local_taxes.items()}
            
        # Add extra withholding
        state_tax += extra_withholding
        
        # Convert to per-period if needed
        if not is_annual:
            periods = {
                "weekly": Decimal("52"),
                "biweekly": Decimal("26"),
                "semimonthly": Decimal("24"),
                "monthly": Decimal("12")
            }
            period_count = periods[pay_period]
            state_tax = state_tax / period_count
            local_taxes = {k: v / period_count for k, v in local_taxes.items()}
            
        # Calculate effective rate (using annual amounts)
        total_tax = state_tax + sum(local_taxes.values())
        effective_rate = total_tax / annual_income if annual_income > 0 else Decimal("0")
        
        return StateTaxResult(
            state_tax=state_tax,
            local_taxes=local_taxes,
            credits={},  # TODO: Implement credits
            deductions={"standard": standard_ded} if itemized_total <= standard_ded else itemized_deductions,
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            warnings=["Part-year resident calculations are estimates"] if part_year_resident else None,
            errors=None
        )
        
    def get_ui_components(self) -> Dict[str, Any]:
        """Define NY-specific UI components for Streamlit."""
        def render(container):
            container.subheader("NY State Tax Options")
            
            # Basic Info
            filing_status = container.selectbox(
                "NY Filing Status",
                self.available_filing_statuses,
                help="Select your NY state filing status"
            )
            
            # Residency
            container.subheader("Residency Status")
            residency = container.radio(
                "Select your residency status:",
                ["Full-Year", "Part-Year"],
                help="Part-year residents are taxed only on income earned while resident in NY"
            )
            
            # Local Tax
            container.subheader("Local Tax Options")
            col1, col2 = container.columns(2)
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
                container.error("❗ You cannot be both a NYC and Yonkers resident.")
                is_yonkers_resident = False
                
            # Return all inputs as a dict
            return {
                "filing_status": filing_status,
                "part_year_resident": residency == "Part-Year",
                "is_nyc_resident": is_nyc_resident,
                "is_yonkers_resident": is_yonkers_resident,
            }
            
        return {"render": render} 
