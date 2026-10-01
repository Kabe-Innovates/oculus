from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from datetime import datetime, timezone
import uuid
from database import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    sender_id = Column(String(50), nullable=False)
    receiver_id = Column(String(50), nullable=False)
    sender_location = Column(String(100), nullable=True)
    device_fingerprint = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    risk_score = Column(Float, nullable=True)
    verdict = Column(String(10), nullable=True)
    latency_ms = Column(Float, nullable=True)
    status = Column(String(20), default='PENDING')
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rule_results = Column(JSON, nullable=True)
