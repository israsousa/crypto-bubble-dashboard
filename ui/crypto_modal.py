"""
Optimized Professional Crypto Modal with Enhanced Interactions
Fixes pinned point bug and adds axis value tracking
"""

import pygame
import math
import time
import random
import os
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta

from config.settings import COLORS
from utils.formatters import format_large_number, format_supply, format_price
from data.chart_data import HistoricalDataGenerator

class OptimizedCryptoChart:
    """Optimized crypto chart with fixed interactions and axis tracking
    
    Features:
    - Symbol as main title (BTC, ETH, etc.)
    - Full name as subtitle (Bitcoin, Ethereum, etc.)
    - Fixed pinned point bug when changing timeframes
    - Axis value tracking with crosshair
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Reduced margins for more chart space
        self.header_height = 60  # Reduced from 80
        self.timeframe_height = 40  # Reduced from 50
        self.chart_x = 50  # Reduced from 60
        self.chart_y = self.header_height + self.timeframe_height + 15
        self.chart_width = width - 280  # Reduced sidebar space
        self.chart_height = height - self.chart_y - 50
        
        # Sidebar
        self.sidebar_x = self.chart_x + self.chart_width + 30
        self.sidebar_width = 200  # Reduced from 240
        
        # State
        self.time_range = "7D"
        self.hovered_point = None
        self.pinned_point = None
        self.pinned_point_data = None  # Store actual data, not just index
        
        # Data
        self.data_points = []
        self.min_point = None
        self.max_point = None
        
        # Crosshair position
        self.crosshair_x = None
        self.crosshair_y = None
        
        # Close button tracking
        self.close_button_rect = None
        self.close_x = 0
        self.close_y = 0
        
        # Time ranges
        self.time_ranges = ["1D", "7D", "30D", "90D", "1Y"]
        self.range_buttons = self._create_range_buttons()
        
        # Colors
        self.chart_color = (107, 114, 128)
        self.grid_color = (55, 65, 81)
        self.bg_color = (17, 24, 39)
        self.text_color = (156, 163, 175)
        self.accent_color = (59, 130, 246)
        self.crosshair_color = (120, 140, 160)
        
        # Fonts
        self.font_large = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 12)
        self.font_tiny = pygame.font.SysFont("Segoe UI", 10)
        
        # Generate initial data
        self.generate_data()
        
    def _create_range_buttons(self):
        """Create compact timeframe buttons"""
        buttons = []
        button_width = 50  # Reduced from 60
        button_height = 30  # Reduced from 35
        start_x = self.chart_x
        start_y = self.header_height + 8
        
        for i, range_name in enumerate(self.time_ranges):
            x = start_x + i * (button_width + 8)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            buttons.append({
                'rect': rect,
                'range': range_name,
                'active': range_name == self.time_range
            })
        return buttons
    
    def generate_data(self):
        """Generate data and clear pinned point"""
        # Clear pinned point when changing timeframe
        self.pinned_point = None
        self.pinned_point_data = None
        
        points_count = {
            '1D': 24, '7D': 168, '30D': 30, '90D': 90, '1Y': 365
        }[self.time_range]
        
        data = []
        base_price = 655.95
        
        for i in range(points_count):
            volatility = {'1D': 0.01, '7D': 0.02, '30D': 0.03, '90D': 0.05, '1Y': 0.1}[self.time_range]
            
            if self.time_range == '1Y':
                trend = math.sin(i / points_count * math.pi * 2) * 0.15 + math.cos(i / points_count * math.pi * 4) * 0.05
            elif self.time_range in ['30D', '90D']:
                trend = math.sin(i / points_count * math.pi * 3) * 0.08
            else:
                trend = math.sin(i / points_count * math.pi * 6) * 0.03
            
            noise = (random.random() - 0.5) * volatility
            momentum = math.sin(i / points_count * math.pi * 8) * 0.02
            
            price = base_price * (1 + trend + noise + momentum)
            price = max(price, base_price * 0.5)
            price = min(price, base_price * 5.0)
            
            now = datetime.now()
            if self.time_range == '1D':
                date = now - timedelta(hours=points_count - i)
            elif self.time_range == '7D':
                date = now - timedelta(hours=points_count - i)
            elif self.time_range == '30D':
                date = now - timedelta(days=points_count - i)
            elif self.time_range == '90D':
                date = now - timedelta(days=points_count - i)
            else:  # 1Y
                date = now - timedelta(days=points_count - i)
            
            base_volume = 1500000000
            volume_variation = random.uniform(0.7, 1.3)
            volume = base_volume * volume_variation
            
            data.append({
                'date': date,
                'price': price,
                'volume': volume,
                'index': i
            })
        
        self.data_points = data
        self._calculate_min_max()
        self._calculate_performance_stats()
    
    def _calculate_performance_stats(self):
        """Calculate performance statistics"""
        if len(self.data_points) < 2:
            return
            
        current = self.data_points[-1]['price']
        first = self.data_points[0]['price']
        
        current_change = ((current - first) / first) * 100
        
        self.performance_stats = {
            '1D': current_change + random.uniform(-0.5, 0.5),
            '7D': current_change + random.uniform(-2, 2), 
            '30D': current_change + random.uniform(-5, 5),
            '90D': current_change + random.uniform(-10, 10),
            '1Y': current_change + random.uniform(-20, 20)
        }
        
        self.performance_stats[self.time_range] = current_change
    
    def _calculate_min_max(self):
        """Calculate min and max points"""
        if not self.data_points:
            return
        self.min_point = min(self.data_points, key=lambda p: p['price'])
        self.max_point = max(self.data_points, key=lambda p: p['price'])
    
    def get_chart_position(self, point_index: int, price: float) -> Tuple[int, int]:
        """Convert data point to screen coordinates"""
        if not self.data_points:
            return (0, 0)
            
        min_price = self.min_point['price']
        max_price = self.max_point['price']
        price_range = max_price - min_price or 1
        
        x = self.chart_x + (point_index / max(1, len(self.data_points) - 1)) * self.chart_width
        y = self.chart_y + self.chart_height - ((price - min_price) / price_range) * self.chart_height
        
        return (int(x), int(y))
    
    def get_price_from_y(self, y: int) -> float:
        """Get price value from Y coordinate"""
        if not self.data_points:
            return 0
            
        min_price = self.min_point['price']
        max_price = self.max_point['price']
        price_range = max_price - min_price or 1
        
        # Invert Y calculation
        y_ratio = (self.chart_y + self.chart_height - y) / self.chart_height
        price = min_price + (y_ratio * price_range)
        
        return max(min_price, min(max_price, price))
    
    def get_time_from_x(self, x: int) -> Optional[datetime]:
        """Get timestamp from X coordinate"""
        if not self.data_points:
            return None
            
        x_ratio = (x - self.chart_x) / self.chart_width
        index = int(x_ratio * (len(self.data_points) - 1))
        index = max(0, min(index, len(self.data_points) - 1))
        
        return self.data_points[index]['date']
    
    def find_nearest_point(self, mouse_pos: Tuple[int, int]) -> Optional[Dict]:
        """Find nearest data point with crosshair update"""
        if not self.data_points:
            return None
            
        mouse_x, mouse_y = mouse_pos
        
        # Update crosshair position
        if (self.chart_x <= mouse_x <= self.chart_x + self.chart_width and
            self.chart_y <= mouse_y <= self.chart_y + self.chart_height):
            self.crosshair_x = mouse_x
            self.crosshair_y = mouse_y
        else:
            self.crosshair_x = None
            self.crosshair_y = None
            return None
        
        # Find closest X position
        chart_relative_x = mouse_x - self.chart_x
        data_index = round((chart_relative_x / self.chart_width) * (len(self.data_points) - 1))
        data_index = max(0, min(data_index, len(self.data_points) - 1))
        
        point = self.data_points[data_index]
        px, py = self.get_chart_position(point['index'], point['price'])
        
        return {
            **point,
            'screen_x': px,
            'screen_y': py
        }
    
    def handle_mouse_move(self, mouse_pos: Tuple[int, int]):
        """Handle mouse movement"""
        self.hovered_point = self.find_nearest_point(mouse_pos)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks"""
        # Check timeframe buttons
        for button in self.range_buttons:
            if button['rect'].collidepoint(mouse_pos):
                if button['range'] != self.time_range:
                    self.time_range = button['range']
                    for btn in self.range_buttons:
                        btn['active'] = btn['range'] == self.time_range
                    self.generate_data()
                return True
        
        # Check chart clicks for pinning
        if self.hovered_point:
            # Toggle pin on the data point
            if self.pinned_point_data and self.pinned_point_data['index'] == self.hovered_point['index']:
                self.pinned_point = None
                self.pinned_point_data = None
            else:
                self.pinned_point = self.hovered_point
                self.pinned_point_data = self.hovered_point.copy()
            return True
        
        return False
    
    def draw_header(self, surface: pygame.Surface, coin_data: dict):
        """Draw compact header with symbol as title and full name as subtitle"""
        # Logo
        logo_size = 40  # Reduced
        logo_x, logo_y = 25, 15
        
        symbol = coin_data.get('symbol', 'BTC').lower()
        logo_path = f"assets/logos/{symbol}.png"
        
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                surface.blit(logo, (logo_x, logo_y))
            except:
                pygame.draw.circle(surface, self.accent_color, 
                                 (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        else:
            pygame.draw.circle(surface, self.accent_color, 
                             (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        
        # Symbol and name
        # Example: BTC (title) / Bitcoin (subtitle), ETH / Ethereum, etc.
        symbol_text = coin_data.get('symbol', 'BTC').upper()
        symbol_surface = self.font_large.render(symbol_text, True, (255, 255, 255))
        surface.blit(symbol_surface, (logo_x + logo_size + 12, logo_y + 2))
        
        # Full name as subtitle (with fallback and length check)
        full_name = coin_data.get('name', '')
        if not full_name:
            # Fallback: use a mapping for common cryptos
            symbol_to_name = {
                'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'BNB': 'Binance Coin',
                'XRP': 'Ripple', 'ADA': 'Cardano', 'DOGE': 'Dogecoin',
                'SOL': 'Solana', 'DOT': 'Polkadot', 'MATIC': 'Polygon',
                'AVAX': 'Avalanche', 'LINK': 'Chainlink', 'UNI': 'Uniswap',
                'LTC': 'Litecoin', 'ATOM': 'Cosmos', 'NEAR': 'NEAR Protocol',
                'XLM': 'Stellar', 'VET': 'VeChain', 'ALGO': 'Algorand',
                'FTM': 'Fantom', 'SAND': 'The Sandbox', 'MANA': 'Decentraland',
                'MATIC': 'Polygon', 'CRO': 'Crypto.com', 'SHIB': 'Shiba Inu',
                'TRX': 'TRON', 'APT': 'Aptos', 'OP': 'Optimism'
            }
            full_name = symbol_to_name.get(symbol_text, symbol_text)
        
        # Truncate if too long
        if len(full_name) > 25:
            full_name = full_name[:22] + "..."
        name_surface = self.font_small.render(full_name, True, self.text_color)
        surface.blit(name_surface, (logo_x + logo_size + 12, logo_y + 26))
        
        # Price and change
        current_price = coin_data.get('current_price', 655.95)
        price_text = f"${current_price:.2f}"
        price_surface = self.font_large.render(price_text, True, (255, 255, 255))
        
        change_24h = coin_data.get('price_change_percentage_24h', -0.54) or -0.54
        change_color = (34, 197, 94) if change_24h >= 0 else (239, 68, 68)
        change_text = f"{change_24h:+.2f}%"
        change_surface = self.font_medium.render(change_text, True, change_color)
        
        price_x = self.width - price_surface.get_width() - 50
        surface.blit(price_surface, (price_x, logo_y))
        surface.blit(change_surface, (price_x, logo_y + 26))
        
        # Close button (FIXED positioning)
        close_size = 28
        self.close_x = self.width - close_size - 12
        self.close_y = 12
        self.close_button_rect = pygame.Rect(self.close_x, self.close_y, close_size, close_size)
        
        pygame.draw.rect(surface, (120, 50, 50), 
                        self.close_button_rect, border_radius=4)
        
        center_x = self.close_x + close_size // 2
        center_y = self.close_y + close_size // 2
        line_len = close_size // 4
        
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 2)
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 2)
    
    def draw_timeframe_buttons(self, surface: pygame.Surface):
        """Draw compact timeframe buttons"""
        for button in self.range_buttons:
            if button['active']:
                bg_color = (55, 65, 81)
                text_color = (255, 255, 255)
                border_color = (75, 85, 99)
            else:
                bg_color = (31, 41, 55)
                text_color = self.text_color
                border_color = (55, 65, 81)
            
            pygame.draw.rect(surface, bg_color, button['rect'], border_radius=4)
            pygame.draw.rect(surface, border_color, button['rect'], 1, border_radius=4)
            
            text_surface = self.font_small.render(button['range'], True, text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            surface.blit(text_surface, text_rect)
    
    def draw_grid(self, surface: pygame.Surface):
        """Draw grid with axis labels"""
        # Grid with thinner lines
        grid_color_light = (45, 55, 70)  # Lighter grid color
        
        # Horizontal lines (thinner)
        for i in range(6):
            y = self.chart_y + (i / 5) * self.chart_height
            pygame.draw.line(surface, grid_color_light, 
                           (self.chart_x, y), (self.chart_x + self.chart_width, y), 1)
        
        # Vertical lines (thinner)
        for i in range(7):
            x = self.chart_x + (i / 6) * self.chart_width
            pygame.draw.line(surface, grid_color_light,
                           (x, self.chart_y), (x, self.chart_y + self.chart_height), 1)
        
        # Y-axis labels
        if self.data_points:
            min_price = self.min_point['price']
            max_price = self.max_point['price']
            price_range = max_price - min_price or 1
            
            for i in range(6):
                price = min_price + (i / 5) * price_range
                y = self.chart_y + self.chart_height - (i / 5) * self.chart_height
                
                if price >= 1000:
                    price_text = f"${price:.0f}"
                elif price >= 100:
                    price_text = f"${price:.1f}"
                else:
                    price_text = f"${price:.2f}"
                
                text_surface = self.font_tiny.render(price_text, True, self.text_color)
                surface.blit(text_surface, (self.chart_x - 48, y - 8))
        
        # X-axis labels
        if self.data_points and len(self.data_points) > 1:
            for i in range(7):
                data_index = int((i / 6) * (len(self.data_points) - 1))
                point = self.data_points[data_index]
                x = self.chart_x + (i / 6) * self.chart_width
                
                if self.time_range == '1D':
                    if i % 2 == 0:
                        time_text = point['date'].strftime("%H:%M")
                    else:
                        continue
                elif self.time_range == '7D':
                    time_text = point['date'].strftime("%d/%m")
                elif self.time_range == '30D':
                    time_text = point['date'].strftime("%d/%m")
                elif self.time_range == '90D':
                    if point['date'].day in [1, 15]:
                        time_text = point['date'].strftime("%d/%m")
                    else:
                        continue
                else:  # 1Y
                    if point['date'].day == 1:
                        time_text = point['date'].strftime("%b")
                    else:
                        continue
                
                text_surface = self.font_tiny.render(time_text, True, self.text_color)
                text_rect = text_surface.get_rect(center=(x, self.chart_y + self.chart_height + 12))
                surface.blit(text_surface, text_rect)
    
    def draw_chart_line(self, surface: pygame.Surface):
        """Draw chart line with fill"""
        if len(self.data_points) < 2:
            return
        
        points = []
        for point in self.data_points:
            x, y = self.get_chart_position(point['index'], point['price'])
            points.append((x, y))
        
        # Draw filled area
        fill_points = points.copy()
        fill_points.append((self.chart_x + self.chart_width, self.chart_y + self.chart_height))
        fill_points.append((self.chart_x, self.chart_y + self.chart_height))
        
        fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(fill_surface, (*self.chart_color, 20), fill_points)
        surface.blit(fill_surface, (0, 0))
        
        # Draw main line (thinner)
        pygame.draw.lines(surface, self.chart_color, False, points, 1)
        
        # Draw min/max markers
        if self.min_point and self.max_point:
            # Min marker
            min_x, min_y = self.get_chart_position(self.min_point['index'], self.min_point['price'])
            pygame.draw.circle(surface, (239, 68, 68), (min_x, min_y), 4)
            
            min_text = f"${self.min_point['price']:.2f}"
            min_surface = self.font_tiny.render(min_text, True, (239, 68, 68))
            surface.blit(min_surface, (min_x - min_surface.get_width() // 2, min_y + 8))
            
            # Max marker
            max_x, max_y = self.get_chart_position(self.max_point['index'], self.max_point['price'])
            pygame.draw.circle(surface, (34, 197, 94), (max_x, max_y), 4)
            
            max_text = f"${self.max_point['price']:.2f}"
            max_surface = self.font_tiny.render(max_text, True, (34, 197, 94))
            surface.blit(max_surface, (max_x - max_surface.get_width() // 2, max_y - 20))
    
    def draw_crosshair_with_values(self, surface: pygame.Surface):
        """Draw crosshair with axis values"""
        if self.crosshair_x is None or self.crosshair_y is None:
            return
        
        # Draw crosshair lines (thinner)
        pygame.draw.line(surface, self.crosshair_color, 
                        (self.chart_x, self.crosshair_y), 
                        (self.chart_x + self.chart_width, self.crosshair_y), 1)
        pygame.draw.line(surface, self.crosshair_color, 
                        (self.crosshair_x, self.chart_y), 
                        (self.crosshair_x, self.chart_y + self.chart_height), 1)
        
        # Draw crosshair center
        pygame.draw.circle(surface, (255, 255, 255), 
                         (self.crosshair_x, self.crosshair_y), 3)
        pygame.draw.circle(surface, self.crosshair_color, 
                         (self.crosshair_x, self.crosshair_y), 2)
        
        # Draw "+" symbol at crosshair (smaller)
        pygame.draw.line(surface, (255, 255, 255),
                        (self.crosshair_x - 3, self.crosshair_y),
                        (self.crosshair_x + 3, self.crosshair_y), 1)
        pygame.draw.line(surface, (255, 255, 255),
                        (self.crosshair_x, self.crosshair_y - 3),
                        (self.crosshair_x, self.crosshair_y + 3), 1)
        
        # Y-axis value (price)
        price = self.get_price_from_y(self.crosshair_y)
        price_text = f"${price:.2f}"
        price_surface = self.font_tiny.render(price_text, True, (255, 255, 255))
        
        # Price label background
        price_bg_rect = pygame.Rect(self.chart_x - 52, self.crosshair_y - 10, 
                                   50, 20)
        pygame.draw.rect(surface, (40, 50, 65), price_bg_rect)
        pygame.draw.rect(surface, self.crosshair_color, price_bg_rect, 1)
        
        price_rect = price_surface.get_rect(center=price_bg_rect.center)
        surface.blit(price_surface, price_rect)
        
        # X-axis value (time)
        timestamp = self.get_time_from_x(self.crosshair_x)
        if timestamp:
            if self.time_range == '1D':
                time_text = timestamp.strftime("%H:%M")
            else:
                time_text = timestamp.strftime("%d/%m")
            
            time_surface = self.font_tiny.render(time_text, True, (255, 255, 255))
            
            # Time label background
            time_bg_rect = pygame.Rect(self.crosshair_x - 30, 
                                      self.chart_y + self.chart_height + 2, 
                                      60, 18)
            pygame.draw.rect(surface, (40, 50, 65), time_bg_rect)
            pygame.draw.rect(surface, self.crosshair_color, time_bg_rect, 1)
            
            time_rect = time_surface.get_rect(center=time_bg_rect.center)
            surface.blit(time_surface, time_rect)
    
    def draw_interactive_points(self, surface: pygame.Surface):
        """Draw hover and pinned points"""
        # Draw pinned point if exists
        if self.pinned_point_data:
            # Find current position of pinned data
            for point in self.data_points:
                if point['index'] == self.pinned_point_data['index']:
                    x, y = self.get_chart_position(point['index'], point['price'])
                    pygame.draw.circle(surface, (245, 158, 11), (x, y), 8, 2)
                    pygame.draw.circle(surface, (245, 158, 11), (x, y), 4)
                    break
    
    def draw_sidebar(self, surface: pygame.Surface, coin_data: dict):
        """Draw compact market data sidebar"""
        # Sidebar background
        sidebar_rect = pygame.Rect(self.sidebar_x, self.chart_y, self.sidebar_width, self.chart_height)
        pygame.draw.rect(surface, (31, 41, 55), sidebar_rect, border_radius=6)
        pygame.draw.rect(surface, (55, 65, 81), sidebar_rect, 1, border_radius=6)
        
        # Title
        title_surface = self.font_medium.render("MARKET DATA", True, (255, 255, 255))
        surface.blit(title_surface, (self.sidebar_x + 15, self.chart_y + 15))
        
        # Market stats
        stats = [
            ("Market Cap", format_large_number(coin_data.get('market_cap', 95700000000))),
            ("Volume 24h", format_large_number(coin_data.get('total_volume', 1622700000))),
            ("Market Rank", f"#{coin_data.get('market_cap_rank', 5)}"),
            ("Supply", format_supply(coin_data.get('circulating_supply', 145900000)))
        ]
        
        y_offset = self.chart_y + 50
        for i, (label, value) in enumerate(stats):
            current_y = y_offset + i * 45
            
            # Label
            label_surface = self.font_tiny.render(label, True, self.text_color)
            surface.blit(label_surface, (self.sidebar_x + 15, current_y))
            
            # Value
            if "Market Cap" in label:
                color = (34, 197, 94)
            elif "Volume" in label:
                color = (59, 130, 246)
            elif "Rank" in label:
                color = (245, 158, 11)
            else:
                color = (156, 163, 175)
            
            value_surface = self.font_small.render(str(value), True, color)
            surface.blit(value_surface, (self.sidebar_x + 15, current_y + 14))
    
    def draw_tooltip(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw enhanced tooltip"""
        point = self.pinned_point_data or self.hovered_point
        if not point:
            return
        
        # Tooltip content
        price_text = f"${point['price']:.2f}"
        
        if self.time_range == '1D':
            time_text = point['date'].strftime("%H:%M")
        elif self.time_range == '7D':
            time_text = point['date'].strftime("%a %H:%M")
        elif self.time_range in ['30D', '90D']:
            time_text = point['date'].strftime("%d/%m %H:%M")
        else:  # 1Y
            time_text = point['date'].strftime("%d/%m/%Y")
        
        volume = point.get('volume', 0)
        if volume >= 1e9:
            volume_text = f"Vol: ${volume/1e9:.1f}B"
        elif volume >= 1e6:
            volume_text = f"Vol: ${volume/1e6:.1f}M"
        else:
            volume_text = f"Vol: ${volume/1e3:.0f}K"
        
        # Calculate change
        change_text = ""
        if point['index'] > 0:
            prev_point = self.data_points[point['index'] - 1]
            change = ((point['price'] - prev_point['price']) / prev_point['price']) * 100
            change_text = f"{change:+.2f}%"
        
        padding = 10
        tooltip_width = 120
        tooltip_height = 70 if change_text else 55
        
        # Position tooltip
        if self.pinned_point_data:
            # Find screen position of pinned point
            px, py = self.get_chart_position(self.pinned_point_data['index'], 
                                            self.pinned_point_data['price'])
            tooltip_x = px + 15
            tooltip_y = py - tooltip_height - 5
        else:
            tooltip_x = mouse_pos[0] + 15
            tooltip_y = mouse_pos[1] - tooltip_height - 5
        
        # Keep on screen
        tooltip_x = max(5, min(tooltip_x, self.width - tooltip_width - 5))
        tooltip_y = max(5, min(tooltip_y, self.height - tooltip_height - 5))
        
        # Background
        bg_color = (45, 55, 72) if self.pinned_point_data else (31, 41, 55)
        border_color = (245, 158, 11) if self.pinned_point_data else (107, 114, 128)
        
        pygame.draw.rect(surface, bg_color, 
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height), border_radius=6)
        pygame.draw.rect(surface, border_color, 
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 1, border_radius=6)
        
        # Content
        y_offset = tooltip_y + padding
        
        # Price
        price_surface = self.font_medium.render(price_text, True, (255, 255, 255))
        surface.blit(price_surface, (tooltip_x + padding, y_offset))
        y_offset += 16
        
        # Time
        time_surface = self.font_tiny.render(time_text, True, self.text_color)
        surface.blit(time_surface, (tooltip_x + padding, y_offset))
        y_offset += 13
        
        # Volume
        volume_surface = self.font_tiny.render(volume_text, True, (156, 163, 175))
        surface.blit(volume_surface, (tooltip_x + padding, y_offset))
        
        # Change
        if change_text:
            y_offset += 13
            change_color = (34, 197, 94) if change_text.startswith('+') else (239, 68, 68)
            change_surface = self.font_tiny.render(change_text, True, change_color)
            surface.blit(change_surface, (tooltip_x + padding, y_offset))
        
        # Pin indicator
        if self.pinned_point_data:
            pin_surface = self.font_tiny.render("📌", True, (245, 158, 11))
            surface.blit(pin_surface, (tooltip_x + tooltip_width - 20, tooltip_y + 3))
    
    def render(self, surface: pygame.Surface, mouse_pos: Tuple[int, int], coin_data: dict):
        """Main render method"""
        surface.fill(self.bg_color)
        
        self.draw_header(surface, coin_data)
        self.draw_timeframe_buttons(surface)
        self.draw_grid(surface)
        self.draw_chart_line(surface)
        self.draw_crosshair_with_values(surface)
        self.draw_interactive_points(surface)
        self.draw_sidebar(surface, coin_data)
        self.draw_tooltip(surface, mouse_pos)

class OptimizedCryptoModal:
    """Optimized modal with fixed size and better performance"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.is_active = False
        
        # Optimized modal size (smaller)
        self.width = int(screen_size[0] * 0.8)  # Reduced from 0.9
        self.height = int(screen_size[1] * 0.8)  # Reduced from 0.9
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        self.chart = OptimizedCryptoChart(self.width, self.height)
        
    def handle_click(self, pos: tuple) -> bool:
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        
        # Check if clicked outside modal
        if not (0 <= relative_pos[0] <= self.width and 0 <= relative_pos[1] <= self.height):
            self.close()
            return True
        
        # Check close button in chart
        if self.chart.close_button_rect:
            if self.chart.close_button_rect.collidepoint(relative_pos):
                self.close()
                return True
        
        return self.chart.handle_click(relative_pos)
    
    def handle_mouse_move(self, pos: tuple):
        if self.is_active:
            relative_pos = (pos[0] - self.x, pos[1] - self.y)
            self.chart.handle_mouse_move(relative_pos)
    
    def open(self):
        self.is_active = True
        
    def close(self):
        self.is_active = False
        
    def update(self, dt: float):
        pass
        
    def draw(self, surface: pygame.Surface):
        if not self.is_active:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Modal background
        modal_surface = pygame.Surface((self.width, self.height))
        mouse_pos = pygame.mouse.get_pos()
        relative_mouse = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        
        self.chart.render(modal_surface, relative_mouse, self.coin_data)
        
        # Draw modal with border
        surface.blit(modal_surface, (self.x, self.y))
        pygame.draw.rect(surface, (60, 80, 110), 
                        (self.x-1, self.y-1, self.width+2, self.height+2), 2)

# Export as main classes
ProfessionalCryptoModal = OptimizedCryptoModal
ModernCryptoModal = OptimizedCryptoModal