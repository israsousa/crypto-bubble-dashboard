"""
Enhanced Cryptocurrency API with Intelligent Rate Limiting
Replaces data/crypto_api.py - Avoids 429 errors with smart caching
"""

import requests
import time
import datetime
import json
import os
from threading import Lock
from time import sleep

from config.settings import *
from utils.rate_limiter import rate_limiter
from utils.data_cache import chart_cache
from utils.data_loader import (
    loading_state, update_loading_state, loading_complete,
    data_lock, news_lock, fear_greed_lock
)

# Global data storage
crypto_data = []
news_list = []
fear_greed_data = {
    'value': 50,
    'label': "Neutral", 
    'timestamp': None,
    'yesterday': {'value': None, 'label': None, 'change': 0},
    'last_week': {'value': None, 'label': None, 'change': 0},
    'last_month': {'value': None, 'label': None, 'change': 0},
    'trend_7d': 0,
    'trend_30d': 0,
    'last_updated': None,
    'is_realtime': True,
    'data_age': 0
}

class SmartCacheManager:
    """Intelligent caching system that reduces API dependency"""
    
    def __init__(self):
        self.cache_dir = "cache"
        self.crypto_cache_file = f"{self.cache_dir}/crypto_data_cache.json"
        self.news_cache_file = f"{self.cache_dir}/news_data_cache.json"
        self.fg_cache_file = f"{self.cache_dir}/fear_greed_cache.json"
        
        # Rate limiting - much more conservative
        self.last_crypto_fetch = 0
        self.last_news_fetch = 0
        self.last_fg_fetch = 0
        
        # Minimum intervals (in seconds)
        self.crypto_interval = 600  # 10 minutes
        self.news_interval = 1800   # 30 minutes  
        self.fg_interval = 3600     # 1 hour
        
        # Daily refresh time (2:00 AM)
        self.daily_refresh_hour = 2
        self.last_daily_refresh = None
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def should_refresh_daily(self):
        """Check if we should do daily API refresh"""
        now = datetime.datetime.now()
        today = now.date()
        
        # Check if it's past 2 AM and we haven't refreshed today
        if (now.hour >= self.daily_refresh_hour and 
            (self.last_daily_refresh is None or self.last_daily_refresh < today)):
            return True
        return False
    
    def can_fetch_crypto(self, force_daily=False):
        """Check if we can fetch crypto data"""
        if force_daily:
            return True
        return time.time() - self.last_crypto_fetch > self.crypto_interval
    
    def can_fetch_news(self, force_daily=False):
        """Check if we can fetch news"""
        if force_daily:
            return True
        return time.time() - self.last_news_fetch > self.news_interval
    
    def can_fetch_fg(self, force_daily=False):
        """Check if we can fetch Fear & Greed"""
        if force_daily:
            return True
        return time.time() - self.last_fg_fetch > self.fg_interval
    
    def save_crypto_cache(self, data):
        """Save crypto data to cache"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            with open(self.crypto_cache_file, 'w') as f:
                json.dump(cache_data, f)
            self.last_crypto_fetch = time.time()
        except Exception as e:
            print(f"Error saving crypto cache: {e}")
    
    def load_crypto_cache(self):
        """Load crypto data from cache"""
        try:
            if os.path.exists(self.crypto_cache_file):
                with open(self.crypto_cache_file, 'r') as f:
                    cache_data = json.load(f)
                return cache_data.get('data', [])
        except Exception as e:
            print(f"Error loading crypto cache: {e}")
        return []
    
    def save_news_cache(self, data):
        """Save news data to cache"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            with open(self.news_cache_file, 'w') as f:
                json.dump(cache_data, f)
            self.last_news_fetch = time.time()
        except Exception as e:
            print(f"Error saving news cache: {e}")
    
    def load_news_cache(self):
        """Load news data from cache"""
        try:
            if os.path.exists(self.news_cache_file):
                with open(self.news_cache_file, 'r') as f:
                    cache_data = json.load(f)
                return cache_data.get('data', [])
        except Exception as e:
            print(f"Error loading news cache: {e}")
        return []
    
    def save_fg_cache(self, data):
        """Save Fear & Greed data to cache"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            with open(self.fg_cache_file, 'w') as f:
                json.dump(cache_data, f)
            self.last_fg_fetch = time.time()
        except Exception as e:
            print(f"Error saving F&G cache: {e}")
    
    def load_fg_cache(self):
        """Load Fear & Greed data from cache"""
        try:
            if os.path.exists(self.fg_cache_file):
                with open(self.fg_cache_file, 'r') as f:
                    cache_data = json.load(f)
                return cache_data.get('data', {})
        except Exception as e:
            print(f"Error loading F&G cache: {e}")
        return {}

# Global cache manager
cache_manager = SmartCacheManager()

class LocalFearGreedCalculator:
    """Calculate Fear & Greed Index using only cached data"""
    
    def __init__(self):
        self.base_value = 50
        self.last_calculation = time.time()
        
    def calculate_from_cached_data(self, crypto_data):
        """Calculate F&G using cached crypto data only"""
        if not crypto_data or len(crypto_data) < 10:
            return 50, "Neutral"
        
        try:
            # Market metrics from cached data
            total_coins = len(crypto_data)
            gaining_coins = sum(1 for coin in crypto_data 
                              if (coin.get('price_change_percentage_24h', 0) or 0) > 0)
            
            # Calculate indicators
            market_breadth = (gaining_coins / total_coins) * 100
            
            # Average 24h change
            changes = [coin.get('price_change_percentage_24h', 0) or 0 
                      for coin in crypto_data]
            avg_change = sum(changes) / len(changes) if changes else 0
            
            # Volume momentum (simplified)
            volumes = [coin.get('total_volume', 0) or 0 for coin in crypto_data[:50]]
            volume_momentum = sum(volumes) / len(volumes) if volumes else 0
            
            # Bitcoin dominance
            btc_data = next((coin for coin in crypto_data 
                           if coin['symbol'].upper() == 'BTC'), None)
            total_market_cap = sum(coin.get('market_cap', 0) or 0 
                                 for coin in crypto_data[:100])
            btc_dominance = ((btc_data.get('market_cap', 0) / total_market_cap * 100) 
                           if btc_data and total_market_cap > 0 else 50)
            
            # Calculate F&G score
            # Market breadth: 0-100% -> maps to score component
            breadth_score = market_breadth
            
            # Average change: -10% to +10% -> 0 to 100
            momentum_score = max(0, min(100, 50 + (avg_change * 2.5)))
            
            # BTC dominance: higher dominance = more fear
            dominance_score = max(0, min(100, 100 - btc_dominance))
            
            # Volume momentum (simplified)
            volume_score = min(100, max(0, (volume_momentum / 1e9) * 10))
            
            # Weighted average
            fear_greed_value = (
                breadth_score * 0.35 +      # 35% market breadth
                momentum_score * 0.30 +     # 30% price momentum
                dominance_score * 0.20 +    # 20% BTC dominance
                volume_score * 0.15         # 15% volume
            )
            
            # Smooth changes (prevent wild swings)
            if abs(fear_greed_value - self.base_value) > 3:
                self.base_value = self.base_value + (fear_greed_value - self.base_value) * 0.3
            else:
                self.base_value = fear_greed_value
            
            # Get label
            value = round(self.base_value)
            if value <= 25:
                label = "Extreme Fear"
            elif value <= 45:
                label = "Fear"
            elif value <= 55:
                label = "Neutral"
            elif value <= 75:
                label = "Greed"
            else:
                label = "Extreme Greed"
            
            self.last_calculation = time.time()
            
            print(f"🎯 Local F&G: {value} ({label}) - Breadth:{market_breadth:.1f}% Momentum:{avg_change:.1f}%")
            
            return value, label
            
        except Exception as e:
            print(f"Error calculating local F&G: {e}")
            return 50, "Neutral"

# Global local calculator
local_fg_calculator = LocalFearGreedCalculator()

def fetch_crypto_data():
    """Fetch cryptocurrency data with intelligent rate limiting"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": MAX_BUBBLES,
        "page": 1,
        "sparkline": "false"
    }
    
    try:
        print("📡 Fetching fresh crypto data from API...")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Successfully fetched {len(data)} cryptocurrencies")
        
        # Save to cache
        cache_manager.save_crypto_cache(data)
        
        return data
    except Exception as e:
        print(f"❌ Error fetching crypto data: {e}")
        print("🔄 Using cached data...")
        return cache_manager.load_crypto_cache()

