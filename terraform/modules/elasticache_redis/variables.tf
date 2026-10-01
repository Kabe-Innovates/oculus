variable "name_prefix" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "redis_sg_id" {
  type = string
}

variable "node_type" {
  type    = string
  default = "cache.t4g.medium"
}

variable "num_cache_clusters" {
  description = "Number of nodes in the replication group (2 for Multi-AZ, matches 2-AZ design)."
  type        = number
  default     = 2
}

variable "tags" {
  type    = map(string)
  default = {}
}
