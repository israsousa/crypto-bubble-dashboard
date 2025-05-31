"""
Cryptocurrency API data fetching and management
"""

import requests
import time
import datetime
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
    'last_updated': None
}

def fetch_crypto_data():
    """Fetch cryptocurrency data from CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": MAX_BUBBLES,
        "page": 1,
        "sparkline": "false"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched {len(data)} cryptocurrencies")
        return data
    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return []

def fetch_crypto_news():
    """Fetch cryptocurrency news"""
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('Data', [])[:10]
    except Exception as e:
        print(f"Error fetching crypto news: {e}")
        return []

def fetch_fear_greed_index():
    """Enhanced Fear & Greed Index fetching"""
    try:
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
        
        # Yesterday's data
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
        
        # Last week's data
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
            
            # Calculate 7-day trend
            week_values = [int(d["value"]) for d in fng_data[:8]]
            if len(week_values) >= 2:
                result['trend_7d'] = (week_values[0] - week_values[-1]) / 7
        
        # Last month's data
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
            
            # Calculate 30-day trend
            month_values = [int(d["value"]) for d in fng_data[:31]]
            if len(month_values) >= 2:
                result['trend_30d'] = (month_values[0] - month_values[-1]) / 30
        
        print(f"Successfully fetched Fear & Greed data: Current={current_value} ({current_label})")
        return result
        
    except Exception as e:
        print(f"Error fetching Fear & Greed Index: {e}")
        return None

def update_crypto_data():
    """Background thread to update cryptocurrency data"""
    global crypto_data
    
    while True:
        try:
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
                
                print(f"Updated crypto data: {len(new_data)} coins")
        except Exception as e:
            print(f"Error in crypto data update thread: {e}")
        
        sleep(UPDATE_INTERVAL)

def update_news_data():
    """Background thread to update news data"""
    global news_list
    
    while True:
        try:
            new_news = fetch_crypto_news()
            if new_news:
                with news_lock:
                    news_list = new_news
                
                if not loading_state['news_data']:
                    update_loading_state('news_data', True)
                    print("News data loaded successfully")
                
                print(f"Updated news: {len(new_news)} articles")
        except Exception as e:
            print(f"Error in news update thread: {e}")
        
        sleep(NEWS_UPDATE_INTERVAL)

def update_fear_greed():
    """Background thread to update Fear & Greed Index"""
    global fear_greed_data
    
    retry_count = 0
    max_retries = 3
    
    while True:
        try:
            print("Fetching Fear & Greed Index data...")
            data = fetch_fear_greed_index()
            
            if data:
                with fear_greed_lock:
                    fear_greed_data.update({
                        'value': data['current']['value'],
                        'label': data['current']['label'],
                        'timestamp': data['current']['timestamp'],
                        'yesterday': data['yesterday'],
                        'last_week': data['last_week'],
                        'last_month': data['last_month'],
                        'trend_7d': data['trend_7d'],
                        'trend_30d': data['trend_30d'],
                        'last_updated': time.time()
                    })
                
                if not loading_state['fear_greed_data']:
                    update_loading_state('fear_greed_data', True)
                    print("Fear & Greed Index data loaded successfully")
                
                retry_count = 0
                print(f"Fear & Greed Index updated: {data['current']['value']} ({data['current']['label']})")
            else:
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"Failed to fetch Fear & Greed data, retry {retry_count}/{max_retries}")
                    sleep(30)
                    continue
                else:
                    print("Max retries reached for Fear & Greed data")
                    retry_count = 0
            
            sleep(FEAR_GREED_UPDATE_INTERVAL)
            
        except Exception as e:
            print(f"Error in fear_greed update thread: {e}")
            retry_count += 1
            if retry_count <= max_retries:
                sleep(60)
            else:
                sleep(FEAR_GREED_UPDATE_INTERVAL)
                retry_count = 0

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