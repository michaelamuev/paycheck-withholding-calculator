from typing import Type, Dict
from .base import StateTaxCalculator
from .ny import NYTaxCalculator
from .ca import CATaxCalculator
from .nj import NJTaxCalculator
from .oh import OHTaxCalculator

# Registry of state calculators
STATE_CALCULATORS: Dict[str, Type[StateTaxCalculator]] = {}

def register_calculator(calculator_class: Type[StateTaxCalculator]):
    """Register a state calculator class."""
    STATE_CALCULATORS[calculator_class().state_code] = calculator_class
    
def get_calculator(state_code: str) -> StateTaxCalculator:
    """Get an instance of a state calculator by state code."""
    if state_code not in STATE_CALCULATORS:
        raise ValueError(f"No calculator registered for state: {state_code}")
    return STATE_CALCULATORS[state_code]()
    
def get_available_states() -> list[str]:
    """Get list of states with registered calculators."""
    return sorted(STATE_CALCULATORS.keys())
    
def get_state_name(state_code: str) -> str:
    """Get full state name from state code."""
    return get_calculator(state_code).state_name

# Register available calculators
register_calculator(NYTaxCalculator)
register_calculator(CATaxCalculator)
register_calculator(NJTaxCalculator)
register_calculator(OHTaxCalculator) 
