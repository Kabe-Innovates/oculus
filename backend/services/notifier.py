from abc import ABC, abstractmethod
import asyncio
import time
import boto3
from config import settings
import logging

logger = logging.getLogger(__name__)


class NotifierBase(ABC):
    @abstractmethod
    async def notify(self, transaction):
        pass


class SNSNotifier(NotifierBase):
    def __init__(self, topic_arn: str, region: str):
        self.topic_arn = topic_arn
        self.region = region
        self.client = boto3.client('sns', region_name=self.region)
        # Per-sender cooldown to avoid alert spam.
        # Production would use Redis or a transactional outbox.
        self._last_alert: dict[str, float] = {}

    async def notify(self, transaction):
        """Publish a fraud alert via SNS, non-blocking.

        Deduplicates per sender within ALERT_COOLDOWN_SECONDS.
        """
        sender = getattr(transaction, "sender_id", "unknown")
        now = time.monotonic()
        last = self._last_alert.get(sender, 0.0)
        if now - last < settings.ALERT_COOLDOWN_SECONDS:
            logger.info("Cooldown active for sender %s — skipping SNS alert", sender)
            return
        self._last_alert[sender] = now

        triggered_rules = []
        if hasattr(transaction, 'rule_results') and transaction.rule_results:
            for r in transaction.rule_results:
                if isinstance(r, dict) and r.get('triggered'):
                    triggered_rules.append(f"  * {r.get('rule_name')}: {r.get('reason')} (score: {r.get('score')})")

        triggered_str = "\n".join(triggered_rules) if triggered_rules else "  * Critical multi-factor threshold exceeded"

        risk_score = round(transaction.risk_score, 1) if transaction.risk_score is not None else 0
        message = (
            f"OCULUS FRAUD DETECTION ALERT\n"
            f"============================\n"
            f"Status: BLOCKED (High-Risk Threshold Exceeded)\n"
            f"Transaction ID: {transaction.id}\n"
            f"Amount: ${transaction.amount:,.2f} {transaction.currency}\n"
            f"Sender: {transaction.sender_id}\n"
            f"Composite Risk Score: {risk_score} / 100\n\n"
            f"Triggered Violations:\n{triggered_str}\n\n"
            f"Timestamp: {transaction.timestamp}\n"
            f"Action Required: Investigate incident in Oculus Review Console.\n"
        )

        try:
            res = await asyncio.to_thread(
                self.client.publish,
                TopicArn=self.topic_arn,
                Message=message,
                Subject=f"FRAUD ALERT: Blocked Transaction {str(transaction.id)[:8]} (Score: {risk_score})",
            )
            logger.info("Published SNS alert %s for transaction %s", res.get('MessageId'), transaction.id)
        except Exception as e:
            logger.error("Failed to publish to SNS: %s", e)


class ConsoleNotifier(NotifierBase):
    async def notify(self, transaction):
        risk_score = round(transaction.risk_score, 1) if transaction.risk_score is not None else 0
        logger.warning(
            "FRAUD ALERT (Console): Blocked transaction %s | Amount: %s | Sender: %s | Score: %s",
            transaction.id, transaction.amount, transaction.sender_id, risk_score,
        )


def get_notifier() -> NotifierBase:
    """Factory: returns SNS notifier if configured, else console fallback."""
    if settings.SNS_TOPIC_ARN:
        return SNSNotifier(settings.SNS_TOPIC_ARN, settings.AWS_REGION)
    return ConsoleNotifier()
