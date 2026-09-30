from engine.base import FraudRule, RuleResult
from config import settings
import math
from typing import List, Dict

class AmountAnomalyRule(FraudRule):
    @property
    def name(self) -> str:
        return 'amount_anomaly'
        
    @property
    def weight(self) -> float:
        return 0.35
        
    async def evaluate(self, transaction: Dict, history: List[Dict]) -> RuleResult:
        amount = transaction.get('amount', 0.0)
        
        if not history:
            if amount > 5000:
                score = min(100.0, (amount / 5000) * 50)
                return RuleResult(self.name, score, "Large amount with no history", True)
            return RuleResult(self.name, 0.0, "No history, normal amount", False)
            
        amounts = [tx.get('amount', 0.0) for tx in history]
        mean = sum(amounts) / len(amounts)
        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            if amount > mean * 2:
                return RuleResult(self.name, 80.0, "Amount significantly higher than constant history", True)
            return RuleResult(self.name, 0.0, "Amount matches constant history", False)
            
        deviation = (amount - mean) / std_dev
        
        if deviation > settings.AMOUNT_DEVIATION_THRESHOLD:
            score = min(100.0, deviation * 20)
            return RuleResult(self.name, score, f"Amount is {deviation:.2f} std devs above mean", True)
            
        return RuleResult(self.name, max(0.0, deviation * 10), "Normal amount", False)
