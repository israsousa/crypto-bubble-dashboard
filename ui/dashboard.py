"""
Enhanced Dashboard UI with Timestamps and Berlin Clock
Includes last update timestamp and real-time Berlin timezone clock
"""

import pygame
import time
import datetime
# Removed pytz dependency - using manual timezone offset
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

class TimestampManager:
    """Manages data update timestamps and Berlin clock"""
    
    def __init__(self):
        self.last_crypto_update = None
        self.last_news_update = None
        self.last_fear_greed_update = None
    
    def update_crypto_timestamp(self):
        """Update crypto data timestamp"""
        self.last_crypto_update = time.time()
    
    def update_news_timestamp(self):
        """Update news data timestamp"""
        self.last_news_update = time.time()
    
    def update_fear_greed_timestamp(self):
        """Update fear & greed timestamp"""
        self.last_fear_greed_update = time.time()
    
    def get_last_update_text(self):
        """Get formatted last update text"""
        timestamps = [
            self.last_crypto_update,
            self.last_news_update, 
            self.last_fear_greed_update
        ]
        
        # Filter out None values
        valid_timestamps = [t for t in timestamps if t is not None]
        
        if not valid_timestamps:
            return "Last updated: --:--"
        
        # Use most recent timestamp
        latest_timestamp = max(valid_timestamps)
        update_time = datetime.datetime.fromtimestamp(latest_timestamp)
        
        return f"Last updated: {update_time.strftime('%H:%M')}"
    
    def get_berlin_time_text(self):
        """Get formatted Berlin time using UTC offset"""
        try:
            # Berlin is UTC+1 (CET) or UTC+2 (CEST during DST)
            utc_time = datetime.datetime.utcnow()
            
            # Simple DST calculation for Central Europe
            # DST: Last Sunday in March to last Sunday in October
            year = utc_time.year
            
            # Calculate DST start (last Sunday in March)
            march_31 = datetime.datetime(year, 3, 31)
            dst_start = march_31 - datetime.timedelta(days=march_31.weekday() + 1)
            if dst_start.day < 25:
                dst_start += datetime.timedelta(days=7)
            
            # Calculate DST end (last Sunday in October) 
            oct_31 = datetime.datetime(year, 10, 31)
            dst_end = oct_31 - datetime.timedelta(days=oct_31.weekday() + 1)
            if dst_end.day < 25:
                dst_end += datetime.timedelta(days=7)
            
            # Determine offset (UTC+1 or UTC+2)
            if dst_start <= utc_time.replace(tzinfo=None) < dst_end:
                offset_hours = 2  # CEST (UTC+2)
            else:
                offset_hours = 1  # CET (UTC+1)
            
            berlin_time = utc_time + datetime.timedelta(hours=offset_hours)
            return f"Berlin Time: {berlin_time.strftime('%H:%M:%S')}"
            
        except:
            # Simple fallback to UTC+1
            utc_time = datetime.datetime.utcnow()
            berlin_time = utc_time + datetime.timedelta(hours=1)
            return f"Berlin Time: {berlin_time.strftime('%H:%M:%S')} (CET)"

