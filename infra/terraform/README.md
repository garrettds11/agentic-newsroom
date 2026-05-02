# Agentic Newsroom AWS Persistence Blueprint

This Terraform/OpenTofu blueprint defines the optional AWS persistence layer for Agentic Newsroom.

It creates:

- DynamoDB table for run state, metadata, status, scores, and source URLs.
- S3 bucket for raw sources, drafts, final artifacts, and logs.
- SQS queue and dead-letter queue for agent jobs.
- Least-privilege IAM managed policy for a local agent runner.

## Safety

Do not run `terraform apply` until AWS permissions, resource names, retention settings, and tags have been reviewed by a human operator.

This blueprint does not include secrets. Do not place access keys, secret keys, API keys, private ARNs, or account IDs in `.tfvars` files.

## Configuration

Start from the example file:

```powershell
Copy-Item infra/terraform/envs/dev/terraform.tfvars.example infra/terraform/envs/dev/terraform.tfvars
```

Review and edit the local `terraform.tfvars` file outside source control. The root `.gitignore` excludes real `.tfvars` files.

## Initialize

Terraform:

```powershell
terraform -chdir=infra/terraform init
```

OpenTofu:

```powershell
tofu -chdir=infra/terraform init
```

## Format

Terraform:

```powershell
terraform -chdir=infra/terraform fmt -recursive
```

OpenTofu:

```powershell
tofu -chdir=infra/terraform fmt -recursive
```

## Validate

Terraform:

```powershell
terraform -chdir=infra/terraform validate
```

OpenTofu:

```powershell
tofu -chdir=infra/terraform validate
```

## Plan

Review the generated plan before any apply:

```powershell
terraform -chdir=infra/terraform plan -var-file="envs/dev/terraform.tfvars"
```

Do not apply infrastructure until naming, permissions, cost, retention, and AWS account context have been explicitly approved.

