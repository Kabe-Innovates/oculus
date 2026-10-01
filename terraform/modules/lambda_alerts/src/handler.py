"""Oculus outbox alert worker.

Consumes outbox events relayed through SQS (fraud_flags / reviews written
in the same DB transaction as the business write) and fans out
notifications via SNS (email/SMS) and SES (rich case-summary email).
"""
import json
import os
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")
ses = boto3.client("ses")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
SES_SENDER = os.environ.get("SES_SENDER_EMAIL", "")


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        _dispatch(body)
    return {"statusCode": 200}


def _dispatch(payload: dict) -> None:
    subject = f"Oculus Fraud Alert: {payload.get('verdict', 'REVIEW')} - {payload.get('transaction_id', '')[:8]}"
    message = json.dumps(payload, default=str)

    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject[:100], Message=message)
    logger.info("Published outbox event %s to SNS", payload.get("transaction_id"))

    if SES_SENDER and payload.get("analyst_email"):
        ses.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [payload["analyst_email"]]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": message}},
            },
        )
