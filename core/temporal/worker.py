import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from core.temporal.activities.falai import generate_video
from core.temporal.activities.storage import (
    save_generation_result,
    upload_to_s3,
)
from core.temporal.activities.tokens import deduct_tokens
from core.temporal.workflows.video_generation import VideoGenerationWorkflow
from utils.env_utils import env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the task queue name
video_task_queue = env.TEMPORAL_WORKER_TASK_QUEUE.get(
    "video_generation", "video-generation"
)


async def run_worker():
    client = await Client.connect(target_host=env.TEMPORAL_TARGET_HOST)
    worker = Worker(
        client,
        task_queue=video_task_queue,
        workflows=[VideoGenerationWorkflow],
        activities=[
            generate_video,
            upload_to_s3,
            save_generation_result,
            deduct_tokens,
        ],
    )

    logger.info(f"Worker started on task queue: {video_task_queue}")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
