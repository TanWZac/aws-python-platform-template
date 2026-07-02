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

## Production Readiness Checklist

- HTTPS enabled at ALB
- `/health/ready` checks all required dependencies
- logs visible in CloudWatch
- secrets loaded from AWS managed secret store
- autoscaling configured
- deployment rollback enabled
- image tags are immutable or commit-SHA based
- CI runs lint and tests before image push
