variable "name_prefix" {
  type = string
}

variable "bucket_suffix" {
  description = "Random/account suffix to keep the S3 bucket name globally unique."
  type        = string
}

variable "alb_dns_name" {
  type = string
}

variable "alb_origin_protocol_policy" {
  description = "Use http-only unless the ALB has an HTTPS listener (certificate_arn set)."
  type        = string
  default     = "http-only"
}

variable "tags" {
  type    = map(string)
  default = {}
}
