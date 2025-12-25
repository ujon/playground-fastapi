from typing import Annotated

from fastapi import APIRouter, Depends, Body, Path

from client_api.dependency import get_weather_service
from client_api.router.weather.request import GetWeatherBatchRequest
from client_api.router.weather.response import WeatherResponse
from client_api.shared.dto.response import ServerResponse
from domain.weather.data.query import WeatherListByCitiesQuery, WeatherByCityQuery
from domain.weather.service import WeatherService

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/{city}")
async def get_weather(
        city: Annotated[str, Path(
            ...,
            description="영어 도시 이름"
        )],
        weather_service: Annotated[WeatherService, Depends(get_weather_service)]
):
    query = WeatherByCityQuery(city=city)
    return await weather_service.get_weather_city(query)


@router.post("/batch", response_model=ServerResponse[list[WeatherResponse]])
async def get_weather_batch(
        request: Annotated[GetWeatherBatchRequest, Body(
            ...,
            description="날씨 배치조회",
            examples=[{"cities": ["Seoul", "Tokyo", "London"]}]
        )],
        weather_service: Annotated[WeatherService, Depends(get_weather_service)]
):
    weather_list = await weather_service.get_weather_cities(WeatherListByCitiesQuery(cities=request.cities))
    return ServerResponse.success([
        WeatherResponse.from_model(it) for it in weather_list
    ])
