from fastapi import status


class BaseOpenWeatherError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str):
        super().__init__(message)


class OpenWeatherClientError(BaseOpenWeatherError):
    status_code: int = status.HTTP_502_BAD_GATEWAY

    def __init__(self, method: str, path: str, retry: int, exception: Exception | None = None):
        super().__init__(f"failed {method} {path}. retry:{retry} ")


class OpenWeatherBadRequestError(BaseOpenWeatherError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        super().__init__(f"bad request")


class OpenWeatherNotFoundError(BaseOpenWeatherError):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, params: dict | None = None):
        super().__init__(f"not found. query: {params}")


class OpenWeatherUnauthorizedError(BaseOpenWeatherError):
    status_code: int = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__(f"[OpenWeather] unauthorized")
