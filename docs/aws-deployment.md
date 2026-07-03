# AWS Deployment Notes

This application template is designed to be deployed as a container image.

## Recommended AWS Services

- ECR for Docker image storage
- ECS Fargate for service hosting
- ALB for HTTP/HTTPS routing
- CloudWatch Logs for application logs
- Secrets Manager or SSM Parameter Store for secrets
- Terraform for provisioning and service updates

## Terraform Variables to Connect

Your infrastructure template usually needs these values:

```hcl
container_image    = "<account-id>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>"
container_port     = 8000
health_check_path  = "/health/ready"
```

## Deployment Flow

```bash
export AWS_ACCOUNT_ID="123456789012"
export AWS_REGION="ap-southeast-2"
export ECR_REPOSITORY="aws-python-platform-template"
export IMAGE_TAG="0.1.0"

./scripts/build_and_push_ecr.sh
```

Then update the Terraform environment value:

```hcl
container_image = "123456789012.dkr.ecr.ap-southeast-2.amazonaws.com/aws-python-platform-template:0.1.0"
```

Run:

```bash
terraform plan
terraform apply
```

## GitHub Deploy Workflow to AWS Resource Mapping

The deploy workflow in `.github/workflows/deploy.yml` expects the following GitHub configuration.

| Workflow Key | Location | Value Type | AWS Resource to Provision in Terraform | Notes |
| --- | --- | --- | --- | --- |
| `secrets.AWS_OIDC_ROLE_ARN` | GitHub Environment Secret | IAM Role ARN | `aws_iam_role.github_actions_deploy` | Role trusted by GitHub OIDC provider; used by `aws-actions/configure-aws-credentials` |
| `vars.AWS_REGION` | GitHub Environment Variable | Region string | Deployment region for ECR/ECS/ALB | Example: `ap-southeast-2` |
| `vars.ECR_REPOSITORY` | GitHub Environment Variable | ECR repository name | `aws_ecr_repository.app` | Example: `aws-python-platform-template` |
| `github.sha` | Workflow runtime | Commit SHA | N/A | Used as image tag |
| `container_image` (step summary output) | Workflow output | Full ECR image URI | Terraform input variable `container_image` | Copy/paste or wire through CD automation |

### Expected Published Image Format

```text
<account-id>.dkr.ecr.<region>.amazonaws.com/<ecr-repository>:<commit-sha>
```

---

## Terraform Handoff Checklist (Companion IaC Repo)

### 1. Identity and OIDC

- [ ] Ensure OIDC provider exists: `token.actions.githubusercontent.com`
- [ ] Create IAM role for GitHub Actions deployment (example name: `github-actions-ecr-publish`)
- [ ] Add trust policy conditions to restrict repository and branch/environment usage
- [ ] Add permission policy for ECR push and auth token retrieval

Trust policy baseline:

```hcl
resource "aws_iam_openid_connect_provider" "github" {
	url             = "https://token.actions.githubusercontent.com"
	client_id_list  = ["sts.amazonaws.com"]
	thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "github_oidc_assume_role" {
	statement {
		actions = ["sts:AssumeRoleWithWebIdentity"]

		principals {
			type        = "Federated"
			identifiers = [aws_iam_openid_connect_provider.github.arn]
		}

		condition {
			test     = "StringEquals"
			variable = "token.actions.githubusercontent.com:aud"
			values   = ["sts.amazonaws.com"]
		}

		condition {
			test     = "StringLike"
			variable = "token.actions.githubusercontent.com:sub"
			values   = ["repo:<github-org>/<github-repo>:*"]
		}
	}
}

resource "aws_iam_role" "github_actions_deploy" {
	name               = "github-actions-ecr-publish"
	assume_role_policy = data.aws_iam_policy_document.github_oidc_assume_role.json
}
```

Permission policy baseline:

```hcl
data "aws_iam_policy_document" "github_ecr_publish" {
	statement {
		actions = [
			"ecr:GetAuthorizationToken",
			"ecr:BatchCheckLayerAvailability",
			"ecr:InitiateLayerUpload",
			"ecr:UploadLayerPart",
			"ecr:CompleteLayerUpload",
			"ecr:PutImage",
			"ecr:BatchGetImage"
		]
		resources = ["*"]
	}
}
```

### 2. ECR

- [ ] Create application ECR repository
- [ ] Enable scan on push
- [ ] Enable immutable image tags in production environments
- [ ] Configure lifecycle policy for stale tags

Example:

```hcl
resource "aws_ecr_repository" "app" {
	name                 = var.ecr_repository
	image_tag_mutability = "IMMUTABLE"

	image_scanning_configuration {
		scan_on_push = true
	}
}
```

### 3. GitHub Environment Wiring

For each environment (`dev`, `test`, `uat`, `prod`):

- [ ] Set secret `AWS_OIDC_ROLE_ARN` to `aws_iam_role.github_actions_deploy.arn`
- [ ] Set variable `AWS_REGION` to deployment region
- [ ] Set variable `ECR_REPOSITORY` to `aws_ecr_repository.app.name`
- [ ] Add environment protection rules for `uat` and `prod` approvals

### 4. ECS/Terraform Deployment Wiring

- [ ] Ensure Terraform module accepts `container_image` input
- [ ] Set ECS task definition container image to `var.container_image`
- [ ] Trigger rolling ECS deployment when image changes
- [ ] Verify target group health check path is `/health/ready`

### 5. Verification Runbook

- [ ] Run GitHub workflow dispatch for `dev`
- [ ] Confirm image pushed to ECR with commit SHA tag
- [ ] Update Terraform `container_image` with emitted image URI
- [ ] `terraform plan` and `terraform apply`
- [ ] Verify `/health/live` and `/health/ready`
- [ ] Confirm logs and metrics in CloudWatch

## Production Readiness Checklist

- HTTPS enabled at ALB
- `/health/ready` checks all required dependencies
- logs visible in CloudWatch
- secrets loaded from AWS managed secret store
- autoscaling configured
- deployment rollback enabled
- image tags are immutable or commit-SHA based
- CI runs lint and tests before image push
