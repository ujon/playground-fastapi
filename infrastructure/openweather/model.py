from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel, to_snake

from domain.weather.data.model import Weather


class BaseResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake)


class WeatherResponse(BaseResponse):
    """
    Link: https://openweathermap.org/current
    """

    class Coord(BaseResponse):
        lon: float  # Longitude of the location
        lat: float  # Latitude of the location

    class Weather(BaseResponse):
        """
        Weather condition codes: https://openweathermap.org/weather-conditions
        """
        id: int  # Weather condition id
        main: str  # Group of weather parameters (Rain, Snow, Clouds etc.)
        description: str  # Weather condition within the group
        icon: str  # Weather icon id

    class Main(BaseResponse):
        temp: float  # Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
        feels_like: float  # Temperature. This temperature parameter accounts for the human perception of weather. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit
        pressure: int  # Atmospheric pressure on the sea level, hPa
        humidity: int  # Humidity, %
        temp_min: float  # Minimum currently observed temperature
        temp_max: float  # Maximum currently observed temperature
        sea_level: int | None = None  # Atmospheric pressure on the sea level, hPa
        ground_level: int | None = Field(
            default=None,
            alias="grnd_level"
        )  # Atmospheric pressure on the ground level, hPa

    class Wind(BaseResponse):
        speed: float  # Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour
        deg: int  # Wind direction, degrees (meteorological)
        gust: float | None = None  # Wind gust. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour

    class Clouds(BaseResponse):
        all: int  # Cloudiness, %

    class Rain(BaseResponse):
        one_hour: float | None = Field(default=None, alias="1h")  # Precipitation in last 1 hour (mm/h)

    class Snow(BaseResponse):
        one_hour: float | None = Field(default=None, alias="1h")  # Snow in last 1 hour (mm/h)

    class System(BaseResponse):
        type: int | None = None  # Internal parameter
        id: int | None = None  # Internal parameter
        message: float | None = None  # Internal parameter
        country: str  # Country code (GB, JP etc.)
        sunrise: int  # Sunrise time, unix, UTC
        sunset: int  # Sunset time, unix, UTC

    coord: Coord  # Coordinate information
    weather: list[Weather]  # Weather condition list
    base: str  # Internal parameter
    main: Main
    visibility: int
    wind: Wind
    clouds: Clouds
    rain: Rain | None = None
    snow: Snow | None = None
    dt: int  # Time of data calculation, unix, UTC
    sys: System
    timezone: int  # Shift in seconds from UTC
    id: int  # City Id
    name: str  # City name
    cod: int  # Internal parameter

    def to_domain(self) -> Weather:
        return Weather(
            city=self.name,
            conditions=[
                Weather.Condition(
                    condition=it.main,
                    description=it.description,
                )
                for it in self.weather
            ]
        )
