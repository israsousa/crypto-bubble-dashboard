"""
Cryptocurrency detail modal with charts
"""

import pygame
import os
import time
import random
import datetime
from threading import Thread
from config.settings import COLORS, FONT_SIZES, SYMBOL_TO_ID
from utils.formatters import format_large_number, format_supply, format_price
from data.chart_data import HistoricalDataGenerator, ChartRenderer

class CryptoDetailModal:
    """Enhanced modal with working charts using pygame"""
    
    def __init__(self, coin_data, screen_size):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.symbol = coin_data['symbol'].upper()
        self.is_active = False
        
        # Modal dimensions
        self.width = int(screen_size[0] * 0.85)
        self.height = int(screen_size[1] * 0.85)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        # Chart properties
        self.selected_timeframe = "7d"
        self.chart_surface = None
        self.loading_chart = False
        
        # Data generator and chart renderer
        self.data_generator = HistoricalDataGenerator()
        chart_width = self.width - 100
        chart_height = self.height - 300
        self.chart_renderer = ChartRenderer(chart_width, chart_height)
        
        # Timeframes
        self.timeframes = {
            "1d": {"label": "1D", "days": 1},
            "7d": {"label": "7D", "days": 7},
            "30d": {"label": "30D", "days": 30},
            "90d": {"label": "90D", "days": 90},
            "1y": {"label": "1Y", "days": 365}
        }
        
        # UI elements
        self.button_rects = {}
        self.close_button_rect = None
        
        print(f"📊 Creating enhanced modal for {self.symbol}")
        
        # Generate initial chart
        self.generate_chart()
    
    def generate_chart(self):
        """Generate chart for current timeframe"""
        try:
            self.loading_chart = True
            
            timeframe_info = self.timeframes[self.selected_timeframe]
            current_price = self.coin_data.get('current_price', 1.0)
            
            print(f"📈 Generating chart for {self.symbol} ({timeframe_info['label']})")
            
            # Generate historical data
            data_points = self.data_generator.generate_realistic_data(
                current_price, 
                self.symbol, 
                timeframe_info['days']
            )
            
            # Render chart
            self.chart_surface = self.chart_renderer.render_price_chart(
                data_points, 
                self.symbol, 
                timeframe_info['label']
            )
            
            print(f"✅ Chart generated successfully for {self.symbol}")
            
        except Exception as e:
            print(f"❌ Error generating chart: {e}")
            self.chart_surface = self.chart_renderer.render_no_data_chart()
        
        self.loading_chart = False
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        if not self.is_active:
            return False
        
        # Check if outside modal
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not modal_rect.collidepoint(pos):
            self.close()
            return True
        
        # Close button
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close()
            return True
        
        # Timeframe buttons
        for timeframe, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                if timeframe != self.selected_timeframe:
                    self.selected_timeframe = timeframe
                    print(f"📊 Switching to {timeframe} timeframe for {self.symbol}")
                    self.generate_chart()
                return True
        
        return True
    
    def open(self):
        """Open the modal"""
        self.is_active = True
        print(f"📱 Modal opened for {self.symbol}")
    
    def close(self):
        """Close the modal"""
        self.is_active = False
        print(f"❌ Modal closed for {self.symbol}")
    
    def draw(self, surface):
        """Draw the complete modal"""
        if not self.is_active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen_size)
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Modal background
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS['modal_bg'], modal_rect, border_radius=15)
        pygame.draw.rect(surface, (70, 70, 80), modal_rect, 3, border_radius=15)
        
        # Draw all components
        self.draw_header(surface)
        self.draw_timeframe_buttons(surface)
        self.draw_chart_area(surface)
        self.draw_statistics(surface)
        self.draw_close_button(surface)
    
    def draw_header(self, surface):
        """Draw header with coin information"""
        header_y = self.y + 20
        
        # Coin logo
        logo_path = f"assets/logos/{self.symbol.lower()}.png"
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (50, 50))
                surface.blit(logo, (self.x + 30, header_y))
            except:
                pass
        
        # Coin name and symbol
        name_font = pygame.font.SysFont("Arial", 24, bold=True)
        symbol_font = pygame.font.SysFont("Arial", 18)
        
        name_text = self.coin_data.get('name', self.symbol)
        if len(name_text) > 30:
            name_text = name_text[:30] + "..."
        
        name_surface = name_font.render(name_text, True, COLORS['text_primary'])
        symbol_surface = symbol_font.render(self.symbol, True, COLORS['text_secondary'])
        
        surface.blit(name_surface, (self.x + 90, header_y + 5))
        surface.blit(symbol_surface, (self.x + 90, header_y + 35))
        
        # Current price
        price_text = format_price(self.coin_data.get('current_price', 0))
        price_font = pygame.font.SysFont("Arial", 28, bold=True)
        price_surface = price_font.render(price_text, True, COLORS['text_primary'])
        price_x = self.x + self.width - price_surface.get_width() - 120
        surface.blit(price_surface, (price_x, header_y + 5))
        
        # 24h change
        change_24h = self.coin_data.get('price_change_percentage_24h', 0) or 0
        change_color = COLORS['positive'] if change_24h >= 0 else COLORS['negative']
        change_text = f"{change_24h:+.2f}%"
        
        change_font = pygame.font.SysFont("Arial", 20, bold=True)
        change_surface = change_font.render(change_text, True, change_color)
        surface.blit(change_surface, (price_x, header_y + 40))
    
    def draw_timeframe_buttons(self, surface):
        """Draw timeframe selection buttons"""
        button_y = self.y + 90
        button_width = 70
        button_height = 35
        button_spacing = 15
        
        self.button_rects.clear()
        
        start_x = self.x + 30
        for i, (key, info) in enumerate(self.timeframes.items()):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Button styling
            if key == self.selected_timeframe:
                button_color = (70, 130, 255)
                text_color = COLORS['text_primary']
                border_color = (100, 150, 255)
            else:
                button_color = (45, 45, 55)
                text_color = COLORS['text_secondary']
                border_color = (80, 80, 100)
            
            pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=8)
            
            # Button text
            button_font = pygame.font.SysFont("Arial", 14, bold=True)
            text_surface = button_font.render(info['label'], True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)
            
            self.button_rects[key] = button_rect
    
    def draw_chart_area(self, surface):
        """Draw the chart area"""
        chart_y = self.y + 140
        chart_width = self.width - 60
        chart_height = self.height - 280
        
        # Chart background
        chart_rect = pygame.Rect(self.x + 30, chart_y, chart_width, chart_height)
        pygame.draw.rect(surface, (15, 15, 20), chart_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 60, 70), chart_rect, 2, border_radius=10)
        
        if self.loading_chart:
            # Loading indicator
            font = pygame.font.SysFont("Arial", 18)
            text = font.render("Generating chart...", True, COLORS['neutral'])
            text_rect = text.get_rect(center=chart_rect.center)
            surface.blit(text, text_rect)
        
        elif self.chart_surface:
            # Display chart
            chart_scaled = pygame.transform.scale(self.chart_surface, (chart_width - 20, chart_height - 20))
            surface.blit(chart_scaled, (chart_rect.x + 10, chart_rect.y + 10))
        
        else:
            # No chart available
            font = pygame.font.SysFont("Arial", 16)
            text = font.render("Chart unavailable", True, COLORS['negative'])
            text_rect = text.get_rect(center=chart_rect.center)
            surface.blit(text, text_rect)
    
    def draw_statistics(self, surface):
        """Draw coin statistics"""
        stats_y = self.y + self.height - 120
        
        # Stats styling
        stats_font = pygame.font.SysFont("Arial", 13, bold=True)
        label_font = pygame.font.SysFont("Arial", 11)
        
        # Prepare statistics
        market_cap = self.coin_data.get('market_cap', 0)
        volume = self.coin_data.get('total_volume', 0)
        rank = self.coin_data.get('market_cap_rank', 'N/A')
        supply = self.coin_data.get('circulating_supply', 0)
        
        stats = [
            ("Market Cap", format_large_number(market_cap)),
            ("Volume 24h", format_large_number(volume)),
            ("Rank", f"#{rank}" if rank != 'N/A' else 'N/A'),
            ("Supply", format_supply(supply))
        ]
        
        # Layout statistics
        stat_width = (self.width - 100) // len(stats)
        
        for i, (label, value) in enumerate(stats):
            stat_x = self.x + 30 + i * stat_width
            
            # Stat background
            stat_bg = pygame.Rect(stat_x, stats_y - 10, stat_width - 15, 60)
            pygame.draw.rect(surface, (35, 35, 40), stat_bg, border_radius=8)
            pygame.draw.rect(surface, (60, 60, 70), stat_bg, 1, border_radius=8)
            
            # Label
            label_surface = label_font.render(label, True, COLORS['neutral'])
            surface.blit(label_surface, (stat_x + 10, stats_y))
            
            # Value
            value_surface = stats_font.render(str(value), True, COLORS['text_primary'])
            surface.blit(value_surface, (stat_x + 10, stats_y + 20))
    
    def draw_close_button(self, surface):
        """Draw close button"""
        button_size = 32
        button_x = self.x + self.width - button_size - 15
        button_y = self.y + 15
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Button styling
        pygame.draw.rect(surface, (255, 70, 70), self.close_button_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 120, 120), self.close_button_rect, 2, border_radius=16)
        
        # X symbol
        close_font = pygame.font.SysFont("Arial", 20, bold=True)
        close_surface = close_font.render("×", True, COLORS['text_primary'])
        close_rect = close_surface.get_rect(center=self.close_button_rect.center)
        surface.blit(close_surface, close_rect)