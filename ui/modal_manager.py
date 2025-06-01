"""
Clean Modal Manager - Professional and efficient
"""

import pygame
import time

# Import do novo modal limpo
try:
    from ui.crypto_modal import CleanCryptoModal
except ImportError:
    print("Warning: Clean modal not found, using fallback")
    from ui.crypto_modal import CryptoDetailModal as CleanCryptoModal

class ModalManager:
    """Clean and efficient modal management"""
    
    def __init__(self):
        self.active_modal = None
        self.last_update = time.time()
        
    def open_crypto_modal(self, coin_data: dict, screen_size: tuple):
        """Open clean crypto modal"""
        # Close existing modal
        if self.active_modal:
            self.active_modal.close()
        
        # Create new clean modal
        self.active_modal = CleanCryptoModal(coin_data, screen_size)
        self.active_modal.open()
        
        print(f"Clean modal opened for {coin_data.get('symbol', 'Unknown').upper()}")
    
    def close_active_modal(self):
        """Close active modal"""
        if self.active_modal:
            self.active_modal.close()
            self.active_modal = None
            print("Modal closed")
    
    def has_active_modal(self) -> bool:
        """Check if modal is active"""
        return self.active_modal is not None and self.active_modal.is_active
    
    def handle_click(self, mouse_pos: tuple) -> bool:
        """Handle modal clicks"""
        if self.active_modal and self.active_modal.is_active:
            return self.active_modal.handle_click(mouse_pos)
        return False
    
    def handle_mouse_move(self, mouse_pos: tuple):
        """Handle mouse movement"""
        if self.active_modal and self.active_modal.is_active:
            self.active_modal.handle_mouse_move(mouse_pos)
    
    def update(self):
        """Update modal animations"""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        if self.active_modal and self.active_modal.is_active:
            self.active_modal.update(dt)
    
    def render(self, surface: pygame.Surface):
        """Render active modal"""
        if self.active_modal and self.active_modal.is_active:
            self.active_modal.draw(surface)