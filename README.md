# AWS Python Platform Template

A production-oriented Python application template designed to run on an AWS Terraform platform.

This repo is the Python-side companion to an infrastructure template. Terraform provisions the hosting layer; this repo provides the application baseline that can be containerized and deployed onto it.

## What This Template Gives You

- FastAPI application baseline
- Docker-ready service for ECS Fargate, App Runner, or any container runtime
- Health endpoints for ALB target groups
- Structured JSON logging
- Environment-based configuration
- Clean service/repository layering
- Background worker placeholder
- Test baseline with pytest
- Linting and formatting with Ruff
- Local development Makefile
- GitHub Actions CI workflow
- Deployment notes for AWS/ECR/ECS

## Architecture

```text
Client
  |
  v
ALB / API Gateway
  |
  v
ECS Fargate Service
  |
  v
FastAPI App
  |
  +--> service layer
  +--> repositories / external integrations
  +--> workers / async jobs
  +--> CloudWatch logs
```

## Repository Structure

```text
.
├── src/platform_service/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       └── v1/example.py
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   └── logging.py
│   ├── repositories/
│   │   └── example_repository.py
│   ├── services/
│   │   └── example_service.py
│   └── workers/
│       └── example_worker.py
├── tests/
├── scripts/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── .env.example
└── .github/workflows/ci.yml
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env

make run
```

Open:

```text
http://localhost:8000/docs
http://localhost:8000/health/live
http://localhost:8000/health/ready
```

The API route in this template (`/api/v1/example`) supports API-key auth via `X-API-Key`.
By default auth is disabled for local development (`AUTH_ENABLED=false`).

## Common Commands

```bash
make install
make run
make test
make lint
make format
make security
make docker-build
make docker-run
```

## Security and Runtime Controls

- `ENABLE_DOCS` defaults to enabled only in local environments when unset.
- `AUTH_ENABLED` defaults to enabled in non-local environments when unset.
- API auth uses `X-API-Key` with comma-separated keys from `API_KEYS`.
- Correlation IDs are propagated via `X-Request-ID` and included in logs.
- Standard API security headers are injected on every response.
- `/health/ready` can probe dependency URLs configured by `READINESS_CHECK_URLS`.
- `src/platform_service/repositories/secrets_manager_repository.py` provides a reusable AWS Secrets Manager wrapper.

## Docker

```bash
docker build -t aws-python-platform-template .
docker run --rm -p 8000:8000 --env-file .env aws-python-platform-template
```

## AWS Deployment Mapping

| Python Repo Component | AWS Platform Component |
| --- | --- |
| Dockerfile | ECR image |
| FastAPI app | ECS Fargate task |
| `APP_PORT=8000` | container port / target group port |
| `/health/ready` | ALB target group health check |
| stdout JSON logs | CloudWatch Logs |
| environment variables | ECS task definition variables |
| secrets references | AWS Secrets Manager / SSM Parameter Store |
| stateless app design | ECS autoscaling |

## Promotion Flow

1. Build and test locally.
2. Build Docker image.
3. Push image to ECR.
4. Update Terraform variable such as `container_image`.
5. Deploy with Terraform.
6. Confirm `/health/ready` returns healthy after rollout.

GitHub workflow `.github/workflows/deploy.yml` publishes an image to ECR using OIDC.
Configure repository environment variables and secrets before use:

- `vars.AWS_REGION`
- `vars.ECR_REPOSITORY`
- `secrets.AWS_OIDC_ROLE_ARN`

## Naming Convention

Recommended future service repos:

```text
<platform-name>-api
<platform-name>-worker
<platform-name>-orchestrator
<platform-name>-rag-service
```

## Customization Checklist

When creating a real platform service from this template:

- Rename package from `platform_service` to your service name.
- Update `APP_NAME` in `.env`.
- Add real routes under `api/routes/v1`.
- Move business logic into `services`.
- Add database / storage integrations under `repositories`.
- Add secrets through AWS-managed secret stores, not `.env`.
- Configure `AUTH_ENABLED=true` and set secure API keys or replace with your platform auth provider.
- Set `ENABLE_DOCS=false` for production.
- Configure `READINESS_CHECK_URLS` with real dependency checks.
- Update Docker image name in CI/CD.
- Connect Terraform `container_image` to the pushed ECR image.
