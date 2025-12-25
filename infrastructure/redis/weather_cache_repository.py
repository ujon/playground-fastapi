import json

from dataclasses import asdict
from dacite import from_dict
from redis.asyncio import Redis

from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherListByCitiesQuery, WeatherByCityQuery
from domain.weather.repository import WeatherCacheRepository


class RedisWeatherCacheRepository(WeatherCacheRepository):
    CITY_WEATHER_KEY = 'weather:city'
    CITY_WEATHER_TTL = 600  # milliseconds

    def __init__(self, redis: Redis):
        self.redis = redis

    def _city_weather_key(self, city: str) -> str:
        return f"{self.CITY_WEATHER_KEY}:{city.lower()}"

    async def save_weather_city(self, weather: Weather, ttl: int = CITY_WEATHER_TTL) -> None:
        key = self._city_weather_key(weather.city)
        value = json.dumps(asdict(weather))
        await self.redis.set(key, value, ex=ttl)

    async def get_weather_city(self, query: WeatherByCityQuery) -> Weather | None:
        key = self._city_weather_key(query.city)
        value = await self.redis.get(key)

        if not value:
            return None

        return from_dict(data_class=Weather, data=json.loads(value))

    async def get_weather_cities(self, query: WeatherListByCitiesQuery) -> list[Weather]:
        if not query.cities:
            return []

        async with self.redis.pipeline() as pipe:
            for city in query.cities:
                await pipe.get(self._city_weather_key(city))

            values = await pipe.execute()

        return [
            from_dict(data_class=Weather, data=json.loads(value))
            for value in values
            if value
        ]
