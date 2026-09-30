#!/usr/bin/env python3
"""
SentinelPay — AWS SNS Topic Setup Script
Run this once before the demo to create the SNS topic and subscribe an email.

Usage:
    python scripts/setup_sns.py --email your-email@example.com --region ap-south-1

After running, check your email and click the confirmation link from AWS.
"""

import argparse
import boto3
import json
import sys


def setup_sns(email: str, region: str = "ap-south-1") -> str:
    """Create SNS topic and subscribe an email address."""
    
    sns = boto3.client("sns", region_name=region)
    
    # Step 1: Create the topic
    print("📡 Creating SNS topic 'SentinelPay-FraudAlerts'...")
    response = sns.create_topic(
        Name="SentinelPay-FraudAlerts",
        Tags=[
            {"Key": "Project", "Value": "SentinelPay"},
            {"Key": "Purpose", "Value": "FraudAlerts"},
        ],
    )
    topic_arn = response["TopicArn"]
    print(f"✅ Topic created: {topic_arn}")
    
    # Step 2: Subscribe the email
    print(f"📧 Subscribing {email} to the topic...")
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol="email",
        Endpoint=email,
    )
    print(f"✅ Subscription created. CHECK YOUR EMAIL and click the confirmation link!")
    
    # Step 3: Output the .env content
    print("\n" + "=" * 60)
    print("Add this to your backend/.env file:")
    print("=" * 60)
    env_content = f'SNS_TOPIC_ARN={topic_arn}\nAWS_REGION={region}'
    print(env_content)
    print("=" * 60)
    
    # Step 4: Auto-create .env file
    env_path = "backend/.env"
    try:
        with open(env_path, "w") as f:
            f.write(env_content + "\n")
        print(f"\n✅ Auto-created {env_path}")
    except Exception as e:
        print(f"\n⚠️  Could not create {env_path}: {e}")
        print("   Create it manually with the content above.")
    
    # Step 5: Send a test notification
    print("\n🧪 Sending test notification...")
    try:
        sns.publish(
            TopicArn=topic_arn,
            Subject="🛡️ SentinelPay Test Alert",
            Message=json.dumps({
                "test": True,
                "message": "SentinelPay fraud alerting is configured and working!",
                "system": "SentinelPay Fraud Detection Engine",
            }, indent=2),
        )
        print("✅ Test notification sent! (You'll receive it after confirming the subscription)")
    except Exception as e:
        print(f"⚠️  Test notification failed: {e}")
    
    return topic_arn


def main():
    parser = argparse.ArgumentParser(
        description="Set up AWS SNS for SentinelPay fraud alerts"
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Email address to receive fraud alerts",
    )
    parser.add_argument(
        "--region",
        default="ap-south-1",
        help="AWS region (default: ap-south-1)",
    )
    
    args = parser.parse_args()
    
    try:
        setup_sns(args.email, args.region)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. AWS CLI is configured (run 'aws configure')")
        print("  2. Your IAM user has SNS permissions")
        print("  3. The region is correct")
        sys.exit(1)


if __name__ == "__main__":
    main()
