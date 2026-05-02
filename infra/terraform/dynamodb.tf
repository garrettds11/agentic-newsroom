resource "aws_dynamodb_table" "run_state" {
  name         = "${local.name_prefix}-run-state"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "run_id"
  range_key    = "record_type"

  attribute {
    name = "run_id"
    type = "S"
  }

  attribute {
    name = "record_type"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  global_secondary_index {
    name            = "status-created-at"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery_enabled
  }

  server_side_encryption {
    enabled = true
  }
}

