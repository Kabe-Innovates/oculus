variable "name_prefix" {
  type = string
}

variable "alert_emails" {
  description = "Email addresses subscribed to the fraud alert SNS topic (analyst/compliance team)."
  type        = list(string)
  default     = []
}

variable "alert_sms_numbers" {
  description = "E.164 phone numbers subscribed to the fraud alert SNS topic for critical BLOCK alerts."
  type        = list(string)
  default     = []
}

variable "ses_sender_email" {
  description = "Verified SES sender identity used for outbound case-summary email. Empty string skips creation."
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
