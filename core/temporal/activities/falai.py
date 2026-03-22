from fal_client import AsyncClient
from temporalio import activity

from core.temporal.types import GenerateVideoDTO
from utils.env_utils import env


@activity.defn
async def generate_video(input: GenerateVideoDTO) -> str:
    """
    Calls FAL.AI to generate a video. Returns the raw CDN URL.
    Temporal will retry this independently if it fails.
    """

    logger = activity.logger
    logger.info(f"Starting FAL.AI generation for {input.generation_id}")

    # Heartbeat keeps Temporal informed the activity is alive
    # Critical for long-running generations (prevents timeout-based retry storms)
    activity.heartbeat("submitted_to_falai")

    if not env.FALAI_API_KEY:
        raise ValueError("FALAI_API_KEY environment variable not set")

    fal_client = AsyncClient(key=env.FALAI_API_KEY)
    result = await fal_client.run(
        input.model,
        arguments={
            "prompt": input.prompt,
            "duration": input.duration,
            "aspect_ratio": input.aspect_ratio,
        },
    )

    activity.heartbeat("falai_generation_complete")

    video_url: str = result["video"]["url"]
    logger.info(f"FAL.AI returned URL for {input.generation_id}: {video_url}")
    return video_url
