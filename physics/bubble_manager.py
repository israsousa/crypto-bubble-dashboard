"""
Bubble Manager for handling multiple cryptocurrency bubbles
"""

import pygame
import time
from threading import Lock

from config.settings import *
from physics.bubble import FloatingBubble
from utils.data_loader import update_loading_state

class BubbleUpdateScheduler:
    """Distribute bubble updates smoothly across time intervals"""
    
    def __init__(self):
        self.update_queue = []
        self.last_update_time = time.time()
        
    def schedule_updates(self, bubbles, new_data, interval):
        """Schedule bubble updates to be distributed over the interval"""
        if not bubbles or not new_data:
            return
            
        self.update_queue.clear()
        
        # Create mapping of symbol to new data
        symbol_to_data = {coin['symbol'].upper(): coin for coin in new_data}
        
        # Schedule updates with delays
        update_delay = interval / max(1, len(bubbles))
        
        for i, bubble in enumerate(bubbles):
            if bubble.symbol in symbol_to_data:
                update_time = time.time() + (i * update_delay)
                self.update_queue.append({
                    'bubble': bubble,
                    'data': symbol_to_data[bubble.symbol],
                    'scheduled_time': update_time
                })
    
    def process_updates(self):
        """Process any scheduled updates that are due"""
        current_time = time.time()
        completed_updates = []
        
        for update in self.update_queue:
            if current_time >= update['scheduled_time']:
                update['bubble'].update_data(update['data'])
                completed_updates.append(update)
        
        # Remove completed updates
        for update in completed_updates:
            self.update_queue.remove(update)

class BubbleManager:
    """Manages all floating bubbles in the application"""
    
    def __init__(self, space):
        self.space = space
        self.bubbles = []
        self.bubbles_created = False
        self.last_bubble_update = time.time()
        self.update_scheduler = BubbleUpdateScheduler()
        self.lock = Lock()
        
    def initialize_bubbles_if_needed(self, crypto_data, screen_size):
        """Create initial bubbles if they haven't been created yet"""
        if not self.bubbles_created and crypto_data:
            width, height = screen_size
            bubble_area = pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                                    int(height * LAYOUT['bubble_height_ratio']))
            self.create_initial_bubbles(crypto_data, bubble_area, screen_size)
            self.bubbles_created = True
            print(f"Bubble manager initialized with {len(self.bubbles)} bubbles!")
    
    def create_initial_bubbles(self, crypto_data, bubble_area, screen_size):
        """Create initial bubbles for top cryptocurrencies"""
        with self.lock:
            print(f"Creating bubbles for top {min(MAX_BUBBLES, len(crypto_data))} cryptocurrencies...")
            
            for coin in crypto_data[:MAX_BUBBLES]:
                try:
                    bubble = FloatingBubble(self.space, coin, bubble_area, screen_size)
                    self.bubbles.append(bubble)
                except Exception as e:
                    print(f"Error creating bubble for {coin.get('symbol', 'Unknown')}: {e}")
            
            print(f"Created {len(self.bubbles)} bubbles successfully")
            update_loading_state('bubbles_ready', True)
    
    def update_screen_size(self, screen_size):
        """Update all bubbles when screen size changes"""
        with self.lock:
            for bubble in self.bubbles:
                bubble.update_radius_for_screen(screen_size)
    
    def update(self, crypto_data):
        """Update bubbles with new data periodically"""
        if not self.bubbles or not crypto_data:
            return
            
        now = time.time()
        if now - self.last_bubble_update > UPDATE_INTERVAL:
            with self.lock:
                # Remove bubbles for coins no longer in top list
                existing_symbols = {bubble.symbol for bubble in self.bubbles}
                data_symbols = {coin['symbol'].upper() for coin in crypto_data}
                
                bubbles_to_remove = []
                for bubble in self.bubbles:
                    if bubble.symbol not in data_symbols:
                        self.space.remove(bubble.body, bubble.shape)
                        bubbles_to_remove.append(bubble)
                
                for bubble in bubbles_to_remove:
                    self.bubbles.remove(bubble)
                
                # Add new bubbles for new coins in top list
                width, height = 1280, 720  # Default size, will be updated
                bubble_area = pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                                        int(height * LAYOUT['bubble_height_ratio']))
                
                for coin in crypto_data[:MAX_BUBBLES]:
                    symbol = coin['symbol'].upper()
                    if symbol not in existing_symbols:
                        try:
                            self.bubbles.append(FloatingBubble(self.space, coin, bubble_area, (width, height)))
                        except Exception as e:
                            print(f"Error creating bubble for {symbol}: {e}")
                
                # Trim to exactly MAX_BUBBLES
                if len(self.bubbles) > MAX_BUBBLES:
                    excess_bubbles = self.bubbles[MAX_BUBBLES:]
                    for bubble in excess_bubbles:
                        self.space.remove(bubble.body, bubble.shape)
                    self.bubbles = self.bubbles[:MAX_BUBBLES]
                
                # Schedule updates for existing bubbles
                self.update_scheduler.schedule_updates(self.bubbles, crypto_data, UPDATE_INTERVAL)
            
            self.last_bubble_update = now
        
        # Process scheduled updates
        self.update_scheduler.process_updates()
        
        # Update all bubbles
        with self.lock:
            width, height = 1280, 720  # Will be updated from actual screen size
            bubble_area = pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                                    int(height * LAYOUT['bubble_height_ratio']))
            
            for bubble in self.bubbles:
                bubble.update(bubble_area)
    
    def handle_click(self, mouse_pos, modal_manager, screen_size):
        """Handle mouse clicks on bubbles"""
        width, height = screen_size
        bubble_area = pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                                int(height * LAYOUT['bubble_height_ratio']))
        
        if bubble_area.collidepoint(mouse_pos):
            with self.lock:
                for bubble in self.bubbles:
                    if bubble.check_click(mouse_pos):
                        modal_manager.open_crypto_modal(bubble.coin_data, screen_size)
                        print(f"Opened details for {bubble.symbol}")
                        return True
        return False
    
    def render(self, screen, layout_areas):
        """Render all bubbles"""
        bubble_area = layout_areas['bubble_area']
        
        # Draw bubble area background
        pygame.draw.rect(screen, COLORS['bubble_area'], bubble_area)
        pygame.draw.rect(screen, COLORS['border'], bubble_area, 2)
        
        # Draw all bubbles
        with self.lock:
            for bubble in self.bubbles:
                bubble.draw(screen)
        
        # Draw title
        title_font = pygame.font.SysFont("Arial", FONT_SIZES['title'], bold=True)
        with self.lock:
            bubble_count = len(self.bubbles)
        
        title_surface = title_font.render(f"Crypto Live Dashboard - {bubble_count} Coins", 
                                        True, COLORS['text_primary'])
        title_rect = title_surface.get_rect(center=(bubble_area.centerx, 25))
        
        # Title background
        title_bg = pygame.Surface((title_surface.get_width() + 30, title_surface.get_height() + 15))
        title_bg.set_alpha(200)
        title_bg.fill((20, 20, 30))
        screen.blit(title_bg, (title_rect.x - 15, title_rect.y - 7))
        screen.blit(title_surface, title_rect)
    
    def get_bubble_count(self):
        """Get current number of bubbles"""
        with self.lock:
            return len(self.bubbles)