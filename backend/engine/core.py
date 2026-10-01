import asyncio
import time
import logging
from typing import List

from engine.base import RuleResult, FraudRule
from engine.registry import RuleRegistry
from models import Transaction
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


def compute_score(results: List[RuleResult], rules: List[FraudRule]) -> float:
    """Compute composite fraud score from rule results.

    Uses weighted average with a single-rule floor so one severe rule
    can still reach BLOCK on its own.  A CRITICAL severity forces the
    score to at least RISK_BLOCK_THRESHOLD.
    """
    triggered_scores = [r.score for r in results if r.triggered]

    # Weighted average
    total_weight = sum(rule.weight for rule in rules)
    if total_weight > 0:
        weighted = sum(r.score * rule.weight for r, rule in zip(results, rules)) / total_weight
    else:
        weighted = 0.0

    # Floor: highest triggered score * factor
    floor = max(triggered_scores, default=0) * settings.SINGLE_RULE_FACTOR
    score = max(weighted, floor)

    # CRITICAL severity escalation
    if any(r.severity == "CRITICAL" and r.triggered for r in results):
        score = max(score, settings.RISK_BLOCK_THRESHOLD)

    return round(max(0.0, min(100.0, score)), 2)


def to_verdict(score: float) -> str:
    """Map a composite score to a verdict string."""
    if score >= settings.RISK_BLOCK_THRESHOLD:
        return "BLOCK"
    if score >= settings.RISK_REVIEW_THRESHOLD:
        return "REVIEW"
    return "ALLOW"


class FraudEngine:
    def __init__(self, registry: RuleRegistry, db: AsyncSession):
        self.registry = registry
        self.db = db

    async def _safe_eval(self, rule: FraudRule, transaction: dict, history: list) -> RuleResult:
        """Run a single rule with a timeout; never propagate exceptions."""
        try:
            return await asyncio.wait_for(
                rule.evaluate(transaction, history),
                timeout=settings.RULE_TIMEOUT_SECONDS,
            )
        except Exception as e:
            logger.exception("Rule '%s' failed", rule.name)
            return RuleResult(
                rule_name=rule.name,
                score=0.0,
                reason=f"Rule error: {type(e).__name__}",
                triggered=False,
            )

    async def process_transaction(self, transaction_data: dict) -> Transaction:
        """Evaluate all rules, persist the transaction and per-rule flags."""
        start_time = time.perf_counter()

        # Load sender history (last 100 transactions)
        stmt = (
            select(Transaction)
            .where(Transaction.sender_id == transaction_data["sender_id"])
            .order_by(Transaction.timestamp.desc())
            .limit(100)
        )
        result = await self.db.execute(stmt)
        history = [
            {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
            for row in result.scalars().all()
        ]

        # Run all rules concurrently with per-rule timeout
        all_rules = self.registry.get_all()
        rule_results: List[RuleResult] = await asyncio.gather(
            *(self._safe_eval(rule, transaction_data, history) for rule in all_rules)
        )

        # Score & verdict
        score = compute_score(rule_results, all_rules)
        verdict = to_verdict(score)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Serialise rule results for the JSON column
        results_json = [
            {
                "rule_name": r.rule_name,
                "score": r.score,
                "reason": r.reason,
                "triggered": r.triggered,
                "severity": r.severity,
            }
            for r in rule_results
        ]

        # Persist transaction
        db_tx = Transaction(**transaction_data)
        db_tx.risk_score = score
        db_tx.verdict = verdict
        db_tx.latency_ms = elapsed_ms
        db_tx.rule_results = results_json

        self.db.add(db_tx)
        await self.db.commit()
        await self.db.refresh(db_tx)

        # NOTE: Notifications are handled by the router via BackgroundTasks,
        # not by the engine.  This keeps process_transaction fast.

        return db_tx
