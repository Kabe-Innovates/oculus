# SQS queue that the outbox-relay pattern drains into: the FastAPI service
# writes rows to the Postgres `outbox` table in the same transaction as the
# business write, and a lightweight relay (or RDS->SQS trigger outside this
# module's scope) publishes them here. A Lambda worker consumes this queue
# asynchronously to fan out alerts.

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.name_prefix}-outbox-dlq"
  message_retention_seconds = 1209600 # 14 days
  tags                      = var.tags
}

resource "aws_sqs_queue" "outbox" {
  name                       = "${var.name_prefix}-outbox"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 345600 # 4 days

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })

  tags = var.tags
}
