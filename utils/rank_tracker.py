"""
Cryptocurrency rank tracking utilities
"""

import time
import datetime
from threading import Lock
from utils.data_loader import daily_rank_tracking, daily_start_time, rank_tracking_lock, save_daily_ranks

def update_daily_rank_tracking(crypto_data):
    """Update daily rank tracking with current data"""
    global daily_rank_tracking, daily_start_time
    
    current_date = datetime.datetime.now().date()
    
    if current_date != daily_start_time:
        print(f"New day detected: {current_date}")
        daily_rank_tracking.clear()
        daily_start_time = current_date
    
    with rank_tracking_lock:
        for i, coin in enumerate(crypto_data):
            symbol = coin['symbol'].upper()
            current_rank = i + 1
            
            if symbol not in daily_rank_tracking:
                daily_rank_tracking[symbol] = {
                    'initial_rank': current_rank,
                    'current_rank': current_rank,
                    'last_updated': time.time()
                }
            else:
                daily_rank_tracking[symbol]['current_rank'] = current_rank
                daily_rank_tracking[symbol]['last_updated'] = time.time()
        
        save_daily_ranks()

def get_daily_rank_change(symbol):
    """Get daily rank change for a symbol"""
    with rank_tracking_lock:
        if symbol not in daily_rank_tracking:
            return 0, ""
        
        initial = daily_rank_tracking[symbol]['initial_rank']
        current = daily_rank_tracking[symbol]['current_rank']
        change = initial - current
        
        if change > 0:
            return change, f"↑{change}"
        elif change < 0:
            return change, f"↓{abs(change)}"
        else:
            return 0, "–"