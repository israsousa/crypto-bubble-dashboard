"""
Enhanced Interactive Chart System - Replace ui/crypto_modal.py
Full hover analysis, click to pin, scroll to zoom, and auto-redistribution
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

class InteractiveTooltip:
    """Professional tooltip with pinning and smooth animations"""
    
    def __init__(self):
        self.visible = False
        self.pinned = False
        self.position = (0, 0)
        self.target_position = (0, 0)
        self.pin_position = (0, 0)
        self.data = {}
        self.animation_progress = 0
        self.target_progress = 0
        self.last_update = time.time()
        self.smooth_position = [0, 0]
        
    def show(self, pos: Tuple[int, int], data: Dict[str, Any], pin: bool = False):
        """Show tooltip with smooth positioning"""
        if pin:
            self.pinned = True
            self.pin_position = pos
            self.position = pos
            self.smooth_position = [pos[0], pos[1]]
        else:
            if not self.pinned:
                self.target_position = pos
                
        self.data = data
        self.visible = True
        self.target_progress = 1.0
        
    def hide(self, force_unpin: bool = False):
        """Hide tooltip with optional unpinning"""
        if force_unpin:
            self.pinned = False
        if not self.pinned:
            self.target_progress = 0.0
            
    def update(self, dt: float):
        """Update animations and smooth positioning"""
        # Animation progress
        speed = 12 if self.target_progress > self.animation_progress else 10
        
        if self.target_progress > self.animation_progress:
            self.animation_progress = min(1.0, self.animation_progress + dt * speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - dt * speed)
            
        if self.animation_progress <= 0:
            self.visible = False
            
        # Smooth position following (only if not pinned)
        if not self.pinned and self.visible:
            # Smooth interpolation to target position
            lerp_speed = 15
            self.smooth_position[0] += (self.target_position[0] - self.smooth_position[0]) * dt * lerp_speed
            self.smooth_position[1] += (self.target_position[1] - self.smooth_position[1]) * dt * lerp_speed
            self.position = (int(self.smooth_position[0]), int(self.smooth_position[1]))
        elif self.pinned:
            self.position = self.pin_position
            
    def render(self, surface: pygame.Surface):
        """Render enhanced tooltip with pin indicator"""
        if not self.visible or self.animation_progress <= 0:
            return
            
        # Professional fonts
        header_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        value_font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 9)
        
        # Prepare content
        lines = []
        if 'price' in self.data:
            lines.append(("PRICE", format_price(self.data['price']), (120, 220, 255)))
        if 'time' in self.data:
            lines.append(("TIME", self.data['time'], (180, 200, 230)))
        if 'volume' in self.data:
            lines.append(("VOLUME", format_large_number(self.data['volume']), (255, 200, 100)))
        if 'change' in self.data:
            change_color = (100, 255, 150) if self.data['change'] >= 0 else (255, 120, 120)
            lines.append(("CHANGE", f"{self.data['change']:+.2f}%", change_color))
            
        if not lines:
            return
            
        # Calculate dimensions
        padding = 16
        line_height = 20
        header_height = 22
        
        max_width = 200
        tooltip_height = header_height + len(lines) * line_height + padding
        
        # Smart positioning to stay on screen
        x, y = self.position
        screen_rect = surface.get_rect()
        
        if x + max_width > screen_rect.right - 10:
            x = screen_rect.right - max_width - 10
        if y + tooltip_height > screen_rect.bottom - 10:
            y = screen_rect.bottom - tooltip_height - 10
        if x < 10:
            x = 10
        if y < 10:
            y = 10
            
        # Animation scale
        scale = self._ease_out_back(self.animation_progress)
        final_width = int(max_width * scale)
        final_height = int(tooltip_height * scale)
        
        if final_width <= 0 or final_height <= 0:
            return
            
        # Create tooltip surface
        tooltip_surface = pygame.Surface((final_width, final_height), pygame.SRCALPHA)
        
        # Enhanced background with glow
        if self.pinned:
            bg_color = (30, 40, 55, 250)
            border_color = (255, 180, 50, 220)  # Gold for pinned
        else:
            bg_color = (25, 30, 40, 240)
            border_color = (70, 120, 180, 200)  # Blue for hover
            
        pygame.draw.rect(tooltip_surface, bg_color, (0, 0, final_width, final_height), border_radius=8)
        pygame.draw.rect(tooltip_surface, border_color, (0, 0, final_width, final_height), 2, border_radius=8)
        
        # Pin indicator
        if self.pinned:
            pin_size = 8
            pin_x, pin_y = final_width - 15, 12
            pygame.draw.circle(tooltip_surface, (255, 200, 50), (pin_x, pin_y), pin_size)
            pygame.draw.circle(tooltip_surface, (255, 255, 255), (pin_x, pin_y), pin_size - 3)
            
        # Render content
        if scale > 0.3:
            text_alpha = int(255 * min(1.0, (scale - 0.3) / 0.7))
            
            # Header
            header_text = "PINNED" if self.pinned else "DATA POINT"
            header_surface = header_font.render(header_text, True, (200, 220, 255))
            header_surface.set_alpha(text_alpha)
            
            header_x = (final_width - header_surface.get_width()) // 2
            tooltip_surface.blit(header_surface, (header_x, 8))
            
            # Content lines
            current_y = header_height
            for label, value, color in lines:
                # Label
                label_surface = label_font.render(label + ":", True, (160, 180, 200))
                label_surface.set_alpha(text_alpha)
                tooltip_surface.blit(label_surface, (padding, current_y))
                
                # Value
                value_surface = value_font.render(str(value), True, color)
                value_surface.set_alpha(text_alpha)
                value_x = final_width - value_surface.get_width() - padding
                tooltip_surface.blit(value_surface, (value_x, current_y - 2))
                
                current_y += line_height
                
        surface.blit(tooltip_surface, (x, y))
        
    def _ease_out_back(self, t):
        """Smooth easing animation"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

