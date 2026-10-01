variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "app_port" {
  description = "Port the FastAPI decision service listens on (HTTP + WebSocket)."
  type        = number
  default     = 8000
}

variable "tags" {
  type    = map(string)
  default = {}
}
