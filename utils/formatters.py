"""
Text and number formatting utilities
"""

def format_large_number(number):
    """Format large numbers with K, M, B, T suffixes"""
    if not number or number == 0:
        return "N/A"
    
    if number >= 1e12:
        return f"${number/1e12:.1f}T"
    elif number >= 1e9:
        return f"${number/1e9:.1f}B"
    elif number >= 1e6:
        return f"${number/1e6:.1f}M"
    elif number >= 1e3:
        return f"${number/1e3:.1f}K"
    else:
        return f"${number:.2f}"

def format_supply(supply):
    """Format supply numbers"""
    if not supply or supply == 0:
        return "N/A"
    
    if supply >= 1e12:
        return f"{supply/1e12:.1f}T"
    elif supply >= 1e9:
        return f"{supply/1e9:.1f}B"
    elif supply >= 1e6:
        return f"{supply/1e6:.1f}M"
    else:
        return f"{supply:,.0f}"

def format_price(price):
    """Format price with appropriate decimal places"""
    if not price or price == 0:
        return "N/A"
    
    if price < 0.01:
        return f"${price:.6f}"
    elif price < 1:
        return f"${price:.4f}"
    else:
        return f"${price:,.2f}"

def format_percentage(percentage):
    """Format percentage with color coding"""
    if percentage is None:
        return "N/A", (150, 150, 150)
    
    color = (100, 255, 100) if percentage >= 0 else (255, 100, 100)
    return f"{percentage:+.2f}%", color