"""
Configuration settings for Crypto Bubble Dashboard
OTIMIZAÇÃO: Configurações melhoradas para suporte a fullscreen
"""

import pygame

# Detecta automaticamente a resolução do desktop
def get_optimal_dimensions():
    """Detecta as melhores dimensões baseadas no monitor"""
    pygame.init()
    info = pygame.display.Info()
    desktop_w, desktop_h = info.current_w, info.current_h
    pygame.quit()
    
    # Tamanho padrão da janela (80% do desktop para melhor experiência)
    windowed_w = int(desktop_w * 0.8)
    windowed_h = int(desktop_h * 0.8)
    
    # Garante tamanhos mínimos
    windowed_w = max(1280, windowed_w)
    windowed_h = max(720, windowed_h)
    
    return windowed_w, windowed_h, desktop_w, desktop_h

# Dimensões otimizadas
WINDOWED_WIDTH, WINDOWED_HEIGHT, DESKTOP_WIDTH, DESKTOP_HEIGHT = get_optimal_dimensions()

# Screen dimensions (valores padrão para janela)
WIDTH, HEIGHT = WINDOWED_WIDTH, WINDOWED_HEIGHT
FPS = 60

# Configurações de fullscreen
FULLSCREEN_CONFIG = {
    'desktop_size': (DESKTOP_WIDTH, DESKTOP_HEIGHT),
    'windowed_size': (WINDOWED_WIDTH, WINDOWED_HEIGHT),
    'min_windowed_size': (1280, 720),
    'transition_smoothing': True,
    'preserve_aspect_ratio': False
}

# Update intervals (in seconds)
UPDATE_INTERVAL = 30  # seconds to update coin data
NEWS_UPDATE_INTERVAL = 60  # seconds to update news
FEAR_GREED_UPDATE_INTERVAL = 1800  # 30 minutes for fear/greed index

# Bubble settings
MAX_BUBBLES = 500  # Maximum number of bubbles to display

# API Rate limiting
API_MAX_REQUESTS = 8
API_TIME_WINDOW = 60  # seconds

# Chart settings
CHART_CACHE_DURATION = 600  # 10 minutes

# Colors (otimizados para diferentes resoluções)
COLORS = {
    'background': (10, 10, 15),
    'bubble_area': (20, 20, 25),
    'border': (60, 60, 80),
    'positive': (50, 255, 100),
    'negative': (255, 50, 50),
    'neutral': (150, 150, 150),
    'text_primary': (255, 255, 255),
    'text_secondary': (180, 180, 180),
    'modal_bg': (25, 25, 30),
    'panel_bg': (25, 25, 30),
    'debug_bg': (0, 0, 0),  # Para overlay de debug
    'fullscreen_indicator': (100, 255, 100)  # Indicador de fullscreen
}

# File paths
LOGOS_DIR = "logos"
CACHE_FILE = "chart_cache.pkl"
DAILY_RANKS_FILE = "daily_ranks.json"

# Font sizes (responsivos baseados na resolução)
def get_responsive_font_sizes(screen_width):
    """Calcula tamanhos de fonte baseados na largura da tela"""
    # Base scale factor (1.0 para 1920px de largura)
    scale = screen_width / 1920.0
    scale = max(0.7, min(1.5, scale))  # Limita entre 70% e 150%
    
    return {
        'title': int(22 * scale),
        'header': int(15 * scale),
        'large': int(16 * scale),
        'normal': int(14 * scale),
        'small': int(12 * scale),
        'tiny': int(10 * scale),
        'debug': int(11 * scale)
    }

# Font sizes padrão
FONT_SIZES = get_responsive_font_sizes(WIDTH)

