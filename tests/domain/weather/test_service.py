import pytest
from domain.weather.data.model import Weather
from domain.weather.data.query import WeatherByCityQuery, WeatherListByCitiesQuery
from domain.weather.provider import WeatherProvider
from domain.weather.repository import WeatherCacheRepository
from domain.weather.service import WeatherService


# Fake in-memory cache repository (Redis 대신 사용)
class FakeWeatherCacheRepository(WeatherCacheRepository):
    def __init__(self):
        import time
        self.cache: dict[str, tuple[Weather, float]] = {}  # (weather, expiry_time)
        self.time = time

    async def save_weather_city(self, weather: Weather, ttl: int) -> None:
        expiry_time = self.time.time() + ttl
        self.cache[weather.city] = (weather, expiry_time)

    async def get_weather_city(self, query: WeatherByCityQuery) -> Weather | None:
        if query.city not in self.cache:
            return None

        weather, expiry_time = self.cache[query.city]

        # TTL 체크: 만료되었으면 삭제하고 None 반환
        if self.time.time() > expiry_time:
            del self.cache[query.city]
            return None

        return weather

    async def get_weather_cities(self, query: WeatherListByCitiesQuery) -> list[Weather]:
        results = []
        current_time = self.time.time()

        for city in query.cities:
            if city in self.cache:
                weather, expiry_time = self.cache[city]

                # TTL 체크
                if current_time <= expiry_time:
                    results.append(weather)
                else:
                    # 만료된 항목 삭제
                    del self.cache[city]

        return results


# Fake weather provider
class FakeWeatherProvider(WeatherProvider):
    def __init__(self):
        self.call_count = 0
        self.called_cities = []

    async def get(self, query: WeatherByCityQuery) -> Weather:
        self.call_count += 1
        self.called_cities.append(query.city)

        return Weather(
            city=query.city,
            conditions=[
                Weather.Condition(
                    condition="Clear",
                    description="clear sky"
                )
            ]
        )


@pytest.fixture
def cache_repo():
    return FakeWeatherCacheRepository()


@pytest.fixture
def weather_provider():
    return FakeWeatherProvider()


@pytest.fixture
def weather_service(cache_repo, weather_provider):
    return WeatherService(
        cache=cache_repo,
        weather_provider=weather_provider
    )


