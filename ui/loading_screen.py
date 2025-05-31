"""
Loading screen component
"""

import pygame
import time
from config.settings import COLORS, FONT_SIZES
from utils.data_loader import loading_state, loading_lock

def draw_loading_screen(surface):
    """Draw enhanced loading screen with progress indicators"""
    surface.fill(COLORS['background'])
    width, height = surface.get_size()
    
    # Main title
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    title_surface = title_font.render("Crypto Market Dashboard", True, COLORS['text_primary'])
    title_rect = title_surface.get_rect(center=(width // 2, height // 2 - 100))
    surface.blit(title_surface, title_rect)
    
    # Subtitle
    subtitle_font = pygame.font.SysFont("Arial", 18)
    subtitle_surface = subtitle_font.render("Loading market data...", True, COLORS['text_secondary'])
    subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 2 - 60))
    surface.blit(subtitle_surface, subtitle_rect)
    
    # Progress indicators
    status_font = pygame.font.SysFont("Arial", 14)
    y_offset = height // 2 - 20
    
    with loading_lock:
        states = loading_state.copy()
    
    status_items = [
        ("Cryptocurrency Data (500 coins)", states['crypto_data']),
        ("News Articles", states['news_data']),
        ("Fear & Greed Index", states['fear_greed_data']),
        ("Cryptocurrency Logos", states['logos_started']),
        ("Initializing Bubbles", states['bubbles_ready'])
    ]
    
    for i, (item, loaded) in enumerate(status_items):
        color = COLORS['positive'] if loaded else COLORS['neutral']
        status = "✓" if loaded else "○"
        text = f"{status} {item}"
        
        text_surface = status_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(width // 2, y_offset + i * 25))
        surface.blit(text_surface, text_rect)
    
    # Animated loading indicator
    current_time = time.time()
    dots = "." * (int(current_time * 2) % 4)
    loading_text = f"Please wait{dots}"
    loading_surface = status_font.render(loading_text, True, COLORS['text_secondary'])
    loading_rect = loading_surface.get_rect(center=(width // 2, y_offset + len(status_items) * 25 + 30))
    surface.blit(loading_surface, loading_rect)