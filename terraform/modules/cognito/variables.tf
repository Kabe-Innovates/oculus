variable "name_prefix" {
  type = string
}

variable "domain_prefix" {
  description = "Cognito hosted UI domain prefix. Empty string skips creating a domain."
  type        = string
  default     = ""
}

variable "callback_urls" {
  type    = list(string)
  default = ["https://localhost/callback"]
}

variable "logout_urls" {
  type    = list(string)
  default = ["https://localhost/logout"]
}

variable "tags" {
  type    = map(string)
  default = {}
}
