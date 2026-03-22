from fastapi import APIRouter, Depends, Request

from core.generations.service import GenerationService
from services.dependencies import get_current_user
from services.exceptions import NotFoundException

from .dtos import (
    GenerateVideoRequestDTO,
    GenerationRunResponseDTO,
    GenerationStatusResponseDTO,
)


class VideoGenerationAPIRouter:
    def __init__(self, generation_service: GenerationService):
        self.generation_service = generation_service
        self.router = APIRouter(
            prefix="/generations",
            tags=["generations"],
            dependencies=[Depends(get_current_user)],
        )

        # Register routers
        self.router.add_api_route(
            "/",
            self.create_generation,
            methods=["POST"],
            response_model=GenerationRunResponseDTO,
        )
        self.router.add_api_route(
            "/{generation_id}/status",
            self.get_generation_status,
            methods=["GET"],
            response_model=GenerationStatusResponseDTO,
        )

    async def create_generation(
        self,
        request: Request,
        generate_request_dto: GenerateVideoRequestDTO,
    ):
        generation_start = await self.generation_service.start_generation_workflow(
            user_id=request.state.user_id,
            create_dto=generate_request_dto,
        )

        run_dto = GenerationRunResponseDTO(
            generation_id=generation_start.generation_id,
            workflow_id=generation_start.handle_id,
            status="queued",
        )
        return run_dto

    async def get_generation_status(
        self,
        request: Request,
        generation_id: str,
    ):
        """Query Temporal directly for workflow state — no DB polling required."""
        try:
            workflow_execution = await self.generation_service.get_workflow_execution(
                generation_id=generation_id
            )
            status_dto = GenerationStatusResponseDTO(
                generation_id=generation_id,
                status=workflow_execution.status.name
                if workflow_execution.status
                else None,
                start_time=workflow_execution.start_time,
            )
            return status_dto
        except Exception as e:
            raise NotFoundException(detail=str(e))
