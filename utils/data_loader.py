"""
Data loading and state management utilities
"""

import time
import json
import datetime
from threading import Lock, Event

# Global state management
data_lock = Lock()
news_lock = Lock()
fear_greed_lock = Lock()
rank_tracking_lock = Lock()
loading_lock = Lock()

# Loading state management
loading_state = {
    'crypto_data': False,
    'news_data': False,
    'fear_greed_data': False,
    'logos_started': False,
    'bubbles_ready': False
}

loading_complete = Event()

# Daily rank tracking
daily_rank_tracking = {}
daily_start_time = datetime.datetime.now().date()

def update_loading_state(component, status=True):
    """Update loading state for a component"""
    with loading_lock:
        loading_state[component] = status
        if (loading_state['crypto_data'] and 
            loading_state['news_data'] and 
            loading_state['fear_greed_data']):
            if not loading_complete.is_set():
                print("All critical data loaded!")
                loading_complete.set()

def save_daily_ranks():
    """Save daily rank data to file"""
    try:
        data = {
            'date': daily_start_time.isoformat(),
            'ranks': daily_rank_tracking
        }
        with open('cache/daily_ranks.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving daily ranks: {e}")

def load_daily_ranks():
    """Load daily rank data from file"""
    global daily_rank_tracking, daily_start_time
    
    try:
        import os
        if os.path.exists('cache/daily_ranks.json'):
            with open('cache/daily_ranks.json', 'r') as f:
                data = json.load(f)
            
            saved_date = datetime.datetime.fromisoformat(data['date']).date()
            current_date = datetime.datetime.now().date()
            
            if saved_date == current_date:
                daily_rank_tracking = data['ranks']
                daily_start_time = saved_date
                print(f"Loaded daily rank tracking for {saved_date}")
            else:
                daily_rank_tracking = {}
                daily_start_time = current_date
    except Exception as e:
        print(f"Error loading daily ranks: {e}")
        daily_rank_tracking = {}
        daily_start_time = datetime.datetime.now().date()
