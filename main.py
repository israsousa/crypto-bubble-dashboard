#!/usr/bin/env python3
"""
Crypto Bubble Live Dashboard - Main Application
Enhanced design with 500+ cryptocurrencies, real-time data, and interactive charts
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
        
        # Estado do fullscreen (apenas para debug info)
        is_fullscreen_detected = False
        
        # Debug info settings
        show_debug = True
        
        # Initialize screen in windowed mode
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Crypto Bubble Live - Enhanced Design")
        clock = pygame.time.Clock()
        
        print(f"🖥️ Started in windowed mode: {WIDTH}x{HEIGHT}")
        
        # Initialize physics space
        space = pymunk.Space()
        space.gravity = PHYSICS['gravity']
        space.damping = PHYSICS['damping']
        
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
        
        def simulate_native_fullscreen_button():
            """
            Simula o clique no botão verde do macOS
            Força o sistema a pensar que o usuário clicou no botão nativo
            """
            try:
                print("🍎 Simulando clique no botão verde do macOS...")
                
                # No macOS, o comando CMD+Control+F simula fullscreen
                # Vamos tentar diferentes abordagens para trigger o fullscreen nativo
                
                current_size = screen.get_size()
                info = pygame.display.Info()
                desktop_size = (info.current_w, info.current_h)
                
                print(f"   Tamanho atual: {current_size}")
                print(f"   Desktop: {desktop_size}")
                
                # Se já está em fullscreen, criar evento para sair
                if (abs(current_size[0] - desktop_size[0]) < 50 and 
                    abs(current_size[1] - desktop_size[1]) < 50):
                    
                    print("   Detectado em fullscreen, simulando saída...")
                    # Simular VIDEORESIZE para tamanho menor (windowed)
                    new_size = (1280, 720)
                    resize_event = pygame.event.Event(pygame.VIDEORESIZE, 
                                                    size=new_size, w=new_size[0], h=new_size[1])
                    pygame.event.post(resize_event)
                    
                else:
                    print("   Detectado em windowed, simulando entrada em fullscreen...")
                    # Simular VIDEORESIZE para tamanho do desktop
                    resize_event = pygame.event.Event(pygame.VIDEORESIZE, 
                                                    size=desktop_size, w=desktop_size[0], h=desktop_size[1])
                    pygame.event.post(resize_event)
                
                print("✅ Evento VIDEORESIZE simulado - processará no próximo frame")
                return True
                
            except Exception as e:
                print(f"❌ Erro simulando botão nativo: {e}")
                return False
        
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
                    # Este é o ÚNICO lugar onde lidamos com mudanças de tamanho
                    # Funciona tanto para o botão verde nativo quanto para a tecla F
                    print(f"🍎 VIDEORESIZE (nativo ou simulado): {event.size}")
                    
                    try:
                        # Atualizar screen
                        screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                        new_size = screen.get_size()
                        
                        print(f"📏 Tamanho atualizado: {last_screen_size} → {new_size}")
                        
                        # Detectar se é fullscreen baseado no tamanho
                        info = pygame.display.Info()
                        desktop_size = (info.current_w, info.current_h)
                        
                        if (abs(new_size[0] - desktop_size[0]) < 50 and 
                            abs(new_size[1] - desktop_size[1]) < 50):
                            is_fullscreen_detected = True
                            print("🍎 Estado: FULLSCREEN")
                        else:
                            is_fullscreen_detected = False
                            print("🍎 Estado: WINDOWED")
                        
                        # Atualizar componentes (como o botão verde faz)
                        bubble_manager.update_screen_size(new_size)
                        dashboard.force_layout_update()
                        
                        last_screen_size = new_size
                        
                        print("✅ Componentes atualizados pelo VIDEORESIZE")
                        
                    except pygame.error as e:
                        print(f"❌ VIDEORESIZE error: {e}")
                        
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
                    elif event.key == pygame.K_r:
                        print("🔄 Manual redistribution (R key)")
                        bubble_manager.force_redistribute(screen.get_size())
                    elif event.key == pygame.K_f:
                        # *** TECLA F = SIMULA O BOTÃO VERDE DO MACOS ***
                        print("🍎 TECLA F: Simulando botão verde do macOS...")
                        simulate_native_fullscreen_button()
                    elif event.key == pygame.K_d:
                        show_debug = not show_debug
                        print(f"🐛 Debug: {'ON' if show_debug else 'OFF'}")
            
            # Detecção automática de mudanças (backup)
            current_size = screen.get_size()
            if current_size != last_screen_size:
                print(f"🔍 Mudança detectada: {last_screen_size} → {current_size}")
                bubble_manager.update_screen_size(current_size)
                last_screen_size = current_size
            
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
            current_screen_size = screen.get_size()
            layout_areas = dashboard.get_layout_areas(current_screen_size)
            
            # Clear screen
            screen.fill(COLORS['background'])
            
            # Render dashboard components
            dashboard.render(screen)
            
            # Render bubbles
            bubble_manager.render(screen, layout_areas)
            
            # Render modal on top
            modal_manager.render(screen)
            
            # Debug info compacto
            if show_debug:
                debug_font = pygame.font.SysFont("Arial", 11)
                
                bubble_area = layout_areas['bubble_area']
                debug_x = bubble_area.left + 10
                debug_y = bubble_area.bottom - 45
                
                # Background
                debug_bg = pygame.Surface((600, 30), pygame.SRCALPHA)
                debug_bg.fill((0, 0, 0, 120))
                screen.blit(debug_bg, (debug_x - 5, debug_y - 5))
                
                # Info compacta
                mode_text = "FULLSCREEN" if is_fullscreen_detected else "WINDOWED"
                debug_text = f"🍎 {current_screen_size[0]}x{current_screen_size[1]} ({mode_text}) | FPS: {clock.get_fps():.1f} | F=Native Fullscreen | R=Redistribute"
                
                debug_surface = debug_font.render(debug_text, True, (150, 150, 150))
                screen.blit(debug_surface, (debug_x, debug_y))
            
            # Update display
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
        try:
            pygame.quit()
        except:
            pass
        print("Dashboard closed successfully!")

if __name__ == "__main__":
    main()