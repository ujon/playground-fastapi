from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherByCityQuery
from domain.weather.provider import WeatherProvider
from infrastructure.openweather.client import OpenWeatherClient
from infrastructure.openweather.model import WeatherResponse


class OpenWeatherProvider(WeatherProvider):

    def __init__(self, client: OpenWeatherClient):
        self.client = client

    async def get(self, query: WeatherByCityQuery) -> Weather:
        data = await self.client.get(
            "/data/2.5/weather",
            params={"q": query.city},
        )
        return WeatherResponse.model_validate(data).to_domain()