class EnhancedDashboard:
    """Enhanced dashboard with timestamps and refined UI"""
    
    def __init__(self):
        self.crypto_table = CryptoTable()
        self.timestamp_manager = TimestampManager()
        self.last_update = time.time()
        self.current_layout_areas = None
        self.layout_update_needed = False
        
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
            self.timestamp_manager.update_crypto_timestamp()
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
            self.timestamp_manager.update_news_timestamp()
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
            self.timestamp_manager.update_fear_greed_timestamp()
            print("Enhanced Fear & Greed Index loaded")
    
    def is_loaded(self):
        """Check if dashboard is fully loaded"""
        return loading_complete.is_set()
    
    def force_complete_loading(self):
        """Force complete loading (for manual skip)"""
        loading_complete.set()
    
    def force_layout_update(self):
        """Force layout update for screen size changes"""
        self.layout_update_needed = True
        self.current_layout_areas = None
        print("Dashboard layout update requested")
    
    def get_crypto_data(self):
        """Get current cryptocurrency data"""
        return get_crypto_data()
    
    def get_layout_areas(self, screen_size):
        """Calculate layout areas for different components"""
        width, height = screen_size
        
        # Update layout if needed
        if (self.current_layout_areas is None or 
            self.layout_update_needed or
            (self.current_layout_areas and 
             self.current_layout_areas.get('screen_size') != screen_size)):
            
            self.current_layout_areas = {
                'screen_size': screen_size,
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
            
            self.layout_update_needed = False
            print(f"Layout updated for {screen_size}")
        
        return self.current_layout_areas
    
    def update(self):
        """Update dashboard components and timestamps"""
        self.crypto_table.update()
    
    def render(self, surface):
        """Render all dashboard components with timestamps"""
        screen_size = surface.get_size()
        layout_areas = self.get_layout_areas(screen_size)
        
        # Clear screen
        surface.fill(COLORS['background'])
        
        # Render table
        table_data = get_crypto_data()
        table_surface = pygame.Surface(layout_areas['table_area'].size)
        self.crypto_table.draw(table_surface, table_data)
        surface.blit(table_surface, layout_areas['table_area'])
        
        # Render news panel
        news_data = get_news_data()
        news_surface = pygame.Surface(layout_areas['news_area'].size)
        draw_news_panel(news_surface, news_data)
        surface.blit(news_surface, layout_areas['news_area'])
        
        # Render Fear & Greed Index
        fear_greed_data = get_fear_greed_data()
        fear_surface = pygame.Surface(layout_areas['fear_area'].size)
        draw_fear_greed_chart(fear_surface, fear_greed_data)
        surface.blit(fear_surface, layout_areas['fear_area'])
        
        # Draw section dividers
        self.draw_dividers(surface, layout_areas)
        
        # ENHANCED: Render timestamps
        self.render_timestamps(surface, screen_size)
    
    def render_timestamps(self, surface, screen_size):
        """Render Berlin clock only"""
        width, height = screen_size
        
        # Fonts
        clock_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        
        # Colors
        clock_color = (180, 200, 220)
        
        # Berlin clock (top-right)
        berlin_time_text = self.timestamp_manager.get_berlin_time_text()
        clock_surface = clock_font.render(berlin_time_text, True, clock_color)
        
        clock_x = width - clock_surface.get_width() - 15
        clock_y = 10
        
        # Background for clock
        clock_bg_width = clock_surface.get_width() + 12
        clock_bg_height = clock_surface.get_height() + 6
        clock_bg = pygame.Surface((clock_bg_width, clock_bg_height), pygame.SRCALPHA)
        clock_bg.fill((25, 30, 40, 220))
        
        surface.blit(clock_bg, (clock_x - 6, clock_y - 3))
        surface.blit(clock_surface, (clock_x, clock_y))
    
    def draw_dividers(self, surface, layout_areas):
        """Draw dividing lines between sections with fallback symbols"""
        width, height = surface.get_size()
        border_color = COLORS['border']
        
        # Vertical divider
        pygame.draw.line(surface, border_color, 
                        (layout_areas['bubble_area'].right, 0), 
                        (layout_areas['bubble_area'].right, height), 2)
        
        # Horizontal divider (table separation)
        pygame.draw.line(surface, border_color, 
                        (0, layout_areas['bubble_area'].bottom), 
                        (layout_areas['bubble_area'].right, layout_areas['bubble_area'].bottom), 2)
        
        # News/Fear greed divider
        pygame.draw.line(surface, border_color, 
                        (layout_areas['news_area'].left, layout_areas['news_area'].bottom), 
                        (layout_areas['news_area'].right, layout_areas['news_area'].bottom), 2)

# Backward compatibility
Dashboard = EnhancedDashboard