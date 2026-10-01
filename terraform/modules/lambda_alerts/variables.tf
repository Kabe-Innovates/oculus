variable "name_prefix" {
  type = string
}

variable "sqs_queue_arn" {
  type = string
}

variable "sns_topic_arn" {
  type = string
}

variable "ses_sender_email" {
  type    = string
  default = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
