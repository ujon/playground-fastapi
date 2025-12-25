from fastapi import APIRouter
from client_api.router.weather.router import router as weather_router

root_router = APIRouter()

root_router.include_router(weather_router)
