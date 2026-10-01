output "db_credentials_secret_arn" {
  value = aws_secretsmanager_secret.db_credentials.arn
}

output "db_credentials_secret_name" {
  value = aws_secretsmanager_secret.db_credentials.name
}

output "app_config_secret_arn" {
  value = aws_secretsmanager_secret.app_config.arn
}

output "db_username" {
  value = var.db_username
}

output "db_password" {
  value     = random_password.db_master.result
  sensitive = true
}
