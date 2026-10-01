variable "name_prefix" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "ecs_sg_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "alb_resource_label" {
  description = "ALB + target group resource label for ALBRequestCountPerTarget scaling (format: app/<alb-name>/<id>/targetgroup/<tg-name>/<id>)."
  type        = string
}

variable "container_image" {
  description = "FastAPI decision service container image URI (e.g. ECR repo:tag)."
  type        = string
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "task_cpu" {
  type    = number
  default = 512
}

variable "task_memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "min_capacity" {
  type    = number
  default = 2
}

variable "max_capacity" {
  type    = number
  default = 10
}

variable "db_host" {
  type = string
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "db_name" {
  type = string
}

variable "redis_host" {
  type = string
}

variable "redis_port" {
  type    = number
  default = 6379
}

variable "sns_topic_arn" {
  type = string
}

variable "sqs_outbox_url" {
  type = string
}

variable "cognito_user_pool_id" {
  type    = string
  default = ""
}

variable "cognito_client_id" {
  type    = string
  default = ""
}

variable "db_credentials_secret_arn" {
  type = string
}

variable "app_config_secret_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
