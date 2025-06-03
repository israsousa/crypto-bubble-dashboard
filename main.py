#!/usr/bin/env python3
"""
Fixed Auto-Redistribution - Complete main.py
Ensures proper timing so bubble content (logo, text, %) updates correctly
"""

import pygame
import pymunk
import time
from threading import Thread, Timer
from datetime import datetime

# Local imports
from config.settings import *
from utils.data_loader import load_daily_ranks, save_daily_ranks
from data.crypto_api import update_crypto_data, update_news_data, update_fear_greed
from ui.loading_screen import draw_loading_screen
from ui.dashboard import Dashboard
from physics.bubble_manager import BubbleManager
from ui.modal_manager import ModalManager
from utils.realtime_fear_greed import start_local_realtime_fear_greed

class EnhancedFullscreenManager:
    """Enhanced fullscreen management with properly timed auto-redistribution"""
    
    def __init__(self):
        self.is_fullscreen = False
        self.windowed_size = (WIDTH, HEIGHT)
        self.screen = None
        self.desktop_size = None
        self._last_size = (WIDTH, HEIGHT)
        self._pending_redistribution = None  # Timer for delayed redistribution
        
    def initialize(self):
        """Initialize display system"""
        info = pygame.display.Info()
        self.desktop_size = (info.current_w, info.current_h)
        
        self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        pygame.display.set_caption("Crypto Bubble Live - Professional Edition")
        self._last_size = self.windowed_size
        print(f"🖥️ Display initialized: {self.windowed_size}")
        return self.screen
    
    def toggle_fullscreen(self, bubble_manager=None, dashboard=None):
        """Toggle fullscreen mode with properly timed auto-redistribution"""
        try:
            if self.is_fullscreen:
                print("🪟 Exiting fullscreen...")
                self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                self.is_fullscreen = False
                print(f"✅ Windowed mode: {self.windowed_size}")
            else:
                print("🖥️ Entering fullscreen...")
                # Save current window size
                self.windowed_size = self.screen.get_size()
                
                self.screen = pygame.display.set_mode(self.desktop_size, pygame.FULLSCREEN)
                self.is_fullscreen = True
                print(f"✅ Fullscreen mode: {self.desktop_size}")
            
            # FIXED AUTO-REDISTRIBUTION: Proper timing with layout update
            if bubble_manager and dashboard:
                new_size = self.screen.get_size()
                self._schedule_delayed_redistribution(new_size, bubble_manager, dashboard)
                self._last_size = new_size
            
            return True
            
        except pygame.error as e:
            print(f"❌ Fullscreen error: {e}")
            return False
    
    def handle_resize(self, new_size, bubble_manager=None, dashboard=None):
        """Handle window resize with properly timed auto-redistribution"""
        if not self.is_fullscreen:
            try:
                self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
                print(f"📏 Window resized: {new_size}")
                
                # FIXED AUTO-REDISTRIBUTION: Proper timing and threshold
                if bubble_manager and dashboard:
                    width_diff = abs(new_size[0] - self._last_size[0])
                    height_diff = abs(new_size[1] - self._last_size[1])
                    
                    # Only redistribute on significant changes (>100px in either dimension)
                    if width_diff > 100 or height_diff > 100:
                        self._schedule_delayed_redistribution(new_size, bubble_manager, dashboard)
                    
                    self._last_size = new_size
                
                return True
            except pygame.error as e:
                print(f"❌ Resize error: {e}")
                return False
        return False
    
    def _schedule_delayed_redistribution(self, new_size, bubble_manager, dashboard):
        """Schedule redistribution with proper timing to allow layout updates"""
        # Cancel any pending redistribution
        if self._pending_redistribution:
            self._pending_redistribution.cancel()
        
        print("🔄 Scheduling auto-redistribution with proper timing...")
        
        # Schedule redistribution after a small delay to ensure layout is updated
        self._pending_redistribution = Timer(0.1, self._execute_redistribution, 
                                           args=[new_size, bubble_manager, dashboard])
        self._pending_redistribution.start()
    
    def _execute_redistribution(self, new_size, bubble_manager, dashboard):
        """Execute redistribution with proper order of operations"""
        try:
            print("🔄 Executing auto-redistribution with proper layout sync...")
            
            # Step 1: Force dashboard layout update first
            dashboard.force_layout_update()
            
            # Step 2: Update bubble manager screen size
            bubble_manager.update_screen_size(new_size)
            
            # Step 3: Force redistribution (this should now have correct layout)
            bubble_manager.force_redistribute(new_size)
            
            print(f"✅ Auto-redistribution completed for {new_size}")
            
        except Exception as e:
            print(f"❌ Error in auto-redistribution: {e}")
    
    def get_current_size(self):
        """Get current screen size"""
        return self.screen.get_size()
    
    def is_fullscreen_active(self):
        """Check if in fullscreen mode"""
        return self.is_fullscreen

