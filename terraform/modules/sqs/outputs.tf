output "queue_arn" {
  value = aws_sqs_queue.outbox.arn
}

output "queue_url" {
  value = aws_sqs_queue.outbox.id
}

output "dlq_arn" {
  value = aws_sqs_queue.dlq.arn
}
