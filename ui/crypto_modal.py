"""
Complete Enhanced Crypto Modal with Professional Trading Tooltips
Replace your entire ui/crypto_modal.py with this version
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

class ProfessionalTradingTooltip:
    """Professional trading tooltip with comprehensive market data"""
    
    def __init__(self):
        self.visible = False
        self.position = (0, 0)
        self.data = {}
        self.animation_progress = 0
        self.target_progress = 0
        self.pinned = False
        self.pin_position = (0, 0)
        self.glow_intensity = 0
        
    def show(self, pos: Tuple[int, int], data: Dict[str, Any], pin: bool = False):
        """Show professional trading tooltip"""
        if pin:
            self.pinned = True
            self.pin_position = pos
        else:
            self.position = pos
            
        self.data = data
        self.visible = True
        self.target_progress = 1.0
        
    def hide(self, force_unpin: bool = False):
        """Hide tooltip with unpin option"""
        if force_unpin:
            self.pinned = False
        if not self.pinned:
            self.target_progress = 0.0
        
    def update(self, dt: float):
        """Update animations"""
        speed = 18 if self.target_progress > self.animation_progress else 15
        
        if self.target_progress > self.animation_progress:
            self.animation_progress = min(1.0, self.animation_progress + dt * speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - dt * speed)
            
        self.glow_intensity = math.sin(time.time() * 3) * 0.3 + 0.7
            
        if self.animation_progress <= 0:
            self.visible = False
    
    def _calculate_technical_indicators(self, price: float, prev_price: float = None) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        if prev_price:
            change = price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price > 0 else 0
            indicators['price_change'] = change
            indicators['price_change_pct'] = change_pct
            
            if change_pct > 2:
                indicators['trend'] = "Strong Bullish"
                indicators['trend_color'] = (50, 255, 100)
            elif change_pct > 0:
                indicators['trend'] = "Bullish"
                indicators['trend_color'] = (100, 255, 150)
            elif change_pct < -2:
                indicators['trend'] = "Strong Bearish"
                indicators['trend_color'] = (255, 50, 50)
            elif change_pct < 0:
                indicators['trend'] = "Bearish"
                indicators['trend_color'] = (255, 100, 100)
            else:
                indicators['trend'] = "Neutral"
                indicators['trend_color'] = (200, 200, 200)
        
        # Mock RSI
        indicators['rsi'] = 45 + (hash(str(price)) % 30)
        if indicators['rsi'] > 70:
            indicators['rsi_signal'] = "Overbought"
            indicators['rsi_color'] = (255, 100, 100)
        elif indicators['rsi'] < 30:
            indicators['rsi_signal'] = "Oversold"
            indicators['rsi_color'] = (100, 255, 100)
        else:
            indicators['rsi_signal'] = "Neutral"
            indicators['rsi_color'] = (200, 200, 200)
            
        return indicators
        
    def render(self, surface: pygame.Surface):
        """Render professional trading tooltip"""
        if not self.visible or self.animation_progress <= 0:
            return
            
        display_pos = self.pin_position if self.pinned else self.position
        
        header_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        value_font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 9)
        
        if not self.data:
            return
            
        price = self.data.get('price', 0)
        timestamp = self.data.get('time', '--:--')
        volume = self.data.get('volume', 0)
        prev_price = self.data.get('prev_price')
        
        indicators = self._calculate_technical_indicators(price, prev_price)
        
        sections = []
        
        # PRICE SECTION
        price_section = {
            'title': 'PRICE ANALYSIS',
            'items': [
                ("Price", format_price(price), (120, 220, 255)),
                ("Time", timestamp, (180, 200, 230))
            ]
        }
        
        if 'price_change' in indicators:
            change_color = (100, 255, 150) if indicators['price_change'] >= 0 else (255, 120, 120)
            price_section['items'].append((
                "Change", 
                f"{indicators['price_change']:+.4f} ({indicators['price_change_pct']:+.2f}%)", 
                change_color
            ))
            
        sections.append(price_section)
        
        # MARKET DATA SECTION
        market_section = {
            'title': 'MARKET DATA',
            'items': [
                ("Volume", format_large_number(volume), (255, 200, 100))
            ]
        }
        
        if 'trend' in indicators:
            market_section['items'].append((
                "Trend", indicators['trend'], indicators['trend_color']
            ))
            
        sections.append(market_section)
        
        # TECHNICAL INDICATORS SECTION
        tech_section = {
            'title': 'TECHNICAL',
            'items': [
                ("RSI(14)", f"{indicators.get('rsi', 50):.1f}", indicators.get('rsi_color', (200, 200, 200))),
                ("Signal", indicators.get('rsi_signal', 'Neutral'), indicators.get('rsi_color', (200, 200, 200)))
            ]
        }
        sections.append(tech_section)
        
        # Calculate dimensions
        padding = 18
        section_spacing = 20
        line_height = 16
        header_height = 18
        
        max_width = 280
        total_height = padding
        
        for section in sections:
            total_height += header_height + len(section['items']) * line_height + section_spacing
            
        tooltip_width = max_width
        tooltip_height = total_height + padding
        
        # Smart positioning
        x, y = display_pos
        screen_rect = surface.get_rect()
        
        edge_padding = 20
        if x + tooltip_width > screen_rect.right - edge_padding:
            x = screen_rect.right - tooltip_width - edge_padding
        if y + tooltip_height > screen_rect.bottom - edge_padding:
            y = screen_rect.bottom - tooltip_height - edge_padding
        if x < edge_padding:
            x = edge_padding
        if y < edge_padding:
            y = edge_padding
            
        scale = self._ease_out_back(self.animation_progress)
        final_width = int(tooltip_width * scale)
        final_height = int(tooltip_height * scale)
        
        if final_width <= 0 or final_height <= 0:
            return
            
        tooltip_surface = pygame.Surface((final_width, final_height), pygame.SRCALPHA)
        
        # Professional background with glow
        glow_alpha = int(self.glow_intensity * 40)
        
        # Outer glow
        for i in range(8):
            glow_size = i * 2
            glow_surf = pygame.Surface((final_width + glow_size*2, final_height + glow_size*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (70, 120, 180, glow_alpha // (i+1)), 
                           (glow_size, glow_size, final_width, final_height), border_radius=10)
            tooltip_surface.blit(glow_surf, (-glow_size, -glow_size))
        
        # Main background
        pygame.draw.rect(tooltip_surface, (20, 25, 35, 252), 
                        (0, 0, final_width, final_height), border_radius=10)
        
        # Professional border
        pygame.draw.rect(tooltip_surface, (70, 120, 180, 220), 
                        (0, 0, final_width, final_height), 3, border_radius=10)
        pygame.draw.rect(tooltip_surface, (40, 60, 90, 150), 
                        (1, 1, final_width-2, final_height-2), 1, border_radius=9)
        
        # Pin indicator
        if self.pinned:
            pin_size = 10
            pin_x, pin_y = final_width - 20, 15
            
            for i in range(3):
                pin_alpha = 255 - i * 60
                pin_radius = pin_size + i
                pygame.draw.circle(tooltip_surface, (255, 200, 100, pin_alpha), 
                                 (pin_x, pin_y), pin_radius)
            
            pygame.draw.circle(tooltip_surface, (255, 255, 255), (pin_x, pin_y), pin_size - 3)
        
        # Render content
        if scale > 0.3:
            text_alpha = int(255 * min(1.0, (scale - 0.3) / 0.7))
            current_y = padding
            
            for section in sections:
                # Section header
                header_surface = header_font.render(section['title'], True, (200, 220, 255))
                header_surface.set_alpha(text_alpha)
                tooltip_surface.blit(header_surface, (padding, current_y))
                
                # Underline
                underline_color = (70, 120, 180, text_alpha)
                pygame.draw.line(tooltip_surface, underline_color[:3], 
                               (padding, current_y + header_height - 2), 
                               (padding + header_surface.get_width(), current_y + header_height - 2), 1)
                
                current_y += header_height + 3
                
                # Section items
                for item_idx, (label, value, color) in enumerate(section['items']):
                    # Label
                    label_surface = label_font.render(label + ":", True, (160, 180, 200))
                    label_surface.set_alpha(text_alpha)
                    tooltip_surface.blit(label_surface, (padding + 4, current_y + 1))
                    
                    # Value (right-aligned)
                    value_surface = value_font.render(str(value), True, color)
                    value_surface.set_alpha(text_alpha)
                    
                    value_x = final_width - value_surface.get_width() - padding - 4
                    tooltip_surface.blit(value_surface, (value_x, current_y - 1))
                    
                    # Separator line
                    if item_idx < len(section['items']) - 1:
                        sep_color = (40, 50, 65, text_alpha // 2)
                        pygame.draw.line(tooltip_surface, sep_color[:3], 
                                       (padding + 4, current_y + line_height - 2), 
                                       (final_width - padding - 4, current_y + line_height - 2), 1)
                    
                    current_y += line_height
                
                current_y += section_spacing - line_height
                
        surface.blit(tooltip_surface, (x, y))
    
    def _ease_out_back(self, t):
        """Professional easing function"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

