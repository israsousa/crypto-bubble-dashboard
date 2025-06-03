"""
Modal de detalhes da criptomoeda com design futurístico
Interface sci-fi com gráficos interativos e animações fluidas
Versão standalone que funciona independentemente
"""

import pygame
import os
import time
import random
import datetime
import math
from threading import Thread
from typing import List, Tuple, Optional, Dict, Any

# Imports locais
from config.settings import COLORS, FONT_SIZES, SYMBOL_TO_ID
from utils.formatters import format_large_number, format_supply, format_price
from data.chart_data import HistoricalDataGenerator

class ParticleSystem:
    """Sistema de partículas para efeitos visuais"""
    
    def __init__(self):
        self.particles = []
    
    def add_particle(self, pos: Tuple[float, float], velocity: Tuple[float, float], 
                    color: Tuple[int, int, int], life: float = 1.0, size: float = 2.0):
        """Adiciona uma partícula ao sistema"""
        self.particles.append({
            'pos': list(pos),
            'vel': list(velocity),
            'color': color,
            'life': life,
            'max_life': life,
            'size': size,
            'birth_time': time.time()
        })
    
    def update(self, dt: float):
        """Atualiza todas as partículas"""
        current_time = time.time()
        
        for particle in self.particles[:]:
            # Atualiza posição
            particle['pos'][0] += particle['vel'][0] * dt
            particle['pos'][1] += particle['vel'][1] * dt
            
            # Atualiza vida
            age = current_time - particle['birth_time']
            particle['life'] = max(0, particle['max_life'] - age)
            
            # Remove partículas mortas
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def render(self, surface: pygame.Surface):
        """Renderiza todas as partículas"""
        for particle in self.particles:
            if particle['life'] > 0:
                life_ratio = particle['life'] / particle['max_life']
                alpha = int(255 * life_ratio)
                size = int(particle['size'] * life_ratio)
                
                if size > 0 and alpha > 0:
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color_with_alpha = (*particle['color'], alpha)
                    pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
                    
                    surface.blit(particle_surface, 
                               (particle['pos'][0] - size, particle['pos'][1] - size))

class DataTooltip:
    """Tooltip interativo para mostrar dados ao passar o mouse"""
    
    def __init__(self):
        self.visible = False
        self.position = (0, 0)
        self.data = {}
        self.animation_progress = 0
        self.target_progress = 0
    
    def show(self, pos: Tuple[int, int], data: Dict[str, Any]):
        """Mostra tooltip na posição especificada"""
        self.position = pos
        self.data = data
        self.visible = True
        self.target_progress = 1.0
    
    def hide(self):
        """Esconde tooltip"""
        self.target_progress = 0.0
    
    def update(self, dt: float):
        """Atualiza animação do tooltip"""
        if self.target_progress > self.animation_progress:
            self.animation_progress = min(1.0, self.animation_progress + dt * 8)
        else:
            self.animation_progress = max(0.0, self.animation_progress - dt * 8)
        
        if self.animation_progress <= 0:
            self.visible = False
    
    def render(self, surface: pygame.Surface):
        """Renderiza tooltip com animação"""
        if not self.visible or self.animation_progress <= 0:
            return
        
        font = pygame.font.SysFont("Consolas", 12, bold=True)
        small_font = pygame.font.SysFont("Consolas", 10)
        
        # Prepara textos
        lines = []
        if 'price' in self.data:
            lines.append(("Price:", f"${self.data['price']:.6f}", (100, 255, 255)))
        if 'time' in self.data:
            lines.append(("Time:", self.data['time'], (200, 200, 255)))
        if 'volume' in self.data:
            lines.append(("Volume:", f"${self.data['volume']:,.0f}", (255, 200, 100)))
        
        if not lines:
            return
        
        # Calcula dimensões
        max_width = 0
        total_height = 0
        line_height = 16
        
        for label, value, color in lines:
            text_width = font.size(f"{label} {value}")[0]
            max_width = max(max_width, text_width)
            total_height += line_height
        
        # Dimensões do tooltip
        padding = 12
        tooltip_width = max_width + padding * 2
        tooltip_height = total_height + padding * 2
        
        # Ajusta posição para não sair da tela
        x, y = self.position
        screen_rect = surface.get_rect()
        
        if x + tooltip_width > screen_rect.right:
            x = screen_rect.right - tooltip_width - 10
        if y + tooltip_height > screen_rect.bottom:
            y = screen_rect.bottom - tooltip_height - 10
        
        # Animação de escala
        scale = self.animation_progress
        scaled_width = int(tooltip_width * scale)
        scaled_height = int(tooltip_height * scale)
        
        if scaled_width <= 0 or scaled_height <= 0:
            return
        
        # Background com glow
        tooltip_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        # Background principal
        pygame.draw.rect(tooltip_surface, (10, 15, 25, 240), 
                        (0, 0, scaled_width, scaled_height), 
                        border_radius=6)
        pygame.draw.rect(tooltip_surface, (0, 255, 255, 180), 
                        (0, 0, scaled_width, scaled_height), 2, 
                        border_radius=6)
        
        # Renderiza texto se o tooltip está grande o suficiente
        if scale > 0.5:
            text_alpha = int(255 * (scale - 0.5) * 2)
            current_y = padding
            
            for label, value, color in lines:
                # Label
                label_surface = small_font.render(label, True, (180, 180, 180))
                label_surface.set_alpha(text_alpha)
                tooltip_surface.blit(label_surface, (padding, current_y))
                
                # Value
                value_surface = font.render(value, True, color)
                value_surface.set_alpha(text_alpha)
                value_x = padding + small_font.size(label)[0] + 5
                tooltip_surface.blit(value_surface, (value_x, current_y - 1))
                
                current_y += line_height
        
        surface.blit(tooltip_surface, (x, y))

