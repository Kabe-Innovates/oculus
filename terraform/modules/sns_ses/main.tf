# SNS topic for fraud alert fan-out (email/SMS) and SES identity for
# transactional email sent directly by the alert worker (e.g. rich HTML
# case summaries) as opposed to the simple SNS email subscription.

resource "aws_sns_topic" "fraud_alerts" {
  name = "${var.name_prefix}-fraud-alerts"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email" {
  for_each  = toset(var.alert_emails)
  topic_arn = aws_sns_topic.fraud_alerts.arn
  protocol  = "email"
  endpoint  = each.value
}

resource "aws_sns_topic_subscription" "sms" {
  for_each  = toset(var.alert_sms_numbers)
  topic_arn = aws_sns_topic.fraud_alerts.arn
  protocol  = "sms"
  endpoint  = each.value
}

resource "aws_ses_email_identity" "sender" {
  count = var.ses_sender_email == "" ? 0 : 1
  email = var.ses_sender_email
}