class ProfessionalChartRenderer:
    """Enhanced chart renderer with professional interactions"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.margin = 50
        self.chart_rect = pygame.Rect(
            self.margin, self.margin,
            width - 2 * self.margin, height - 2 * self.margin
        )
        
        self.tooltip = ProfessionalTradingTooltip()
        self.mouse_pos = (0, 0)
        self.hovered_point_index = None
        
        self.zoom_factor = 1.0
        self.pan_offset = 0
        self.dragging = False
        self.drag_start = (0, 0)
        
        self.crosshair_position = None
        self.hover_animation = 0
        self.cursor_style = 'default'
        
        self.colors = {
            'primary': (70, 120, 180),
            'positive': (80, 200, 120),
            'negative': (220, 80, 80),
            'grid_major': (50, 65, 85),
            'grid_minor': (35, 45, 60),
            'text': (180, 190, 210),
            'highlight': (255, 255, 255),
            'crosshair': (120, 150, 200)
        }
        
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update chart interactions"""
        self.mouse_pos = mouse_pos
        self.tooltip.update(dt)
        
        if self.hovered_point_index is not None:
            self.hover_animation = min(1.0, self.hover_animation + dt * 8)
        else:
            self.hover_animation = max(0.0, self.hover_animation - dt * 6)
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """Handle mouse press events"""
        if button == 1:  # Left click
            if self.chart_rect.collidepoint(pos):
                if self.hovered_point_index is not None:
                    self.tooltip.show(pos, self.tooltip.data, pin=True)
                else:
                    self.dragging = True
                    self.drag_start = pos
        elif button == 3:  # Right click
            self.tooltip.hide(force_unpin=True)
    
    def handle_mouse_up(self, pos: Tuple[int, int], button: int):
        """Handle mouse release"""
        if button == 1:
            self.dragging = False
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement"""
        self.mouse_pos = pos
        
        if self.dragging:
            dx = pos[0] - self.drag_start[0]
            self.pan_offset += dx / self.zoom_factor
            self.drag_start = pos
        
        if self.chart_rect.collidepoint(pos):
            if self.hovered_point_index is not None:
                self.cursor_style = 'pointer'
            elif self.dragging:
                self.cursor_style = 'grabbing'
            else:
                self.cursor_style = 'crosshair'
        else:
            self.cursor_style = 'default'
    
    def handle_scroll(self, scroll_y: int):
        """Handle zoom"""
        if self.chart_rect.collidepoint(self.mouse_pos):
            zoom_delta = 1.1 if scroll_y > 0 else 0.9
            self.zoom_factor = max(0.5, min(5.0, self.zoom_factor * zoom_delta))
    
    def get_cursor_style(self) -> str:
        """Get cursor style"""
        return self.cursor_style
    
    def render_price_chart(self, data_points: List[Dict], symbol: str, 
                          timeframe_label: str) -> pygame.Surface:
        """Render enhanced chart"""
        if not data_points or len(data_points) < 2:
            return self.render_no_data_chart()
            
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        visible_data = self._get_visible_data(data_points)
        if len(visible_data) < 2:
            return surface
        
        prices = [point['price'] for point in visible_data]
        timestamps = [point['timestamp'] for point in visible_data]
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else max_price * 0.1
        
        first_price = prices[0]
        last_price = prices[-1]
        change_percent = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
        line_color = self._get_trend_color(change_percent)
        
        chart_points = self._calculate_chart_points(visible_data, min_price, price_range)
        
        self._render_enhanced_grid(surface, min_price, max_price, timestamps)
        self._render_chart_fill(surface, chart_points, line_color)
        self._render_smooth_line(surface, chart_points, line_color)
        self._render_interactive_points(surface, chart_points, visible_data, line_color)
        self._render_professional_axes(surface, min_price, max_price, timestamps)
        self._render_title_with_stats(surface, symbol, timeframe_label, change_percent)
        
        return surface
    
    def _get_visible_data(self, data_points: List[Dict]) -> List[Dict]:
        """Get visible data for zoom/pan"""
        if self.zoom_factor <= 1.0:
            return data_points
        
        total_points = len(data_points)
        visible_count = int(total_points / self.zoom_factor)
        
        center_index = total_points // 2 + int(self.pan_offset)
        start_index = max(0, center_index - visible_count // 2)
        end_index = min(total_points, start_index + visible_count)
        
        return data_points[start_index:end_index]
    
    def _calculate_chart_points(self, data_points: List[Dict], min_price: float, 
                               price_range: float) -> List[Tuple[int, int]]:
        """Calculate chart coordinates"""
        chart_points = []
        for i, point in enumerate(data_points):
            x = self.chart_rect.left + (i / (len(data_points) - 1)) * self.chart_rect.width
            y = self.chart_rect.bottom - ((point['price'] - min_price) / price_range) * self.chart_rect.height
            chart_points.append((int(x), int(y)))
        return chart_points
    
    def _render_enhanced_grid(self, surface: pygame.Surface, min_price: float, 
                             max_price: float, timestamps: List):
        """Render professional grid"""
        for i in range(0, 11, 2):
            alpha = 100 if i % 4 == 0 else 60
            color = (*self.colors['grid_major'], alpha)
            
            x = self.chart_rect.left + (i / 10) * self.chart_rect.width
            pygame.draw.line(surface, color[:3], 
                           (x, self.chart_rect.top), (x, self.chart_rect.bottom), 1)
            
            y = self.chart_rect.top + (i / 10) * self.chart_rect.height
            pygame.draw.line(surface, color[:3], 
                           (self.chart_rect.left, y), (self.chart_rect.right, y), 1)
        
        for i in range(1, 10, 2):
            color = (*self.colors['grid_minor'], 40)
            x = self.chart_rect.left + (i / 10) * self.chart_rect.width
            pygame.draw.line(surface, color[:3], 
                           (x, self.chart_rect.top), (x, self.chart_rect.bottom), 1)
    
    def _render_chart_fill(self, surface: pygame.Surface, points: List[Tuple[int, int]], 
                          color: Tuple[int, int, int]):
        """Render gradient fill"""
        if len(points) < 2:
            return
            
        fill_points = points.copy()
        fill_points.append((points[-1][0], self.chart_rect.bottom))
        fill_points.append((points[0][0], self.chart_rect.bottom))
        
        fill_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        for i in range(25):
            alpha = int(80 * (1 - i / 25) * 0.7)
            if alpha > 0:
                layer_color = (*color, alpha)
                offset_points = []
                for point in fill_points:
                    offset_y = point[1] + i
                    offset_points.append((point[0], min(offset_y, self.chart_rect.bottom)))
                pygame.draw.polygon(fill_surface, layer_color, offset_points)
                
        surface.blit(fill_surface, (0, 0))
    
    def _render_smooth_line(self, surface: pygame.Surface, points: List[Tuple[int, int]], 
                           color: Tuple[int, int, int]):
        """Render smooth line"""
        if len(points) < 2:
            return
            
        glow_layers = [(4, 30), (3, 50), (2, 80), (1, 255)]
        
        for thickness, alpha in glow_layers:
            if thickness > 1:
                line_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                line_color = (*color, alpha)
                pygame.draw.lines(line_surface, line_color, False, points, thickness)
                surface.blit(line_surface, (0, 0))
            else:
                pygame.draw.lines(surface, color, False, points, thickness)
    
    def _render_interactive_points(self, surface: pygame.Surface, chart_points: List[Tuple[int, int]], 
                                  data_points: List[Dict], color: Tuple[int, int, int]):
        """Enhanced interactive points with professional tooltips"""
        mouse_x, mouse_y = self.mouse_pos
        hover_radius = 35
        closest_point = None
        closest_distance = float('inf')
        
        for i, (point, data) in enumerate(zip(chart_points, data_points)):
            x, y = point
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)
            
            if distance < hover_radius and distance < closest_distance:
                closest_distance = distance
                closest_point = (i, point, data)
        
        self.hovered_point_index = closest_point[0] if closest_point else None
        
        # Enhanced tooltip
        if closest_point and not self.tooltip.pinned:
            point_x, point_y = closest_point[1]
            data = closest_point[2]
            
            tooltip_data = {
                'price': data['price'],
                'time': data['timestamp'].strftime("%m/%d %H:%M"),
                'volume': data.get('volume', 0)
            }
            
            if closest_point[0] > 0:
                tooltip_data['prev_price'] = data_points[closest_point[0] - 1]['price']
            
            self.tooltip.show((mouse_x + 25, mouse_y - 25), tooltip_data)
        elif not closest_point and not self.tooltip.pinned:
            self.tooltip.hide()
        
        # Professional crosshair
        if self.hovered_point_index is not None:
            point_x, point_y = chart_points[self.hovered_point_index]
            
            crosshair_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            
            # Gradient crosshair
            for i in range(3):
                alpha = 200 - i * 60
                pygame.draw.line(crosshair_surface, (120, 180, 255, alpha), 
                               (point_x - i, self.chart_rect.top), 
                               (point_x - i, self.chart_rect.bottom), 1)
                pygame.draw.line(crosshair_surface, (120, 180, 255, alpha), 
                               (point_x + i, self.chart_rect.top), 
                               (point_x + i, self.chart_rect.bottom), 1)
                pygame.draw.line(crosshair_surface, (120, 180, 255, alpha), 
                               (self.chart_rect.left, point_y - i), 
                               (self.chart_rect.right, point_y - i), 1)
                pygame.draw.line(crosshair_surface, (120, 180, 255, alpha), 
                               (self.chart_rect.left, point_y + i), 
                               (self.chart_rect.right, point_y + i), 1)
            
            surface.blit(crosshair_surface, (0, 0))
            
            # Professional point highlight
            for radius in [15, 10, 6, 3]:
                if radius == 3:
                    pygame.draw.circle(surface, (255, 255, 255), (point_x, point_y), radius)
                    pygame.draw.circle(surface, color, (point_x, point_y), radius - 1)
                else:
                    alpha = 150 - (radius - 3) * 20
                    ring_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, (*color, alpha), (radius, radius), radius, 2)
                    surface.blit(ring_surface, (point_x - radius, point_y - radius))
            
            # Professional price label
            price = data_points[self.hovered_point_index]['price']
            price_text = format_price(price)
            label_font = pygame.font.SysFont("Segoe UI", 10, bold=True)
            text_surface = label_font.render(price_text, True, (255, 255, 255))
            
            label_width = text_surface.get_width() + 12
            label_height = text_surface.get_height() + 6
            label_x = self.chart_rect.right + 8
            label_y = point_y - label_height // 2
            
            label_surface = pygame.Surface((label_width, label_height), pygame.SRCALPHA)
            pygame.draw.rect(label_surface, (*color, 240), (0, 0, label_width, label_height), border_radius=4)
            pygame.draw.rect(label_surface, (255, 255, 255, 180), (0, 0, label_width, label_height), 1, border_radius=4)
            
            label_surface.blit(text_surface, (6, 3))
            surface.blit(label_surface, (label_x, label_y))
    
    def _render_professional_axes(self, surface: pygame.Surface, min_price: float, 
                                 max_price: float, timestamps: List):
        """Render professional axes"""
        label_font = pygame.font.SysFont("Segoe UI", 9)
        
        price_steps = 6
        for i in range(price_steps):
            price = min_price + (i / (price_steps - 1)) * (max_price - min_price)
            y = self.chart_rect.bottom - (i / (price_steps - 1)) * self.chart_rect.height
            
            price_text = format_price(price)
            text_surface = label_font.render(price_text, True, self.colors['text'])
            
            bg_width = text_surface.get_width() + 6
            bg_height = text_surface.get_height() + 2
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            bg_surface.fill((15, 20, 28, 200))
            
            surface.blit(bg_surface, (5, y - bg_height // 2))
            surface.blit(text_surface, (8, y - text_surface.get_height() // 2))
        
        if timestamps:
            time_steps = min(6, len(timestamps))
            for i in range(time_steps):
                timestamp_index = int(i * (len(timestamps) - 1) / (time_steps - 1))
                timestamp = timestamps[timestamp_index]
                x = self.chart_rect.left + (i / (time_steps - 1)) * self.chart_rect.width
                
                time_text = timestamp.strftime("%H:%M")
                text_surface = label_font.render(time_text, True, self.colors['text'])
                
                text_x = x - text_surface.get_width() // 2
                text_y = self.chart_rect.bottom + 8
                
                bg_surface = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 2), pygame.SRCALPHA)
                bg_surface.fill((15, 20, 28, 200))
                
                surface.blit(bg_surface, (text_x - 2, text_y))
                surface.blit(text_surface, (text_x, text_y + 1))
    
    def _render_title_with_stats(self, surface: pygame.Surface, symbol: str, 
                               timeframe_label: str, change_percent: float):
        """Render title with stats"""
        title_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        stats_font = pygame.font.SysFont("Segoe UI", 11)
        
        title_text = f"{symbol} • {timeframe_label}"
        if self.zoom_factor > 1.0:
            title_text += f" (Zoom: {self.zoom_factor:.1f}x)"
        
        title_surface = title_font.render(title_text, True, (220, 230, 250))
        
        change_color = self._get_trend_color(change_percent)
        change_text = f"{change_percent:+.2f}%"
        change_surface = stats_font.render(change_text, True, change_color)
        
        if self.zoom_factor > 1.0:
            instruction_text = "Drag to pan • Scroll to zoom • Right-click to unpin"
            instruction_surface = pygame.font.SysFont("Segoe UI", 9).render(instruction_text, True, (140, 160, 180))
        else:
            instruction_text = "Hover for analysis • Click to pin • Scroll to zoom"
            instruction_surface = pygame.font.SysFont("Segoe UI", 9).render(instruction_text, True, (140, 160, 180))
        
        title_x = self.chart_rect.left
        title_y = 8
        
        surface.blit(title_surface, (title_x, title_y))
        surface.blit(change_surface, (title_x + title_surface.get_width() + 15, title_y + 3))
        surface.blit(instruction_surface, (title_x, title_y + 25))
    
    def _get_trend_color(self, change_percent: float) -> Tuple[int, int, int]:
        """Get trend color"""
        if change_percent > 2:
            return (80, 220, 120)
        elif change_percent > 0:
            return (120, 200, 120)
        elif change_percent < -2:
            return (220, 80, 80)
        elif change_percent < 0:
            return (200, 120, 120)
        else:
            return self.colors['primary']
    
    def render_no_data_chart(self) -> pygame.Surface:
        """Render no-data state"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((15, 20, 28))
        
        font = pygame.font.SysFont("Segoe UI", 16)
        text = "Loading chart data..."
        text_surface = font.render(text, True, (120, 140, 160))
        
        x = (self.width - text_surface.get_width()) // 2
        y = (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (x, y))
        
        dots = "." * (int(time.time() * 2) % 4)
        dots_surface = font.render(dots, True, (120, 140, 160))
        surface.blit(dots_surface, (x + text_surface.get_width(), y))
        
        return surface
    
    def render_tooltip(self, surface: pygame.Surface):
        """Render tooltip"""
        self.tooltip.render(surface)
    
    def handle_mouse_move(self, pos: Tuple[int, int]):
        """Handle mouse movement"""
        self.handle_mouse_motion(pos)

