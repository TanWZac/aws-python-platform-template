# Design Principles

## 1. Keep the App Stateless

The app should not depend on local disk or in-memory state for correctness. This allows ECS to scale tasks horizontally.

## 2. Separate API, Service, and Repository Layers

- API layer: request/response handling
- Service layer: business logic
- Repository layer: database, object storage, vector store, or external APIs

## 3. Make Health Checks Real

`/health/live` should confirm the process is running.

`/health/ready` should confirm the app is ready to receive traffic.

For production, extend readiness checks to include:

- database connection
- queue availability
- vector store availability
- required model/service dependencies

## 4. Use Environment Variables

Local `.env` is for development only.

Production should use:

- ECS task environment variables
- Secrets Manager
- SSM Parameter Store

## 5. Log to stdout

Containers should log to stdout/stderr. AWS will route logs to CloudWatch.

## 6. Keep Docker Builds Simple

The default Dockerfile is intentionally simple. For larger services, consider:

- multi-stage builds
- dependency caching
- vulnerability scanning
- non-root runtime user

## 7. Use OIDC for CI/CD Identity

CI/CD pipelines should use short-lived credentials via GitHub OIDC federation.

Do not use long-lived AWS access keys in repository secrets.

For deploy workflows, provision an IAM role trusted by `token.actions.githubusercontent.com` and scope permissions to the minimum required resources.

## 8. Use Immutable, Traceable Image Tags

Production deployments should use immutable image tags (commit SHA or release tags), not mutable tags such as `latest`.

This improves rollback safety, auditability, and incident diagnosis.

## 9. Keep App and Infrastructure Contracts Explicit

Every workflow variable/secret consumed by CI/CD must map to a concrete Terraform-managed resource.

Maintain this mapping in deployment docs so application teams and infrastructure teams can complete handoff without ambiguity.
