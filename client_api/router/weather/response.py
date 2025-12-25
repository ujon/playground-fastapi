from pydantic import BaseModel

from domain.weather.data.model import Weather


class WeatherResponse(BaseModel):
    class Condition(BaseModel):
        condition: str
        description: str

    city: str
    conditions: list[Condition]

    @classmethod
    def from_model(cls, weather: Weather) -> "WeatherResponse":
        return cls(
            city=weather.city,
            conditions=[
                cls.Condition(
                    condition=c.condition,
                    description=c.description,
                )
                for c in weather.conditions
            ]
        )
