"""
Chart data generation for cryptocurrency prices
"""
import pygame
import random
import time
import datetime
import math
from threading import Lock

class HistoricalDataGenerator:
    """Generate realistic historical price data"""
    
    def __init__(self):
        self.data_lock = Lock()
        self.cached_data = {}
    
    def generate_realistic_data(self, current_price, symbol, timeframe_days):
        """Generate realistic historical data based on current price and symbol"""
        if timeframe_days <= 1:
            points = 24
            interval_seconds = 3600  # 1 hour
        elif timeframe_days <= 7:
            points = timeframe_days * 4
            interval_seconds = 21600  # 6 hours
        elif timeframe_days <= 30:
            points = timeframe_days
            interval_seconds = 86400  # 1 day
        else:
            points = min(timeframe_days, 365)
            interval_seconds = 86400  # 1 day
        
        data_points = []
        current_time = time.time()
        
        # Start with a price that makes sense relative to current price
        base_price = current_price * random.uniform(0.85, 1.15)
        
        # Volatility based on coin type
        if symbol in ['BTC', 'ETH']:
            volatility = 0.03  # Lower volatility for major coins
        elif symbol in ['USDT', 'USDC', 'DAI']:
            volatility = 0.001  # Very low volatility for stablecoins
        else:
            volatility = 0.06  # Higher volatility for altcoins
        
        price = base_price
        for i in range(points):
            timestamp_seconds = current_time - ((points - i) * interval_seconds)
            timestamp = datetime.datetime.fromtimestamp(timestamp_seconds)
            
            # Add some trend (slight upward bias)
            trend = 0.0001 * (i / points)
            
            # Random walk with volatility
            change = random.normalvariate(trend, volatility)
            price *= (1 + change)
            
            # Prevent unrealistic prices
            price = max(price, current_price * 0.1)  # Don't go below 10% of current
            price = min(price, current_price * 5.0)   # Don't go above 500% of current
            
            data_points.append({
                'timestamp': timestamp,
                'price': price,
                'volume': random.uniform(1000000, 10000000)  # Random volume
            })
        
        # Ensure the last price is close to current price
        data_points[-1]['price'] = current_price * random.uniform(0.98, 1.02)
        
        return data_points

