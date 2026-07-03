# FastAPI 后端仓库 — Claude 指南

## 架构分层（从外到内）
```
api/routes/      ← HTTP 路由，仅调用 services
services/        ← 业务逻辑
repositories/    ← 外部集成（AWS、数据库、缓存）
core/            ← 禁止修改：中间件、认证、配置、错误、日志
```

## 核心规则
- `core/` 层不可修改（`CorrelationIdMiddleware`、`SecurityHeadersMiddleware` 已生产就绪）
- 新端点须经过 `require_api_key` 依赖（`AUTH_ENABLED=true` 时）
- 所有响应须用 `AppError` 抛出结构化错误
- 日志须用 `get_logger(__name__)`，禁止 `print()`

## 常用命令
```bash
pytest                    # 运行测试（含覆盖率报告）
ruff check src tests      # 代码检查
ruff format src tests     # 格式化
bandit -r src -ll         # 安全扫描
pip-audit                 # 依赖漏洞检查
docker build -t app:dev . # 构建镜像
```

## 环境变量（`core/config.py` 的 `Settings` 类）
- `AUTH_ENABLED` — 本地默认关闭，非本地默认开启
- `API_KEYS` — 逗号分隔密钥列表（SSM SecureString）
- `REDIS_HOST` / `REDIS_PORT` — Redis 连接
- `READINESS_CHECK_URLS` — 就绪探针依赖 URL

## 新增功能模式
1. `repositories/` 新建集成类（注入 boto3/httpx 客户端，便于测试）
2. `services/` 新建业务逻辑类（接收仓库实例）
3. `api/routes/v1/` 新建路由文件
4. `main.py` 注册路由（带认证依赖）
5. `config.py` 新增配置项
6. `.env.example` 同步新增环境变量示例
7. 编写测试（含错误路径）

## 禁止
- 禁止在路由层直接调用 boto3 或外部服务
- 禁止修改 `core/middleware.py` 的安全头
- 禁止硬编码密钥或 AWS 资源 ARN
