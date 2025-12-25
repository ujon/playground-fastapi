from pydantic import BaseModel


class OpenWeatherSettings(BaseModel):
    host: str = ""
    api_key: str = ""


