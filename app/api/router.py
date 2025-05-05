from fastapi import APIRouter

from app.api.ecosystem_matches_endpoints import router as ecosystem_matches_router
from app.api.characterization_endpoints import router as characterization_router

# Router principal que incluye todos los demás routers
api_router = APIRouter()

# Incluir los routers de la aplicación
api_router.include_router(
    ecosystem_matches_router,
    prefix="/api/v1",
    tags=["ecosystem-matches"]
)
