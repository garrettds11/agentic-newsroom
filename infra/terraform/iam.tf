data "aws_iam_policy_document" "local_agent_runner" {
  statement {
    sid    = "DynamoDbRunStateAccess"
    effect = "Allow"

    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:ConditionCheckItem",
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:UpdateItem"
    ]

    resources = [
      aws_dynamodb_table.run_state.arn,
      "${aws_dynamodb_table.run_state.arn}/index/*"
    ]
  }

  statement {
    sid    = "S3ArtifactAccess"
    effect = "Allow"

    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.artifacts.arn,
      "${aws_s3_bucket.artifacts.arn}/*"
    ]
  }

  statement {
    sid    = "SqsAgentJobAccess"
    effect = "Allow"

    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.agent_jobs.arn,
      aws_sqs_queue.agent_jobs_dlq.arn
    ]
  }
}

resource "aws_iam_policy" "local_agent_runner" {
  name        = "${local.name_prefix}-local-agent-runner"
  description = "Least-privilege access for the Agentic Newsroom local agent runner persistence layer."
  policy      = data.aws_iam_policy_document.local_agent_runner.json
}

