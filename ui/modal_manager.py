"""
Modal window manager
"""

import pygame
from ui.crypto_modal import CryptoDetailModal

class ModalManager:
    """Manages modal windows in the application"""
    
    def __init__(self):
        self.active_modal = None
    
    def open_crypto_modal(self, coin_data, screen_size):
        """Open a cryptocurrency detail modal"""
        self.active_modal = CryptoDetailModal(coin_data, screen_size)
        self.active_modal.open()
    
    def close_active_modal(self):
        """Close the currently active modal"""
        if self.active_modal:
            self.active_modal.close()
            self.active_modal = None
    
    def has_active_modal(self):
        """Check if there's an active modal"""
        return self.active_modal is not None and self.active_modal.is_active
    
    def handle_click(self, mouse_pos):
        """Handle mouse clicks on modals"""
        if self.active_modal and self.active_modal.is_active:
            return self.active_modal.handle_click(mouse_pos)
        return False
    
    def render(self, surface):
        """Render the active modal if any"""
        if self.active_modal and self.active_modal.is_active:
            self.active_modal.draw(surface)