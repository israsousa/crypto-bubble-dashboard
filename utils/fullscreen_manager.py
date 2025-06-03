"""
Fullscreen Manager - Gerenciamento otimizado de fullscreen
"""

import pygame
import time
from typing import Tuple, Optional, Callable
from config.settings import FULLSCREEN_CONFIG, update_settings_for_screen_size

class FullscreenManager:
    """
    Gerenciador otimizado e robusto para transições de fullscreen
    
    Características:
    - Transições suaves entre modos
    - Preservação do estado da janela
    - Callback system para componentes
    - Detecção automática de capacidades do sistema
    - Fallback para sistemas que não suportam fullscreen nativo
    """
    
    def __init__(self, initial_size: Tuple[int, int] = None):
        self.is_fullscreen = False
        self.windowed_size = initial_size or FULLSCREEN_CONFIG['windowed_size']
        self.desktop_size = FULLSCREEN_CONFIG['desktop_size']
        self.min_size = FULLSCREEN_CONFIG['min_windowed_size']
        
        self.screen: Optional[pygame.Surface] = None
        self.last_transition_time = 0
        self.transition_cooldown = 0.5  # Previne transições muito rápidas
        
        # Callbacks para notificar componentes sobre mudanças
        self.size_change_callbacks: list[Callable] = []
        self.mode_change_callbacks: list[Callable] = []
        
        # Estado de debug
        self.transition_history = []
        self.error_count = 0
        
        print("🖥️ FullscreenManager inicializado")
        print(f"   Desktop: {self.desktop_size}")
        print(f"   Windowed: {self.windowed_size}")
    
    def initialize_display(self) -> pygame.Surface:
        """Inicializa o display em modo janela"""
        try:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            pygame.display.set_caption("Crypto Bubble Live - Enhanced Design")
            
            # Atualiza configurações para o tamanho inicial
            update_settings_for_screen_size(self.windowed_size)
            
            print(f"✅ Display inicializado: {self.windowed_size}")
            return self.screen
            
        except pygame.error as e:
            print(f"❌ Erro ao inicializar display: {e}")
            # Fallback para tamanho mínimo
            self.windowed_size = self.min_size
            self.screen = pygame.display.set_mode(self.min_size, pygame.RESIZABLE)
            return self.screen
    
    def can_transition(self) -> bool:
        """Verifica se pode fazer transição (cooldown)"""
        return time.time() - self.last_transition_time > self.transition_cooldown
    
    def toggle_fullscreen(self) -> bool:
        """
        Alterna entre fullscreen e janela
        
        Returns:
            bool: True se a transição foi bem-sucedida
        """
        if not self.can_transition():
            print("⏳ Transição em cooldown, aguarde...")
            return False
        
        old_mode = "fullscreen" if self.is_fullscreen else "windowed"
        
        try:
            if self.is_fullscreen:
                success = self._exit_fullscreen()
            else:
                success = self._enter_fullscreen()
            
            if success:
                self.last_transition_time = time.time()
                new_mode = "fullscreen" if self.is_fullscreen else "windowed"
                
                # Registra transição
                self.transition_history.append({
                    'time': time.time(),
                    'from': old_mode,
                    'to': new_mode,
                    'success': True
                })
                
                # Notifica callbacks sobre mudança de modo
                self._notify_mode_change()
                
                print(f"✅ Transição {old_mode} → {new_mode} bem-sucedida")
                return True
            else:
                self.error_count += 1
                print(f"❌ Falha na transição {old_mode} → {'fullscreen' if not self.is_fullscreen else 'windowed'}")
                return False
                
        except Exception as e:
            self.error_count += 1
            print(f"❌ Erro na transição fullscreen: {e}")
            return False
    
    def _enter_fullscreen(self) -> bool:
        """Entra em modo fullscreen"""
        try:
            # Salva o tamanho atual da janela se não estiver em fullscreen
            if not self.is_fullscreen:
                current_size = self.screen.get_size()
                if current_size != self.desktop_size:  # Só salva se não for desktop size
                    self.windowed_size = current_size
            
            # Tenta fullscreen nativo primeiro
            self.screen = pygame.display.set_mode(self.desktop_size, pygame.FULLSCREEN)
            self.is_fullscreen = True
            
            # Atualiza configurações para fullscreen
            update_settings_for_screen_size(self.desktop_size)
            self._notify_size_change(self.desktop_size)
            
            return True
            
        except pygame.error as e:
            print(f"⚠️ Fullscreen nativo falhou, tentando borderless: {e}")
            
            # Fallback: janela borderless do tamanho do desktop
            try:
                self.screen = pygame.display.set_mode(self.desktop_size, pygame.NOFRAME)
                self.is_fullscreen = True
                
                update_settings_for_screen_size(self.desktop_size)
                self._notify_size_change(self.desktop_size)
                
                print("✅ Usando modo borderless como fallback")
                return True
                
            except pygame.error as e2:
                print(f"❌ Fallback borderless também falhou: {e2}")
                return False
    
    def _exit_fullscreen(self) -> bool:
        """Sai do modo fullscreen"""
        try:
            # Volta para o tamanho de janela salvo
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            self.is_fullscreen = False
            
            # Atualiza configurações para modo janela
            update_settings_for_screen_size(self.windowed_size)
            self._notify_size_change(self.windowed_size)
            
            return True
            
        except pygame.error as e:
            print(f"❌ Erro ao sair do fullscreen: {e}")
            
            # Fallback para tamanho mínimo
            try:
                self.screen = pygame.display.set_mode(self.min_size, pygame.RESIZABLE)
                self.windowed_size = self.min_size
                self.is_fullscreen = False
                
                update_settings_for_screen_size(self.min_size)
                self._notify_size_change(self.min_size)
                
                print("⚠️ Fallback para tamanho mínimo")
                return True
                
            except pygame.error as e2:
                print(f"❌ Fallback crítico falhou: {e2}")
                return False
    
    def handle_window_resize(self, new_size: Tuple[int, int]) -> bool:
        """
        Lida com redimensionamento de janela (apenas em modo janela)
        
        Args:
            new_size: Novo tamanho da janela
            
        Returns:
            bool: True se o redimensionamento foi processado
        """
        if self.is_fullscreen:
            # Ignora resize events em fullscreen
            return False
        
        # Valida tamanho mínimo
        width, height = new_size
        min_width, min_height = self.min_size
        
        if width < min_width or height < min_height:
            new_size = (max(width, min_width), max(height, min_height))
        
        try:
            self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
            self.windowed_size = new_size
            
            # Atualiza configurações
            update_settings_for_screen_size(new_size)
            self._notify_size_change(new_size)
            
            print(f"📏 Janela redimensionada: {new_size}")
            return True
            
        except pygame.error as e:
            print(f"❌ Erro no redimensionamento: {e}")
            return False
    
    def add_size_change_callback(self, callback: Callable[[Tuple[int, int]], None]):
        """Adiciona callback para mudanças de tamanho"""
        self.size_change_callbacks.append(callback)
    
    def add_mode_change_callback(self, callback: Callable[[bool], None]):
        """Adiciona callback para mudanças de modo (fullscreen/windowed)"""
        self.mode_change_callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove um callback específico"""
        if callback in self.size_change_callbacks:
            self.size_change_callbacks.remove(callback)
        if callback in self.mode_change_callbacks:
            self.mode_change_callbacks.remove(callback)
    
    def _notify_size_change(self, new_size: Tuple[int, int]):
        """Notifica callbacks sobre mudança de tamanho"""
        for callback in self.size_change_callbacks:
            try:
                callback(new_size)
            except Exception as e:
                print(f"❌ Erro em callback de tamanho: {e}")
    
    def _notify_mode_change(self):
        """Notifica callbacks sobre mudança de modo"""
        for callback in self.mode_change_callbacks:
            try:
                callback(self.is_fullscreen)
            except Exception as e:
                print(f"❌ Erro em callback de modo: {e}")
    
    def get_current_size(self) -> Tuple[int, int]:
        """Retorna o tamanho atual da tela"""
        if self.screen:
            return self.screen.get_size()
        return self.windowed_size
    
    def get_current_mode(self) -> str:
        """Retorna o modo atual como string"""
        return "fullscreen" if self.is_fullscreen else "windowed"
    
    def is_fullscreen_active(self) -> bool:
        """Verifica se está em modo fullscreen"""
        return self.is_fullscreen
    
    def get_windowed_size(self) -> Tuple[int, int]:
        """Retorna o tamanho salvo da janela"""
        return self.windowed_size
    
    def get_desktop_size(self) -> Tuple[int, int]:
        """Retorna o tamanho do desktop"""
        return self.desktop_size
    
    def force_window_size(self, size: Tuple[int, int]) -> bool:
        """
        Força um tamanho específico para a janela (apenas em modo janela)
        
        Args:
            size: Tamanho desejado (width, height)
            
        Returns:
            bool: True se bem-sucedido
        """
        if self.is_fullscreen:
            print("⚠️ Não é possível redimensionar em fullscreen")
            return False
        
        return self.handle_window_resize(size)
    
    def get_aspect_ratio(self) -> float:
        """Retorna o aspect ratio atual"""
        width, height = self.get_current_size()
        return width / height if height > 0 else 1.0
    
    def is_ultra_wide(self) -> bool:
        """Verifica se está em uma tela ultra-wide (>21:9)"""
        return self.get_aspect_ratio() > 2.33
    
    def is_portrait(self) -> bool:
        """Verifica se está em orientação portrait"""
        return self.get_aspect_ratio() < 1.0
    
    def get_debug_info(self) -> dict:
        """Retorna informações de debug"""
        return {
            'current_mode': self.get_current_mode(),
            'current_size': self.get_current_size(),
            'windowed_size': self.windowed_size,
            'desktop_size': self.desktop_size,
            'aspect_ratio': round(self.get_aspect_ratio(), 2),
            'transition_count': len(self.transition_history),
            'error_count': self.error_count,
            'last_transition': self.last_transition_time,
            'callbacks_registered': {
                'size_change': len(self.size_change_callbacks),
                'mode_change': len(self.mode_change_callbacks)
            }
        }
    
    def optimize_for_screen(self) -> dict:
        """
        Otimiza configurações baseadas na tela atual
        
        Returns:
            dict: Configurações otimizadas
        """
        size = self.get_current_size()
        width, height = size
        total_pixels = width * height
        aspect_ratio = self.get_aspect_ratio()
        
        # Configurações baseadas na resolução
        if total_pixels >= 3840 * 2160:  # 4K+
            quality_preset = "ultra_high"
            bubble_count = 400
            physics_quality = "high"
        elif total_pixels >= 2560 * 1440:  # 1440p+
            quality_preset = "high"
            bubble_count = 500
            physics_quality = "high"
        elif total_pixels >= 1920 * 1080:  # 1080p
            quality_preset = "medium_high"
            bubble_count = 500
            physics_quality = "medium"
        else:  # Menor que 1080p
            quality_preset = "medium"
            bubble_count = 350
            physics_quality = "low"
        
        # Ajustes para ultra-wide
        if self.is_ultra_wide():
            bubble_count = int(bubble_count * 1.2)  # Mais bolhas em ultra-wide
        
        optimizations = {
            'screen_info': {
                'size': size,
                'total_pixels': total_pixels,
                'aspect_ratio': aspect_ratio,
                'is_ultra_wide': self.is_ultra_wide(),
                'is_portrait': self.is_portrait()
            },
            'performance': {
                'quality_preset': quality_preset,
                'max_bubbles': bubble_count,
                'physics_quality': physics_quality,
                'enable_effects': total_pixels <= 2560 * 1440,
                'chart_quality': "high" if total_pixels >= 1920 * 1080 else "medium"
            },
            'layout': {
                'use_compact_ui': width < 1400,
                'sidebar_width_ratio': 0.3 if width < 1600 else 0.25,
                'font_scale': max(0.8, min(1.3, width / 1920))
            }
        }
        
        return optimizations
    
    def auto_detect_best_mode(self) -> str:
        """
        Detecta automaticamente o melhor modo baseado no hardware
        
        Returns:
            str: "fullscreen" ou "windowed"
        """
        desktop_w, desktop_h = self.desktop_size
        total_pixels = desktop_w * desktop_h
        
        # Telas muito grandes podem ter melhor performance em janela
        if total_pixels > 4096 * 2160:  # Maior que 4K
            return "windowed"
        
        # Telas pequenas funcionam melhor em fullscreen
        if total_pixels < 1920 * 1080:
            return "fullscreen"
        
        # Para telas médias, depende do aspect ratio
        aspect_ratio = desktop_w / desktop_h
        if aspect_ratio > 2.5:  # Ultra-wide extremo
            return "windowed"
        
        return "fullscreen"  # Default para a maioria dos casos
    
    def suggest_optimal_windowed_size(self) -> Tuple[int, int]:
        """Sugere um tamanho ótimo para modo janela"""
        desktop_w, desktop_h = self.desktop_size
        
        # 85% do desktop, mas respeitando limites
        optimal_w = int(desktop_w * 0.85)
        optimal_h = int(desktop_h * 0.85)
        
        # Garante proporção 16:9 se possível
        target_ratio = 16 / 9
        current_ratio = optimal_w / optimal_h
        
        if current_ratio > target_ratio:
            optimal_w = int(optimal_h * target_ratio)
        else:
            optimal_h = int(optimal_w / target_ratio)
        
        # Aplica limites mínimos e máximos
        min_w, min_h = self.min_size
        optimal_w = max(min_w, min(optimal_w, desktop_w - 100))
        optimal_h = max(min_h, min(optimal_h, desktop_h - 100))
        
        return (optimal_w, optimal_h)
    
    def cleanup(self):
        """Limpa recursos do gerenciador"""
        self.size_change_callbacks.clear()
        self.mode_change_callbacks.clear()
        
        print("🧹 FullscreenManager limpo")
        
        # Log final de estatísticas
        if self.transition_history:
            successful_transitions = sum(1 for t in self.transition_history if t['success'])
            total_transitions = len(self.transition_history)
            success_rate = (successful_transitions / total_transitions) * 100
            
            print(f"📊 Estatísticas finais:")
            print(f"   Transições: {successful_transitions}/{total_transitions} ({success_rate:.1f}% sucesso)")
            print(f"   Erros: {self.error_count}")


class FullscreenHelper:
    """Classe auxiliar com funções utilitárias para fullscreen"""
    
    @staticmethod
    def detect_display_capabilities() -> dict:
        """Detecta capacidades do display"""
        pygame.init()
        
        capabilities = {
            'fullscreen_support': True,
            'resizable_support': True,
            'hardware_acceleration': False,
            'multiple_displays': False,
            'max_resolution': (0, 0),
            'supported_modes': []
        }
        
        try:
            # Testa suporte a fullscreen
            info = pygame.display.Info()
            capabilities['max_resolution'] = (info.current_w, info.current_h)
            
            # Testa diferentes modos
            modes = pygame.display.list_modes()
            if modes != -1:  # -1 significa todos os modos suportados
                capabilities['supported_modes'] = modes[:10]  # Primeiros 10 modos
            
            # Testa hardware acceleration (aproximado)
            test_surface = pygame.display.set_mode((800, 600), pygame.HWSURFACE)
            if test_surface.get_flags() & pygame.HWSURFACE:
                capabilities['hardware_acceleration'] = True
                
        except Exception as e:
            print(f"⚠️ Erro detectando capacidades: {e}")
            capabilities['fullscreen_support'] = False
        
        pygame.quit()
        return capabilities
    
    @staticmethod
    def get_recommended_settings(screen_size: Tuple[int, int]) -> dict:
        """Retorna configurações recomendadas para um tamanho de tela"""
        width, height = screen_size
        total_pixels = width * height
        
        settings = {
            'fps_target': 60,
            'vsync': True,
            'quality_level': 'medium',
            'enable_effects': True,
            'max_bubbles': 500
        }
        
        # Ajusta baseado na resolução
        if total_pixels >= 3840 * 2160:  # 4K+
            settings.update({
                'fps_target': 120,  # 4K pode rodar em FPS maior
                'quality_level': 'ultra',
                'max_bubbles': 400  # Menos bolhas para manter performance
            })
        elif total_pixels >= 2560 * 1440:  # 1440p
            settings.update({
                'fps_target': 75,
                'quality_level': 'high',
                'max_bubbles': 500
            })
        elif total_pixels < 1366 * 768:  # Baixa resolução
            settings.update({
                'fps_target': 60,
                'quality_level': 'low',
                'enable_effects': False,
                'max_bubbles': 300
            })
        
        return settings