class ProfessionalDebugRenderer:
    """Professional debug overlay with enhanced information"""
    
    def __init__(self):
        self.enabled = True
        self.compact_mode = False
        self.position = 0
        self.positions = ["bottom_left", "bottom_right", "top_left", "top_right"]
        self.last_toggle = 0
        self.toggle_cooldown = 0.2
        
    def toggle(self):
        """Toggle debug display"""
        current_time = time.time()
        if current_time - self.last_toggle > self.toggle_cooldown:
            self.enabled = not self.enabled
            self.last_toggle = current_time
            print(f"🐛 Debug: {'ON' if self.enabled else 'OFF'}")
    
    def toggle_compact(self):
        """Toggle compact mode"""
        current_time = time.time()
        if current_time - self.last_toggle > self.toggle_cooldown:
            self.compact_mode = not self.compact_mode
            self.last_toggle = current_time
            print(f"📊 Debug mode: {'COMPACT' if self.compact_mode else 'DETAILED'}")
    
    def cycle_position(self):
        """Cycle debug position"""
        current_time = time.time()
        if current_time - self.last_toggle > self.toggle_cooldown:
            self.position = (self.position + 1) % len(self.positions)
            self.last_toggle = current_time
            print(f"📍 Debug position: {self.positions[self.position]}")
    
    def render(self, screen, layout_areas, fullscreen_manager, clock, bubble_manager, quality_mode=True):
        """Render professional debug overlay"""
        if not self.enabled:
            return
        
        # Professional fonts
        try:
            debug_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
            small_font = pygame.font.SysFont("Segoe UI", 9)
        except:
            debug_font = pygame.font.SysFont("Arial", 11, bold=True)
            small_font = pygame.font.SysFont("Arial", 9)
        
        # System info
        current_size = fullscreen_manager.get_current_size()
        mode = "FULLSCREEN" if fullscreen_manager.is_fullscreen_active() else "WINDOWED"
        fps = clock.get_fps()
        bubble_count = bubble_manager.get_bubble_count()
        mode_indicator = "[QUALITY]" if quality_mode else "[PERFORMANCE]"
        
        if self.compact_mode:
            # Compact single line
            debug_text = f"{current_size[0]}x{current_size[1]} {mode} | FPS: {fps:.1f} | Bubbles: {bubble_count} {mode_indicator} | Auto-Redist: SYNCED"
            text_surface = debug_font.render(debug_text, True, (200, 220, 255))
            
            # Position based on current setting
            margin = 15
            if self.positions[self.position] == "top_left":
                x, y = margin, margin
            elif self.positions[self.position] == "top_right":
                x, y = current_size[0] - text_surface.get_width() - margin, margin
            elif self.positions[self.position] == "bottom_right":
                x, y = current_size[0] - text_surface.get_width() - margin, current_size[1] - text_surface.get_height() - margin
            else:  # bottom_left
                x, y = margin, current_size[1] - text_surface.get_height() - margin
            
            # Professional background
            bg_width = text_surface.get_width() + 16
            bg_height = text_surface.get_height() + 8
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (20, 25, 35, 220), (0, 0, bg_width, bg_height), border_radius=6)
            pygame.draw.rect(bg_surface, (70, 90, 120, 150), (0, 0, bg_width, bg_height), 1, border_radius=6)
            
            screen.blit(bg_surface, (x - 8, y - 4))
            screen.blit(text_surface, (x, y))
            
        else:
            # Detailed mode
            bubble_area = layout_areas['bubble_area']
            debug_x = bubble_area.left + 10
            debug_y = bubble_area.bottom - 90
            
            # Professional background
            bg_width = 1000
            bg_height = 80
            debug_bg = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(debug_bg, (20, 25, 35, 240), (0, 0, bg_width, bg_height), border_radius=8)
            pygame.draw.rect(debug_bg, (70, 90, 120, 180), (0, 0, bg_width, bg_height), 2, border_radius=8)
            screen.blit(debug_bg, (debug_x - 8, debug_y - 8))
            
            # Main info line
            line1 = f"DISPLAY: {current_size[0]}x{current_size[1]} ({mode}) | FPS: {fps:.1f} | BUBBLES: {bubble_count} {mode_indicator} | Auto-Redist: SYNCED"
            text1 = debug_font.render(line1, True, (220, 230, 250))
            screen.blit(text1, (debug_x, debug_y))
            
            # Controls line
            line2 = "CONTROLS: F11=Fullscreen+Sync Redist | ESC=Exit | R=Manual Redist | D=Debug | SHIFT+D=Compact | TAB=Position | P=Quality"
            text2 = pygame.font.SysFont("Segoe UI", 10)
            text2_surface = text2.render(line2, True, (160, 180, 210))
            screen.blit(text2_surface, (debug_x, debug_y + 18))
            
            # Status line
            aspect_ratio = current_size[0] / current_size[1] if current_size[1] > 0 else 1.0
            position_name = self.positions[self.position].replace("_", " ").title()
            line3 = f"STATUS: Aspect {aspect_ratio:.2f} | Desktop {fullscreen_manager.desktop_size[0]}x{fullscreen_manager.desktop_size[1]} | Debug: {position_name} | Layout-Sync: ENABLED"
            text3 = pygame.font.SysFont("Segoe UI", 10)
            text3_surface = text3.render(line3, True, (140, 160, 190))
            screen.blit(text3_surface, (debug_x, debug_y + 36))

