from typing import Annotated

from fastapi import APIRouter, Depends

from platform_service.services.example_service import ExampleService

router = APIRouter()


def get_example_service() -> ExampleService:
    return ExampleService()


@router.get("")
async def get_example(
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> dict[str, str]:
    return service.get_message()