class FuturisticChartRenderer:
    """Renderizador de gráficos futurístico simplificado"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.margin = 50
        self.chart_rect = pygame.Rect(
            self.margin, self.margin,
            width - 2 * self.margin, height - 2 * self.margin
        )
        
        # Sistemas visuais
        self.particle_system = ParticleSystem()
        self.tooltip = DataTooltip()
        
        # Estado de interação
        self.mouse_pos = (0, 0)
        self.animation_time = 0
        
        # Configurações de estilo
        self.primary_color = (0, 255, 255)  # Cyan
        self.accent_color = (100, 255, 100)  # Verde
        self.danger_color = (255, 50, 100)  # Vermelho
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Atualiza sistemas de animação"""
        self.animation_time += dt
        self.mouse_pos = mouse_pos
        
        self.particle_system.update(dt)
        self.tooltip.update(dt)
    
    def get_color_for_trend(self, change_percent: float) -> Tuple[int, int, int]:
        """Retorna cor baseada na tendência"""
        if change_percent > 0:
            return self.accent_color
        else:
            return self.danger_color
    
    def render_price_chart(self, data_points: List[Dict], symbol: str, 
                          timeframe_label: str) -> pygame.Surface:
        """Renderiza gráfico de preços futurístico"""
        if not data_points or len(data_points) < 2:
            return self.render_no_data_chart()
        
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Background escuro
        surface.fill((5, 8, 15))
        
        # Grade de fundo
        self.render_grid(surface)
        
        # Processa dados
        prices = [point['price'] for point in data_points]
        timestamps = [point['timestamp'] for point in data_points]
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.1
        
        # Determina cor baseada na performance
        first_price = prices[0]
        last_price = prices[-1]
        change_percent = ((last_price - first_price) / first_price) * 100
        line_color = self.get_color_for_trend(change_percent)
        
        # Calcula pontos do gráfico
        chart_points = []
        for i, price in enumerate(prices):
            x = self.chart_rect.left + (i / (len(prices) - 1)) * self.chart_rect.width
            y = self.chart_rect.bottom - ((price - min_price) / price_range) * self.chart_rect.height
            chart_points.append((int(x), int(y)))
        
        # Renderiza área preenchida
        if len(chart_points) >= 2:
            fill_points = chart_points.copy()
            fill_points.append((chart_points[-1][0], self.chart_rect.bottom))
            fill_points.append((chart_points[0][0], self.chart_rect.bottom))
            
            # Gradiente simples
            fill_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(fill_surface, (*line_color, 60), fill_points)
            surface.blit(fill_surface, (0, 0))
            
            # Linha principal
            pygame.draw.lines(surface, line_color, False, chart_points, 3)
        
        # Pontos interativos
        self.render_data_points(surface, chart_points, data_points, line_color)
        
        # Labels
        self.render_axis_labels(surface, min_price, max_price, timestamps)
        self.render_title(surface, symbol, timeframe_label, change_percent)
        
        return surface
    
    def render_grid(self, surface: pygame.Surface):
        """Renderiza grade de fundo"""
        grid_color = (0, 100, 100, 30)
        grid_size = 30
        
        # Linhas verticais
        for x in range(self.chart_rect.left, self.chart_rect.right, grid_size):
            pygame.draw.line(surface, grid_color[:3], 
                           (x, self.chart_rect.top), 
                           (x, self.chart_rect.bottom), 1)
        
        # Linhas horizontais
        for y in range(self.chart_rect.top, self.chart_rect.bottom, grid_size):
            pygame.draw.line(surface, grid_color[:3], 
                           (self.chart_rect.left, y), 
                           (self.chart_rect.right, y), 1)
    
    def render_data_points(self, surface: pygame.Surface, chart_points: List[Tuple[int, int]], 
                          data_points: List[Dict], color: Tuple[int, int, int]):
        """Renderiza pontos de dados com interatividade"""
        mouse_x, mouse_y = self.mouse_pos
        hover_radius = 20
        closest_point = None
        closest_distance = float('inf')
        
        # Encontra ponto mais próximo do mouse
        for i, (point, data) in enumerate(zip(chart_points, data_points)):
            x, y = point
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)
            
            if distance < hover_radius and distance < closest_distance:
                closest_distance = distance
                closest_point = (i, point, data)
        
        # Renderiza alguns pontos
        for i, (point, data) in enumerate(zip(chart_points, data_points)):
            if i % max(1, len(chart_points) // 15) == 0:  # Mostra apenas alguns pontos
                x, y = point
                is_hovered = (closest_point and closest_point[0] == i)
                
                if is_hovered:
                    # Ponto em hover
                    pygame.draw.circle(surface, (255, 255, 255), (x, y), 8)
                    pygame.draw.circle(surface, color, (x, y), 6)
                    
                    # Atualiza tooltip
                    tooltip_data = {
                        'price': data['price'],
                        'time': data['timestamp'].strftime("%H:%M"),
                        'volume': data.get('volume', 0)
                    }
                    self.tooltip.show((mouse_x + 20, mouse_y - 20), tooltip_data)
                else:
                    # Ponto normal
                    pygame.draw.circle(surface, (255, 255, 255), (x, y), 4)
                    pygame.draw.circle(surface, color, (x, y), 2)
        
        if not closest_point:
            self.tooltip.hide()
    
    def render_axis_labels(self, surface: pygame.Surface, min_price: float, 
                          max_price: float, timestamps: List):
        """Renderiza labels dos eixos"""
        font = pygame.font.SysFont("Consolas", 10)
        
        # Labels do eixo Y (preços)
        for i in range(5):
            price = min_price + (i / 4) * (max_price - min_price)
            y = self.chart_rect.bottom - (i / 4) * self.chart_rect.height
            
            price_text = format_price(price)
            text_surface = font.render(price_text, True, (150, 200, 255))
            surface.blit(text_surface, (5, y - text_surface.get_height() // 2))
        
        # Labels do eixo X (tempo)
        if len(timestamps) > 0:
            for i in range(4):
                if i < len(timestamps):
                    timestamp = timestamps[int(i * (len(timestamps) - 1) / 3)]
                    x = self.chart_rect.left + (i / 3) * self.chart_rect.width
                    
                    time_text = timestamp.strftime("%H:%M")
                    text_surface = font.render(time_text, True, (150, 200, 255))
                    surface.blit(text_surface, (x - text_surface.get_width() // 2, 
                                               self.chart_rect.bottom + 10))
    
    def render_title(self, surface: pygame.Surface, symbol: str, timeframe_label: str, 
                    change_percent: float):
        """Renderiza título"""
        title_font = pygame.font.SysFont("Consolas", 18, bold=True)
        
        # Título principal
        title_text = f"{symbol} - {timeframe_label}"
        title_surface = title_font.render(title_text, True, self.primary_color)
        
        title_x = (self.width - title_surface.get_width()) // 2
        title_y = 10
        
        surface.blit(title_surface, (title_x, title_y))
    
    def render_no_data_chart(self) -> pygame.Surface:
        """Renderiza placeholder quando não há dados"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill((5, 8, 15))
        
        # Mensagem
        font = pygame.font.SysFont("Consolas", 20, bold=True)
        text = "LOADING CHART DATA..."
        text_surface = font.render(text, True, (100, 200, 255))
        
        x = (self.width - text_surface.get_width()) // 2
        y = (self.height - text_surface.get_height()) // 2
        
        surface.blit(text_surface, (x, y))
        
        return surface
    
    def handle_mouse_move(self, pos: Tuple[int, int]):
        """Manipula movimento do mouse"""
        self.mouse_pos = pos
    
    def render_tooltip(self, surface: pygame.Surface):
        """Renderiza tooltip se visível"""
        self.tooltip.render(surface)

class HolographicButton:
    """Botão com design holográfico"""
    
    def __init__(self, rect: pygame.Rect, text: str, active: bool = False):
        self.rect = rect
        self.text = text
        self.active = active
        self.hover = False
        self.glow_intensity = 0.0
        
    def update(self, dt: float, mouse_pos: tuple):
        """Atualiza estado do botão"""
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Animação de glow
        if self.hover or self.active:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 6)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 4)
    
    def render(self, surface: pygame.Surface):
        """Renderiza botão holográfico"""
        # Cores baseadas no estado
        if self.active:
            base_color = (0, 255, 255)
            bg_color = (0, 40, 40)
        else:
            base_color = (100, 150, 200)
            bg_color = (20, 25, 35)
        
        # Background do botão
        btn_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (*bg_color, 200), 
                        (0, 0, self.rect.width, self.rect.height), 
                        border_radius=6)
        
        # Border
        pygame.draw.rect(btn_surface, base_color, 
                        (0, 0, self.rect.width, self.rect.height), 
                        2, border_radius=6)
        
        surface.blit(btn_surface, self.rect.topleft)
        
        # Texto
        font = pygame.font.SysFont("Consolas", 12, bold=True)
        text_color = (255, 255, 255) if self.active else (200, 200, 200)
        text_surface = font.render(self.text, True, text_color)
        
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class FuturisticCryptoModal:
    """Modal futurístico para detalhes da criptomoeda"""
    
    def __init__(self, coin_data: dict, screen_size: tuple):
        self.coin_data = coin_data
        self.screen_size = screen_size
        self.symbol = coin_data['symbol'].upper()
        self.is_active = False
        
        # Dimensões do modal
        self.width = int(screen_size[0] * 0.9)
        self.height = int(screen_size[1] * 0.9)
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        # Sistema de gráficos
        chart_width = self.width - 350
        chart_height = self.height - 200
        self.chart_renderer = FuturisticChartRenderer(chart_width, chart_height)
        
        # Gerador de dados
        self.data_generator = HistoricalDataGenerator()
        
        # Estado do modal
        self.selected_timeframe = "7d"
        self.chart_surface = None
        self.loading_chart = False
        self.animation_time = 0
        self.entrance_animation = 0
        
        # Timeframes
        self.timeframes = {
            "1d": {"label": "1D", "days": 1},
            "7d": {"label": "7D", "days": 7},
            "30d": {"label": "30D", "days": 30},
            "90d": {"label": "90D", "days": 90},
            "1y": {"label": "1Y", "days": 365}
        }
        
        # Botões
        self.buttons = {}
        self.create_buttons()
        
        # Estado de mouse
        self.mouse_pos = (0, 0)
        self.close_button_rect = None
        
        print(f"🚀 Futuristic modal created for {self.symbol}")
        
        # Gera gráfico inicial
        self.generate_chart()
    
    def create_buttons(self):
        """Cria botões para timeframes"""
        button_width = 60
        button_height = 35
        button_spacing = 10
        
        start_x = 50
        start_y = 120
        
        for i, (key, info) in enumerate(self.timeframes.items()):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, start_y, button_width, button_height)
            
            is_active = (key == self.selected_timeframe)
            self.buttons[key] = HolographicButton(button_rect, info['label'], is_active)
    
    def generate_chart(self):
        """Gera gráfico para o timeframe atual"""
        try:
            self.loading_chart = True
            
            timeframe_info = self.timeframes[self.selected_timeframe]
            current_price = self.coin_data.get('current_price', 1.0)
            
            print(f"📊 Generating chart for {self.symbol} ({timeframe_info['label']})")
            
            # Gera dados históricos
            data_points = self.data_generator.generate_realistic_data(
                current_price, 
                self.symbol, 
                timeframe_info['days']
            )
            
            # Renderiza gráfico
            self.chart_surface = self.chart_renderer.render_price_chart(
                data_points, 
                self.symbol, 
                timeframe_info['label']
            )
            
            print(f"✅ Chart generated for {self.symbol}")
            
        except Exception as e:
            print(f"❌ Error generating chart: {e}")
            self.chart_surface = self.chart_renderer.render_no_data_chart()
        
        self.loading_chart = False
    
    def handle_click(self, pos: tuple) -> bool:
        """Manipula cliques no modal"""
        if not self.is_active:
            return False
        
        # Verifica se clicou fora do modal
        modal_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not modal_rect.collidepoint(pos):
            self.close()
            return True
        
        # Botão de fechar
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close()
            return True
        
        # Botões de timeframe
        for timeframe, button in self.buttons.items():
            if button.rect.collidepoint(pos):
                if timeframe != self.selected_timeframe:
                    self.selected_timeframe = timeframe
                    
                    # Atualiza botões
                    for key, btn in self.buttons.items():
                        btn.active = (key == timeframe)
                    
                    print(f"🔄 Switching to {timeframe} timeframe")
                    self.generate_chart()
                return True
        
        return True
    
    def handle_mouse_move(self, pos: tuple):
        """Manipula movimento do mouse"""
        self.mouse_pos = pos
        
        # Posição relativa para o gráfico
        chart_x = self.x + 50
        chart_y = self.y + 170
        
        relative_pos = (pos[0] - chart_x, pos[1] - chart_y)
        self.chart_renderer.handle_mouse_move(relative_pos)
    
    def open(self):
        """Abre o modal"""
        self.is_active = True
        self.entrance_animation = 0
        print(f"🚀 Modal opened for {self.symbol}")
    
    def close(self):
        """Fecha o modal"""
        self.is_active = False
        print(f"❌ Modal closed for {self.symbol}")
    
    def update(self, dt: float):
        """Atualiza animações do modal"""
        if not self.is_active:
            return
        
        self.animation_time += dt
        
        # Animação de entrada
        if self.entrance_animation < 1.0:
            self.entrance_animation = min(1.0, self.entrance_animation + dt * 4)
        
        # Atualiza botões
        for button in self.buttons.values():
            # Posição relativa ao modal
            relative_mouse = (self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y)
            button.update(dt, relative_mouse)
        
        # Atualiza sistema de gráficos
        chart_mouse = (
            self.mouse_pos[0] - self.x - 50,
            self.mouse_pos[1] - self.y - 170
        )
        self.chart_renderer.update(dt, chart_mouse)
    
    def draw(self, surface: pygame.Surface):
        """Renderiza o modal completo"""
        if not self.is_active:
            return
        
        # Overlay escuro
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay_alpha = int(180 * self.entrance_animation)
        overlay.fill((0, 0, 0, overlay_alpha))
        surface.blit(overlay, (0, 0))
        
        # Escala de entrada
        scale = self.entrance_animation
        if scale <= 0:
            return
        
        # Superfície do modal
        modal_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Renderiza componentes
        self.render_background(modal_surface)
        self.render_header(modal_surface)
        self.render_timeframe_buttons(modal_surface)
        self.render_chart_area(modal_surface)
        self.render_stats_panel(modal_surface)
        self.render_close_button(modal_surface)
        
        # Aplica escala se necessário
        if scale < 1.0:
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            modal_surface = pygame.transform.scale(modal_surface, (scaled_width, scaled_height))
            
            # Centraliza
            scaled_x = self.x + (self.width - scaled_width) // 2
            scaled_y = self.y + (self.height - scaled_height) // 2
            surface.blit(modal_surface, (scaled_x, scaled_y))
        else:
            surface.blit(modal_surface, (self.x, self.y))
    
    def render_background(self, surface: pygame.Surface):
        """Renderiza background futurístico"""
        # Background principal
        pygame.draw.rect(surface, (8, 12, 20), (0, 0, self.width, self.height), 
                        border_radius=15)
        
        # Scan lines
        for y in range(0, self.height, 4):
            alpha = int(20 * (1 + math.sin(self.animation_time * 2 + y * 0.1)))
            if alpha > 0:
                scan_surface = pygame.Surface((self.width, 1), pygame.SRCALPHA)
                scan_surface.fill((0, 255, 255, alpha))
                surface.blit(scan_surface, (0, y))
        
        # Border
        pygame.draw.rect(surface, (0, 255, 255, 200), (0, 0, self.width, self.height), 
                        2, border_radius=15)
    
    def render_header(self, surface: pygame.Surface):
        """Renderiza cabeçalho"""
        # Logo placeholder
        logo_size = 50
        logo_x, logo_y = 30, 20
        
        logo_path = f"assets/logos/{self.symbol.lower()}.png"
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
                surface.blit(logo, (logo_x, logo_y))
            except:
                # Fallback
                pygame.draw.circle(surface, (0, 255, 255), 
                                 (logo_x + logo_size//2, logo_y + logo_size//2), 
                                 logo_size//2)
        else:
            # Fallback
            pygame.draw.circle(surface, (0, 255, 255), 
                             (logo_x + logo_size//2, logo_y + logo_size//2), 
                             logo_size//2)
        
        # Nome e símbolo
        name_font = pygame.font.SysFont("Consolas", 24, bold=True)
        symbol_font = pygame.font.SysFont("Consolas", 16)
        
        coin_name = self.coin_data.get('name', self.symbol)
        if len(coin_name) > 25:
            coin_name = coin_name[:25] + "..."
        
        name_surface = name_font.render(coin_name, True, (255, 255, 255))
        symbol_surface = symbol_font.render(f"[{self.symbol}]", True, (0, 255, 255))
        
        surface.blit(name_surface, (logo_x + logo_size + 20, logo_y + 5))
        surface.blit(symbol_surface, (logo_x + logo_size + 20, logo_y + 35))
        
        # Preço atual
        current_price = self.coin_data.get('current_price', 0)
        price_text = format_price(current_price)
        price_font = pygame.font.SysFont("Consolas", 28, bold=True)
        price_surface = price_font.render(price_text, True, (100, 255, 150))
        
        price_x = self.width - price_surface.get_width() - 150
        surface.blit(price_surface, (price_x, logo_y + 5))
        
        # Mudança 24h
        change_24h = self.coin_data.get('price_change_percentage_24h', 0) or 0
        change_color = (100, 255, 150) if change_24h >= 0 else (255, 100, 120)
        change_text = f"{change_24h:+.2f}%"
        
        change_font = pygame.font.SysFont("Consolas", 20, bold=True)
        change_surface = change_font.render(change_text, True, change_color)
        surface.blit(change_surface, (price_x, logo_y + 40))
    
    def render_timeframe_buttons(self, surface: pygame.Surface):
        """Renderiza botões de timeframe"""
        for button in self.buttons.values():
            button.render(surface)
    
    def render_chart_area(self, surface: pygame.Surface):
        """Renderiza área do gráfico"""
        chart_x, chart_y = 50, 170
        
        if self.loading_chart:
            # Loading
            loading_surface = self.chart_renderer.render_no_data_chart()
            surface.blit(loading_surface, (chart_x, chart_y))
        elif self.chart_surface:
            # Gráfico principal
            surface.blit(self.chart_surface, (chart_x, chart_y))
            
            # Tooltip
            self.chart_renderer.render_tooltip(surface)
    
    def render_stats_panel(self, surface: pygame.Surface):
        """Renderiza painel de estatísticas"""
        panel_x = self.width - 300
        panel_y = 80
        panel_width = 280
        panel_height = self.height - 160
        
        # Background do painel
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (5, 10, 20, 230), 
                        (0, 0, panel_width, panel_height), 
                        border_radius=10)
        pygame.draw.rect(panel_surface, (0, 255, 255, 150), 
                        (0, 0, panel_width, panel_height), 
                        2, border_radius=10)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Dados das estatísticas
        font_label = pygame.font.SysFont("Consolas", 11)
        font_value = pygame.font.SysFont("Consolas", 13, bold=True)
        
        stats = [
            ("MARKET CAP", format_large_number(self.coin_data.get('market_cap', 0))),
            ("VOLUME 24H", format_large_number(self.coin_data.get('total_volume', 0))),
            ("RANK", f"#{self.coin_data.get('market_cap_rank', 'N/A')}" 
                    if self.coin_data.get('market_cap_rank') != 'N/A' else 'N/A'),
            ("SUPPLY", format_supply(self.coin_data.get('circulating_supply', 0)))
        ]
        
        y_offset = panel_y + 20
        line_height = (panel_height - 40) // len(stats)
        
        for i, (label, value) in enumerate(stats):
            current_y = y_offset + i * line_height
            
            # Label
            label_surface = font_label.render(label, True, (100, 200, 255))
            surface.blit(label_surface, (panel_x + 15, current_y))
            
            # Value
            if "MARKET CAP" in label or "VOLUME" in label:
                value_color = (100, 255, 150)
            elif "RANK" in label:
                value_color = (255, 200, 100)
            else:
                value_color = (255, 255, 255)
            
            value_surface = font_value.render(str(value), True, value_color)
            surface.blit(value_surface, (panel_x + 15, current_y + 15))
    
    def render_close_button(self, surface: pygame.Surface):
        """Renderiza botão de fechar"""
        button_size = 40
        button_x = self.width - button_size - 20
        button_y = 20
        
        self.close_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Hover
        mouse_in_button = self.close_button_rect.collidepoint(
            self.mouse_pos[0] - self.x, self.mouse_pos[1] - self.y
        )
        
        # Background
        pygame.draw.circle(surface, (40, 20, 20), 
                         (button_x + button_size//2, button_y + button_size//2), 
                         button_size//2)
        
        # Border
        border_color = (255, 150, 150) if mouse_in_button else (255, 100, 100)
        pygame.draw.circle(surface, border_color, 
                         (button_x + button_size//2, button_y + button_size//2), 
                         button_size//2, 2)
        
        # X symbol
        center_x = button_x + button_size//2
        center_y = button_y + button_size//2
        line_len = button_size//4
        
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x - line_len, center_y - line_len),
                        (center_x + line_len, center_y + line_len), 3)
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x + line_len, center_y - line_len),
                        (center_x - line_len, center_y + line_len), 3)