from pydantic import BaseModel
from typing import Optional


class RedisSettings(BaseModel):
    """
    prefix: REDIS__
    """
    host: str = ""
    port: int = 6379
    password: Optional[str] = None

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}"
        return f"redis://{self.host}:{self.port}"
