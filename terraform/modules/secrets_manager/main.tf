# Secrets Manager holds the RDS master credentials and app runtime config.
# ECS task definitions reference these ARNs via the `secrets` block so
# values are injected at container start, never baked into the image or
# task definition in plaintext.

resource "random_password" "db_master" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.name_prefix}/rds/credentials"
  description = "Oculus RDS PostgreSQL master credentials"
  tags        = var.tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_master.result
  })
}

resource "aws_secretsmanager_secret" "app_config" {
  name        = "${var.name_prefix}/app/config"
  description = "Oculus FastAPI decision service runtime configuration (non-DB secrets)"
  tags        = var.tags
}

resource "aws_secretsmanager_secret_version" "app_config" {
  secret_id = aws_secretsmanager_secret.app_config.id
  secret_string = jsonencode({
    risk_block_threshold  = "75.0"
    risk_review_threshold = "40.0"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
