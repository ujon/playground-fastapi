from abc import ABC, abstractmethod

from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherByCityQuery


class WeatherProvider(ABC):
    @abstractmethod
    async def get(self, query: WeatherByCityQuery) -> Weather:
        pass
