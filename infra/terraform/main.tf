locals {
  name_prefix = lower("${var.project_name}-${var.environment}")

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      System      = "agentic-newsroom"
    },
    var.tags
  )
}

