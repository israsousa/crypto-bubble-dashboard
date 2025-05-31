"""
Main Dashboard UI components and layout management
"""

import pygame
from config.settings import *
from data.crypto_api import (
    fetch_crypto_data, fetch_crypto_news, fetch_fear_greed_index,
    get_crypto_data, get_news_data, get_fear_greed_data
)
from ui.crypto_table import CryptoTable
from ui.news_panel import draw_news_panel
from ui.fear_greed_chart import draw_fear_greed_chart
from utils.data_loader import (
    loading_complete, update_loading_state,
    data_lock, news_lock, fear_greed_lock
)
from utils.rank_tracker import update_daily_rank_tracking
from utils.logo_loader import preload_top_logos
from threading import Thread
import time

class Dashboard:
    """Main dashboard class managing all UI components"""
    
    def __init__(self):
        self.crypto_table = CryptoTable()
        self.last_update = time.time()
        self.layout_cache = {}
        self.last_screen_size = (0, 0)
        
    def load_initial_data(self):
        """Load initial data for the dashboard"""
        print("Loading initial data...")
        
        # Load crypto data first
        initial_data = fetch_crypto_data()
        if initial_data:
            with data_lock:
                from data.crypto_api import crypto_data
                crypto_data.clear()
                crypto_data.extend(initial_data)
            
            update_daily_rank_tracking(initial_data)
            update_loading_state('crypto_data', True)
            print(f"Loaded {len(initial_data)} cryptocurrencies")
            
            # Start logo preloading
            Thread(target=preload_top_logos, args=(initial_data, 50), daemon=True).start()
        
        # Load news data
        initial_news = fetch_crypto_news()
        if initial_news:
            with news_lock:
                from data.crypto_api import news_list
                news_list.clear()
                news_list.extend(initial_news)
            
            update_loading_state('news_data', True)
            print(f"Loaded {len(initial_news)} news articles")
        
        # Load fear & greed data
        initial_fear_greed = fetch_fear_greed_index()
        if initial_fear_greed:
            with fear_greed_lock:
                from data.crypto_api import fear_greed_data
                fear_greed_data.update({
                    'value': initial_fear_greed['current']['value'],
                    'label': initial_fear_greed['current']['label'],
                    'timestamp': initial_fear_greed['current']['timestamp'],
                    'yesterday': initial_fear_greed['yesterday'],
                    'last_week': initial_fear_greed['last_week'],
                    'last_month': initial_fear_greed['last_month'],
                    'trend_7d': initial_fear_greed['trend_7d'],
                    'trend_30d': initial_fear_greed['trend_30d'],
                    'last_updated': time.time()
                })
            
            update_loading_state('fear_greed_data', True)
            print("Enhanced Fear & Greed Index loaded")
    
    def is_loaded(self):
        """Check if dashboard is fully loaded"""
        return loading_complete.is_set()
    
    def force_complete_loading(self):
        """Force complete loading (for manual skip)"""
        loading_complete.set()
    
    def force_layout_update(self):
        """Force layout recalculation (for fullscreen transitions)"""
        print("🔄 Dashboard: Forcing layout update...")
        self.layout_cache.clear()
        self.last_screen_size = (0, 0)  # Force recalculation
        
        # Force crypto table to recalculate
        self.crypto_table = CryptoTable()
        
        print("✅ Dashboard: Layout update complete")
    
    def get_crypto_data(self):
        """Get current cryptocurrency data"""
        return get_crypto_data()
    
    def get_layout_areas(self, screen_size):
        """Calculate layout areas for different components with caching"""
        width, height = screen_size
        
        # Use cache if screen size hasn't changed significantly
        if (abs(width - self.last_screen_size[0]) < 10 and 
            abs(height - self.last_screen_size[1]) < 10 and 
            screen_size in self.layout_cache):
            return self.layout_cache[screen_size]
        
        # Calculate new layout
        layout_areas = {
            'bubble_area': pygame.Rect(0, 0, 
                                     int(width * LAYOUT['bubble_width_ratio']), 
                                     int(height * LAYOUT['bubble_height_ratio'])),
            'table_area': pygame.Rect(0, 
                                    int(height * LAYOUT['bubble_height_ratio']), 
                                    int(width * LAYOUT['bubble_width_ratio']), 
                                    int(height * (1 - LAYOUT['bubble_height_ratio']))),
            'news_area': pygame.Rect(int(width * LAYOUT['bubble_width_ratio']), 0, 
                                   int(width * LAYOUT['news_width_ratio']), 
                                   int(height * LAYOUT['news_height_ratio'])),
            'fear_area': pygame.Rect(int(width * LAYOUT['bubble_width_ratio']), 
                                   int(height * LAYOUT['news_height_ratio']), 
                                   int(width * LAYOUT['news_width_ratio']), 
                                   int(height * LAYOUT['fear_greed_height_ratio']))
        }
        
        # Cache the result
        self.layout_cache[screen_size] = layout_areas
        self.last_screen_size = screen_size
        
        return layout_areas
    
    def update(self):
        """Update dashboard components"""
        # Update crypto table pagination
        self.crypto_table.update()
    
    def render(self, screen):
        """Render all dashboard components"""
        screen_size = screen.get_size()
        layout_areas = self.get_layout_areas(screen_size)
        
        # Clear screen
        screen.fill(COLORS['background'])
        
        # Render table
        table_data = get_crypto_data()
        table_surface = pygame.Surface(layout_areas['table_area'].size)
        self.crypto_table.draw(table_surface, table_data)
        screen.blit(table_surface, layout_areas['table_area'])
        
        # Render news panel
        news_data = get_news_data()
        news_surface = pygame.Surface(layout_areas['news_area'].size)
        draw_news_panel(news_surface, news_data)
        screen.blit(news_surface, layout_areas['news_area'])
        
        # Render Fear & Greed Index
        fear_greed_data = get_fear_greed_data()
        fear_surface = pygame.Surface(layout_areas['fear_area'].size)
        draw_fear_greed_chart(fear_surface, fear_greed_data)
        screen.blit(fear_surface, layout_areas['fear_area'])
        
        # Draw section dividers
        self.draw_dividers(screen, layout_areas)
    
    def draw_dividers(self, screen, layout_areas):
        """Draw dividing lines between sections"""
        width, height = screen.get_size()
        
        # Vertical divider
        pygame.draw.line(screen, COLORS['border'], 
                        (layout_areas['bubble_area'].right, 0), 
                        (layout_areas['bubble_area'].right, height), 2)
        
        # Horizontal divider (table separation)
        pygame.draw.line(screen, COLORS['border'], 
                        (0, layout_areas['bubble_area'].bottom), 
                        (layout_areas['bubble_area'].right, layout_areas['bubble_area'].bottom), 2)
        
        # News/Fear greed divider
        pygame.draw.line(screen, COLORS['border'], 
                        (layout_areas['news_area'].left, layout_areas['news_area'].bottom), 
                        (layout_areas['news_area'].right, layout_areas['news_area'].bottom), 2)