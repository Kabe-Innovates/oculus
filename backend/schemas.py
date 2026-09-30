from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: float
    currency: str = 'USD'
    sender_id: str
    receiver_id: str
    sender_location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None

class RuleResultSchema(BaseModel):
    rule_name: str
    score: float
    reason: str
    triggered: bool

class TransactionResponse(BaseModel):
    id: str
    amount: float
    currency: str
    sender_id: str
    receiver_id: str
    sender_location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    risk_score: Optional[float] = None
    verdict: Optional[str] = None
    status: str
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rule_results: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

class ReviewRequest(BaseModel):
    status: str
    reviewer_notes: Optional[str] = None

class StatsResponse(BaseModel):
    total_transactions: int
    flagged_count: int
    blocked_count: int
    cleared_count: int
    avg_risk_score: float
    risk_distribution: Dict[str, int]
