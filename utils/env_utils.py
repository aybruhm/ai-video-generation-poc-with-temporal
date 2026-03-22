import json
import os
from typing import Dict

from pydantic import BaseModel


class EnvSettings(BaseModel):
    # Infrastructure Settings
    TEMPORAL_TARGET_HOST: str = os.getenv("TEMPORAL_TARGET_HOST", "temporal:7233")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////tmp/poc.db")

    # Application Settings
    TEMPORAL_WORKER_TASK_QUEUE: Dict[str, str] = json.loads(
        os.getenv("TEMPORAL_WORKER_TASK_QUEUE", "{}")
    )
    JWT_KEY: str = os.getenv("JWT_KEY", "")
    JWT_EXP: int = int(os.getenv("JWT_EXP", "900"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # AI Provider Settings
    FALAI_API_KEY: str = os.getenv("FALAI_API_KEY", "")


env = EnvSettings()
