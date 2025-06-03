"""
Cryptocurrency table component with reduced font sizes
"""

import pygame
import time
import os
from config.settings import COLORS, FONT_SIZES
from utils.rank_tracker import get_daily_rank_change
from utils.formatters import format_large_number, format_supply, format_price

class CryptoTable:
    """Enhanced table with daily rank tracking and smaller fonts"""
    
    def __init__(self):
        self.page_size = 15
        self.current_page = 0
        self.last_page_switch = time.time()
        self.page_switch_interval = 10
        self.headers = ["#", "Coin", "Price", "Market Cap", "24h Change", "Volume"]
    
    def calculate_optimal_layout(self, available_height):
        """Calculate optimal layout"""
        header_height = 40
        footer_height = 20
        margin = 8
        
        usable_height = available_height - header_height - footer_height - margin
        min_row_height = 28
        max_row_height = 42
        
        best_config = None
        best_efficiency = 0
        
        for row_height in range(min_row_height, max_row_height + 1):
            rows_that_fit = usable_height // row_height
            if rows_that_fit >= 8:
                used_space = rows_that_fit * row_height
                efficiency = used_space / usable_height
                
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_config = (rows_that_fit, row_height)
        
        if best_config is None:
            rows_that_fit = max(8, usable_height // min_row_height)
            row_height = usable_height // rows_that_fit
            best_config = (rows_that_fit, row_height)
        
        return best_config[0], best_config[1], header_height
    
    def update(self):
        """Update table pagination"""
        pass
    
    def update_pagination(self, total_items, rows_per_page):
        """Update pagination logic"""
        now = time.time()
        if now - self.last_page_switch > self.page_switch_interval:
            self.current_page += 1
            max_pages = max(1, (total_items + rows_per_page - 1) // rows_per_page)
            if self.current_page >= max_pages:
                self.current_page = 0
            self.last_page_switch = now
    
    def draw(self, surface, crypto_data):
        """Draw the cryptocurrency table with smaller fonts"""
        surface.fill(COLORS['panel_bg'])
        
        if not crypto_data:
            font = pygame.font.SysFont("Arial", 16, bold=True)
            loading_surface = font.render("Loading cryptocurrency data...", True, COLORS['neutral'])
            surface.blit(loading_surface, (10, 50))
            return
        
        width, height = surface.get_size()
        rows_per_page, row_height, header_height = self.calculate_optimal_layout(height)
        
        self.update_pagination(len(crypto_data), rows_per_page)
        
        # Column widths
        col_widths = [0.15, 0.22, 0.18, 0.18, 0.15, 0.12]
        col_positions = []
        x = 0
        for w in col_widths:
            col_positions.append(x)
            x += w * width
        
        # Font sizes (reduzidos)
        header_font_size = min(16, max(14, row_height // 2 + 2))
        data_font_size = min(12, max(14, row_height // 2 - 1))
        rank_font_size = min(16, max(12, row_height // 3 + 1))
        change_font_size = min(14, max(10, row_height // 4))
        
        header_font = pygame.font.SysFont("Arial", header_font_size, bold=True)
        data_font = pygame.font.SysFont("Arial", data_font_size, bold=True)
        rank_font = pygame.font.SysFont("Arial", rank_font_size, bold=True)
        change_font = pygame.font.SysFont("Arial", change_font_size, bold=True)
        
        # Draw header
        header_rect = pygame.Rect(0, 0, width, header_height)
        pygame.draw.rect(surface, (30, 30, 40), header_rect)
        
        for i, header in enumerate(self.headers):
            text_surface = header_font.render(header, True, (220, 220, 220))
            surface.blit(text_surface, (col_positions[i] + 8, 6))
        
        pygame.draw.line(surface, (60, 60, 80), (0, header_height), (width, header_height), 2)
        
        # Calculate visible rows
        start_idx = self.current_page * rows_per_page
        end_idx = min(start_idx + rows_per_page, len(crypto_data))
        visible_data = crypto_data[start_idx:end_idx]
        
        # Draw data rows
        for i, coin in enumerate(visible_data):
            y = header_height + i * row_height
            
            if i % 2 == 0:
                row_color = (20, 20, 25)
            else:
                row_color = (25, 25, 30)
            
            row_rect = pygame.Rect(0, y, width, row_height)
            pygame.draw.rect(surface, row_color, row_rect)
            
            text_center_y = y + row_height // 2
            
            # Rank column with daily change
            current_rank = start_idx + i + 1
            symbol = coin['symbol'].upper()
            
            rank_change, change_indicator = get_daily_rank_change(symbol)
            
            rank_text = str(current_rank)
            rank_surface = rank_font.render(rank_text, True, (220, 220, 220))
            rank_x = col_positions[0] + 8
            rank_y = text_center_y - rank_surface.get_height() // 2
            surface.blit(rank_surface, (rank_x, rank_y))
            
            if change_indicator and change_indicator != "–":
                change_x = rank_x + rank_surface.get_width() + 6
                
                if rank_change > 0:
                    change_color = COLORS['positive']
                elif rank_change < 0:
                    change_color = COLORS['negative']
                else:
                    change_color = COLORS['neutral']
                
                change_surface = change_font.render(change_indicator, True, change_color)
                change_y = text_center_y - change_surface.get_height() // 2
                surface.blit(change_surface, (change_x, change_y))
            
            # Coin column with logo
            logo_path = f"assets/logos/{symbol.lower()}.png"
            coin_x = col_positions[1] + 8
            logo_size = min(24, row_height - 4)
            
            if os.path.exists(logo_path):
                try:
                    logo = pygame.image.load(logo_path).convert_alpha()
                    logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                    logo_y = y + (row_height - logo_size) // 2
                    surface.blit(logo, (coin_x, logo_y))
                    coin_x += logo_size + 6
                except:
                    pass
            
            symbol_surface = data_font.render(symbol, True, (200, 200, 200))
            symbol_y = text_center_y - symbol_surface.get_height() // 2
            surface.blit(symbol_surface, (coin_x, symbol_y))
            
            # Price column
            price_text = format_price(coin.get('current_price', 0))
            price_surface = data_font.render(price_text, True, (180, 180, 180))
            price_y = text_center_y - price_surface.get_height() // 2
            surface.blit(price_surface, (col_positions[2] + 8, price_y))
            
            # Market cap column
            mc_text = format_large_number(coin.get('market_cap', 0))
            mc_surface = data_font.render(mc_text, True, (180, 180, 180))
            mc_y = text_center_y - mc_surface.get_height() // 2
            surface.blit(mc_surface, (col_positions[3] + 8, mc_y))
            
            # 24h change column
            change_24h = coin.get('price_change_percentage_24h', 0) or 0
            change_color = COLORS['positive'] if change_24h >= 0 else COLORS['negative']
            change_text = f"{change_24h:+.2f}%"
            
            change_surface = data_font.render(change_text, True, change_color)
            change_y = text_center_y - change_surface.get_height() // 2
            surface.blit(change_surface, (col_positions[4] + 8, change_y))
            
            # Volume column
            vol_text = format_large_number(coin.get('total_volume', 0))
            vol_surface = data_font.render(vol_text, True, (180, 180, 180))
            vol_y = text_center_y - vol_surface.get_height() // 2
            surface.blit(vol_surface, (col_positions[5] + 8, vol_y))
        
        # Pagination info
        total_pages = max(1, (len(crypto_data) + rows_per_page - 1) // rows_per_page)
        page_info = f"Page {self.current_page + 1} of {total_pages} • {rows_per_page} rows • {len(crypto_data)} cryptocurrencies"
        
        page_font = pygame.font.SysFont("Arial", max(10, data_font_size - 3))
        page_surface = page_font.render(page_info, True, COLORS['neutral'])
        
        page_y = height - 18
        surface.blit(page_surface, (width - page_surface.get_width() - 10, page_y))