"""
Bubble Manager with Dynamic Scaling and Space-Efficient Layout
Enhanced to use available space efficiently with adaptive bubble sizing
"""

import pygame
import time
import math
import pymunk
from threading import Lock

from config.settings import *
from physics.bubble import EnhancedFloatingBubble, SpaceCalculator
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
        
        symbol_to_data = {coin['symbol'].upper(): coin for coin in new_data}
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
        
        for update in completed_updates:
            self.update_queue.remove(update)

class EnhancedBubbleManager:
    """Manages floating bubbles with dynamic space-efficient scaling"""
    
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
        self.current_scale_factor = 1.0
        
    def get_bubble_area(self, screen_size):
        """Calculate the bubble area based on current screen size"""
        width, height = screen_size
        return pygame.Rect(0, 0, int(width * LAYOUT['bubble_width_ratio']), 
                          int(height * LAYOUT['bubble_height_ratio']))
    
    def calculate_optimal_scaling(self, bubble_area, total_bubbles, screen_size):
        """Calculate optimal bubble scaling for space efficiency"""
        return SpaceCalculator.calculate_bubble_scaling(bubble_area, total_bubbles, screen_size)
    
    def redistribute_bubbles(self, new_bubble_area, new_scale_factor):
        """Redistribute bubbles with dynamic scaling"""
        if not self.bubbles or not new_bubble_area:
            return
        
        print(f"🔄 Redistributing {len(self.bubbles)} bubbles with scale factor {new_scale_factor:.2f}")
        
        with self.lock:
            import random
            
            for bubble in self.bubbles:
                # Update bubble scaling
                old_radius = bubble.radius
                bubble.scale_factor = new_scale_factor
                bubble.calculate_scaling_factors()
                
                # Recalculate radius with new scale factor
                market_cap_normalized = max(1e6, min(bubble.market_cap, 1e12))
                size_factor = math.sqrt(market_cap_normalized / 1e9)
                base_min_radius = 10 * new_scale_factor
                base_max_radius = 30 * new_scale_factor
                new_radius = base_min_radius + (base_max_radius - base_min_radius) * min(1.0, size_factor / 5.0)
                
                # Update physics body if radius changed significantly
                if abs(new_radius - old_radius) > 2:
                    # Remove old shape
                    self.space.remove(bubble.body, bubble.shape)
                    
                    # Update radius and create new shape
                    bubble.radius = new_radius
                    bubble.shape = pymunk.Circle(bubble.body, bubble.radius)
                    bubble.shape.elasticity = 0.2
                    bubble.shape.friction = 0.1
                    
                    # Re-add to space
                    self.space.add(bubble.body, bubble.shape)
                
                # Calculate safe position within new bounds
                safety_margin = bubble.radius + 20
                safe_area = pygame.Rect(
                    new_bubble_area.left + safety_margin,
                    new_bubble_area.top + safety_margin,
                    max(100, new_bubble_area.width - 2 * safety_margin),
                    max(100, new_bubble_area.height - 2 * safety_margin)
                )
                
                current_x, current_y = bubble.body.position
                
                # Check if bubble needs repositioning
                if (current_x < safe_area.left or current_x > safe_area.right or
                    current_y < safe_area.top or current_y > safe_area.bottom):
                    
                    new_x = random.uniform(safe_area.left, safe_area.right)
                    new_y = random.uniform(safe_area.top, safe_area.bottom)
                    
                    bubble.body.position = (new_x, new_y)
                    bubble.body.velocity = (0, 0)
                
                # Update bubble's boundary constraints
                bubble.bounds = pygame.Rect(
                    safe_area.left,
                    safe_area.top,
                    safe_area.width,
                    safe_area.height
                )
    
    def initialize_bubbles_if_needed(self, crypto_data, screen_size):
        """Create initial bubbles with dynamic scaling"""
        if not self.bubbles_created and crypto_data:
            bubble_area = self.get_bubble_area(screen_size)
            
            # Calculate optimal scale factor
            self.current_scale_factor = self.calculate_optimal_scaling(
                bubble_area, min(MAX_BUBBLES, len(crypto_data)), screen_size
            )
            
            self.create_initial_bubbles(crypto_data, bubble_area, screen_size)
            self.bubbles_created = True
            self.current_bubble_area = bubble_area
            self.last_screen_size = screen_size
            
            print(f"✨ Enhanced bubble manager initialized with {len(self.bubbles)} space-efficient bubbles!")
            print(f"📐 Scale factor: {self.current_scale_factor:.2f}, Area: {bubble_area.width}x{bubble_area.height}")
    
    def create_initial_bubbles(self, crypto_data, bubble_area, screen_size):
        """Create initial bubbles with optimal scaling"""
        with self.lock:
            print(f"🫧 Creating space-efficient bubbles for top {min(MAX_BUBBLES, len(crypto_data))} cryptocurrencies...")
            
            for coin in crypto_data[:MAX_BUBBLES]:
                try:
                    bubble = EnhancedFloatingBubble(
                        self.space, coin, bubble_area, screen_size, self.current_scale_factor
                    )
                    self.bubbles.append(bubble)
                except Exception as e:
                    print(f"❌ Error creating bubble for {coin.get('symbol', 'Unknown')}: {e}")
            
            print(f"✅ Created {len(self.bubbles)} space-efficient bubbles successfully")
            update_loading_state('bubbles_ready', True)
    
    def update_screen_size(self, screen_size):
        """Update bubbles when screen size changes with dynamic scaling"""
        if not self.bubbles:
            return
        
        width_diff = abs(screen_size[0] - self.last_screen_size[0])
        height_diff = abs(screen_size[1] - self.last_screen_size[1])
        
        # Update if change is significant
        if width_diff > 50 or height_diff > 50:
            print(f"🖥️ Screen size changed: {self.last_screen_size} → {screen_size}")
            
            new_bubble_area = self.get_bubble_area(screen_size)
            
            # Recalculate optimal scale factor
            new_scale_factor = self.calculate_optimal_scaling(
                new_bubble_area, len(self.bubbles), screen_size
            )
            
            print(f"📏 Scale factor adjusted: {self.current_scale_factor:.2f} → {new_scale_factor:.2f}")
            
            # Redistribute with new scaling
            self.redistribute_bubbles(new_bubble_area, new_scale_factor)
            
            self.current_bubble_area = new_bubble_area
            self.current_scale_factor = new_scale_factor
            self.last_screen_size = screen_size
            self.last_boundary_update = time.time()
    
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
                
                # Add new bubbles with current scaling
                current_bubble_area = self.current_bubble_area or self.get_bubble_area(self.last_screen_size)
                
                for coin in crypto_data[:MAX_BUBBLES]:
                    symbol = coin['symbol'].upper()
                    if symbol not in existing_symbols:
                        try:
                            new_bubble = EnhancedFloatingBubble(
                                self.space, coin, current_bubble_area, 
                                self.last_screen_size, self.current_scale_factor
                            )
                            self.bubbles.append(new_bubble)
                        except Exception as e:
                            print(f"❌ Error creating bubble for {symbol}: {e}")
                
                # Trim to exactly MAX_BUBBLES
                if len(self.bubbles) > MAX_BUBBLES:
                    excess_bubbles = self.bubbles[MAX_BUBBLES:]
                    for bubble in excess_bubbles:
                        self.space.remove(bubble.body, bubble.shape)
                    self.bubbles = self.bubbles[:MAX_BUBBLES]
                
                # Update scale factor if bubble count changed significantly
                if abs(len(self.bubbles) - MAX_BUBBLES) > 10:
                    new_scale_factor = self.calculate_optimal_scaling(
                        current_bubble_area, len(self.bubbles), self.last_screen_size
                    )
                    
                    if abs(new_scale_factor - self.current_scale_factor) > 0.2:
                        print(f"📊 Adjusting scale factor due to bubble count change: {new_scale_factor:.2f}")
                        self.redistribute_bubbles(current_bubble_area, new_scale_factor)
                        self.current_scale_factor = new_scale_factor
                
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
                        print(f"🚀 Opened modal for {bubble.symbol}")
                        return True
        return False
    
    def render(self, surface, layout_areas):
        """Render all space-efficient bubbles"""
        bubble_area = layout_areas['bubble_area']
        
        # Update current bubble area if changed
        if self.current_bubble_area != bubble_area:
            self.current_bubble_area = bubble_area
            
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
        pygame.draw.rect(surface, COLORS['bubble_area'], bubble_area)
        pygame.draw.rect(surface, COLORS['border'], bubble_area, 2)
        
        # Draw all space-efficient bubbles
        with self.lock:
            for bubble in self.bubbles:
                bubble.draw(surface)
        
        # Draw title with scale info
        title_font = pygame.font.SysFont("Arial", FONT_SIZES['title'], bold=True)
        with self.lock:
            bubble_count = len(self.bubbles)
        
        title_text = f"Space-Efficient Crypto Dashboard - {bubble_count} Bubbles (Scale: {self.current_scale_factor:.2f}x)"
        title_surface = title_font.render(title_text, True, COLORS['text_primary'])
        title_rect = title_surface.get_rect(center=(bubble_area.centerx, 25))
        
        # Title background
        title_bg = pygame.Surface((title_surface.get_width() + 30, title_surface.get_height() + 15))
        title_bg.set_alpha(200)
        title_bg.fill((20, 20, 30))
        surface.blit(title_bg, (title_rect.x - 15, title_rect.y - 7))
        surface.blit(title_surface, title_rect)
    
    def get_bubble_count(self):
        """Get current number of bubbles"""
        with self.lock:
            return len(self.bubbles)
    
    def force_redistribute(self, screen_size):
        """Force redistribution with optimal scaling"""
        new_bubble_area = self.get_bubble_area(screen_size)
        new_scale_factor = self.calculate_optimal_scaling(
            new_bubble_area, len(self.bubbles), screen_size
        )
        
        self.redistribute_bubbles(new_bubble_area, new_scale_factor)
        self.current_bubble_area = new_bubble_area
        self.current_scale_factor = new_scale_factor
        self.last_screen_size = screen_size
        
        print(f"🔄 Forced redistribution with scale factor: {new_scale_factor:.2f}")

# Backward compatibility
BubbleManager = EnhancedBubbleManager