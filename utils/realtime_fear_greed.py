"""
Real-Time Fear & Greed Index Calculator
Calculates dynamic F&G index every minute using rolling 24h market data
"""

import time
import math
import statistics
from threading import Thread, Lock
from collections import deque
from datetime import datetime, timedelta
import requests

class RealTimeFearGreedCalculator:
    """
    Calculates Fear & Greed Index in real-time using simplified sentiment indicators
    """
    
    def __init__(self):
        self.data_lock = Lock()
        self.running = False
        
        # Rolling 24h data storage (1440 minutes)
        self.price_data = deque(maxlen=1440)  # 24h of minute data
        self.volume_data = deque(maxlen=1440)
        self.market_cap_data = deque(maxlen=1440)
        
        # Current real-time F&G value
        self.current_value = 50
        self.last_calculation = time.time()
        
        # Calculation weights (total = 100%)
        self.weights = {
            'price_momentum': 0.25,    # 25% - 24h price changes
            'volatility': 0.20,        # 20% - Price volatility 
            'volume_momentum': 0.20,   # 20% - Trading volume changes
            'market_dominance': 0.15,  # 15% - BTC dominance
            'market_breadth': 0.20     # 20% - % of coins gaining
        }
        
        print("🔄 Real-time Fear & Greed calculator initialized")
    
    def start_real_time_updates(self):
        """Start real-time data collection and calculation"""
        self.running = True
        
        # Start data collection thread
        Thread(target=self._data_collection_loop, daemon=True).start()
        
        # Start calculation thread  
        Thread(target=self._calculation_loop, daemon=True).start()
        
        print("✅ Real-time F&G updates started")
    
    def stop_real_time_updates(self):
        """Stop real-time updates"""
        self.running = False
        print("⏹️ Real-time F&G updates stopped")
    
    def _data_collection_loop(self):
        """Collect market data every minute"""
        while self.running:
            try:
                self._collect_market_snapshot()
                time.sleep(60)  # Collect every minute
            except Exception as e:
                print(f"⚠️ Data collection error: {e}")
                time.sleep(60)
    
    def _calculation_loop(self):
        """Calculate F&G index every minute"""
        while self.running:
            try:
                if len(self.price_data) >= 60:  # Need at least 1h of data
                    self._calculate_fear_greed_index()
                time.sleep(60)  # Calculate every minute
            except Exception as e:
                print(f"⚠️ Calculation error: {e}")
                time.sleep(60)
    
    def _collect_market_snapshot(self):
        """Collect current market snapshot"""
        try:
            # Get top 100 coins for broader market analysis
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc", 
                "per_page": 100,
                "page": 1,
                "sparkline": "false"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Calculate market metrics
            total_market_cap = sum(coin.get('market_cap', 0) or 0 for coin in data)
            total_volume = sum(coin.get('total_volume', 0) or 0 for coin in data)
            
            # Bitcoin dominance
            btc_data = next((coin for coin in data if coin['symbol'].upper() == 'BTC'), None)
            btc_dominance = (btc_data.get('market_cap', 0) / total_market_cap * 100) if btc_data and total_market_cap > 0 else 50
            
            # Market breadth (% gaining)
            gaining_coins = sum(1 for coin in data if (coin.get('price_change_percentage_24h', 0) or 0) > 0)
            market_breadth = (gaining_coins / len(data)) * 100 if data else 50
            
            # Average price change
            price_changes = [coin.get('price_change_percentage_24h', 0) or 0 for coin in data]
            avg_price_change = statistics.mean(price_changes) if price_changes else 0
            
            # Store data point
            with self.data_lock:
                self.price_data.append({
                    'timestamp': time.time(),
                    'avg_change': avg_price_change,
                    'btc_dominance': btc_dominance,
                    'market_breadth': market_breadth
                })
                
                self.volume_data.append({
                    'timestamp': time.time(),
                    'total_volume': total_volume
                })
                
                self.market_cap_data.append({
                    'timestamp': time.time(), 
                    'total_market_cap': total_market_cap
                })
            
            print(f"📊 Market snapshot: {avg_price_change:.1f}% avg change, {market_breadth:.1f}% gaining")
            
        except Exception as e:
            print(f"❌ Failed to collect market data: {e}")
    
    def _calculate_fear_greed_index(self):
        """Calculate Fear & Greed index using market sentiment indicators"""
        try:
            with self.data_lock:
                if len(self.price_data) < 60:
                    return
                
                # Get recent data for calculations
                recent_prices = list(self.price_data)[-60:]  # Last hour
                all_prices = list(self.price_data)  # All available data
                recent_volumes = list(self.volume_data)[-60:]
                
                # 1. Price Momentum (25%) - Recent vs 24h average
                momentum_score = self._calculate_momentum_score(recent_prices, all_prices)
                
                # 2. Volatility (20%) - Lower volatility = more greed
                volatility_score = self._calculate_volatility_score(all_prices)
                
                # 3. Volume Momentum (20%) - High volume = strong sentiment
                volume_score = self._calculate_volume_score(recent_volumes)
                
                # 4. Market Dominance (15%) - BTC dominance trends
                dominance_score = self._calculate_dominance_score(all_prices)
                
                # 5. Market Breadth (20%) - % of coins gaining
                breadth_score = self._calculate_breadth_score(recent_prices)
                
                # Weighted average
                fear_greed_value = (
                    momentum_score * self.weights['price_momentum'] +
                    volatility_score * self.weights['volatility'] + 
                    volume_score * self.weights['volume_momentum'] +
                    dominance_score * self.weights['market_dominance'] +
                    breadth_score * self.weights['market_breadth']
                )
                
                # Clamp between 0-100
                fear_greed_value = max(0, min(100, fear_greed_value))
                
                # Smooth the value (prevent wild swings)
                if abs(fear_greed_value - self.current_value) > 5:
                    # Large change - smooth it
                    self.current_value = self.current_value + (fear_greed_value - self.current_value) * 0.3
                else:
                    # Small change - use directly
                    self.current_value = fear_greed_value
                
                self.last_calculation = time.time()
                
                print(f"🎯 Real-time F&G: {self.current_value:.1f} (M:{momentum_score:.1f} V:{volatility_score:.1f} Vol:{volume_score:.1f} D:{dominance_score:.1f} B:{breadth_score:.1f})")
                
        except Exception as e:
            print(f"❌ F&G calculation error: {e}")
    
    def _calculate_momentum_score(self, recent_data, all_data):
        """Calculate price momentum score (0-100)"""
        if len(all_data) < 2:
            return 50
        
        # Compare recent average vs 24h average
        recent_avg = statistics.mean([d['avg_change'] for d in recent_data[-10:]])
        all_avg = statistics.mean([d['avg_change'] for d in all_data])
        
        # Convert to 0-100 scale
        momentum = recent_avg - all_avg
        # Normalize: -10% to +10% change maps to 0-100
        score = 50 + (momentum * 2.5)  # Each 1% = 2.5 points
        return max(0, min(100, score))
    
    def _calculate_volatility_score(self, price_data):
        """Calculate volatility score (0-100, lower vol = higher score)"""
        if len(price_data) < 10:
            return 50
        
        # Calculate price change volatility
        changes = [d['avg_change'] for d in price_data[-60:]]  # Last hour
        volatility = statistics.stdev(changes) if len(changes) > 1 else 0
        
        # Lower volatility = higher score (more greed)
        # Normalize: 0-5% volatility maps to 100-0
        score = 100 - (volatility * 20)
        return max(0, min(100, score))
    
    def _calculate_volume_score(self, volume_data):
        """Calculate volume momentum score (0-100)"""
        if len(volume_data) < 10:
            return 50
        
        # Compare recent vs historical volume
        recent_vol = statistics.mean([d['total_volume'] for d in volume_data[-10:]])
        historical_vol = statistics.mean([d['total_volume'] for d in volume_data[:-10]]) if len(volume_data) > 10 else recent_vol
        
        if historical_vol == 0:
            return 50
        
        # Volume ratio
        vol_ratio = recent_vol / historical_vol
        
        # Higher volume = higher score (stronger sentiment)
        # 50% to 200% volume ratio maps to 25-75 base score
        score = 25 + ((vol_ratio - 0.5) / 1.5) * 50
        return max(0, min(100, score))
    
    def _calculate_dominance_score(self, price_data):
        """Calculate BTC dominance score (0-100)"""
        if len(price_data) < 2:
            return 50
        
        # BTC dominance trend
        current_dom = price_data[-1]['btc_dominance']
        prev_dom = price_data[-10]['btc_dominance'] if len(price_data) >= 10 else current_dom
        
        dom_change = current_dom - prev_dom
        
        # Rising dominance = more fear, falling = more greed
        # -5% to +5% dominance change maps to 100-0
        score = 50 - (dom_change * 10)
        return max(0, min(100, score))
    
    def _calculate_breadth_score(self, price_data):
        """Calculate market breadth score (0-100)"""
        if not price_data:
            return 50
        
        # Recent market breadth (% gaining)
        recent_breadth = statistics.mean([d['market_breadth'] for d in price_data[-10:]])
        
        # 0-100% breadth maps directly to 0-100 score
        return max(0, min(100, recent_breadth))
    
    def get_current_value(self):
        """Get current real-time Fear & Greed value"""
        return round(self.current_value)
    
    def get_current_label(self):
        """Get current label for the value"""
        value = self.get_current_value()
        if value <= 25:
            return "Extreme Fear"
        elif value <= 45:
            return "Fear" 
        elif value <= 55:
            return "Neutral"
        elif value <= 75:
            return "Greed"
        else:
            return "Extreme Greed"
    
    def is_data_ready(self):
        """Check if enough data is available for calculation"""
        with self.data_lock:
            return len(self.price_data) >= 60  # At least 1 hour of data
    
    def get_data_age(self):
        """Get age of last calculation in seconds"""
        return time.time() - self.last_calculation


# Global real-time calculator instance
realtime_fear_greed = RealTimeFearGreedCalculator()


def update_fear_greed_with_realtime(fear_greed_data):
    """
    Update fear_greed_data with real-time value while keeping API historical data
    """
    if realtime_fear_greed.is_data_ready():
        # Use real-time value for current
        fear_greed_data['value'] = realtime_fear_greed.get_current_value()
        fear_greed_data['label'] = realtime_fear_greed.get_current_label()
        fear_greed_data['is_realtime'] = True
        fear_greed_data['data_age'] = realtime_fear_greed.get_data_age()
    else:
        # Fallback to API value
        fear_greed_data['is_realtime'] = False
    
    return fear_greed_data


def start_realtime_fear_greed():
    """Start real-time Fear & Greed calculation"""
    realtime_fear_greed.start_real_time_updates()


def stop_realtime_fear_greed():
    """Stop real-time Fear & Greed calculation"""
    realtime_fear_greed.stop_real_time_updates()