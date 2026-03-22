from time import sleep
from uuid import UUID

import httpx
from temporalio import activity

from core.generations.dtos import GenerationUpdateDTO
from core.temporal.types import SaveResultDTO, UploadToS3DTO
from dbs.inmemory.generations.dao import GenerationDAO


@activity.defn
async def upload_to_s3(input: UploadToS3DTO) -> str:
    """Downloads from AI Provider's CDN and re-uploads to your S3 bucket."""

    bucket = "generations"
    key = f"videos/{input.user_id}/{input.generation_id}.mp4"

    async with httpx.AsyncClient() as client:
        response = await client.get(input.source_url)
        response.raise_for_status()

    # Simulate s3 upload
    # Idempotent — re-uploading the same key is safe
    sleep(3)

    s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    activity.logger.info(f"Uploaded {input.generation_id} to {s3_url}")
    return s3_url


@activity.defn
async def save_generation_result(input: SaveResultDTO) -> None:
    """Persists final generation state to the DB."""
    from core.generations.service import GenerationService

    generation_service = GenerationService(dao=GenerationDAO())
    await generation_service.update_generation(
        generation_id=UUID(input.generation_id),
        update_dto=GenerationUpdateDTO(
            status="completed",
            output_url=input.s3_url,
        ),
    )

    activity.logger.info(f"Saved result for {input.generation_id}")
