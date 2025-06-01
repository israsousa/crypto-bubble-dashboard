"""
Professional Crypto Modal with Elegant Cyberpunk Design
Minimal, clean interface focused on usability and clarity
"""

import pygame
import os
import time
import random
import datetime
import math
from threading import Thread
from typing import List, Tuple, Optional, Dict, Any

from config.settings import COLORS, FONT_SIZES, SYMBOL_TO_ID
from utils.formatters import format_large_number, format_supply, format_price
from data.chart_data import HistoricalDataGenerator

class ProfessionalTooltip:
    """Professional investment-grade tooltip system"""
    
    def __init__(self):
        self.visible = False
        self.position = (0, 0)
        self.data = {}
        self.animation_progress = 0
        self.target_progress = 0
        self.last_update = time.time()
        
    def show(self, pos: Tuple[int, int], data: Dict[str, Any]):
        """Show tooltip with investment-grade data"""
        self.position = pos
        self.data = data
        self.visible = True
        self.target_progress = 1.0
        
    def hide(self):
        """Hide tooltip smoothly"""
        self.target_progress = 0.0
        
    def update(self, dt: float):
        """Update tooltip animation"""
        # Smooth animation
        if self.target_progress > self.animation_progress:
            self.animation_progress = min(1.0, self.animation_progress + dt * 12)
        else:
            self.animation_progress = max(0.0, self.animation_progress - dt * 12)
            
        if self.animation_progress <= 0:
            self.visible = False
            
    def render(self, surface: pygame.Surface):
        """Render professional tooltip"""
        if not self.visible or self.animation_progress <= 0:
            return
            
        # Professional font
        header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        value_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 10)
        
        # Prepare data lines
        lines = []
        if 'price' in self.data:
            price_str = format_price(self.data['price'])
            lines.append(("PRICE", price_str, (100, 255, 180)))
            
        if 'time' in self.data:
            lines.append(("TIME", self.data['time'], (180, 220, 255)))
            
        if 'volume' in self.data:
            volume_str = format_large_number(self.data['volume'])
            lines.append(("VOLUME", volume_str, (255, 200, 120)))
            
        if 'change' in self.data:
            change = self.data['change']
            change_color = (100, 255, 180) if change >= 0 else (255, 120, 120)
            change_str = f"{change:+.2f}%"
            lines.append(("CHANGE", change_str, change_color))
        
        if not lines:
            return
            
        # Calculate dimensions
        padding = 16
        line_spacing = 22
        header_height = 20
        
        max_width = 0
        for label, value, color in lines:
            label_width = label_font.size(label)[0]
            value_width = value_font.size(value)[0]
            total_width = max(label_width, value_width) + padding * 2
            max_width = max(max_width, total_width)
            
        tooltip_width = max(max_width, 180)
        tooltip_height = header_height + len(lines) * line_spacing + padding
        
        # Adjust position to stay on screen
        x, y = self.position
        screen_rect = surface.get_rect()
        
        if x + tooltip_width > screen_rect.right - 10:
            x = screen_rect.right - tooltip_width - 10
        if y + tooltip_height > screen_rect.bottom - 10:
            y = screen_rect.bottom - tooltip_height - 10
            
        # Animation scale
        scale = self.animation_progress
        final_width = int(tooltip_width * scale)
        final_height = int(tooltip_height * scale)
        
        if final_width <= 0 or final_height <= 0:
            return
            
        # Create tooltip surface
        tooltip_surface = pygame.Surface((final_width, final_height), pygame.SRCALPHA)
        
        # Professional background
        pygame.draw.rect(tooltip_surface, (25, 30, 40, 250), 
                        (0, 0, final_width, final_height), border_radius=8)
        pygame.draw.rect(tooltip_surface, (70, 120, 180, 200), 
                        (0, 0, final_width, final_height), 2, border_radius=8)
        
        # Subtle inner border
        pygame.draw.rect(tooltip_surface, (40, 50, 65, 150), 
                        (1, 1, final_width-2, final_height-2), 1, border_radius=7)
        
        # Render content if tooltip is large enough
        if scale > 0.3:
            text_alpha = int(255 * min(1.0, (scale - 0.3) / 0.7))
            
            # Header
            header_text = "DATA POINT"
            header_surface = header_font.render(header_text, True, (200, 220, 255))
            header_surface.set_alpha(text_alpha)
            
            header_x = (final_width - header_surface.get_width()) // 2
            tooltip_surface.blit(header_surface, (header_x, padding // 2))
            
            # Data lines
            current_y = header_height
            for label, value, color in lines:
                # Label
                label_surface = label_font.render(label, True, (160, 180, 200))
                label_surface.set_alpha(text_alpha)
                tooltip_surface.blit(label_surface, (padding, current_y))
                
                # Value
                value_surface = value_font.render(value, True, color)
                value_surface.set_alpha(text_alpha)
                tooltip_surface.blit(value_surface, (padding, current_y + 8))
                
                current_y += line_spacing
                
        surface.blit(tooltip_surface, (x, y))

class ProfessionalChartRenderer:
    """Investment-grade chart renderer with smooth interactions"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.margin = 40
        self.chart_rect = pygame.Rect(
            self.margin, self.margin,
            width - 2 * self.margin, height - 2 * self.margin
        )
        
        self.tooltip = ProfessionalTooltip()
        self.mouse_pos = (0, 0)
        self.hovered_point_index = None
        
        # Professional colors
        self.primary_color = (70, 120, 180)
        self.positive_color = (80, 200, 120)
        self.negative_color = (220, 80, 80)
        self.grid_color = (40, 50, 65)
        self.text_color = (180, 190, 210)
        
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update chart interactions"""
        self.mouse_pos = mouse_pos
        self.tooltip.update(dt)
        
    def get_trend_color(self, change_percent: float) -> Tuple[int, int, int]:
        """Get color based on price trend"""
        if change_percent > 0:
            return self.positive_color
        elif change_percent < 0:
            return self.negative_color
        else:
            return self.primary_color
            
    def render_price_chart(self, data_points: List[Dict], symbol: str, 
                          timeframe_label: str) -> pygame.Surface:
        """Render professional price chart"""
        if not data_points or len(data_points) < 2:
            return self.render_no_data_chart()
            
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        # Process data
        prices = [point['price'] for point in data_points]
        timestamps = [point['timestamp'] for point in data_points]
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else max_price * 0.1
        
        # Calculate trend
        first_price = prices[0]
        last_price = prices[-1]
        change_percent = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
        line_color = self.get_trend_color(change_percent)
        
        # Calculate chart points
        chart_points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i / (len(prices) - 1)) * self.chart_rect.width
            y = self.chart_rect.bottom - ((price - min_price) / price_range) * self.chart_rect.height
            chart_points.append((int(x), int(y)))
            
        # Render professional grid
        self.render_professional_grid(surface)
        
        # Render filled area with smooth gradient
        self.render_chart_fill(surface, chart_points, line_color)
        
        # Render main line with anti-aliasing
        self.render_chart_line(surface, chart_points, line_color)
        
        # Render interactive points
        self.render_interactive_points(surface, chart_points, data_points, line_color)
        
        # Render professional axes
        self.render_professional_axes(surface, min_price, max_price, timestamps)
        
        # Render title
        self.render_professional_title(surface, symbol, timeframe_label, change_percent)
        
        return surface
        
    def render_professional_grid(self, surface: pygame.Surface):
        """Render clean professional grid"""
        # Vertical lines
        for i in range(1, 6):
            x = self.chart_rect.left + (i / 6) * self.chart_rect.width
            pygame.draw.line(surface, self.grid_color, 
                           (x, self.chart_rect.top), (x, self.chart_rect.bottom), 1)
                           
        # Horizontal lines
        for i in range(1, 5):
            y = self.chart_rect.top + (i / 5) * self.chart_rect.height
            pygame.draw.line(surface, self.grid_color, 
                           (self.chart_rect.left, y), (self.chart_rect.right, y), 1)
                           
    def render_chart_fill(self, surface: pygame.Surface, points: List[Tuple[int, int]], 
                         color: Tuple[int, int, int]):
        """Render smooth filled area under chart"""
        if len(points) < 2:
            return
            
        # Create fill polygon
        fill_points = points.copy()
        fill_points.append((points[-1][0], self.chart_rect.bottom))
        fill_points.append((points[0][0], self.chart_rect.bottom))
        
        # Create gradient fill
        fill_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Multi-layer gradient for smoothness
        for i in range(20):
            alpha = int(60 * (1 - i / 20))
            if alpha > 0:
                gradient_color = (*color, alpha)
                
                # Create slightly smaller polygon for each layer
                offset_points = []
                for point in fill_points:
                    offset_y = point[1] + i * 2
                    offset_points.append((point[0], min(offset_y, self.chart_rect.bottom)))
                
                pygame.draw.polygon(fill_surface, gradient_color, offset_points)
                
        surface.blit(fill_surface, (0, 0))
        
    def render_chart_line(self, surface: pygame.Surface, points: List[Tuple[int, int]], 
                         color: Tuple[int, int, int]):
        """Render smooth chart line"""
        if len(points) < 2:
            return
            
        # Main line with slight glow
        for thickness in [5, 3, 1]:
            alpha = 255 if thickness == 1 else 60
            line_color = (*color, alpha) if thickness > 1 else color
            
            # Create line surface for alpha blending
            if thickness > 1:
                line_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                pygame.draw.lines(line_surface, line_color, False, points, thickness)
                surface.blit(line_surface, (0, 0))
            else:
                pygame.draw.lines(surface, line_color, False, points, thickness)
                
    def render_interactive_points(self, surface: pygame.Surface, chart_points: List[Tuple[int, int]], 
                                 data_points: List[Dict], color: Tuple[int, int, int]):
        """Render interactive data points with professional tooltips"""
        mouse_x, mouse_y = self.mouse_pos
        hover_radius = 25
        closest_point = None
        closest_distance = float('inf')
        
        # Find closest point to mouse
        for i, (point, data) in enumerate(zip(chart_points, data_points)):
            x, y = point
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)
            
            if distance < hover_radius and distance < closest_distance:
                closest_distance = distance
                closest_point = (i, point, data)
                
        self.hovered_point_index = closest_point[0] if closest_point else None
        
        # Render crosshair for hovered point
        if closest_point:
            point_x, point_y = closest_point[1]
            
            # Crosshair lines
            pygame.draw.line(surface, (100, 150, 200, 150), 
                           (self.chart_rect.left, point_y), (self.chart_rect.right, point_y), 1)
            pygame.draw.line(surface, (100, 150, 200, 150), 
                           (point_x, self.chart_rect.top), (point_x, self.chart_rect.bottom), 1)
            
            # Highlight point
            pygame.draw.circle(surface, (255, 255, 255), (point_x, point_y), 6)
            pygame.draw.circle(surface, color, (point_x, point_y), 4)
            
            # Show professional tooltip
            tooltip_data = {
                'price': closest_point[2]['price'],
                'time': closest_point[2]['timestamp'].strftime("%H:%M"),
                'volume': closest_point[2].get('volume', 0)
            }
            
            # Calculate price change if not first point
            if closest_point[0] > 0:
                prev_price = data_points[closest_point[0] - 1]['price']
                current_price = closest_point[2]['price']
                change = ((current_price - prev_price) / prev_price) * 100
                tooltip_data['change'] = change
                
            self.tooltip.show((mouse_x + 15, mouse_y - 15), tooltip_data)
        else:
            self.tooltip.hide()
            
        # Render subtle data points along the line
        point_spacing = max(1, len(chart_points) // 30)
        for i in range(0, len(chart_points), point_spacing):
            x, y = chart_points[i]
            if i == self.hovered_point_index:
                continue  # Skip hovered point (already rendered)
                
            pygame.draw.circle(surface, (255, 255, 255, 180), (x, y), 2)
            
    def render_professional_axes(self, surface: pygame.Surface, min_price: float, 
                                max_price: float, timestamps: List):
        """Render professional axis labels"""
        font = pygame.font.SysFont("Segoe UI", 9)
        
        # Y-axis (price) labels
        for i in range(6):
            price = min_price + (i / 5) * (max_price - min_price)
            y = self.chart_rect.bottom - (i / 5) * self.chart_rect.height
            
            price_text = format_price(price)
            text_surface = font.render(price_text, True, self.text_color)
            surface.blit(text_surface, (5, y - text_surface.get_height() // 2))
            
        # X-axis (time) labels
        if timestamps:
            for i in range(5):
                if i < len(timestamps):
                    timestamp_index = int(i * (len(timestamps) - 1) / 4)
                    timestamp = timestamps[timestamp_index]
                    x = self.chart_rect.left + (i / 4) * self.chart_rect.width
                    
                    time_text = timestamp.strftime("%H:%M")
                    text_surface = font.render(time_text, True, self.text_color)
                    surface.blit(text_surface, (x - text_surface.get_width() // 2, 
                                               self.chart_rect.bottom + 8))
                                               
    def render_professional_title(self, surface: pygame.Surface, symbol: str, 
                                 timeframe_label: str, change_percent: float):
        """Render professional chart title"""
        title_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        subtitle_font = pygame.font.SysFont("Segoe UI", 12)
        
        # Main title
        title_text = f"{symbol} • {timeframe_label}"
        title_surface = title_font.render(title_text, True, (220, 230, 250))
        
        # Performance indicator
        change_color = self.get_trend_color(change_percent)
        change_text = f"{change_percent:+.2f}%"
        change_surface = subtitle_font.render(change_text, True, change_color)
        
        # Position
        title_x = self.chart_rect.left
        title_y = 8
        
        surface.blit(title_surface, (title_x, title_y))
        surface.blit(change_surface, (title_x + title_surface.get_width() + 15, title_y + 2))
        
    def render_no_data_chart(self) -> pygame.Surface:
        """Render professional no-data state"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        font = pygame.font.SysFont("Segoe UI", 16)
        text = "Loading chart data..."
        text_surface = font.render(text, True, (120, 140, 160))
        
        x = (self.width - text_surface.get_width()) // 2
        y = (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (x, y))
        
        return surface
        
    def handle_mouse_move(self, pos: Tuple[int, int]):
        """Handle mouse movement for interactions"""
        self.mouse_pos = pos
        
    def render_tooltip(self, surface: pygame.Surface):
        """Render tooltip if visible"""
        self.tooltip.render(surface)

class ProfessionalButton:
    """Clean professional button"""
    
    def __init__(self, rect: pygame.Rect, text: str, active: bool = False):
        self.rect = rect
        self.text = text
        self.active = active
        self.hover = False
        
    def update(self, dt: float, mouse_pos: tuple):
        """Update button state"""
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def render(self, surface: pygame.Surface):
        """Render professional button"""
        # Background
        if self.active:
            bg_color = (70, 120, 180)
            text_color = (255, 255, 255)
            border_color = (90, 140, 200)
        elif self.hover:
            bg_color = (45, 55, 70)
            text_color = (200, 220, 255)
            border_color = (70, 90, 120)
        else:
            bg_color = (30, 35, 45)
            text_color = (160, 180, 200)
            border_color = (50, 60, 75)
            
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)
        
        # Text
        font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class ProfessionalCryptoModal:
    """Professional crypto modal with elegant design"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.symbol = coin_data['symbol'].upper()
        self.is_active = False
        
        # Modal dimensions
        self.width = int(screen_size[0] * 0.85)
        self.height = int(screen_size[1] * 0.85)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        # Chart system
        chart_width = self.width - 320
        chart_height = self.height - 180
        self.chart_renderer = ProfessionalChartRenderer(chart_width, chart_height)
        
        # Data generation
        self.data_generator = HistoricalDataGenerator()
        
        # Modal state
        self.selected_timeframe = "7d"
        self.chart_surface = None
        self.loading_chart = False
        self.entrance_animation = 0
        
        # Timeframes
        self.timeframes = {
            "1d": {"label": "1D", "days": 1},
            "7d": {"label": "7D", "days": 7}, 
            "30d": {"label": "30D", "days": 30},
            "90d": {"label": "90D", "days": 90},
            "1y": {"label": "1Y", "days": 365}
        }
        
        # UI elements
        self.buttons = {}
        self.create_buttons()
        
        self.mouse_pos = (0, 0)
        self.close_button_rect = None
        
        print(f"Professional modal created for {self.symbol}")
        self.generate_chart()
        
    def create_buttons(self):
        """Create professional timeframe buttons"""
        button_width = 50
        button_height = 30
        button_spacing = 8
        
        start_x = 40
        start_y = 90
        
        for i, (key, info) in enumerate(self.timeframes.items()):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
            
            is_active = (key == self.selected_timeframe)
            self.buttons[key] = ProfessionalButton(button_rect, info['label'], is_active)
            
    def generate_chart(self):
        """Generate professional chart"""
        try:
            self.loading_chart = True
            
            timeframe_info = self.timeframes[self.selected_timeframe]
            current_price = self.coin_data.get('current_price', 1.0)
            
            # Generate realistic data
            data_points = self.data_generator.generate_realistic_data(
                current_price, self.symbol, timeframe_info['days']
            )
            
            # Render professional chart
            self.chart_surface = self.chart_renderer.render_price_chart(
                data_points, self.symbol, timeframe_info['label']
            )
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            self.chart_surface = self.chart_renderer.render_no_data_chart()
            
        self.loading_chart = False
        
    def handle_click(self, pos: tuple) -> bool:
        """Handle modal clicks"""
        if not self.is_active:
            return False
            
        # Check if clicked outside modal
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not modal_rect.collidepoint(pos):
            self.close()
            return True
            
        # Close button (fixed X button)
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close()
            return True
            
        # Timeframe buttons
        for timeframe, button in self.buttons.items():
            if button.rect.collidepoint(pos):
                if timeframe != self.selected_timeframe:
                    self.selected_timeframe = timeframe
                    
                    # Update button states
                    for key, btn in self.buttons.items():
                        btn.active = (key == timeframe)
                        
                    self.generate_chart()
                return True
                
        return True
        
    def handle_mouse_move(self, pos: tuple):
        """Handle mouse movement for chart interactions"""
        self.mouse_pos = pos
        
        # Update chart with relative mouse position
        chart_x = self.x + 40
        chart_y = self.y + 130
        
        relative_pos = (pos[0] - chart_x, pos[1] - chart_y)
        self.chart_renderer.handle_mouse_move(relative_pos)
        
    def open(self):
        """Open modal with animation"""
        self.is_active = True
        self.entrance_animation = 0
        
    def close(self):
        """Close modal"""
        self.is_active = False
        
    def update(self, dt: float):
        """Update modal animations"""
        if not self.is_active:
            return
            
        # Entrance animation
        if self.entrance_animation < 1.0:
            self.entrance_animation = min(1.0, self.entrance_animation + dt * 6)
            
        # Update buttons
        for button in self.buttons.values():
            relative_mouse = (self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y)
            button.update(dt, relative_mouse)
            
        # Update chart interactions
        chart_mouse = (
            self.mouse_pos[0] - self.x - 40,
            self.mouse_pos[1] - self.y - 130
        )
        self.chart_renderer.update(dt, chart_mouse)
        
    def draw(self, surface: pygame.Surface):
        """Draw professional modal"""
        if not self.is_active:
            return
            
        # Professional overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay_alpha = int(200 * self.entrance_animation)
        overlay.fill((0, 0, 0, overlay_alpha))
        surface.blit(overlay, (0, 0))
        
        # Modal surface
        modal_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Render components
        self.render_background(modal_surface)
        self.render_header(modal_surface)
        self.render_timeframe_buttons(modal_surface)
        self.render_chart_area(modal_surface)
        self.render_stats_panel(modal_surface)
        self.render_close_button(modal_surface)
        
        # Apply entrance animation
        scale = self.entrance_animation
        if scale < 1.0:
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            modal_surface = pygame.transform.smoothscale(modal_surface, (scaled_width, scaled_height))
            
            scaled_x = self.x + (self.width - scaled_width) // 2
            scaled_y = self.y + (self.height - scaled_height) // 2
            surface.blit(modal_surface, (scaled_x, scaled_y))
        else:
            surface.blit(modal_surface, (self.x, self.y))
            
    def render_background(self, surface: pygame.Surface):
        """Render clean professional background"""
        # Main background
        pygame.draw.rect(surface, (20, 25, 35), (0, 0, self.width, self.height), 
                        border_radius=12)
        
        # Subtle border
        pygame.draw.rect(surface, (60, 80, 110), (0, 0, self.width, self.height), 
                        2, border_radius=12)
                        
        # Inner highlight
        pygame.draw.rect(surface, (40, 50, 65), (1, 1, self.width-2, self.height-2), 
                        1, border_radius=11)
                        
    def render_header(self, surface: pygame.Surface):
        """Render professional header"""
        # Logo
        logo_size = 40
        logo_x, logo_y = 30, 20
        
        logo_path = f"assets/logos/{self.symbol.lower()}.png"
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                surface.blit(logo, (logo_x, logo_y))
            except:
                pygame.draw.circle(surface, (70, 120, 180), 
                                 (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        else:
            pygame.draw.circle(surface, (70, 120, 180), 
                             (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
                             
        # Coin info
        name_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        symbol_font = pygame.font.SysFont("Segoe UI", 14)
        
        coin_name = self.coin_data.get('name', self.symbol)
        if len(coin_name) > 25:
            coin_name = coin_name[:25] + "..."
            
        name_surface = name_font.render(coin_name, True, (220, 230, 250))
        symbol_surface = symbol_font.render(f"{self.symbol}", True, (160, 180, 210))
        
        surface.blit(name_surface, (logo_x + logo_size + 15, logo_y + 2))
        surface.blit(symbol_surface, (logo_x + logo_size + 15, logo_y + 28))
        
        # Current price
        current_price = self.coin_data.get('current_price', 0)
        price_text = format_price(current_price)
        price_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        price_surface = price_font.render(price_text, True, (255, 255, 255))
        
        price_x = self.width - price_surface.get_width() - 120
        surface.blit(price_surface, (price_x, logo_y + 2))
        
        # 24h change
        change_24h = self.coin_data.get('price_change_percentage_24h', 0) or 0
        change_color = (80, 200, 120) if change_24h >= 0 else (220, 80, 80)
        change_text = f"{change_24h:+.2f}%"
        
        change_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        change_surface = change_font.render(change_text, True, change_color)
        surface.blit(change_surface, (price_x, logo_y + 32))
        
    def render_timeframe_buttons(self, surface: pygame.Surface):
        """Render professional timeframe buttons"""
        for button in self.buttons.values():
            button.render(surface)
            
    def render_chart_area(self, surface: pygame.Surface):
        """Render chart area"""
        chart_x, chart_y = 40, 130
        
        if self.loading_chart:
            loading_surface = self.chart_renderer.render_no_data_chart()
            surface.blit(loading_surface, (chart_x, chart_y))
        elif self.chart_surface:
            surface.blit(self.chart_surface, (chart_x, chart_y))
            self.chart_renderer.render_tooltip(surface)
            
    def render_stats_panel(self, surface: pygame.Surface):
        """Render professional stats panel"""
        panel_x = self.width - 280
        panel_y = 80
        panel_width = 260
        panel_height = self.height - 120
        
        # Panel background
        pygame.draw.rect(surface, (25, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=8)
        pygame.draw.rect(surface, (50, 65, 85), 
                        (panel_x, panel_y, panel_width, panel_height), 1, border_radius=8)
        
        # Stats data
        header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 10)
        value_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
        # Panel title
        title_surface = header_font.render("MARKET DATA", True, (180, 200, 230))
        surface.blit(title_surface, (panel_x + 20, panel_y + 20))
        
        stats = [
            ("Market Cap", format_large_number(self.coin_data.get('market_cap', 0))),
            ("Volume 24h", format_large_number(self.coin_data.get('total_volume', 0))),
            ("Market Rank", f"#{self.coin_data.get('market_cap_rank', 'N/A')}" 
                           if self.coin_data.get('market_cap_rank') != 'N/A' else 'N/A'),
            ("Circulating Supply", format_supply(self.coin_data.get('circulating_supply', 0)))
        ]
        
        y_offset = panel_y + 50
        line_height = 45
        
        for i, (label, value) in enumerate(stats):
            current_y = y_offset + i * line_height
            
            # Label
            label_surface = label_font.render(label, True, (140, 160, 180))
            surface.blit(label_surface, (panel_x + 20, current_y))
            
            # Value
            value_color = (200, 220, 255)
            if "Market Cap" in label or "Volume" in label:
                value_color = (120, 200, 150)
            elif "Rank" in label:
                value_color = (200, 180, 120)
                
            value_surface = value_font.render(str(value), True, value_color)
            surface.blit(value_surface, (panel_x + 20, current_y + 15))
            
    def render_close_button(self, surface: pygame.Surface):
        """Render professional close button (FIXED X BUTTON)"""
        button_size = 32
        button_x = self.width - button_size - 15
        button_y = 15
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Check hover state
        mouse_in_button = self.close_button_rect.collidepoint(
            self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y
        )
        
        # Button colors
        if mouse_in_button:
            bg_color = (200, 70, 70)
            border_color = (220, 90, 90)
            x_color = (255, 255, 255)
        else:
            bg_color = (120, 50, 50)
            border_color = (150, 70, 70)
            x_color = (200, 200, 200)
            
        # Background
        pygame.draw.rect(surface, bg_color, self.close_button_rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.close_button_rect, 1, border_radius=4)
        
        # X symbol (FIXED)
        center_x = button_x + button_size // 2
        center_y = button_y + button_size // 2
        line_len = button_size // 4
        
        # Draw X with proper lines
        pygame.draw.line(surface, x_color, 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 2)
        pygame.draw.line(surface, x_color, 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 2)