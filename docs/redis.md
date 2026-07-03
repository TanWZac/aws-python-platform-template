# Redis Cache Integration

This template includes a Redis client and cache service that can connect to local Redis or AWS ElastiCache.

## Environment Variables

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_SSL=false
REDIS_TIMEOUT_SECONDS=2
CACHE_DEFAULT_TTL_SECONDS=300
```

For AWS ElastiCache with in-transit encryption enabled:

```bash
REDIS_HOST=<elasticache-primary-endpoint>
REDIS_PORT=6379
REDIS_SSL=true
```

## Local Redis with Docker

```bash
docker run --rm -p 6379:6379 redis:7
```

Then run the API:

```bash
make run
```

## Example Endpoints

```text
GET /api/v1/cache/ping
GET /api/v1/cache/example
```

## Code Structure

```text
src/platform_service/core/cache.py
src/platform_service/services/cache_service.py
src/platform_service/api/routes/v1/cache.py
```

## Recommended Use Cases

- API response caching
- user session cache
- rate limiting
- idempotency keys
- distributed locks
- job coordination
- temporary AI/RAG state

## Production Notes

Use Terraform output `redis_primary_endpoint` as `REDIS_HOST`.

If Redis AUTH is enabled in infrastructure, extend `core/cache.py` to read the secret from your runtime secret provider.
