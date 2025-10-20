"""
GitHub Search Planner - Smart rate limit management and query sharding.

Handles GitHub API rate limits intelligently:
- Search API: 30 requests/min
- Code Search API: 10 requests/min  
- REST API: 5,000 requests/hour

Features:
- Query sharding by time windows (created:YYYY-MM-DD..YYYY-MM-DD)
- Rate limit monitoring via X-RateLimit-* headers
- Exponential backoff with jitter
- Progress indicators for long operations
- Automatic query splitting when results > 1000
"""

import time
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class RateLimitState:
    """Tracks rate limit state for a specific API endpoint."""
    limit: int = 0
    remaining: int = 0
    reset_time: float = 0
    last_request_time: float = 0
    requests_this_window: int = 0
    window_start: float = 0
    
    def update_from_headers(self, headers: Dict[str, str]):
        """Update state from X-RateLimit-* headers."""
        if 'X-RateLimit-Limit' in headers:
            self.limit = int(headers['X-RateLimit-Limit'])
        if 'X-RateLimit-Remaining' in headers:
            self.remaining = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            self.reset_time = float(headers['X-RateLimit-Reset'])
    
    def should_wait(self, safety_margin: int = 3) -> Tuple[bool, float]:
        """Check if we should wait before next request."""
        if self.remaining <= safety_margin:
            wait_time = max(0, self.reset_time - time.time())
            return True, wait_time
        return False, 0


@dataclass
class SearchPlanner:
    """Plans and executes GitHub searches with intelligent rate limit handling."""
    
    # Rate limit states
    search_state: RateLimitState = field(default_factory=RateLimitState)
    code_search_state: RateLimitState = field(default_factory=RateLimitState)
    rest_state: RateLimitState = field(default_factory=RateLimitState)
    
    # Configuration
    search_rpm: int = 28  # Stay under 30/min limit
    code_search_rpm: int = 8  # Stay under 10/min limit
    min_request_interval: float = 2.5  # Minimum seconds between requests
    
    def __post_init__(self):
        """Initialize rate limit windows."""
        now = time.time()
        self.search_state.window_start = now
        self.code_search_state.window_start = now
    
    def wait_if_needed(self, endpoint_type: str = "search") -> float:
        """
        Wait if necessary to respect rate limits.
        
        Args:
            endpoint_type: "search", "code_search", or "rest"
        
        Returns:
            Seconds waited
        """
        state = self._get_state(endpoint_type)
        rpm_limit = self._get_rpm_limit(endpoint_type)
        
        # Check if we need to wait based on headers
        should_wait, wait_time = state.should_wait()
        if should_wait:
            print(f"⏳ Rate limit reached for {endpoint_type}. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time + 1)  # +1s buffer
            return wait_time + 1
        
        # Check if we've hit our self-imposed RPM limit
        now = time.time()
        window_duration = now - state.window_start
        
        if window_duration >= 60:
            # Reset window
            state.requests_this_window = 0
            state.window_start = now
        elif state.requests_this_window >= rpm_limit:
            # Hit our RPM limit, wait for window to reset
            wait_time = 60 - window_duration + 1
            print(f"⏳ Self-imposed {endpoint_type} limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            state.requests_this_window = 0
            state.window_start = time.time()
            return wait_time
        
        # Enforce minimum interval between requests
        since_last = now - state.last_request_time
        if since_last < self.min_request_interval:
            wait_time = self.min_request_interval - since_last
            time.sleep(wait_time)
            return wait_time
        
        return 0
    
    def record_request(self, endpoint_type: str, headers: Optional[Dict[str, str]] = None):
        """Record that a request was made and update state."""
        state = self._get_state(endpoint_type)
        state.last_request_time = time.time()
        state.requests_this_window += 1
        
        if headers:
            state.update_from_headers(headers)
    
    def shard_query_by_time(self, base_query: str, days: int, 
                           max_results_per_shard: int = 800) -> List[str]:
        """
        Shard a query into time windows to avoid 1000-result GitHub limit.
        
        Args:
            base_query: Base search query (e.g., "topic:rust stars:>100")
            days: Number of days to look back
            max_results_per_shard: Target max results per shard (leave buffer under 1000)
        
        Returns:
            List of queries with created: date ranges
        """
        # Estimate how many shards we need based on expected results per day
        # This is a heuristic - we'll adjust if we hit limits
        estimated_results_per_day = 50  # Conservative estimate
        estimated_total = estimated_results_per_day * days
        
        if estimated_total <= max_results_per_shard:
            # Single query is fine
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            query = f"{base_query} created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            return [query]
        
        # Need to shard - split into time windows
        num_shards = math.ceil(estimated_total / max_results_per_shard)
        days_per_shard = max(1, days // num_shards)
        
        queries = []
        end_date = datetime.now()
        
        for i in range(num_shards):
            shard_end = end_date - timedelta(days=i * days_per_shard)
            shard_start = shard_end - timedelta(days=days_per_shard)
            
            if i == num_shards - 1:
                # Last shard - extend to cover remaining days
                shard_start = end_date - timedelta(days=days)
            
            query = f"{base_query} created:{shard_start.strftime('%Y-%m-%d')}..{shard_end.strftime('%Y-%m-%d')}"
            queries.append(query)
        
        return queries
    
    def estimate_search_time(self, num_queries: int, endpoint_type: str = "search") -> float:
        """Estimate how long a series of queries will take."""
        rpm = self._get_rpm_limit(endpoint_type)
        minutes_needed = num_queries / rpm
        return minutes_needed * 60
    
    def _get_state(self, endpoint_type: str) -> RateLimitState:
        """Get the rate limit state for an endpoint type."""
        if endpoint_type == "search":
            return self.search_state
        elif endpoint_type == "code_search":
            return self.code_search_state
        else:
            return self.rest_state
    
    def _get_rpm_limit(self, endpoint_type: str) -> int:
        """Get the RPM limit for an endpoint type."""
        if endpoint_type == "search":
            return self.search_rpm
        elif endpoint_type == "code_search":
            return self.code_search_rpm
        else:
            return 5000  # REST is per hour, not per minute
    
    def get_status(self) -> Dict[str, Dict]:
        """Get current status of all rate limits."""
        return {
            "search": {
                "remaining": self.search_state.remaining,
                "limit": self.search_state.limit,
                "reset_time": datetime.fromtimestamp(self.search_state.reset_time).isoformat() if self.search_state.reset_time else None,
                "requests_this_window": self.search_state.requests_this_window,
                "window_start": datetime.fromtimestamp(self.search_state.window_start).isoformat() if self.search_state.window_start else None
            },
            "code_search": {
                "remaining": self.code_search_state.remaining,
                "limit": self.code_search_state.limit,
                "reset_time": datetime.fromtimestamp(self.code_search_state.reset_time).isoformat() if self.code_search_state.reset_time else None,
                "requests_this_window": self.code_search_state.requests_this_window,
                "window_start": datetime.fromtimestamp(self.code_search_state.window_start).isoformat() if self.code_search_state.window_start else None
            },
            "rest": {
                "remaining": self.rest_state.remaining,
                "limit": self.rest_state.limit,
                "reset_time": datetime.fromtimestamp(self.rest_state.reset_time).isoformat() if self.rest_state.reset_time else None,
                "requests_this_window": self.rest_state.requests_this_window
            }
        }


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff with jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
    
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.1)  # 10% jitter
    return delay + jitter
