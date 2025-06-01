"""
Bubble Manager for handling multiple cryptocurrency bubbles
FIXED: Updated imports to use EnhancedFloatingBubble
"""

import pygame
import time
from threading import Lock

from config.settings import *
from physics.bubble import EnhancedFloatingBubble  # FIXED IMPORT
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
        self.last_boundary_update = time.time()
        self.update_scheduler = BubbleUpdateScheduler()
        self.lock = Lock()
        self.current_bubble_area = None
        self.last_screen_size = (0, 0)
        
    def get_bubble_area(self, screen_size):
        """Calculate the bubble area based on current screen size"""
        width, height = screen_size
        return pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                          int(height * LAYOUT['bubble_height_ratio']))
    
    def redistribute_bubbles(self, new_bubble_area):
        """Redistribute bubbles when screen size changes significantly"""
        if not self.bubbles or not new_bubble_area:
            return
        
        print(f"🔄 Redistributing {len(self.bubbles)} enhanced bubbles to new area: {new_bubble_area.width}x{new_bubble_area.height}")
        
        with self.lock:
            import random
            
            for bubble in self.bubbles:
                # Calculate safe position within new bounds
                safety_margin = bubble.radius + 20
                safe_area = pygame.Rect(
                    new_bubble_area.left + safety_margin,
                    new_bubble_area.top + safety_margin,
                    max(100, new_bubble_area.width - 2 * safety_margin),
                    max(100, new_bubble_area.height - 2 * safety_margin)
                )
                
                # Get current position
                current_x, current_y = bubble.body.position
                
                # Check if bubble is outside new safe area
                if (current_x < safe_area.left or current_x > safe_area.right or
                    current_y < safe_area.top or current_y > safe_area.bottom):
                    
                    # Reposition bubble within safe area
                    new_x = random.uniform(safe_area.left, safe_area.right)
                    new_y = random.uniform(safe_area.top, safe_area.bottom)
                    
                    bubble.body.position = (new_x, new_y)
                    bubble.body.velocity = (0, 0)  # Reset velocity
                    
                    print(f"📍 Moved {bubble.symbol} from ({current_x:.0f},{current_y:.0f}) to ({new_x:.0f},{new_y:.0f})")
                
                # Update bubble's boundary constraints
                bubble.bounds = pygame.Rect(
                    safe_area.left,
                    safe_area.top,
                    safe_area.width,
                    safe_area.height
                )
    
    def initialize_bubbles_if_needed(self, crypto_data, screen_size):
        """Create initial enhanced bubbles if they haven't been created yet"""
        if not self.bubbles_created and crypto_data:
            bubble_area = self.get_bubble_area(screen_size)
            self.create_initial_bubbles(crypto_data, bubble_area, screen_size)
            self.bubbles_created = True
            self.current_bubble_area = bubble_area
            self.last_screen_size = screen_size
            print(f"✨ Enhanced bubble manager initialized with {len(self.bubbles)} smooth floating bubbles!")
    
    def create_initial_bubbles(self, crypto_data, bubble_area, screen_size):
        """Create initial enhanced bubbles for top cryptocurrencies"""
        with self.lock:
            print(f"🫧 Creating enhanced floating bubbles for top {min(MAX_BUBBLES, len(crypto_data))} cryptocurrencies...")
            print(f"📐 Bubble area: {bubble_area.width}x{bubble_area.height}")
            
            for coin in crypto_data[:MAX_BUBBLES]:
                try:
                    # FIXED: Use EnhancedFloatingBubble
                    bubble = EnhancedFloatingBubble(self.space, coin, bubble_area, screen_size)
                    self.bubbles.append(bubble)
                except Exception as e:
                    print(f"❌ Error creating enhanced bubble for {coin.get('symbol', 'Unknown')}: {e}")
            
            print(f"✅ Created {len(self.bubbles)} enhanced floating bubbles successfully")
            update_loading_state('bubbles_ready', True)
    
    def update_screen_size(self, screen_size):
        """Update all bubbles when screen size changes"""
        if not self.bubbles:
            return
        
        # Check if screen size changed significantly
        width_diff = abs(screen_size[0] - self.last_screen_size[0])
        height_diff = abs(screen_size[1] - self.last_screen_size[1])
        
        # Only update if change is significant (more than 50 pixels)
        if width_diff > 50 or height_diff > 50:
            print(f"🖥️ Screen size changed: {self.last_screen_size} → {screen_size}")
            
            new_bubble_area = self.get_bubble_area(screen_size)
            
            # Update bubble radius for screen size
            with self.lock:
                for bubble in self.bubbles:
                    if hasattr(bubble, 'update_radius_for_screen'):
                        bubble.update_radius_for_screen(screen_size)
            
            # Redistribute bubbles to new area
            self.redistribute_bubbles(new_bubble_area)
            
            self.current_bubble_area = new_bubble_area
            self.last_screen_size = screen_size
            self.last_boundary_update = time.time()
    
    def update(self, crypto_data):
        """Update bubbles with new data periodically"""
        if not self.bubbles or not crypto_data:
            return
            
        now = time.time()
        
        # Update bubble data periodically
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
                current_bubble_area = self.current_bubble_area or self.get_bubble_area(self.last_screen_size)
                
                for coin in crypto_data[:MAX_BUBBLES]:
                    symbol = coin['symbol'].upper()
                    if symbol not in existing_symbols:
                        try:
                            # FIXED: Use EnhancedFloatingBubble
                            new_bubble = EnhancedFloatingBubble(self.space, coin, current_bubble_area, self.last_screen_size)
                            self.bubbles.append(new_bubble)
                        except Exception as e:
                            print(f"❌ Error creating enhanced bubble for {symbol}: {e}")
                
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
        
        # Update all bubbles with current boundary constraints
        if self.current_bubble_area:
            with self.lock:
                for bubble in self.bubbles:
                    bubble.update(self.current_bubble_area)
    
    def handle_click(self, mouse_pos, modal_manager, screen_size):
        """Handle mouse clicks on bubbles"""
        bubble_area = self.get_bubble_area(screen_size)
        
        if bubble_area.collidepoint(mouse_pos):
            with self.lock:
                for bubble in self.bubbles:
                    if bubble.check_click(mouse_pos):
                        modal_manager.open_crypto_modal(bubble.coin_data, screen_size)
                        print(f"🚀 Opened enhanced modal for {bubble.symbol}")
                        return True
        return False
    
    def render(self, screen, layout_areas):
        """Render all enhanced floating bubbles"""
        bubble_area = layout_areas['bubble_area']
        
        # Update current bubble area if it changed
        if self.current_bubble_area != bubble_area:
            self.current_bubble_area = bubble_area
            # Force boundary update for all bubbles
            with self.lock:
                for bubble in self.bubbles:
                    safety_margin = bubble.radius + 10
                    bubble.bounds = pygame.Rect(
                        bubble_area.left + safety_margin,
                        bubble_area.top + safety_margin,
                        max(100, bubble_area.width - 2 * safety_margin),
                        max(100, bubble_area.height - 2 * safety_margin)
                    )
        
        # Draw bubble area background
        pygame.draw.rect(screen, COLORS['bubble_area'], bubble_area)
        pygame.draw.rect(screen, COLORS['border'], bubble_area, 2)
        
        # Draw all enhanced floating bubbles
        with self.lock:
            for bubble in self.bubbles:
                bubble.draw(screen)
        
        # Draw title
        title_font = pygame.font.SysFont("Arial", FONT_SIZES['title'], bold=True)
        with self.lock:
            bubble_count = len(self.bubbles)
        
        title_surface = title_font.render(f"Enhanced Crypto Live Dashboard - {bubble_count} Floating Bubbles", 
                                        True, COLORS['text_primary'])
        title_rect = title_surface.get_rect(center=(bubble_area.centerx, 25))
        
        # Title background
        title_bg = pygame.Surface((title_surface.get_width() + 30, title_surface.get_height() + 15))
        title_bg.set_alpha(200)
        title_bg.fill((20, 20, 30))
        screen.blit(title_bg, (title_rect.x - 15, title_rect.y - 7))
        screen.blit(title_surface, title_rect)
    
    def get_bubble_count(self):
        """Get current number of enhanced bubbles"""
        with self.lock:
            return len(self.bubbles)
    
    def force_redistribute(self, screen_size):
        """Force redistribution of bubbles (useful for testing)"""
        new_bubble_area = self.get_bubble_area(screen_size)
        self.redistribute_bubbles(new_bubble_area)
        self.current_bubble_area = new_bubble_area
        self.last_screen_size = screen_size
        print(f"🔄 Forced redistribution of enhanced bubbles to area: {new_bubble_area.width}x{new_bubble_area.height}")