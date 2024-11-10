from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from agentex.utils.model_utils import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class EnvVarKeys(str, Enum):
    ENV = "ENV"
    TEMPORAL_ADDRESS = "TEMPORAL_ADDRESS"
    REDIS_URL = "REDIS_URL"


class Environment(str, Enum):
    DEV = "development"
    PROD = "production"


refreshed_environment_variables = None


class EnvironmentVariables(BaseModel):
    ENV: Optional[str] = Environment.DEV
    TEMPORAL_ADDRESS: Optional[str]
    REDIS_URL: Optional[str]

    @classmethod
    def refresh(cls) -> Optional[EnvironmentVariables]:
        global refreshed_environment_variables
        if refreshed_environment_variables is not None:
            return refreshed_environment_variables

        if os.environ.get(EnvVarKeys.ENV) == Environment.DEV:
            load_dotenv(dotenv_path=Path(PROJECT_ROOT / '.env'), override=True)
        environment_variables = EnvironmentVariables(
            ENV=os.environ.get(EnvVarKeys.ENV),
            TEMPORAL_ADDRESS=os.environ.get(EnvVarKeys.TEMPORAL_ADDRESS),
            REDIS_URL=os.environ.get(EnvVarKeys.REDIS_URL),
        )
        refreshed_environment_variables = environment_variables
        return refreshed_environment_variables
