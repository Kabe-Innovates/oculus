variable "name_prefix" {
  type = string
}

variable "alb_arn" {
  type = string
}

variable "rate_limit_per_5min" {
  description = "Max requests from a single IP per 5-minute window before blocking."
  type        = number
  default     = 2000
}

variable "tags" {
  type    = map(string)
  default = {}
}
