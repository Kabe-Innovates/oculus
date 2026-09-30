from engine.base import FraudRule, RuleResult
from config import settings
from datetime import datetime, timezone
from typing import List, Dict

class VelocityRule(FraudRule):
    @property
    def name(self) -> str:
        return 'velocity_check'
        
    @property
    def weight(self) -> float:
        return 0.35
        
    async def evaluate(self, transaction: Dict, history: List[Dict]) -> RuleResult:
        now = datetime.now(timezone.utc)
        count = 0
        for tx in history:
            tx_time = tx.get('timestamp')
            if tx_time:
                # Ensure tx_time is timezone aware if comparing with now
                if tx_time.tzinfo is None:
                    tx_time = tx_time.replace(tzinfo=timezone.utc)
                if (now - tx_time).total_seconds() <= settings.VELOCITY_WINDOW_SECONDS:
                    count += 1
                    
        threshold = settings.VELOCITY_THRESHOLD
        if count > threshold:
            score = min(100.0, (count / threshold) * 100)
            triggered = True
        else:
            score = (count / threshold) * 50 if threshold > 0 else 0
            triggered = False
            
        return RuleResult(
            rule_name=self.name,
            score=score,
            reason=f"{count} transactions in the last {settings.VELOCITY_WINDOW_SECONDS} seconds.",
            triggered=triggered
        )