class ProfessionalButton:
    """Professional button with click detection"""
    
    def __init__(self, rect: pygame.Rect, text: str, active: bool = False):
        self.rect = rect
        self.text = text
        self.active = active
        self.hover = False
        self.click_time = 0
        
    def update(self, dt: float, mouse_pos: tuple):
        """Update button state"""
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if self.click_time > 0:
            self.click_time = max(0, self.click_time - dt)
        
    def handle_click(self, mouse_pos: tuple) -> bool:
        """Handle click detection"""
        if self.rect.collidepoint(mouse_pos):
            self.click_time = 0.2
            return True
        return False
        
    def render(self, surface: pygame.Surface):
        """Render professional button"""
        if self.active:
            bg_color = (80, 120, 180)
            text_color = (255, 255, 255)
            border_color = (100, 140, 200)
        elif self.hover:
            bg_color = (50, 60, 80)
            text_color = (220, 230, 255)
            border_color = (80, 100, 130)
        else:
            bg_color = (35, 42, 55)
            text_color = (160, 180, 200)
            border_color = (60, 70, 85)
            
        if self.click_time > 0:
            intensity = int(40 * (self.click_time / 0.2))
            bg_color = tuple(min(255, c + intensity) for c in bg_color)
            
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=4)
        
        font = pygame.font.SysFont("Segoe UI", 11, bold=True)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class ProfessionalCryptoModal:
    """Professional crypto modal with enhanced chart interactions"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.symbol = coin_data['symbol'].upper()
        self.is_active = False
        
        self.width = int(screen_size[0] * 0.85)
        self.height = int(screen_size[1] * 0.85)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        chart_width = self.width - 320
        chart_height = self.height - 180
        self.chart_renderer = ProfessionalChartRenderer(chart_width, chart_height)
        
        self.data_generator = HistoricalDataGenerator()
        
        self.selected_timeframe = "7d"
        self.chart_surface = None
        self.loading_chart = False
        self.entrance_animation = 0
        
        self.timeframes = {
            "1d": {"label": "1D", "days": 1},
            "7d": {"label": "7D", "days": 7}, 
            "30d": {"label": "30D", "days": 30},
            "90d": {"label": "90D", "days": 90},
            "1y": {"label": "1Y", "days": 365}
        }
        
        self.buttons = {}
        self.create_buttons()
        
        self.mouse_pos = (0, 0)
        self.close_button_rect = None
        self.current_cursor = 'default'
        
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
        """Generate chart"""
        try:
            self.loading_chart = True
            
            timeframe_info = self.timeframes[self.selected_timeframe]
            current_price = self.coin_data.get('current_price', 1.0)
            
            data_points = self.data_generator.generate_realistic_data(
                current_price, self.symbol, timeframe_info['days']
            )
            
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
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        
        modal_rect = pygame.Rect(0, 0, self.width, self.height)
        if not modal_rect.collidepoint(relative_pos):
            self.close()
            return True
            
        if self.close_button_rect and self.close_button_rect.collidepoint(relative_pos):
            self.close()
            return True
            
        # Chart interactions
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        if hasattr(self.chart_renderer, 'handle_mouse_down'):
            self.chart_renderer.handle_mouse_down(chart_relative_pos, 1)
            
        # Timeframe buttons
        for timeframe, button in self.buttons.items():
            if button.handle_click(relative_pos):
                if timeframe != self.selected_timeframe:
                    self.selected_timeframe = timeframe
                    
                    for key, btn in self.buttons.items():
                        btn.active = (key == timeframe)
                    
                    self.generate_chart()
                return True
                
        return True
    
    def handle_right_click(self, pos: tuple) -> bool:
        """Handle right-click"""
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        if hasattr(self.chart_renderer, 'handle_mouse_down'):
            self.chart_renderer.handle_mouse_down(chart_relative_pos, 3)
            
        return True
    
    def handle_mouse_up(self, pos: tuple, button: int) -> bool:
        """Handle mouse release"""
        if not self.is_active:
            return False
            
        relative_pos = (pos[0] - self.x, pos[1] - self.y)
        chart_x, chart_y = 40, 130
        chart_relative_pos = (relative_pos[0] - chart_x, relative_pos[1] - chart_y)
        
        if hasattr(self.chart_renderer, 'handle_mouse_up'):
            self.chart_renderer.handle_mouse_up(chart_relative_pos, button)
            
        return True
    
    def handle_scroll(self, pos: tuple, scroll_y: int) -> bool:
        """Handle scroll"""
        if not self.is_active:
            return False
            
        if hasattr(self.chart_renderer, 'handle_scroll'):
            self.chart_renderer.handle_scroll(scroll_y)
            
        return True
    
    def handle_mouse_move(self, pos: tuple):
        """Handle mouse movement"""
        self.mouse_pos = pos
        
        chart_x = self.x + 40
        chart_y = self.y + 130
        
        relative_pos = (pos[0] - chart_x, pos[1] - chart_y)
        self.chart_renderer.handle_mouse_motion(relative_pos)
        
        if hasattr(self.chart_renderer, 'get_cursor_style'):
            desired_cursor = self.chart_renderer.get_cursor_style()
            if desired_cursor != self.current_cursor:
                self.current_cursor = desired_cursor
                self._update_pygame_cursor(desired_cursor)
    
    def _update_pygame_cursor(self, cursor_style: str):
        """Update cursor"""
        cursor_map = {
            'default': pygame.SYSTEM_CURSOR_ARROW,
            'pointer': pygame.SYSTEM_CURSOR_HAND,
            'crosshair': pygame.SYSTEM_CURSOR_CROSSHAIR,
            'grabbing': pygame.SYSTEM_CURSOR_SIZEALL
        }
        
        if cursor_style in cursor_map:
            try:
                pygame.mouse.set_cursor(cursor_map[cursor_style])
            except:
                pass
        
    def open(self):
        """Open modal"""
        self.is_active = True
        self.entrance_animation = 0
        
    def close(self):
        """Close modal"""
        self.is_active = False
        
    def update(self, dt: float):
        """Update modal"""
        if not self.is_active:
            return
            
        if self.entrance_animation < 1.0:
            self.entrance_animation = min(1.0, self.entrance_animation + dt * 6)
            
        relative_mouse = (self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y)
        for button in self.buttons.values():
            button.update(dt, relative_mouse)
            
        chart_mouse = (
            self.mouse_pos[0] - self.x - 40,
            self.mouse_pos[1] - self.y - 130
        )
        self.chart_renderer.update(dt, chart_mouse)
        
    def draw(self, surface: pygame.Surface):
        """Draw modal"""
        if not self.is_active:
            return
            
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay_alpha = int(200 * self.entrance_animation)
        overlay.fill((0, 0, 0, overlay_alpha))
        surface.blit(overlay, (0, 0))
        
        modal_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.render_background(modal_surface)
        self.render_header(modal_surface)
        self.render_timeframe_buttons(modal_surface)
        self.render_chart_area(modal_surface)
        self.render_stats_panel(modal_surface)
        self.render_close_button(modal_surface)
        
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
        """Render background"""
        pygame.draw.rect(surface, (20, 25, 35), (0, 0, self.width, self.height), 
                        border_radius=12)
        pygame.draw.rect(surface, (70, 90, 120), (0, 0, self.width, self.height), 
                        2, border_radius=12)
        pygame.draw.rect(surface, (35, 45, 60), (1, 1, self.width-2, self.height-2), 
                        1, border_radius=11)
                        
    def render_header(self, surface: pygame.Surface):
        """Render header"""
        logo_size = 40
        logo_x, logo_y = 30, 20
        
        logo_path = f"assets/logos/{self.symbol.lower()}.png"
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                surface.blit(logo, (logo_x, logo_y))
            except:
                pygame.draw.circle(surface, (80, 120, 180), 
                                 (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
        else:
            pygame.draw.circle(surface, (80, 120, 180), 
                             (logo_x + logo_size//2, logo_y + logo_size//2), logo_size//2)
                             
        name_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        symbol_font = pygame.font.SysFont("Segoe UI", 14)
        
        coin_name = self.coin_data.get('name', self.symbol)
        if len(coin_name) > 25:
            coin_name = coin_name[:25] + "..."
            
        name_surface = name_font.render(coin_name, True, (220, 230, 250))
        symbol_surface = symbol_font.render(f"{self.symbol}", True, (160, 180, 210))
        
        surface.blit(name_surface, (logo_x + logo_size + 15, logo_y + 2))
        surface.blit(symbol_surface, (logo_x + logo_size + 15, logo_y + 28))
        
        current_price = self.coin_data.get('current_price', 0)
        price_text = format_price(current_price)
        price_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        price_surface = price_font.render(price_text, True, (255, 255, 255))
        
        price_x = self.width - price_surface.get_width() - 120
        surface.blit(price_surface, (price_x, logo_y + 2))
        
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
        """Render chart area"""
        chart_x, chart_y = 40, 130
        
        if self.loading_chart:
            loading_surface = self.chart_renderer.render_no_data_chart()
            surface.blit(loading_surface, (chart_x, chart_y))
        elif self.chart_surface:
            surface.blit(self.chart_surface, (chart_x, chart_y))
            self.chart_renderer.render_tooltip(surface)
            
    def render_stats_panel(self, surface: pygame.Surface):
        """Render stats panel"""
        panel_x = self.width - 280
        panel_y = 80
        panel_width = 260
        panel_height = self.height - 120
        
        pygame.draw.rect(surface, (25, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=8)
        pygame.draw.rect(surface, (60, 80, 110), 
                        (panel_x, panel_y, panel_width, panel_height), 1, border_radius=8)
        
        header_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        title_surface = header_font.render("MARKET DATA", True, (180, 200, 230))
        surface.blit(title_surface, (panel_x + 20, panel_y + 20))
        
        label_font = pygame.font.SysFont("Segoe UI", 10)
        value_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
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
            
            if "Market Cap" in label or "Volume" in label:
                value_color = (120, 200, 150)
            elif "Rank" in label:
                value_color = (200, 180, 120)
            else:
                value_color = (200, 220, 255)
                
            value_surface = value_font.render(str(value), True, value_color)
            surface.blit(value_surface, (panel_x + 20, current_y + 15))
            
    def render_close_button(self, surface: pygame.Surface):
        """Render close button"""
        button_size = 32
        button_x = self.width - button_size - 15
        button_y = 15
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        relative_mouse = (self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y)
        mouse_in_button = self.close_button_rect.collidepoint(relative_mouse)
        
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