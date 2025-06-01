"""
FloatingBubble com design original e animação melhorada
Mantém o visual original mas com movimento mais fluido e natural
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

class FloatingBubble:
    """Bolha flutuante com design original e animação melhorada"""
    
    def __init__(self, space, coin_data, bounds, screen_size):
        self.coin_data = coin_data
        self.symbol = coin_data['symbol'].upper()
        self.price_change = coin_data.get('price_change_percentage_24h', 0.0) or 0.0
        self.market_cap = coin_data.get('market_cap', 1e9) or 1e9
        self.last_price_change = self.price_change
        self.screen_size = screen_size
        
        # Calculate bubble size based on market cap (ORIGINAL)
        market_cap_normalized = max(1e6, min(self.market_cap, 1e12))
        size_factor = math.sqrt(market_cap_normalized / 1e9)
        
        min_radius = 20
        max_radius = 50
        self.radius = min_radius + (max_radius - min_radius) * min(1.0, size_factor / 5.0)
        self.area = math.pi * self.radius * self.radius
        
        # Set bounds with safety margin
        self.update_bounds(bounds)
        
        # Create physics body (ORIGINAL)
        mass = self.radius / 25
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        
        # Safe initial position within bounds
        x = random.uniform(self.bounds.left + self.radius, self.bounds.right - self.radius)
        y = random.uniform(self.bounds.top + self.radius, self.bounds.bottom - self.radius)
        self.body.position = (x, y)
        
        # Physics properties (ORIGINAL)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = PHYSICS['bubble_elasticity']
        self.shape.friction = PHYSICS['bubble_friction']
        space.add(self.body, self.shape)
        
        # MELHORADA: Animação mais fluida e suave
        self.float_offset_x = random.uniform(0, 2 * math.pi)
        self.float_offset_y = random.uniform(0, 2 * math.pi)
        
        # Velocidades mais suaves para movimento fluido
        self.float_speed_x = random.uniform(0.5, 1.2)  # Mais lento e suave
        self.float_speed_y = random.uniform(0.6, 1.4)
        
        # Amplitudes mais naturais
        self.float_amplitude_x = random.uniform(0.3, 0.8)
        self.float_amplitude_y = random.uniform(0.4, 1.0)
        
        # Movimento adicional para mais fluidez
        self.drift_speed = random.uniform(0.2, 0.5)
        self.drift_amplitude = random.uniform(0.1, 0.3)
        self.drift_offset = random.uniform(0, 2 * math.pi)
        
        # Propriedades de movimento (MELHORADAS)
        self.velocity_damping = 0.96  # Mais suave
        self.max_velocity = 12.0  # Ligeiramente mais rápido para fluidez
        
        # Visual effects (ORIGINAL)
        self.effects = []
        
        # Calculate scaling factors (ORIGINAL)
        self.calculate_scaling_factors()
        
        # Load logo (ORIGINAL)
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
        """Update the boundary constraints for this bubble (ORIGINAL)"""
        safety_margin = self.radius + 15
        
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
        
        # If bubble is outside new bounds, reposition it
        if hasattr(self, 'body'):
            self.ensure_within_bounds()
    
    def ensure_within_bounds(self):
        """Ensure bubble is within current bounds (ORIGINAL)"""
        x, y = self.body.position
        
        # Check and correct position if outside bounds
        corrected_x = max(self.bounds.left, min(self.bounds.right, x))
        corrected_y = max(self.bounds.top, min(self.bounds.bottom, y))
        
        if corrected_x != x or corrected_y != y:
            self.body.position = (corrected_x, corrected_y)
            # Dampen velocity when repositioning
            vx, vy = self.body.velocity
            self.body.velocity = (vx * 0.5, vy * 0.5)
    
    def calculate_scaling_factors(self):
        """Calculate all scaling factors (ORIGINAL)"""
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

    def update_radius_for_screen(self, screen_size):
        """Update bubble radius when screen size changes (ORIGINAL)"""
        if abs(screen_size[0] - self.screen_size[0]) > 100 or abs(screen_size[1] - self.screen_size[1]) > 100:
            self.screen_size = screen_size
            
            market_cap_normalized = max(1e6, min(self.market_cap, 1e12))
            size_factor = math.sqrt(market_cap_normalized / 1e9)
            
            min_radius = 20
            max_radius = 50
            new_radius = min_radius + (max_radius - min_radius) * min(1.0, size_factor / 5.0)
            
            if abs(new_radius - self.radius) > 3:
                old_radius = self.radius
                self.radius = new_radius
                self.area = math.pi * self.radius * self.radius
                self.calculate_scaling_factors()
                
                # Update physics shape
                space = self.shape.space
                if space:
                    space.remove(self.shape)
                    self.shape = pymunk.Circle(self.body, self.radius)
                    self.shape.elasticity = PHYSICS['bubble_elasticity']
                    self.shape.friction = PHYSICS['bubble_friction']
                    space.add(self.shape)

    def update_data(self, new_coin_data):
        """Update bubble with new market data (ORIGINAL)"""
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

    def apply_boundary_forces(self):
        """MELHORADA: Forças de flutuação mais suaves e naturais"""
        x, y = self.body.position
        vx, vy = self.body.velocity
        
        # Apply velocity limiting (ORIGINAL)
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            vx *= scale
            vy *= scale
            self.body.velocity = (vx, vy)
        
        # MELHORADA: Movimento de flutuação mais suave e fluido
        current_time = time.time()
        
        # Movimento primário mais suave
        float_force_x = math.sin(current_time * self.float_speed_x + self.float_offset_x) * self.float_amplitude_x * 0.08
        float_force_y = math.cos(current_time * self.float_speed_y + self.float_offset_y) * self.float_amplitude_y * 0.1
        
        # Movimento secundário para mais naturalidade
        drift_force_x = math.cos(current_time * self.drift_speed + self.drift_offset) * self.drift_amplitude * 0.05
        drift_force_y = math.sin(current_time * self.drift_speed + self.drift_offset * 1.3) * self.drift_amplitude * 0.06
        
        # Movimento terciário muito sutil para quebrar padrões
        micro_force_x = math.sin(current_time * 2.1 + self.float_offset_x * 0.7) * 0.02
        micro_force_y = math.cos(current_time * 1.8 + self.float_offset_y * 0.8) * 0.025
        
        # Soft boundary forces (MELHORADAS)
        boundary_force_x = 0
        boundary_force_y = 0
        force_strength = 1.0  # Aumentado para melhor controle
        boundary_zone = self.radius * 3.5  # Zona maior para transições mais suaves
        
        # Horizontal boundaries com curvas suaves
        if x < self.bounds.left + boundary_zone:
            push_factor = 1.0 - (x - self.bounds.left) / boundary_zone
            # Curva suave para transição natural
            boundary_force_x = push_factor * push_factor * force_strength
        elif x > self.bounds.right - boundary_zone:
            push_factor = 1.0 - (self.bounds.right - x) / boundary_zone
            boundary_force_x = -push_factor * push_factor * force_strength
            
        # Vertical boundaries com curvas suaves
        if y < self.bounds.top + boundary_zone:
            push_factor = 1.0 - (y - self.bounds.top) / boundary_zone
            boundary_force_y = push_factor * push_factor * force_strength
        elif y > self.bounds.bottom - boundary_zone:
            push_factor = 1.0 - (self.bounds.bottom - y) / boundary_zone
            boundary_force_y = -push_factor * push_factor * force_strength
        
        # Apply enhanced velocity damping (MELHORADO)
        self.body.velocity = (vx * self.velocity_damping, vy * self.velocity_damping)
        
        # Combine all forces for fluid motion
        total_force_x = float_force_x + drift_force_x + micro_force_x + boundary_force_x
        total_force_y = float_force_y + drift_force_y + micro_force_y + boundary_force_y
        
        self.body.apply_force_at_local_point((total_force_x, total_force_y), (0, 0))
        
        # Hard boundary correction (MELHORADO para ser mais suave)
        corrected = False
        new_x, new_y = x, y
        new_vx, new_vy = vx, vy
        
        if x < self.bounds.left:
            new_x = self.bounds.left
            new_vx = max(0, vx * 0.4)  # Bounce mais suave
            corrected = True
        elif x > self.bounds.right:
            new_x = self.bounds.right
            new_vx = min(0, vx * 0.4)
            corrected = True
            
        if y < self.bounds.top:
            new_y = self.bounds.top
            new_vy = max(0, vy * 0.4)
            corrected = True
        elif y > self.bounds.bottom:
            new_y = self.bounds.bottom
            new_vy = min(0, vy * 0.4)
            corrected = True
        
        if corrected:
            self.body.position = (new_x, new_y)
            self.body.velocity = (new_vx, new_vy)

    def update(self, bounds):
        """Update bubble physics and effects (ORIGINAL)"""
        # Update bounds if they changed
        if bounds != self.bounds:
            self.update_bounds(bounds)
        
        self.apply_boundary_forces()
        
        # Update effects
        self.effects = [effect for effect in self.effects if effect.is_alive()]
        for effect in self.effects:
            effect.update()

    def check_click(self, mouse_pos):
        """Check if the bubble was clicked (ORIGINAL)"""
        x, y = self.body.position
        distance = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)
        return distance <= self.radius

    def get_coin_id(self):
        """Get the coin ID for API calls (ORIGINAL)"""
        return SYMBOL_TO_ID.get(self.symbol, self.symbol.lower())

    def draw(self, surface):
        """Draw bubble with ORIGINAL design and improved smoothness"""
        x, y = int(self.body.position.x), int(self.body.position.y)
        
        # Determine colors (ORIGINAL)
        is_negative = self.price_change < 0
        edge_color = COLORS['negative'] if is_negative else COLORS['positive']
        
        # Create gradient surface (ORIGINAL design)
        circle_surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        center_pos = (int(self.radius), int(self.radius))
        
        # Create radial gradient (ORIGINAL)
        fill_limit = int(self.radius * 0.4)
        
        for r in range(int(self.radius), fill_limit, -1):
            alpha_factor = (r - fill_limit) / (self.radius - fill_limit)
            alpha = int(160 * alpha_factor)
            
            color_with_alpha = (*edge_color, alpha)
            pygame.draw.circle(circle_surf, color_with_alpha, center_pos, r)
        
        # Blit the gradient circle (ORIGINAL)
        surface.blit(circle_surf, (x - int(self.radius), y - int(self.radius)))
        
        # Content layout (ORIGINAL)
        content_y_start = y + int(self.logo_y_offset)
        
        # Draw logo (ORIGINAL)
        if self.logo_surface:
            logo_rect = self.logo_surface.get_rect(center=(x, content_y_start))
            surface.blit(self.logo_surface, logo_rect)
            next_y = logo_rect.bottom + self.symbol_spacing
        else:
            next_y = content_y_start + self.symbol_spacing
        
        # Symbol text (ORIGINAL)
        symbol_font = pygame.font.SysFont("Arial", self.symbol_font_size, bold=True)
        text_color = COLORS['text_primary']
        
        # Smart symbol truncation (ORIGINAL)
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
        
        # Ensure symbol stays within bounds (ORIGINAL)
        max_symbol_y = y + int(self.radius * self.text_boundary_factor)
        if symbol_rect.bottom > max_symbol_y:
            symbol_rect.centery = max_symbol_y - symbol_text.get_height() // 2
        
        surface.blit(symbol_text, symbol_rect)
        
        # Percentage text (ORIGINAL)
        pct_font = pygame.font.SysFont("Arial", self.pct_font_size, bold=True)
        pct_color = COLORS['positive'] if not is_negative else COLORS['negative']
        
        # Format percentage (ORIGINAL)
        if self.area < 2000:
            pct_str = f"{self.price_change:+.1f}%"
        else:
            pct_str = f"{self.price_change:+.2f}%"
        
        # Check if percentage text fits (ORIGINAL)
        pct_text = pct_font.render(pct_str, True, pct_color)
        pct_width = pct_text.get_width()
        
        if pct_width > max_text_width:
            pct_str = f"{int(self.price_change):+d}%"
            pct_text = pct_font.render(pct_str, True, pct_color)
        
        # Position percentage (ORIGINAL)
        pct_y = symbol_rect.bottom + self.pct_spacing
        
        # Final boundary check (ORIGINAL)
        max_pct_y = y + int(self.radius * self.text_boundary_factor)
        if pct_y + pct_text.get_height() // 2 > max_pct_y:
            pct_y = max_pct_y - pct_text.get_height() // 2
        
        pct_rect = pct_text.get_rect(center=(x, pct_y))
        surface.blit(pct_text, pct_rect)
        
        # Draw floating effects (ORIGINAL)
        for effect in self.effects:
            effect.draw(surface)