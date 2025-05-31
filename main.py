#!/usr/bin/env python3
"""
Crypto Bubble Live Dashboard - Main Application
Enhanced design with 100+ cryptocurrencies, real-time data, and interactive charts
"""

import pygame
import pymunk
import time
from threading import Thread
from datetime import datetime

# Local imports
from config.settings import *
from utils.data_loader import load_daily_ranks, save_daily_ranks
from data.crypto_api import update_crypto_data, update_news_data, update_fear_greed
from ui.loading_screen import draw_loading_screen
from ui.dashboard import Dashboard
from physics.bubble_manager import BubbleManager
from ui.modal_manager import ModalManager

def main():
    """Main application loop with enhanced loading screen and crypto detail modal system"""
    try:
        # Load daily rank tracking data
        load_daily_ranks()
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Crypto Bubble Live - Enhanced Design")
        clock = pygame.time.Clock()
        
        # Initialize physics space
        space = pymunk.Space()
        space.gravity = (0, 0)
        space.damping = 0.95
        
        # Initialize managers
        dashboard = Dashboard()
        bubble_manager = BubbleManager(space)
        modal_manager = ModalManager()
        
        # Start background threads for data loading
        print("Starting background data loading threads...")
        Thread(target=update_crypto_data, daemon=True).start()
        Thread(target=update_news_data, daemon=True).start()
        Thread(target=update_fear_greed, daemon=True).start()
        
        print("Enhanced crypto bubble dashboard starting...")
        
        # Load initial data
        dashboard.load_initial_data()
        
        running = True
        last_screen_size = screen.get_size()
        
        print("Starting main loop with loading screen...")
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Shutting down...")
                    save_daily_ranks()
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Handle modal clicks first
                        if modal_manager.handle_click(mouse_pos):
                            continue
                        
                        # Check bubble clicks
                        if dashboard.is_loaded():
                            bubble_manager.handle_click(mouse_pos, modal_manager, screen.get_size())
                    
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    current_size = screen.get_size()
                    if current_size != last_screen_size:
                        bubble_manager.update_screen_size(current_size)
                        last_screen_size = current_size
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if modal_manager.has_active_modal():
                            modal_manager.close_active_modal()
                        else:
                            save_daily_ranks()
                            running = False
                    elif event.key == pygame.K_SPACE:
                        if not dashboard.is_loaded():
                            print("Manual loading skip triggered")
                            dashboard.force_complete_loading()
            
            # Check if we should show loading screen or main dashboard
            if not dashboard.is_loaded():
                draw_loading_screen(screen)
                pygame.display.flip()
                clock.tick(30)
                continue
            
            # Initialize bubbles if needed
            bubble_manager.initialize_bubbles_if_needed(dashboard.get_crypto_data(), screen.get_size())
            
            # Update components
            dashboard.update()
            bubble_manager.update(dashboard.get_crypto_data())
            
            # Physics simulation
            dt = min(clock.tick(FPS) / 1000.0, 1.0/30.0)
            space.step(dt)
            
            # Render everything
            dashboard.render(screen)
            bubble_manager.render(screen, dashboard.get_layout_areas(screen.get_size()))
            modal_manager.render(screen)
            
            pygame.display.flip()
    
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        save_daily_ranks()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        save_daily_ranks()
        pygame.quit()
        print("Dashboard closed successfully!")

if __name__ == "__main__":
    main()