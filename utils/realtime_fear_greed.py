"""
Local Real-Time Fear & Greed Calculator (Cache-Only Version)
Replaces utils/realtime_fear_greed.py - Uses only cached data, no API calls
"""

import time
import math
import statistics
from threading import Thread, Lock
from collections import deque
from datetime import datetime, timedelta

class LocalRealTimeFearGreedCalculator:
    """
    Calculates Fear & Greed Index using only cached crypto data
    NO EXTERNAL API CALLS - prevents rate limiting
    """
    
    def __init__(self):
        self.data_lock = Lock()
        self.running = False
        
        # Historical calculation storage (24h worth of calculations)
        self.historical_values = deque(maxlen=1440)  # 24h of minute data
        self.historical_market_data = deque(maxlen=1440)
        
        # Current calculated value
        self.current_value = 50
        self.current_label = "Neutral"
        self.last_calculation = time.time()
        
        # Calculation weights
        self.weights = {
            'market_breadth': 0.35,     # 35% - % of coins gaining
            'price_momentum': 0.25,     # 25% - Average price changes
            'volatility': 0.20,         # 20% - Market volatility
            'dominance_trend': 0.20     # 20% - BTC dominance changes
        }
        
        # Smoothing parameters
        self.smoothing_factor = 0.3
        self.max_change_per_update = 5
        
        print("🎯 Local Real-time F&G calculator initialized (cache-only)")
    
    def start_local_calculations(self):
        """Start local calculation loop using cached data only"""
        self.running = True
        
        # Start calculation thread that uses cached data
        Thread(target=self._local_calculation_loop, daemon=True).start()
        
        print("✅ Local F&G calculations started (no API calls)")
    
    def stop_local_calculations(self):
        """Stop local calculations"""
        self.running = False
        print("⏹️ Local F&G calculations stopped")
    
    def _local_calculation_loop(self):
        """Calculate F&G using only cached crypto data"""
        while self.running:
            try:
                # Get cached crypto data (no API calls)
                from data.crypto_api import get_crypto_data
                crypto_data = get_crypto_data()
                
                if crypto_data and len(crypto_data) >= 10:
                    self._calculate_fear_greed_from_cache(crypto_data)
                else:
                    print("⚠️ Insufficient cached crypto data for F&G calculation")
                
                # Calculate every minute
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Local F&G calculation error: {e}")
                time.sleep(60)
    
    def _calculate_fear_greed_from_cache(self, crypto_data):
        """Calculate Fear & Greed using cached market data only"""
        try:
            with self.data_lock:
                # Market metrics from cached data
                total_coins = len(crypto_data)
                
                # 1. Market Breadth (35%) - % of coins gaining
                gaining_coins = sum(1 for coin in crypto_data 
                                  if (coin.get('price_change_percentage_24h', 0) or 0) > 0)
                market_breadth = (gaining_coins / total_coins) * 100
                
                # 2. Price Momentum (25%) - Average 24h changes
                price_changes = [coin.get('price_change_percentage_24h', 0) or 0 
                               for coin in crypto_data]
                avg_change = statistics.mean(price_changes) if price_changes else 0
                
                # 3. Volatility (20%) - Standard deviation of changes
                volatility = statistics.stdev(price_changes) if len(price_changes) > 1 else 0
                
                # 4. BTC Dominance Trend (20%)
                btc_data = next((coin for coin in crypto_data 
                               if coin['symbol'].upper() == 'BTC'), None)
                total_market_cap = sum(coin.get('market_cap', 0) or 0 
                                     for coin in crypto_data[:100])
                current_btc_dominance = ((btc_data.get('market_cap', 0) / total_market_cap * 100) 
                                       if btc_data and total_market_cap > 0 else 50)
                
                # Store current market snapshot
                market_snapshot = {
                    'timestamp': time.time(),
                    'market_breadth': market_breadth,
                    'avg_change': avg_change,
                    'volatility': volatility,
                    'btc_dominance': current_btc_dominance
                }
                self.historical_market_data.append(market_snapshot)
                
                # Calculate component scores
                breadth_score = self._calculate_breadth_score(market_breadth)
                momentum_score = self._calculate_momentum_score(avg_change)
                volatility_score = self._calculate_volatility_score(volatility)
                dominance_score = self._calculate_dominance_score()
                
                # Weighted combination
                raw_fear_greed_value = (
                    breadth_score * self.weights['market_breadth'] +
                    momentum_score * self.weights['price_momentum'] +
                    volatility_score * self.weights['volatility'] +
                    dominance_score * self.weights['dominance_trend']
                )
                
                # Apply smoothing to prevent wild swings
                smoothed_value = self._apply_smoothing(raw_fear_greed_value)
                
                # Update current values
                self.current_value = max(0, min(100, smoothed_value))
                self.current_label = self._get_label_for_value(self.current_value)
                self.last_calculation = time.time()
                
                # Store in history
                self.historical_values.append({
                    'timestamp': time.time(),
                    'value': self.current_value,
                    'label': self.current_label,
                    'components': {
                        'breadth': breadth_score,
                        'momentum': momentum_score,
                        'volatility': volatility_score,
                        'dominance': dominance_score
                    }
                })
                
                print(f"🎯 Local F&G: {self.current_value:.1f} ({self.current_label}) "
                      f"[B:{breadth_score:.0f} M:{momentum_score:.0f} V:{volatility_score:.0f} D:{dominance_score:.0f}]")
                
        except Exception as e:
            print(f"❌ Error in local F&G calculation: {e}")
    
    def _calculate_breadth_score(self, market_breadth):
        """Calculate market breadth score (0-100)"""
        # Market breadth directly maps to 0-100 scale
        return max(0, min(100, market_breadth))
    
    def _calculate_momentum_score(self, avg_change):
        """Calculate price momentum score (0-100)"""
        # -10% to +10% change maps to 0-100 scale
        # Neutral (0% change) = 50
        score = 50 + (avg_change * 2.5)  # Each 1% = 2.5 points
        return max(0, min(100, score))
    
    def _calculate_volatility_score(self, volatility):
        """Calculate volatility score (0-100) - lower volatility = higher score"""
        # Lower volatility indicates more confidence (greed)
        # 0-10% volatility maps to 100-0 score
        score = max(0, 100 - (volatility * 10))
        return max(0, min(100, score))
    
    def _calculate_dominance_score(self):
        """Calculate BTC dominance trend score (0-100)"""
        if len(self.historical_market_data) < 10:
            return 50  # Neutral if not enough data
        
        # Compare recent dominance vs historical
        recent_data = list(self.historical_market_data)[-10:]
        older_data = list(self.historical_market_data)[-60:-10] if len(self.historical_market_data) >= 60 else recent_data
        
        recent_dominance = statistics.mean([d['btc_dominance'] for d in recent_data])
        older_dominance = statistics.mean([d['btc_dominance'] for d in older_data])
        
        # Rising dominance = more fear, falling = more greed
        dominance_change = recent_dominance - older_dominance
        
        # -5% to +5% dominance change maps to 100-0 scale
        score = 50 - (dominance_change * 10)
        return max(0, min(100, score))
    
    def _apply_smoothing(self, new_value):
        """Apply smoothing to prevent sudden value changes"""
        if abs(new_value - self.current_value) > self.max_change_per_update:
            # Large change - apply smoothing
            change_direction = 1 if new_value > self.current_value else -1
            max_change = self.max_change_per_update * change_direction
            smoothed = self.current_value + max_change
        else:
            # Small change - use weighted average
            smoothed = (self.current_value * (1 - self.smoothing_factor) + 
                       new_value * self.smoothing_factor)
        
        return smoothed
    
    def _get_label_for_value(self, value):
        """Get text label for numerical value"""
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
    
    def get_current_value(self):
        """Get current Fear & Greed value"""
        return round(self.current_value)
    
    def get_current_label(self):
        """Get current Fear & Greed label"""
        return self.current_label
    
    def get_data_age(self):
        """Get age of last calculation in seconds"""
        return time.time() - self.last_calculation
    
    def is_data_ready(self):
        """Check if calculator has enough data"""
        return len(self.historical_values) >= 5  # At least 5 minutes of data
    
    def get_trend_analysis(self):
        """Get trend analysis over different timeframes"""
        if len(self.historical_values) < 60:
            return {'1h': 0, '4h': 0, '24h': 0}
        
        current_value = self.current_value
        
        # 1 hour ago
        hour_ago_values = [v['value'] for v in self.historical_values if 
                          time.time() - v['timestamp'] <= 3600]
        hour_ago_avg = statistics.mean(hour_ago_values[-60:]) if len(hour_ago_values) >= 60 else current_value
        
        # 4 hours ago
        four_hour_ago_values = [v['value'] for v in self.historical_values if 
                               time.time() - v['timestamp'] <= 14400]
        four_hour_ago_avg = statistics.mean(four_hour_ago_values[-240:]) if len(four_hour_ago_values) >= 240 else current_value
        
        # 24 hours ago
        day_ago_values = [v['value'] for v in self.historical_values if 
                         time.time() - v['timestamp'] <= 86400]
        day_ago_avg = statistics.mean(day_ago_values) if day_ago_values else current_value
        
        return {
            '1h': current_value - hour_ago_avg,
            '4h': current_value - four_hour_ago_avg,
            '24h': current_value - day_ago_avg
        }
    
    def get_volatility_analysis(self):
        """Get volatility analysis of F&G values"""
        if len(self.historical_values) < 60:
            return {'current': 0, 'trend': 'stable'}
        
        recent_values = [v['value'] for v in self.historical_values[-60:]]
        volatility = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
        
        # Classify volatility
        if volatility < 3:
            trend = 'very_stable'
        elif volatility < 6:
            trend = 'stable'
        elif volatility < 10:
            trend = 'moderate'
        elif volatility < 15:
            trend = 'volatile'
        else:
            trend = 'very_volatile'
        
        return {'current': volatility, 'trend': trend}


