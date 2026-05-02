# Slice 003: AWS IaC Blueprint

## Goal

Create a Terraform blueprint for optional AWS persistence using DynamoDB, S3, and SQS.

## Scope

- Add `infra/terraform` structure.
- Define configurable variables for project name, environment, region, and tags.
- Define DynamoDB tables for run state and metadata.
- Define S3 buckets or bucket modules for raw sources, drafts, artifacts, and logs.
- Define SQS queues for agent jobs and dead-letter handling.
- Add least-privilege IAM policy examples for the Python Agent Runner.
- Add backend guidance without hard-coding backend state.

## Acceptance Criteria

- Terraform contains no hard-coded AWS account IDs.
- Terraform contains no API keys, private credentials, or region-specific ARNs.
- Resources are configurable by variables.
- `terraform fmt -check -recursive` passes.
- `terraform validate` passes after `terraform init`.
- Documentation clearly states not to run `terraform apply` without explicit approval.

## Verification Commands

```powershell
terraform -chdir=infra/terraform fmt -check -recursive
```

```powershell
terraform -chdir=infra/terraform init
```

```powershell
terraform -chdir=infra/terraform validate
```