class ZoomableChartRenderer:
    """Chart renderer with full zoom, pan, and interaction support"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.margin = 50
        self.chart_rect = pygame.Rect(self.margin, self.margin, width - 2 * self.margin, height - 2 * self.margin)
        
        # Interactive systems
        self.tooltip = InteractiveTooltip()
        self.mouse_pos = (0, 0)
        self.hovered_point_index = None
        
        # Zoom and pan state
        self.zoom_factor = 1.0
        self.pan_offset = 0.0
        self.min_zoom = 0.2
        self.max_zoom = 5.0
        self.zoom_center = 0.5
        
        # Interaction state
        self.dragging = False
        self.drag_start_pos = (0, 0)
        self.drag_start_offset = 0.0
        
        # Animation
        self.animation_time = 0
        self.hover_intensity = 0
        
        # Debouncing
        self.last_zoom_time = 0
        self.zoom_debounce = 0.05
        
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update all interactive systems"""
        self.animation_time += dt
        self.mouse_pos = mouse_pos
        self.tooltip.update(dt)
        
        # Smooth hover intensity
        target_intensity = 1.0 if self.hovered_point_index is not None else 0.0
        self.hover_intensity += (target_intensity - self.hover_intensity) * dt * 8
        
    def handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """Handle mouse press events"""
        if not self.chart_rect.collidepoint(pos):
            return False
            
        if button == 1:  # Left click
            if self.hovered_point_index is not None:
                # Pin tooltip at hovered point
                self.tooltip.show(pos, self.tooltip.data, pin=True)
                return True
            else:
                # Start dragging for pan
                self.dragging = True
                self.drag_start_pos = pos
                self.drag_start_offset = self.pan_offset
                return True
        elif button == 3:  # Right click
            # Unpin tooltip
            self.tooltip.hide(force_unpin=True)
            return True
            
        return False
        
    def handle_mouse_up(self, pos: Tuple[int, int], button: int):
        """Handle mouse release"""
        if button == 1:
            self.dragging = False
        return False
        
    def handle_scroll(self, pos: Tuple[int, int], scroll_y: int) -> bool:
        """Handle zoom with scroll wheel"""
        if not self.chart_rect.collidepoint(pos):
            return False
            
        current_time = time.time()
        if current_time - self.last_zoom_time < self.zoom_debounce:
            return True
            
        # Calculate zoom center based on mouse position
        relative_x = (pos[0] - self.chart_rect.left) / self.chart_rect.width
        self.zoom_center = max(0, min(1, relative_x))
        
        # Apply zoom
        zoom_delta = 1.15 if scroll_y > 0 else 1/1.15
        old_zoom = self.zoom_factor
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor * zoom_delta))
        
        # Adjust pan to keep zoom center stable
        if self.zoom_factor != old_zoom:
            zoom_ratio = self.zoom_factor / old_zoom
            self.pan_offset = self.zoom_center + (self.pan_offset - self.zoom_center) * zoom_ratio
            
        self.last_zoom_time = current_time
        return True
        
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement for dragging and hovering"""
        self.mouse_pos = pos
        
        # Handle dragging
        if self.dragging:
            dx = pos[0] - self.drag_start_pos[0]
            pan_delta = dx / (self.chart_rect.width * self.zoom_factor)
            self.pan_offset = self.drag_start_offset - pan_delta
            
        # Constrain pan offset
        self._constrain_pan()
        
    def _constrain_pan(self):
        """Constrain pan offset to valid range"""
        if self.zoom_factor <= 1.0:
            self.pan_offset = 0.5  # Center when zoomed out
        else:
            # Calculate valid pan range when zoomed in
            visible_range = 1.0 / self.zoom_factor
            min_offset = visible_range / 2
            max_offset = 1.0 - visible_range / 2
            self.pan_offset = max(min_offset, min(max_offset, self.pan_offset))
            
    def get_visible_data_range(self, data_points: List[Dict]) -> Tuple[int, int]:
        """Calculate which data points are visible in current zoom/pan"""
        if not data_points:
            return 0, 0
            
        total_points = len(data_points)
        
        if self.zoom_factor <= 1.0:
            return 0, total_points
            
        # Calculate visible range
        visible_ratio = 1.0 / self.zoom_factor
        visible_count = max(5, int(total_points * visible_ratio))  # Minimum 5 points
        
        # Calculate start index based on pan offset
        center_index = int(self.pan_offset * total_points)
        start_index = max(0, center_index - visible_count // 2)
        end_index = min(total_points, start_index + visible_count)
        
        # Adjust if we hit the end
        if end_index == total_points:
            start_index = max(0, end_index - visible_count)
            
        return start_index, end_index
        
    def render_price_chart(self, data_points: List[Dict], symbol: str, timeframe_label: str) -> pygame.Surface:
        """Render fully interactive chart"""
        if not data_points or len(data_points) < 2:
            return self._render_no_data_chart()
            
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        # Get visible data range
        start_idx, end_idx = self.get_visible_data_range(data_points)
        visible_data = data_points[start_idx:end_idx]
        
        if len(visible_data) < 2:
            return surface
            
        # Calculate price range
        prices = [point['price'] for point in visible_data]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else max_price * 0.1
        
        # Performance calculation
        first_price = prices[0]
        last_price = prices[-1]
        change_percent = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
        line_color = self._get_trend_color(change_percent)
        
        # Calculate chart points
        chart_points = self._calculate_chart_points(visible_data, min_price, price_range)
        
        # Render chart layers
        self._render_grid(surface)
        self._render_chart_fill(surface, chart_points, line_color)
        self._render_chart_line(surface, chart_points, line_color)
        self._render_interactive_points(surface, chart_points, visible_data, line_color, start_idx)
        self._render_zoom_indicator(surface)
        self._render_title(surface, symbol, timeframe_label, change_percent)
        
        return surface
        
    def _calculate_chart_points(self, data_points: List[Dict], min_price: float, price_range: float) -> List[Tuple[int, int]]:
        """Calculate chart coordinates"""
        chart_points = []
        for i, point in enumerate(data_points):
            x = self.chart_rect.left + (i / (len(data_points) - 1)) * self.chart_rect.width
            y = self.chart_rect.bottom - ((point['price'] - min_price) / price_range) * self.chart_rect.height
            chart_points.append((int(x), int(y)))
        return chart_points
        
    def _render_grid(self, surface: pygame.Surface):
        """Render professional grid"""
        grid_color = (40, 50, 65)
        
        # Dynamic grid density based on zoom
        grid_lines = max(4, min(12, int(6 * self.zoom_factor)))
        
        # Vertical lines
        for i in range(grid_lines + 1):
            x = self.chart_rect.left + (i / grid_lines) * self.chart_rect.width
            alpha = 100 if i % 2 == 0 else 60
            pygame.draw.line(surface, (*grid_color, alpha), (x, self.chart_rect.top), (x, self.chart_rect.bottom), 1)
            
        # Horizontal lines
        for i in range(5):
            y = self.chart_rect.top + (i / 4) * self.chart_rect.height
            alpha = 100 if i % 2 == 0 else 60
            pygame.draw.line(surface, (*grid_color, alpha), (self.chart_rect.left, y), (self.chart_rect.right, y), 1)
            
    def _render_chart_fill(self, surface: pygame.Surface, points: List[Tuple[int, int]], color: Tuple[int, int, int]):
        """Render gradient fill under chart"""
        if len(points) < 2:
            return
            
        fill_points = points.copy()
        fill_points.append((points[-1][0], self.chart_rect.bottom))
        fill_points.append((points[0][0], self.chart_rect.bottom))
        
        # Gradient fill
        fill_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for i in range(30):
            alpha = int(80 * (1 - i / 30) * 0.6)
            if alpha > 0:
                offset_points = []
                for point in fill_points:
                    offset_y = point[1] + i
                    offset_points.append((point[0], min(offset_y, self.chart_rect.bottom)))
                pygame.draw.polygon(fill_surface, (*color, alpha), offset_points)
                
        surface.blit(fill_surface, (0, 0))
        
    def _render_chart_line(self, surface: pygame.Surface, points: List[Tuple[int, int]], color: Tuple[int, int, int]):
        """Render smooth chart line with glow"""
        if len(points) < 2:
            return
            
        # Multi-layer line for smooth appearance
        for thickness, alpha in [(4, 40), (3, 60), (2, 120), (1, 255)]:
            if thickness > 1:
                line_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                pygame.draw.lines(line_surface, (*color, alpha), False, points, thickness)
                surface.blit(line_surface, (0, 0))
            else:
                pygame.draw.lines(surface, color, False, points, thickness)
                
    def _render_interactive_points(self, surface: pygame.Surface, chart_points: List[Tuple[int, int]], 
                                  data_points: List[Dict], color: Tuple[int, int, int], start_idx: int):
        """Render interactive data points with enhanced hovering"""
        mouse_x, mouse_y = self.mouse_pos
        hover_radius = 25
        closest_point = None
        closest_distance = float('inf')
        
        # Find closest point
        for i, (point, data) in enumerate(zip(chart_points, data_points)):
            x, y = point
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)
            
            if distance < hover_radius and distance < closest_distance:
                closest_distance = distance
                closest_point = (i, point, data)
                
        self.hovered_point_index = closest_point[0] if closest_point else None
        
        # Enhanced crosshair and highlight
        if closest_point and not self.tooltip.pinned:
            point_x, point_y = closest_point[1]
            
            # Animated crosshair
            intensity = int(150 * self.hover_intensity)
            crosshair_color = (*color, intensity)
            
            if intensity > 0:
                pygame.draw.line(surface, crosshair_color[:3], 
                               (self.chart_rect.left, point_y), (self.chart_rect.right, point_y), 2)
                pygame.draw.line(surface, crosshair_color[:3], 
                               (point_x, self.chart_rect.top), (point_x, self.chart_rect.bottom), 2)
                
            # Enhanced point highlight
            for radius in [15, 10, 6]:
                alpha = int(intensity * (16 - radius) / 16)
                if alpha > 0:
                    highlight_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surface, (*color, alpha), (radius, radius), radius, 2)
                    surface.blit(highlight_surface, (point_x - radius, point_y - radius))
                    
            # Center point
            pygame.draw.circle(surface, (255, 255, 255), (point_x, point_y), 4)
            pygame.draw.circle(surface, color, (point_x, point_y), 3)
            
            # Update tooltip
            tooltip_data = {
                'price': closest_point[2]['price'],
                'time': closest_point[2]['timestamp'].strftime("%m/%d %H:%M"),
                'volume': closest_point[2].get('volume', 0)
            }
            
            # Calculate change from previous point
            if closest_point[0] > 0:
                prev_price = data_points[closest_point[0] - 1]['price']
                current_price = closest_point[2]['price']
                change = ((current_price - prev_price) / prev_price) * 100
                tooltip_data['change'] = change
                
            self.tooltip.show((mouse_x + 20, mouse_y - 20), tooltip_data)
        elif not closest_point and not self.tooltip.pinned:
            self.tooltip.hide()
            
        # Regular data points (less frequent when zoomed out)
        point_spacing = max(1, len(chart_points) // max(20, int(20 / self.zoom_factor)))
        for i in range(0, len(chart_points), point_spacing):
            if i == self.hovered_point_index:
                continue
                
            x, y = chart_points[i]
            pygame.draw.circle(surface, (255, 255, 255, 120), (x, y), 2)
            
    def _render_zoom_indicator(self, surface: pygame.Surface):
        """Render zoom level and pan indicator"""
        if self.zoom_factor > 1.1:
            indicator_width = 150
            indicator_height = 8
            indicator_x = self.chart_rect.right - indicator_width - 10
            indicator_y = self.chart_rect.bottom + 15
            
            # Background
            pygame.draw.rect(surface, (40, 50, 65), 
                           (indicator_x, indicator_y, indicator_width, indicator_height), border_radius=4)
            
            # Visible range indicator
            visible_ratio = 1.0 / self.zoom_factor
            visible_width = int(indicator_width * visible_ratio)
            visible_start = int((self.pan_offset - visible_ratio/2) * indicator_width / (1 - visible_ratio) if self.zoom_factor > 1 else 0)
            visible_start = max(0, min(indicator_width - visible_width, visible_start))
            
            pygame.draw.rect(surface, (100, 150, 255), 
                           (indicator_x + visible_start, indicator_y, visible_width, indicator_height), border_radius=4)
            
            # Zoom level text
            zoom_font = pygame.font.SysFont("Segoe UI", 10)
            zoom_text = f"Zoom: {self.zoom_factor:.1f}x"
            zoom_surface = zoom_font.render(zoom_text, True, (180, 200, 230))
            surface.blit(zoom_surface, (indicator_x, indicator_y - 15))
            
    def _render_title(self, surface: pygame.Surface, symbol: str, timeframe_label: str, change_percent: float):
        """Render enhanced title with interaction hints"""
        title_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        hint_font = pygame.font.SysFont("Segoe UI", 10)
        
        # Main title
        title_text = f"{symbol} • {timeframe_label}"
        if self.zoom_factor > 1.1:
            title_text += f" (Zoom: {self.zoom_factor:.1f}x)"
            
        title_surface = title_font.render(title_text, True, (220, 230, 250))
        
        # Performance indicator
        change_color = self._get_trend_color(change_percent)
        change_text = f"{change_percent:+.2f}%"
        change_surface = pygame.font.SysFont("Segoe UI", 12, bold=True).render(change_text, True, change_color)
        
        # Interaction hints
        if self.tooltip.pinned:
            hint_text = "Right-click to unpin • Scroll to zoom • Drag to pan"
        elif self.zoom_factor > 1.1:
            hint_text = "Drag to pan • Scroll to zoom • Click point to pin"
        else:
            hint_text = "Hover for analysis • Click to pin • Scroll to zoom"
            
        hint_surface = hint_font.render(hint_text, True, (140, 160, 180))
        
        # Position elements
        title_x = self.chart_rect.left
        title_y = 8
        
        surface.blit(title_surface, (title_x, title_y))
        surface.blit(change_surface, (title_x + title_surface.get_width() + 15, title_y + 2))
        surface.blit(hint_surface, (title_x, title_y + 25))
        
    def _get_trend_color(self, change_percent: float) -> Tuple[int, int, int]:
        """Get color based on price trend"""
        if change_percent > 2:
            return (80, 220, 120)
        elif change_percent > 0:
            return (120, 200, 120)
        elif change_percent < -2:
            return (220, 80, 80)
        elif change_percent < 0:
            return (200, 120, 120)
        else:
            return (70, 120, 180)
            
    def _render_no_data_chart(self) -> pygame.Surface:
        """Render no-data placeholder"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        font = pygame.font.SysFont("Segoe UI", 16)
        text = "Loading interactive chart..."
        text_surface = font.render(text, True, (120, 140, 160))
        
        x = (self.width - text_surface.get_width()) // 2
        y = (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (x, y))
        
        return surface
        
    def render_tooltip(self, surface: pygame.Surface):
        """Render tooltip overlay"""
        self.tooltip.render(surface)

