import json
import os
from typing import Dict

from pydantic import BaseModel


class EnvSettings(BaseModel):
    # Infrastructure Settings
    TEMPORAL_TARGET_HOST: str = os.getenv(
        "TEMPORAL_TARGET_HOST", "localhost:7233"
    )
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////tmp/poc.db")

    # Application Settings
    TEMPORAL_WORKER_TASK_QUEUE: Dict[str, str] = json.loads(
        os.getenv("TEMPORAL_WORKER_TASK_QUEUE", "{}")
    )


env = EnvSettings()
