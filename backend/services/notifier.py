from abc import ABC, abstractmethod
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
        
    async def notify(self, transaction):
        triggered_rules = []
        if hasattr(transaction, 'rule_results') and transaction.rule_results:
            for r in transaction.rule_results:
                if isinstance(r, dict) and r.get('triggered'):
                    triggered_rules.append(f"  * {r.get('rule_name')}: {r.get('reason')} (score: {r.get('score')})")
        
        triggered_str = "\n".join(triggered_rules) if triggered_rules else "  * Critical multi-factor threshold exceeded"

        message = (
            f"OCULUS FRAUD DETECTION ALERT\n"
            f"============================\n"
            f"Status: BLOCKED (High-Risk Threshold Exceeded)\n"
            f"Transaction ID: {transaction.id}\n"
            f"Amount: ${transaction.amount:,.2f} {transaction.currency}\n"
            f"Sender: {transaction.sender_id}\n"
            f"Composite Risk Score: {transaction.risk_score:.1f} / 100\n\n"
            f"Triggered Violations:\n{triggered_str}\n\n"
            f"Timestamp: {transaction.timestamp}\n"
            f"Action Required: Investigate incident in Oculus Review Console.\n"
        )
        try:
            res = self.client.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject=f"FRAUD ALERT: Blocked Transaction {str(transaction.id)[:8]} (Score: {transaction.risk_score:.0f})"
            )
            print(f"[+] Successfully published SNS alert {res.get('MessageId')} for transaction {transaction.id}")
        except Exception as e:
            logger.error(f"Failed to publish to SNS: {e}")
            print(f"[!] SNS publish error: {e}")

class ConsoleNotifier(NotifierBase):
    async def notify(self, transaction):
        print(f"FRAUD ALERT (Console): Blocked transaction {transaction.id} | Amount: {transaction.amount} | Sender: {transaction.sender_id} | Score: {transaction.risk_score}")

def get_notifier() -> NotifierBase:
    if settings.SNS_TOPIC_ARN:
        return SNSNotifier(settings.SNS_TOPIC_ARN, settings.AWS_REGION)
    return ConsoleNotifier()
