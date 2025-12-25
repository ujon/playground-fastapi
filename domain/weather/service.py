import asyncio
from abc import ABC, abstractmethod

from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherByCityQuery, WeatherListByCitiesQuery
from domain.weather.provider import WeatherProvider
from domain.weather.repository import WeatherCacheRepository


class IWeatherService(ABC):
    @abstractmethod
    async def get_weather_city(self, query: WeatherByCityQuery) -> Weather:
        pass

    @abstractmethod
    async def get_weather_cities(self, query: WeatherListByCitiesQuery) -> list[Weather]:
        pass


class WeatherService(IWeatherService):

    def __init__(
            self,
            cache: WeatherCacheRepository,
            weather_provider: WeatherProvider,
    ):
        self.cache = cache
        self.weather_provider = weather_provider

    async def get_weather_city(self, query: WeatherByCityQuery) -> Weather:
        cached_weather = await self.cache.get_weather_city(query)
        if cached_weather:
            return cached_weather
        return await self._get_weather(query.city)

    async def get_weather_cities(self, query: WeatherListByCitiesQuery) -> list[Weather]:
        cached_weathers = await self.cache.get_weather_cities(query)
        cached_cities_set = {weather.city for weather in cached_weathers}

        missing_cities = [city for city in query.cities if city not in cached_cities_set]

        if missing_cities:
            tasks = [self._get_weather(city) for city in missing_cities]
            fetched_weathers = await asyncio.gather(*tasks)
        else:
            fetched_weathers = []

        return cached_weathers + fetched_weathers

    # MARK: - private
    async def _get_weather(self, city: str) -> Weather:
        """
        날씨 조회 + 캐시 저장
        """
        weather = await self.weather_provider.get(WeatherByCityQuery(city=city))
        await self.cache.save_weather_city(weather, 600)
        return weather