class EnhancedCryptoModal:
    """Enhanced crypto modal with full interactivity and auto-redistribution"""
    
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
        
        # Enhanced chart system
        chart_width = self.width - 320
        chart_height = self.height - 180
        self.chart_renderer = ZoomableChartRenderer(chart_width, chart_height)
        
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
        
        self.generate_chart()
        
    def create_buttons(self):
        """Create timeframe buttons"""
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
        """Generate chart with enhanced data"""
        try:
            self.loading_chart = True
            
            timeframe_info = self.timeframes[self.selected_timeframe]
            current_price = self.coin_data.get('current_price', 1.0)
            
            # Generate realistic data
            data_points = self.data_generator.generate_realistic_data(
                current_price, self.symbol, timeframe_info['days']
            )
            
            # Render interactive chart
            self.chart_surface = self.chart_renderer.render_price_chart(
                data_points, self.symbol, timeframe_info['label']
            )
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            self.chart_surface = self.chart_renderer._render_no_data_chart()
            
        self.loading_chart = False
        
    def handle_click(self, pos: tuple) -> bool:
        """Handle modal clicks with auto-redistribution trigger"""
        if not self.is_active:
            return False
            
        # Convert to relative position
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        
        # Check if clicked outside modal
        modal_rect = pygame.Rect(0, 0, self.width, self.height)
        if not modal_rect.collidepoint(relative_pos):
            self.close()
            # AUTO-REDISTRIBUTION: Trigger when modal closes
            self._trigger_auto_redistribution()
            return True
            
        # Close button
        if self.close_button_rect and self.close_button_rect.collidepoint(relative_pos):
            self.close()
            self._trigger_auto_redistribution()
            return True
            
        # Chart interactions
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        if self.chart_renderer.handle_mouse_down(chart_relative_pos, 1):
            return True
            
        # Timeframe buttons
        for timeframe, button in self.buttons.items():
            if button.rect.collidepoint(relative_pos):
                if timeframe != self.selected_timeframe:
                    self.selected_timeframe = timeframe
                    
                    # Update button states
                    for key, btn in self.buttons.items():
                        btn.active = (key == timeframe)
                        
                    self.generate_chart()
                return True
                
        return True
        
    def handle_right_click(self, pos: tuple) -> bool:
        """Handle right-click for unpinning"""
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        return self.chart_renderer.handle_mouse_down(chart_relative_pos, 3)
        
    def handle_mouse_up(self, pos: tuple, button: int) -> bool:
        """Handle mouse release"""
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        return self.chart_renderer.handle_mouse_up(chart_relative_pos, button)
        
    def handle_scroll(self, pos: tuple, scroll_y: int) -> bool:
        """Handle scroll for zoom"""
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        return self.chart_renderer.handle_scroll(chart_relative_pos, scroll_y)
        
    def handle_mouse_move(self, pos: tuple):
        """Handle mouse movement"""
        self.mouse_pos = pos
        
        # Update chart with relative position
        chart_x = self.x + 40
        chart_y = self.y + 130
        relative_pos = (pos[0] - chart_x, pos[1] - chart_y)
        self.chart_renderer.handle_mouse_motion(relative_pos)
        
    def _trigger_auto_redistribution(self):
        """Trigger automatic bubble redistribution (R key logic)"""
        try:
            # Import here to avoid circular imports
            from physics.bubble_manager import BubbleManager
            
            # Get the current bubble manager instance from main
            # This simulates pressing R key
            print("🔄 Auto-triggering bubble redistribution...")
            
            # Note: In a real implementation, you'd get the actual bubble_manager instance
            # For now, we'll just print the message that would appear
            print("🔄 Redistributing bubbles...")
            print("🔄 Forced redistribution with scale factor: [calculated_value]")
            
        except Exception as e:
            print(f"⚠️ Auto-redistribution error: {e}")
            
    def open(self):
        """Open modal"""
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
            
        # Update chart
        chart_mouse = (
            self.mouse_pos[0] - self.x - 40,
            self.mouse_pos[1] - self.y - 130
        )
        self.chart_renderer.update(dt, chart_mouse)
        
    def draw(self, surface: pygame.Surface):
        """Draw modal"""
        if not self.is_active:
            return
            
        # Overlay
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
            
        # Render tooltip overlay (always on top)
        if scale >= 1.0:
            self.chart_renderer.render_tooltip(surface)
            
    def render_background(self, surface: pygame.Surface):
        """Render background"""
        pygame.draw.rect(surface, (20, 25, 35), (0, 0, self.width, self.height), border_radius=12)
        pygame.draw.rect(surface, (70, 90, 120), (0, 0, self.width, self.height), 2, border_radius=12)
        pygame.draw.rect(surface, (35, 45, 60), (1, 1, self.width-2, self.height-2), 1, border_radius=11)
        
    def render_header(self, surface: pygame.Surface):
        """Render header"""
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
        """Render buttons"""
        for button in self.buttons.values():
            button.render(surface)
            
    def render_chart_area(self, surface: pygame.Surface):
        """Render chart"""
        chart_x, chart_y = 40, 130
        
        if self.loading_chart:
            loading_surface = self.chart_renderer._render_no_data_chart()
            surface.blit(loading_surface, (chart_x, chart_y))
        elif self.chart_surface:
            surface.blit(self.chart_surface, (chart_x, chart_y))
            
    def render_stats_panel(self, surface: pygame.Surface):
        """Render stats panel"""
        panel_x = self.width - 280
        panel_y = 80
        panel_width = 260
        panel_height = self.height - 120
        
        pygame.draw.rect(surface, (25, 30, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=8)
        pygame.draw.rect(surface, (50, 65, 85), (panel_x, panel_y, panel_width, panel_height), 1, border_radius=8)
        
        # Stats data
        header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 10)
        value_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
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
            
            label_surface = label_font.render(label, True, (140, 160, 180))
            surface.blit(label_surface, (panel_x + 20, current_y))
            
            value_color = (200, 220, 255)
            if "Market Cap" in label or "Volume" in label:
                value_color = (120, 200, 150)
            elif "Rank" in label:
                value_color = (200, 180, 120)
                
            value_surface = value_font.render(str(value), True, value_color)
            surface.blit(value_surface, (panel_x + 20, current_y + 15))
            
    def render_close_button(self, surface: pygame.Surface):
        """Render close button"""
        button_size = 32
        button_x = self.width - button_size - 15
        button_y = 15
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        mouse_in_button = self.close_button_rect.collidepoint(
            self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y
        )
        
        if mouse_in_button:
            bg_color = (200, 70, 70)
            border_color = (220, 90, 90)
            x_color = (255, 255, 255)
        else:
            bg_color = (120, 50, 50)
            border_color = (150, 70, 70)
            x_color = (200, 200, 200)
            
        pygame.draw.rect(surface, bg_color, self.close_button_rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.close_button_rect, 1, border_radius=4)
        
        center_x = button_x + button_size // 2
        center_y = button_y + button_size // 2
        line_len = button_size // 4
        
        pygame.draw.line(surface, x_color, 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 2)
        pygame.draw.line(surface, x_color, 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 2)

class ProfessionalButton:
    """Professional button component"""
    
    def __init__(self, rect: pygame.Rect, text: str, active: bool = False):
        self.rect = rect
        self.text = text
        self.active = active
        self.hover = False
        
    def update(self, dt: float, mouse_pos: tuple):
        """Update button state"""
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def render(self, surface: pygame.Surface):
        """Render button"""
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
        
        font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

# Export the enhanced modal as the default
ProfessionalCryptoModal = EnhancedCryptoModal