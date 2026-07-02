from fastapi import APIRouter

from platform_service.services.example_service import ExampleService

router = APIRouter()


@router.get("")
async def get_example() -> dict[str, str]:
    service = ExampleService()
    return service.get_message()