def main():
    """Enhanced main application with synchronized auto-redistribution"""
    try:
        # Initialize data
        load_daily_ranks()
        
        # Initialize pygame
        pygame.init()
        
        # Enhanced managers
        fullscreen_manager = EnhancedFullscreenManager()
        screen = fullscreen_manager.initialize()
        clock = pygame.time.Clock()
        
        # Debug system
        debug_renderer = ProfessionalDebugRenderer()
        
        # Quality mode
        quality_mode = True
        
        # Physics system
        space = pymunk.Space()
        space.gravity = PHYSICS['gravity']
        space.damping = PHYSICS['damping']
        
        # Core managers
        dashboard = Dashboard()
        bubble_manager = BubbleManager(space)
        modal_manager = ModalManager()
        
        # Start data loading threads
        print("🚀 Starting professional crypto dashboard...")
        Thread(target=update_crypto_data, daemon=True).start()
        Thread(target=update_news_data, daemon=True).start()
        Thread(target=update_fear_greed, daemon=True).start()
        
        # START LOCAL REAL-TIME FEAR & GREED
        print("🎯 Starting local real-time Fear & Greed calculator...")
        start_local_realtime_fear_greed()
        
        # Load initial data
        dashboard.load_initial_data()
        
        running = True
        last_screen_size = screen.get_size()
        
        # Enhanced physics update function
        def update_enhanced_physics():
            """Update physics with enhanced quality settings"""
            if quality_mode:
                target_fps = 90
                dt = min(clock.tick(target_fps) / 1000.0, 1.0/45.0)
            else:
                target_fps = 60
                dt = min(clock.tick(target_fps) / 1000.0, 1.0/30.0)
            
            sub_steps = 2 if quality_mode else 1
            sub_dt = dt / sub_steps
            
            for _ in range(sub_steps):
                space.step(sub_dt)
            
            return dt
        
        print("✅ Professional dashboard started with synchronized features!")
        print("🔧 Features Active:")
        print("   ✅ Synchronized auto-redistribution (layout + bubbles)")
        print("   ✅ Interactive charts with hover/pin/zoom")
        print("   ✅ Enhanced Fear & Greed with local calculation")
        print("   ✅ Rate-limited API to prevent 429 errors")
        
        while running:
            # Enhanced event handling with synchronized auto-redistribution
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("🔄 Shutting down...")
                    save_daily_ranks()
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Modal clicks first
                        if modal_manager.handle_mouse_down(mouse_pos, 1):
                            continue
                        
                        # Bubble clicks
                        if dashboard.is_loaded():
                            bubble_manager.handle_click(mouse_pos, modal_manager, screen.get_size())
                    
                    elif event.button == 3:  # Right click
                        mouse_pos = pygame.mouse.get_pos()
                        modal_manager.handle_mouse_down(mouse_pos, 3)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in [1, 3]:
                        modal_manager.handle_mouse_up(mouse_pos, button)
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    modal_manager.handle_mouse_move(mouse_pos)
                
                elif event.type == pygame.MOUSEWHEEL:
                    mouse_pos = pygame.mouse.get_pos()
                    modal_manager.handle_scroll(mouse_pos, event.y)
                    
                elif event.type == pygame.VIDEORESIZE:
                    # FIXED: Synchronized resize handling
                    if not fullscreen_manager.is_fullscreen_active():
                        if fullscreen_manager.handle_resize(event.size, bubble_manager, dashboard):
                            screen = fullscreen_manager.screen
                            new_size = screen.get_size()
                            print(f"📏 Window resized: {last_screen_size} → {new_size}")
                            
                            # Manual updates for immediate responsiveness
                            bubble_manager.update_screen_size(new_size)
                            dashboard.force_layout_update()
                            last_screen_size = new_size
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if modal_manager.has_active_modal():
                            modal_manager.close_active_modal()
                        elif fullscreen_manager.is_fullscreen_active():
                            # FIXED: Synchronized fullscreen exit
                            if fullscreen_manager.toggle_fullscreen(bubble_manager, dashboard):
                                screen = fullscreen_manager.screen
                                new_size = screen.get_size()
                                bubble_manager.update_screen_size(new_size)
                                dashboard.force_layout_update()
                                last_screen_size = new_size
                        else:
                            save_daily_ranks()
                            running = False
                            
                    elif event.key == pygame.K_SPACE:
                        if not dashboard.is_loaded():
                            print("⏩ Manual loading skip")
                            dashboard.force_complete_loading()
                            
                    elif event.key == pygame.K_r:
                        print("🔄 Manual bubble redistribution (R key)...")
                        # Manual R key still works as before for immediate redistribution
                        dashboard.force_layout_update()
                        bubble_manager.force_redistribute(screen.get_size())
                        
                    elif event.key == pygame.K_F11:
                        # FIXED: Synchronized fullscreen toggle
                        print("🖥️ Toggling fullscreen (F11) with synchronized redistribution...")
                        if fullscreen_manager.toggle_fullscreen(bubble_manager, dashboard):
                            screen = fullscreen_manager.screen
                            new_size = screen.get_size()
                            
                            # Manual updates for immediate responsiveness
                            bubble_manager.update_screen_size(new_size)
                            dashboard.force_layout_update()
                            last_screen_size = new_size
                            
                    elif event.key == pygame.K_p:
                        quality_mode = not quality_mode
                        mode_name = "QUALITY (90 FPS)" if quality_mode else "PERFORMANCE (60 FPS)"
                        print(f"⚙️ Mode switched to: {mode_name}")
                        
                    elif event.key == pygame.K_TAB:
                        debug_renderer.cycle_position()
                            
                    elif event.key == pygame.K_d:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            debug_renderer.toggle_compact()
                        else:
                            debug_renderer.toggle()
            
            # Loading screen check
            if not dashboard.is_loaded():
                draw_loading_screen(screen)
                pygame.display.flip()
                clock.tick(30)
                continue
            
            # Initialize enhanced bubbles
            bubble_manager.initialize_bubbles_if_needed(dashboard.get_crypto_data(), screen.get_size())
            
            # Update all components
            dashboard.update()
            bubble_manager.update(dashboard.get_crypto_data())
            modal_manager.update()
            
            # Enhanced physics
            dt = update_enhanced_physics()
            
            # Render everything
            current_screen_size = screen.get_size()
            layout_areas = dashboard.get_layout_areas(current_screen_size)
            
            # Clear with professional background
            screen.fill(COLORS['background'])
            
            # Render dashboard
            dashboard.render(screen)
            
            # Render enhanced bubbles
            bubble_manager.render(screen, layout_areas)
            
            # Render enhanced modal
            modal_manager.render(screen)
            
            # Professional debug overlay
            debug_renderer.render(screen, layout_areas, fullscreen_manager, clock, bubble_manager, quality_mode)
            
            # Update display
            pygame.display.flip()
    
    except KeyboardInterrupt:
        print("\n🔄 Graceful shutdown...")
        save_daily_ranks()
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        save_daily_ranks()
        try:
            pygame.quit()
        except:
            pass
        print("✅ Professional dashboard closed successfully!")

if __name__ == "__main__":
    main()