def fetch_crypto_news():
    """Fetch cryptocurrency news with rate limiting"""
    try:
        print("📡 Fetching fresh news from API...")
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        news_data = data.get('Data', [])[:10]
        
        # Save to cache
        cache_manager.save_news_cache(news_data)
        
        return news_data
    except Exception as e:
        print(f"❌ Error fetching crypto news: {e}")
        print("🔄 Using cached news...")
        return cache_manager.load_news_cache()

def fetch_fear_greed_index():
    """Fetch Fear & Greed Index with rate limiting"""
    try:
        print("📡 Fetching Fear & Greed from API...")
        url = "https://api.alternative.me/fng/?limit=31"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data or len(data["data"]) == 0:
            print("No Fear & Greed data available")
            return None
        
        fng_data = data["data"]
        current = fng_data[0]
        current_value = int(current["value"])
        current_label = current["value_classification"]
        current_timestamp = current.get("timestamp")
        
        result = {
            'current': {
                'value': current_value,
                'label': current_label,
                'timestamp': current_timestamp
            },
            'yesterday': {'value': None, 'label': None, 'change': 0},
            'last_week': {'value': None, 'label': None, 'change': 0},
            'last_month': {'value': None, 'label': None, 'change': 0},
            'trend_7d': 0,
            'trend_30d': 0
        }
        
        # Process historical data
        if len(fng_data) > 1:
            yesterday = fng_data[1]
            yesterday_value = int(yesterday["value"])
            yesterday_label = yesterday["value_classification"]
            yesterday_change = current_value - yesterday_value
            
            result['yesterday'] = {
                'value': yesterday_value,
                'label': yesterday_label,
                'change': yesterday_change
            }
        
        if len(fng_data) > 7:
            last_week = fng_data[7]
            last_week_value = int(last_week["value"])
            last_week_label = last_week["value_classification"]
            last_week_change = current_value - last_week_value
            
            result['last_week'] = {
                'value': last_week_value,
                'label': last_week_label,
                'change': last_week_change
            }
            
            week_values = [int(d["value"]) for d in fng_data[:8]]
            if len(week_values) >= 2:
                result['trend_7d'] = (week_values[0] - week_values[-1]) / 7
        
        if len(fng_data) > 30:
            last_month = fng_data[30]
            last_month_value = int(last_month["value"])
            last_month_label = last_month["value_classification"]
            last_month_change = current_value - last_month_value
            
            result['last_month'] = {
                'value': last_month_value,
                'label': last_month_label,
                'change': last_month_change
            }
            
            month_values = [int(d["value"]) for d in fng_data[:31]]
            if len(month_values) >= 2:
                result['trend_30d'] = (month_values[0] - month_values[-1]) / 30
        
        print(f"✅ Fear & Greed fetched: {current_value} ({current_label})")
        
        # Save to cache
        cache_manager.save_fg_cache(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching Fear & Greed Index: {e}")
        print("🔄 Using cached F&G data...")
        cached = cache_manager.load_fg_cache()
        return cached if cached else None

def update_crypto_data():
    """Background thread to update cryptocurrency data with smart rate limiting"""
    global crypto_data
    
    # Load initial cached data
    cached_data = cache_manager.load_crypto_cache()
    if cached_data:
        with data_lock:
            crypto_data = cached_data
        print(f"🔄 Loaded {len(cached_data)} coins from cache")
        
        if not loading_state['crypto_data']:
            update_loading_state('crypto_data', True)
            
            # Start logo preloading
            from utils.logo_loader import preload_top_logos
            from threading import Thread
            Thread(target=preload_top_logos, args=(cached_data, 50), daemon=True).start()
    
    while True:
        try:
            # Check if we should do daily refresh
            force_daily = cache_manager.should_refresh_daily()
            
            if force_daily or cache_manager.can_fetch_crypto():
                new_data = fetch_crypto_data()
                if new_data:
                    with data_lock:
                        crypto_data = new_data
                    
                    # Update daily rank tracking
                    from utils.rank_tracker import update_daily_rank_tracking
                    update_daily_rank_tracking(new_data)
                    
                    if not loading_state['crypto_data']:
                        update_loading_state('crypto_data', True)
                        print("Cryptocurrency data loaded successfully")
                        
                        # Start logo preloading
                        from utils.logo_loader import preload_top_logos
                        from threading import Thread
                        Thread(target=preload_top_logos, args=(new_data, 50), daemon=True).start()
                    
                    if force_daily:
                        cache_manager.last_daily_refresh = datetime.datetime.now().date()
                        print("✅ Daily crypto data refresh completed")
                    
                    print(f"✅ Updated crypto data: {len(new_data)} coins")
                else:
                    print("⚠️ Using existing cached data")
            else:
                # Use local calculation for real-time updates
                if crypto_data:
                    print("🔄 Using cached crypto data for local updates")
                
        except Exception as e:
            print(f"❌ Error in crypto data update thread: {e}")
        
        # Sleep for a shorter interval to allow local updates
        sleep(60)  # Check every minute, but only fetch when allowed

def update_news_data():
    """Background thread to update news data with rate limiting"""
    global news_list
    
    # Load initial cached data
    cached_news = cache_manager.load_news_cache()
    if cached_news:
        with news_lock:
            news_list = cached_news
        print(f"🔄 Loaded {len(cached_news)} news articles from cache")
        
        if not loading_state['news_data']:
            update_loading_state('news_data', True)
    
    while True:
        try:
            force_daily = cache_manager.should_refresh_daily()
            
            if force_daily or cache_manager.can_fetch_news():
                new_news = fetch_crypto_news()
                if new_news:
                    with news_lock:
                        news_list = new_news
                    
                    if not loading_state['news_data']:
                        update_loading_state('news_data', True)
                        print("News data loaded successfully")
                    
                    print(f"✅ Updated news: {len(new_news)} articles")
                else:
                    print("⚠️ Using existing cached news")
        except Exception as e:
            print(f"❌ Error in news update thread: {e}")
        
        sleep(300)  # Check every 5 minutes

def update_fear_greed():
    """Background thread to update Fear & Greed Index with local calculation"""
    global fear_greed_data
    
    # Load initial cached historical data
    cached_fg = cache_manager.load_fg_cache()
    if cached_fg:
        with fear_greed_lock:
            fear_greed_data.update({
                'timestamp': cached_fg.get('current', {}).get('timestamp'),
                'yesterday': cached_fg.get('yesterday', {'value': None, 'label': None, 'change': 0}),
                'last_week': cached_fg.get('last_week', {'value': None, 'label': None, 'change': 0}),
                'last_month': cached_fg.get('last_month', {'value': None, 'label': None, 'change': 0}),
                'trend_7d': cached_fg.get('trend_7d', 0),
                'trend_30d': cached_fg.get('trend_30d', 0),
            })
        print("🔄 Loaded Fear & Greed historical data from cache")
        
        if not loading_state['fear_greed_data']:
            update_loading_state('fear_greed_data', True)
    
    while True:
        try:
            # Always calculate local F&G using cached crypto data
            current_crypto_data = get_crypto_data()
            if current_crypto_data:
                local_value, local_label = local_fg_calculator.calculate_from_cached_data(current_crypto_data)
                
                with fear_greed_lock:
                    fear_greed_data['value'] = local_value
                    fear_greed_data['label'] = local_label
                    fear_greed_data['is_realtime'] = True
                    fear_greed_data['data_age'] = time.time() - local_fg_calculator.last_calculation
                    fear_greed_data['last_updated'] = time.time()
            
            # Only fetch API data for historical comparison (much less frequently)
            force_daily = cache_manager.should_refresh_daily()
            if force_daily or cache_manager.can_fetch_fg():
                api_data = fetch_fear_greed_index()
                if api_data:
                    with fear_greed_lock:
                        # Keep local value but update historical data
                        fear_greed_data.update({
                            'timestamp': api_data['current']['timestamp'],
                            'yesterday': api_data['yesterday'],
                            'last_week': api_data['last_week'],
                            'last_month': api_data['last_month'],
                            'trend_7d': api_data['trend_7d'],
                            'trend_30d': api_data['trend_30d'],
                        })
                    
                    if force_daily:
                        print("✅ Daily F&G historical data refresh completed")
            
            if not loading_state['fear_greed_data']:
                update_loading_state('fear_greed_data', True)
                print("Fear & Greed Index data loaded successfully")
            
        except Exception as e:
            print(f"❌ Error in fear_greed update thread: {e}")
        
        # Update local F&G every minute, fetch API data much less frequently
        sleep(60)

def get_crypto_data():
    """Get current crypto data thread-safely"""
    with data_lock:
        return crypto_data.copy()

def get_news_data():
    """Get current news data thread-safely"""
    with news_lock:
        return news_list.copy()

def get_fear_greed_data():
    """Get current fear & greed data thread-safely"""
    with fear_greed_lock:
        return fear_greed_data.copy()