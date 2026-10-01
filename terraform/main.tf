# Oculus root module: wires VPC, security groups, WAF, ALB, ECS Fargate,
# RDS PostgreSQL, ElastiCache Redis, outbox SQS -> Lambda -> SNS/SES,
# Cognito, CloudFront+S3 SPA, Secrets Manager, and CloudWatch observability.
# Single region (ap-south-1), 2 AZs. See docs/architecture.md for the
# diagram and VPC/subnet/SG boundaries.

module "vpc" {
  source = "./modules/vpc"

  name_prefix          = var.name_prefix
  vpc_cidr             = var.vpc_cidr
  azs                  = var.azs
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                 = local.common_tags
}

module "security_groups" {
  source = "./modules/security_groups"

  name_prefix = var.name_prefix
  vpc_id      = module.vpc.vpc_id
  app_port    = var.app_port
  tags        = local.common_tags
}

module "secrets_manager" {
  source = "./modules/secrets_manager"

  name_prefix = var.name_prefix
  tags        = local.common_tags
}

module "rds" {
  source = "./modules/rds_postgres"

  name_prefix        = var.name_prefix
  private_subnet_ids = module.vpc.private_subnet_ids
  rds_sg_id          = module.security_groups.rds_sg_id
  instance_class     = var.db_instance_class
  multi_az           = var.db_multi_az
  db_username        = module.secrets_manager.db_username
  db_password        = module.secrets_manager.db_password
  tags               = local.common_tags
}

module "redis" {
  source = "./modules/elasticache_redis"

  name_prefix        = var.name_prefix
  private_subnet_ids = module.vpc.private_subnet_ids
  redis_sg_id        = module.security_groups.redis_sg_id
  node_type          = var.redis_node_type
  tags               = local.common_tags
}

module "sqs" {
  source = "./modules/sqs"

  name_prefix = var.name_prefix
  tags        = local.common_tags
}

module "sns_ses" {
  source = "./modules/sns_ses"

  name_prefix       = var.name_prefix
  alert_emails      = var.alert_emails
  alert_sms_numbers = var.alert_sms_numbers
  ses_sender_email  = var.ses_sender_email
  tags              = local.common_tags
}

module "lambda_alerts" {
  source = "./modules/lambda_alerts"

  name_prefix      = var.name_prefix
  sqs_queue_arn    = module.sqs.queue_arn
  sns_topic_arn    = module.sns_ses.topic_arn
  ses_sender_email = var.ses_sender_email
  tags             = local.common_tags
}

module "cognito" {
  source = "./modules/cognito"

  name_prefix   = var.name_prefix
  domain_prefix = var.cognito_domain_prefix
  callback_urls = var.cognito_callback_urls
  logout_urls   = var.cognito_logout_urls
  tags          = local.common_tags
}

module "alb" {
  source = "./modules/alb"

  name_prefix       = var.name_prefix
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  alb_sg_id         = module.security_groups.alb_sg_id
  app_port          = var.app_port
  health_check_path = var.health_check_path
  certificate_arn   = var.certificate_arn
  tags              = local.common_tags
}

module "waf" {
  source = "./modules/waf"

  name_prefix         = var.name_prefix
  alb_arn             = module.alb.alb_arn
  rate_limit_per_5min = var.waf_rate_limit_per_5min
  tags                = local.common_tags
}

module "ecs" {
  source = "./modules/ecs_fargate"

  name_prefix               = var.name_prefix
  aws_region                = var.aws_region
  private_subnet_ids        = module.vpc.private_subnet_ids
  ecs_sg_id                 = module.security_groups.ecs_sg_id
  target_group_arn          = module.alb.target_group_arn
  alb_resource_label        = "${module.alb.alb_arn}/${module.alb.target_group_arn}"
  container_image           = var.container_image
  app_port                  = var.app_port
  health_check_path         = var.health_check_path
  desired_count             = var.desired_count
  min_capacity              = var.min_capacity
  max_capacity              = var.max_capacity
  db_host                   = module.rds.address
  db_port                   = module.rds.port
  db_name                   = module.rds.db_name
  redis_host                = module.redis.primary_endpoint_address
  redis_port                = module.redis.port
  sns_topic_arn             = module.sns_ses.topic_arn
  sqs_outbox_url            = module.sqs.queue_url
  cognito_user_pool_id      = module.cognito.user_pool_id
  cognito_client_id         = module.cognito.client_id
  db_credentials_secret_arn = module.secrets_manager.db_credentials_secret_arn
  app_config_secret_arn     = module.secrets_manager.app_config_secret_arn
  tags                      = local.common_tags
}

module "cloudfront_spa" {
  source = "./modules/cloudfront_spa"

  name_prefix   = var.name_prefix
  bucket_suffix = var.spa_bucket_suffix
  alb_dns_name  = module.alb.alb_dns_name
  tags          = local.common_tags
}

module "cloudwatch" {
  source = "./modules/cloudwatch"

  name_prefix                   = var.name_prefix
  aws_region                    = var.aws_region
  alb_arn_suffix                = module.alb.alb_arn
  ecs_cluster_name              = module.ecs.cluster_name
  ecs_service_name              = module.ecs.service_name
  ecs_log_group_name            = module.ecs.log_group_name
  sqs_queue_name                = "${var.name_prefix}-outbox"
  p95_latency_threshold_seconds = var.p95_latency_threshold_seconds
  alarm_sns_topic_arn           = module.sns_ses.topic_arn
  tags                          = local.common_tags
}
