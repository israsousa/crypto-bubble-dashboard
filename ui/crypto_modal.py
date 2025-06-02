"""
Professional Crypto Chart - Modern Design matching reference image
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

class ModernCryptoChart:
    """Modern crypto chart matching the reference design"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Layout based on reference image
        self.header_height = 80
        self.timeframe_height = 50
        self.chart_x = 60
        self.chart_y = self.header_height + self.timeframe_height + 20
        self.chart_width = width - 340  # Leave space for sidebar
        self.chart_height = height - self.chart_y - 60
        
        # Sidebar
        self.sidebar_x = self.chart_x + self.chart_width + 40
        self.sidebar_width = 240
        
        # State
        self.time_range = "7D"
        self.hovered_point = None
        self.pinned_point = None
        
        # Data
        self.data_points = []
        self.min_point = None
        self.max_point = None
        
        # Time ranges matching reference
        self.time_ranges = ["1D", "7D", "30D", "90D", "1Y"]
        self.range_buttons = self._create_range_buttons()
        
        # Colors - gray theme
        self.chart_color = (107, 114, 128)  # Gray-500
        self.grid_color = (55, 65, 81)
        self.bg_color = (17, 24, 39)
        self.text_color = (156, 163, 175)
        self.accent_color = (59, 130, 246)
        
        # Fonts
        self.font_large = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 14)
        self.font_tiny = pygame.font.SysFont("Segoe UI", 12)
        
        # Generate initial data
        self.generate_data()
        
    def _create_range_buttons(self):
        """Create timeframe buttons matching reference"""
        buttons = []
        button_width = 60
        button_height = 35
        start_x = self.chart_x
        start_y = self.header_height + 10
        
        for i, range_name in enumerate(self.time_ranges):
            x = start_x + i * (button_width + 10)
            rect = pygame.Rect(x, start_y, button_width, button_height)
            buttons.append({
                'rect': rect,
                'range': range_name,
                'active': range_name == self.time_range
            })
        return buttons
    
    def generate_data(self):
        """Generate enhanced realistic crypto data"""
        points_count = {
            '1D': 24, '7D': 168, '30D': 30, '90D': 90, '1Y': 365
        }[self.time_range]
        
        data = []
        base_price = 655.95
        
        for i in range(points_count):
            # More realistic price movement
            volatility = {'1D': 0.01, '7D': 0.02, '30D': 0.03, '90D': 0.05, '1Y': 0.1}[self.time_range]
            
            # Create realistic trends
            if self.time_range == '1Y':
                trend = math.sin(i / points_count * math.pi * 2) * 0.15 + math.cos(i / points_count * math.pi * 4) * 0.05
            elif self.time_range in ['30D', '90D']:
                trend = math.sin(i / points_count * math.pi * 3) * 0.08
            else:
                trend = math.sin(i / points_count * math.pi * 6) * 0.03
            
            # Add realistic noise
            noise = (random.random() - 0.5) * volatility
            momentum = math.sin(i / points_count * math.pi * 8) * 0.02
            
            price = base_price * (1 + trend + noise + momentum)
            price = max(price, base_price * 0.5)  # Floor price
            
            # Enhanced time calculation
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
            
            # Calculate volume (realistic simulation)
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
        """Calculate realistic performance statistics"""
        if len(self.data_points) < 2:
            return
            
        current = self.data_points[-1]['price']
        first = self.data_points[0]['price']
        
        # Calculate actual performance for current timeframe
        current_change = ((current - first) / first) * 100
        
        # Simulate other timeframes with realistic variations
        self.performance_stats = {
            '1D': current_change + random.uniform(-0.5, 0.5),
            '7D': current_change + random.uniform(-2, 2), 
            '30D': current_change + random.uniform(-5, 5),
            '90D': current_change + random.uniform(-10, 10),
            '1Y': current_change + random.uniform(-20, 20)
        }
        
        # Ensure current timeframe shows actual calculated change
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
    
    def find_nearest_point(self, mouse_pos: Tuple[int, int]) -> Optional[Dict]:
        """Find nearest data point to mouse position with crosshair"""
        if not self.data_points:
            return None
            
        mouse_x, mouse_y = mouse_pos
        
        # Check if mouse is in chart area
        if not (self.chart_x <= mouse_x <= self.chart_x + self.chart_width and
                self.chart_y <= mouse_y <= self.chart_y + self.chart_height):
            return None
        
        # Find closest X position (snap to chart line)
        chart_relative_x = mouse_x - self.chart_x
        data_index = round((chart_relative_x / self.chart_width) * (len(self.data_points) - 1))
        data_index = max(0, min(data_index, len(self.data_points) - 1))
        
        point = self.data_points[data_index]
        px, py = self.get_chart_position(point['index'], point['price'])
        
        # Return point with screen coordinates for crosshair
        return {
            **point,
            'screen_x': px,
            'screen_y': py
        }
    
    def handle_mouse_move(self, mouse_pos: Tuple[int, int]):
        """Handle mouse movement for hover detection"""
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
            if self.pinned_point and self.pinned_point['index'] == self.hovered_point['index']:
                self.pinned_point = None
            else:
                self.pinned_point = self.hovered_point
            return True
        
        return False
    
    def draw_header(self, surface: pygame.Surface, coin_data: dict):
        """Draw header matching reference design"""
        # Logo
        logo_size = 48
        logo_x, logo_y = 30, 20
        
        # Try to load actual logo
        symbol = coin_data.get('symbol', 'BTC').lower()
        logo_path = f"assets/logos/{symbol}.png"
        
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                surface.blit(logo, (logo_x, logo_y))
            except:
                # Fallback circle
                pygame.draw.circle(surface, self.accent_color, 
                                 (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        else:
            # Fallback circle
            pygame.draw.circle(surface, self.accent_color, 
                             (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        
        # Symbol and name
        symbol_text = coin_data.get('symbol', 'BTC').upper()
        symbol_surface = self.font_large.render(symbol_text, True, (255, 255, 255))
        surface.blit(symbol_surface, (logo_x + logo_size + 15, logo_y + 5))
        
        name_text = coin_data.get('symbol', 'BTC').upper()  # Use symbol, not full name
        name_surface = self.font_small.render(name_text, True, self.text_color)
        surface.blit(name_surface, (logo_x + logo_size + 15, logo_y + 35))
        
        # Price and change (right aligned)
        current_price = coin_data.get('current_price', 655.95)
        price_text = f"${current_price:.2f}"
        price_surface = self.font_large.render(price_text, True, (255, 255, 255))
        
        change_24h = coin_data.get('price_change_percentage_24h', -0.54) or -0.54
        change_color = (34, 197, 94) if change_24h >= 0 else (239, 68, 68)
        change_text = f"{change_24h:+.2f}%"
        change_surface = self.font_medium.render(change_text, True, change_color)
        
        # Right align
        price_x = self.width - price_surface.get_width() - 60
        surface.blit(price_surface, (price_x, logo_y + 5))
        surface.blit(change_surface, (price_x, logo_y + 35))
        
        # Close button
        close_size = 32
        close_x = self.width - close_size - 15
        close_y = 15
        
        pygame.draw.rect(surface, (120, 50, 50), 
                        (close_x, close_y, close_size, close_size), border_radius=4)
        
        # X symbol
        center_x = close_x + close_size // 2
        center_y = close_y + close_size // 2
        line_len = close_size // 4
        
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 2)
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 2)
    
    def draw_timeframe_buttons(self, surface: pygame.Surface):
        """Draw timeframe buttons matching reference"""
        for button in self.range_buttons:
            if button['active']:
                bg_color = (55, 65, 81)
                text_color = (255, 255, 255)
                border_color = (75, 85, 99)
            else:
                bg_color = (31, 41, 55)
                text_color = self.text_color
                border_color = (55, 65, 81)
            
            pygame.draw.rect(surface, bg_color, button['rect'], border_radius=6)
            pygame.draw.rect(surface, border_color, button['rect'], 1, border_radius=6)
            
            text_surface = self.font_small.render(button['range'], True, text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            surface.blit(text_surface, text_rect)
        
        # Chart title
        title_text = f"{self.time_range}"
        title_surface = self.font_medium.render(title_text, True, (255, 255, 255))
        surface.blit(title_surface, (self.chart_x, self.chart_y - 30))
    
    def draw_grid(self, surface: pygame.Surface):
        """Draw enhanced grid with better time labels"""
        # Horizontal lines
        for i in range(6):
            y = self.chart_y + (i / 5) * self.chart_height
            pygame.draw.line(surface, self.grid_color, 
                           (self.chart_x, y), (self.chart_x + self.chart_width, y), 1)
        
        # Vertical lines
        for i in range(7):
            x = self.chart_x + (i / 6) * self.chart_width
            pygame.draw.line(surface, self.grid_color,
                           (x, self.chart_y), (x, self.chart_y + self.chart_height), 1)
        
        # Enhanced Y-axis labels with better formatting
        if self.data_points:
            min_price = self.min_point['price']
            max_price = self.max_point['price']
            price_range = max_price - min_price or 1
            
            for i in range(6):
                price = min_price + (i / 5) * price_range
                y = self.chart_y + self.chart_height - (i / 5) * self.chart_height
                
                # Better price formatting
                if price >= 1000:
                    price_text = f"${price:.0f}"
                elif price >= 100:
                    price_text = f"${price:.1f}"
                else:
                    price_text = f"${price:.2f}"
                
                text_surface = self.font_tiny.render(price_text, True, self.text_color)
                surface.blit(text_surface, (self.chart_x - 55, y - 8))
        
        # Enhanced X-axis labels with smart time formatting
        if self.data_points and len(self.data_points) > 1:
            for i in range(7):
                data_index = int((i / 6) * (len(self.data_points) - 1))
                point = self.data_points[data_index]
                x = self.chart_x + (i / 6) * self.chart_width
                
                # Smart time formatting based on range
                if self.time_range == '1D':
                    if i % 2 == 0:  # Show every other hour
                        time_text = point['date'].strftime("%H:%M")
                    else:
                        continue
                elif self.time_range == '7D':
                    time_text = point['date'].strftime("%a\n%H:%M")
                elif self.time_range == '30D':
                    time_text = point['date'].strftime("%d/%m")
                elif self.time_range == '90D':
                    if point['date'].day in [1, 15]:  # Show 1st and 15th
                        time_text = point['date'].strftime("%d/%m")
                    else:
                        continue
                else:  # 1Y
                    if point['date'].day == 1:  # Show first of month
                        time_text = point['date'].strftime("%b\n%Y")
                    else:
                        continue
                
                # Multi-line text support
                lines = time_text.split('\n')
                for j, line in enumerate(lines):
                    text_surface = self.font_tiny.render(line, True, self.text_color)
                    text_rect = text_surface.get_rect(center=(x, self.chart_y + self.chart_height + 15 + j * 12))
                    surface.blit(text_surface, text_rect)
    
    def draw_chart_line(self, surface: pygame.Surface):
        """Draw clean professional chart line"""
        if len(self.data_points) < 2:
            return
        
        # Create points
        points = []
        for point in self.data_points:
            x, y = self.get_chart_position(point['index'], point['price'])
            points.append((x, y))
        
        # Draw filled area
        fill_points = points.copy()
        fill_points.append((self.chart_x + self.chart_width, self.chart_y + self.chart_height))
        fill_points.append((self.chart_x, self.chart_y + self.chart_height))
        
        # Create gradient fill
        fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(fill_surface, (*self.chart_color, 30), fill_points)
        surface.blit(fill_surface, (0, 0))
        
        # Draw main line (no points)
        pygame.draw.lines(surface, self.chart_color, False, points, 2)
        
        # Draw min/max markers only
        if self.min_point and self.max_point:
            # Min marker (red circle only)
            min_x, min_y = self.get_chart_position(self.min_point['index'], self.min_point['price'])
            pygame.draw.circle(surface, (239, 68, 68), (min_x, min_y), 5)
            
            # Min label
            min_text = f"${self.min_point['price']:.2f}"
            min_surface = self.font_tiny.render(min_text, True, (239, 68, 68))
            label_x = min_x - min_surface.get_width() // 2
            label_y = min_y + 15
            
            # Background for label
            pygame.draw.rect(surface, (17, 24, 39), 
                           (label_x - 4, label_y - 2, min_surface.get_width() + 8, 14))
            surface.blit(min_surface, (label_x, label_y))
            
            # Max marker (green circle only)
            max_x, max_y = self.get_chart_position(self.max_point['index'], self.max_point['price'])
            pygame.draw.circle(surface, (34, 197, 94), (max_x, max_y), 5)
            
            # Max label
            max_text = f"${self.max_point['price']:.2f}"
            max_surface = self.font_tiny.render(max_text, True, (34, 197, 94))
            label_x = max_x - max_surface.get_width() // 2
            label_y = max_y - 20
            
            # Background for label
            pygame.draw.rect(surface, (17, 24, 39), 
                           (label_x - 4, label_y - 2, max_surface.get_width() + 8, 14))
            surface.blit(max_surface, (label_x, label_y))
    
    def draw_crosshair(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw crosshair cursor on chart"""
        if not self.hovered_point:
            return
            
        point = self.hovered_point
        if 'screen_x' not in point or 'screen_y' not in point:
            return
        
        x, y = point['screen_x'], point['screen_y']
        
        # Crosshair lines
        crosshair_color = (156, 163, 175, 180)
        
        # Vertical line
        pygame.draw.line(surface, crosshair_color[:3], 
                        (x, self.chart_y), (x, self.chart_y + self.chart_height), 1)
        
        # Horizontal line  
        pygame.draw.line(surface, crosshair_color[:3], 
                        (self.chart_x, y), (self.chart_x + self.chart_width, y), 1)
        
        # Center point
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 4)
        pygame.draw.circle(surface, self.chart_color, (x, y), 3)
    
    def draw_interactive_points(self, surface: pygame.Surface):
        """Draw hover and pinned points - simplified"""
        # Only draw pinned point if exists
        if self.pinned_point:
            if 'screen_x' in self.pinned_point and 'screen_y' in self.pinned_point:
                x, y = self.pinned_point['screen_x'], self.pinned_point['screen_y']
            else:
                x, y = self.get_chart_position(self.pinned_point['index'], self.pinned_point['price'])
            
            # Pinned marker
            pygame.draw.circle(surface, (245, 158, 11), (x, y), 8, 2)
            pygame.draw.circle(surface, (245, 158, 11), (x, y), 4)
    
    def draw_sidebar(self, surface: pygame.Surface, coin_data: dict):
        """Draw market data sidebar matching reference"""
        # Sidebar background
        sidebar_rect = pygame.Rect(self.sidebar_x, self.chart_y, self.sidebar_width, self.chart_height)
        pygame.draw.rect(surface, (31, 41, 55), sidebar_rect, border_radius=8)
        pygame.draw.rect(surface, (55, 65, 81), sidebar_rect, 1, border_radius=8)
        
        # Title
        title_surface = self.font_medium.render("MARKET DATA", True, (255, 255, 255))
        surface.blit(title_surface, (self.sidebar_x + 20, self.chart_y + 20))
        
        # Market stats
        stats = [
            ("Market Cap", format_large_number(coin_data.get('market_cap', 95700000000))),
            ("Volume 24h", format_large_number(coin_data.get('total_volume', 1622700000))),
            ("Market Rank", f"#{coin_data.get('market_cap_rank', 5)}"),
            ("Circulating Supply", format_supply(coin_data.get('circulating_supply', 145900000)))
        ]
        
        y_offset = self.chart_y + 60
        for i, (label, value) in enumerate(stats):
            current_y = y_offset + i * 50
            
            # Label
            label_surface = self.font_tiny.render(label, True, self.text_color)
            surface.blit(label_surface, (self.sidebar_x + 20, current_y))
            
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
            surface.blit(value_surface, (self.sidebar_x + 20, current_y + 15))
    
    def draw_tooltip(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw enhanced floating tooltip that follows crosshair"""
        point = self.pinned_point or self.hovered_point
        if not point:
            return
        
        # Enhanced tooltip content
        price_text = f"${point['price']:.2f}"
        
        # Smart date formatting
        if self.time_range == '1D':
            time_text = point['date'].strftime("%H:%M")
        elif self.time_range == '7D':
            time_text = point['date'].strftime("%a %H:%M")
        elif self.time_range in ['30D', '90D']:
            time_text = point['date'].strftime("%d/%m %H:%M")
        else:  # 1Y
            time_text = point['date'].strftime("%d/%m/%Y")
        
        # Volume formatting
        volume = point.get('volume', 0)
        if volume >= 1e9:
            volume_text = f"Vol: ${volume/1e9:.1f}B"
        elif volume >= 1e6:
            volume_text = f"Vol: ${volume/1e6:.1f}M"
        else:
            volume_text = f"Vol: ${volume/1e3:.0f}K"
        
        # Calculate change from previous point
        change_text = ""
        if point['index'] > 0:
            prev_point = self.data_points[point['index'] - 1]
            change = ((point['price'] - prev_point['price']) / prev_point['price']) * 100
            change_text = f"{change:+.2f}%"
        
        padding = 12
        tooltip_width = 140
        tooltip_height = 85 if change_text else 65
        
        # Position tooltip near crosshair
        if self.pinned_point:
            tooltip_x = self.pinned_point.get('screen_x', mouse_pos[0]) + 20
            tooltip_y = self.pinned_point.get('screen_y', mouse_pos[1]) - tooltip_height - 10
        else:
            tooltip_x = mouse_pos[0] + 20
            tooltip_y = mouse_pos[1] - tooltip_height - 10
        
        # Keep on screen
        tooltip_x = max(5, min(tooltip_x, self.width - tooltip_width - 5))
        tooltip_y = max(5, min(tooltip_y, self.height - tooltip_height - 5))
        
        # Enhanced background with subtle shadow
        shadow_offset = 2
        pygame.draw.rect(surface, (0, 0, 0, 50), 
                        (tooltip_x + shadow_offset, tooltip_y + shadow_offset, tooltip_width, tooltip_height), 
                        border_radius=8)
        
        bg_color = (45, 55, 72) if self.pinned_point else (31, 41, 55)
        border_color = (245, 158, 11) if self.pinned_point else (107, 114, 128)
        
        pygame.draw.rect(surface, bg_color, 
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height), border_radius=8)
        pygame.draw.rect(surface, border_color, 
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2, border_radius=8)
        
        # Content
        y_offset = tooltip_y + padding
        
        # Price
        price_surface = self.font_medium.render(price_text, True, (255, 255, 255))
        surface.blit(price_surface, (tooltip_x + padding, y_offset))
        y_offset += 18
        
        # Time
        time_surface = self.font_tiny.render(time_text, True, self.text_color)
        surface.blit(time_surface, (tooltip_x + padding, y_offset))
        y_offset += 15
        
        # Volume
        volume_surface = self.font_tiny.render(volume_text, True, (156, 163, 175))
        surface.blit(volume_surface, (tooltip_x + padding, y_offset))
        y_offset += 15
        
        # Change
        if change_text:
            change_color = (34, 197, 94) if change_text.startswith('+') else (239, 68, 68)
            change_surface = self.font_tiny.render(change_text, True, change_color)
            surface.blit(change_surface, (tooltip_x + padding, y_offset))
        
        # Pin indicator
        if self.pinned_point:
            pin_surface = self.font_tiny.render("📌", True, (245, 158, 11))
            surface.blit(pin_surface, (tooltip_x + tooltip_width - 25, tooltip_y + 5))
    
    def render(self, surface: pygame.Surface, mouse_pos: Tuple[int, int], coin_data: dict):
        """Main render method with professional styling"""
        surface.fill(self.bg_color)
        
        self.draw_header(surface, coin_data)
        self.draw_timeframe_buttons(surface)
        self.draw_grid(surface)
        self.draw_chart_line(surface)
        self.draw_crosshair(surface, mouse_pos)  # Add crosshair
        self.draw_interactive_points(surface)
        self.draw_sidebar(surface, coin_data)
        self.draw_tooltip(surface, mouse_pos)

# Integration with existing modal system
class ModernCryptoModal:
    """Modern modal with reference design"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.is_active = False
        
        self.width = int(screen_size[0] * 0.9)
        self.height = int(screen_size[1] * 0.9)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        self.chart = ModernCryptoChart(self.width, self.height)
        
    def handle_click(self, pos: tuple) -> bool:
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        
        if not (0 <= relative_pos[0] <= self.width and 0 <= relative_pos[1] <= self.height):
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
            
        modal_surface = pygame.Surface((self.width, self.height))
        mouse_pos = pygame.mouse.get_pos()
        relative_mouse = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        
        self.chart.render(modal_surface, relative_mouse, self.coin_data)
        
        surface.blit(modal_surface, (self.x, self.y))

# Export
ProfessionalCryptoModal = ModernCryptoModal