import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Required for Streamlit
from decimal import Decimal

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
    
    # Add value labels on top of each bar
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
    
    # Format y-axis labels as currency
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
    
    # Add value labels on top of each bar
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