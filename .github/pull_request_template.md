## Summary

<!-- What does this PR do? -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Improvement / refactor
- [ ] Security fix
- [ ] Infrastructure / CI change

## Testing

- [ ] Tests added / updated (`pytest` passes)
- [ ] `ruff check` and `ruff format` pass
- [ ] `bandit` / `pip-audit` clean
- [ ] Docker image builds and health check passes locally

## API contract

- [ ] No API changes
- [ ] API changed — `contracts/api-contract.yaml` in `aws-platform` updated

## Checklist

- [ ] No secrets or credentials in this PR
- [ ] `APP_ENV` / `AUTH_ENABLED` behaviour verified for all environments
- [ ] ECS task definition changes tested (`health_check_grace_period_seconds` sufficient)
- [ ] SSM parameter changes reflected in `contracts/ssm-parameters.yaml`
