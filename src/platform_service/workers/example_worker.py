from platform_service.core.logging import get_logger

logger = get_logger(__name__)


def run_once() -> None:
    """Placeholder for batch or background work.

    This can later be separated into:
    - ECS scheduled task
    - SQS consumer
    - EventBridge-triggered job
    - async worker process
    """

    logger.info("Example worker executed")
