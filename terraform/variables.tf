variable "aws_region" {
  description = "AWS region. Oculus is single-region."
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "name_prefix" {
  type    = string
  default = "oculus"
}

variable "azs" {
  description = "Exactly 2 Availability Zones in ap-south-1."
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.20.0.0/24", "10.20.1.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.20.10.0/24", "10.20.11.0/24"]
}

variable "app_port" {
  description = "FastAPI decision service port (also handles WebSocket upgrades)."
  type        = number
  default     = 8000
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for the ALB HTTPS listener. Leave empty to serve HTTP only (not recommended for production)."
  type        = string
  default     = ""
}

variable "container_image" {
  description = "ECR image URI for the FastAPI decision service."
  type        = string
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

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "db_multi_az" {
  type    = bool
  default = true
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.medium"
}

variable "alert_emails" {
  description = "Analyst/compliance email addresses subscribed to fraud alerts."
  type        = list(string)
  default     = []
}

variable "alert_sms_numbers" {
  type    = list(string)
  default = []
}

variable "ses_sender_email" {
  description = "Verified SES sender for rich case-summary email. Empty disables SES send."
  type        = string
  default     = ""
}

variable "cognito_domain_prefix" {
  description = "Cognito Hosted UI domain prefix (must be globally unique). Empty skips domain creation."
  type        = string
  default     = ""
}

variable "cognito_callback_urls" {
  type    = list(string)
  default = ["https://localhost/callback"]
}

variable "cognito_logout_urls" {
  type    = list(string)
  default = ["https://localhost/logout"]
}

variable "spa_bucket_suffix" {
  description = "Suffix to keep the SPA S3 bucket name globally unique (e.g. account id)."
  type        = string
}

variable "waf_rate_limit_per_5min" {
  type    = number
  default = 2000
}

variable "p95_latency_threshold_seconds" {
  type    = number
  default = 0.3
}
