import logging
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception,
    before_sleep_log,
    RetryCallState,
)

from infrastructure.openweather.error import OpenWeatherClientError, OpenWeatherNotFoundError, \
    OpenWeatherBadRequestError, OpenWeatherUnauthorizedError

logger = logging.getLogger(__name__)


# MARK: - Logging
async def _log_request(request: httpx.Request) -> None:
    logger.debug(
        "[OpenWeather] request %s %s",
        request.method,
        request.url,
    )


async def _log_response(response: httpx.Response) -> None:
    request = response.request
    if response.is_success:
        logger.debug(
            "[OpenWeather] success %s %s status: %s",
            request.method,
            request.url,
            response.status_code,
        )
    else:
        await response.aread()
        # log 레벨을 error로 할 경우 중복 에러로그가 너무 많을 수 있음
        logger.debug(
            "[OpenWeather] error %s %s status: %s \n%s",
            request.method,
            request.url,
            response.status_code,
            response.text[:200],
        )


# MARK: - Retry
def is_retryable(exception: BaseException) -> bool:
    """
    5xx 에러만 재시도
    """
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        return not (status < 500)
    if isinstance(exception, (httpx.TimeoutException, httpx.TransportError)):
        return True
    return False


# MARK: - Error
def raise_custom_error(retry_state: RetryCallState) -> None:
    args = retry_state.args
    method = args[1] if len(args) > 1 else "UNKNOWN"
    path = args[2] if len(args) > 2 else "UNKNOWN"

    raise OpenWeatherClientError(
        method=method,
        path=path,
        retry=retry_state.attempt_number,
        exception=retry_state.outcome.exception(),
    )


# MARK: - Client
class OpenWeatherClient:
    def __init__(
            self,
            api_key: str,
            host: str,
            timeout: float = 30,  # seconds
    ):
        self.api_key = api_key
        self.host = host
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            event_hooks={
                "request": [_log_request],
                "response": [_log_response],
            },
        )

    async def get(self, path: str, params: dict[str, str | int | float] | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, str | int | float | list | dict | None] | None = None) -> dict:
        return await self._request("POST", path, json=json)

    async def close(self) -> None:
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential_jitter(initial=0.5, max=10),
        retry=retry_if_exception(is_retryable),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        retry_error_callback=raise_custom_error
    )
    async def _request(
            self,
            method: str,
            path: str,
            params: dict[str, str | int | float] | None = None,
            json: dict[str, str | int | float | list | dict | None] | None = None,
    ) -> dict:
        url = f"{self.host}{path}"
        params = params or {}
        params["appid"] = self.api_key

        response = await self.client.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )

        match response.status_code:
            case status if 200 <= status < 300:
                return response.json()
            case 400:
                raise OpenWeatherBadRequestError()
            case 401:
                raise OpenWeatherUnauthorizedError()
            case 404:
                raise OpenWeatherNotFoundError(params=self._sanitize_params(params))
            case status if status < 500:
                raise OpenWeatherClientError(
                    method=method,
                    path=path,
                    retry=0,
                )
            case _:
                response.raise_for_status()
                return response.json()

    def _sanitize_params(self, params: dict) -> dict:
        sensitive_keys = {"appid"}
        return {k: v for k, v in params.items() if k not in sensitive_keys}
