"""
Data caching system
"""

import pickle
import time
import os
from threading import Lock

class ChartDataCache:
    """Cache system for chart data"""
    
    def __init__(self, cache_duration=600):
        self.cache_duration = cache_duration
        self.cache = {}
        self.cache_file = "cache/chart_cache.pkl"
        self.lock = Lock()
        self.load_cache()
    
    def get_cache_key(self, coin_id, timeframe):
        return f"{coin_id}_{timeframe}"
    
    def get(self, coin_id, timeframe):
        """Get cached data if valid"""
        with self.lock:
            key = self.get_cache_key(coin_id, timeframe)
            
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_duration:
                    return data
                else:
                    del self.cache[key]
            
            return None
    
    def set(self, coin_id, timeframe, data):
        """Cache data"""
        with self.lock:
            key = self.get_cache_key(coin_id, timeframe)
            self.cache[key] = (data, time.time())
            self.save_cache()
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            os.makedirs("cache", exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}

# Global cache instance
chart_cache = ChartDataCache(cache_duration=600)