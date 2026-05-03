locals {
  artifact_bucket_name = coalesce(var.s3_bucket_name, "${local.name_prefix}-artifacts")
}

resource "aws_s3_bucket" "artifacts" {
  bucket        = local.artifact_bucket_name
  force_destroy = var.s3_force_destroy
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "retain-run-artifacts"
    status = "Enabled"

    filter {
      prefix = "runs/env=${var.environment}/"
    }

    noncurrent_version_expiration {
      noncurrent_days = var.s3_noncurrent_version_retention_days
    }
  }

  rule {
    id     = "expire-run-artifacts"
    status = "Enabled"

    filter {
      prefix = "runs/env=${var.environment}/"
    }

    expiration {
      days = var.s3_run_artifact_retention_days
    }
  }
}
