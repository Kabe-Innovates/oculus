output "vpc_id" {
  value = module.vpc.vpc_id
}

output "alb_dns_name" {
  value = module.alb.alb_dns_name
}

output "cloudfront_domain_name" {
  value = module.cloudfront_spa.distribution_domain_name
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "redis_primary_endpoint" {
  value = module.redis.primary_endpoint_address
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "sns_fraud_alerts_topic_arn" {
  value = module.sns_ses.topic_arn
}

output "sqs_outbox_queue_url" {
  value = module.sqs.queue_url
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}
