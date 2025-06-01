"""
Enhanced Bubble Physics with Smooth Soap Bubble Movement
Realistic floating animation with soft, organic motion patterns
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

class EnhancedFloatingBubble:
    """Enhanced bubble with realistic soap bubble physics"""
    
    def __init__(self, space, coin_data, bounds, screen_size):
        self.coin_data = coin_data
        self.symbol = coin_data['symbol'].upper()
        self.price_change = coin_data.get('price_change_percentage_24h', 0.0) or 0.0
        self.market_cap = coin_data.get('market_cap', 1e9) or 1e9
        self.last_price_change = self.price_change
        self.screen_size = screen_size
        
        # Calculate bubble size based on market cap
        market_cap_normalized = max(1e6, min(self.market_cap, 1e12))
        size_factor = math.sqrt(market_cap_normalized / 1e9)
        
        min_radius = 20
        max_radius = 50
        self.radius = min_radius + (max_radius - min_radius) * min(1.0, size_factor / 5.0)
        self.area = math.pi * self.radius * self.radius
        
        # Set bounds with safety margin
        self.update_bounds(bounds)
        
        # Enhanced physics body for smooth movement
        mass = self.radius / 30  # Lighter for more floating effect
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        
        # Safe initial position within bounds
        x = random.uniform(self.bounds.left + self.radius, self.bounds.right - self.radius)
        y = random.uniform(self.bounds.top + self.radius, self.bounds.bottom - self.radius)
        self.body.position = (x, y)
        
        # Enhanced physics properties for soap bubble effect
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.2  # Soft bouncing
        self.shape.friction = 0.1    # Low friction for floating
        space.add(self.body, self.shape)
        
        # Enhanced floating parameters for organic movement
        self.float_time = 0
        self.float_speed_primary = random.uniform(0.3, 0.7)     # Primary wave
        self.float_speed_secondary = random.uniform(0.5, 0.9)   # Secondary wave
        self.float_speed_tertiary = random.uniform(0.1, 0.3)    # Micro movements
        
        # Multiple wave amplitudes for complex motion
        self.amplitude_x_primary = random.uniform(0.4, 0.8)
        self.amplitude_y_primary = random.uniform(0.5, 1.0)
        self.amplitude_x_secondary = random.uniform(0.2, 0.4)
        self.amplitude_y_secondary = random.uniform(0.2, 0.5)
        self.amplitude_tertiary = random.uniform(0.1, 0.2)
        
        # Phase offsets for each wave
        self.phase_x_primary = random.uniform(0, 2 * math.pi)
        self.phase_y_primary = random.uniform(0, 2 * math.pi)
        self.phase_x_secondary = random.uniform(0, 2 * math.pi)
        self.phase_y_secondary = random.uniform(0, 2 * math.pi)
        self.phase_tertiary = random.uniform(0, 2 * math.pi)
        
        # Enhanced movement properties for smooth floating
        self.velocity_smoothing = 0.95    # Smooth velocity changes
        self.max_velocity = 8.0           # Gentle maximum speed
        self.boundary_softness = 0.02     # Soft boundary forces
        
        # Natural drift simulation
        self.drift_direction = random.uniform(0, 2 * math.pi)
        self.drift_speed = random.uniform(0.1, 0.3)
        self.drift_change_time = random.uniform(5.0, 15.0)
        self.last_drift_change = time.time()
        
        # Bubble surface tension simulation
        self.surface_tension = random.uniform(0.8, 1.2)
        self.air_resistance = 0.02
        
        # Visual effects
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
        """Update boundary constraints with enhanced safety margins"""
        safety_margin = self.radius + 20
        
        # Ensure minimum bounds size
        min_width = 200
        min_height = 200
        
        actual_width = max(min_width, new_bounds.width - 2 * safety_margin)
        actual_height = max(min_height, new_bounds.height - 2 * safety_margin)
        
        self.bounds = pygame.Rect(
            new_bounds.left + safety_margin,
            new_bounds.top + safety_margin,
            actual_width,
            actual_height
        )
        
        # If bubble is outside new bounds, reposition it gently
        if hasattr(self, 'body'):
            self.ensure_within_bounds()
    
    def ensure_within_bounds(self):
        """Ensure bubble is within bounds with smooth correction"""
        x, y = self.body.position
        
        # Gentle position correction
        corrected_x = max(self.bounds.left, min(self.bounds.right, x))
        corrected_y = max(self.bounds.top, min(self.bounds.bottom, y))
        
        if corrected_x != x or corrected_y != y:
            self.body.position = (corrected_x, corrected_y)
            # Gentle velocity dampening instead of harsh reset
            vx, vy = self.body.velocity
            self.body.velocity = (vx * 0.8, vy * 0.8)
    
    def calculate_scaling_factors(self):
        """Calculate all scaling factors for UI elements"""
        area_factor = self.area / (math.pi * 35 * 35)
        
        # Logo scaling
        self.logo_size = max(10, min(30, 12 + int(10 * math.sqrt(area_factor))))
        
        # Font scaling
        self.symbol_font_size = max(7, min(16, 8 + int(5 * math.sqrt(area_factor))))
        self.pct_font_size = max(6, min(13, 7 + int(4 * math.sqrt(area_factor))))
        
        # Spacing
        self.logo_y_offset = -self.radius * 0.4
        self.symbol_spacing = 6 + int(2 * math.sqrt(area_factor))
        self.pct_spacing = 5 + int(2 * math.sqrt(area_factor))
        
        # Text boundary limits
        self.text_boundary_factor = 0.8

    def apply_enhanced_floating_forces(self):
        """Apply enhanced floating forces for realistic soap bubble movement"""
        x, y = self.body.position
        vx, vy = self.body.velocity
        
        # Update float time for wave calculations
        self.float_time += 1/60.0  # Assuming 60 FPS
        
        # Apply velocity smoothing first
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            vx *= scale
            vy *= scale
            self.body.velocity = (vx, vy)
        
        # Multi-layered wave motion for organic floating
        # Primary wave (main floating motion)
        primary_x = math.sin(self.float_time * self.float_speed_primary + self.phase_x_primary) * self.amplitude_x_primary
        primary_y = math.cos(self.float_time * self.float_speed_primary + self.phase_y_primary) * self.amplitude_y_primary
        
        # Secondary wave (adds complexity)
        secondary_x = math.sin(self.float_time * self.float_speed_secondary + self.phase_x_secondary) * self.amplitude_x_secondary
        secondary_y = math.cos(self.float_time * self.float_speed_secondary + self.phase_y_secondary) * self.amplitude_y_secondary
        
        # Tertiary wave (micro movements for realism)
        tertiary_x = math.sin(self.float_time * self.float_speed_tertiary * 3.7 + self.phase_tertiary) * self.amplitude_tertiary
        tertiary_y = math.cos(self.float_time * self.float_speed_tertiary * 2.3 + self.phase_tertiary * 1.7) * self.amplitude_tertiary
        
        # Combine all waves with scaling
        wave_force_x = (primary_x + secondary_x + tertiary_x) * 0.08
        wave_force_y = (primary_y + secondary_y + tertiary_y) * 0.08
        
        # Natural drift simulation (changes direction periodically)
        current_time = time.time()
        if current_time - self.last_drift_change > self.drift_change_time:
            self.drift_direction += random.uniform(-0.5, 0.5)
            self.drift_speed = random.uniform(0.1, 0.3)
            self.drift_change_time = random.uniform(5.0, 15.0)
            self.last_drift_change = current_time
        
        drift_force_x = math.cos(self.drift_direction) * self.drift_speed * 0.05
        drift_force_y = math.sin(self.drift_direction) * self.drift_speed * 0.05
        
        # Surface tension effect (bubbles naturally try to minimize surface area)
        tension_force_x = -vx * self.surface_tension * 0.01
        tension_force_y = -vy * self.surface_tension * 0.01
        
        # Air resistance (very subtle)
        air_resistance_x = -vx * self.air_resistance
        air_resistance_y = -vy * self.air_resistance
        
        # Enhanced soft boundary forces with smooth transitions
        boundary_force_x = 0
        boundary_force_y = 0
        boundary_zone = self.radius * 4.0  # Larger zone for smoother transitions
        force_strength = 1.2
        
        # Horizontal boundaries with smooth curves
        if x < self.bounds.left + boundary_zone:
            distance_ratio = (x - self.bounds.left) / boundary_zone
            # Smooth curve: stronger force closer to boundary
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_x = push_factor * force_strength
        elif x > self.bounds.right - boundary_zone:
            distance_ratio = (self.bounds.right - x) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_x = -push_factor * force_strength
            
        # Vertical boundaries with smooth curves
        if y < self.bounds.top + boundary_zone:
            distance_ratio = (y - self.bounds.top) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_y = push_factor * force_strength
        elif y > self.bounds.bottom - boundary_zone:
            distance_ratio = (self.bounds.bottom - y) / boundary_zone
            push_factor = 1.0 - (distance_ratio * distance_ratio)
            boundary_force_y = -push_factor * force_strength
        
        # Apply enhanced velocity smoothing
        self.body.velocity = (vx * self.velocity_smoothing, vy * self.velocity_smoothing)
        
        # Combine all forces for natural floating motion
        total_force_x = (wave_force_x + drift_force_x + tension_force_x + 
                        air_resistance_x + boundary_force_x)
        total_force_y = (wave_force_y + drift_force_y + tension_force_y + 
                        air_resistance_y + boundary_force_y)
        
        # Apply combined forces
        self.body.apply_force_at_local_point((total_force_x, total_force_y), (0, 0))
        
        # Ultra-smooth boundary correction
        corrected = False
        new_x, new_y = x, y
        new_vx, new_vy = vx, vy
        
        # Gentle boundary bounce with surface tension
        if x < self.bounds.left:
            new_x = self.bounds.left
            new_vx = abs(vx) * 0.3  # Gentle bounce back
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
        
        # Create floating effect for changes
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
        # Update bounds if they changed
        if bounds != self.bounds:
            self.update_bounds(bounds)
        
        # Apply enhanced floating forces
        self.apply_enhanced_floating_forces()
        
        # Update effects
        self.effects = [effect for effect in self.effects if effect.is_alive()]
        for effect in self.effects:
            effect.update()

    def check_click(self, mouse_pos):
        """Check if the bubble was clicked"""
        x, y = self.body.position
        distance = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)
        return distance <= self.radius

    def get_coin_id(self):
        """Get the coin ID for API calls"""
        return SYMBOL_TO_ID.get(self.symbol, self.symbol.lower())

    def draw(self, surface):
        """Draw bubble with enhanced visual effects"""
        x, y = int(self.body.position.x), int(self.body.position.y)
        
        # Determine colors
        is_negative = self.price_change < 0
        edge_color = COLORS['negative'] if is_negative else COLORS['positive']
        
        # Enhanced gradient surface with soap bubble effect
        circle_surf = pygame.Surface((int(self.radius * 2.2), int(self.radius * 2.2)), pygame.SRCALPHA)
        center_pos = (int(self.radius * 1.1), int(self.radius * 1.1))
        
        # Create multi-layer radial gradient for soap bubble effect
        for i, layer_radius in enumerate(range(int(self.radius), int(self.radius * 0.3), -2)):
            if layer_radius <= 0:
                break
                
            # Calculate alpha for gradient
            alpha_factor = (layer_radius - self.radius * 0.3) / (self.radius * 0.7)
            alpha = int(180 * alpha_factor * alpha_factor)  # Quadratic falloff
            
            # Add slight iridescent effect
            hue_shift = int(20 * math.sin(self.float_time * 0.5 + i * 0.3))
            shifted_color = (
                min(255, max(0, edge_color[0] + hue_shift)),
                min(255, max(0, edge_color[1] + hue_shift // 2)),
                min(255, max(0, edge_color[2] - hue_shift // 3))
            )
            
            color_with_alpha = (*shifted_color, alpha)
            pygame.draw.circle(circle_surf, color_with_alpha, center_pos, layer_radius)
        
        # Add subtle highlight for soap bubble effect
        highlight_radius = int(self.radius * 0.7)
        highlight_offset_x = int(self.radius * 0.2)
        highlight_offset_y = int(self.radius * 0.2)
        highlight_pos = (center_pos[0] - highlight_offset_x, center_pos[1] - highlight_offset_y)
        
        for i in range(highlight_radius, highlight_radius // 3, -1):
            alpha = int(80 * (1 - (highlight_radius - i) / (highlight_radius * 0.7)))
            highlight_color = (255, 255, 255, alpha)
            pygame.draw.circle(circle_surf, highlight_color, highlight_pos, i)
        
        # Blit the enhanced gradient circle
        surface.blit(circle_surf, (x - int(self.radius * 1.1), y - int(self.radius * 1.1)))
        
        # Content layout (same as original but with enhanced positioning)
        content_y_start = y + int(self.logo_y_offset)
        
        # Draw logo
        if self.logo_surface:
            logo_rect = self.logo_surface.get_rect(center=(x, content_y_start))
            surface.blit(self.logo_surface, logo_rect)
            next_y = logo_rect.bottom + self.symbol_spacing
        else:
            next_y = content_y_start + self.symbol_spacing
        
        # Symbol text
        symbol_font = pygame.font.SysFont("Arial", self.symbol_font_size, bold=True)
        text_color = COLORS['text_primary']
        
        # Smart symbol truncation
        display_symbol = self.symbol
        symbol_width = symbol_font.size(self.symbol)[0]
        max_text_width = int(self.radius * 2 * self.text_boundary_factor)
        
        if symbol_width > max_text_width:
            for length in range(len(self.symbol) - 1, 2, -1):
                test_symbol = self.symbol[:length]
                if symbol_font.size(test_symbol)[0] <= max_text_width:
                    display_symbol = test_symbol
                    break
        
        symbol_text = symbol_font.render(display_symbol, True, text_color)
        symbol_rect = symbol_text.get_rect(center=(x, next_y))
        
        # Ensure symbol stays within bounds
        max_symbol_y = y + int(self.radius * self.text_boundary_factor)
        if symbol_rect.bottom > max_symbol_y:
            symbol_rect.centery = max_symbol_y - symbol_text.get_height() // 2
        
        surface.blit(symbol_text, symbol_rect)
        
        # Percentage text
        pct_font = pygame.font.SysFont("Arial", self.pct_font_size, bold=True)
        pct_color = COLORS['positive'] if not is_negative else COLORS['negative']
        
        # Format percentage
        if self.area < 2000:
            pct_str = f"{self.price_change:+.1f}%"
        else:
            pct_str = f"{self.price_change:+.2f}%"
        
        # Check if percentage text fits
        pct_text = pct_font.render(pct_str, True, pct_color)
        pct_width = pct_text.get_width()
        
        if pct_width > max_text_width:
            pct_str = f"{int(self.price_change):+d}%"
            pct_text = pct_font.render(pct_str, True, pct_color)
        
        # Position percentage
        pct_y = symbol_rect.bottom + self.pct_spacing
        
        # Final boundary check
        max_pct_y = y + int(self.radius * self.text_boundary_factor)
        if pct_y + pct_text.get_height() // 2 > max_pct_y:
            pct_y = max_pct_y - pct_text.get_height() // 2
        
        pct_rect = pct_text.get_rect(center=(x, pct_y))
        surface.blit(pct_text, pct_rect)
        
        # Draw floating effects
        for effect in self.effects:
            effect.draw(surface)

# Backward compatibility alias
FloatingBubble = EnhancedFloatingBubble