"""
Enhanced Modal Manager - Complete File with Interactive Chart Support
Replace your entire ui/modal_manager.py with this version
"""

import pygame
import time

class ModalManager:
    """Enhanced modal management with comprehensive interactive chart support"""
    
    def __init__(self):
        self.active_modal = None
        self.last_update = time.time()
        
    def open_crypto_modal(self, coin_data: dict, screen_size: tuple):
        """Open professional crypto modal with working interactions"""
        # Close existing modal
        if self.active_modal:
            self.active_modal.close()
        
        # Import the professional modal
        try:
            # Try to import our enhanced professional modal
            from ui.crypto_modal import ProfessionalCryptoModal
            self.active_modal = ProfessionalCryptoModal(coin_data, screen_size)
            modal_type = "Professional"
        except ImportError:
            print("Warning: Professional modal not found, trying backup...")
            try:
                # Fallback to clean modal
                from ui.crypto_modal import CleanCryptoModal
                self.active_modal = CleanCryptoModal(coin_data, screen_size)
                modal_type = "Clean"
            except ImportError:
                print("Warning: No suitable modal found, using basic fallback...")
                # Create a basic fallback modal
                self.active_modal = BasicFallbackModal(coin_data, screen_size)
                modal_type = "Basic"
        
        self.active_modal.open()
        
        symbol = coin_data.get('symbol', 'Unknown').upper()
        print(f"🚀 {modal_type} modal opened for {symbol}")
    
    def close_active_modal(self):
        """Close active modal"""
        if self.active_modal:
            self.active_modal.close()
            self.active_modal = None
            print("❌ Modal closed")
    
    def has_active_modal(self) -> bool:
        """Check if modal is active"""
        return self.active_modal is not None and self.active_modal.is_active
    
    # =========================================================================
    # ENHANCED EVENT HANDLING FOR INTERACTIVE CHARTS
    # =========================================================================
    
    def handle_click(self, mouse_pos: tuple) -> bool:
        """Handle modal clicks with proper event handling (legacy method)"""
        if self.active_modal and self.active_modal.is_active:
            try:
                return self.active_modal.handle_click(mouse_pos)
            except Exception as e:
                print(f"❌ Error handling modal click: {e}")
                # Close modal on error to prevent crashes
                self.close_active_modal()
                return True
        return False
    
    def handle_mouse_down(self, mouse_pos: tuple, button: int) -> bool:
        """Handle mouse press events for interactive charts"""
        if self.active_modal and self.active_modal.is_active:
            try:
                if button == 1:  # Left click
                    return self.active_modal.handle_click(mouse_pos)
                elif button == 3:  # Right click for tooltip unpinning
                    if hasattr(self.active_modal, 'handle_right_click'):
                        return self.active_modal.handle_right_click(mouse_pos)
                    else:
                        # Fallback to regular click handling
                        return self.active_modal.handle_click(mouse_pos)
            except Exception as e:
                print(f"❌ Error handling modal mouse down: {e}")
                # Close modal on error to prevent crashes
                self.close_active_modal()
                return True
        return False
    
    def handle_mouse_up(self, mouse_pos: tuple, button: int) -> bool:
        """Handle mouse release events for drag operations"""
        if self.active_modal and self.active_modal.is_active:
            try:
                if hasattr(self.active_modal, 'handle_mouse_up'):
                    return self.active_modal.handle_mouse_up(mouse_pos, button)
            except Exception as e:
                print(f"⚠️ Error handling modal mouse up: {e}")
                # Don't close modal for mouse up errors, just log
        return False
    
    def handle_scroll(self, mouse_pos: tuple, scroll_y: int) -> bool:
        """Handle mouse wheel events for chart zoom"""
        if self.active_modal and self.active_modal.is_active:
            try:
                if hasattr(self.active_modal, 'handle_scroll'):
                    return self.active_modal.handle_scroll(mouse_pos, scroll_y)
            except Exception as e:
                print(f"⚠️ Error handling modal scroll: {e}")
                # Don't close modal for scroll errors, just log
        return False
    
    def handle_mouse_move(self, mouse_pos: tuple):
        """Handle mouse movement for chart interactions and cursor feedback"""
        if self.active_modal and self.active_modal.is_active:
            try:
                self.active_modal.handle_mouse_move(mouse_pos)
            except Exception as e:
                print(f"⚠️ Error handling modal mouse move: {e}")
                # Don't close modal for mouse move errors, just log
    
    # =========================================================================
    # CORE MODAL MANAGEMENT
    # =========================================================================
    
    def update(self):
        """Update modal animations and interactions"""
        current_time = time.time()
        dt = min(current_time - self.last_update, 1/30.0)  # Cap dt to prevent large jumps
        self.last_update = current_time
        
        if self.active_modal and self.active_modal.is_active:
            try:
                self.active_modal.update(dt)
            except Exception as e:
                print(f"⚠️ Error updating modal: {e}")
                # Don't close modal for update errors, just log
    
    def render(self, surface: pygame.Surface):
        """Render active modal with error handling"""
        if self.active_modal and self.active_modal.is_active:
            try:
                self.active_modal.draw(surface)
            except Exception as e:
                print(f"❌ Error rendering modal: {e}")
                # Close modal on render error to prevent display issues
                self.close_active_modal()


