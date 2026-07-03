.PHONY: install run test lint format security docker-build docker-run clean

APP_MODULE=platform_service.main:app
APP_HOST=0.0.0.0
APP_PORT=8000
IMAGE_NAME=aws-python-platform-template

install:
	pip install -e ".[dev]"

run:
	uvicorn $(APP_MODULE) --host $(APP_HOST) --port $(APP_PORT) --reload

test:
	pytest

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check src tests --fix

security:
	pip-audit
	bandit -r src -ll

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm -p $(APP_PORT):$(APP_PORT) --env-file .env $(IMAGE_NAME)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	rm -rf .coverage htmlcov dist build *.egg-info
