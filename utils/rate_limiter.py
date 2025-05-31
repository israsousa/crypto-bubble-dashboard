"""
API Rate limiting utilities
"""

import time
from threading import Lock

class APIRateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests=8, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = Lock()
    
    def can_make_request(self):
        """Check if we can make a request"""
        with self.lock:
            now = time.time()
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def wait_time(self):
        """Get wait time until next request is allowed"""
        with self.lock:
            if not self.requests:
                return 0
            
            oldest_request = min(self.requests)
            wait_time = self.time_window - (time.time() - oldest_request)
            return max(0, wait_time)

# Global rate limiter instance
rate_limiter = APIRateLimiter(max_requests=8, time_window=60)