# Global local calculator instance
local_realtime_fear_greed = LocalRealTimeFearGreedCalculator()


def update_fear_greed_with_local_calculation(fear_greed_data):
    """
    Update fear_greed_data with local calculation while keeping API historical data
    """
    if local_realtime_fear_greed.is_data_ready():
        # Use local real-time calculation for current value
        fear_greed_data['value'] = local_realtime_fear_greed.get_current_value()
        fear_greed_data['label'] = local_realtime_fear_greed.get_current_label()
        fear_greed_data['is_realtime'] = True
        fear_greed_data['data_age'] = local_realtime_fear_greed.get_data_age()
        
        # Add trend analysis
        trends = local_realtime_fear_greed.get_trend_analysis()
        fear_greed_data['trends'] = trends
        
        # Add volatility info
        volatility = local_realtime_fear_greed.get_volatility_analysis()
        fear_greed_data['volatility'] = volatility
        
    else:
        # Fallback if not enough local data
        fear_greed_data['is_realtime'] = False
    
    return fear_greed_data


def start_local_realtime_fear_greed():
    """Start local real-time Fear & Greed calculation (no API calls)"""
    local_realtime_fear_greed.start_local_calculations()


def stop_local_realtime_fear_greed():
    """Stop local real-time Fear & Greed calculation"""
    local_realtime_fear_greed.stop_local_calculations()


def get_local_fear_greed_debug_info():
    """Get debug information about local F&G calculation"""
    return {
        'current_value': local_realtime_fear_greed.get_current_value(),
        'current_label': local_realtime_fear_greed.get_current_label(),
        'data_age': local_realtime_fear_greed.get_data_age(),
        'is_ready': local_realtime_fear_greed.is_data_ready(),
        'historical_data_points': len(local_realtime_fear_greed.historical_values),
        'market_data_points': len(local_realtime_fear_greed.historical_market_data),
        'trends': local_realtime_fear_greed.get_trend_analysis(),
        'volatility': local_realtime_fear_greed.get_volatility_analysis()
    }