from platform_service.repositories.example_repository import ExampleRepository


class ExampleService:
    def __init__(self, repository: ExampleRepository | None = None) -> None:
        self.repository = repository or ExampleRepository()

    def get_message(self) -> dict[str, str]:
        value = self.repository.get_value()
        return {"message": f"Platform service is running: {value}"}
