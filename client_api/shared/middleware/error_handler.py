import logging
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from client_api.shared.dto.response import ServerResponse
from infrastructure.openweather import BaseOpenWeatherError


async def openweather_error_handler(request: Request, exc: BaseOpenWeatherError) -> JSONResponse:
    status_code = exc.status_code
    message = str(exc)
    _print_log(status_code, message)
    response = ServerResponse.error(message=message)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


async def common_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Client에게 상세 에러 내용을 알려주지 않음
    """
    status_code = 500
    message = str(exc)
    _print_log(status_code, message)
    response = ServerResponse.error(message="Unknown error")
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseOpenWeatherError, openweather_error_handler)
    app.add_exception_handler(Exception, common_error_handler)


def _print_log(status_code: int, message: str) -> None:
    if status_code < 500:
        logging.info(message)
    else:
        logging.error(message)
