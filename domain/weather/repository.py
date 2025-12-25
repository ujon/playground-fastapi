from abc import ABC, abstractmethod

from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherListByCitiesQuery, WeatherByCityQuery


class WeatherCacheRepository(ABC):

    @abstractmethod
    async def save_weather_city(self, weather: Weather, ttl: int) -> None:
        pass

    @abstractmethod
    async def get_weather_city(self, query: WeatherByCityQuery) -> Weather | None:
        pass

    @abstractmethod
    async def get_weather_cities(self, query: WeatherListByCitiesQuery) -> list[Weather]:
        pass
