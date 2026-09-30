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
        message = (
            f"FRAUD ALERT: Blocked transaction {transaction.id}\n"
            f"Amount: {transaction.amount} {transaction.currency}\n"
            f"Sender: {transaction.sender_id}\n"
            f"Score: {transaction.risk_score}\n"
        )
        try:
            self.client.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject="SentinelPay Fraud Alert"
            )
        except Exception as e:
            logger.error(f"Failed to publish to SNS: {e}")

class ConsoleNotifier(NotifierBase):
    async def notify(self, transaction):
        print(f"FRAUD ALERT (Console): Blocked transaction {transaction.id} | Amount: {transaction.amount} | Sender: {transaction.sender_id} | Score: {transaction.risk_score}")

def get_notifier() -> NotifierBase:
    if settings.SNS_TOPIC_ARN:
        return SNSNotifier(settings.SNS_TOPIC_ARN, settings.AWS_REGION)
    return ConsoleNotifier()
