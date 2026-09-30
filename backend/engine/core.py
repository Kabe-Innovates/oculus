import asyncio
from engine.registry import RuleRegistry
from models import Transaction
from services.notifier import get_notifier
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class FraudEngine:
    def __init__(self, registry: RuleRegistry, db: AsyncSession):
        self.registry = registry
        self.db = db
        self.notifier = get_notifier()

    async def process_transaction(self, transaction_data: dict) -> Transaction:
        stmt = select(Transaction).where(Transaction.sender_id == transaction_data['sender_id']).order_by(Transaction.timestamp.desc()).limit(100)
        result = await self.db.execute(stmt)
        history = [row.__dict__ for row in result.scalars().all()]
        
        all_rules = self.registry.get_all()
        tasks = [rule.evaluate(transaction_data, history) for rule in all_rules]
        results = await asyncio.gather(*tasks)
        
        total_weight = sum(rule.weight for rule in all_rules)
        if total_weight > 0:
            composite_score = sum(res.score * rule.weight for res, rule in zip(results, all_rules)) / total_weight
        else:
            composite_score = 0
            
        if composite_score >= settings.RISK_BLOCK_THRESHOLD:
            verdict = 'BLOCK'
        elif composite_score >= settings.RISK_REVIEW_THRESHOLD:
            verdict = 'REVIEW'
        else:
            verdict = 'ALLOW'
            
        db_tx = Transaction(**transaction_data)
        db_tx.risk_score = composite_score
        db_tx.verdict = verdict
        db_tx.rule_results = [
            {
                "rule_name": r.rule_name,
                "score": r.score,
                "reason": r.reason,
                "triggered": r.triggered
            }
            for r in results
        ]
        
        self.db.add(db_tx)
        await self.db.commit()
        await self.db.refresh(db_tx)
        
        if verdict == 'BLOCK':
            await self.notifier.notify(db_tx)
            
        return db_tx