# Layout ratios (otimizados para diferentes aspectos)
def get_responsive_layout(screen_size):
    """Calcula layout responsivo baseado no tamanho da tela"""
    width, height = screen_size
    aspect_ratio = width / height
    
    # Ajusta ratios baseado no aspect ratio
    if aspect_ratio > 1.8:  # Telas ultra-wide
        bubble_width_ratio = 0.78
        news_width_ratio = 0.22
    elif aspect_ratio < 1.3:  # Telas mais quadradas/verticais
        bubble_width_ratio = 0.7
        news_width_ratio = 0.3
    else:  # Aspect ratio padrão (16:9, 16:10)
        bubble_width_ratio = 0.75
        news_width_ratio = 0.25
    
    return {
        'bubble_width_ratio': bubble_width_ratio,
        'bubble_height_ratio': 0.6,
        'news_width_ratio': news_width_ratio,
        'news_height_ratio': 0.7,
        'fear_greed_height_ratio': 0.3
    }

# Layout padrão
LAYOUT = get_responsive_layout((WIDTH, HEIGHT))

# Physics settings (independentes da resolução)
PHYSICS = {
    'gravity': (0, 0),
    'damping': 0.95,
    'bubble_elasticity': 0.15,
    'bubble_friction': 0.95,
    'velocity_damping': 0.94,
    'max_velocity': 15.0
}

# Performance settings baseadas na resolução
def get_performance_config(screen_size):
    """Configurações de performance baseadas na resolução"""
    width, height = screen_size
    total_pixels = width * height
    
    if total_pixels > 3840 * 2160:  # 4K+
        return {
            'max_bubbles': 400,  # Menos bolhas em 4K+
            'physics_substeps': 1,
            'chart_quality': 'high',
            'effect_quality': 'medium'
        }
    elif total_pixels > 1920 * 1080:  # 1440p+
        return {
            'max_bubbles': 500,
            'physics_substeps': 1,
            'chart_quality': 'high',
            'effect_quality': 'high'
        }
    else:  # 1080p e menor
        return {
            'max_bubbles': 500,
            'physics_substeps': 2,
            'chart_quality': 'medium',
            'effect_quality': 'high'
        }

# Performance config padrão
PERFORMANCE = get_performance_config((WIDTH, HEIGHT))

# Symbol to CoinGecko ID mapping
SYMBOL_TO_ID = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
    'XRP': 'ripple', 'ADA': 'cardano', 'DOGE': 'dogecoin',
    'SOL': 'solana', 'TRX': 'tron', 'DOT': 'polkadot',
    'MATIC': 'matic-network', 'LTC': 'litecoin', 'SHIB': 'shiba-inu',
    'AVAX': 'avalanche-2', 'UNI': 'uniswap', 'LINK': 'chainlink',
    'XLM': 'stellar', 'ATOM': 'cosmos', 'XMR': 'monero',
    'ETC': 'ethereum-classic', 'BCH': 'bitcoin-cash', 'NEAR': 'near',
    'APT': 'aptos', 'QNT': 'quant-network', 'STX': 'blockstack',
    'ICP': 'internet-computer', 'CRO': 'crypto-com-chain',
    'VET': 'vechain', 'ALGO': 'algorand', 'HBAR': 'hedera-hashgraph',
    'FIL': 'filecoin', 'LDO': 'lido-dao', 'OP': 'optimism'
}

# Funções utilitárias para atualização dinâmica
def update_settings_for_screen_size(screen_size):
    """Atualiza configurações globais baseadas no tamanho da tela"""
    global FONT_SIZES, LAYOUT, PERFORMANCE
    
    FONT_SIZES = get_responsive_font_sizes(screen_size[0])
    LAYOUT = get_responsive_layout(screen_size)
    PERFORMANCE = get_performance_config(screen_size)
    
    print(f"⚙️ Configurações atualizadas para {screen_size[0]}x{screen_size[1]}")
    print(f"   Font scale: {screen_size[0]/1920:.2f}")
    print(f"   Layout: {LAYOUT['bubble_width_ratio']:.2f}/{LAYOUT['news_width_ratio']:.2f}")
    print(f"   Performance: {PERFORMANCE['max_bubbles']} bubbles, {PERFORMANCE['chart_quality']} quality")

# Configurações de debug melhoradas
DEBUG_CONFIG = {
    'show_fps': True,
    'show_bubble_count': True,
    'show_screen_info': True,
    'show_performance_stats': True,
    'overlay_alpha': 120,
    'update_interval': 0.5  # segundos
}