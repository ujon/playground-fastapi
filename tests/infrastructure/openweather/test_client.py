import os
import pytest
import httpx
from dotenv import load_dotenv
from unittest.mock import AsyncMock, patch, MagicMock
from infrastructure.openweather.client import OpenWeatherClient
from infrastructure.openweather.error import OpenWeatherClientError

load_dotenv("client_api/.env.local")


@pytest.fixture
def client():
    api_key = os.getenv("OPENWEATHERMAP__API_KEY")
    host = os.getenv("OPENWEATHERMAP__HOST")
    return OpenWeatherClient(
        api_key=api_key,
        host=host,
        timeout=10,
    )


@pytest.mark.integration
class TestOpenWeatherClientIntegration:
    async def test_get_weather_success(self, client):
        """실제 API를 호출하여 요청이 잘 보내지는지 테스트"""
        result = await client.get("/data/2.5/weather", params={"q": "Seoul"})

        assert result is not None
        assert "name" in result
        assert result["name"] == "Seoul"
        assert "weather" in result
        assert "main" in result
        await client.close()


@pytest.mark.unit
class TestOpenWeatherClientRetry:
    async def test_5xx_error_triggers_retry(self):
        """5xx 에러 발생 시 재시도 로직 테스트"""
        client = OpenWeatherClient(
            api_key="test_key",
            host="https://api.openweathermap.org",
            timeout=10,
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            # 5xx 에러를 반환하는 mock response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response
            )
            mock_request.return_value = mock_response

            # 5번 재시도 후 OpenWeatherClientError 발생 확인
            with pytest.raises(OpenWeatherClientError) as exc_info:
                await client.get("/test")

            # 5번 재시도 확인
            assert mock_request.call_count == 5
            assert "retry:5" in str(exc_info.value)

        await client.close()

    async def test_4xx_error_no_retry(self):
        """4xx 에러는 재시도하지 않는지 테스트"""
        client = OpenWeatherClient(
            api_key="test_key",
            host="https://api.openweathermap.org",
            timeout=10,
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_request.return_value = mock_resp

            with pytest.raises(Exception):
                await client.get("/test")

            # 4xx 에러는 재시도하지 않으므로 1번만 호출
            assert mock_request.call_count == 1

        await client.close()
