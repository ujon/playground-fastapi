from pydantic import BaseModel


class WeatherByCityQuery(BaseModel):
    city: str


class WeatherListByCitiesQuery(BaseModel):
    cities: list[str]
