import uvicorn
from fastapi import FastAPI
from client_api.router import root_router
from client_api.shared.config.log_config import LOG_CONFIG
from client_api.shared.middleware.error_handler import register_exception_handlers
from client_api.settings import settings
from contextlib import asynccontextmanager
from infrastructure.redis.redis_manager import redis_manager
from infrastructure.openweather.client import OpenWeatherClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect(redis_url=settings.redis.url)
    app.state.openweather_client = OpenWeatherClient(
        api_key=settings.openweathermap.api_key,
        host=settings.openweathermap.host,
    )
    yield
    await redis_manager.close()
    await app.state.openweather_client.close()


app = FastAPI(lifespan=lifespan, title="Client API")
app.include_router(root_router)
register_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run(
        "client_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=LOG_CONFIG,
    )


@app.get("/")
async def health_check():
    return {"status": "ok", "redis_url": settings.redis.url}
