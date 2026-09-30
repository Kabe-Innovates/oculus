from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RuleResult:
    rule_name: str
    score: float
    reason: str
    triggered: bool

class FraudRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def weight(self) -> float: ...
    
    @abstractmethod
    async def evaluate(self, transaction: Dict, history: List[Dict]) -> RuleResult: ...
