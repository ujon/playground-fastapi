from pydantic import BaseModel


class GetWeatherBatchRequest(BaseModel):
    cities: list[str]
