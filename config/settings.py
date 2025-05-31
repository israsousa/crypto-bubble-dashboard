"""
Configuration settings for Crypto Bubble Dashboard
"""

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
FPS = 60

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

# Colors
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
    'panel_bg': (25, 25, 30)
}

# File paths
LOGOS_DIR = "logos"
CACHE_FILE = "chart_cache.pkl"
DAILY_RANKS_FILE = "daily_ranks.json"

# Font sizes
FONT_SIZES = {
    'title': 22,
    'header': 18,
    'large': 16,
    'normal': 14,
    'small': 12,
    'tiny': 10
}

# Layout ratios
LAYOUT = {
    'bubble_width_ratio': 0.75,
    'bubble_height_ratio': 0.6,
    'news_width_ratio': 0.25,
    'news_height_ratio': 0.7,
    'fear_greed_height_ratio': 0.3
}

# Physics settings
PHYSICS = {
    'gravity': (0, 0),
    'damping': 0.95,
    'bubble_elasticity': 0.15,
    'bubble_friction': 0.95,
    'velocity_damping': 0.94,
    'max_velocity': 15.0
}

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