"""
User Interface components for the Crypto Dashboard
Fixed imports - using only existing components
"""

# Import dos componentes que existem
from .dashboard import Dashboard
from .loading_screen import draw_loading_screen
from .crypto_table import CryptoTable
from .news_panel import draw_news_panel
from .fear_greed_chart import draw_fear_greed_chart
from .effects import FloatingEffect, PulseEffect, ParticleEffect, GlowEffect
from .modal_manager import ModalManager

print("✅ Core UI components loaded successfully")

__all__ = [
    'Dashboard',
    'draw_loading_screen', 
    'CryptoTable',
    'draw_news_panel',
    'draw_fear_greed_chart',
    'FloatingEffect',
    'PulseEffect', 
    'ParticleEffect',
    'GlowEffect',
    'ModalManager'
]