resource "aws_sqs_queue" "agent_jobs_dlq" {
  name                      = "${local.name_prefix}-agent-jobs-dlq"
  message_retention_seconds = var.sqs_message_retention_seconds

  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "agent_jobs" {
  name                       = "${local.name_prefix}-agent-jobs"
  visibility_timeout_seconds = var.sqs_visibility_timeout_seconds
  message_retention_seconds  = var.sqs_message_retention_seconds

  sqs_managed_sse_enabled = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.agent_jobs_dlq.arn
    maxReceiveCount     = var.sqs_max_receive_count
  })
}

