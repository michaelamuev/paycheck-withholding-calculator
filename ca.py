from decimal import Decimal
from typing import Dict, Any
import streamlit as st

from .base import StateTaxCalculator, StateTaxResult

class CATaxCalculator(StateTaxCalculator):
    # Constants (2024 estimated)
    STANDARD_DEDUCTION = {
        "Single": Decimal("5202"),
        "Married": Decimal("10404"),
        "Head": Decimal("10404"),
        "Separate": Decimal("5202")
    }
    
    TAX_BRACKETS = {
        "Single": [
            {"min": Decimal("0"), "max": Decimal("10099"), "rate": Decimal("0.01"), "base": Decimal("0")},
            {"min": Decimal("10099"), "max": Decimal("23942"), "rate": Decimal("0.02"), "base": Decimal("101")},
            {"min": Decimal("23942"), "max": Decimal("37788"), "rate": Decimal("0.04"), "base": Decimal("377")},
            {"min": Decimal("37788"), "max": Decimal("52455"), "rate": Decimal("0.06"), "base": Decimal("931")},
            {"min": Decimal("52455"), "max": Decimal("66295"), "rate": Decimal("0.08"), "base": Decimal("1811")},
            {"min": Decimal("66295"), "max": Decimal("338639"), "rate": Decimal("0.093"), "base": Decimal("2918")},
            {"min": Decimal("338639"), "max": Decimal("406364"), "rate": Decimal("0.103"), "base": Decimal("28246")},
            {"min": Decimal("406364"), "max": Decimal("677275"), "rate": Decimal("0.113"), "base": Decimal("35222")},
            {"min": Decimal("677275"), "max": None, "rate": Decimal("0.123"), "base": Decimal("65835")}
        ],
        "Married": [
            {"min": Decimal("0"), "max": Decimal("20198"), "rate": Decimal("0.01"), "base": Decimal("0")},
            {"min": Decimal("20198"), "max": Decimal("47884"), "rate": Decimal("0.02"), "base": Decimal("202")},
            {"min": Decimal("47884"), "max": Decimal("75576"), "rate": Decimal("0.04"), "base": Decimal("754")},
            {"min": Decimal("75576"), "max": Decimal("104910"), "rate": Decimal("0.06"), "base": Decimal("1862")},
            {"min": Decimal("104910"), "max": Decimal("132590"), "rate": Decimal("0.08"), "base": Decimal("3622")},
            {"min": Decimal("132590"), "max": Decimal("677278"), "rate": Decimal("0.093"), "base": Decimal("5836")},
            {"min": Decimal("677278"), "max": Decimal("812728"), "rate": Decimal("0.103"), "base": Decimal("56492")},
            {"min": Decimal("812728"), "max": Decimal("1354550"), "rate": Decimal("0.113"), "base": Decimal("70444")},
            {"min": Decimal("1354550"), "max": None, "rate": Decimal("0.123"), "base": Decimal("131670")}
        ],
        "Head": [
            {"min": Decimal("0"), "max": Decimal("20212"), "rate": Decimal("0.01"), "base": Decimal("0")},
            {"min": Decimal("20212"), "max": Decimal("47887"), "rate": Decimal("0.02"), "base": Decimal("202")},
            {"min": Decimal("47887"), "max": Decimal("61730"), "rate": Decimal("0.04"), "base": Decimal("754")},
            {"min": Decimal("61730"), "max": Decimal("76397"), "rate": Decimal("0.06"), "base": Decimal("1308")},
            {"min": Decimal("76397"), "max": Decimal("90240"), "rate": Decimal("0.08"), "base": Decimal("2188")},
            {"min": Decimal("90240"), "max": Decimal("460547"), "rate": Decimal("0.093"), "base": Decimal("3295")},
            {"min": Decimal("460547"), "max": Decimal("552658"), "rate": Decimal("0.103"), "base": Decimal("37622")},
            {"min": Decimal("552658"), "max": Decimal("921095"), "rate": Decimal("0.113"), "base": Decimal("47059")},
            {"min": Decimal("921095"), "max": None, "rate": Decimal("0.123"), "base": Decimal("88771")}
        ],
        "Separate": [
            {"min": Decimal("0"), "max": Decimal("10099"), "rate": Decimal("0.01"), "base": Decimal("0")},
            {"min": Decimal("10099"), "max": Decimal("23942"), "rate": Decimal("0.02"), "base": Decimal("101")},
            {"min": Decimal("23942"), "max": Decimal("37788"), "rate": Decimal("0.04"), "base": Decimal("377")},
            {"min": Decimal("37788"), "max": Decimal("52455"), "rate": Decimal("0.06"), "base": Decimal("931")},
            {"min": Decimal("52455"), "max": Decimal("66295"), "rate": Decimal("0.08"), "base": Decimal("1811")},
            {"min": Decimal("66295"), "max": Decimal("338639"), "rate": Decimal("0.093"), "base": Decimal("2918")},
            {"min": Decimal("338639"), "max": Decimal("406364"), "rate": Decimal("0.103"), "base": Decimal("28246")},
            {"min": Decimal("406364"), "max": Decimal("677275"), "rate": Decimal("0.113"), "base": Decimal("35222")},
            {"min": Decimal("677275"), "max": None, "rate": Decimal("0.123"), "base": Decimal("65835")}
        ]
    }
    
    @property
    def state_code(self) -> str:
        return "CA"
        
    @property
    def state_name(self) -> str:
        return "California"
        
    @property
    def has_local_tax(self) -> bool:
        return False
        
    @property
    def available_filing_statuses(self) -> list[str]:
        return ["Single", "Married", "Head", "Separate"]
        
    def get_local_jurisdictions(self) -> list[str]:
        return []  # CA doesn't have local income taxes
        
    def calculate(
        self,
        income: Decimal,
        filing_status: str,
        pay_period: str,
        is_annual: bool = False,
        **kwargs
    ) -> StateTaxResult:
        """Calculate CA state taxes."""
        # Convert to annual if needed
        periods = {
            "weekly": Decimal("52"),
            "biweekly": Decimal("26"),
            "semimonthly": Decimal("24"),
            "monthly": Decimal("12")
        }
        period_count = periods[pay_period]
        annual_income = income if is_annual else income * period_count
        
        # Calculate standard deduction
        standard_ded = self.STANDARD_DEDUCTION[filing_status]
        
        # Calculate taxable income
        taxable_income = max(annual_income - standard_ded, Decimal("0"))
        
        # Find tax bracket and calculate tax
        brackets = self.TAX_BRACKETS[filing_status]
        state_tax = Decimal("0")
        marginal_rate = Decimal("0")
        
        for bracket in brackets:
            if bracket["max"] is None or taxable_income <= bracket["max"]:
                excess = taxable_income - bracket["min"]
                state_tax = bracket["base"] + (excess * bracket["rate"])
                marginal_rate = bracket["rate"]
                break
                
        # Convert to per-period if needed
        if not is_annual:
            state_tax = state_tax / period_count
            
        # Calculate effective rate
        effective_rate = state_tax / annual_income if annual_income > 0 else Decimal("0")
        
        return StateTaxResult(
            state_tax=state_tax,
            local_taxes={},  # No local taxes in CA
            credits={},
            deductions={"standard": standard_ded},
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            warnings=None,
            errors=None
        )
        
    def get_ui_components(self) -> Dict[str, Any]:
        """Define CA-specific UI components for Streamlit."""
        def render(container):
            container.subheader("California Tax Options")
            
            filing_status = container.selectbox(
                "CA Filing Status",
                self.available_filing_statuses,
                help="Select your California filing status"
            )
            
            # Return inputs
            return {
                "filing_status": filing_status
            }
            
        return {"render": render} 