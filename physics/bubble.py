"""
Enhanced Bubble Physics with Dynamic Scaling and Symbol Display (Fixed)
Complete physics/bubble.py file with symbol display like the table
"""

import pygame
import pymunk
import math
import time
import random
import os

from config.settings import *
from ui.effects import FloatingEffect
from utils.logo_loader import download_logo

class SpaceCalculator:
    """Calculates optimal bubble scaling based on available space"""
    
    @staticmethod
    def calculate_bubble_scaling(bubble_area_rect, total_bubbles, screen_size):
        """Calculate optimal bubble scale factor for efficient space usage"""
        area_width = bubble_area_rect.width
        area_height = bubble_area_rect.height
        total_area = area_width * area_height
        
        # Calculate base bubble area (assuming average radius of 20px)
        base_bubble_area = math.pi * 20 * 20
        total_bubble_area = total_bubbles * base_bubble_area
        
        # Add spacing factor (bubbles shouldn't completely fill the space)
        spacing_factor = 0.4  # 40% of space for movement/spacing
        usable_area = total_area * (1 - spacing_factor)
        
        # Calculate scale factor
        if total_bubble_area > 0:
            scale_factor = math.sqrt(usable_area / total_bubble_area)
            # Clamp between reasonable bounds
            scale_factor = max(0.3, min(2.5, scale_factor))
        else:
            scale_factor = 1.0
        
        # Adjust for screen density
        screen_density = (screen_size[0] * screen_size[1]) / (1920 * 1080)
        density_adjustment = math.sqrt(screen_density)
        
        final_scale = scale_factor * density_adjustment
        return max(0.5, min(3.0, final_scale))