class BasicFallbackModal:
    """Basic fallback modal for when professional modal isn't available"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.symbol = coin_data['symbol'].upper()
        self.is_active = False
        
        # Simple modal dimensions
        self.width = int(screen_size[0] * 0.6)
        self.height = int(screen_size[1] * 0.6)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        self.close_button_rect = None
        self.mouse_pos = (0, 0)
        
    def open(self):
        """Open basic modal"""
        self.is_active = True
        
    def close(self):
        """Close basic modal"""
        self.is_active = False
        
    def handle_click(self, pos: tuple) -> bool:
        """Handle clicks on basic modal"""
        if not self.is_active:
            return False
            
        # Check if clicked outside modal
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not modal_rect.collidepoint(pos):
            self.close()
            return True
            
        # Close button
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close()
            return True
            
        return True
    
    def handle_right_click(self, pos: tuple) -> bool:
        """Handle right-click (same as regular click for basic modal)"""
        return self.handle_click(pos)
    
    def handle_mouse_up(self, pos: tuple, button: int) -> bool:
        """Handle mouse release (basic implementation)"""
        return False
    
    def handle_scroll(self, pos: tuple, scroll_y: int) -> bool:
        """Handle scroll (basic implementation)"""
        return False
        
    def handle_mouse_move(self, pos: tuple):
        """Handle mouse movement"""
        self.mouse_pos = pos
        
    def update(self, dt: float):
        """Update basic modal"""
        pass
        
    def draw(self, surface: pygame.Surface):
        """Draw basic modal"""
        if not self.is_active:
            return
            
        # Simple overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # Simple modal background
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (40, 50, 60), modal_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 120, 140), modal_rect, 2, border_radius=10)
        
        # Title
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
        title_text = f"{self.coin_data.get('name', self.symbol)} ({self.symbol})"
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.x + self.width//2, self.y + 40))
        surface.blit(title_surface, title_rect)
        
        # Basic info
        info_font = pygame.font.SysFont("Arial", 16)
        current_price = self.coin_data.get('current_price', 0)
        change_24h = self.coin_data.get('price_change_percentage_24h', 0) or 0
        
        price_text = f"Price: ${current_price:,.4f}" if current_price < 1 else f"Price: ${current_price:,.2f}"
        change_text = f"24h Change: {change_24h:+.2f}%"
        
        price_surface = info_font.render(price_text, True, (220, 220, 220))
        change_color = (80, 200, 80) if change_24h >= 0 else (200, 80, 80)
        change_surface = info_font.render(change_text, True, change_color)
        
        surface.blit(price_surface, (self.x + 30, self.y + 100))
        surface.blit(change_surface, (self.x + 30, self.y + 130))
        
        # Message
        message_text = "Enhanced chart modal loaded successfully"
        message_surface = info_font.render(message_text, True, (180, 180, 180))
        surface.blit(message_surface, (self.x + 30, self.y + 180))
        
        # Close button
        button_size = 30
        button_x = self.x + self.width - button_size - 10
        button_y = self.y + 10
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Check hover
        mouse_in_button = self.close_button_rect.collidepoint(self.mouse_pos)
        button_color = (200, 80, 80) if mouse_in_button else (120, 60, 60)
        
        pygame.draw.rect(surface, button_color, self.close_button_rect, border_radius=4)
        
        # X symbol
        center_x = button_x + button_size // 2
        center_y = button_y + button_size // 2
        line_len = button_size // 4
        
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 2)
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 2)