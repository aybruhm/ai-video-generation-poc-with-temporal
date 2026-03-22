from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from core.temporal.types import VideoGenerationWorkflowDTO

# Imports inside this block are excluded from Temporal's sandbox restrictions
with workflow.unsafe.imports_passed_through():
    from core.temporal.activities.falai import GenerateVideoDTO, generate_video
    from core.temporal.activities.storage import (
        SaveResultDTO,
        UploadToS3DTO,
        save_generation_result,
        upload_to_s3,
    )
    from core.temporal.activities.tokens import (
        DeductTokensDTO,
        deduct_tokens,
    )


# Retry policy for non-idempotent, fast ops (DB writes, token deduction)
_db_retry_policy = RetryPolicy(
    maximum_attempts=5,
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=1.5,
    maximum_interval=timedelta(seconds=30),
)

# Retry policy for FAL AI — longer gaps, fewer retries (expensive external call)
_fal_retry_policy = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=15),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=2),
)


@workflow.defn
class VideoGenerationWorkflow:
    """
    Orchestrates the full video generation pipeline:
      1. Generate via FAL.AI
      2. Upload output to S3
      3. Deduct user tokens (post-success only)
      4. Persist result to DB

    Each step is independently retried. If the worker crashes at any point,
    Temporal replays from the last successful activity result.
    """

    @workflow.run
    async def run(self, input: VideoGenerationWorkflowDTO) -> str:
        workflow.logger.info(
            f"Starting VideoGenerationWorkflow for generation {input.generation_id}"
        )

        # --- Step 1: Generate ---
        # start_to_close_timeout is per-attempt; heartbeat_timeout detects hangs
        raw_video_url: str = await workflow.execute_activity(
            generate_video,
            GenerateVideoDTO(
                generation_id=input.generation_id,
                prompt=input.prompt,
                model=input.model,
                duration=input.duration,
                aspect_ratio=input.aspect_ratio,
            ),
            start_to_close_timeout=timedelta(minutes=15),
            heartbeat_timeout=timedelta(minutes=2),
            retry_policy=_fal_retry_policy,
        )

        # --- Step 2: Upload to S3 ---
        s3_url: str = await workflow.execute_activity(
            upload_to_s3,
            UploadToS3DTO(
                generation_id=input.generation_id,
                source_url=raw_video_url,
                user_id=input.user_id,
            ),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=_db_retry_policy,
        )

        # --- Step 3: Deduct tokens ---
        await workflow.execute_activity(
            deduct_tokens,
            DeductTokensDTO(
                user_id=input.user_id,
                generation_id=input.generation_id,  # idempotency key
                amount=input.token_cost,
            ),
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_db_retry_policy,
        )

        # --- Step 4: Persist result ---
        await workflow.execute_activity(
            save_generation_result,
            SaveResultDTO(
                generation_id=input.generation_id,
                s3_url=s3_url,
                status="completed",
            ),
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=_db_retry_policy,
        )

        workflow.logger.info(
            f"VideoGenerationWorkflow completed for {input.generation_id}"
        )
        return s3_url
