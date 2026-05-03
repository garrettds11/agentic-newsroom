output "dynamodb_run_state_table_name" {
  description = "Name of the DynamoDB table for compact run ledger metadata and S3 pointers."
  value       = aws_dynamodb_table.run_state.name
}

output "s3_artifact_bucket_name" {
  description = "Name of the S3 bucket for large research artifacts and manifests."
  value       = aws_s3_bucket.artifacts.bucket
}

output "sqs_agent_jobs_queue_url" {
  description = "URL of the SQS queue for agent jobs."
  value       = aws_sqs_queue.agent_jobs.url
}

output "local_agent_runner_iam_policy_arn" {
  description = "ARN of the managed IAM policy for the local agent runner."
  value       = aws_iam_policy.local_agent_runner.arn
}
