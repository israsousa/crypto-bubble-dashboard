"""
Logo loading and caching utilities
"""

import os
import requests
from PIL import Image
import io

def download_logo(symbol, url):
    """Download and cache cryptocurrency logo"""
    os.makedirs("assets/logos", exist_ok=True)
    path = f"assets/logos/{symbol}.png"
    
    if os.path.exists(path):
        return path
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        img = img.convert("RGBA").resize((50, 50), Image.Resampling.LANCZOS)
        img.save(path)
        return path
    except Exception as e:
        print(f"Error downloading logo for {symbol}: {e}")
        return None

def preload_top_logos(crypto_data, limit=50):
    """Preload logos for top cryptocurrencies"""
    print(f"Preloading logos for top {limit} cryptocurrencies...")
    loaded_count = 0
    
    for coin in crypto_data[:limit]:
        symbol = coin['symbol'].lower()
        image_url = coin.get('image', '')
        
        if image_url and download_logo(symbol, image_url):
            loaded_count += 1
    
    print(f"Preloaded {loaded_count}/{limit} logos")
    from utils.data_loader import update_loading_state
    update_loading_state('logos_started', True)
