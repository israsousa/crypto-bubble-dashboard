"""
Visual effects for the cryptocurrency dashboard
"""

import pygame
import random
from config.settings import COLORS

class FloatingEffect:
    """Enhanced visual effect for price changes"""
    
    def __init__(self, text, position, is_positive):
        self.text = text
        self.position = list(position)
        self.start_position = list(position)
        self.alpha = 255
        self.is_positive = is_positive
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.color = COLORS['positive'] if is_positive else COLORS['negative']
        self.lifetime = 120  # frames
        self.age = 0
        
        # Enhanced animation properties
        self.velocity_y = -1.5 if is_positive else 1.2
        self.velocity_x = random.uniform(-0.5, 0.5)
        self.scale = 1.0

    def update(self):
        """Update the floating effect animation"""
        self.age += 1
        
        # Update position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Decelerate movement over time
        self.velocity_y *= 0.98
        self.velocity_x *= 0.99
        
        # Scale effect
        if self.age < 20:
            self.scale = 1.0 + (self.age / 20) * 0.3
        else:
            self.scale = 1.3 - ((self.age - 20) / (self.lifetime - 20)) * 0.3
        
        # Fade out
        fade_progress = self.age / self.lifetime
        self.alpha = max(0, int(255 * (1 - fade_progress * fade_progress)))

    def draw(self, surface):
        """Draw the floating effect"""
        if self.alpha <= 0:
            return
        
        # Apply scaling
        scaled_font_size = max(10, int(14 * self.scale))
        scaled_font = pygame.font.SysFont("Arial", scaled_font_size, bold=True)
        
        # Create text surface
        text_surface = scaled_font.render(self.text, True, self.color)
        text_surface.set_alpha(int(self.alpha))
        rect = text_surface.get_rect(center=(int(self.position[0]), int(self.position[1])))
        surface.blit(text_surface, rect)

    def is_alive(self):
        """Check if the effect is still alive"""
        return self.age < self.lifetime


class PulseEffect:
    """Pulsing effect for important elements"""
    
    def __init__(self, center, radius, color, duration=60):
        self.center = center
        self.radius = radius
        self.max_radius = radius * 2
        self.color = color
        self.duration = duration
        self.age = 0
        self.alpha = 255
    
    def update(self):
        """Update pulse animation"""
        self.age += 1
        progress = self.age / self.duration
        
        # Expand radius
        self.radius = self.radius + (self.max_radius - self.radius) * 0.1
        
        # Fade out
        self.alpha = max(0, int(255 * (1 - progress)))
    
    def draw(self, surface):
        """Draw the pulse effect"""
        if self.alpha <= 0:
            return
        
        # Create transparent surface for the pulse
        pulse_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pulse_color = (*self.color, self.alpha)
        pygame.draw.circle(pulse_surface, pulse_color, 
                         (int(self.radius), int(self.radius)), int(self.radius), 3)
        
        # Blit to main surface
        rect = pulse_surface.get_rect(center=self.center)
        surface.blit(pulse_surface, rect)
    
    def is_alive(self):
        """Check if effect is still alive"""
        return self.age < self.duration


class ParticleEffect:
    """Particle system for celebration effects"""
    
    def __init__(self, center, count=10, color=None):
        self.particles = []
        self.center = center
        
        for _ in range(count):
            particle = {
                'pos': [center[0], center[1]],
                'vel': [random.uniform(-3, 3), random.uniform(-5, -1)],
                'life': random.randint(30, 60),
                'max_life': random.randint(30, 60),
                'color': color or (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            }
            self.particles.append(particle)
    
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:
            # Update position
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            
            # Apply gravity
            particle['vel'][1] += 0.2
            
            # Reduce life
            particle['life'] -= 1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * life_ratio)
            
            if alpha > 0:
                color = (*particle['color'], alpha)
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (3, 3), 3)
                surface.blit(particle_surface, particle['pos'])
    
    def is_alive(self):
        """Check if any particles are still alive"""
        return len(self.particles) > 0


class GlowEffect:
    """Glow effect for highlighting elements"""
    
    def __init__(self, rect, color, intensity=100):
        self.rect = rect
        self.color = color
        self.intensity = intensity
        self.pulse_phase = 0
    
    def update(self):
        """Update glow animation"""
        self.pulse_phase += 0.1
    
    def draw(self, surface):
        """Draw glow effect"""
        # Create glow surface
        glow_rect = pygame.Rect(self.rect.x - 10, self.rect.y - 10, 
                               self.rect.width + 20, self.rect.height + 20)
        
        # Pulsing intensity
        pulse_intensity = self.intensity + (20 * abs(pygame.math.Vector2(1, 0).rotate(self.pulse_phase).x))
        
        # Draw multiple layers for glow effect
        for i in range(5):
            alpha = max(0, int(pulse_intensity - (i * 20)))
            if alpha > 0:
                glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                glow_color = (*self.color, alpha)
                pygame.draw.rect(glow_surface, glow_color, 
                               (i, i, glow_rect.width - 2*i, glow_rect.height - 2*i), 
                               border_radius=5)
                surface.blit(glow_surface, (glow_rect.x + i, glow_rect.y + i))