from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class StateTaxResult:
    """Standard result format for state tax calculations."""
    state_tax: Decimal
    local_taxes: Dict[str, Decimal]  # e.g., {"nyc": Decimal("100.00")}
    credits: Dict[str, Decimal]  # e.g., {"household": Decimal("50.00")}
    deductions: Dict[str, Decimal]  # e.g., {"standard": Decimal("12000.00")}
    effective_rate: Decimal
    marginal_rate: Decimal
    warnings: list[str] = None
    errors: list[str] = None

class StateTaxCalculator(ABC):
    """Abstract base class for state tax calculators."""
    
    @property
    @abstractmethod
    def state_code(self) -> str:
        """Two-letter state code (e.g., 'NY')"""
        pass
        
    @property
    @abstractmethod
    def state_name(self) -> str:
        """Full state name (e.g., 'New York')"""
        pass
        
    @property
    @abstractmethod
    def has_local_tax(self) -> bool:
        """Whether this state has any local/city taxes"""
        pass
        
    @property
    @abstractmethod
    def available_filing_statuses(self) -> list[str]:
        """List of valid filing statuses for this state"""
        pass
        
    @abstractmethod
    def get_local_jurisdictions(self) -> list[str]:
        """Return list of localities that have their own tax rates"""
        pass
        
    @abstractmethod
    def calculate(
        self,
        income: Decimal,
        filing_status: str,
        pay_period: str,
        is_annual: bool = False,
        **kwargs
    ) -> StateTaxResult:
        """
        Calculate state taxes based on inputs.
        
        Args:
            income: Gross income (annual if is_annual=True, else per period)
            filing_status: Filing status (must be in available_filing_statuses)
            pay_period: One of ['weekly', 'biweekly', 'semimonthly', 'monthly']
            is_annual: Whether income is annual (True) or per-period (False)
            **kwargs: State-specific optional parameters
            
        Returns:
            StateTaxResult object containing tax calculation details
        """
        pass
        
    @abstractmethod
    def get_ui_components(self) -> Dict[str, Any]:
        """
        Return state-specific UI components for Streamlit.
        
        Returns:
            Dict of component definitions that app.py will render
        """
        pass 