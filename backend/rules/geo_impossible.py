from engine.base import FraudRule, RuleResult
from config import settings
from datetime import datetime, timezone
import math
from typing import List, Dict

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

class GeoImpossibilityRule(FraudRule):
    @property
    def name(self) -> str:
        return 'geo_impossibility'
        
    @property
    def weight(self) -> float:
        return 0.30
        
    async def evaluate(self, transaction: Dict, history: List[Dict]) -> RuleResult:
        current_loc = transaction.get('sender_location')
        if not current_loc or not history:
            return RuleResult(self.name, 0.0, "Missing location data or history", False)
            
        try:
            cur_lat, cur_lon = map(float, current_loc.split(','))
        except ValueError:
            return RuleResult(self.name, 0.0, "Invalid location format", False)
            
        last_tx = next((tx for tx in history if tx.get('sender_location')), None)
        if not last_tx:
            return RuleResult(self.name, 0.0, "No prior location history", False)
            
        try:
            last_lat, last_lon = map(float, last_tx['sender_location'].split(','))
        except ValueError:
            return RuleResult(self.name, 0.0, "Invalid prior location format", False)
            
        distance = haversine(cur_lat, cur_lon, last_lat, last_lon)
        
        current_time = datetime.now(timezone.utc)
        last_time = last_tx['timestamp']
        if not last_time:
             return RuleResult(self.name, 0.0, "Missing timestamp in history", False)
        
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
             
        time_diff_hours = (current_time - last_time).total_seconds() / 3600.0
        
        if time_diff_hours <= 0:
            speed = float('inf')
        else:
            speed = distance / time_diff_hours
            
        if speed > settings.GEO_MAX_SPEED_KMH:
            return RuleResult(self.name, 100.0, f"Impossible speed: {speed:.2f} km/h", True)
            
        return RuleResult(self.name, 0.0, "Possible travel speed", False)
