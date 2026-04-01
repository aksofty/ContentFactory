from dataclasses import dataclass
from typing import Any

@dataclass
class AppConfig:
    scheduler: Any
    client: Any
    gen_api_token: str
    vk_token: str