class ChartRenderer:
    """Render price charts using pygame"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.margin = 40
        self.chart_area = pygame.Rect(
            self.margin, self.margin, 
            width - 2 * self.margin, 
            height - 2 * self.margin
        )
    
    def render_price_chart(self, data_points, symbol, timeframe_label):
        """Render a price chart from data points"""
        if not data_points or len(data_points) < 2:
            return self.render_no_data_chart()
        
        import pygame
        surface = pygame.Surface((self.width, self.height))
        surface.fill((20, 20, 25))
        
        prices = [point['price'] for point in data_points]
        timestamps = [point['timestamp'] for point in data_points]
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.1
        
        # Determine chart color based on performance
        first_price = prices[0]
        last_price = prices[-1]
        is_positive = last_price >= first_price
        
        line_color = (80, 255, 120) if is_positive else (255, 80, 100)
        fill_color = (*line_color[:3], 60)
        grid_color = (60, 60, 70)
        text_color = (220, 220, 220)
        
        # Draw grid
        self.draw_grid(surface, grid_color)
        
        # Calculate chart points
        chart_points = []
        for i, price in enumerate(prices):
            x = self.chart_area.left + (i / (len(prices) - 1)) * self.chart_area.width
            y = self.chart_area.bottom - ((price - min_price) / price_range) * self.chart_area.height
            chart_points.append((x, y))
        
        # Draw filled area under the line
        if len(chart_points) >= 2:
            fill_points = chart_points.copy()
            fill_points.append((chart_points[-1][0], self.chart_area.bottom))
            fill_points.append((chart_points[0][0], self.chart_area.bottom))
            
            fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(fill_surface, fill_color, fill_points)
            surface.blit(fill_surface, (0, 0))
            
            # Draw price line
            pygame.draw.lines(surface, line_color, False, chart_points, 3)
        
        # Draw data points
        for point in chart_points[::max(1, len(chart_points)//20)]:
            pygame.draw.circle(surface, line_color, [int(point[0]), int(point[1])], 4)
            pygame.draw.circle(surface, (255, 255, 255), [int(point[0]), int(point[1])], 2)
        
        # Draw labels and annotations
        self.draw_price_labels(surface, min_price, max_price, text_color)
        self.draw_time_labels(surface, timestamps, text_color)
        self.draw_title(surface, f"{symbol} - {timeframe_label}", text_color)
        
        # Draw current price line
        current_price_y = self.chart_area.bottom - ((last_price - min_price) / price_range) * self.chart_area.height
        pygame.draw.line(surface, line_color, 
                        (self.chart_area.left, current_price_y), 
                        (self.chart_area.right, current_price_y), 2)
        
        # Price annotation
        if last_price < 0.01:
            price_text = f"${last_price:.6f}"
        elif last_price < 1:
            price_text = f"${last_price:.4f}"
        else:
            price_text = f"${last_price:.2f}"
        
        font = pygame.font.SysFont("Arial", 12, bold=True)
        price_surface = font.render(price_text, True, (255, 255, 255))
        
        # Price label background
        price_bg = pygame.Surface((price_surface.get_width() + 10, price_surface.get_height() + 6), pygame.SRCALPHA)
        price_bg.fill((*line_color, 200))
        surface.blit(price_bg, (self.chart_area.right - price_surface.get_width() - 15, 
                               current_price_y - price_surface.get_height() // 2 - 3))
        surface.blit(price_surface, (self.chart_area.right - price_surface.get_width() - 10, 
                                   current_price_y - price_surface.get_height() // 2))
        
        return surface
    
    def draw_grid(self, surface, color):
        """Draw grid lines"""
        import pygame
        # Vertical lines
        for i in range(5):
            x = self.chart_area.left + (i / 4) * self.chart_area.width
            pygame.draw.line(surface, color, (x, self.chart_area.top), (x, self.chart_area.bottom), 1)
        
        # Horizontal lines
        for i in range(5):
            y = self.chart_area.top + (i / 4) * self.chart_area.height
            pygame.draw.line(surface, color, (self.chart_area.left, y), (self.chart_area.right, y), 1)
    
    def draw_price_labels(self, surface, min_price, max_price, color):
        """Draw price labels on Y-axis"""
        import pygame
        font = pygame.font.SysFont("Arial", 10)
        
        for i in range(5):
            price = min_price + (i / 4) * (max_price - min_price)
            y = self.chart_area.bottom - (i / 4) * self.chart_area.height
            
            if price < 0.01:
                price_text = f"${price:.6f}"
            elif price < 1:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.2f}"
            
            text_surface = font.render(price_text, True, color)
            surface.blit(text_surface, (5, y - text_surface.get_height() // 2))
    
    def draw_time_labels(self, surface, timestamps, color):
        """Draw time labels on X-axis"""
        import pygame
        font = pygame.font.SysFont("Arial", 10)
        
        for i in range(4):
            if i < len(timestamps):
                timestamp = timestamps[int(i * (len(timestamps) - 1) / 3)]
                x = self.chart_area.left + (i / 3) * self.chart_area.width
                
                time_text = timestamp.strftime("%m/%d %H:%M")
                text_surface = font.render(time_text, True, color)
                surface.blit(text_surface, (x - text_surface.get_width() // 2, self.chart_area.bottom + 5))
    
    def draw_title(self, surface, title, color):
        """Draw chart title"""
        import pygame
        font = pygame.font.SysFont("Arial", 16, bold=True)
        text_surface = font.render(title, True, color)
        x = (self.width - text_surface.get_width()) // 2
        surface.blit(text_surface, (x, 5))
    
    def render_no_data_chart(self):
        """Render a placeholder chart when no data is available"""
        import pygame
        surface = pygame.Surface((self.width, self.height))
        surface.fill((20, 20, 25))
        
        font = pygame.font.SysFont("Arial", 18, bold=True)
        text = "No chart data available"
        text_surface = font.render(text, True, (150, 150, 150))
        
        x = (self.width - text_surface.get_width()) // 2
        y = (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (x, y))
        
        return surface