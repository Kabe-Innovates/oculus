variable "name_prefix" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "alb_arn_suffix" {
  type = string
}

variable "ecs_cluster_name" {
  type = string
}

variable "ecs_service_name" {
  type = string
}

variable "ecs_log_group_name" {
  type = string
}

variable "sqs_queue_name" {
  type = string
}

variable "p95_latency_threshold_seconds" {
  type    = number
  default = 0.3
}

variable "alarm_sns_topic_arn" {
  description = "SNS topic to notify on alarm state (ops channel). Empty string disables alarm actions."
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
