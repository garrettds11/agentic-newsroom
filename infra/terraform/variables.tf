variable "project_name" {
  description = "Short project name used in resource names."
  type        = string
  default     = "agentic-newsroom"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,40}[a-z0-9]$", var.project_name))
    error_message = "project_name must be 3-42 lowercase letters, numbers, or hyphens, and start/end with a letter or number."
  }
}

variable "environment" {
  description = "Deployment environment name such as dev, test, or prod."
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,20}[a-z0-9]$", var.environment))
    error_message = "environment must be 3-22 lowercase letters, numbers, or hyphens, and start/end with a letter or number."
  }
}

variable "aws_region" {
  description = "AWS region for resources. Do not encode region-specific ARNs elsewhere."
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Additional tags applied to supported resources."
  type        = map(string)
  default     = {}
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode."
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.dynamodb_billing_mode)
    error_message = "dynamodb_billing_mode must be PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "dynamodb_point_in_time_recovery_enabled" {
  description = "Enable DynamoDB point-in-time recovery."
  type        = bool
  default     = true
}

variable "s3_bucket_name" {
  description = "Optional explicit S3 bucket name. Leave null to derive one from project and environment."
  type        = string
  default     = null
}

variable "s3_force_destroy" {
  description = "Allow Terraform to delete a non-empty artifact bucket. Keep false for safer environments."
  type        = bool
  default     = false
}

variable "s3_log_retention_days" {
  description = "Days before objects under logs/ expire."
  type        = number
  default     = 90
}

variable "s3_raw_source_retention_days" {
  description = "Days before objects under raw-sources/ expire."
  type        = number
  default     = 365
}

variable "s3_noncurrent_version_retention_days" {
  description = "Days to retain noncurrent S3 object versions."
  type        = number
  default     = 30
}

variable "sqs_visibility_timeout_seconds" {
  description = "SQS visibility timeout for agent jobs."
  type        = number
  default     = 300
}

variable "sqs_message_retention_seconds" {
  description = "SQS message retention period for agent jobs."
  type        = number
  default     = 345600
}

variable "sqs_max_receive_count" {
  description = "Number of receives before moving a job to the dead-letter queue."
  type        = number
  default     = 5
}

