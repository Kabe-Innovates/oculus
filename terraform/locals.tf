locals {
  common_tags = {
    Project     = "oculus"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
