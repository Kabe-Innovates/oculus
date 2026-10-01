output "function_name" {
  value = aws_lambda_function.outbox_worker.function_name
}

output "function_arn" {
  value = aws_lambda_function.outbox_worker.arn
}

output "role_arn" {
  value = aws_iam_role.lambda_exec.arn
}
