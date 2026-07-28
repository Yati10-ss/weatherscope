from fastapi import APIRouter

from app.api.routes import exports, health, locations, weather, weather_searches


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(locations.router)
api_router.include_router(weather.router)
api_router.include_router(weather_searches.router)
api_router.include_router(exports.router)