class EnhancedFloatingBubble:
    """Enhanced bubble with dynamic scaling and symbol display"""
    
    def __init__(self, space, coin_data, bounds, screen_size, scale_factor=1.0):
        self.coin_data = coin_data
        self.symbol = coin_data['symbol'].upper()
        self.price_change = coin_data.get('price_change_percentage_24h', 0.0) or 0.0
        self.market_cap = coin_data.get('market_cap', 1e9) or 1e9
        self.last_price_change = self.price_change
        self.screen_size = screen_size
        self.scale_factor = scale_factor
        
        # Calculate dynamic bubble size based on market cap and scale factor
        market_cap_normalized = max(1e6, min(self.market_cap, 1e12))
        size_factor = math.sqrt(market_cap_normalized / 1e9)
        
        # Dynamic sizing with scale factor
        base_min_radius = 10 * scale_factor
        base_max_radius = 30 * scale_factor
        self.radius = base_min_radius + (base_max_radius - base_min_radius) * min(1.0, size_factor / 5.0)
        self.area = math.pi * self.radius * self.radius
        
        # Size thresholds (scaled)
        self.small_threshold = 15 * scale_factor
        self.medium_threshold = 22 * scale_factor
        
        # Set bounds with safety margin
        self.update_bounds(bounds)
        
        # Physics setup
        mass = self.radius / 30
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        
        # Safe initial position
        x = random.uniform(self.bounds.left + self.radius, self.bounds.right - self.radius)
        y = random.uniform(self.bounds.top + self.radius, self.bounds.bottom - self.radius)
        self.body.position = (x, y)
        
        # Physics properties
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.2
        self.shape.friction = 0.1
        space.add(self.body, self.shape)
        
        # Floating animation parameters
        self.float_time = 0
        self.float_speed_primary = random.uniform(0.3, 0.7)
        self.float_speed_secondary = random.uniform(0.5, 0.9)
        self.float_speed_tertiary = random.uniform(0.1, 0.3)
        
        self.amplitude_x_primary = random.uniform(0.4, 0.8)
        self.amplitude_y_primary = random.uniform(0.5, 1.0)
        self.amplitude_x_secondary = random.uniform(0.2, 0.4)
        self.amplitude_y_secondary = random.uniform(0.2, 0.5)
        self.amplitude_tertiary = random.uniform(0.1, 0.2)
        
        self.phase_x_primary = random.uniform(0, 2 * math.pi)
        self.phase_y_primary = random.uniform(0, 2 * math.pi)
        self.phase_x_secondary = random.uniform(0, 2 * math.pi)
        self.phase_y_secondary = random.uniform(0, 2 * math.pi)
        self.phase_tertiary = random.uniform(0, 2 * math.pi)
        
        # Movement properties
        self.velocity_smoothing = 0.95
        self.max_velocity = 8.0
        self.boundary_softness = 0.02
        
        # Drift simulation
        self.drift_direction = random.uniform(0, 2 * math.pi)
        self.drift_speed = random.uniform(0.1, 0.3)
        self.drift_change_time = random.uniform(5.0, 15.0)
        self.last_drift_change = time.time()
        
        self.surface_tension = random.uniform(0.8, 1.2)
        self.air_resistance = 0.02
        
        # Effects
        self.effects = []
        
        # Calculate scaling factors
        self.calculate_scaling_factors()
        
        # Load logo
        self.logo_surface = None
        logo_path = download_logo(self.symbol.lower(), coin_data.get('image', ''))
        if logo_path and os.path.exists(logo_path):
            try:
                logo_img = pygame.image.load(logo_path).convert_alpha()
                logo_size = int(self.logo_size)
                self.logo_surface = pygame.transform.smoothscale(logo_img, (logo_size, logo_size))
            except Exception as e:
                print(f"Error loading logo for {self.symbol}: {e}")
    
    def update_bounds(self, new_bounds):
        """Update boundary constraints"""
        safety_margin = self.radius + 15
        
        actual_width = max(150, new_bounds.width - 2 * safety_margin)
        actual_height = max(150, new_bounds.height - 2 * safety_margin)
        
        self.bounds = pygame.Rect(
            new_bounds.left + safety_margin,
            new_bounds.top + safety_margin,
            actual_width,
            actual_height
        )
        
        if hasattr(self, 'body'):
            self.ensure_within_bounds()
    
    def ensure_within_bounds(self):
        """Ensure bubble stays within bounds"""
        x, y = self.body.position
        
        corrected_x = max(self.bounds.left, min(self.bounds.right, x))
        corrected_y = max(self.bounds.top, min(self.bounds.bottom, y))
        
        if corrected_x != x or corrected_y != y:
            self.body.position = (corrected_x, corrected_y)
            vx, vy = self.body.velocity
            self.body.velocity = (vx * 0.8, vy * 0.8)
    
    def calculate_scaling_factors(self):
        """Calculate size-adaptive scaling factors"""
        # Logo scaling based on bubble size
        self.logo_size = max(6, min(self.radius * 0.8, 28))
        
        # Font scaling for different bubble sizes
        if self.radius < self.small_threshold:
            # Small bubble
            self.name_font_size = max(5, int(self.radius * 0.25))
            self.pct_font_size = max(4, int(self.radius * 0.2))
        elif self.radius < self.medium_threshold:
            # Medium bubble
            self.name_font_size = max(6, int(self.radius * 0.3))
            self.pct_font_size = max(5, int(self.radius * 0.25))
        else:
            # Large bubble
            self.name_font_size = max(8, int(self.radius * 0.35))
            self.pct_font_size = max(6, int(self.radius * 0.3))
        
        # Content positioning
        self.content_spacing = max(2, int(self.radius * 0.1))

    def get_display_name(self):
        """Get symbol for display - FIXED to use symbols like table"""
        # Always use symbol like the table, adapted to bubble size
        if self.radius < self.small_threshold:
            # Small bubbles: 3-4 character symbols
            if len(self.symbol) <= 4:
                return self.symbol
            else:
                return self.symbol[:3]  # Max 3 chars for small bubbles
        elif self.radius < self.medium_threshold:
            # Medium bubbles: full symbol
            return self.symbol
        else:
            # Large bubbles: full symbol (never long names)
            return self.symbol

    def apply_enhanced_floating_forces(self):
        """Apply floating forces for smooth movement"""
        x, y = self.body.position
        vx, vy = self.body.velocity
        
        self.float_time += 1/60.0
        
        # Velocity limiting
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            vx *= scale
            vy *= scale
            self.body.velocity = (vx, vy)
        
        # Multi-layer wave motion
        primary_x = math.sin(self.float_time * self.float_speed_primary + self.phase_x_primary) * self.amplitude_x_primary
        primary_y = math.cos(self.float_time * self.float_speed_primary + self.phase_y_primary) * self.amplitude_y_primary
        
        secondary_x = math.sin(self.float_time * self.float_speed_secondary + self.phase_x_secondary) * self.amplitude_x_secondary
        secondary_y = math.cos(self.float_time * self.float_speed_secondary + self.phase_y_secondary) * self.amplitude_y_secondary
        
        tertiary_x = math.sin(self.float_time * self.float_speed_tertiary * 3.7 + self.phase_tertiary) * self.amplitude_tertiary
        tertiary_y = math.cos(self.float_time * self.float_speed_tertiary * 2.3 + self.phase_tertiary * 1.7) * self.amplitude_tertiary
        
        wave_force_x = (primary_x + secondary_x + tertiary_x) * 0.08
        wave_force_y = (primary_y + secondary_y + tertiary_y) * 0.08
        
        # Natural drift
        current_time = time.time()
        if current_time - self.last_drift_change > self.drift_change_time:
            self.drift_direction += random.uniform(-0.5, 0.5)
            self.drift_speed = random.uniform(0.1, 0.3)
            self.drift_change_time = random.uniform(5.0, 15.0)
            self.last_drift_change = current_time
        
        drift_force_x = math.cos(self.drift_direction) * self.drift_speed * 0.05
        drift_force_y = math.sin(self.drift_direction) * self.drift_speed * 0.05
        
        # Surface tension and air resistance
        tension_force_x = -vx * self.surface_tension * 0.01
        tension_force_y = -vy * self.surface_tension * 0.01
        air_resistance_x = -vx * self.air_resistance
        air_resistance_y = -vy * self.air_resistance
        
        # Boundary forces
        boundary_force_x = 0
        boundary_force_y = 0
        boundary_zone = self.radius * 4.0
        force_strength = 1.2
        
        if x < self.bounds.left + boundary_zone:
            distance_ratio = (x - self.bounds.left) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_x = push_factor * force_strength
        elif x > self.bounds.right - boundary_zone:
            distance_ratio = (self.bounds.right - x) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_x = -push_factor * force_strength
            
        if y < self.bounds.top + boundary_zone:
            distance_ratio = (y - self.bounds.top) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_y = push_factor * force_strength
        elif y > self.bounds.bottom - boundary_zone:
            distance_ratio = (self.bounds.bottom - y) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_y = -push_factor * force_strength
        
        # Apply velocity smoothing
        self.body.velocity = (vx * self.velocity_smoothing, vy * self.velocity_smoothing)
        
        # Combine forces
        total_force_x = (wave_force_x + drift_force_x + tension_force_x + 
                        air_resistance_x + boundary_force_x)
        total_force_y = (wave_force_y + drift_force_y + tension_force_y + 
                        air_resistance_y + boundary_force_y)
        
        self.body.apply_force_at_local_point((total_force_x, total_force_y), (0, 0))
        
        # Boundary correction
        corrected = False
        new_x, new_y = x, y
        new_vx, new_vy = vx, vy
        
        if x < self.bounds.left:
            new_x = self.bounds.left
            new_vx = abs(vx) * 0.3
            corrected = True
        elif x > self.bounds.right:
            new_x = self.bounds.right
            new_vx = -abs(vx) * 0.3
            corrected = True
            
        if y < self.bounds.top:
            new_y = self.bounds.top
            new_vy = abs(vy) * 0.3
            corrected = True
        elif y > self.bounds.bottom:
            new_y = self.bounds.bottom
            new_vy = -abs(vy) * 0.3
            corrected = True
        
        if corrected:
            self.body.position = (new_x, new_y)
            self.body.velocity = (new_vx, new_vy)

    def update_data(self, new_coin_data):
        """Update bubble with new market data"""
        new_price_change = new_coin_data.get('price_change_percentage_24h', 0.0) or 0.0
        
        diff = new_price_change - self.price_change
        if abs(diff) > 0.01:
            sign = "+" if diff > 0 else ""
            effect_text = f"{sign}{diff:.2f}%"
            self.effects.append(FloatingEffect(effect_text, self.body.position, diff > 0))
        
        self.last_price_change = self.price_change
        self.price_change = new_price_change
        self.market_cap = new_coin_data.get('market_cap', self.market_cap) or self.market_cap

    def update(self, bounds):
        """Update bubble physics and effects"""
        if bounds != self.bounds:
            self.update_bounds(bounds)
        
        self.apply_enhanced_floating_forces()
        
        self.effects = [effect for effect in self.effects if effect.is_alive()]
        for effect in self.effects:
            effect.update()

    def check_click(self, mouse_pos):
        """Check if bubble was clicked"""
        x, y = self.body.position
        distance = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)
        return distance <= self.radius

    def get_coin_id(self):
        """Get coin ID for API calls"""
        return SYMBOL_TO_ID.get(self.symbol, self.symbol.lower())

    def draw(self, surface):
        """Draw bubble with symbol display like table - FIXED"""
        x, y = int(self.body.position.x), int(self.body.position.y)
        
        # Determine colors
        is_negative = self.price_change < 0
        edge_color = COLORS['negative'] if is_negative else COLORS['positive']
        
        # Enhanced gradient bubble effect (ring only, no background)
        circle_surf = pygame.Surface((int(self.radius * 2.2), int(self.radius * 2.2)), pygame.SRCALPHA)
        center_pos = (int(self.radius * 1.1), int(self.radius * 1.1))
        
        ring_thickness = max(2, int(self.radius * 0.15))
        
        for i in range(ring_thickness):
            ring_radius = int(self.radius - i)
            if ring_radius <= 0:
                break
                
            alpha = int(120 * (1 - i / ring_thickness))
            
            hue_shift = int(15 * math.sin(self.float_time * 0.5 + i * 0.2))
            shifted_color = (
                min(255, max(0, edge_color[0] + hue_shift)),
                min(255, max(0, edge_color[1] + hue_shift // 2)),
                min(255, max(0, edge_color[2] - hue_shift // 3))
            )
            
            color_with_alpha = (*shifted_color, alpha)
            pygame.draw.circle(circle_surf, color_with_alpha, center_pos, ring_radius, max(1, ring_thickness - i))
        
        surface.blit(circle_surf, (x - int(self.radius * 1.1), y - int(self.radius * 1.1)))
        
        # CLEAN CONTENT: LOGO + SYMBOL + % CHANGE
        content_y = y - int(self.radius * 0.4)
        
        # Logo (top)
        if self.logo_surface:
            logo_rect = self.logo_surface.get_rect(center=(x, content_y))
            surface.blit(self.logo_surface, logo_rect)
            next_y = logo_rect.bottom + self.content_spacing
        else:
            # Text fallback (no gray circle)
            fallback_font = pygame.font.SysFont("Arial", max(6, int(self.radius * 0.4)), bold=True)
            fallback_text = self.symbol[:3]
            fallback_surface = fallback_font.render(fallback_text, True, (255, 255, 255))
            fallback_rect = fallback_surface.get_rect(center=(x, content_y))
            surface.blit(fallback_surface, fallback_rect)
            next_y = fallback_rect.bottom + self.content_spacing
        
        # Symbol (middle) - FIXED to use symbols like table
        display_symbol = self.get_display_name()  # Now returns symbol only
        symbol_font = pygame.font.SysFont("Arial", self.name_font_size, bold=True)
        symbol_surface = symbol_font.render(display_symbol, True, COLORS['text_primary'])
        symbol_rect = symbol_surface.get_rect(center=(x, next_y))
        
        # Ensure symbol fits within bubble
        max_width = int(self.radius * 1.8)
        if symbol_surface.get_width() > max_width:
            # If still doesn't fit, shorten more
            shortened_symbol = display_symbol[:3] if len(display_symbol) > 3 else display_symbol
            symbol_surface = symbol_font.render(shortened_symbol, True, COLORS['text_primary'])
        
        surface.blit(symbol_surface, symbol_rect)
        next_y = symbol_rect.bottom + self.content_spacing
        
        # Percentage change (bottom)
        pct_color = COLORS['positive'] if not is_negative else COLORS['negative']
        pct_text = f"{self.price_change:+.1f}%"
        
        pct_font = pygame.font.SysFont("Arial", self.pct_font_size, bold=True)
        pct_surface = pct_font.render(pct_text, True, pct_color)
        
        # Ensure percentage fits
        if pct_surface.get_width() > max_width:
            pct_text = f"{int(self.price_change):+d}%"
            pct_surface = pct_font.render(pct_text, True, pct_color)
        
        # Final position check
        max_y = y + int(self.radius * 0.8)
        if next_y + pct_surface.get_height() // 2 > max_y:
            next_y = max_y - pct_surface.get_height() // 2
        
        pct_rect = pct_surface.get_rect(center=(x, next_y))
        surface.blit(pct_surface, pct_rect)
        
        # Draw floating effects
        for effect in self.effects:
            effect.draw(surface)

# Backward compatibility
FloatingBubble = EnhancedFloatingBubble