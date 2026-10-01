variable "name_prefix" {
  type = string
}

variable "db_username" {
  type    = string
  default = "oculus_app"
}

variable "tags" {
  type    = map(string)
  default = {}
}