@pytest.mark.unit
class TestWeatherService:
    async def test_get_weather_city_cache_miss(self, weather_service, weather_provider, cache_repo):
        """캐시에 없을 때 provider를 호출하고 캐시에 저장"""
        query = WeatherByCityQuery(city="Seoul")

        result = await weather_service.get_weather_city(query)

        assert result is not None
        assert result.city == "Seoul"
        assert len(result.conditions) == 1
        assert result.conditions[0].condition == "Clear"

        # Provider가 호출되었는지 확인
        assert weather_provider.call_count == 1
        assert "Seoul" in weather_provider.called_cities

        # 캐시에 저장되었는지 확인
        assert "Seoul" in cache_repo.cache

    async def test_get_weather_city_cache_hit(self, weather_service, weather_provider, cache_repo):
        """캐시에 있을 때 provider를 호출하지 않음"""
        # 먼저 캐시에 데이터 저장
        cached_weather = Weather(
            city="Tokyo",
            conditions=[
                Weather.Condition(
                    condition="Rain",
                    description="light rain"
                )
            ]
        )
        await cache_repo.save_weather_city(cached_weather, 600)

        query = WeatherByCityQuery(city="Tokyo")
        result = await weather_service.get_weather_city(query)

        assert result is not None
        assert result.city == "Tokyo"
        assert result.conditions[0].condition == "Rain"

        # Provider가 호출되지 않았는지 확인
        assert weather_provider.call_count == 0

    async def test_get_weather_cities_all_cached(self, weather_service, weather_provider, cache_repo):
        """모든 도시가 캐시에 있을 때"""
        # 캐시에 데이터 저장
        cities_data = [
            Weather(city="Seoul", conditions=[Weather.Condition(condition="Clear", description="clear")]),
            Weather(city="Tokyo", conditions=[Weather.Condition(condition="Rain", description="rain")]),
            Weather(city="London", conditions=[Weather.Condition(condition="Clouds", description="clouds")]),
        ]
        for weather in cities_data:
            await cache_repo.save_weather_city(weather, 600)

        query = WeatherListByCitiesQuery(cities=["Seoul", "Tokyo", "London"])
        results = await weather_service.get_weather_cities(query)

        assert len(results) == 3
        assert {w.city for w in results} == {"Seoul", "Tokyo", "London"}

        # Provider가 호출되지 않았는지 확인
        assert weather_provider.call_count == 0

    async def test_get_weather_cities_partial_cached(self, weather_service, weather_provider, cache_repo):
        """일부 도시만 캐시에 있을 때"""
        # Seoul만 캐시에 저장
        cached_weather = Weather(
            city="Seoul",
            conditions=[Weather.Condition(condition="Clear", description="clear")]
        )
        await cache_repo.save_weather_city(cached_weather, 600)

        query = WeatherListByCitiesQuery(cities=["Seoul", "Tokyo", "London"])
        results = await weather_service.get_weather_cities(query)

        assert len(results) == 3
        assert {w.city for w in results} == {"Seoul", "Tokyo", "London"}

        # Provider가 2번 호출되었는지 확인 (Tokyo, London)
        assert weather_provider.call_count == 2
        assert "Tokyo" in weather_provider.called_cities
        assert "London" in weather_provider.called_cities
        assert "Seoul" not in weather_provider.called_cities

        # 새로 조회한 도시들이 캐시에 저장되었는지 확인
        assert "Tokyo" in cache_repo.cache
        assert "London" in cache_repo.cache

    async def test_get_weather_cities_none_cached(self, weather_service, weather_provider, cache_repo):
        """캐시에 아무것도 없을 때"""
        query = WeatherListByCitiesQuery(cities=["Seoul", "Tokyo", "London"])
        results = await weather_service.get_weather_cities(query)

        assert len(results) == 3
        assert {w.city for w in results} == {"Seoul", "Tokyo", "London"}

        # Provider가 3번 호출되었는지 확인
        assert weather_provider.call_count == 3

        # 모든 도시가 캐시에 저장되었는지 확인
        assert len(cache_repo.cache) == 3

    async def test_get_weather_cities_empty_list(self, weather_service, weather_provider):
        """빈 리스트 조회"""
        query = WeatherListByCitiesQuery(cities=[])
        results = await weather_service.get_weather_cities(query)

        assert len(results) == 0
        assert weather_provider.call_count == 0

    async def test_cache_ttl_expiration(self, cache_repo):
        """TTL이 만료되면 캐시가 자동으로 삭제되는지 확인"""
        import time

        # TTL 1초로 저장
        weather = Weather(
            city="Berlin",
            conditions=[Weather.Condition(condition="Clear", description="clear sky")]
        )
        await cache_repo.save_weather_city(weather, ttl=1)

        # 즉시 조회 - 있어야 함
        query = WeatherByCityQuery(city="Berlin")
        cached = await cache_repo.get_weather_city(query)
        assert cached is not None
        assert cached.city == "Berlin"

        # 1.5초 대기
        time.sleep(1.5)

        # 만료되어 None이어야 함
        cached = await cache_repo.get_weather_city(query)
        assert cached is None
        # 캐시에서도 삭제되었는지 확인
        assert "Berlin" not in cache_repo.cache

    async def test_cache_ttl_multiple_items(self, cache_repo):
        """여러 항목의 TTL이 개별적으로 작동하는지 확인"""
        import time

        # 서로 다른 TTL로 저장
        weather1 = Weather(city="City1", conditions=[Weather.Condition(condition="Clear", description="clear")])
        weather2 = Weather(city="City2", conditions=[Weather.Condition(condition="Rain", description="rain")])

        await cache_repo.save_weather_city(weather1, ttl=1)  # 1초 후 만료
        await cache_repo.save_weather_city(weather2, ttl=10)  # 10초 후 만료

        # 1.5초 대기
        time.sleep(1.5)

        # City1은 만료, City2는 유효
        cached1 = await cache_repo.get_weather_city(WeatherByCityQuery(city="City1"))
        cached2 = await cache_repo.get_weather_city(WeatherByCityQuery(city="City2"))

        assert cached1 is None
        assert cached2 is not None
        assert cached2.city == "City2"

    async def test_get_weather_cities_with_expired(self, cache_repo):
        """get_weather_cities에서 만료된 항목은 제외되는지 확인"""
        import time

        # 서로 다른 TTL로 여러 항목 저장
        weather1 = Weather(city="Seoul", conditions=[Weather.Condition(condition="Clear", description="clear")])
        weather2 = Weather(city="Tokyo", conditions=[Weather.Condition(condition="Rain", description="rain")])
        weather3 = Weather(city="London", conditions=[Weather.Condition(condition="Clouds", description="clouds")])

        await cache_repo.save_weather_city(weather1, ttl=1)  # 1초 후 만료
        await cache_repo.save_weather_city(weather2, ttl=10)  # 10초 후 만료
        await cache_repo.save_weather_city(weather3, ttl=1)  # 1초 후 만료

        # 1.5초 대기
        time.sleep(1.5)

        # 조회 - Tokyo만 반환되어야 함
        query = WeatherListByCitiesQuery(cities=["Seoul", "Tokyo", "London"])
        results = await cache_repo.get_weather_cities(query)

        assert len(results) == 1
        assert results[0].city == "Tokyo"

        # 만료된 항목들은 캐시에서도 삭제되었는지 확인
        assert "Seoul" not in cache_repo.cache
        assert "London" not in cache_repo.cache
        assert "Tokyo" in cache_repo.cache
