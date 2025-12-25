from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class ServerResponse(BaseModel, Generic[T]):
    message: str
    payload: T | None = None

    @classmethod
    def success(cls, payload: T | None = None) -> "ServerResponse[T]":
        return cls(message="success", payload=payload)

    @classmethod
    def error(cls, message: str) -> "ServerResponse[None]":
        return cls(message=message, payload=None)