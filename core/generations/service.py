from uuid import UUID, uuid4

from core.generations.dtos import (
    GenerationDTO,
    GenerationUpdateDTO,
    StartGenerationRequestDTO,
    StartGenerationResponseDTO,
)
from core.temporal.workflows.video_generation import (
    VideoGenerationWorkflow,
    VideoGenerationWorkflowDTO,
)
from dbs.inmemory.generations.dbes import GenerationDBE
from dbs.inmemory.generations.interfaces import GenerationDAOInterface
from services.dependencies import get_temporal_client
from utils.env_utils import env

# Configure the task queue name
video_task_queue = env.TEMPORAL_WORKER_TASK_QUEUE.get(
    "video_generation", "video-generation"
)


class GenerationService:
    def __init__(self, dao: GenerationDAOInterface):
        self.generation_dao = dao

    def _map_dbe_to_dto(self, dbe: GenerationDBE) -> GenerationDTO:
        return GenerationDTO(
            id=dbe.id,  # type: ignore[arg-type]
            status=dbe.status,  # type: ignore[arg-type]
            output_url=dbe.output_url,  # type: ignore[arg-type]
        )

    async def start_generation_workflow(
        self,
        user_id: UUID,
        create_dto: StartGenerationRequestDTO,
    ):
        generation_id = str(uuid4())
        temporal_client = await get_temporal_client()
        handle = await temporal_client.start_workflow(
            VideoGenerationWorkflow.run,
            VideoGenerationWorkflowDTO(
                user_id=str(user_id),
                generation_id=generation_id,
                prompt=create_dto.prompt,
                model=create_dto.model,
                duration=create_dto.duration,
                aspect_ratio=create_dto.aspect_ratio,
                token_cost=create_dto.token_cost,
            ),
            id=f"video-gen-{generation_id}",
            task_queue=video_task_queue,
        )

        return StartGenerationResponseDTO(
            generation_id=generation_id,
            handle_id=handle.id,
        )

    async def get_workflow_execution(self, generation_id: str):
        temporal_client = await get_temporal_client()
        handle = temporal_client.get_workflow_handle(f"video-gen-{generation_id}")
        description = await handle.describe()
        return description

    async def get_generation(self, generation_id: UUID) -> GenerationDTO | None:
        generation_dbe = await self.generation_dao.get(generation_id=generation_id)
        if generation_dbe is None:
            return None

        generation_dto = self._map_dbe_to_dto(dbe=generation_dbe)
        return generation_dto

    async def update_generation(
        self,
        generation_id: UUID,
        update_dto: GenerationUpdateDTO,
    ) -> None:
        await self.generation_dao.update(
            generation_id=generation_id,
            values_to_update=update_dto.model_dump(),
        )
