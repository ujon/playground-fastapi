from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from domain.weather.provider import WeatherProvider
from domain.weather.service import WeatherService
from domain.weather.repository import WeatherCacheRepository
from infrastructure.openweather.client import OpenWeatherClient
from infrastructure.openweather.provider import OpenWeatherProvider
from infrastructure.redis.redis_manager import redis_manager
from infrastructure.redis.weather_cache_repository import RedisWeatherCacheRepository


# MARK: - infra

# MARK: - infra/openweather
def get_openweather_client(request: Request) -> OpenWeatherClient:
    return request.app.state.openweather_client


def get_open_weather_provider(
        client: Annotated[OpenWeatherClient, Depends(get_openweather_client)]
) -> WeatherProvider:
    return OpenWeatherProvider(client)


OpenWeatherProviderDI = Annotated[OpenWeatherProvider, Depends(get_open_weather_provider)]


# MARK: - infra/redis
async def get_redis() -> Redis:
    return await redis_manager.get_client()


RedisDI = Annotated[Redis, Depends(get_redis)]


# MARK: - domain

# MARK: - domain/weather
def get_weather_cache_repository(redis: RedisDI) -> WeatherCacheRepository:
    return RedisWeatherCacheRepository(redis)


def get_weather_service(
        cache: Annotated[WeatherCacheRepository, Depends(get_weather_cache_repository)],
        weather_provider: Annotated[WeatherProvider, Depends(get_open_weather_provider)],
) -> WeatherService:
    return WeatherService(cache, weather_provider)
